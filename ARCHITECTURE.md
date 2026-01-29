# Greek Bible Study App - Architecture Documentation

## Table of Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Core Components](#core-components)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Data Flow](#data-flow)
- [Search System](#search-system)
- [Reading View](#reading-view)
- [Design Decisions](#design-decisions)
- [Future Enhancements](#future-enhancements)

---

## Overview

The Greek Bible Study App is a web-based application designed for linguistic and morphological analysis of Greek biblical texts. It provides advanced search capabilities, parallel passage finding, and a continuous reading interface for both the Greek New Testament (NT) and the Septuagint (LXX).

### Key Capabilities
- **Morphological Search**: Search by lemma, part of speech, tense, voice, mood, case, number, gender, person
- **Advanced Query Syntax**: Custom query language for complex linguistic searches
- **Relative Search**: Find parallel passages based on vocabulary similarity
- **Reading View**: Read Greek text with infinite scroll and dual display modes
- **Multi-Corpus Support**: Search and read both NT and LXX texts

---

## Technology Stack

### Backend
- **Framework**: Flask 3.0.0 (Python web framework)
- **Database**: SQLite (embedded, serverless database)
- **Language**: Python 3.x
- **Data Processing**: 
  - `requests` for HTTP data fetching
  - `pysword` for SWORD module parsing
  - Built-in `sqlite3` for database operations

### Frontend
- **HTML5**: Jinja2 templating engine
- **JavaScript**: Vanilla JS (no frameworks)
- **CSS3**: Custom styling with CSS variables
- **Fonts**: Greek Unicode fonts (SBL Greek, Gentium Plus, Cardo)

### Data Sources
- **MorphGNT**: Morphologically tagged Greek New Testament
  - Source: https://github.com/morphgnt/sblgnt
  - Format: Tab-separated text files with morphology codes
- **SWORD Module (LXX)**: Septuagint with morphological tagging
  - Format: OSIS XML with Strong's numbers and Packard morphology codes

---

## Project Structure

```
greek-bible-app/
├── app.py                      # Main Flask application with API routes
├── query_parser.py             # Advanced search syntax parser
├── relative_search.py          # Parallel passage finder (relative search)
├── setup_database.py           # Database initialization & NT import
├── lxx_importer.py            # LXX data importer from SWORD module
├── greek_nt.db                # SQLite database (generated)
├── requirements.txt           # Python dependencies
│
├── templates/
│   └── index.html             # Single-page application UI
│
├── static/
│   ├── script.js              # Frontend logic & API interactions
│   └── style.css              # Application styling
│
├── ARCHITECTURE.md            # This file
├── SEARCH_SYNTAX.md           # Search syntax documentation
└── LXX_INTEGRATION_GUIDE.md   # LXX import guide
```

---

## Database Schema

### Tables

#### 1. `books`
Stores metadata about biblical books.

```sql
CREATE TABLE books (
    book_code TEXT PRIMARY KEY,    -- e.g., '01' (Matt), '04' (John), '40' (Gen)
    book_name TEXT NOT NULL,       -- Full name: 'Matthew', 'Genesis'
    book_abbrev TEXT NOT NULL,     -- Abbreviation: 'Matt', 'Gen'
    corpus TEXT NOT NULL           -- 'NT' or 'LXX'
);
```

**Book Code Ranges:**
- NT: `01-27` (Matthew to Revelation)
- LXX: `40-78` (Genesis to Malachi)

#### 2. `words`
Stores every word with morphological data.

```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_code TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    word_position INTEGER NOT NULL,
    word TEXT NOT NULL,            -- Greek text (inflected form)
    lemma TEXT NOT NULL,           -- Dictionary form
    morph_code TEXT,               -- Raw morphology code
    pos TEXT,                      -- Part of speech
    person TEXT,                   -- 1st, 2nd, 3rd
    tense TEXT,                    -- present, aorist, imperfect, etc.
    voice TEXT,                    -- active, middle, passive
    mood TEXT,                     -- indicative, subjunctive, etc.
    case_value TEXT,               -- nominative, genitive, etc.
    number TEXT,                   -- singular, plural
    gender TEXT,                   -- masculine, feminine, neuter
    corpus TEXT NOT NULL DEFAULT 'NT',
    UNIQUE(book_code, chapter, verse, word_position, corpus)
);
```

**Indexes:**
- Primary key on `id`
- Unique constraint on `(book_code, chapter, verse, word_position, corpus)`

#### 3. `words_fts`
Full-text search virtual table for fast text searches.

```sql
CREATE VIRTUAL TABLE words_fts USING fts5(
    word, 
    lemma, 
    content=words
);
```

---

## Core Components

### 1. Flask Application (`app.py`)

**Purpose**: Main web server handling HTTP requests and routing.

**Key Routes:**
- `GET /` - Serve the main application page
- `POST /api/search` - Standard search with morphology filters
- `POST /api/advanced-search` - Custom syntax search (including relative search)
- `POST /api/read` - Reading view API for fetching chapters
- `GET /api/books` - Get list of all books
- `GET /api/stats` - Database statistics
- `GET /api/morphology/options` - Available morphology filter options
- `GET /api/search-help` - Search syntax help documentation

**Database Connection:**
- Uses `sqlite3.Row` for dictionary-like row access
- Connection per request pattern with `get_db()`

### 2. Query Parser (`query_parser.py`)

**Purpose**: Parse custom search syntax into SQL queries.

**Main Components:**
- `MORPH_CODE_ORDER`: Maps single-character codes to database fields
- `BOOK_ABBREVIATIONS`: Maps book names/abbreviations to book codes
- `SPECIAL_TOKENS`: Pre-defined tokens like `[article]`, `[noun]`, `[verb]`
- `SearchTerm` class: Represents a single search term with morphology
- `Query` class: Represents a complete query with terms, proximity, books, corpus
- `parse_query()`: Main parsing function
- `execute_query()`: Executes parsed query against database
- `execute_proximity_search()`: Handles multi-term proximity searches

**Morphology Code System:**
- Single-letter codes for concise queries
- Examples: `N`=noun, `v`=verb, `p`=present, `A`=active, `s`=singular, `g`=genitive

### 3. Relative Search (`relative_search.py`)

**Purpose**: Find parallel passages based on vocabulary similarity.

**Main Components:**
- `POS_WEIGHTS`: Weights for different parts of speech
  - Verbs, Adverbs, Adjectives, Nouns: weight = 3
  - Conjunctions, Prepositions, Pronouns, Particles, Articles: weight = 1
- `parse_verse_reference()`: Parse references like "Rom. 8:1"
- `get_verse_words()`: Extract unique lemmas from a verse
- `search_by_lemmas()`: Find verses with similar vocabulary
- `get_verse_context()`: Get full text of a verse

**Algorithm:**
1. Extract all unique lemmas from source verse
2. Assign weights based on part of speech
3. Search for verses containing any of those lemmas
4. Score each result based on matched lemmas and weights
5. Sort by score (highest first)
6. Highlight matching words in results

### 4. Database Setup (`setup_database.py`)

**Purpose**: Initialize database and import Greek NT data.

**Process:**
1. Create database schema (books, words, words_fts)
2. Download MorphGNT files from GitHub
3. Parse each file line-by-line
4. Extract morphology using custom parser
5. Insert into database with unique constraint
6. Build full-text search index

**MorphGNT Format:**
```
BBCCVV WW NNWORD LEMMA POS MORPHOLOGY LEMMA
```
Example:
```
010101 01 Βίβλος βίβλος N- N----NSF- βίβλος
```

### 5. LXX Importer (`lxx_importer.py`)

**Purpose**: Import Septuagint data from SWORD module.

**Process:**
1. Load SWORD module using `pysword`
2. Parse OSIS XML for each verse
3. Extract words with `lemma` (Strong's numbers) and `morph` (Packard codes)
4. Convert Packard morphology to standardized format
5. Map Strong's numbers to Greek lemmas (when available)
6. Insert into database with corpus='LXX'

**Packard Morphology Codes:**
- Nouns: `N#-CSG` (declension-case-number-gender)
- Verbs: `V..-TVMP#` (tense-voice-mood-person-number)
- Articles: `RA-CSG`

---

## Features

### 1. Standard Search
- Filter by book, lemma, morphology
- Uses dropdown menus for all filters
- Returns matching verses with context

### 2. Advanced Search (Custom Syntax)

**Syntax Examples:**
```
*λόγος@Nsg              # Search entire NT for λόγος (noun, singular, genitive)
[Matt.] + [verb]@pAI3s  # Present active indicative verbs, 3rd singular in Matthew
*[article] & [noun] W2   # Article within 2 words of noun
[Rom., 1Cor] + θεός     # Search for θεός in Romans and 1 Corinthians
```

**Components:**
- `*` = whole NT/LXX
- `[Book]` = specific book(s)
- `@codes` = morphology
- `&` = multiple terms
- `W#` = proximity (within # words)
- `+` = separates books from search terms

### 3. Relative Search (Parallel Passages)

**Syntax:**
```
*rel Rom. 8:1           # Find verses similar to Romans 8:1
rel John 3:16           # Find verses similar to John 3:16
```

**Features:**
- Extracts all unique lemmas from source verse
- Weights by importance (verbs/nouns > articles/prepositions)
- Interactive word selection (check/uncheck words)
- Displays similarity scores
- Highlights matching words in bold

### 4. Reading View

**Features:**
- Book and chapter selector
- Corpus selection (NT/LXX)
- Two display modes:
  - **Verse-by-Verse**: Traditional format with circular verse numbers
  - **Paragraph**: Continuous text with superscript verse numbers
- Infinite scroll (loads previous/next chapters automatically)
- Pre-loads context (1 chapter before and after)
- Smooth scroll positioning to requested chapter

**Infinite Scroll Logic:**
- Detects scroll near top → loads previous chapter
- Detects scroll near bottom → loads next chapter
- Maintains scroll position when loading above
- Tracks loaded chapters to avoid duplicates

---

## API Endpoints

### GET `/`
Returns the main HTML page.

### GET `/api/books`
Returns list of all books with metadata.

**Response:**
```json
[
  {
    "book_code": "01",
    "book_name": "Matthew",
    "book_abbrev": "Matt",
    "corpus": "NT"
  },
  ...
]
```

### GET `/api/stats`
Returns database statistics.

**Response:**
```json
{
  "total_words": 485385,
  "unique_lemmas": 5436,
  "total_books": 39
}
```

### POST `/api/search`
Standard search with morphology filters.

**Request:**
```json
{
  "book": "01",
  "lemma": "λόγος",
  "pos": "noun",
  "case": "genitive"
}
```

**Response:**
```json
{
  "results": [
    {
      "reference": "Matthew 1:1",
      "verse_text": "Βίβλος γενέσεως...",
      "word": "λόγου",
      "lemma": "λόγος",
      "morphology": {...}
    }
  ],
  "count": 15
}
```

### POST `/api/advanced-search`
Advanced search with custom syntax.

**Request:**
```json
{
  "query_string": "*λόγος@Nsg",
  "corpora": ["NT"]
}
```

**Response (Standard Search):**
```json
{
  "results": [...],
  "count": 42,
  "query_type": "standard"
}
```

**Response (Relative Search):**
```json
{
  "source_verse": {
    "reference": "Romans 8:1",
    "text": "Οὐδὲν ἄρα νῦν...",
    "words": [
      {
        "lemma": "οὐδείς",
        "pos": "adjective",
        "weight": 3
      },
      ...
    ]
  },
  "results": [
    {
      "reference": "Romans 8:34",
      "verse_text": "τίς ὁ κατακρινῶν...",
      "score": 12,
      "match_count": 4,
      "matched_lemmas": ["Χριστός", "Ἰησοῦς", "θεός"]
    }
  ],
  "query_type": "relative"
}
```

### POST `/api/read`
Get chapter(s) for reading view.

**Request:**
```json
{
  "book_code": "01",
  "chapter": 5,
  "corpus": "NT",
  "context": 1
}
```

**Response:**
```json
{
  "chapters": [
    {
      "book_code": "01",
      "book_name": "Matthew",
      "book_abbrev": "Matt",
      "chapter": 4,
      "verses": [
        {
          "verse": 1,
          "text": "Τότε ὁ Ἰησοῦς..."
        },
        ...
      ]
    },
    {
      "chapter": 5,
      "verses": [...]
    },
    {
      "chapter": 6,
      "verses": [...]
    }
  ],
  "requested_chapter": 5,
  "corpus": "NT"
}
```

### GET `/api/morphology/options`
Get available morphology filter options.

**Response:**
```json
{
  "pos": ["noun", "verb", "adjective", ...],
  "tense": ["present", "aorist", "imperfect", ...],
  "voice": ["active", "middle", "passive"],
  ...
}
```

---

## Data Flow

### Search Request Flow

```
User Input (Frontend)
    ↓
JavaScript Validation
    ↓
HTTP POST /api/advanced-search
    ↓
Flask Route Handler
    ↓
Query Parser (parse_query)
    ↓
SQL Query Construction
    ↓
SQLite Database Query
    ↓
Results Processing
    ↓
JSON Response
    ↓
JavaScript DOM Manipulation
    ↓
Display Results to User
```

### Relative Search Flow

```
User Input: *rel Rom. 8:1
    ↓
Parse Verse Reference
    ↓
Query Database for Source Verse Words
    ↓
Extract Unique Lemmas
    ↓
Assign POS Weights
    ↓
Display Word Selection UI
    ↓
User Selects/Deselects Words
    ↓
Search for Matching Verses
    ↓
Calculate Similarity Scores
    ↓
Sort by Score
    ↓
Highlight Matching Words
    ↓
Display Results
```

### Reading View Flow

```
User Selects Book/Chapter
    ↓
HTTP POST /api/read (request chapter + context)
    ↓
Database Query (3 chapters)
    ↓
Format Verses by Display Mode
    ↓
Render HTML
    ↓
Auto-scroll to Requested Chapter
    ↓
User Scrolls
    ↓
Scroll Event Handler
    ↓
Near Top? → Load Previous Chapter
Near Bottom? → Load Next Chapter
    ↓
Update DOM Without Full Reload
```

---

## Search System

### Morphology Code Mapping

The app uses single-character codes for concise queries:

| Category | Code | Full Value |
|----------|------|------------|
| **Part of Speech** | N | noun |
| | v | verb |
| | J | adjective |
| | P | pronoun |
| | R | article |
| | D | adverb |
| | C | conjunction |
| | E | preposition |
| **Tense** | p | present |
| | a | aorist |
| | i | imperfect |
| | f | future |
| | x | perfect |
| | y | pluperfect |
| **Voice** | A | active |
| | M | middle |
| | P | passive |
| **Mood** | I | indicative |
| | S | subjunctive |
| | O | optative |
| | D | imperative |
| | N | infinitive |
| | P | participle |
| **Case** | n | nominative |
| | g | genitive |
| | d | dative |
| | a | accusative |
| | v | vocative |
| **Number** | s | singular |
| | p | plural |
| **Gender** | m | masculine |
| | f | feminine |
| | u | neuter |
| **Person** | 1 | 1st |
| | 2 | 2nd |
| | 3 | 3rd |

### Special Tokens

Pre-defined tokens for common searches:

- `[article]` → `pos=pronoun AND morph_code LIKE 'RA%'`
- `[noun]` → `pos=noun`
- `[verb]` → `pos=verb`
- `[adj]` or `[adjective]` → `pos=adjective`
- `[adv]` or `[adverb]` → `pos=adverb`
- `[prep]` or `[preposition]` → `pos=preposition`
- `[conj]` or `[conjunction]` → `pos=conjunction`
- `[pron]` or `[pronoun]` → `pos=pronoun`
- `[part]` or `[participle]` → `mood=participle`

### Proximity Search Algorithm

For multi-term searches with proximity (e.g., `*[article] & λόγος W2`):

1. Find all occurrences of first term
2. For each occurrence, check if second term appears within N words
3. Track word positions to ensure sequence
4. Return only verses where all terms match within proximity
5. Group by verse for display

---

## Reading View

### Display Modes

#### Verse-by-Verse Mode
- Each verse displayed on separate line
- Large circular verse numbers (40px diameter)
- Easy reference for study
- Hover effects on verses
- Traditional format

**HTML Structure:**
```html
<div class="verse-item">
  <div class="verse-number">1</div>
  <div class="verse-text">Ἐν ἀρχῇ...</div>
</div>
```

#### Paragraph Mode
- Continuous text flow
- Small superscript verse numbers
- Better reading experience
- Text-align: justify
- Narrative-friendly format

**HTML Structure:**
```html
<div class="paragraph-content">
  <span class="verse-item">
    <sup class="verse-number">1</sup>
    <span class="verse-text">Ἐν ἀρχῇ...</span>
  </span>
  <span class="verse-item">
    <sup class="verse-number">2</sup>
    <span class="verse-text">οὗτος...</span>
  </span>
</div>
```

### Infinite Scroll Implementation

**State Management:**
```javascript
currentReadingState = {
    bookCode: "01",
    currentChapter: 5,
    corpus: "NT",
    displayMode: "verse",
    loadedChapters: Set([4, 5, 6]),
    isLoading: false,
    hasMoreBefore: true,
    hasMoreAfter: true
}
```

**Scroll Detection:**
- Monitor `scrollTop` position
- Trigger when within 300px of top/bottom
- Prevent duplicate loads with `isLoading` flag
- Track loaded chapters to avoid re-fetching

**Chapter Insertion:**
- Insert in correct sequential order
- Maintain scroll position when prepending
- Use `data-chapter` attributes for tracking

---

## Design Decisions

### 1. SQLite Database
**Reason**: Embedded, serverless, no setup required, perfect for desktop/single-user apps, excellent performance for read-heavy workloads.

### 2. Custom Query Syntax
**Reason**: Traditional UI with dropdowns is tedious for complex queries. Custom syntax enables power users to construct sophisticated searches quickly.

### 3. Single-Page Application
**Reason**: Better UX with no page reloads, smooth transitions, maintains state, feels more like a native app.

### 4. Lemma-Based Search
**Reason**: Users searching for a word want to find all inflected forms, not just exact matches. Lemma search enables this naturally.

### 5. Unique Constraint on Words
**Reason**: Prevents duplicate entries when re-running imports. Ensures data integrity and correct word counts.

### 6. Separate Book Codes for NT/LXX
**Reason**: Avoids conflicts (e.g., John in NT vs. LXX books). Makes corpus filtering straightforward.
- NT: 01-27
- LXX: 40-78

### 7. Weighted Relative Search
**Reason**: Not all words are equally important. Verbs and nouns carry more semantic meaning than articles and prepositions. Weighting improves result quality.

### 8. Infinite Scroll
**Reason**: More natural reading experience than pagination. Users can read continuously without interruption.

### 9. Dual Display Modes
**Reason**: Different use cases require different formats. Study needs verse-by-verse; devotional reading benefits from paragraph flow.

### 10. Frontend State Management
**Reason**: Keeps backend simple (stateless API). All reading state managed client-side enables smooth, responsive UI.

---

## Future Enhancements

### High Priority
1. **Complete LXX Import**: Import all 39 OT books (currently only 12 Minor Prophets)
2. **Strong's Number Lookup**: Display definitions for Strong's numbers in LXX
3. **Interlinear Mode**: Show Greek text with English glosses word-by-word
4. **Lexicon Integration**: Link to Greek lexicons (BDAG, LSJ)
5. **Export Results**: Export search results to CSV, JSON, or formatted text

### Medium Priority
6. **Bookmarks**: Save favorite verses or search queries
7. **Notes**: Add personal notes to verses
8. **Highlighting**: Highlight words in reading view
9. **Verse Comparison**: Side-by-side comparison of parallel passages
10. **Advanced Statistics**: Word frequency analysis, concordance generation

### Low Priority
11. **English Translation**: Display English alongside Greek
12. **Morphology Quiz**: Interactive learning tool for Greek morphology
13. **Vocabulary Lists**: Generate vocab lists from selected passages
14. **Dark Mode**: UI theme toggle
15. **Mobile Optimization**: Responsive design improvements for mobile devices

### Technical Improvements
16. **Caching**: Cache frequent queries for faster response
17. **Pagination**: Optional pagination for very large result sets
18. **Progressive Web App**: Enable offline usage
19. **Authentication**: Multi-user support with saved preferences
20. **REST API**: Standardize API for external integrations

---

## Performance Considerations

### Database Optimization
- **Indexes**: Automatic indexing on book_code, chapter, verse
- **FTS5**: Full-text search for fast lemma queries
- **Unique Constraints**: Prevents duplicate data, improves query planning
- **Read-Heavy**: SQLite excels at read operations (this app's primary use case)

### Frontend Optimization
- **Lazy Loading**: Only load visible chapters
- **Debouncing**: Prevent excessive API calls during rapid scrolling
- **DOM Recycling**: Reuse DOM elements when possible
- **CSS Transitions**: Hardware-accelerated animations

### Scalability
- **Single-User**: Optimized for desktop/personal use
- **Database Size**: ~50MB for NT + 12 LXX books (manageable)
- **Query Performance**: Most queries < 100ms
- **Network**: Local server (no network latency)

---

## Development Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/spmitchell10/greek-bible-app.git
cd greek-bible-app

# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_database.py

# (Optional) Import LXX data
python lxx_importer.py

# Run application
python app.py
```

### Access
Open browser to: http://localhost:5000

---

## License & Credits

### Data Sources
- **MorphGNT**: CC BY-SA 3.0
- **SWORD Project**: Public domain / various licenses
- **Greek Fonts**: SIL Open Font License

### Application
- Developed by: [Your Name]
- Repository: https://github.com/spmitchell10/greek-bible-app
- License: [Specify License]

---

## Conclusion

The Greek Bible Study App combines powerful linguistic search capabilities with a beautiful reading interface, making it an invaluable tool for serious students of the Greek New Testament and Septuagint. Its architecture balances simplicity (SQLite, vanilla JS) with sophistication (custom query language, weighted search algorithms), resulting in a fast, reliable, and feature-rich application.

The modular design allows for easy extension, and the comprehensive API enables potential integration with other biblical study tools. Whether used for detailed morphological analysis or devotional reading, the app provides the tools scholars need in an elegant, user-friendly package.
