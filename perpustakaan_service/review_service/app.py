from flask import Flask, request, jsonify
import sqlite3
import os
import contextlib
import requests

# Inisialisasi Flask
app = Flask(__name__)
DB_NAME = "review_data.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# Utilitas koneksi DB
@contextlib.contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Membuat tabel review jika belum ada"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    reviewer TEXT NOT NULL,
                    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                    comment TEXT
                )
            ''')
            conn.commit()
        print(f"ReviewService: Database '{DB_NAME}' diinisialisasi.")
    except Exception as e:
        print(f"ReviewService: Gagal inisialisasi DB '{DB_NAME}' - {e}")
        raise

# Endpoint untuk membuat review
@app.route('/reviews', methods=['POST'])
def create_review():
    if not request.is_json:
        return jsonify({'error': 'Request harus JSON'}), 400
    data = request.get_json()
    book_id = data.get('book_id')
    reviewer = data.get('reviewer')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not book_id or not reviewer or not rating:
        return jsonify({'error': 'book_id, reviewer, dan rating diperlukan'}), 400

    try:
        # Simpan review ke database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reviews (book_id, reviewer, rating, comment)
                VALUES (?, ?, ?, ?)
            ''', (book_id, reviewer, rating, comment))
            conn.commit()
            review_id = cursor.lastrowid

        # Ambil data buku dari book_service
        book_response = requests.get(f'http://localhost:5001/books/{book_id}')
        if book_response.status_code == 200:
            book_data = book_response.json()
        else:
            book_data = {'id': book_id, 'title': 'Tidak ditemukan', 'author': 'Tidak diketahui'}

        return jsonify({
            'review_id': review_id,
            'book': book_data,
            'reviewer': reviewer,
            'rating': rating,
            'comment': comment
        }), 201
    except Exception as e:
        app.logger.error(f"Gagal membuat review: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500


# Endpoint untuk melihat semua review berdasarkan book_id
@app.route('/reviews/book/<int:book_id>', methods=['GET'])
def get_reviews_by_book(book_id):
    try:
        # Ambil data buku terlebih dahulu
        book_response = requests.get(f'http://localhost:5001/books/{book_id}')
        if book_response.status_code == 200:
            book_data = book_response.json()
        else:
            book_data = {'id': book_id, 'title': 'Tidak ditemukan', 'author': 'Tidak diketahui'}

        # Ambil reviews dari database
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews WHERE book_id = ?", (book_id,))
            reviews = cursor.fetchall()
        
        # Format respons yang konsisten dengan POST
        response = {
            'book': book_data,
            'reviews': [dict(r) for r in reviews]
        }
        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"Gagal mengambil review buku {book_id}: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Review tidak ditemukan'}), 404
        return jsonify({'message': f'Review dengan ID {review_id} berhasil dihapus'}), 200
    except Exception as e:
        app.logger.error(f"Error deleting review {review_id}: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500


# Menjalankan layanan
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5004, debug=True)
