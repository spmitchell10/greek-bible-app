"""
Advanced query parser for Greek NT search with custom syntax.

Syntax Examples:
- *λόγος@nsg - Search for λόγος as noun, singular, genitive
- *εἰμί@vaAi3s - Search for εἰμί as verb, aorist, active, indicative, 3rd person, singular
- *[article] & λόγος@nsg - Article followed by λόγος (noun, singular, genitive)
- *[article] & λόγος@nsg W2 - Article within 2 words of λόγος
"""

import re
from typing import List, Dict, Any, Tuple, Optional
import sqlite3


# Morphology code mappings (single character to database value)
# Order matters! Process in this order to avoid ambiguity
MORPH_CODE_ORDER = [
    ('pos', {
        'N': 'noun',
        'V': 'verb',
        'J': 'adjective',  # Changed from 'a' to avoid conflict with accusative
        'D': 'adverb',
        'C': 'conjunction',
        'P': 'preposition',
        'R': 'pronoun',
        'T': 'particle',
        'I': 'interjection',
    }),
    ('tense', {
        'p': 'present',
        'i': 'imperfect',
        'f': 'future',
        'a': 'aorist',
        'r': 'perfect',
        'l': 'pluperfect',
    }),
    ('voice', {
        'A': 'active',
        'M': 'middle',
        'P': 'passive',
    }),
    ('mood', {
        'I': 'indicative',  # Changed from 'i' to avoid conflict
        'S': 'subjunctive',  # Changed from 's' to avoid conflict
        'O': 'optative',
        'M': 'imperative',  # Note: conflicts with Middle voice - use context
        'N': 'infinitive',  # Changed from 'n' to avoid conflict
        'p': 'participle',
    }),
    ('person', {
        '1': '1st',
        '2': '2nd',
        '3': '3rd',
    }),
    ('case', {
        'n': 'nominative',
        'g': 'genitive',
        'd': 'dative',
        'a': 'accusative',
        'v': 'vocative',
    }),
    ('number', {
        's': 'singular',
        'p': 'plural',
    }),
    ('gender', {
        'm': 'masculine',
        'f': 'feminine',
        'u': 'neuter',  # Changed from 'n' to avoid conflict
    }),
]

# Book abbreviation to book code mapping
BOOK_ABBREVIATIONS = {
    'Matt': '01', 'Matt.': '01', 'Matthew': '01',
    'Mark': '02', 'Mk': '02', 'Mk.': '02',
    'Luke': '03', 'Lk': '03', 'Lk.': '03',
    'John': '04', 'Jn': '04', 'Jn.': '04',
    'Acts': '05', 'Ac': '05', 'Ac.': '05',
    'Rom': '06', 'Rom.': '06', 'Romans': '06',
    '1Cor': '07', '1Cor.': '07', '1Corinthians': '07',
    '2Cor': '08', '2Cor.': '08', '2Corinthians': '08',
    'Gal': '09', 'Gal.': '09', 'Galatians': '09',
    'Eph': '10', 'Eph.': '10', 'Ephesians': '10',
    'Phil': '11', 'Phil.': '11', 'Philippians': '11',
    'Col': '12', 'Col.': '12', 'Colossians': '12',
    '1Thess': '13', '1Thess.': '13', '1Th': '13', '1Thessalonians': '13',
    '2Thess': '14', '2Thess.': '14', '2Th': '14', '2Thessalonians': '14',
    '1Tim': '15', '1Tim.': '15', '1Ti': '15', '1Timothy': '15',
    '2Tim': '16', '2Tim.': '16', '2Ti': '16', '2Timothy': '16',
    'Titus': '17', 'Tit': '17', 'Tit.': '17',
    'Phlm': '18', 'Phlm.': '18', 'Phm': '18', 'Philemon': '18',
    'Heb': '19', 'Heb.': '19', 'Hebrews': '19',
    'Jas': '20', 'Jas.': '20', 'James': '20',
    '1Pet': '21', '1Pet.': '21', '1Pe': '21', '1Peter': '21',
    '2Pet': '22', '2Pet.': '22', '2Pe': '22', '2Peter': '22',
    '1John': '23', '1Jn': '23', '1Jn.': '23',
    '2John': '24', '2Jn': '24', '2Jn.': '24',
    '3John': '25', '3Jn': '25', '3Jn.': '25',
    'Jude': '26', 'Jud': '26', 'Jud.': '26',
    'Rev': '27', 'Rev.': '27', 'Re': '27', 'Revelation': '27',
}

# Special tokens for parts of speech
# Note: Articles are marked as pronouns with morph code starting with 'RA'
SPECIAL_TOKENS = {
    '[article]': {'pos': 'pronoun', 'morph_prefix': 'RA'},
    '[noun]': {'pos': 'noun'},
    '[verb]': {'pos': 'verb'},
    '[adjective]': {'pos': 'adjective'},
    '[pronoun]': {'pos': 'pronoun'},
    '[preposition]': {'pos': 'preposition'},
    '[conjunction]': {'pos': 'conjunction'},
    '[particle]': {'pos': 'particle'},
    '[adverb]': {'pos': 'adverb'},
}


class SearchTerm:
    """Represents a single search term in the query."""
    
    def __init__(self, lemma: Optional[str] = None, morph_codes: str = "", 
                 special_token: Optional[str] = None):
        self.lemma = lemma
        self.special_token = special_token
        self.morphology = self._parse_morphology(morph_codes)
    
    def _parse_morphology(self, codes: str) -> Dict[str, str]:
        """Parse morphology codes into database field values."""
        morph = {}
        used_chars = set()
        
        # Special handling: POS should only match first character if it's uppercase
        if codes and codes[0].isupper():
            for category, mapping in MORPH_CODE_ORDER:
                if category == 'pos' and codes[0] in mapping:
                    morph['pos'] = mapping[codes[0]]
                    used_chars.add(codes[0])
                    break
        
        # Process remaining codes in order
        for category, mapping in MORPH_CODE_ORDER:
            if category == 'pos':  # Already handled above
                continue
            for char in codes:
                if char in used_chars:
                    continue
                if char in mapping:
                    morph[category] = mapping[char]
                    used_chars.add(char)
                    break  # Only take first match per category
        
        return morph
    
    def to_sql_conditions(self) -> Tuple[str, List[Any]]:
        """Convert to SQL WHERE conditions."""
        conditions = []
        params = []
        
        if self.lemma:
            conditions.append("lemma = ?")
            params.append(self.lemma)
        
        if self.special_token and self.special_token in SPECIAL_TOKENS:
            token_morph = SPECIAL_TOKENS[self.special_token]
            for field, value in token_morph.items():
                if field == 'morph_prefix':
                    # Special handling for morph code prefix (e.g., RA for articles)
                    conditions.append("morph_code LIKE ?")
                    params.append(f"{value}%")
                else:
                    conditions.append(f"{field} = ?")
                    params.append(value)
        
        for field, value in self.morphology.items():
            if field == 'case':
                conditions.append("case_value = ?")
            else:
                conditions.append(f"{field} = ?")
            params.append(value)
        
        return " AND ".join(conditions) if conditions else "1=1", params
    
    def __repr__(self):
        if self.lemma:
            return f"SearchTerm(lemma={self.lemma}, morph={self.morphology})"
        return f"SearchTerm(token={self.special_token}, morph={self.morphology})"


class Query:
    """Represents a complete search query."""
    
    def __init__(self):
        self.terms: List[SearchTerm] = []
        self.proximity: Optional[int] = None  # For W# syntax
        self.whole_nt = False  # For * wildcard
        self.book_codes: List[str] = []  # For book filtering (e.g., ['01', '02'])
    
    def __repr__(self):
        return f"Query(terms={self.terms}, proximity={self.proximity}, whole_nt={self.whole_nt}, books={self.book_codes})"


def parse_query(query_string: str) -> Query:
    """
    Parse a query string into a Query object.
    
    Examples:
    - *λόγος@Nsg
    - *[article] & λόγος@Nsg W2
    - *εἰμί@VaAI3s
    - [Matt.] + [verb]@aAI3s
    - [Matt., Mk, Lk] + [verb]@aAI3s
    """
    query = Query()
    query_string = query_string.strip()
    
    # Check for book specification: [Book, Book] + query
    book_match = re.match(r'\[([^\]]+)\]\s*\+\s*(.+)', query_string)
    if book_match:
        # Extract book abbreviations
        book_str = book_match.group(1)
        book_abbrevs = [b.strip() for b in book_str.split(',')]
        
        # Map to book codes
        for abbrev in book_abbrevs:
            if abbrev in BOOK_ABBREVIATIONS:
                query.book_codes.append(BOOK_ABBREVIATIONS[abbrev])
        
        # Continue parsing the rest of the query
        query_string = book_match.group(2).strip()
    
    # Check for wildcard
    elif query_string.startswith('*'):
        query.whole_nt = True
        query_string = query_string[1:].strip()
    
    # Check for proximity at the end (W#)
    proximity_match = re.search(r'\s+W(\d+)\s*$', query_string, re.IGNORECASE)
    if proximity_match:
        query.proximity = int(proximity_match.group(1))
        query_string = query_string[:proximity_match.start()].strip()
    
    # Split by & to get multiple terms
    term_strings = [t.strip() for t in query_string.split('&')]
    
    for term_str in term_strings:
        if not term_str:
            continue
        
        # Check if it's a special token (with optional morphology codes)
        special_token_match = re.match(r'\[(\w+)\](?:@(.+))?', term_str)
        if special_token_match:
            token = f"[{special_token_match.group(1)}]"
            codes = special_token_match.group(2) if special_token_match.group(2) else ""
            query.terms.append(SearchTerm(special_token=token, morph_codes=codes))
            continue
        
        # Parse lemma@codes format
        if '@' in term_str:
            parts = term_str.split('@', 1)
            lemma = parts[0].strip()
            codes = parts[1].strip() if len(parts) > 1 else ""
            query.terms.append(SearchTerm(lemma=lemma, morph_codes=codes))
        else:
            # Just a lemma without codes
            lemma = term_str.strip()
            query.terms.append(SearchTerm(lemma=lemma))
    
    return query


def execute_query(conn: sqlite3.Connection, query: Query, corpora: List[str] = None) -> List[Dict[str, Any]]:
    """
    Execute a parsed query against the database.
    
    Args:
        conn: Database connection
        query: Parsed query object
        corpora: List of corpora to search (e.g., ['NT', 'LXX']). If None, searches all.
    
    Returns a list of results with verse context.
    """
    cursor = conn.cursor()
    
    if len(query.terms) == 0:
        return []
    
    # Default to all corpora if not specified
    if corpora is None:
        corpora = ['NT', 'LXX']
    
    # Single term search (no proximity needed)
    if len(query.terms) == 1:
        term = query.terms[0]
        conditions, params = term.to_sql_conditions()
        
        # Add book filtering if specified
        if query.book_codes:
            placeholders = ','.join('?' * len(query.book_codes))
            conditions += f" AND book_code IN ({placeholders})"
            params.extend(query.book_codes)
        
        # Add corpus filtering
        corpus_placeholders = ','.join('?' * len(corpora))
        conditions += f" AND corpus IN ({corpus_placeholders})"
        params.extend(corpora)
        
        sql = f"""
            SELECT DISTINCT 
                book_code, chapter, verse, word, lemma, morph_code, 
                pos, tense, voice, mood, case_value, number, gender, person
            FROM words 
            WHERE {conditions}
            ORDER BY book_code, chapter, verse, word_position
            LIMIT 500
        """
        
        cursor.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            results.append({
                'book_code': row[0],
                'chapter': row[1],
                'verse': row[2],
                'word': row[3],
                'lemma': row[4],
                'morph_code': row[5],
                'pos': row[6],
                'tense': row[7],
                'voice': row[8],
                'mood': row[9],
                'case': row[10],
                'number': row[11],
                'gender': row[12],
                'person': row[13],
            })
        
        return results
    
    # Multi-term search with proximity
    else:
        return execute_proximity_search(conn, query, corpora)


def execute_proximity_search(conn: sqlite3.Connection, query: Query, corpora: List[str] = None) -> List[Dict[str, Any]]:
    """
    Execute a multi-term search with optional proximity constraint.
    """
    cursor = conn.cursor()
    results = []
    
    # Default to all corpora if not specified
    if corpora is None:
        corpora = ['NT', 'LXX']
    
    # Build queries for each term
    term_queries = []
    for i, term in enumerate(query.terms):
        conditions, params = term.to_sql_conditions()
        term_queries.append((conditions, params))
    
    # If no proximity specified, they must be adjacent (next word)
    max_distance = query.proximity if query.proximity else 1
    
    # Get all matches for first term
    first_conditions, first_params = term_queries[0]
    
    # Add book filtering if specified
    if query.book_codes:
        placeholders = ','.join('?' * len(query.book_codes))
        first_conditions += f" AND book_code IN ({placeholders})"
        first_params.extend(query.book_codes)
    
    # Add corpus filtering
    corpus_placeholders = ','.join('?' * len(corpora))
    first_conditions += f" AND corpus IN ({corpus_placeholders})"
    first_params.extend(corpora)
    
    sql = f"""
        SELECT id, book_code, chapter, verse, word_position, 
               word, lemma, morph_code, pos, tense, voice, mood, 
               case_value, number, gender, person
        FROM words 
        WHERE {first_conditions}
        ORDER BY book_code, chapter, verse, word_position
    """
    
    cursor.execute(sql, first_params)
    first_matches = cursor.fetchall()
    
    # For each match of the first term, look for subsequent terms nearby
    for first_match in first_matches:
        first_id, book_code, chapter, verse, word_pos = first_match[:5]
        
        # Check if all subsequent terms exist within proximity
        all_found = True
        last_pos = word_pos
        matched_words = [first_match]
        
        for i in range(1, len(query.terms)):
            conditions, params = term_queries[i]
            
            # Look for this term within max_distance words
            search_sql = f"""
                SELECT id, book_code, chapter, verse, word_position,
                       word, lemma, morph_code, pos, tense, voice, mood,
                       case_value, number, gender, person
                FROM words
                WHERE book_code = ? AND chapter = ? AND verse = ?
                  AND word_position > ? AND word_position <= ?
                  AND {conditions}
                ORDER BY word_position
                LIMIT 1
            """
            
            search_params = [book_code, chapter, verse, last_pos, last_pos + max_distance] + params
            cursor.execute(search_sql, search_params)
            
            next_match = cursor.fetchone()
            if next_match:
                matched_words.append(next_match)
                last_pos = next_match[4]  # word_position
            else:
                all_found = False
                break
        
        # If all terms found, add to results
        if all_found:
            for match in matched_words:
                results.append({
                    'book_code': match[1],
                    'chapter': match[2],
                    'verse': match[3],
                    'word': match[5],
                    'lemma': match[6],
                    'morph_code': match[7],
                    'pos': match[8],
                    'tense': match[9],
                    'voice': match[10],
                    'mood': match[11],
                    'case': match[12],
                    'number': match[13],
                    'gender': match[14],
                    'person': match[15],
                })
    
    return results[:500]  # Limit results


def format_search_help() -> Dict[str, Any]:
    """Return help documentation for the search syntax."""
    return {
        'syntax': {
            'basic': '*λόγος@Nsg - Search entire NT (*) for λόγος as noun (N), singular (s), genitive (g)',
            'verb': '*εἰμί@VaAI3s - Search for εἰμί as verb (V), aorist (a), active (A), indicative (I), 3rd (3), singular (s)',
            'multi': '*[article] & λόγος@Nsg - Article followed by λόγος',
            'proximity': '*[article] & λόγος@Nsg W2 - Article within 2 words of λόγος',
            'book_single': '[Matt.] + [verb]@pAI3s - Search only in Matthew',
            'book_multi': '[Matt., Mk, Lk] + [verb]@pAI3s - Search in Matthew, Mark, and Luke',
        },
        'codes': {
            'pos': 'N=noun, V=verb, J=adjective, D=adverb, C=conjunction, P=preposition, R=pronoun, T=particle, I=interjection',
            'case': 'n=nominative, g=genitive, d=dative, a=accusative, v=vocative',
            'number': 's=singular, p=plural',
            'gender': 'm=masculine, f=feminine, u=neuter',
            'tense': 'p=present, i=imperfect, f=future, a=aorist, r=perfect, l=pluperfect',
            'voice': 'A=active, M=middle, P=passive',
            'mood': 'I=indicative, S=subjunctive, O=optative, M=imperative, N=infinitive, p=participle',
            'person': '1=1st, 2=2nd, 3=3rd',
        },
        'special_tokens': list(SPECIAL_TOKENS.keys()),
        'book_abbreviations': 'Matt, Mark, Mk, Luke, Lk, John, Jn, Acts, Rom, 1Cor, 2Cor, Gal, Eph, Phil, Col, 1Thess, 2Thess, 1Tim, 2Tim, Titus, Phlm, Heb, Jas, 1Pet, 2Pet, 1John, 2John, 3John, Jude, Rev',
    }
