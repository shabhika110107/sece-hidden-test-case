# Trigger Vercel deployment
import os
import sqlite3
from flask import Flask, jsonify, render_template, request

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/leetvault.db")
FLAG = os.environ.get("CTF_FLAG", "SECE{legacy_search_leaks_internal_notes}")

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        problem_count INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        starter_code TEXT NOT NULL,
        is_public INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS internal_notes (
        id INTEGER PRIMARY KEY,
        note_type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL,
        joined_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        verdict TEXT NOT NULL,
        runtime_ms INTEGER NOT NULL,
        submitted_at TEXT NOT NULL
    );
    """)

    count = conn.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    if count == 0:
        conn.executemany("""
            INSERT INTO problems (title, difficulty, category, description, starter_code, is_public)
            VALUES (?, ?, ?, ?, ?, 1)
        """, [
            ("Two Sum", "Easy", "Arrays", "Find two values that add up to a target.", "def two_sum(nums, target):\n    pass"),
            ("Valid Parentheses", "Easy", "Stack", "Determine whether brackets are balanced.", "def is_valid(s):\n    pass"),
            ("Merge Two Sorted Lists", "Easy", "Linked List", "Merge two sorted linked lists.", "def merge_lists(a, b):\n    pass"),
            ("Binary Search", "Easy", "Binary Search", "Find a target in a sorted array.", "def binary_search(nums, target):\n    pass"),
            ("Longest Substring Without Repeating Characters", "Medium", "Strings", "Find the longest substring with unique characters.", "def longest_unique(s):\n    pass"),
            ("Contains Duplicate", "Easy", "Hash Table", "Check whether an array contains duplicates.", "def contains_duplicate(nums):\n    pass"),
        ])
        conn.executemany("INSERT INTO categories(name, problem_count) VALUES (?, ?)", [
            ("Arrays", 1), ("Stack", 1), ("Linked List", 1),
            ("Binary Search", 1), ("Strings", 1), ("Hash Table", 1)
        ])
        conn.execute(
            "INSERT INTO internal_notes(note_type, content, created_at) VALUES (?, ?, ?)",
            ("verification", FLAG, "2026-10-11")
        )
        conn.execute(
            "INSERT INTO internal_notes(note_type, content, created_at) VALUES (?, ?, ?)",
            ("maintenance", "Legacy search service retained for compatibility testing.", "2026-10-11")
        )
        conn.execute(
            "INSERT INTO users(username, role, joined_at) VALUES (?, ?, ?)",
            ("vault_admin", "admin", "2024-05-01")
        )
    conn.commit()
    conn.close()

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/problems")
def problems_page():
    return render_template("problems.html")

@app.get("/challenge")
def challenge_page():
    return render_template("challenge.html")

@app.get("/login")
def login_page():
    return render_template("login.html")

@app.get("/api/problems")
def api_problems():
    search = request.args.get("search", "")

    # INTENTIONAL CTF VULNERABILITY:
    # Unsafe string interpolation lets a participant inject SQL via `search`.
    # Do not reuse this pattern in a real application.
    query = (
        "SELECT id, title, difficulty, category FROM problems "
        f"WHERE title LIKE '%{search}%' OR category LIKE '%{search}%' "
        "AND is_public = 1"
    )

    conn = get_db()
    try:
        rows = conn.execute(query).fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "title": row["title"],
                "difficulty": row["difficulty"],
                "category": row["category"],
            })
        return jsonify({"count": len(results), "query": search, "results": results})
    except sqlite3.Error:
        return jsonify({"error": "The legacy search service rejected that query."}), 400
    finally:
        conn.close()

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "legacy-search"})

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
else:
    init_db()
