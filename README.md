# Greek New Testament Bible Study App

A web-based application for studying the Greek New Testament with advanced linguistic syntax querying capabilities.

## Features

- **Complete Greek New Testament**: Full text of the Greek NT (Nestle-Aland/UBS text)
- **Linguistic Syntax Queries**: Search and filter based on:
  - Part of speech (verb, noun, adjective, etc.)
  - Morphological features (case, number, gender, tense, voice, mood)
  - Lemmas (dictionary forms)
  - Grammatical relationships
- **Advanced Search**: Combine multiple linguistic criteria
- **Verse Context**: View results with full verse context and references

## Technology Stack

- **Backend**: Python with Flask
- **Database**: SQLite with full-text search
- **Data Source**: MorphGNT (Morphologically tagged Greek New Testament)
- **Frontend**: HTML/CSS/JavaScript with modern UI

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_database.py

# Run the application
python app.py
```

## Query Examples

- Find all aorist passive verbs
- Search for specific lemmas (e.g., λόγος)
- Filter by grammatical case (nominative, genitive, etc.)
- Combine criteria (e.g., all participles in dative case)

## Data Attribution

This project uses MorphGNT data, which is freely available under the CC BY-SA License.
