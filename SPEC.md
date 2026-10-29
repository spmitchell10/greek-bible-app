# Spec: OpenBible-style study workspace

Status: proposed  
Baseline: `main` as of 27 Oct 2026 (`3043e70`, click-to-inspect)  
Comparison target: the public app at [theopenbible.app](https://theopenbible.app/)

This spec turns the study-workspace plan into work this repository can accept. It keeps Flask, SQLite, and the existing query language. It does not reproduce OpenBible's library.

## Goal

A person can search, read, and inspect a Greek word without leaving the page, then see an English verse and a real lexicon entry for that word.

After the first four phases, the app should feel like OpenBible's study loop for the Greek New Testament:

- Search on the left, reading in the middle, word analysis on the right, styled like OpenBible's desktop panes (see Look and feel).
- The command line still accepts the syntax in `SEARCH_SYNTAX.md`. It also accepts a plain verse reference, which moves Browse, and the three main BibleWorks search forms (`.`, `'`, `/`).
- Hovering a Greek word fills the analysis pane from `/api/word-info`. Clicking pins it.
- Selecting a search hit moves Browse to that verse.
- The reading pane can show the Greek text alone or beside one public-domain English version.
- The analysis pane can open a lexicon article, not only the one-line MorphGNT gloss.
- A verse can list Treasury of Scripture Knowledge references.

`*rel` and `*inf` stay. They are not in OpenBible. Discourse features in `DISCOURSE_FEATURES_PLAN.md` stay out of this sequence.

## Non-goals

- Copying files, databases, or lexicons from theopenbible.app. This includes its CSS, icons, and JavaScript: the look is reproduced with this repository's own stylesheet.
- Shipping NA28, BDAG, HALOT, LSJ, TDNT, or any other text this project does not have a license to redistribute.
- Matching OpenBible's 369-text catalog, maps, manuscript images, or media modules.
- Replacing Flask or moving SQLite into the browser. OpenBible runs SQLite in a browser Web Worker, which is why its search works offline. This app keeps SQLite on the server, so offline search is a known difference (see phase 6).
- Authentication, accounts, or sync.
- Changing the meaning of the current search syntax. The BibleWorks forms are added beside it, not in place of it.
- BibleWorks morphology codes. After `@`, codes keep this app's meaning in every search form.

## What the repo already does

Use these pieces. Do not rewrite them for phase 1.

| Piece | Where |
| --- | --- |
| Flask routes for search, reading, books, stats, and word info | `app.py` |
| Query language (`*`, `[Book] +`, `@`, `&`, `W#`, `*rel`, `*inf`) | `query_parser.py`, `relative_search.py`, `inference_search.py` |
| MorphGNT words, lemmas, morphology | `setup_database.py`, table `words` |
| One-line English gloss by lemma | table `lexicon`, `import_lexicon.py` |
| Reading view and click popup | `templates/index.html`, `static/script.js`, `GET /api/word-info` |
| Partial LXX import | `lxx_importer.py` (12 Minor Prophets) |
| Verse reference parser (`Rom 8:1`, `1 Cor 8:1`) | `parse_verse_reference` in `relative_search.py` |
| `*rel` re-search with selected words | `POST /api/relative-search` |

`GET /api/word-info?id=<word_id>` already returns surface form, lemma, parsing, gloss, book count, and NT count. The popup (`#word-popup`) is the analysis pane in miniature.

The page today is one column: reading controls, then the command line (`#advanced-search`), then results. Search and reading are alternatives ("OR"), not neighbors.

## Target layout

Desktop, wide window:

```
+------------------+------------------------+------------------+
| Search           | Browse                 | Analysis         |
| command line     | version, book, chapter | lemma, parsing   |
| corpus checkboxes| Greek text             | gloss, frequency |
| result list      | optional English column| lexicon (later)  |
+------------------+------------------------+------------------+
```

- Search keeps `#advanced-search`, the help panel, corpus checkboxes, the `*rel` word-selection panel, and the results list. Selecting a hit moves Browse to that verse.
- Browse keeps book, chapter, corpus, and verse/paragraph display. Add a version control when phase 2 lands. Remove the "OR" divider so both panes are visible together.
- Analysis is the current popup's content, docked and persistent, inside a tab strip. Phase 1 has one tab, **Analysis**. X-Refs (phase 4) and later tabs join the same strip.
- Hovering a word in Browse or in a search result updates Analysis after about 60 ms. Clicking a word pins it: Analysis keeps that word until another word is clicked. Moving the mouse off a pinned word does not clear it.
- **Freeze** holds the current word against both hover and click until Freeze is turned off.
- Before any word is chosen, Analysis says: "Move the mouse over a word in the Browse pane to see its parsing here. Click a word to keep it."
- Below about 1100px wide, or on a touch-first device (`(pointer: coarse)`), the three regions become Search, Browse, and Analysis tabs. On touch, the first tap on a word shows it in Analysis. The existing popup may remain as a fallback only if the analysis tab is hidden.

Resizable splits are optional. A fixed three-column grid satisfies phase 1.

## Look and feel

The target is OpenBible's desktop-application look, written as this repository's own CSS. `features.md` ("The shell around the windows") records what was observed.

Pane chrome:

- Each pane has a dark title bar with a menu row, as OpenBible does:
  - Search: "Search", then Help (the existing `?` panel) and Options. Copy and Tools stay out until there is something behind them.
  - Browse: "Browse", then the book, chapter, and corpus selectors and the verse/paragraph control. Phase 2 adds the version control here.
  - Analysis: "Analysis", then Freeze, then the tab strip.
- The command line sits at the top of the Search pane, full pane width, with the placeholder "Enter search words or verse here". A one-line message area sits under it for errors and notices.
- Panes are separated by 1px lines, not cards, shadows, or gaps.

Tokens. Define these as CSS custom properties on `:root` and use only them in pane styles:

| Token | Use | Light starting value |
| --- | --- | --- |
| `--chrome`, `--chrome-ink` | Title bars and menus | `#333333`, `#ffffff` |
| `--bg`, `--ink` | Pane background and text | `#ffffff`, `#1a1a1a` |
| `--panel`, `--line` | Secondary background and borders | mixed from `--bg` and `--ink` |
| `--sel-bg` | Selected hit, pinned word | `#d9d6d6` |
| `--sel-strong`, `--focus` | Accent and focus ring | `#cc4411` |
| `--lemma`, `--ref`, `--link` | Lemma text, references, links | pick for contrast |

The chrome and accent values are the BibleWorks scheme colors OpenBible ships. OpenBible's default light and dark values were not retrievable. Before phase 1 closes, compare screenshots of the two apps side by side and adjust the starting values.

Type:

- Greek: SBL BibLit, falling back to Gentium Plus and then serif. Check the SBL font license before bundling the file. Gentium Plus is under the SIL Open Font License.
- Sizes: Greek text 20px, English text 17px, UI 15px, small UI 13px.
- Density: compact rows (about 24px in lists on desktop), small menus, and no large buttons. On touch, targets are at least 44px.

Keyboard:

- Command line: Enter runs, Escape clears, Up and Down walk history.
- Results list: Up, Down, Page Up, Page Down, Home, and End move the selection, and Browse follows.

## Command line

One field, `#advanced-search`, does search and navigation. Input is read in this order:

1. **Current syntax.** Text starting with `*` or `[`, or with `rel ` or `inf ` (any case), goes to `parse_query` unchanged.
2. **BibleWorks forms** (phase 1b). Text starting with `.`, `'`, or `/`:
   - `.w1 w2` finds verses containing every word, in any order.
   - `'w1 w2` finds the words as an adjacent phrase. This is the same search as `*w1 & w2`.
   - `/w1 w2` finds verses containing any of the words.
   - A word may carry `@codes` with this app's meaning. Words match by lemma, as bare words do in `parse_query` today (`lemma = ?`). BibleWorks matches inflected forms here. Form matching is out of scope until a later change to this spec.
   - `;`, `(`, `~`, and `=` are reserved. They show "That BibleWorks search form is not supported yet."
3. **Reference.** Text that parses as a reference (`Rom 8:28`, `1 Cor 13`, `John 3:16`) moves Browse to that chapter and verse. A chapter-only reference opens verse 1. Extend `parse_verse_reference` for chapter-only input. Do not write a second parser.
4. **Anything else** goes to `parse_query` as it does today, so existing bare queries keep working.
5. If `parse_query` cannot read it either (an error or no terms), the message line shows: "Not a search or a reference. Start a search with * . ' or /, or type a reference like Rom 8:28."

History stores every entry that ran. Up and Down step through it.

## Licensing

Every imported text records `source_name`, `source_url`, and `license` in the database and in this file's phase notes when the import lands.

Allowed for this spec:

- MorphGNT / SBLGNT, already imported (CC BY-SA).
- A public-domain English Bible: WEB, KJV, or ASV. Pick one in phase 2 and stay with it until alignment is solid.
- A public-domain or openly licensed Greek lexicon with article text, such as Abbott-Smith. The MorphGNT gloss table is not that lexicon.
- Treasury of Scripture Knowledge (public domain).

Not allowed:

- Downloading `/data/` from theopenbible.app and loading it here.
- BDAG, HALOT, LSJ, or a commercial NA edition, unless a later change to this spec names the license and the files are obtained from the publisher.

## Data model

Phase 1 adds no tables. Later phases add the tables below. Greek tokens stay in `words`. English verses and lexicon articles do not become rows of `words`.

Book identity stays the current scheme: NT `01`–`27`, LXX `40`–`78`. English verses use those NT codes. A `verse_map` is required wherever a source's chapter or verse numbering differs (Psalms and the LXX are the known cases). Do not assume `book + chapter + verse` matches across versions until that row exists.

```sql
CREATE TABLE sources (
    id TEXT PRIMARY KEY,          -- 'sblgnt', 'web', 'abbott-smith', 'tsk'
    name TEXT NOT NULL,
    kind TEXT NOT NULL,           -- 'bible' | 'lexicon' | 'crossrefs'
    language TEXT NOT NULL,
    license TEXT NOT NULL,
    source_url TEXT NOT NULL
);

CREATE TABLE version_verses (
    source_id TEXT NOT NULL,
    book_code TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (source_id, book_code, chapter, verse)
);

CREATE TABLE lexicon_entries (
    source_id TEXT NOT NULL,
    lemma TEXT NOT NULL,          -- same lemma string as words.lemma
    entry TEXT NOT NULL,
    PRIMARY KEY (source_id, lemma)
);

-- One row per verse whose number differs between a source and the
-- canonical scheme (NT: SBLGNT; LXX: the LXX import). Verses with no
-- row map to the same book, chapter, and verse.
CREATE TABLE verse_map (
    source_id TEXT NOT NULL,
    book_code TEXT NOT NULL,
    chapter INTEGER NOT NULL,     -- in the source's numbering
    verse INTEGER NOT NULL,
    canon_book_code TEXT NOT NULL,
    canon_chapter INTEGER NOT NULL,
    canon_verse INTEGER NOT NULL,
    PRIMARY KEY (source_id, book_code, chapter, verse)
);

CREATE TABLE cross_refs (
    source_id TEXT NOT NULL,
    from_book TEXT NOT NULL,
    from_chapter INTEGER NOT NULL,
    from_verse INTEGER NOT NULL,
    to_book TEXT NOT NULL,
    to_chapter INTEGER NOT NULL,
    to_verse INTEGER NOT NULL
);
```

Hebrew (phase 5) is a new `corpus` value, not extra columns on Greek morphology. Packard and MorphGNT codes do not describe Hebrew. That phase adds its own morphology fields and a verse map onto the English and LXX texts.

## API

Phase 1 uses the routes that exist and adds one. Phase 1b extends one.

| When | Route | Behavior |
| --- | --- | --- |
| Phase 1 | `GET /api/word-info` | Unchanged response. The analysis pane renders it. Hover requests for a word already shown are not repeated. |
| Phase 1 | `POST /api/read`, `POST /api/advanced-search` | Unchanged. Browse and Search call them as they do now. |
| Phase 1 | `GET /api/resolve-ref` | Query: `q`. Returns `book_code`, `chapter`, `verse`, and `corpus`, or 404 when `q` is not a reference. Uses `parse_verse_reference`. |
| Phase 1b | `POST /api/advanced-search` | Also accepts queries starting with `.`, `'`, or `/`. Existing queries return what they return today. |
| Phase 2 | `GET /api/sources` | Lists bible sources and licenses. |
| Phase 2 | `GET /api/verse-text` | Query: `source`, `book_code`, `chapter`. Returns the English (or other) verses for that chapter. |
| Phase 3 | `GET /api/lexicon` | Query: `lemma`. Returns the article, or 404 when the lemma is absent. |
| Phase 4 | `GET /api/cross-refs` | Query: `book_code`, `chapter`, `verse`. Returns reference pairs for that verse. |

Search continues to run on `words`. A hit's English line is a lookup in `version_verses`, not a second morphological index.

## Phases

Each phase is done only when its checks pass. Later phases may start after the previous phase's checks pass.

### Phase 1 — Workspace

Effort: 3–5 weeks.

Put Search, Browse, and Analysis on one screen with OpenBible's pane chrome and tokens. Wire Analysis to the existing word-info API with hover, pin, and Freeze. Make the command line navigate by reference. No new corpus.

Acceptance:

- At a wide window, all three regions are visible at once, each with a dark title bar and its menu row as described in Look and feel.
- Pane styles use only the tokens in Look and feel. Changing `--chrome` in one place changes all three title bars.
- Greek renders in SBL BibLit or the Gentium Plus fallback at 20px.
- A side-by-side screenshot with OpenBible at the same window size shows the same arrangement: title bars, command line at the top of Search, a tab strip in Analysis.
- Running `*λόγος@Nsg` still returns the same kind of results as today, in the Search region.
- Typing `Rom 8:28` and pressing Enter moves Browse to Romans 8 with verse 28 in view. `1 Cor 13` opens 1 Corinthians 13:1.
- Typing text that is neither a search nor a reference shows the message from the Command line section and changes nothing else.
- Up and Down in the command line step through earlier entries. Escape clears the field.
- Selecting a search hit, by click or by Up/Down/Page Up/Page Down/Home/End, moves Browse to that verse.
- Loading Matthew 1 in Browse still shows the Greek text, verse mode and paragraph mode.
- Hovering a word in Browse fills Analysis with surface form, lemma, parsing, gloss, and both frequencies, matching `/api/word-info`. Hovering a word in a search result does the same.
- Clicking a word pins it. Moving the mouse over other words then leaves Analysis unchanged until another word is clicked.
- Freeze holds the current analysis against hover and click. Turning Freeze off makes the next hover or click update it.
- `*rel Rom. 8:1` still shows the word-selection panel and can be re-run.
- `*inf John 1:1` still color-codes parts of speech.
- Narrow viewport, or a touch-first device, shows three tabs instead of three columns. A tap on a word shows it in Analysis.
- Existing routes and the query syntax are unchanged. `GET /api/resolve-ref` is the only new route.

### Phase 1b — BibleWorks search forms

Effort: 1–2 weeks. May run alongside phase 2.

Add the `.`, `'`, and `/` forms from the Command line section on top of the existing query engine.

Acceptance:

- `'ἐν ἀρχή` returns the same verses as `*ἐν & ἀρχή`.
- `.θεός ἀγάπη` returns verses containing both words in any order, including verses where they are not adjacent.
- `/θεός κύριος` returns verses containing either word. The count equals the union of the two single-word searches.
- `@codes` on a word in these forms filter it exactly as in `*` searches.
- `;`, `(`, `~`, and `=` show the "not supported yet" message.
- Every query in `SEARCH_SYNTAX.md` returns the same results as before phase 1b.
- `SEARCH_SYNTAX.md` and the `?` help panel document the three forms.

### Phase 2 — Second version

Effort: 3–5 weeks.

Add one public-domain English Bible, aligned to NT `book_code`, chapter, and verse.

Acceptance:

- The source row records name, URL, and license.
- Browse can show Greek only, or Greek and English for the same chapter.
- A missing English verse leaves a visible gap and does not shift later verses.
- A search hit can show the English of that verse under the Greek.
- LXX chapters, which have no English row yet, stay Greek-only.
- Re-running `setup_database.py` does not duplicate English rows.

### Phase 3 — Lexicon article

Effort: 3–6 weeks.

Add one open Greek lexicon keyed by the same lemma strings stored in `words.lemma`. Keep the MorphGNT gloss. The article is additional.

Acceptance:

- Analysis shows the one-line gloss and, when present, the lexicon article.
- A lemma with no article says so, and the parsing still renders.
- Lemmas that differ by accent or final sigma are matched through one documented normalization step. The rule is written next to the importer.
- The source row records name, URL, and license.
- The article text is stored locally. The pane does not depend on a live call to another site.

### Phase 4 — Cross-references

Effort: 2–3 weeks.

Import Treasury of Scripture Knowledge as verse-to-verse links.

Acceptance:

- Opening a verse in Browse lists its references as book, chapter, and verse.
- Choosing a reference loads that passage in Browse.
- A verse with no references shows an empty list, not an error.
- `*rel` and `*inf` still run and are labeled as similarity search, distinct from these fixed references.
- Book names in the source file map onto `books.book_code`. Unmapped names fail the import with a report, rather than being skipped silently.

### Phase 5 — Hebrew and a full Septuagint

Effort: 2–4 months. Start only after phase 4.

Finish the LXX import beyond the 12 Minor Prophets. Add one morphology-tagged Hebrew text (Open Scriptures Hebrew Bible or MACULA). Align both to the English version through `verse_map` wherever numbering differs.

Acceptance:

- Every LXX book this importer claims to support can be opened in Browse.
- Hebrew morphology is queryable with its own codes, documented in `SEARCH_SYNTAX.md`, and those codes are not MorphGNT codes.
- A sample of Psalms references demonstrates the verse map (Hebrew numbering versus the English text).
- License rows exist for both corpora.

### Phase 6 — Installable app

Effort: 2–4 weeks.

Make the site installable and usable offline for texts already imported. SQLite stays on the server unless a later spec moves it.

Acceptance:

- A service worker caches the app shell and the last-opened chapter.
- Light, dark, and system theme. The choice persists in `localStorage`.
- The phone tab layout from phase 1 is the installed phone layout.
- Search still requires the local server. Offline use covers the shell and cached reading, and it says so when a search cannot run. This is where the app differs most from OpenBible, which searches offline. Closing that gap would mean moving SQLite into the browser, which needs a spec change.

## Out of this sequence

Do not schedule these until phase 4 is in use:

- Maps, manuscript images, audio.
- The discourse layer in `DISCOURSE_FEATURES_PLAN.md`.
- Bookmarks, notes, and accounts (`ARCHITECTURE.md` future list).
- More English versions. One aligned text is enough to prove the column.

## Done

The spec is satisfied for a daily Greek study app when phases 1, 1b, and 2–4 pass. Phases 5 and 6 are the wider library and the installable shell. They are not required for the app to resemble OpenBible's study loop.

## Source of this plan

Written from this repository (`README.md`, `ARCHITECTURE.md`, `app.py`) and from the public OpenBible page: three panes (Search, Browse, Analysis), Freeze, version switching, and a large multi-language catalog. The catalog size is a boundary, not a backlog.

Revised 29 Oct 2026 after reading OpenBible's command handler, Analysis tab code, and stylesheets. That pass added the Look and feel and Command line sections, hover-to-inspect, result-driven Browse, phase 1b, and `verse_map`.
