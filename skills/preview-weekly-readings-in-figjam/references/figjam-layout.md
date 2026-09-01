# FigJam layout specification

Use native FigJam sections, shapes, text, connectors, and hyperlinks. Load fonts before text mutations. Return every mutated node ID from each write call.

## Navigation hierarchy

`Course Hub → Weekly Readings Index → Article File → Weekly Readings Index / Course Hub`

Preserve existing file URLs whenever deepening or rebuilding an article. Do not create a replacement file merely to simplify layout work.

## Weekly Readings Index

- Group cards by the assignment's teaching weeks.
- Give every assigned article exactly one stable card named `Reading Card · Rxx`.
- A multi-week article lists all weeks on its single card.
- Show article number, short citation, week, status, and concise reading focus.
- Pending cards display `待生成 Pending`, have no article-file hyperlink, and use a subdued style.
- Completed cards display `已完成 Complete` and link to the article file.
- Add an index entry in the course hub without moving or rebuilding unrelated course content.

## Article file dimensions

Design a narrow vertical companion for half-screen use. Use a consistent content width of roughly 3200–3800 canvas units and a single reading direction from top to bottom. Avoid a wide dashboard that forces horizontal panning.

Recommended geometry:

- outer margin: 120–180;
- vertical gap between major sections: 120–180;
- reading-unit gap: 72–100;
- locator column: 360–480;
- translation column: 1700–2200;
- logic/overview column: 760–980;
- internal card padding: 32–48;
- body text: at least 24–28 at the expected zoom;
- labels and metadata: at least 18–22.

Treat these as visual constraints, not arbitrary fixed sizes. Expand card height from text measurements and never clip content.

## Top area

Name stable nodes:

- `Article Header`
- `Back to Reading Index`
- `Back to Course Hub`
- `Source Instruction`
- `AI Policy`
- `Internal Navigation`
- `Reading Guide`

Show the source filename, but not an absolute local path or a fragile `file://` link. State that the original PDF should be open locally and the board should sit beside it.

Internal navigation links to each section start, the final synthesis, and the question-analysis area.

## Reading guide

Keep the pre-reading guide compact. Show:

- research or conceptual question;
- major constructs or loci;
- psychological or argumentative mechanisms;
- engagement or intermediate process;
- cognition, attitude, behavior, or other outcomes when present;
- article section order, page ranges, and each section's role.

This is orientation, not a substitute for the reading flow.

## Reading unit

Name every unit `Reading Unit · p{page-or-range} · {sequence}`. Use three aligned columns:

1. `Locator · ...` — page, column/section, unit number, and short English anchor.
2. `Translation · ...` — Chinese interpretive translation with English key terms retained.
3. `Logic · ...` — argumentative function, example role, connection, or section overview.

Under the translation, add `Concepts & Vocabulary · ...`. Keep items inside or immediately beneath the same unit; never move the only explanation to a remote glossary.

At the first unit of a section, use a visually distinct `Section Overview · {section}` card in the right column.

## Full-article synthesis

Name the section `Full Article Synthesis`. Include page references and only supported components:

- core proposition;
- complete conceptual or causal model;
- construct comparison matrix;
- mechanism relationships;
- examples/evidence map;
- trade-offs and paradoxes;
- theoretical contribution and implications;
- untested propositions and inference boundaries;
- term index with first-occurrence locator.

## Question analysis

Name the section `Question Analysis`. It must contain exactly two top-level children:

1. bilingual title;
2. large blank editable canvas.

## Visual system

Use one calm academic palette across the course. Suggested roles:

- navigation/header: deep blue;
- locator: cool gray-blue;
- translation: warm white;
- logic/overview: light blue;
- concepts: pale yellow;
- vocabulary: pale green;
- synthesis: pale violet;
- warning/policy: pale coral;
- blank question area: white with a subtle border.

Color is semantic support, not decoration. Keep contrast accessible and avoid saturated backgrounds behind long text.

## Screenshot QA

Capture and inspect:

- the full index;
- article header and reading guide;
- first reading unit;
- each major section transition;
- final reading unit and synthesis;
- question-analysis area.

Check half-screen readability, bounds, overlaps, clipping, accidental empty space, duplicate nodes, and link targets.
