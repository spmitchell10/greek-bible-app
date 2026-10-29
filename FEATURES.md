# OpenBible feature inventory

Observed 28 Oct 2026 from the public app at [theopenbible.app](https://theopenbible.app/): the page, its styles, and the script the browser loads. Rechecked 29 Oct 2026 against `sw.js`, `boot.js`, the main app bundle (`/a/app-*.js`), `workspace.css`, and `mobile.css`. This file describes what the app does. It is the companion to `spec.md`, which is the build plan for this repository. It is not a copy of OpenBible's texts, images, or lexicons.

The app is a web build of BibleWorks 10 (its stored preferences are named `bw10.*` and its help pages are the BibleWorks help files). Three regions stay on screen together: Search, Browse, and Analysis. On a phone those same regions are tabs. A signed-in user can sync preferences. The shell can be installed and can cache reading offline.

## Command line

This is the part that feels different from the search box in greek-bible-app.

greek-bible-app has one field for a custom query (`*λόγος@Nsg`, `[Matt.] + [verb]@pAI3s`, `*rel`, `*inf`), a Search button, and a help panel you open with `?`. Reading is a separate set of controls, divided from search by an "OR".

OpenBible has one command line, labeled "Enter search words or verse here." The same field does both jobs:

- A verse reference moves Browse to that verse.
- A word or construction runs a search and fills the verse list under the field.
- The up and down arrows step through Command Line history and verse history. History stores the search version that was active, and choosing an old entry can switch the search version back.
- A favorite display set is recalled by typing `d` and its name.

How the field decides what you typed, in order (from the app's command handler):

1. Text that starts with `.` `/` `'` `;` `(` `~` or `=` is a search. These are the BibleWorks search prefixes: `.` all the words in a verse, `'` a phrase, `/` any of the words. `;` `(` and `~` start the other BibleWorks query forms, and `=` in front of a search forces the link search described below.
2. A version id on its own (`BNT`, `KJV`) makes that the search version and adds it to the display versions.
3. `limits <range>` sets the search limits.
4. Anything else is tried as a reference in the search version (`Rom 8:28`). Browse moves there.
5. A version id followed by a reference (`KJV Ps 23:1`) is read in that version's numbering and mapped to the search version's. The message line says what it mapped to.
6. Otherwise the message line reads: "Not a search or a reference. Start a search with . / ' ; ( or ~, or type a reference like Rom 8:28."

Keys in the field: Enter runs, Escape clears, up and down walk history. When the search version is Greek or Hebrew, letters typed on a Latin keyboard are turned into Greek or Hebrew as you type, and the placeholder changes to "Enter search words or verse here (type Greek with Latin letters)".

## Verse list (search results)

The list under the command line drives Browse. Selecting a hit moves Browse to that verse.

- Up, Down, Page Up, Page Down, Home, and End move the selection, and Browse follows.
- Space checks or unchecks the selected hit. Shift+Delete removes hits from the list.
- Checked hits are what Copy and the verse-list tools act on.

Three ways of using that field:

- **Beginner.** The command line is replaced by Easy Search, Easy Lookup, and Easy Copy.
- **Standard.** The command line stays, and a row of buttons inserts the characters the syntax uses.
- **Power user.** The command line alone.

While you type, two helpers can open:

- A word list that tracks the letters so far and shows which forms exist in the current search version.
- Morphology-code help, which opens as you type a code and decodes it. The decoder covers the BibleWorks positional codes and records values the help file does not define.

Other command-line behavior that is switched in options:

- Exact hit counts. A search can count every combination the query allows, which is slower and exact.
- An OR search warns when one branch matches nothing, and can continue because the other branches are still valid.
- A range typed on the command line is kept when Browse refreshes.
- A fuzzy search stems words, or follows the word-link list (`faith works` can find `working`, `faithfulness`). The same choice is on the right-click menu. An equals sign in front of a search (`=. faith works`) forces the link search once.
- Wildcards for pointed Hebrew, inserted as Ins-1 through Ins-5, used when vowel-point sensitivity is on.

Around the field:

- **Assistant** opens the Command Line Assistant.
- **Options** is the verse-list menu.
- **Tools** and **Copy** are menus. Copy has its own Copy Center: what to copy (a range, which versions) and where it goes.
- Result tabs, history back, and a verse-history button sit above the field.
- The version button chooses the search version and the display versions. Default display versions when none are saved are KJV, NAS, BNT, WTT, and LXT.
- Previous and next step through the verse list.

Search also has a **Graphical Search Engine**: you place word boxes, merge boxes, and agreement boxes, connect them, set order and proximity, and run the picture as a query. The command line can be imported into that picture.

Related search tools, opened from Tools rather than typed:

- Word List Manager and Verse List Manager (load, save, sort, include or exclude, export).
- Related Verses and Phrase Matching.
- KWIC and collocation table. The collocation word is blue and the key word is red. Results can cross verse boundaries and can show the brother text.
- Cross-version search: current version only, all same-language display versions, or search and then prune.
- Search limits by book, testament, apocrypha, or an explicit verse range.
- Detailed statistics for the current search.

## Browse

Browse is the reading pane.

- Version, book, chapter, and verse selectors, plus outline headings.
- **Browse mode** shows the whole chapter of one version. **Multiple versions** shows one verse in each chosen display version. The button toggles them.
- The header can show the current verse, extra buttons, the outline heading, or the list boxes, or it can be hidden.
- Secondary browse windows can sit beside the main one.
- Interlinear mode, Strong's numbers, version notes, and difference highlighting can be turned on.
- Word tips follow the pointer. A tip can include the short English gloss. Hebrew and Greek morphology can be decoded in the tip.
- Hovering a word can also drive the manuscript image (see Manuscripts). That link can be limited to Shift-hover.
- Clicking a reference inside a lexicon or note sends that reference back to the command line.
- Double-clicking a version label in Multiple versions makes that version the search version.
- Paragraph marks and a verse map keep numbering aligned when a version does not match the Hebrew (WTT), Greek NT (GNT), LXX (LXT), or NRS scheme. The verse-map editor explains the correspondence and lets an entry be changed.

## Analysis

Hover is the default. Analysis follows the word under the mouse in Browse (after a delay of about 60 ms) and clicking a word pins it, so it stays while the mouse moves on. **Freeze** holds the current word against both hover and click. On a touch screen, a tap shows the word and a second tap opens its menu. A second Analysis window can be opened, and the tabs can wrap.

Before any word is chosen, the tab reads: "Move the mouse over a word in the Browse Window to see its parsing and lexicon entry here. Click a word to keep it."

The **Analysis** tab, the first and default tab, shows for the current word:

1. A source line: the morphology source, or the version and reference.
2. The word as it appears in the text.
3. For each parsing: lemma, the morphology code (`@` plus code), and the code spelled out in words.
4. Strong's numbers, when the version has them.
5. The lexicon sections for that lemma (see Lexicons below), one block per enabled lexicon.

An option hides very common words: above a frequency cutoff the tab says how often the lemma occurs instead of showing it.

Tabs the app registers, in its order: Analysis, Notes, Editor, Resources, X-Refs, Context, Words, Stats, Browse, Use, Forms, Vs1, Vs2, Mss, Version Info, AGNT, UserLex, EPUB, Dictionary, Leningrad, CNTTS, SOLM. The ones described from their behavior:

| Tab | What it shows |
| --- | --- |
| Analysis | Parsing and lexicon for the current word, as above. |
| Context | The verse in its surrounding context. (From the tab and help-page name; contents not yet checked.) |
| Words | Word-level information for the current verse. (Not yet checked.) |
| Use | Where and how the current word is used. (Not yet checked.) |
| Vs1, Vs2 | A single verse in other versions, kept beside Browse. |
| Browse | A secondary Browse window inside the Analysis pane. |
| Notes, Editor | Verse notes and the rich-text editor (see Other tools). |
| UserLex, EPUB | The user lexicon and the EPUB reader, hosted as tabs. |
| Forms | Every parsing of the form under the pointer, and every inflected form of the lemma, with counts. Sort by frequency, alphabet, or morphology code. Click an entry to search it. |
| Resources | Resource Summary for the verse: which modules mention it. It can follow the pointer. |
| Mss | Manuscript collation and the page image. Detailed below. |
| Leningrad | Leningrad Codex page images, separate from the Greek manuscript tab. |
| CNTTS | Center for New Testament Textual Studies apparatus. Search the apparatus, merge or remove hits from the verse list, and open the manuscript key. |
| AGNT | Analytical Greek New Testament line: lemma, morphology, English reference gloss, phrase line. Copy the interlinear. If the versions are not word-for-word parallel, the tab says some lines are missing. |
| SOLM | Linear morphology display. |
| Dictionary | Bible-dictionary entry for the word. |
| X-Refs | Cross-references for the verse. Open another X-Refs window, add and edit references, show or hide the verse text, freeze the list. |
| Stats | Counts for the current search or word. |
| Version Info | Bibliography and copyright notice for the version on screen. |

Lexicon sections in the same pane are chosen per lemma. Double-click a lexicon in the chooser to show or hide it. A missing entry says there is no article, and the parsing still shows. Hebrew homonyms can all be listed. Hebrew joined by maqqef can show the full analysis of each part. Definition order for Hebrew can be reversed.

## Manuscripts

The Mss tab is a study of one verse across witnesses, with the photograph of the page under the table.

### The collation

The top of the tab is a table. Each row is a witness (a manuscript or a transcribed version). Each column is a word of the verse. A cell that differs is marked. A witness that omits the word shows a dash. The row labels stay put while you scroll sideways. Clicking a verse reference in a label goes to that verse.

Collation options:

- Which witnesses are columns. The default set can be changed. A compiled transcription can be added to the list.
- Nu-bar, nomina sacra, movable nu, and manuscript spelling can be expanded or kept as written.
- Freeze keeps the table from chasing Browse.

The table can be copied as plain text or as HTML, shown in a popup that stays still, or shown in a popup that follows Browse. It can also be printed.

Hovering a cell marks that word. Hovering the photograph does the reverse, described next.

### The page image and the hover

Under the table, a splitter, then the page. The app calls it a manuscript page image. You drag to move it and Ctrl-scroll to zoom. It is drawn on a canvas from a page image (a JPEG preview, plus tiles), not as a loose file you scroll in a PDF reader.

The page is coded with regions. Each line of the verse is a rectangle. The words of that line are spread across the rectangle. When the pointer is over the image, the app:

1. Finds which line rectangle contains the pointer.
2. Finds how far across that line the pointer is.
3. Turns that fraction into a word index.
4. Highlights that word in the collation table and draws a marker on the image.

Labels sit on the image for the verse or word. A tip can show the Hebrew line, an English line, and the reference. Image settings control whether labels are on, and whether Browse-hover is Shift-only.

Hovering a word in Browse (optionally only while Shift is held) moves this tab to that verse, so the photograph and the collation stay with the reading.

### Leningrad Codex

A separate Analysis tab, Leningrad, browses the Codex Leningradensis images. A list of pages sits beside the same kind of page viewer. It follows the verse in Browse, and it also listens to hover in the Browse pane.

### CNTTS apparatus

CNTTS is a search of the critical apparatus rather than a photograph. You can search the whole apparatus or only the previous results, then merge, remove, or replace the main verse list. Dates and Aland categories come from the CNTTS manuscript descriptions. A witness with no category is left out of the grid. The manuscript key opens in a window (the introduction that ships with the apparatus).

### Transcription and tagging

These are the tools for making a witness, not just reading one.

- Transcription window: a base text (BYZ by default), the transcription, and notes. Differences against the base are colored. Options cover word or letter mode, case, underdot, overbar, corrections, accents, and a blinking marker.
- Images can be attached. Shift-drag selects a region on the image. Notes sit in their own pane. Macros are two-line pairs (name, then text) and appear on the notes right-click menu.
- Tagging projects: pretag a text, search and replace, color sets, compile a transcription into a version that collation can display, extract a plain verse file from a BWT transcription.
- The About line of the manuscripts area names the BibleWorks Manuscripts Project (Kent Clarke, T. A. E. Brown, Randy Leedy, Steve Delamarter, Michael Bushell, Michael Tan).

## Maps

Resources includes the BibleWorks Map Module and, separately, NET Bible Quick Maps.

### The map window

OpenBible Maps is its own window: a menu, a toolbar, the map canvas, and a status line. You pan and zoom. An inset in the corner shows where the current view sits in the wider map; click the inset to jump. A ruler reports distance in miles and kilometers and a travel time from a speed you set in Travel speed. Color adjustment changes the base map. Views can be opened, saved, and discarded.

A site under the pointer opens a card: the name, coordinates, classification, Strong's number, Hebrew and Aramaic, notes, and which overlay it belongs to. The same card can list other overlays that contain that site.

### Overlays and the checkboxes

Overlays / Stacking order is the checkbox list. Each row is a folder or an overlay. A checkbox draws that layer. Folders expand. Rows can be reordered, which is the stacking order. A changed overlay is marked until you save it. A shipped overlay you edit is saved as your own copy under "My overlays." Deleted overlays can be shown again. Each overlay has a title, a description, a time period, and Bible references; hovering a row shows that text.

The shipped overlay ids, read from the app's overlay list:

| Id | What the layer is |
| --- | --- |
| `exodusrt`, `exodsite` | The Exodus route and its sites. This is the Moses journey layer. |
| `paul1`, `paul2`, `paul3`, `paul4`, `paul_journey_cities` | Paul's journeys, in four stages, plus the cities. |
| `jesus_min_path`, `jesus_min_path2` … `jesus_min_path6`, `jesus_min_sites` | Jesus' ministry routes and sites. |
| `abraham` | Abraham. |
| `jacob_path`, `jacob_sites`, `jacob_tags` | Jacob's route, sites, and labels. |
| `joshua_canaan`, `joshua_canaan2`, `joshua_canaan3` | Joshua and Canaan. |
| `peter_journey`, `peter_sites`, `philip_journey`, `philip_sites` | Peter and Philip. |
| `bk00-gen` through `bk65-rev` | One label layer per biblical book, Genesis through Revelation. |
| `era00` through `era24` | Era layers. |
| `patriarc`, `assyrian`, `persian`, `division`, `empisite`, `medobaby` | Patriarchs, empires, the divided kingdom, and related sites. |
| `jerusdet`, `keysites`, `ntcities`, `general-nt`, `genov` | Jerusalem detail, key sites, NT cities, and general overlays. |

Checking `exodusrt` draws the route. Checking `paul1` draws that journey. Unchecking removes it. Several can be on at once, in the stacking order you set.

You can also make an overlay: sites, text, and lines (solid, dashed, curved), then save it. Editing Tools places new items into the overlay you pick.

### Quick Maps, atlas, find

- **Quick Maps** are the NET Bible maps: Galilee and the north, Samaria, Judah, the coastal plain and Shephelah, the wilderness, the Negev, and Journeys of Paul 1–4. Zoom is 10% to 200%.
- **Moody Bible Atlas** is a gallery of plates and pictures, with related plates for the place you are on.
- **Find place** is a search box over a table of sites. Choosing a row moves the map there.
- The status line names the map and the coordinates.

## Lexicons and dictionaries

Hovering a word in Browse or Analysis asks the lexicon index for that lemma and can open the entry. A scripture link inside an entry jumps to the verse. The Lexicon Browser is a window of its own: search the lexicon text, copy to the editor or the clipboard, highlight the current verse, and walk a history list.

Greek lexicons the app ships, in the browser's default order: BDAG, Friberg (Analytical Lexicon), Thayer, Louw-Nida, Danker, Gingrich, Barclay Newman UBS, Liddell-Scott unabridged (LSJM), Liddell-Scott abridged, LEH (Septuagint), Moulton-Milligan (VGNT), TDNT abridged, EDNT, Preuschen, Kassühlke. Enabled on a fresh setup: BDAG, Friberg, Thayer, Louw-Nida, Danker, LSJM, TDNT.

Hebrew lexicons: HALOT, BDB, Holladay, TWOT, PONS. Enabled on a fresh setup: HALOT, BDB, Holladay, TWOT.

Strong's Hebrew and Greek are available in English, German, French, Dutch, and Russian, plus BibleWorks supplement codes for Hebrew.

Dictionaries and related books: Easton, Fausset, ISBE, Nave's Topical Bible, a Bible outline, Geneva Bible notes (1599), Matthew Henry (verse-keyed), Daily Light.

**Parallel Hebrew–LXX** (Tov-Polak) aligns a Hebrew word with the Greek of the Septuagint. You can search both at once (a blank box is a wildcard; Hebrew ignores vowel points), see the raw or formatted line, and read the critical-note tips.

A user lexicon can be edited and shown as its own material. The link editor attaches an external link to a lemma.

## Cross-references and topics

- Treasury of Scripture Knowledge, as a browser: entries, history, the article, and the verse list. Verses can be sent to the editor or to the Search window. TSK also has chapter outlines, keyword notes, and book essays.
- Nave's, Torrey's Topical Textbook, Thompson Chain References, and a biographical Bible, in the same kind of three-column browser.
- Westminster Confession references.
- Master Module Index, and a dialog to compile a module index.
- Resource Summary, which is the Analysis "Resources" tab and a standalone window.

## Media, reading aloud, and pictures

- Read Text speaks the passage. Voices come from the app, and the audio can be fetched as a wav.
- Paradigm pronunciations for grammar forms.
- Vocabulary flashcards can play and record a word.
- A picture viewer for images attached to articles.
- Daily Light on the Daily Path: morning and evening, with a calendar, a version, and an option to use the Bagster text when the version is KJV.

## Other tools

These are real windows in the app, opened from Tools or Resources.

- **Editor.** A rich-text editor for notes: fonts, Greek and Hebrew defaults, lists, find and replace, spell check, insert a verse or a picture. Notes can be searched.
- **Report generator.** Presets and page setup for a formatted report.
- **Diagramming.** Draw Greek or Hebrew sentence diagrams (Leedy-style GNT diagrams are a print range of their own). Word details can be the word only, the word plus morphology, or lemma, form, and morphology. Lines, curves, callouts, and text boxes.
- **New Testament Diagram Database.** Stored diagrams, separate from the blank drawing module.
- **Synopsis.** Gospel (or other) parallels in columns. Remove blank cells, find a verse, open and save a synopsis file.
- **Timeline.** A chronological strip with captions.
- **Bible outline.** Headings for the chapter, also used as the Browse heading.
- **EPUB.** Two reader tabs and a library. Import books, assign categories, search the current book, all books, or a custom set. Navigation has its own font size.
- **Keyboards.** On-screen Greek and Hebrew keyboards, layouts, and a Greek alias list so a transliteration resolves to a Greek form.
- **Version Database Compiler.** Build a version from a text file. Book-name alias lists (`.bna`) control the names Browse shows and the names the command line accepts. English, French, German, and Spanish sets are included.
- **External resources (Ermie).** A catalog of links and files outside the app. Editing the shipped catalog saves a copy.
- **Color.** Program colors, colors on search hits, and Targum variant colors.
- **Checkpoints, backup, migrate.** Save the session, restore it, and move settings.

## The shell around the windows

Each pane has a dark title bar with its own menu row, as on the live page:

- Search: "Search Window", Assistant, Options ▾, Tools ▾, Copy ▾, and the search-version button (KJV by default).
- Browse: "Browse Window", Options ▾, Multiple versions.
- Analysis: "Analysis Window", Freeze, then the tab strip.

Look, from the stylesheets and the theme code:

- The style is a dense desktop application, not a web page: small UI text (15px UI, 13px small), thin borders, menus and dropdowns rather than large buttons.
- Colors are a small set of tokens: `--chrome` (title bars and menus), `--chrome-ink`, `--bg` (pane background), `--ink` (text), `--panel` and `--line` (mixed from `--bg` and `--ink`), `--sel-bg` (selection), `--sel-strong` and `--focus` (accent), plus `--lemma`, `--ref`, `--link`, `--code`.
- The optional BibleWorks color schemes fill those tokens with the classic BibleWorks look: chrome `#333333`, headings `#747474`, pane background `#cecece`, selection `#888585`, accent `#cc4411`. The default light and dark values are in `app.css`, which was not retrievable when this was checked.
- Greek and Hebrew use SBL BibLit by default (SBL Greek and SBL Hebrew are options). Greek text is 20px, Hebrew 22px, Latin 17px.

- Light, dark, or system theme, stored in preferences.
- English and Spanish interface strings.
- Layout: command line on top, Search on the left, Analysis on the right, or Analysis stacked under Browse. Splitters resize the panes.
- Toolbar size from 17px to 60px, and an editor for which buttons appear.
- Configuration manager: named layouts you can load.
- Word history and verse history as their own windows, not only the arrows on the command line.
- On a phone, Search, Browse, and Analysis are tabs. The switch follows the device (a touch-first, coarse pointer), not only the window width. Touch targets are 44px. Lists that sit beside a page collapse behind a button.
- An account can sync preferences across devices. The account line shows "saving…" while a change is pending, "offline: kept on this device" when there is no connection, and "synced" after.
- The databases run in the browser. A Web Worker holds the SQLite connections, and the service worker answers every `/api/*` request by passing it to that worker. Search and reading therefore keep working offline once the data is cached.

## What this inventory leaves out

The menu resource file still contains the old BibleWorks desktop menus (print, register, Paratext send/receive, and the installer). Those entries are listed in the UI data. They are not all separate web features. The sections above are the ones the web app actually builds windows for.

`spec.md` says which of these to build first, and which data this repository is allowed to use. The manuscript photographs, the map plates, and the lexicon articles above are someone else's licensed material. This file names them so the behavior is clear. It does not bring that material into this repository.
