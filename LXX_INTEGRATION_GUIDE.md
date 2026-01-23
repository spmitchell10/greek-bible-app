# Septuagint (LXX) Integration Guide

## Current Status

The app infrastructure is **fully prepared** for Septuagint (LXX) data:
- ✅ Database schema includes `corpus` field (`'NT'` or `'LXX'`)
- ✅ UI has corpus selection checkboxes (LXX currently disabled)
- ✅ Query logic filters by corpus
- ✅ All search features work with corpus selection

**What's missing:** LXX morphologically-tagged data source

## When LXX Data Becomes Available

Follow these steps to integrate LXX data:

### 1. Prepare LXX Data

You'll need LXX data in a format similar to MorphGNT, with:
- Book/Chapter/Verse references
- Greek words
- Lemmas (dictionary forms)
- Morphological codes (POS, case, number, gender, tense, voice, mood, person)

### 2. Update `setup_database.py`

Add LXX book definitions after the NT books:

```python
# Septuagint (LXX) books
LXX_BOOKS = [
    ("101", "Genesis", "Gen", "file_id", "abbreviation"),
    ("102", "Exodus", "Exod", "file_id", "abbreviation"),
    # ... add all LXX books
]
```

**Note:** Use book codes 101+ for LXX to avoid conflicts with NT (01-27).

### 3. Create LXX Download Function

Add a function to download/parse LXX data:

```python
def download_lxx_file(book_name: str, file_id: str) -> List[str]:
    """Download an LXX file for a specific book."""
    # Implement based on your LXX data source
    url = f"YOUR_LXX_BASE_URL/{file_id}"
    # ... download logic
    return lines

def populate_lxx_database(conn):
    """Download LXX data and populate the database."""
    cursor = conn.cursor()
    
    # Insert LXX books
    for book_code, book_name, book_abbrev, file_id, file_abbrev in LXX_BOOKS:
        cursor.execute(
            "INSERT OR REPLACE INTO books (book_code, book_name, book_abbrev, corpus) VALUES (?, ?, ?, ?)",
            (book_code, book_name, book_abbrev, 'LXX')
        )
    
    # Download and parse each book
    word_count = 0
    for book_code, book_name, book_abbrev, file_id, file_abbrev in LXX_BOOKS:
        lines = download_lxx_file(book_name, file_id)
        
        current_verse = None
        verse_word_pos = 0
        
        for line in lines:
            # Parse LXX data (format may vary)
            data = parse_lxx_line(line)
            if data:
                # Track word position
                verse_key = (data["book_code"], data["chapter"], data["verse"])
                if verse_key != current_verse:
                    current_verse = verse_key
                    verse_word_pos = 1
                else:
                    verse_word_pos += 1
                
                parsed = data["parsed_morph"]
                cursor.execute("""
                    INSERT INTO words (
                        book_code, chapter, verse, word_position, word, lemma, morph_code,
                        pos, person, tense, voice, mood, case_value, number, gender, corpus
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["book_code"],
                    data["chapter"],
                    data["verse"],
                    verse_word_pos,
                    data["word"],
                    data["lemma"],
                    data["morph_code"],
                    parsed.get("pos"),
                    parsed.get("person"),
                    parsed.get("tense"),
                    parsed.get("voice"),
                    parsed.get("mood"),
                    parsed.get("case"),
                    parsed.get("number"),
                    parsed.get("gender"),
                    'LXX',  # Corpus identifier
                ))
                word_count += 1
        
        conn.commit()
    
    return word_count
```

### 4. Update Main Function

In the `main()` function of `setup_database.py`, add LXX population:

```python
def main():
    # ... existing NT setup code ...
    
    # Add LXX data
    print("\nDownloading and parsing Septuagint (LXX) data...")
    print("(This may take a while)")
    lxx_word_count = populate_lxx_database(conn)
    print(f"[OK] LXX data populated with {lxx_word_count} words!")
```

### 5. Enable LXX Checkbox

In `templates/index.html`, remove the `disabled` attribute:

```html
<label class="checkbox-label" title="Search the Septuagint">
    <input type="checkbox" id="corpus-lxx">
    <span>Septuagint (LXX)</span>
</label>
```

### 6. Update Book Abbreviations

In `query_parser.py`, add LXX book abbreviations to `BOOK_ABBREVIATIONS`:

```python
BOOK_ABBREVIATIONS = {
    # ... existing NT books ...
    
    # LXX books
    'Gen': '101', 'Genesis': '101',
    'Exod': '102', 'Exodus': '102',
    # ... add all LXX books
}
```

### 7. Test

Run the setup script:
```bash
python setup_database.py
```

Then test searches:
- Check both NT and LXX checkboxes
- Search for common Greek words
- Try book-specific searches: `[Gen] + [noun]@Nns`

## Potential LXX Data Sources

Consider these options:

1. **CCAT (Computer-Assisted Tools for Septuagint Studies)**
   - May require academic access
   - Has morphological tagging

2. **OpenText.org**
   - Open source LXX resources
   - Check licensing

3. **Perseus Digital Library**
   - Has LXX texts
   - May need morphological processing

4. **Contact Academic Institutions**
   - Many have LXX research projects
   - May share data for educational purposes

## Notes

- LXX book codes should start at 101 to avoid conflicts with NT (01-27)
- Morphology format may differ from MorphGNT - adjust parsing accordingly
- Consider adding a separate morphology parser for LXX if format differs significantly
- Test thoroughly with both corpora selected simultaneously

## Questions or Issues?

The infrastructure is ready - just need the data! When you find a suitable LXX source, follow these steps and the integration should be straightforward.
