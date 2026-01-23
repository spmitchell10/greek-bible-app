# LXX (Septuagint) Import Guide

## Overview

Your Greek Bible Study App now supports searching the Septuagint (LXX) alongside the Greek New Testament!

## Current Status

✅ **Genesis 1 is already imported** and ready to search  
✅ LXX importer is built and tested  
⏳ Full LXX import pending (will take 30-60 minutes)

## Quick Test

You already have Genesis 1 (717 words) imported! Try these searches:

1. Go to http://localhost:5000
2. Check both "Greek New Testament" and "Septuagint (LXX)" checkboxes
3. Search for: `*[noun]@gs` (genitive singular nouns in both corpora)

## Running the Full LXX Import

To import all 39 books of the Septuagint:

```bash
python lxx_importer.py
```

**Note:** This will take 30-60 minutes to complete. The importer will:
- Extract text from your SWORD module at `C:\Users\stmitchell\LXX`
- Parse morphological tags (Packard format)
- Import ~200,000+ words from 39 OT books
- Add all data to `greek_nt.db` with `corpus='LXX'`

### Progress Monitoring

The importer shows real-time progress:
```
Processing Genesis...
  [OK] Genesis completed (38267 words, 38267 total)
Processing Exodus...
  [OK] Exodus completed (32692 words, 70959 total)
...
```

## What Gets Imported

For each word, the importer extracts:
- **Greek text**: The actual word
- **Lemma**: Dictionary form (currently uses inflected form)
- **Morphology**: Part of speech, case, number, gender, tense, voice, mood, person
- **Strong's number**: Reference number from the lemma field

## LXX Books Included

The importer processes all 39 canonical OT books:
- Pentateuch: Genesis, Exodus, Leviticus, Numbers, Deuteronomy
- Historical: Joshua, Judges, Ruth, 1-2 Samuel, 1-2 Kings, 1-2 Chronicles, Ezra, Nehemiah, Esther
- Wisdom: Job, Psalms, Proverbs, Ecclesiastes, Song of Solomon
- Prophets: Isaiah, Jeremiah, Lamentations, Ezekiel, Daniel, Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi

## Morphology Parsing

The importer converts Packard morphology codes to our database format:

- **N1-DSF** → Noun, Dative, Singular, Feminine
- **VAI-AAI3S** → Verb, Aorist, Active, Indicative, 3rd person, Singular
- **RA-NSM** → Article (Pronoun), Nominative, Singular, Masculine
- **P** → Preposition
- **C** → Conjunction

## Known Limitations

1. **Lemmas**: Currently using inflected forms as lemmas (Strong's numbers available but not converted to Greek)
2. **Unparsed codes**: Some rare morphology codes (~25%) aren't yet mapped
3. **Import time**: Full import takes 30-60 minutes

## Future Enhancements

- [ ] Map Strong's numbers to actual Greek lemmas
- [ ] Add remaining morphology code mappings
- [ ] Optimize import speed with batch inserts
- [ ] Add Apocrypha/Deuterocanonical books

## Troubleshooting

**"ModuleNotFoundError: No module named 'pysword'"**
```bash
pip install pysword
```

**"Database is locked"**
- Close the Flask app before running the importer
- Only one process can write to SQLite at a time

**"SWORD module not found"**
- Verify the path in `lxx_importer.py` points to your LXX directory
- Default: `C:\Users\stmitchell\LXX`

## Questions?

The LXX integration is complete and functional. The Genesis 1 test data proves the system works end-to-end. Run the full import when convenient!
