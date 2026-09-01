# Preview Weekly Readings in FigJam

A Codex skill for turning assigned academic PDFs into bilingual, source-grounded FigJam companion workspaces.

The generated workspace keeps the original PDF as the primary reading surface and creates a narrow FigJam companion with precise page/section locators, faithful Chinese interpretive translation, section overviews, contextual concepts, dense vocabulary, argument guidance, final theory synthesis, and a blank question-analysis canvas.

## What it builds

```text
Course Hub
  └── Weekly Readings Index
        ├── Reading 01 FigJam
        ├── Reading 02 FigJam
        └── Pending article cards
```

Each completed article file includes:

- source filename, reading instructions, return links, and internal navigation;
- a compact argument map and section route;
- page- or section-aligned `Locator | 中文伴读释译 | 章节概述/论证功能` units;
- concepts and high-value vocabulary directly beneath the relevant translation;
- a traceable full-article model, comparison matrix, evidence boundaries, and term index;
- a large blank `问题解析 Question Analysis` area for the learner.

The skill deliberately does **not** upload PDF pages, reproduce long English passages, browse without authorization, or store article text and translations in its local registry.

## Install

Copy or symlink the skill directory into your Codex skills directory:

```bash
git clone https://github.com/3519130448wzr-alt/preview-weekly-readings-in-figjam.git
mkdir -p ~/.codex/skills
cp -R preview-weekly-readings-in-figjam/skills/preview-weekly-readings-in-figjam ~/.codex/skills/
```

The workflow expects Codex's PDF capability and Figma/FigJam tools. It also loads the prerequisite Figma skills before creating or editing files.

## Use

Invoke it explicitly:

```text
$preview-weekly-readings-in-figjam
请根据课程 syllabus、weekly reading assignment 和 Reading materials 文件夹，
建立每周阅读索引，并先完成 W02 的文章。每篇文章使用独立 FigJam 文件。
```

Continue later without duplicating work:

```text
$preview-weekly-readings-in-figjam 继续完成 W03，并把每个阅读单元的词汇增加到 16–22 个。
```

Deepen an existing overview-style article board:

```text
$preview-weekly-readings-in-figjam
保留当前 Reading 01 的 URL 和返回链接，重构为与本地 PDF 并排使用的逐页深度伴读白板。
```

## Repository layout

- `skills/preview-weekly-readings-in-figjam/SKILL.md` — workflow and trigger instructions.
- `references/` — content, layout, Figma writing, and state rules.
- `scripts/build_reading_manifest.py` — deterministic PDF inventory and fingerprints.
- `scripts/reading_registry.py` — private local route metadata lifecycle.
- `scripts/self_test.py` — dependency-light smoke test.

Run the test:

```bash
python3 skills/preview-weekly-readings-in-figjam/scripts/self_test.py
```

## Privacy and copyright

Keep course PDFs, generated translations, Figma file keys, local paths, and registry data out of Git. Only the generic skill implementation belongs in this repository.

## License

MIT
