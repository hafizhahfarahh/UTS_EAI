from flask import Flask, request, jsonify
import sqlite3
import os
import contextlib
import requests

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
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                reviewer TEXT NOT NULL,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                comment TEXT
            )
        ''')
        conn.commit()
        print("ReviewService: Database diinisialisasi.")

#Fungsi untuk mengambil data buku dari book_service
def get_book_details(book_id):
    try:
        response = requests.get(f'http://localhost:5001/books/{book_id}')
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        app.logger.error(f"Gagal mengambil data buku: {e}")
    return {'id': book_id, 'title': 'Tidak ditemukan', 'author': 'Tidak diketahui'}

#Fungsi untuk validasi member dari member_service
def is_valid_member(member_id):
    try:
        response = requests.get(f'http://localhost:5002/members/{member_id}')
        if response.status_code == 200:
            member_data = response.json()
            return member_data.get('active', True)  # Pastikan member aktif
    except Exception as e:
        app.logger.error(f"Gagal validasi member {member_id}: {e}")
    return False

#Fungsi untuk cek apakah member sudah pernah meminjam buku
def has_borrowed_book(member_id, book_id):
    try:
        response = requests.get(f'http://localhost:5003/loans')
        if response.status_code == 200:
            loans = response.json()
            return any(loan['member']['id'] == member_id and loan['book']['id'] == book_id for loan in loans)
    except Exception as e:
        app.logger.error(f"Gagal cek riwayat pinjam member {member_id}: {e}")
    return False

#Endpoint: POST
@app.route('/reviews', methods=['POST'])
def create_review():
    if not request.is_json:
        return jsonify({'error': 'Request harus dalam format JSON'}), 400
    data = request.get_json()

    book_id = data.get('book_id')
    member_id = data.get('member_id')
    reviewer = data.get('reviewer')
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not all([book_id, member_id, reviewer, rating]):
        return jsonify({'error': 'book_id, member_id, reviewer, dan rating diperlukan'}), 400

    # Validasi member
    if not is_valid_member(member_id):
        return jsonify({'error': 'Member tidak valid atau tidak aktif'}), 403

    # Validasi apakah member sudah pernah meminjam buku
    if not has_borrowed_book(member_id, book_id):
        return jsonify({'error': 'Member belum pernah meminjam buku ini'}), 403

    # Ambil data buku
    book_data = get_book_details(book_id)

    # Simpan review ke database
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reviews (book_id, member_id, reviewer, rating, comment)
                VALUES (?, ?, ?, ?, ?)
            ''', (book_id, member_id, reviewer, rating, comment))
            conn.commit()
            review_id = cursor.lastrowid

        return jsonify({
            'review_id': review_id,
            'book': book_data,
            'reviewer': reviewer,
            'rating': rating,
            'comment': comment
        }), 201
    except Exception as e:
        app.logger.error(f"Gagal menyimpan review: {e}")
        return jsonify({'error': 'Kesalahan server'}), 500

#Endpoint: GET
@app.route('/reviews/book/<int:book_id>', methods=['GET'])
def get_reviews_by_book(book_id):
    try:
        # Ambil data buku
        book_data = get_book_details(book_id)

        # Ambil reviews dari database
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews WHERE book_id = ?", (book_id,))
            reviews = cursor.fetchall()

        return jsonify({
            'book': book_data,
            'reviews': [dict(r) for r in reviews]
        }), 200
    except Exception as e:
        app.logger.error(f"Gagal mengambil review: {e}")
        return jsonify({'error': 'Kesalahan server'}), 500

#Endpoint: PUT
@app.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment', '')

    if not rating:
        return jsonify({'error': 'rating diperlukan'}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reviews
                SET rating = ?, comment = ?
                WHERE id = ?
            ''', (rating, comment, review_id))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'error': 'Review tidak ditemukan'}), 404

        return jsonify({'message': 'Review berhasil diperbarui'}), 200
    except Exception as e:
        app.logger.error(f"Gagal mengupdate review: {e}")
        return jsonify({'error': 'Kesalahan server'}), 500

#Endpoint: DELETE
@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Review tidak ditemukan'}), 404
        return jsonify({'message': f'Review ID {review_id} berhasil dihapus'}), 200
    except Exception as e:
        app.logger.error(f"Gagal menghapus review: {e}")
        return jsonify({'error': 'Kesalahan server'}), 500

#Menjalankan Aplikasi
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5004, debug=True)
