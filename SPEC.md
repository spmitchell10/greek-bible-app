# Spec: OpenBible-style study workspace

Status: proposed  
Baseline: `main` as of 27 Oct 2026 (`3043e70`, click-to-inspect)  
Comparison target: the public app at [theopenbible.app](https://theopenbible.app/)

This spec turns the study-workspace plan into work this repository can accept. It keeps Flask, SQLite, and the existing query language. It does not reproduce OpenBible's library.

## Goal

A person can search, read, and inspect a Greek word without leaving the page, then see an English verse and a real lexicon entry for that word.

After the first four phases, the app should feel like OpenBible's study loop for the Greek New Testament:

- Search on the left, reading in the middle, word analysis on the right.
- The command line still accepts the syntax in `SEARCH_SYNTAX.md`.
- Clicking a Greek word fills the analysis pane from `/api/word-info`.
- The reading pane can show the Greek text alone or beside one public-domain English version.
- The analysis pane can open a lexicon article, not only the one-line MorphGNT gloss.
- A verse can list Treasury of Scripture Knowledge references.

`*rel` and `*inf` stay. They are not in OpenBible. Discourse features in `DISCOURSE_FEATURES_PLAN.md` stay out of this sequence.

## Non-goals

- Copying files, databases, or lexicons from theopenbible.app.
- Shipping NA28, BDAG, HALOT, LSJ, TDNT, or any other text this project does not have a license to redistribute.
- Matching OpenBible's 369-text catalog, maps, manuscript images, or media modules.
- Replacing Flask or moving SQLite into the browser.
- Authentication, accounts, or sync.
- Changing the meaning of the current search syntax.

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

- Search keeps `#advanced-search`, the help panel, corpus checkboxes, the `*rel` word-selection panel, and the results list.
- Browse keeps book, chapter, corpus, and verse/paragraph display. Add a version control when phase 2 lands. Remove the "OR" divider so both panes are visible together.
- Analysis is the current popup, docked and persistent. A click in Browse or in a search result updates it.
- **Freeze** stops later clicks from replacing the current word until Freeze is turned off.
- Below about 1100px, the three regions become Search, Browse, and Analysis tabs. The existing popup may remain as a fallback only if the analysis tab is hidden.

Resizable splits are optional. A fixed three-column grid satisfies phase 1.

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

Phase 1 uses the routes that exist.

| When | Route | Behavior |
| --- | --- | --- |
| Phase 1 | `GET /api/word-info` | Unchanged response. The analysis pane renders it. |
| Phase 1 | `POST /api/read`, `POST /api/advanced-search` | Unchanged. Browse and Search call them as they do now. |
| Phase 2 | `GET /api/sources` | Lists bible sources and licenses. |
| Phase 2 | `GET /api/verse-text` | Query: `source`, `book_code`, `chapter`. Returns the English (or other) verses for that chapter. |
| Phase 3 | `GET /api/lexicon` | Query: `lemma`. Returns the article, or 404 when the lemma is absent. |
| Phase 4 | `GET /api/cross-refs` | Query: `book_code`, `chapter`, `verse`. Returns reference pairs for that verse. |

Search continues to run on `words`. A hit's English line is a lookup in `version_verses`, not a second morphological index.

## Phases

Each phase is done only when its checks pass. Later phases may start after the previous phase's checks pass.

### Phase 1 — Workspace

Effort: 2–4 weeks.

Put Search, Browse, and Analysis on one screen. Wire Analysis to the existing word-info API. No new corpus.

Acceptance:

- At a wide window, all three regions are visible at once.
- Running `*λόγος@Nsg` still returns the same kind of results as today, in the Search region.
- Loading Matthew 1 in Browse still shows the Greek text, verse mode and paragraph mode.
- Clicking a word in Browse fills Analysis with surface form, lemma, parsing, gloss, and both frequencies, matching `/api/word-info`.
- Clicking a word in a search result does the same.
- Freeze holds the current analysis while other words are clicked. Turning Freeze off makes the next click update it.
- `*rel Rom. 8:1` still shows the word-selection panel and can be re-run.
- `*inf John 1:1` still color-codes parts of speech.
- Narrow viewport shows three tabs instead of three columns.
- Existing routes and the query syntax are unchanged.

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
- Search still requires the local server. Offline use covers the shell and cached reading, and it says so when a search cannot run.

## Out of this sequence

Do not schedule these until phase 4 is in use:

- Maps, manuscript images, audio.
- The discourse layer in `DISCOURSE_FEATURES_PLAN.md`.
- Bookmarks, notes, and accounts (`ARCHITECTURE.md` future list).
- More English versions. One aligned text is enough to prove the column.

## Done

The spec is satisfied for a daily Greek study app when phases 1–4 pass. Phases 5 and 6 are the wider library and the installable shell. They are not required for the app to resemble OpenBible's study loop.

## Source of this plan

Written from this repository (`README.md`, `ARCHITECTURE.md`, `app.py`) and from the public OpenBible page: three panes (Search, Browse, Analysis), Freeze, version switching, and a large multi-language catalog. The catalog size is a boundary, not a backlog.
