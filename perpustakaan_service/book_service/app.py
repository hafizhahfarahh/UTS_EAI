import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
DB_NAME = "book_data.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# --- Utilitas Database ---
@contextlib.contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Inisialisasi database buku (book_data.db) jika belum ada."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    year INTEGER
                )
            ''')
            conn.commit()
        print(f"Provider Buku: Database '{DB_NAME}' diinisialisasi.")
    except Exception as e:
        print(f"Provider Buku: Gagal inisialisasi DB '{DB_NAME}' - {e}")
        raise

# --- API Endpoints ---

# Endpoint: POST /books
@app.route('/books', methods=['POST'])
def create_book():
    if not request.is_json:
        app.logger.error("Request is not JSON")
        return jsonify({"error": "Request harus berupa JSON"}), 400
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')

    if not title or not author or year is None:
        app.logger.error(f"Missing data - title: {title}, author: {author}, year: {year}")
        return jsonify({"error": "Judul, penulis, dan tahun terbit diperlukan"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year))
            conn.commit()
            book_id = cursor.lastrowid
        app.logger.info(f"Book created with ID {book_id}")
        return jsonify({'id': book_id, 'title': title, 'author': author, 'year': year}), 201
    except Exception as e:
        app.logger.error(f"Error creating book: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500
    
# Endpoint: GET /books
@app.route('/books', methods=['GET'])
def get_all_books():
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, year FROM books")
            books = [dict(row) for row in cursor.fetchall()]
        return jsonify(books), 200
    except Exception as e:
        app.logger.error(f"Error fetching books: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: GET /books/<int:book_id>
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, year FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
        if book:
            return jsonify(dict(book)), 200
        else:
            return jsonify({'error': 'Buku tidak ditemukan'}), 404
    except Exception as e:
        app.logger.error(f"Error fetching book {book_id}: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
