import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify
import requests

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
DB_NAME = "loan_data.db"
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
    """Inisialisasi database peminjaman (loan_data.db) jika belum ada."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL
                )
            ''')
            conn.commit()
        print(f"Provider Peminjaman: Database '{DB_NAME}' diinisialisasi.")
    except Exception as e:
        print(f"Provider Peminjaman: Gagal inisialisasi DB '{DB_NAME}' - {e}")
        raise

# --- API Endpoints ---

# Endpoint: GET /loans
@app.route('/loans', methods=['GET'])
def get_loans():
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM loans")
            loans = cursor.fetchall()

        loan_list = []
        for loan in loans:
            loan_dict = dict(loan)
            # Ambil data member dan book dari service lain
            member_resp = requests.get(f"http://localhost:5002/members/{loan_dict['member_id']}")
            book_resp = requests.get(f"http://localhost:5001/books/{loan_dict['book_id']}")
            member = member_resp.json() if member_resp.status_code == 200 else {'error': 'Anggota tidak ditemukan'}
            book = book_resp.json() if book_resp.status_code == 200 else {'error': 'Buku tidak ditemukan'}

            loan_list.append({
                'loan_id': loan_dict['id'],
                'member': member,
                'book': book
            })
        return jsonify(loan_list), 200
    except Exception as e:
        return jsonify({'error': f'Gagal mengambil data peminjaman - {e}'}), 500

# Endpoint: POST /loans
@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    member_id = data.get('member_id')
    book_id = data.get('book_id')

    if not member_id or not book_id:
        return jsonify({"error": "member_id dan book_id diperlukan"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO loans (member_id, book_id) VALUES (?, ?)", (member_id, book_id))
            conn.commit()
        return jsonify({'message': 'Peminjaman berhasil dibuat'}), 201
    except Exception as e:
        return jsonify({'error': f'Gagal membuat peminjaman - {e}'}), 500

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
