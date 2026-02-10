"""
Inference Search Module
Finds verses with similar syntactic/grammatical structure to a given source verse.
"""

import sqlite3
import re
from typing import Dict, List, Tuple, Any, Optional
from difflib import SequenceMatcher

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


def get_verse_pattern(
    conn: sqlite3.Connection,
    book_code: str,
    chapter: int,
    verse: int,
    corpus: str = 'NT',
    include_morphology: bool = False
) -> List[Dict[str, Any]]:
    """
    Extract the grammatical pattern from a specific verse.
    
    Args:
        conn: Database connection
        book_code: Book code
        chapter: Chapter number
        verse: Verse number
        corpus: Corpus ('NT' or 'LXX')
        include_morphology: If True, include case, number, gender in pattern
    
    Returns:
        List of dicts with pattern elements, each containing:
        - pos: part of speech
        - case: grammatical case (if include_morphology)
        - number: grammatical number (if include_morphology)
        - gender: grammatical gender (if include_morphology)
        - pattern_str: string representation for matching
    """
    cursor = conn.cursor()
    
    if include_morphology:
        query = """
            SELECT pos, case_val, number, gender, word
            FROM words
            WHERE book_code = ? AND chapter = ? AND verse = ? AND corpus = ?
            ORDER BY word_position
        """
    else:
        query = """
            SELECT pos, word
            FROM words
            WHERE book_code = ? AND chapter = ? AND verse = ? AND corpus = ?
            ORDER BY word_position
        """
    
    cursor.execute(query, (book_code, chapter, verse, corpus))
    rows = cursor.fetchall()
    
    pattern = []
    for row in rows:
        if include_morphology:
            pos, case_val, number, gender, word = row
            
            # Build a pattern string like "noun-gsm" or "verb-3pai"
            parts = [pos] if pos else ['?']
            if case_val:
                parts.append(case_val[0])  # First letter
            if number:
                parts.append(number[0])  # First letter
            if gender:
                parts.append(gender[0])  # First letter
            
            pattern_str = '-'.join(parts)
            
            pattern.append({
                'pos': pos,
                'case': case_val,
                'number': number,
                'gender': gender,
                'word': word,
                'pattern_str': pattern_str
            })
        else:
            pos, word = row
            pattern.append({
                'pos': pos if pos else '?',
                'word': word,
                'pattern_str': pos if pos else '?'
            })
    
    return pattern


def calculate_pattern_similarity(pattern1: List[str], pattern2: List[str]) -> float:
    """
    Calculate similarity between two patterns using sequence matching.
    Returns a score between 0 and 1 (1 = identical).
    
    Uses SequenceMatcher which implements a Ratcliff-Obershelp algorithm,
    which finds the longest contiguous matching subsequence.
    """
    if not pattern1 or not pattern2:
        return 0.0
    
    # Use SequenceMatcher to get similarity ratio
    matcher = SequenceMatcher(None, pattern1, pattern2)
    return matcher.ratio()


def levenshtein_distance(seq1: List[str], seq2: List[str]) -> int:
    """
    Calculate the Levenshtein distance between two sequences.
    Returns the minimum number of edits (insertions, deletions, substitutions)
    needed to transform seq1 into seq2.
    """
    len1, len2 = len(seq1), len(seq2)
    
    # Create a matrix to store distances
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    # Initialize base cases
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
    
    # Fill the matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if seq1[i-1] == seq2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # Deletion
                    dp[i][j-1],    # Insertion
                    dp[i-1][j-1]   # Substitution
                )
    
    return dp[len1][len2]


def search_by_pattern(
    conn: sqlite3.Connection,
    source_pattern: List[Dict[str, Any]],
    source_book: str,
    source_chapter: int,
    source_verse: int,
    corpora: List[str] = None,
    min_similarity: float = 0.6,
    include_morphology: bool = False,
    max_results: int = 100,
    book_codes: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for verses with similar syntactic patterns.
    
    Args:
        conn: Database connection
        source_pattern: Pattern from source verse
        source_book: Book code of source verse
        source_chapter: Chapter of source verse
        source_verse: Verse number of source verse
        corpora: List of corpora to search ('NT', 'LXX', or both)
        min_similarity: Minimum similarity threshold (0.0 to 1.0)
        include_morphology: Whether pattern includes morphological details
        max_results: Maximum number of results to return
        book_codes: Optional list of book codes to filter results (e.g., ['01', '06'])
    
    Returns:
        List of dicts with match information, sorted by similarity (descending)
    """
    if not source_pattern:
        return []
    
    if corpora is None:
        corpora = ['NT']
    
    cursor = conn.cursor()
    
    # Extract pattern strings from source
    source_pattern_strs = [p['pattern_str'] for p in source_pattern]
    source_length = len(source_pattern_strs)
    
    # Get all verses in the corpus
    corpus_placeholders = ','.join(['?' for _ in corpora])
    
    # Add book filtering if specified
    book_filter = ""
    if book_codes:
        book_placeholders = ','.join(['?' for _ in book_codes])
        book_filter = f"AND book_code IN ({book_placeholders})"
    
    query = f"""
        SELECT DISTINCT book_code, chapter, verse, corpus
        FROM words
        WHERE corpus IN ({corpus_placeholders})
        {book_filter}
        AND NOT (book_code = ? AND chapter = ? AND verse = ?)
        ORDER BY book_code, chapter, verse
    """
    
    params = corpora
    if book_codes:
        params = params + book_codes
    params = params + [source_book, source_chapter, source_verse]
    cursor.execute(query, params)
    all_verses = cursor.fetchall()
    
    results = []
    
    # Compare each verse's pattern to the source pattern
    for book_code, chapter, verse, corpus in all_verses:
        # Get pattern for this verse
        verse_pattern = get_verse_pattern(
            conn, book_code, chapter, verse, corpus, include_morphology
        )
        
        if not verse_pattern:
            continue
        
        verse_pattern_strs = [p['pattern_str'] for p in verse_pattern]
        
        # Calculate similarity
        similarity = calculate_pattern_similarity(source_pattern_strs, verse_pattern_strs)
        
        # Skip if below threshold
        if similarity < min_similarity:
            continue
        
        # Get verse text with POS tags for highlighting
        temp_cursor = conn.cursor()
        verse_words_data = temp_cursor.execute(
            "SELECT word, pos FROM words WHERE book_code = ? AND chapter = ? AND verse = ? AND corpus = ? ORDER BY word_position",
            (book_code, chapter, verse, corpus)
        ).fetchall()
        
        # Create array of word objects with POS
        verse_words = [{'word': word, 'pos': pos if pos else 'unknown'} for word, pos in verse_words_data]
        verse_text = ' '.join([w['word'] for w in verse_words])
        
        # Get book name
        book_name_result = temp_cursor.execute(
            "SELECT book_name FROM books WHERE book_code = ? AND corpus = ? LIMIT 1",
            (book_code, corpus)
        ).fetchone()
        
        book_name = book_name_result[0] if book_name_result else f"Book {book_code}"
        
        # Calculate edit distance for additional metric
        edit_distance = levenshtein_distance(source_pattern_strs, verse_pattern_strs)
        
        results.append({
            'book_code': book_code,
            'book_name': book_name,
            'chapter': chapter,
            'verse': verse,
            'corpus': corpus,
            'verse_text': verse_text.strip(),
            'verse_words': verse_words,  # Array of {word, pos} objects for highlighting
            'pattern': verse_pattern_strs,
            'pattern_objects': verse_pattern,  # Full pattern objects with POS details
            'similarity': round(similarity * 100, 1),  # Convert to percentage
            'edit_distance': edit_distance,
            'length_diff': abs(len(verse_pattern_strs) - source_length)
        })
        
        # Early exit if we have enough results with high similarity
        if len(results) >= max_results * 2:
            # Sort and trim
            results.sort(key=lambda x: (-x['similarity'], x['edit_distance'], x['length_diff']))
            results = results[:max_results]
    
    # Final sort by similarity (descending), then by edit distance (ascending)
    results.sort(key=lambda x: (-x['similarity'], x['edit_distance'], x['length_diff']))
    
    # Limit results
    return results[:max_results]


def get_verse_text(
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
