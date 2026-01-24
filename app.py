"""
Flask web application for Greek New Testament Bible Study.
Provides linguistic syntax querying capabilities.
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from typing import List, Dict, Any
import os
from query_parser import parse_query, execute_query, format_search_help
from relative_search import parse_verse_reference, get_verse_words, search_by_lemmas, get_verse_context

app = Flask(__name__)
DATABASE = "greek_nt.db"


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def format_reference(book_code: str, chapter: int, verse: int) -> str:
    """Format a verse reference."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT book_abbrev FROM books WHERE book_code = ?", (book_code,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return f"{result['book_abbrev']} {chapter}:{verse}"
    return f"{book_code} {chapter}:{verse}"


def get_verse_text(book_code: str, chapter: int, verse: int) -> str:
    """Get the full Greek text of a verse."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT word FROM words
        WHERE book_code = ? AND chapter = ? AND verse = ?
        ORDER BY word_position
    """, (book_code, chapter, verse))
    
    words = [row["word"] for row in cursor.fetchall()]
    conn.close()
    return " ".join(words)


@app.route("/")
def index():
    """Main page."""
    return render_template("index.html")


@app.route("/api/books")
def get_books():
    """Get list of all books."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT book_code, book_name, book_abbrev FROM books ORDER BY book_code")
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(books)


@app.route("/api/search", methods=["POST"])
def search():
    """
    Search the Greek NT based on linguistic criteria.
    Accepts JSON with search parameters.
    """
    data = request.json
    
    # Build query dynamically based on provided criteria
    query = "SELECT DISTINCT book_code, chapter, verse, word, lemma, morph_code, pos, tense, voice, mood, case_value, number, gender FROM words WHERE 1=1"
    params = []
    
    # Text search (word or lemma)
    if data.get("text"):
        query += " AND (word LIKE ? OR lemma LIKE ?)"
        search_term = f"%{data['text']}%"
        params.extend([search_term, search_term])
    
    # Lemma search (exact)
    if data.get("lemma"):
        query += " AND lemma = ?"
        params.append(data["lemma"])
    
    # Part of speech
    if data.get("pos"):
        query += " AND pos = ?"
        params.append(data["pos"])
    
    # Tense
    if data.get("tense"):
        query += " AND tense = ?"
        params.append(data["tense"])
    
    # Voice
    if data.get("voice"):
        query += " AND voice = ?"
        params.append(data["voice"])
    
    # Mood
    if data.get("mood"):
        query += " AND mood = ?"
        params.append(data["mood"])
    
    # Case
    if data.get("case"):
        query += " AND case_value = ?"
        params.append(data["case"])
    
    # Number
    if data.get("number"):
        query += " AND number = ?"
        params.append(data["number"])
    
    # Gender
    if data.get("gender"):
        query += " AND gender = ?"
        params.append(data["gender"])
    
    # Person
    if data.get("person"):
        query += " AND person = ?"
        params.append(data["person"])
    
    # Book filter
    if data.get("book"):
        query += " AND book_code = ?"
        params.append(data["book"])
    
    # Add ordering and limit
    query += " ORDER BY book_code, chapter, verse LIMIT 500"
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    results = []
    seen_verses = set()
    
    for row in cursor.fetchall():
        verse_key = (row["book_code"], row["chapter"], row["verse"])
        
        result = {
            "reference": format_reference(row["book_code"], row["chapter"], row["verse"]),
            "book_code": row["book_code"],
            "chapter": row["chapter"],
            "verse": row["verse"],
            "word": row["word"],
            "lemma": row["lemma"],
            "morph_code": row["morph_code"],
            "pos": row["pos"],
            "tense": row["tense"],
            "voice": row["voice"],
            "mood": row["mood"],
            "case": row["case_value"],
            "number": row["number"],
            "gender": row["gender"],
        }
        
        # Add full verse text if we haven't seen this verse yet
        if verse_key not in seen_verses:
            result["verse_text"] = get_verse_text(row["book_code"], row["chapter"], row["verse"])
            seen_verses.add(verse_key)
        
        results.append(result)
    
    conn.close()
    
    return jsonify({
        "results": results,
        "count": len(results),
        "limited": len(results) >= 500
    })


@app.route("/api/stats")
def get_stats():
    """Get database statistics."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM words")
    total_words = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(DISTINCT lemma) as count FROM words")
    unique_lemmas = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM books")
    total_books = cursor.fetchone()["count"]
    
    conn.close()
    
    return jsonify({
        "total_words": total_words,
        "unique_lemmas": unique_lemmas,
        "total_books": total_books
    })


@app.route("/api/morphology/options")
def get_morphology_options():
    """Get available morphological options for dropdowns."""
    conn = get_db()
    cursor = conn.cursor()
    
    options = {}
    
    # Get unique values for each morphological category
    categories = ["pos", "tense", "voice", "mood", "case_value", "number", "gender", "person"]
    
    for category in categories:
        cursor.execute(f"SELECT DISTINCT {category} FROM words WHERE {category} IS NOT NULL ORDER BY {category}")
        options[category.replace("_value", "")] = [row[category] for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify(options)


@app.route("/api/advanced-search", methods=["POST"])
def advanced_search():
    """
    Advanced search using custom query syntax.
    
    Examples:
    - *λόγος@Nsg
    - *[article] & λόγος@Nsg W2
    - *εἰμί@VaAI3s
    """
    data = request.json
    query_string = data.get("query", "").strip()
    corpora = data.get("corpora", ["NT"])  # Default to NT if not specified
    
    if not query_string:
        return jsonify({"results": [], "count": 0, "error": "No query provided"})
    
    if not corpora or len(corpora) == 0:
        return jsonify({"results": [], "count": 0, "error": "No corpus selected"})
    
    try:
        # Parse the query
        query = parse_query(query_string)
        
        # Check if it's a relative search
        if query.is_relative_search:
            # Handle relative search
            return handle_relative_search(query.relative_verse_ref, corpora, data.get("lemmas"))
        
        # Execute the query with corpus filtering
        conn = get_db()
        results = execute_query(conn, query, corpora)
        
        # Add verse references and full verse text
        formatted_results = []
        seen_verses = set()
        
        for result in results:
            verse_key = (result["book_code"], result["chapter"], result["verse"])
            
            # Add reference
            result["reference"] = format_reference(
                result["book_code"], 
                result["chapter"], 
                result["verse"]
            )
            
            # Add full verse text if we haven't seen this verse yet
            if verse_key not in seen_verses:
                result["verse_text"] = get_verse_text(
                    result["book_code"],
                    result["chapter"],
                    result["verse"]
                )
                seen_verses.add(verse_key)
            
            formatted_results.append(result)
        
        conn.close()
        
        return jsonify({
            "results": formatted_results,
            "count": len(formatted_results),
            "limited": len(formatted_results) >= 500,
            "query": str(query)
        })
        
    except Exception as e:
        return jsonify({
            "results": [],
            "count": 0,
            "error": str(e)
        }), 400


def handle_relative_search(verse_reference, corpora, provided_lemmas=None):
    """
    Handle a relative search request.
    Extracted as a separate function so it can be called from both
    advanced search and the dedicated relative search endpoint.
    """
    try:
        # Parse the verse reference
        book_code, chapter, verse = parse_verse_reference(verse_reference)
        
        # Get connection
        conn = get_db()
        
        # If lemmas are provided, use them (for re-search)
        # Otherwise, get all words from the source verse
        if provided_lemmas:
            lemmas = provided_lemmas
        else:
            lemmas = get_verse_words(conn, book_code, chapter, verse)
        
        if not lemmas:
            return jsonify({
                "error": "No words found in source verse",
                "source_verse": verse_reference,
                "is_relative_search": True
            }), 404
        
        # Get the source verse text
        source_corpus = conn.execute(
            "SELECT corpus FROM words WHERE book_code = ? AND chapter = ? AND verse = ? LIMIT 1",
            (book_code, chapter, verse)
        ).fetchone()
        
        if not source_corpus:
            return jsonify({
                "error": f"Verse not found: {verse_reference}",
                "is_relative_search": True
            }), 404
        
        source_corpus = source_corpus[0]
        source_text = get_verse_context(conn, book_code, chapter, verse, source_corpus)
        
        # Get book name
        book_name = conn.execute(
            "SELECT book_name FROM books WHERE book_code = ? AND corpus = ?",
            (book_code, source_corpus)
        ).fetchone()[0]
        
        # Search for similar verses
        results = search_by_lemmas(
            conn,
            lemmas,
            book_code,
            chapter,
            verse,
            corpora
        )
        
        # Format results with references
        for result in results:
            result["reference"] = f"{result['book_name']} {result['chapter']}:{result['verse']}"
        
        conn.close()
        
        # Return results with source verse info and flag
        return jsonify({
            "is_relative_search": True,
            "source_verse": {
                "reference": f"{book_name} {chapter}:{verse}",
                "text": source_text,
                "book_code": book_code,
                "chapter": chapter,
                "verse": verse,
                "corpus": source_corpus,
                "words": lemmas  # Include all words for checkbox UI
            },
            "results": results[:100],  # Limit to top 100 results
            "count": len(results[:100]),
            "total_matches": len(results),
            "limited": len(results) > 100
        })
        
    except ValueError as e:
        return jsonify({"error": str(e), "is_relative_search": True}), 400
    except Exception as e:
        return jsonify({"error": f"Search error: {str(e)}", "is_relative_search": True}), 500


@app.route("/api/relative-search", methods=["POST"])
def relative_search():
    """
    Search for verses with similar vocabulary to a given source verse.
    Expects JSON: {
        "verse_reference": "Rom. 8:1",
        "corpora": ["NT", "LXX"],
        "lemmas": [{"lemma": "λόγος", "pos": "noun", "weight": 3}, ...]  // optional for re-search
    }
    """
    data = request.json
    verse_reference = data.get("verse_reference", "").strip()
    corpora = data.get("corpora", ["NT"])
    provided_lemmas = data.get("lemmas")  # For re-search with selected words
    
    if not verse_reference:
        return jsonify({"error": "No verse reference provided"}), 400
    
    try:
        # Parse the verse reference
        book_code, chapter, verse = parse_verse_reference(verse_reference)
        
        # Get connection
        conn = get_db()
        
        # If lemmas are provided, use them (for re-search)
        # Otherwise, get all words from the source verse
        if provided_lemmas:
            lemmas = provided_lemmas
        else:
            lemmas = get_verse_words(conn, book_code, chapter, verse)
        
        if not lemmas:
            return jsonify({
                "error": "No words found in source verse",
                "source_verse": verse_reference
            }), 404
        
        # Get the source verse text
        source_corpus = conn.execute(
            "SELECT corpus FROM words WHERE book_code = ? AND chapter = ? AND verse = ? LIMIT 1",
            (book_code, chapter, verse)
        ).fetchone()
        
        if not source_corpus:
            return jsonify({
                "error": f"Verse not found: {verse_reference}"
            }), 404
        
        source_corpus = source_corpus[0]
        source_text = get_verse_context(conn, book_code, chapter, verse, source_corpus)
        
        # Get book name
        book_name = conn.execute(
            "SELECT book_name FROM books WHERE book_code = ? AND corpus = ?",
            (book_code, source_corpus)
        ).fetchone()[0]
        
        # Search for similar verses
        results = search_by_lemmas(
            conn,
            lemmas,
            book_code,
            chapter,
            verse,
            corpora
        )
        
        # Format results with references
        for result in results:
            result["reference"] = f"{result['book_name']} {result['chapter']}:{result['verse']}"
        
        conn.close()
        
        # Return results with source verse info
        return jsonify({
            "source_verse": {
                "reference": f"{book_name} {chapter}:{verse}",
                "text": source_text,
                "book_code": book_code,
                "chapter": chapter,
                "verse": verse,
                "corpus": source_corpus,
                "words": lemmas  # Include all words for checkbox UI
            },
            "results": results[:100],  # Limit to top 100 results
            "total_matches": len(results),
            "limited": len(results) > 100
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Search error: {str(e)}"}), 500


@app.route("/api/search-help")
def search_help():
    """Get help documentation for advanced search syntax."""
    return jsonify(format_search_help())


if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        print("Error: Database not found. Please run 'python setup_database.py' first.")
        exit(1)
    
    print("=" * 60)
    print("Greek New Testament Bible Study App")
    print("=" * 60)
    print("Server starting at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host="0.0.0.0", port=5000)
