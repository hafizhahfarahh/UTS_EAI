import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
DB_NAME = "member_data.db"
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
    """Inisialisasi database anggota (member_data.db) jika belum ada."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            conn.commit()
        print(f"Provider Anggota: Database '{DB_NAME}' diinisialisasi.")
    except Exception as e:
        print(f"Provider Anggota: Gagal inisialisasi DB '{DB_NAME}' - {e}")
        raise

# --- API Endpoints ---

# Endpoint: POST /members
@app.route('/members', methods=['POST'])
def create_member():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Nama diperlukan"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO members (name) VALUES (?)", (name,))
            conn.commit()
            member_id = cursor.lastrowid
        return jsonify({'id': member_id, 'name': name}), 201
    except Exception as e:
        app.logger.error(f"Error creating member: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: GET /members/<int:member_id>
@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM members WHERE id = ?", (member_id,))
            member = cursor.fetchone()
        if member:
            return jsonify(dict(member)), 200
        else:
            return jsonify({'error': 'Anggota tidak ditemukan'}), 404
    except Exception as e:
        app.logger.error(f"Error fetching member {member_id}: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
