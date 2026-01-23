# Usage Guide - Greek New Testament Bible Study App

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up the Database

This will download the Greek New Testament data and create the database (takes a few minutes):

```bash
python setup_database.py
```

### 3. Run the Application

```bash
python app.py
```

Then open your browser to: http://localhost:5000

---

## Search Features

### Text Search
- **Text / Lemma Search**: Enter any Greek word or lemma to find occurrences
  - Example: `λόγος` (logos - word)
  - Example: `ἀγάπη` (agape - love)

- **Exact Lemma**: Search for the exact dictionary form
  - More precise than text search
  - Example: `λέγω` will find all forms of "to say"

### Linguistic Filters

#### Part of Speech
Filter by grammatical category:
- **verb**: Action words
- **noun**: People, places, things
- **adjective**: Descriptive words
- **pronoun**: He, she, it, etc.
- **conjunction**: And, but, or, etc.
- **adverb**: Modifies verbs
- **preposition**: In, on, with, etc.
- **article**: The (ὁ, ἡ, τό)
- **particle**: Small function words
- **interjection**: Exclamations

#### Verb-Specific Filters

**Tense** (when action occurs):
- **present**: Ongoing action
- **imperfect**: Past ongoing action
- **future**: Future action
- **aorist**: Simple past action
- **perfect**: Completed action with ongoing results
- **pluperfect**: Past completed action

**Voice** (relationship of subject to action):
- **active**: Subject performs action
- **middle**: Subject acts on/for self
- **passive**: Subject receives action

**Mood** (how action is presented):
- **indicative**: Statement of fact
- **imperative**: Command
- **subjunctive**: Possibility/expectation
- **optative**: Wish/potential
- **infinitive**: Verbal noun
- **participle**: Verbal adjective

#### Noun/Adjective Filters

**Case** (function in sentence):
- **nominative**: Subject
- **genitive**: Possession/description
- **dative**: Indirect object
- **accusative**: Direct object
- **vocative**: Direct address

**Number**:
- **singular**: One
- **plural**: More than one

**Gender**:
- **masculine**
- **feminine**
- **neuter**

**Person** (for verbs):
- **1**: I/we
- **2**: you
- **3**: he/she/it/they

---

## Example Searches

### Find All Aorist Passive Verbs
1. Set **Part of Speech** to "verb"
2. Set **Tense** to "aorist"
3. Set **Voice** to "passive"
4. Click **Search**

### Find All Occurrences of λόγος (logos)
1. Enter `λόγος` in **Exact Lemma**
2. Click **Search**

### Find All Participles in Matthew
1. Select "Matthew" from **Book** dropdown
2. Set **Part of Speech** to "verb"
3. Set **Mood** to "participle"
4. Click **Search**

### Find Nominative Plural Nouns
1. Set **Part of Speech** to "noun"
2. Set **Case** to "nominative"
3. Set **Number** to "plural"
4. Click **Search**

### Find All Words in the Dative Case
1. Set **Case** to "dative"
2. Click **Search**

### Combine Multiple Criteria
You can combine any filters! For example:
- **Book**: John
- **Part of Speech**: verb
- **Tense**: present
- **Mood**: indicative
- **Person**: 1

This finds all present indicative verbs in first person in the Gospel of John.

---

## Understanding Results

Each result shows:
- **Reference**: Book, chapter, and verse
- **Verse Text**: Full Greek text with matched words highlighted
- **Word Details**: Morphological breakdown of each matching word
  - Word form as it appears in text
  - Lemma (dictionary form)
  - All grammatical properties

---

## Tips

1. **Start Broad**: Begin with fewer filters, then narrow down
2. **Mix Text and Grammar**: Combine word search with morphological filters
3. **Results Limit**: Results are limited to 500 for performance
4. **Clear Filters**: Use the "Clear" button to reset all filters
5. **Greek Input**: You can copy/paste Greek text from online resources

---

## Data Attribution

This application uses **MorphGNT** data:
- Morphologically tagged Greek New Testament
- Based on the SBL Greek New Testament
- Available under CC BY-SA License
- https://github.com/morphgnt/sblgnt

---

## Technical Details

### Database
- SQLite database with full-text search
- ~138,000 words indexed
- Morphological data for every word
- Optimized with indexes on all searchable fields

### Search Performance
- Searches typically complete in < 100ms
- Multiple criteria are combined with AND logic
- Case-insensitive text search
- Exact matching for morphological features

---

## Troubleshooting

**Database not found error**:
- Make sure you ran `python setup_database.py` first

**No results found**:
- Check spelling of Greek text
- Try removing some filters to broaden search
- Use text search instead of exact lemma

**Download errors during setup**:
- Check internet connection
- GitHub may be temporarily unavailable
- Try running setup again

**Port already in use**:
- Another application is using port 5000
- Stop the other application or edit `app.py` to use a different port

---

## Advanced Usage

### Query the Database Directly

You can also query the database using SQLite:

```bash
sqlite3 greek_nt.db
```

Example queries:

```sql
-- Find all words with lemma λόγος
SELECT * FROM words WHERE lemma = 'λόγος';

-- Count verbs by tense
SELECT tense, COUNT(*) FROM words WHERE pos = 'verb' GROUP BY tense;

-- Find rare words (appearing only once)
SELECT lemma, COUNT(*) as count FROM words GROUP BY lemma HAVING count = 1;
```

### Extend the Application

The codebase is modular and easy to extend:
- `app.py`: Add new API endpoints
- `templates/index.html`: Modify the UI
- `static/style.css`: Customize styling
- `setup_database.py`: Enhance data processing

---

Enjoy studying the Greek New Testament!
