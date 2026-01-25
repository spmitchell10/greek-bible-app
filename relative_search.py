"""
Relative Search Module
Finds verses with similar vocabulary (lemmas) to a given source verse.
"""

import sqlite3
import re
from typing import Dict, List, Tuple, Any

# Part of speech weights for scoring
POS_WEIGHTS = {
    'verb': 3,
    'noun': 3,
    'adjective': 3,
    'adverb': 3,
    'pronoun': 1,
    'article': 1,
    'preposition': 1,
    'particle': 1,
    'conjunction': 1,
    'interjection': 1,
}

# Book abbreviations to codes (from query_parser.py)
BOOK_ABBREVIATIONS = {
    # New Testament
    'matt': '01', 'matthew': '01', 'mt': '01',
    'mark': '02', 'mk': '02', 'mar': '02',
    'luke': '03', 'lk': '03', 'luk': '03',
    'john': '04', 'jn': '04', 'joh': '04',
    'acts': '05', 'ac': '05', 'act': '05',
    'rom': '06', 'romans': '06', 'ro': '06',
    '1cor': '07', '1 cor': '07', '1corinthians': '07',
    '2cor': '08', '2 cor': '08', '2corinthians': '08',
    'gal': '09', 'galatians': '09',
    'eph': '10', 'ephesians': '10',
    'phil': '11', 'philippians': '11', 'php': '11',
    'col': '12', 'colossians': '12',
    '1thess': '13', '1 thess': '13', '1thessalonians': '13', '1th': '13',
    '2thess': '14', '2 thess': '14', '2thessalonians': '14', '2th': '14',
    '1tim': '15', '1 tim': '15', '1timothy': '15', '1ti': '15',
    '2tim': '16', '2 tim': '16', '2timothy': '16', '2ti': '16',
    'titus': '17', 'tit': '17', 'ti': '17',
    'philem': '18', 'philemon': '18', 'phm': '18',
    'heb': '19', 'hebrews': '19',
    'james': '20', 'jas': '20', 'jam': '20',
    '1pet': '21', '1 pet': '21', '1peter': '21', '1pe': '21',
    '2pet': '22', '2 pet': '22', '2peter': '22', '2pe': '22',
    '1john': '23', '1 john': '23', '1jn': '23', '1jo': '23',
    '2john': '24', '2 john': '24', '2jn': '24', '2jo': '24',
    '3john': '25', '3 john': '25', '3jn': '25', '3jo': '25',
    'jude': '26', 'jud': '26',
    'rev': '27', 'revelation': '27', 're': '27',
}


def parse_verse_reference(ref: str) -> Tuple[str, int, int]:
    """
    Parse a verse reference like 'Rom. 8:1' or 'Romans 8:1'
    Returns (book_code, chapter, verse)
    """
    # Remove periods and extra spaces
    ref = ref.replace('.', '').strip()
    
    # Match patterns like "Rom 8:1" or "1 Cor 8:1"
    match = re.match(r'^([123]?\s*[a-zA-Z]+)\s+(\d+):(\d+)$', ref)
    if not match:
        raise ValueError(f"Invalid verse reference format: {ref}")
    
    book_str, chapter_str, verse_str = match.groups()
    book_str = book_str.lower().replace(' ', '')
    
    # Look up book code
    book_code = BOOK_ABBREVIATIONS.get(book_str)
    if not book_code:
        raise ValueError(f"Unknown book: {book_str}")
    
    return book_code, int(chapter_str), int(verse_str)


def get_verse_words(conn: sqlite3.Connection, book_code: str, chapter: int, verse: int) -> List[Dict[str, Any]]:
    """
    Get unique lemmas from a specific verse with their parts of speech.
    Returns list of dicts with keys: lemma, pos, weight (deduplicated by lemma)
    """
    cursor = conn.cursor()
    
    query = """
        SELECT DISTINCT lemma, pos
        FROM words
        WHERE book_code = ? AND chapter = ? AND verse = ?
        ORDER BY lemma
    """
    
    cursor.execute(query, (book_code, chapter, verse))
    rows = cursor.fetchall()
    
    # Use a dict to track unique lemmas (in case same lemma has different POS)
    lemma_dict = {}
    for row in rows:
        lemma, pos = row
        
        if not lemma:  # Skip empty lemmas
            continue
        
        # Determine weight based on part of speech
        weight = POS_WEIGHTS.get(pos, 1)
        
        # If lemma already exists, keep the higher weight
        if lemma in lemma_dict:
            if weight > lemma_dict[lemma]['weight']:
                lemma_dict[lemma] = {
                    'lemma': lemma,
                    'pos': pos,
                    'weight': weight
                }
        else:
            lemma_dict[lemma] = {
                'lemma': lemma,
                'pos': pos,
                'weight': weight
            }
    
    # Convert to list and sort by weight (descending), then alphabetically
    words = sorted(lemma_dict.values(), key=lambda x: (-x['weight'], x['lemma']))
    
    return words


def search_by_lemmas(
    conn: sqlite3.Connection,
    lemmas: List[Dict[str, Any]],
    source_book: str,
    source_chapter: int,
    source_verse: int,
    corpora: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for verses containing the given lemmas.
    Returns results sorted by similarity score (descending).
    
    Args:
        conn: Database connection
        lemmas: List of dicts with 'lemma', 'pos', and 'weight' keys
        source_book: Book code of source verse
        source_chapter: Chapter of source verse
        source_verse: Verse number of source verse
        corpora: List of corpora to search ('NT', 'LXX', or both)
    """
    if not lemmas:
        return []
    
    if corpora is None:
        corpora = ['NT']
    
    cursor = conn.cursor()
    
    # Build a query that counts matches for each verse
    # We'll use a subquery approach to score each verse
    
    # Create a list of lemmas to search for
    lemma_list = [l['lemma'] for l in lemmas if l['lemma']]
    if not lemma_list:
        return []
    
    # Create a mapping of lemma -> weight
    lemma_weights = {l['lemma']: l['weight'] for l in lemmas}
    
    # Build the query
    placeholders = ','.join(['?' for _ in lemma_list])
    corpus_placeholders = ','.join(['?' for _ in corpora])
    
    query = f"""
        SELECT 
            book_code,
            chapter,
            verse,
            corpus
        FROM words
        WHERE lemma IN ({placeholders})
        AND corpus IN ({corpus_placeholders})
        AND NOT (book_code = ? AND chapter = ? AND verse = ?)
        GROUP BY book_code, chapter, verse, corpus
        ORDER BY book_code, chapter, verse
    """
    
    params = lemma_list + corpora + [source_book, source_chapter, source_verse]
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Score each result
    results = []
    for row in rows:
        book_code, chapter, verse, corpus = row
        
        # Use a separate cursor for each nested query
        temp_cursor = conn.cursor()
        
        # Get all words with their lemmas from the verse
        words_data = temp_cursor.execute(
            "SELECT word, lemma FROM words WHERE book_code = ? AND chapter = ? AND verse = ? AND corpus = ? ORDER BY word_position",
            (book_code, chapter, verse, corpus)
        ).fetchall()
        
        # Build verse text with matching words in bold
        verse_words = []
        matched_lemmas = set()
        for word, lemma in words_data:
            if lemma in lemma_list:
                # This word matches - wrap in <strong> tags
                verse_words.append(f"<strong>{word}</strong>")
                matched_lemmas.add(lemma)
            else:
                verse_words.append(word)
        
        verse_text = " ".join(verse_words)
        
        # Calculate score
        score = sum(lemma_weights.get(lemma, 1) for lemma in matched_lemmas)
        
        # Get book name
        book_name_result = temp_cursor.execute(
            "SELECT book_name FROM books WHERE book_code = ? AND corpus = ? LIMIT 1",
            (book_code, corpus)
        ).fetchone()
        
        if not book_name_result:
            # Fallback if book not found
            book_name = f"Book {book_code}"
        else:
            book_name = book_name_result[0]
        
        results.append({
            'book_code': book_code,
            'book_name': book_name,
            'chapter': chapter,
            'verse': verse,
            'corpus': corpus,
            'verse_text': verse_text.strip(),
            'matched_lemmas': list(matched_lemmas),
            'score': score,
            'match_count': len(matched_lemmas)
        })
    
    # Sort by score (descending), then by match count
    results.sort(key=lambda x: (x['score'], x['match_count']), reverse=True)
    
    return results


def get_verse_context(
    conn: sqlite3.Connection,
    book_code: str,
    chapter: int,
    verse: int,
    corpus: str = 'NT'
) -> str:
    """Get the full text of a verse."""
    cursor = conn.cursor()
    
    query = """
        SELECT GROUP_CONCAT(word, ' ')
        FROM words
        WHERE book_code = ? AND chapter = ? AND verse = ? AND corpus = ?
        ORDER BY word_position
    """
    
    cursor.execute(query, (book_code, chapter, verse, corpus))
    result = cursor.fetchone()
    return result[0] if result and result[0] else ""
