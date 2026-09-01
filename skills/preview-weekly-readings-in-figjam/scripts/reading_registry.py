#!/usr/bin/env python3
"""Maintain the privacy-safe route registry for weekly reading FigJam files."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_STATUS = {"pending", "in_progress", "complete"}
FORBIDDEN_KEYS = {
    "path",
    "sourcepath",
    "text",
    "body",
    "translation",
    "summary",
    "content",
    "token",
    "secret",
    "password",
}


class RegistryError(ValueError):
    pass


def empty_registry() -> dict[str, Any]:
    return {"schemaVersion": 1, "courses": {}}


def read_registry(path: Path, allow_missing: bool = False) -> dict[str, Any]:
    if not path.exists() and allow_missing:
        return empty_registry()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"Could not read registry: {exc}") from exc
    if not isinstance(data, dict):
        raise RegistryError("Registry root must be an object")
    return data


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def route(file_key: str, url: str) -> dict[str, str]:
    key = file_key.strip()
    link = url.strip()
    if bool(key) != bool(link):
        raise RegistryError("file key and URL must be provided together")
    if link and not re.match(r"^https://(?:www\.)?figma\.com/(?:board|file|design)/", link):
        raise RegistryError(f"Not a supported Figma URL: {link}")
    return {"fileKey": key, "url": link}


def weeks(value: str) -> list[str]:
    result = [item.strip() for item in value.split(",") if item.strip()]
    if not result:
        raise RegistryError("At least one week is required")
    return list(dict.fromkeys(result))


def normalize_number(value: str) -> str:
    text = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", text):
        raise RegistryError(f"Invalid article number: {value!r}")
    return text.zfill(2) if text.isdigit() else text


def validate_registry(data: dict[str, Any], course_key: str | None = None) -> list[str]:
    errors: list[str] = []
    if data.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    courses = data.get("courses")
    if not isinstance(courses, dict):
        return errors + ["courses must be an object"]

    keys = [course_key] if course_key else list(courses)
    for key in keys:
        if key not in courses:
            errors.append(f"course not found: {key}")
            continue
        course = courses[key]
        if not isinstance(course, dict):
            errors.append(f"course {key} must be an object")
            continue
        for route_name in ("courseHub", "readingIndex"):
            value = course.get(route_name, {})
            if not isinstance(value, dict):
                errors.append(f"{key}.{route_name} must be an object")
                continue
            try:
                route(str(value.get("fileKey", "")), str(value.get("url", "")))
            except RegistryError as exc:
                errors.append(f"{key}.{route_name}: {exc}")

        articles = course.get("articles", {})
        if not isinstance(articles, dict):
            errors.append(f"{key}.articles must be an object")
            continue
        for number, article in articles.items():
            if not isinstance(article, dict):
                errors.append(f"{key}.articles.{number} must be an object")
                continue
            status = article.get("status")
            if status not in ALLOWED_STATUS:
                errors.append(f"{key}.articles.{number} has invalid status: {status}")
            article_weeks = article.get("weeks")
            if not isinstance(article_weeks, list) or not article_weeks:
                errors.append(f"{key}.articles.{number}.weeks must be non-empty")
            if not str(article.get("sourceName", "")).lower().endswith(".pdf"):
                errors.append(f"{key}.articles.{number}.sourceName must be a PDF basename")
            if Path(str(article.get("sourceName", ""))).name != article.get("sourceName"):
                errors.append(f"{key}.articles.{number}.sourceName must not be a path")
            fingerprint = str(article.get("sourceFingerprint", ""))
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", fingerprint):
                errors.append(f"{key}.articles.{number} has invalid fingerprint")
            try:
                article_route = route(str(article.get("fileKey", "")), str(article.get("url", "")))
                if status == "complete" and not article_route["url"]:
                    errors.append(f"{key}.articles.{number} is complete without a Figma route")
            except RegistryError as exc:
                errors.append(f"{key}.articles.{number}: {exc}")

    def walk(value: Any, prefix: str = "") -> None:
        if isinstance(value, dict):
            for item_key, item_value in value.items():
                normalized = re.sub(r"[^a-z]", "", item_key.lower())
                if normalized in FORBIDDEN_KEYS:
                    errors.append(f"forbidden field: {prefix}{item_key}")
                walk(item_value, f"{prefix}{item_key}.")
        elif isinstance(value, list):
            for item in value:
                walk(item, prefix)

    walk(data)
    return errors


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    data = read_registry(args.registry, allow_missing=True)
    data.setdefault("schemaVersion", 1)
    courses = data.setdefault("courses", {})
    course = courses.setdefault(args.course_key, {"articles": {}})
    course["courseHub"] = route(args.course_hub_key, args.course_hub_url)
    course["readingIndex"] = route(args.index_key, args.index_url)
    course.setdefault("articles", {})
    return data


def cmd_upsert(args: argparse.Namespace) -> dict[str, Any]:
    data = read_registry(args.registry)
    courses = data.get("courses", {})
    if args.course_key not in courses:
        raise RegistryError(f"Initialize course first: {args.course_key}")
    status = args.status
    if status not in ALLOWED_STATUS:
        raise RegistryError(f"Invalid status: {status}")
    article_route = route(args.file_key, args.url)
    if status == "complete" and not article_route["url"]:
        raise RegistryError("complete status requires a Figma file key and URL")
    source_name = args.source_name.strip()
    if Path(source_name).name != source_name or not source_name.lower().endswith(".pdf"):
        raise RegistryError("source-name must be a PDF basename")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", args.fingerprint):
        raise RegistryError("fingerprint must be sha256:<64 lowercase hex characters>")

    number = normalize_number(args.number)
    courses[args.course_key].setdefault("articles", {})[number] = {
        "weeks": weeks(args.weeks),
        "sourceName": source_name,
        "sourceFingerprint": args.fingerprint,
        **article_route,
        "status": status,
        "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    return data


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize or update course routes")
    init.add_argument("--registry", required=True, type=Path)
    init.add_argument("--course-key", required=True)
    init.add_argument("--course-hub-key", default="")
    init.add_argument("--course-hub-url", default="")
    init.add_argument("--index-key", default="")
    init.add_argument("--index-url", default="")

    upsert = sub.add_parser("upsert", help="insert or replace an article route")
    upsert.add_argument("--registry", required=True, type=Path)
    upsert.add_argument("--course-key", required=True)
    upsert.add_argument("--number", required=True)
    upsert.add_argument("--weeks", required=True, help="comma-separated week labels")
    upsert.add_argument("--source-name", required=True)
    upsert.add_argument("--fingerprint", required=True)
    upsert.add_argument("--file-key", default="")
    upsert.add_argument("--url", default="")
    upsert.add_argument("--status", choices=sorted(ALLOWED_STATUS), required=True)

    validate = sub.add_parser("validate", help="validate schema and privacy rules")
    validate.add_argument("--registry", required=True, type=Path)
    validate.add_argument("--course-key")

    show = sub.add_parser("show", help="print the registry or one course")
    show.add_argument("--registry", required=True, type=Path)
    show.add_argument("--course-key")
    return parser


def main() -> int:
    args = make_parser().parse_args()
    try:
        if args.command == "init":
            data = cmd_init(args)
            errors = validate_registry(data, args.course_key)
            if errors:
                raise RegistryError("; ".join(errors))
            atomic_write(args.registry, data)
            print(f"initialized {args.course_key} in {args.registry}")
        elif args.command == "upsert":
            data = cmd_upsert(args)
            errors = validate_registry(data, args.course_key)
            if errors:
                raise RegistryError("; ".join(errors))
            atomic_write(args.registry, data)
            print(f"updated article {normalize_number(args.number)} in {args.registry}")
        elif args.command == "validate":
            data = read_registry(args.registry)
            errors = validate_registry(data, args.course_key)
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 2
            print("registry is valid")
        elif args.command == "show":
            data = read_registry(args.registry)
            value = data
            if args.course_key:
                value = data.get("courses", {}).get(args.course_key)
                if value is None:
                    raise RegistryError(f"course not found: {args.course_key}")
            print(json.dumps(value, ensure_ascii=False, indent=2))
    except RegistryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
