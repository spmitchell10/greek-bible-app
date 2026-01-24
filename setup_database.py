"""
Script to download MorphGNT data and set up the database for the Greek Bible Study App.
MorphGNT provides morphologically tagged Greek New Testament texts.
"""

import sqlite3
import requests
import os
import re
from typing import List, Tuple

# MorphGNT GitHub repository - contains morphologically tagged Greek NT
MORPHGNT_BASE_URL = "https://raw.githubusercontent.com/morphgnt/sblgnt/master/"

# List of NT books (in order)
# Format: (book_code, display_name, abbreviation, file_number, file_abbrev)
# Note: file_number is used in the filename (61-Mt-morphgnt.txt), book_code is used in the data (01)
NT_BOOKS = [
    ("01", "Matthew", "Matt", "61", "Mt"),
    ("02", "Mark", "Mark", "62", "Mk"),
    ("03", "Luke", "Luke", "63", "Lk"),
    ("04", "John", "John", "64", "Jn"),
    ("05", "Acts", "Acts", "65", "Ac"),
    ("06", "Romans", "Rom", "66", "Ro"),
    ("07", "1Corinthians", "1Cor", "67", "1Co"),
    ("08", "2Corinthians", "2Cor", "68", "2Co"),
    ("09", "Galatians", "Gal", "69", "Ga"),
    ("10", "Ephesians", "Eph", "70", "Eph"),
    ("11", "Philippians", "Phil", "71", "Php"),
    ("12", "Colossians", "Col", "72", "Col"),
    ("13", "1Thessalonians", "1Thess", "73", "1Th"),
    ("14", "2Thessalonians", "2Thess", "74", "2Th"),
    ("15", "1Timothy", "1Tim", "75", "1Ti"),
    ("16", "2Timothy", "2Tim", "76", "2Ti"),
    ("17", "Titus", "Titus", "77", "Tit"),
    ("18", "Philemon", "Phlm", "78", "Phm"),
    ("19", "Hebrews", "Heb", "79", "Heb"),
    ("20", "James", "Jas", "80", "Jas"),
    ("21", "1Peter", "1Pet", "81", "1Pe"),
    ("22", "2Peter", "2Pet", "82", "2Pe"),
    ("23", "1John", "1John", "83", "1Jn"),
    ("24", "2John", "2John", "84", "2Jn"),
    ("25", "3John", "3John", "85", "3Jn"),
    ("26", "Jude", "Jude", "86", "Jud"),
    ("27", "Revelation", "Rev", "87", "Re"),
]


def parse_morphology(morph_code: str) -> dict:
    """
    Parse MorphGNT morphology codes into readable components.
    Format: Combined POS (2 chars) + morphology (8 chars) = 10 chars total
    Example: "N-----NSF-" or "V-3AAI-S--"
    """
    if not morph_code or len(morph_code) < 2:
        return {}
    
    parts = {}
    
    # First character is part of speech
    pos_map = {
        "N": "noun",
        "V": "verb",
        "A": "adjective",
        "R": "pronoun",
        "C": "conjunction",
        "D": "adverb",
        "P": "preposition",
        "T": "article",
        "I": "interjection",
        "X": "particle",
    }
    
    parts["pos"] = pos_map.get(morph_code[0], morph_code[0])
    
    # For verbs: V-3AAI-S--
    # Position 2: person (1,2,3)
    # Position 3: tense (P,I,F,A,X,Y)
    # Position 4: voice (A,M,P)
    # Position 5: mood (I,D,S,O,N,P)
    # Position 7: number (S,P)
    # Position 8: gender (M,F,N)
    if morph_code[0] == "V" and len(morph_code) >= 8:
        # Person
        if len(morph_code) > 2 and morph_code[2] != "-":
            parts["person"] = morph_code[2] + "rd" if morph_code[2] == "3" else morph_code[2] + ("st" if morph_code[2] == "1" else "nd")
        # Tense
        tense_map = {"P": "present", "I": "imperfect", "F": "future", 
                     "A": "aorist", "X": "perfect", "Y": "pluperfect"}
        if len(morph_code) > 3 and morph_code[3] != "-":
            parts["tense"] = tense_map.get(morph_code[3], morph_code[3])
        # Voice
        voice_map = {"A": "active", "M": "middle", "P": "passive"}
        if len(morph_code) > 4 and morph_code[4] != "-":
            parts["voice"] = voice_map.get(morph_code[4], morph_code[4])
        # Mood
        mood_map = {"I": "indicative", "D": "imperative", "S": "subjunctive", 
                    "O": "optative", "N": "infinitive", "P": "participle"}
        if len(morph_code) > 5 and morph_code[5] != "-":
            parts["mood"] = mood_map.get(morph_code[5], morph_code[5])
        # Case (position 6, for participles)
        case_map = {"N": "nominative", "G": "genitive", "D": "dative", "A": "accusative", "V": "vocative"}
        if len(morph_code) > 6 and morph_code[6] != "-":
            parts["case"] = case_map.get(morph_code[6], morph_code[6])
        # Number
        if len(morph_code) > 7 and morph_code[7] != "-":
            parts["number"] = "singular" if morph_code[7] == "S" else "plural"
        # Gender
        if len(morph_code) > 8 and morph_code[8] != "-":
            gender_map = {"M": "masculine", "F": "feminine", "N": "neuter"}
            parts["gender"] = gender_map.get(morph_code[8], morph_code[8])
    
    # For nouns, adjectives, pronouns, articles: N-----NSF-
    # Position 6: case (N,G,D,A,V)
    # Position 7: number (S,P)
    # Position 8: gender (M,F,N)
    elif morph_code[0] in ["N", "A", "R", "T"] and len(morph_code) >= 8:
        # Case
        case_map = {"N": "nominative", "G": "genitive", "D": "dative", "A": "accusative", "V": "vocative"}
        if len(morph_code) > 6 and morph_code[6] != "-":
            parts["case"] = case_map.get(morph_code[6], morph_code[6])
        # Number
        if len(morph_code) > 7 and morph_code[7] != "-":
            parts["number"] = "singular" if morph_code[7] == "S" else "plural"
        # Gender
        if len(morph_code) > 8 and morph_code[8] != "-":
            gender_map = {"M": "masculine", "F": "feminine", "N": "neuter"}
            parts["gender"] = gender_map.get(morph_code[8], morph_code[8])
    
    return parts


def download_morphgnt_file(book_name: str, file_number: str, file_abbrev: str) -> List[str]:
    """Download a MorphGNT file for a specific book."""
    url = f"{MORPHGNT_BASE_URL}{file_number}-{file_abbrev}-morphgnt.txt"
    print(f"Downloading {book_name}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"  [OK] Successfully downloaded {book_name}")
        return response.text.strip().split("\n")
    except Exception as e:
        print(f"  [ERROR] Error downloading {book_name}: {e}")
        return []


def parse_morphgnt_line(line: str) -> dict:
    """
    Parse a single line from MorphGNT format.
    Format: REFERENCE POS MORPH WORD NORMALIZED VARIANT LEMMA
    Example: 010101 N- ----GSF- γενέσεως γενέσεως γενέσεως γένεσις
    The lemma (dictionary form) is in position 6.
    """
    parts = line.strip().split()
    if len(parts) < 7:  # Need at least 7 parts for lemma
        return None
    
    ref = parts[0]
    book = ref[:2]
    chapter = int(ref[2:4])
    verse = int(ref[4:6])
    word_pos = int(ref[6:]) if len(ref) > 6 else 1
    
    pos_code = parts[1] if len(parts) > 1 else ""
    morph_code = parts[2] if len(parts) > 2 else ""
    word = parts[3] if len(parts) > 3 else ""
    lemma = parts[6] if len(parts) > 6 else ""  # Fixed: lemma is at position 6
    
    # Combine pos and morph codes
    full_morph = pos_code + morph_code
    parsed_morph = parse_morphology(full_morph)
    
    return {
        "book_code": book,
        "chapter": chapter,
        "verse": verse,
        "word_position": word_pos,
        "word": word,
        "lemma": lemma,
        "morph_code": full_morph,
        "parsed_morph": parsed_morph,
    }


def create_database():
    """Create the SQLite database schema."""
    conn = sqlite3.connect("greek_nt.db")
    cursor = conn.cursor()
    
    # Books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_code TEXT PRIMARY KEY,
            book_name TEXT NOT NULL,
            book_abbrev TEXT NOT NULL,
            corpus TEXT NOT NULL DEFAULT 'NT'
        )
    """)
    
    # Words table with full morphological data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_code TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            word_position INTEGER NOT NULL,
            word TEXT NOT NULL,
            lemma TEXT NOT NULL,
            morph_code TEXT,
            pos TEXT,
            person TEXT,
            tense TEXT,
            voice TEXT,
            mood TEXT,
            case_value TEXT,
            number TEXT,
            gender TEXT,
            corpus TEXT NOT NULL DEFAULT 'NT',
            FOREIGN KEY (book_code) REFERENCES books(book_code),
            UNIQUE(book_code, chapter, verse, word_position, corpus)
        )
    """)
    
    # Create indexes for efficient querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_book_chapter_verse ON words(book_code, chapter, verse)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lemma ON words(lemma)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pos ON words(pos)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tense ON words(tense)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_voice ON words(voice)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mood ON words(mood)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_case ON words(case_value)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_number ON words(number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gender ON words(gender)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_corpus ON words(corpus)")
    
    # Full-text search virtual table
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS words_fts USING fts5(
            word, lemma, content=words, content_rowid=id
        )
    """)
    
    conn.commit()
    return conn


def populate_database(conn):
    """Download MorphGNT data and populate the database."""
    cursor = conn.cursor()
    
    # Insert books
    for book_code, book_name, book_abbrev, file_number, file_abbrev in NT_BOOKS:
        cursor.execute(
            "INSERT OR REPLACE INTO books (book_code, book_name, book_abbrev, corpus) VALUES (?, ?, ?, ?)",
            (book_code, book_name, book_abbrev, 'NT')
        )
    
    conn.commit()
    
    # Download and parse each book
    word_count = 0
    for book_code, book_name, book_abbrev, file_number, file_abbrev in NT_BOOKS:
        lines = download_morphgnt_file(book_name, file_number, file_abbrev)
        
        # Track word position within each verse
        current_verse = None
        verse_word_pos = 0
        
        for line in lines:
            if not line.strip():
                continue
            
            data = parse_morphgnt_line(line)
            if data:
                # Track word position within verse
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
                    verse_word_pos,  # Use tracked position instead of parsed position
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
                    'NT',  # Corpus identifier
                ))
                word_count += 1
        
        conn.commit()
        print(f"  [OK] {book_name} completed ({word_count} total words)")
    
    # Populate FTS table
    print("\nBuilding full-text search index...")
    cursor.execute("""
        INSERT INTO words_fts (rowid, word, lemma)
        SELECT id, word, lemma FROM words
    """)
    
    conn.commit()
    print(f"[OK] Database populated with {word_count} words!")


def main():
    """Main setup function."""
    print("=" * 60)
    print("Greek New Testament Bible Study App - Database Setup")
    print("=" * 60)
    print()
    
    if os.path.exists("greek_nt.db"):
        response = input("Database already exists. Recreate? (yes/no): ")
        if response.lower() != "yes":
            print("Setup cancelled.")
            return
        os.remove("greek_nt.db")
    
    print("Creating database schema...")
    conn = create_database()
    print("[OK] Database schema created")
    print()
    
    print("Downloading and parsing Greek New Testament data...")
    print("(This may take a few minutes)")
    print()
    populate_database(conn)
    
    conn.close()
    print()
    print("=" * 60)
    print("Setup complete! Run 'python app.py' to start the application.")
    print("=" * 60)


if __name__ == "__main__":
    main()
