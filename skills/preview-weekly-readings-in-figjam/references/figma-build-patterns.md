# Figma build patterns

## Idempotency

Before creating anything, inspect the current file and search by stable node names. Update matching nodes in place. Create only missing nodes. Never assume that an earlier write completed if the tool reported failure.

Use stable names from `figjam-layout.md`, plus:

- index group: `Reading Week · Wxx`;
- article card: `Reading Card · Rxx`;
- section start: `Section Start · {article-section}`;
- summary block: `Synthesis · {topic}`;
- vocabulary item: `Vocab · p{page} · {normalized-term}`.

## Batching

Keep each write bounded. A practical sequence is:

1. header, navigation, and reading guide;
2. two to four reading units per call;
3. synthesis blocks;
4. question-analysis area;
5. hyperlinks and status changes;
6. audit-only calls.

If a call times out or fails, inspect file state before retrying. Retrying the entire file risks duplication.

## Layout calculation

Calculate each text panel's height from wrapped line count, font size, line height, and padding. Position the next unit from the maximum bottom edge of the current unit's three columns plus the vertical gap.

Do not stretch the locator or logic column to match a very long translation unless the background design requires it. Align the column tops and let the outer reading-unit section contain the tallest child.

## Hyperlinks

- Use file URLs for navigation between FigJam files.
- Use internal node hyperlinks for section navigation inside an article.
- Verify the destination after writing each link.
- Pending article cards must not contain a stale or placeholder link.
- When rebuilding, preserve the current file URL and existing valid return destinations.

## Text mutation

Load every font used by a text node before changing its characters or style. Prefer fonts with dependable Chinese and Latin coverage. Keep English terms unbroken when possible.

Never inject the two-character sequence `\\n` into displayed text. Use actual line breaks.

## Audit queries

After writing, programmatically inspect:

- counts of `Reading Card ·` nodes against the manifest;
- uniqueness of `Reading Unit ·` and `Vocab ·` names;
- text and child count of `Question Analysis`;
- non-empty hyperlinks on completed cards and return buttons;
- absence of hyperlinks on pending cards;
- node bounds and pairwise overlap within each reading unit;
- text nodes whose rendered bounds exceed their parent;
- vocabulary count per unit;
- absolute local paths, `file://`, long English blocks, and literal `\\n`.

Return an audit summary with mutated node IDs, created/updated counts, and violations. Fix violations before activating the index card.

## Failure boundaries

- Missing article PDF: leave the card pending and report the filename.
- Assignment/PDF mismatch: do not guess the mapping; surface the conflicting entries.
- Existing article file with unexpected structure: inspect and preserve useful content, file URL, and links; rebuild in named sections.
- Unreadable or scanned PDF: use the PDF skill's approved OCR path and mark low-confidence locators for manual review.
- Figma permission/tool failure: stop before registry status or index activation changes.
