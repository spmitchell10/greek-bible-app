"""
LXX (Septuagint) Importer for Greek Bible Study App
Extracts morphologically tagged text from SWORD module and imports into database.
"""

import sqlite3
import re
from typing import Dict, List, Tuple, Optional
from pysword.modules import SwordModules
import xml.etree.ElementTree as ET

# Packard morphology code mapping
# Format: Category-Number-Case-Number-Gender (e.g., N1-DSF)
# Position codes vary by part of speech

def parse_packard_morph(morph_code: str) -> Dict[str, str]:
    """
    Parse Packard morphology codes into database fields.
    
    Examples:
    - N1-DSF: Noun, 1st declension, Dative, Singular, Feminine
    - VAI-AAI3S: Verb, Aorist, Active, Indicative, 3rd person, Singular
    - RA-NSM: Article (pRonoun-Article), Nominative, Singular, Masculine
    """
    morph = {}
    
    # Remove 'packard:' prefix if present
    if ':' in morph_code:
        morph_code = morph_code.split(':')[1]
    
    # Noun pattern: N#-CSG where C=case, S=number, G=gender
    noun_match = re.match(r'N(\d+)-(.)(.)(.*)', morph_code)
    if noun_match:
        morph['pos'] = 'noun'
        case_code = noun_match.group(2)
        number_code = noun_match.group(3)
        gender_code = noun_match.group(4) if noun_match.group(4) else None
        
        # Case mapping
        case_map = {'N': 'nominative', 'G': 'genitive', 'D': 'dative', 'A': 'accusative', 'V': 'vocative'}
        if case_code in case_map:
            morph['case'] = case_map[case_code]
        
        # Number mapping
        if number_code == 'S':
            morph['number'] = 'singular'
        elif number_code == 'P':
            morph['number'] = 'plural'
        
        # Gender mapping
        if gender_code:
            gender_map = {'M': 'masculine', 'F': 'feminine', 'N': 'neuter'}
            if gender_code in gender_map:
                morph['gender'] = gender_map[gender_code]
        
        return morph
    
    # Verb pattern: V..-...#. where positions are tense/voice/mood/person/number
    verb_match = re.match(r'V([A-Z]{2})-([A-Z])([A-Z])([A-Z])(\d)?(.)?', morph_code)
    if verb_match:
        morph['pos'] = 'verb'
        tense_code = verb_match.group(1)
        voice_code = verb_match.group(2)
        mood_code = verb_match.group(3)
        tense_variant = verb_match.group(4)
        person_code = verb_match.group(5)
        number_code = verb_match.group(6)
        
        # Tense mapping
        tense_map = {
            'PA': 'present', 'IA': 'imperfect', 'FA': 'future',
            'AA': 'aorist', 'XA': 'perfect', 'YA': 'pluperfect',
            'AI': 'aorist'  # Alternative aorist code
        }
        if tense_code in tense_map:
            morph['tense'] = tense_map[tense_code]
        
        # Voice mapping
        voice_map = {'A': 'active', 'M': 'middle', 'P': 'passive'}
        if voice_code in voice_map:
            morph['voice'] = voice_map[voice_code]
        
        # Mood mapping
        mood_map = {'I': 'indicative', 'S': 'subjunctive', 'O': 'optative', 
                    'D': 'imperative', 'N': 'infinitive', 'P': 'participle'}
        if mood_code in mood_map:
            morph['mood'] = mood_map[mood_code]
        
        # Person
        if person_code:
            person_map = {'1': '1st', '2': '2nd', '3': '3rd'}
            if person_code in person_map:
                morph['person'] = person_map[person_code]
        
        # Number
        if number_code:
            if number_code == 'S':
                morph['number'] = 'singular'
            elif number_code == 'P':
                morph['number'] = 'plural'
        
        return morph
    
    # Article pattern: RA-CSG (pRonoun-Article)
    article_match = re.match(r'RA?-?(.)(.)(.)?', morph_code)
    if article_match or morph_code.startswith('RA'):
        morph['pos'] = 'pronoun'  # Articles stored as pronouns
        parts = morph_code.replace('RA-', '').replace('RA', '')
        if len(parts) >= 2:
            case_code = parts[0] if len(parts) > 0 else None
            number_code = parts[1] if len(parts) > 1 else None
            gender_code = parts[2] if len(parts) > 2 else None
            
            case_map = {'N': 'nominative', 'G': 'genitive', 'D': 'dative', 'A': 'accusative', 'V': 'vocative'}
            if case_code in case_map:
                morph['case'] = case_map[case_code]
            
            if number_code == 'S':
                morph['number'] = 'singular'
            elif number_code == 'P':
                morph['number'] = 'plural'
            
            if gender_code:
                gender_map = {'M': 'masculine', 'F': 'feminine', 'N': 'neuter'}
                if gender_code in gender_map:
                    morph['gender'] = gender_map[gender_code]
        
        return morph
    
    # Adjective pattern: similar to noun
    adj_match = re.match(r'A(\d+)-(.)(.)(.*)', morph_code)
    if adj_match:
        morph['pos'] = 'adjective'
        case_code = adj_match.group(2)
        number_code = adj_match.group(3)
        gender_code = adj_match.group(4) if adj_match.group(4) else None
        
        case_map = {'N': 'nominative', 'G': 'genitive', 'D': 'dative', 'A': 'accusative', 'V': 'vocative'}
        if case_code in case_map:
            morph['case'] = case_map[case_code]
        
        if number_code == 'S':
            morph['number'] = 'singular'
        elif number_code == 'P':
            morph['number'] = 'plural'
        
        if gender_code:
            gender_map = {'M': 'masculine', 'F': 'feminine', 'N': 'neuter'}
            if gender_code in gender_map:
                morph['gender'] = gender_map[gender_code]
        
        return morph
    
    # Simple POS codes
    simple_pos = {
        'P': 'preposition',
        'C': 'conjunction',
        'D': 'adverb',
        'T': 'particle',
        'X': 'interjection'
    }
    
    if morph_code[0] in simple_pos:
        morph['pos'] = simple_pos[morph_code[0]]
        return morph
    
    # If we can't parse it, return what we have
    print(f"Warning: Could not fully parse morphology code: {morph_code}")
    return morph


def extract_strong_number(lemma: str) -> Optional[str]:
    """Extract Strong's number from lemma field (e.g., 'strong:G746' -> 'G746')"""
    if 'strong:' in lemma:
        return lemma.split('strong:')[1]
    return None


# LXX Book mapping (OT books)
# Book codes start at 40 to avoid conflict with NT (01-27)
LXX_BOOKS = {
    'Genesis': ('40', 'Gen'),
    'Exodus': ('41', 'Exod'),
    'Leviticus': ('42', 'Lev'),
    'Numbers': ('43', 'Num'),
    'Deuteronomy': ('44', 'Deut'),
    'Joshua': ('45', 'Josh'),
    'Judges': ('46', 'Judg'),
    'Ruth': ('47', 'Ruth'),
    '1 Samuel': ('48', '1Sam'),
    '2 Samuel': ('49', '2Sam'),
    '1 Kings': ('50', '1Kgs'),
    '2 Kings': ('51', '2Kgs'),
    '1 Chronicles': ('52', '1Chr'),
    '2 Chronicles': ('53', '2Chr'),
    'Ezra': ('54', 'Ezra'),
    'Nehemiah': ('55', 'Neh'),
    'Esther': ('56', 'Esth'),
    'Job': ('57', 'Job'),
    'Psalms': ('58', 'Ps'),
    'Proverbs': ('59', 'Prov'),
    'Ecclesiastes': ('60', 'Eccl'),
    'Song of Solomon': ('61', 'Song'),
    'Isaiah': ('62', 'Isa'),
    'Jeremiah': ('63', 'Jer'),
    'Lamentations': ('64', 'Lam'),
    'Ezekiel': ('65', 'Ezek'),
    'Daniel': ('66', 'Dan'),
    'Hosea': ('67', 'Hos'),
    'Joel': ('68', 'Joel'),
    'Amos': ('69', 'Amos'),
    'Obadiah': ('70', 'Obad'),
    'Jonah': ('71', 'Jonah'),
    'Micah': ('72', 'Mic'),
    'Nahum': ('73', 'Nah'),
    'Habakkuk': ('74', 'Hab'),
    'Zephaniah': ('75', 'Zeph'),
    'Haggai': ('76', 'Hag'),
    'Zechariah': ('77', 'Zech'),
    'Malachi': ('78', 'Mal'),
}


def parse_osis_verse(osis_text: str) -> List[Dict]:
    """
    Parse OSIS XML to extract words with morphology.
    
    Example OSIS:
    <w lemma="strong:G746" morph="packard:N1-DSF">ἀρχῇ</w>
    """
    words = []
    
    # Find all <w> tags
    word_pattern = r'<w\s+lemma="([^"]*)"\s+morph="([^"]*)"\s*[^>]*>([^<]*)</w>'
    matches = re.findall(word_pattern, osis_text)
    
    for lemma, morph, word_text in matches:
        # Skip empty words
        if not word_text.strip():
            continue
        
        # Parse morphology
        parsed_morph = parse_packard_morph(morph)
        
        # Extract Strong's number
        strong_num = extract_strong_number(lemma)
        
        words.append({
            'word': word_text.strip(),
            'strong_number': strong_num,
            'lemma': word_text.strip(),  # For now, use the word itself as lemma
            'morph_code': morph.replace('packard:', ''),
            'morphology': parsed_morph
        })
    
    return words


def import_lxx_to_database(sword_dir: str, db_path: str):
    """
    Import LXX data from SWORD module into the database.
    """
    print("=" * 60)
    print("LXX Septuagint Importer")
    print("=" * 60)
    
    # Initialize SWORD module
    print("\nLoading SWORD module...")
    modules = SwordModules(sword_dir)
    modules.parse_modules()
    lxx = modules.get_bible_from_module('LXX')
    print("[OK] LXX module loaded")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add LXX books to books table if needed
    print("\nAdding LXX books to database...")
    for book_name, (book_code, book_abbrev) in LXX_BOOKS.items():
        cursor.execute("""
            INSERT OR IGNORE INTO books (book_code, book_name, book_abbrev, corpus)
            VALUES (?, ?, ?, 'LXX')
        """, (book_code, book_name, book_abbrev))
    
    conn.commit()
    print(f"[OK] Added {len(LXX_BOOKS)} LXX books")
    
    # Import words from each book
    total_words = 0
    
    for book_name, (book_code, book_abbrev) in LXX_BOOKS.items():
        print(f"\nProcessing {book_name}...")
        
        try:
            # Get book structure (how many chapters)
            # Try to get first 50 chapters (most books have fewer)
            book_words = 0
            
            for chapter in range(1, 151):  # Max 150 chapters (Psalms)
                try:
                    # Get all verses in the chapter
                    # Try up to 200 verses (some chapters are long)
                    for verse in range(1, 201):
                        try:
                            # Get verse with morphology
                            verse_data = lxx.get(books=[book_name], chapters=[chapter], verses=[verse], clean=False)
                            
                            if not verse_data:
                                break  # No more verses in this chapter
                            
                            # Parse OSIS to extract words
                            verse_text = str(verse_data)
                            words = parse_osis_verse(verse_text)
                            
                            # Insert words into database
                            for word_position, word_data in enumerate(words, 1):
                                morph = word_data['morphology']
                                
                                cursor.execute("""
                                    INSERT INTO words (
                                        book_code, chapter, verse, word_position, word, lemma,
                                        morph_code, pos, tense, voice, mood, case_value, 
                                        number, gender, person, corpus
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'LXX')
                                """, (
                                    book_code, chapter, verse, word_position,
                                    word_data['word'], word_data['lemma'],
                                    word_data['morph_code'],
                                    morph.get('pos'),
                                    morph.get('tense'),
                                    morph.get('voice'),
                                    morph.get('mood'),
                                    morph.get('case'),
                                    morph.get('number'),
                                    morph.get('gender'),
                                    morph.get('person')
                                ))
                                
                                book_words += 1
                                total_words += 1
                            
                        except Exception as e:
                            # Probably no more verses in this chapter
                            break
                    
                    # Commit after each chapter
                    if book_words > 0:
                        conn.commit()
                    
                except Exception as e:
                    # Probably no more chapters in this book
                    break
            
            print(f"  [OK] {book_name} completed ({book_words} words, {total_words} total)")
            
        except Exception as e:
            print(f"  [ERROR] {book_name}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"LXX import complete! Imported {total_words} words from {len(LXX_BOOKS)} books.")
    print("=" * 60)
    
    conn.close()


if __name__ == "__main__":
    import os
    
    sword_dir = r"C:\Users\stmitchell\LXX"
    db_path = "greek_nt.db"
    
    if not os.path.exists(db_path):
        print("Error: Database not found! Please run setup_database.py first.")
        exit(1)
    
    import_lxx_to_database(sword_dir, db_path)
