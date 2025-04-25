import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
DB_NAME = "loan_data.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

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
                CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    tanggal_peminjaman TEXT,
                    tanggal_jatuh_tempo TEXT,
                    tanggal_pengembalian TEXT,
                    status TEXT DEFAULT 'dipinjam',
                    denda INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
        print(f"Provider Peminjaman: Database '{DB_NAME}' diinisialisasi.")
    except Exception as e:
        print(f"Provider Peminjaman: Gagal inisialisasi DB '{DB_NAME}' - {e}")
        raise

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
            member_resp = requests.get(f"http://localhost:5002/members/{loan_dict['member_id']}")
            book_resp = requests.get(f"http://localhost:5001/books/{loan_dict['book_id']}")
            member = member_resp.json() if member_resp.status_code == 200 else {'error': 'Anggota tidak ditemukan'}
            book = book_resp.json() if book_resp.status_code == 200 else {'error': 'Buku tidak ditemukan'}

            loan_list.append({
                'loan_id': loan_dict['id'],
                'member': member,
                'book': book,
                'tanggal_peminjaman': loan_dict['tanggal_peminjaman'],
                'tanggal_jatuh_tempo': loan_dict['tanggal_jatuh_tempo'],
                'tanggal_pengembalian': loan_dict['tanggal_pengembalian'],
                'status': loan_dict['status'],
                'denda': loan_dict['denda']
            })
        return jsonify(loan_list), 200
    except Exception as e:
        return jsonify({'error': f'Gagal mengambil data peminjaman - {e}'}), 500

@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    member_id = data.get('member_id')
    book_id = data.get('book_id')

    if not member_id or not book_id:
        return jsonify({"error": "member_id dan book_id diperlukan"}), 400

    member_resp = requests.get(f"http://localhost:5002/members/{member_id}")
    if member_resp.status_code != 200:
        return jsonify({"error": "Anggota tidak ditemukan"}), 404

    book_resp = requests.get(f"http://localhost:5001/books/{book_id}")
    if book_resp.status_code != 200:
        return jsonify({"error": "Buku tidak ditemukan"}), 404

    try:
        tanggal_peminjaman = datetime.today().strftime('%Y-%m-%d')
        tanggal_jatuh_tempo = (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d')

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO loans (member_id, book_id, tanggal_peminjaman, tanggal_jatuh_tempo)
                VALUES (?, ?, ?, ?)
            ''', (member_id, book_id, tanggal_peminjaman, tanggal_jatuh_tempo))
            conn.commit()

        return jsonify({'message': 'Peminjaman berhasil dibuat'}), 201
    except Exception as e:
        return jsonify({'error': f'Gagal membuat peminjaman - {e}'}), 500

# Endpoint: Pengembalian Buku
@app.route('/loans/<int:loan_id>/return', methods=['PATCH'])
def return_loan(loan_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tanggal_jatuh_tempo FROM loans WHERE id = ? AND status = 'dipinjam'", (loan_id,))
            row = cursor.fetchone()

            if not row:
                return jsonify({'error': 'Peminjaman tidak ditemukan atau sudah dikembalikan'}), 404

            jatuh_tempo = datetime.strptime(row[0], '%Y-%m-%d')
            hari_ini = datetime.today()
            selisih = (hari_ini - jatuh_tempo).days
            denda = 1000 * selisih if selisih > 0 else 0

            cursor.execute('''
                UPDATE loans
                SET tanggal_pengembalian = ?, status = 'dikembalikan', denda = ?
                WHERE id = ?
            ''', (hari_ini.strftime('%Y-%m-%d'), denda, loan_id))
            conn.commit()

        return jsonify({'message': 'Pengembalian berhasil', 'denda': denda}), 200
    except Exception as e:
        return jsonify({'error': f'Gagal melakukan pengembalian - {e}'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
