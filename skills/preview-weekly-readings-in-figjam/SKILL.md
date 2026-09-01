---
name: preview-weekly-readings-in-figjam
description: Build or continue bilingual, source-grounded FigJam workspaces for assigned weekly academic readings. Use when a user wants to pre-study, deeply read, translate, annotate, or organize journal articles or book chapters in FigJam; create a course reading index; create one linked FigJam file per article; or reproduce a PDF-aligned companion with Chinese interpretive translation, chapter overviews, concepts, dense vocabulary, theory synthesis, and a blank question-analysis area.
---

# Preview Weekly Readings in FigJam

Turn assigned PDFs into a linked FigJam reading system designed to sit beside the original PDF. Preserve the reading experience: the PDF remains the primary text, while FigJam supplies precise location anchors, faithful Chinese interpretive translation, argument guidance, concepts, vocabulary, and a post-reading synthesis.

## Required companion skills

Before taking task actions:

1. Read the `pdf` skill completely before inspecting PDFs.
2. Read `figma-create-new-file` before every Figma `create_new_file` call.
3. Read both `figma-use` and `figma-use-figjam` before every Figma `use_figma` call.
4. If a course hub already follows `preview-course-in-figjam`, read that skill and preserve its navigation and registry conventions.

If a required Figma capability is unavailable, prepare and validate the source manifest and content plan, then report that Figma writing is blocked. Do not fabricate file URLs or node links.

## Operating modes

Choose the smallest mode that satisfies the request:

- **Initialize course readings**: inspect the assignment and reading directory, create the index, add a course-hub entry, and leave unrequested articles as inactive `Pending` cards.
- **Generate selected readings**: create or rebuild only the requested week or article files, then activate their index cards after QA.
- **Continue**: read the registry, inspect existing Figma nodes by stable names, and resume without duplicating files, cards, or content.
- **Deepen an article**: preserve the file URL and links while replacing overview-style notes with page- or section-aligned companion reading.

Default to incremental generation. Never pre-analyze every article unless the user explicitly asks for the full set.

## Workflow

### 1. Discover sources and scope

Inspect the syllabus or assignment sheet, the reading directory, the course hub, and the local route registry if present. Use only the supplied sources unless the user explicitly authorizes external research.

Resolve:

- course key and course title;
- teaching week for every assigned reading;
- stable article number, citation, source filename, page count, and source fingerprint;
- existing hub, reading index, article file, and return-link destinations;
- requested article range and desired translation density.

An article spanning several teaching weeks still receives exactly one index card and one article file. Record all applicable week labels on that card.

Create a mapping JSON and run:

```bash
python3 scripts/build_reading_manifest.py \
  --course-key "COURSE-KEY" \
  --reading-dir "/absolute/path/to/readings" \
  --mapping "/absolute/path/to/mapping.json" \
  --output "/tmp/COURSE-KEY-reading-manifest.json"
```

The manifest may contain filenames, fingerprints, page counts, citations, weeks, and status. It must not contain article text, translations, credentials, personal paths, or Figma secrets.

### 2. Plan navigation before content

Use this stable route:

`Course Hub → Weekly Readings Index → Article File → Index / Course Hub`

The index contains exactly one card per manifest article. Pending cards are visibly inactive. An article card becomes clickable only after its article file passes QA. Related course-week cards may link to the reading index, but do not disturb the existing course layout.

Read `references/state-schema.md`. Initialize or validate the registry with `scripts/reading_registry.py`. Store only routing metadata, never prose from a reading.

### 3. Extract and map the article

Read the complete article in PDF order. Exclude the bibliography from paragraph-by-paragraph translation unless the user asks for it. Build an internal content plan with:

- article metadata and page ranges;
- section boundaries and each section's role in the argument;
- every substantive paragraph or coherent paragraph cluster;
- a unique locator: PDF page, left/right column when applicable, unit number, and a very short English anchor;
- key terms at first meaningful occurrence;
- examples, mechanisms, claims, evidence status, limitations, and inferential boundaries.

Do not use the abstract as a substitute for the body. Do not invent empirical confirmation for a conceptual or theoretical paper.

### 4. Write source-grounded companion content

Read `references/content-policy.md`. For each reading unit, create:

1. **Locator** — PDF page, column/section, unit number, and a short English anchor.
2. **中文伴读释译** — faithful Chinese interpretive translation that preserves key English terms and argumentative relationships; do not reproduce long English passages.
3. **论证功能 / 章节概述** — explain what this unit does, how it connects, and why an example appears.
4. **概念与词汇** — place explanations directly below the translation.

At each new section, add a side overview stating the section question, link from the previous section, mechanism to track, key concepts/examples, and resulting conclusion.

Vocabulary must have real learning value. Default target:

- page-level units: about 16–22 combined concepts and vocabulary items per PDF page;
- wider page-range units: at least 12 vocabulary items plus 4 core concepts per unit;
- each entry: English term, concise Chinese meaning, contextual use, and first page;
- include academic verbs, argument-signalling phrases, mechanism terms, and easily confused pairs—not only headline concepts.

Avoid padding with trivial words or duplicates. For a single-word annotation request, give the contextual translation immediately and add it to the relevant unit if it meets the vocabulary criteria.

### 5. Build the article board

Read `references/figjam-layout.md` and `references/figma-build-patterns.md`. The article board must flow vertically in PDF order:

1. top navigation, local source filename, reading instructions, and course AI-policy notice;
2. compact reading guide and argument route;
3. page/section-aligned companion units;
4. full-article theory and viewpoint synthesis;
5. `问题解析 Question Analysis` followed by a large editable blank area.

Do not add prompts, questions, tags, or answers inside the blank question-analysis area.

Use stable node names and idempotent writes. Build in bounded batches, inspect after each batch, and return every mutated node ID from `use_figma`.

### 6. Synthesize only after the reading flow

The final synthesis must include, when supported by the article:

- core proposition and complete causal or conceptual model;
- comparison matrix for major constructs;
- relationships among mechanisms, engagement, and outcomes;
- how examples or evidence support each mechanism;
- trade-offs, paradoxes, boundary conditions, and design implications;
- theoretical contribution;
- claims awaiting empirical testing and conclusions that must not be overextended;
- a term index pointing back to first occurrence.

Every major synthesis claim must be traceable to PDF pages. Place this section after the last reading unit so it does not replace the reading process.

### 7. Link, register, and activate

After the article file passes QA:

- link its index card;
- verify both return links;
- add or preserve the course-hub shortcut;
- update the registry status to `complete`;
- never store generated translation or source text in the registry.

Use `scripts/reading_registry.py validate` before reporting completion.

### 8. Visual and semantic QA

Inspect the index and representative article regions with screenshots. At minimum check:

- global reading guide;
- first content page;
- every section transition;
- final content page and synthesis;
- blank question-analysis area.

Verify:

- all assigned readings appear exactly once;
- requested article links and return links work;
- every substantive reading unit has a unique source locator;
- text remains readable when the PDF and FigJam each occupy half the screen;
- no clipping, overlap, accidental empty regions, literal `\\n`, or tiny text;
- concepts appear near their relevant translation and the term index points back correctly;
- the question area contains only its bilingual title and blank editable canvas;
- no PDF page image, long English excerpt, unsupported conclusion, external-source claim, personal path, or credential appears on the board or in the registry.

Do not activate an article card until these checks pass.

## Output report

Report the course hub, reading index, and created or updated article links; completed and pending article counts; source scope; and QA performed. Mention any article whose source was missing, unreadable, or mismatched instead of silently skipping it.

## References and scripts

- `references/content-policy.md` — source, translation, copyright, vocabulary, AI-policy, and question-area rules.
- `references/figjam-layout.md` — exact index and article-board information architecture.
- `references/figma-build-patterns.md` — idempotent creation, links, batching, and audit patterns.
- `references/state-schema.md` — manifest and route-registry schemas.
- `scripts/build_reading_manifest.py` — deterministic source inventory and fingerprints.
- `scripts/reading_registry.py` — routing metadata lifecycle and validation.
- `scripts/self_test.py` — local smoke test for both scripts.
