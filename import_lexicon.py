"""
Script to download the MorphGNT morphological lexicon (lexemes.yaml) and import
English glosses into the greek_nt.db database.

Run this once to add glosses to an existing database:
    python import_lexicon.py

Or it will be called automatically by setup_database.py for new installs.
"""

import sqlite3
import requests
import os

LEXEMES_URL = "https://raw.githubusercontent.com/morphgnt/morphological-lexicon/master/lexemes.yaml"
DATABASE = "greek_nt.db"


def download_lexemes() -> str:
    """Download the lexemes.yaml file and return its text content."""
    print("Downloading MorphGNT morphological lexicon (lexemes.yaml)...")
    try:
        response = requests.get(LEXEMES_URL, timeout=30)
        response.raise_for_status()
        print(f"  [OK] Downloaded {len(response.text):,} characters")
        return response.text
    except Exception as e:
        print(f"  [ERROR] {e}")
        return ""


def parse_lexemes_yaml(text: str) -> dict:
    """
    Parse lexemes.yaml to extract a lemma → gloss mapping.

    The file format is simple YAML:
        GreekLemma:
         gloss: English gloss text
         pos: N
         ...

    We only care about the top-level key (lemma) and the 'gloss' property.
    """
    entries = {}
    current_lemma = None

    for line in text.split("\n"):
        # Top-level key: line not starting with whitespace, ending with ':'
        if line and not line[0].isspace() and line.endswith(":"):
            current_lemma = line[:-1].strip()
        elif current_lemma and line.strip().startswith("gloss:"):
            gloss_part = line.split(":", 1)[1].strip()
            if gloss_part:
                entries[current_lemma] = gloss_part

    return entries


def create_lexicon_table(conn: sqlite3.Connection):
    """Create the lexicon table if it doesn't already exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lexicon (
            lemma TEXT PRIMARY KEY,
            gloss TEXT NOT NULL
        )
    """)
    conn.commit()


def populate_lexicon(conn: sqlite3.Connection, entries: dict):
    """Insert or replace lexicon entries into the database."""
    rows = [(lemma, gloss) for lemma, gloss in entries.items()]
    conn.executemany(
        "INSERT OR REPLACE INTO lexicon (lemma, gloss) VALUES (?, ?)",
        rows
    )
    conn.commit()
    return len(rows)


def main():
    print("=" * 60)
    print("Greek NT Lexicon Import")
    print("=" * 60)
    print()

    if not os.path.exists(DATABASE):
        print(f"Error: {DATABASE} not found.")
        print("Please run 'python setup_database.py' first.")
        return

    text = download_lexemes()
    if not text:
        print("Failed to download lexicon data. Aborting.")
        return

    print("Parsing lexicon entries...")
    entries = parse_lexemes_yaml(text)
    print(f"  [OK] Parsed {len(entries):,} lemma entries")
    print()

    conn = sqlite3.connect(DATABASE)
    create_lexicon_table(conn)

    print("Importing glosses into database...")
    count = populate_lexicon(conn, entries)
    print(f"  [OK] Imported {count:,} glosses")

    conn.close()
    print()
    print("=" * 60)
    print("Lexicon import complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
