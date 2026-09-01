# State schemas

The manifest and registry are routing aids, not a note database. Never store source text, translations, summaries, vocabulary explanations, credentials, absolute local paths, or personal information.

## Reading manifest

`build_reading_manifest.py` writes:

```json
{
  "schemaVersion": 1,
  "courseKey": "COURSE-101",
  "articleCount": 2,
  "articles": [
    {
      "number": "01",
      "weeks": ["W02"],
      "sourceName": "01-example.pdf",
      "citation": "Example Author (2024)",
      "pageCount": 12,
      "sourceFingerprint": "sha256:...",
      "status": "pending"
    }
  ]
}
```

Input mapping JSON:

```json
{
  "articles": [
    {
      "number": "01",
      "weeks": ["W02"],
      "filename": "01-example.pdf",
      "citation": "Example Author (2024)",
      "status": "pending"
    }
  ]
}
```

Article numbers and filenames must be unique. `weeks` must be a non-empty list. `status` is `pending`, `in_progress`, or `complete`.

## Route registry

```json
{
  "schemaVersion": 1,
  "courses": {
    "COURSE-101": {
      "courseHub": {
        "fileKey": "opaque-key",
        "url": "https://www.figma.com/board/..."
      },
      "readingIndex": {
        "fileKey": "opaque-key",
        "url": "https://www.figma.com/board/..."
      },
      "articles": {
        "01": {
          "weeks": ["W02"],
          "sourceName": "01-example.pdf",
          "sourceFingerprint": "sha256:...",
          "fileKey": "opaque-key",
          "url": "https://www.figma.com/board/...",
          "status": "complete",
          "updatedAt": "2026-01-01T00:00:00+00:00"
        }
      }
    }
  }
}
```

`complete` requires an article URL and file key. An index may be registered before any article is complete. If a source fingerprint changes, treat the existing content as stale and inspect the replacement PDF before updating the board.
