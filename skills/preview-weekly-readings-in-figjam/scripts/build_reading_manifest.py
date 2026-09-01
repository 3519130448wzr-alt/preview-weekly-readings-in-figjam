#!/usr/bin/env python3
"""Build a privacy-safe manifest for assigned reading PDFs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_STATUS = {"pending", "in_progress", "complete"}


class ManifestError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def pdf_page_count(path: Path) -> int:
    try:
        from pypdf import PdfReader  # type: ignore

        return len(PdfReader(str(path)).pages)
    except Exception:
        data = path.read_bytes()
        count = len(re.findall(rb"/Type\s*/Page\b", data))
        if count:
            return count
        raise ManifestError(f"Could not determine PDF page count: {path.name}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"Could not read mapping JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError("Mapping root must be an object")
    return value


def normalize_number(value: Any) -> str:
    text = str(value).strip()
    if not text or not re.fullmatch(r"[A-Za-z0-9._-]+", text):
        raise ManifestError(f"Invalid article number: {value!r}")
    return text.zfill(2) if text.isdigit() else text


def normalize_weeks(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ManifestError("Each article must have a non-empty weeks array")
    weeks: list[str] = []
    for item in value:
        week = str(item).strip()
        if not week:
            raise ManifestError("Week labels cannot be empty")
        if week not in weeks:
            weeks.append(week)
    return weeks


def source_path(reading_dir: Path, filename: Any) -> Path:
    name = str(filename).strip()
    if not name or Path(name).name != name:
        raise ManifestError(f"filename must be a basename, not a path: {name!r}")
    if not name.lower().endswith(".pdf"):
        raise ManifestError(f"Reading source is not a PDF: {name}")
    root = reading_dir.resolve()
    candidate = (root / name).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ManifestError(f"Reading escapes the source directory: {name}") from exc
    if not candidate.is_file():
        raise ManifestError(f"Reading PDF not found: {name}")
    return candidate


def build_manifest(course_key: str, reading_dir: Path, mapping: dict[str, Any]) -> dict[str, Any]:
    key = course_key.strip()
    if not key:
        raise ManifestError("course-key cannot be empty")
    raw_articles = mapping.get("articles")
    if not isinstance(raw_articles, list) or not raw_articles:
        raise ManifestError("Mapping must contain a non-empty articles array")

    seen_numbers: set[str] = set()
    seen_files: set[str] = set()
    articles: list[dict[str, Any]] = []

    for raw in raw_articles:
        if not isinstance(raw, dict):
            raise ManifestError("Every article entry must be an object")
        number = normalize_number(raw.get("number", ""))
        filename = str(raw.get("filename", "")).strip()
        if number in seen_numbers:
            raise ManifestError(f"Duplicate article number: {number}")
        if filename.casefold() in seen_files:
            raise ManifestError(f"Duplicate reading filename: {filename}")
        seen_numbers.add(number)
        seen_files.add(filename.casefold())

        path = source_path(reading_dir, filename)
        status = str(raw.get("status", "pending")).strip()
        if status not in ALLOWED_STATUS:
            raise ManifestError(f"Invalid status for article {number}: {status}")
        citation = str(raw.get("citation", "")).strip()
        if not citation:
            raise ManifestError(f"Article {number} requires a citation")

        articles.append(
            {
                "number": number,
                "weeks": normalize_weeks(raw.get("weeks")),
                "sourceName": path.name,
                "citation": citation,
                "pageCount": pdf_page_count(path),
                "sourceFingerprint": sha256_file(path),
                "status": status,
            }
        )

    return {
        "schemaVersion": 1,
        "courseKey": key,
        "articleCount": len(articles),
        "articles": articles,
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course-key", required=True)
    parser.add_argument("--reading-dir", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = build_manifest(args.course_key, args.reading_dir, read_json(args.mapping))
        write_json(args.output, manifest)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {manifest['articleCount']} articles to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
