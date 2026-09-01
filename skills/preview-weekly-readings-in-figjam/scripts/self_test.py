#!/usr/bin/env python3
"""Dependency-light smoke tests for manifest and registry scripts."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def run(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, check=False, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


def fake_pdf(path: Path, pages: int) -> None:
    markers = "\n".join(f"{i + 1} 0 obj << /Type /Page >> endobj" for i in range(pages))
    path.write_bytes(f"%PDF-1.4\n{markers}\n%%EOF\n".encode("ascii"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="weekly-reading-skill-") as tmp:
        root = Path(tmp)
        readings = root / "readings"
        readings.mkdir()
        fake_pdf(readings / "01-example.pdf", 2)
        fake_pdf(readings / "02-example.pdf", 3)

        mapping = root / "mapping.json"
        mapping.write_text(
            json.dumps(
                {
                    "articles": [
                        {
                            "number": 1,
                            "weeks": ["W02"],
                            "filename": "01-example.pdf",
                            "citation": "Example Author (2024)",
                        },
                        {
                            "number": 2,
                            "weeks": ["W03", "W04"],
                            "filename": "02-example.pdf",
                            "citation": "Another Author (2025)",
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )
        manifest = root / "manifest.json"
        run(
            sys.executable,
            str(HERE / "build_reading_manifest.py"),
            "--course-key",
            "COURSE-101",
            "--reading-dir",
            str(readings),
            "--mapping",
            str(mapping),
            "--output",
            str(manifest),
        )
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert data["articleCount"] == 2
        assert data["articles"][0]["pageCount"] == 2
        assert data["articles"][1]["weeks"] == ["W03", "W04"]
        serialized = manifest.read_text(encoding="utf-8")
        assert str(root) not in serialized

        registry = root / "registry.json"
        run(
            sys.executable,
            str(HERE / "reading_registry.py"),
            "init",
            "--registry",
            str(registry),
            "--course-key",
            "COURSE-101",
            "--course-hub-key",
            "hub-key",
            "--course-hub-url",
            "https://www.figma.com/board/hub-key/example",
            "--index-key",
            "index-key",
            "--index-url",
            "https://www.figma.com/board/index-key/example",
        )
        first = data["articles"][0]
        run(
            sys.executable,
            str(HERE / "reading_registry.py"),
            "upsert",
            "--registry",
            str(registry),
            "--course-key",
            "COURSE-101",
            "--number",
            "1",
            "--weeks",
            "W02",
            "--source-name",
            first["sourceName"],
            "--fingerprint",
            first["sourceFingerprint"],
            "--file-key",
            "article-key",
            "--url",
            "https://www.figma.com/board/article-key/example",
            "--status",
            "complete",
        )
        run(
            sys.executable,
            str(HERE / "reading_registry.py"),
            "validate",
            "--registry",
            str(registry),
            "--course-key",
            "COURSE-101",
        )
        registry_text = registry.read_text(encoding="utf-8")
        assert str(root) not in registry_text
        assert "translation" not in registry_text.lower()

    print("self-test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
