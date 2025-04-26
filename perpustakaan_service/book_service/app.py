import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
CORS(app)
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

# --- Konsumer Endpoints ---

# Endpoint: GET /books/<int:book_id>/reviews
@app.route('/books/<int:book_id>/reviews', methods=['GET'])
def get_book_reviews(book_id):
    try:
        # Periksa apakah buku ada
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, year FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
            
        if not book:
            return jsonify({'error': 'Buku tidak ditemukan'}), 404
            
        # Ambil ulasan dari review_service
        try:
            response = requests.get(f'http://localhost:5004/reviews/book/{book_id}')
            
            if response.status_code == 200:
                reviews_data = response.json()
                
                # Gabungkan data buku dengan ulasan
                result = {
                    'book': dict(book),
                    'reviews': reviews_data.get('reviews', [])
                }
                
                return jsonify(result), 200
            else:
                return jsonify({
                    'book': dict(book),
                    'reviews': [],
                    'error': 'Gagal mengambil data ulasan'
                }), 200
                
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error connecting to review_service: {e}")
            return jsonify({
                'book': dict(book),
                'reviews': [],
                'error': 'Gagal terhubung ke layanan ulasan'
            }), 200
            
    except Exception as e:
        app.logger.error(f"Error retrieving book reviews: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: GET /books/<int:book_id>/loan_status
@app.route('/books/<int:book_id>/loan_status', methods=['GET'])
def get_book_loan_status(book_id):
    try:
        # Periksa apakah buku ada
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, author, year FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
            
        if not book:
            return jsonify({'error': 'Buku tidak ditemukan'}), 404
            
        # Periksa status ketersediaan buku dari loan_service
        try:
            response = requests.get(f'http://localhost:5003/books/{book_id}/check_availability')
            
            book_data = dict(book)
            
            if response.status_code == 200:
                # Buku tersedia
                book_data['status'] = 'tersedia'
                book_data['message'] = 'Buku tersedia untuk dipinjam'
            else:
                # Buku tidak tersedia (sedang dipinjam)
                book_data['status'] = 'dipinjam'
                book_data['message'] = 'Buku sedang dipinjam'
                
            return jsonify(book_data), 200
                
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error connecting to loan_service: {e}")
            book_data['status'] = 'unknown'
            book_data['message'] = 'Gagal memeriksa status buku'
            return jsonify(book_data), 200
            
    except Exception as e:
        app.logger.error(f"Error checking book loan status: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
