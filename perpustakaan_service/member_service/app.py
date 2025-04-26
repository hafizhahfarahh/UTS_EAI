import sqlite3
import os
import contextlib
from flask import Flask, request, jsonify
import requests  
from flask_cors import CORS

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)
CORS(app)
DB_NAME = "member_data.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

# --- Utilitas Database ---
@contextlib.contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone_number TEXT
                )
            ''')
            conn.commit()
        print(f"Provider Anggota: Database '{DB_NAME}' diinisialisasi.")
    except Exception as e:
        print(f"Provider Anggota: Gagal inisialisasi DB '{DB_NAME}' - {e}")
        raise

# --- Helper function untuk format data member ---
def serialize_member(member):
    return {
        'id': member['id'],
        'name': member['name'],
        'phone_number': member['phone_number']
    }

# --- API Endpoints ---

# Endpoint: POST /members
@app.route('/members', methods=['POST'])
def create_member():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    name = data.get('name')
    phone_number = data.get('phone_number')

    if not name:
        return jsonify({"error": "Nama diperlukan"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO members (name, phone_number) VALUES (?, ?)",
                (name, phone_number)
            )
            conn.commit()
            member_id = cursor.lastrowid
        return jsonify(serialize_member({
            'id': member_id,
            'name': name,
            'phone_number': phone_number
        })), 201
    except Exception as e:
        app.logger.error(f"Error creating member: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: GET /members/<int:member_id>
@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
            member = cursor.fetchone()
        if member:
            return jsonify(serialize_member(member)), 200
        else:
            return jsonify({'error': 'Anggota tidak ditemukan'}), 404
    except Exception as e:
        app.logger.error(f"Error fetching member {member_id}: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: GET /members
@app.route('/members', methods=['GET'])
def get_all_members():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members")
            members = cursor.fetchall()
        return jsonify([serialize_member(member) for member in members]), 200
    except Exception as e:
        app.logger.error(f"Error fetching members: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: PUT /members/<int:member_id>
@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    name = data.get('name')
    phone_number = data.get('phone_number')

    if not name:
        return jsonify({"error": "Nama diperlukan"}), 400

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE members SET name = ?, phone_number = ? WHERE id = ?",
                (name, phone_number, member_id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Anggota tidak ditemukan'}), 404
        return jsonify({'message': 'Anggota berhasil diperbarui'}), 200
    except Exception as e:
        app.logger.error(f"Error updating member {member_id}: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: DELETE /members/<int:member_id>
@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Anggota tidak ditemukan'}), 404
        return jsonify({'message': 'Anggota berhasil dihapus'}), 200
    except Exception as e:
        app.logger.error(f"Error deleting member {member_id}: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500


# Endpoint: GET /members/<int:member_id>/loans
@app.route('/members/<int:member_id>/loans', methods=['GET'])
def get_member_loan_history(member_id):
    try:
        # Periksa apakah anggota ada
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
            member = cursor.fetchone()
            
        if not member:
            return jsonify({'error': 'Anggota tidak ditemukan'}), 404
            
        # Ambil riwayat peminjaman dari loan_service
        try:
            response = requests.get(f'http://localhost:5003/loans/history/{member_id}')
            
            if response.status_code == 200:
                loans = response.json()
                
                # Data informasi buku
                enriched_loans = []
                for loan in loans:
                    book_id = loan.get('book_id')
                    book_response = requests.get(f'http://localhost:5001/books/{book_id}')
                    
                    if book_response.status_code == 200:
                        book_info = book_response.json()
                        loan['book_info'] = book_info
                    else:
                        loan['book_info'] = {'error': 'Informasi buku tidak ditemukan'}
                        
                    enriched_loans.append(loan)
                
                # Gabungkan data anggota dengan riwayat peminjaman
                result = {
                    'member': serialize_member(member),
                    'loan_history': enriched_loans
                }
                
                return jsonify(result), 200
            else:
                return jsonify({'error': 'Gagal mengambil data peminjaman', 'detail': response.text}), response.status_code
                
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error connecting to loan_service: {e}")
            return jsonify({'error': 'Gagal terhubung ke layanan peminjaman'}), 503
            
    except Exception as e:
        app.logger.error(f"Error retrieving loan history: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# Endpoint: GET /members/<int:member_id>/summary
@app.route('/members/<int:member_id>/summary', methods=['GET'])
def get_member_summary(member_id):
    try:
        # Ambil data anggota
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
            member = cursor.fetchone()
            
        if not member:
            return jsonify({'error': 'Anggota tidak ditemukan'}), 404
        
        member_data = serialize_member(member)
        
        # Ambil riwayat peminjaman
        try:
            loan_response = requests.get(f'http://localhost:5003/loans/history/{member_id}')
            if loan_response.status_code != 200:
                loan_history = {'error': 'Gagal mengambil riwayat peminjaman'}
            else:
                loan_history = loan_response.json()
                
            # Hitung statistik peminjaman
            total_loans = len(loan_history)
            active_loans = sum(1 for loan in loan_history if loan.get('status') == 'dipinjam')
            returned_loans = sum(1 for loan in loan_history if loan.get('status') == 'dikembalikan')
            total_fines = sum(loan.get('denda', 0) for loan in loan_history)
            
            # Susun data ringkasan
            summary = {
                'member': member_data,
                'loan_stats': {
                    'total_loans': total_loans,
                    'active_loans': active_loans,
                    'returned_loans': returned_loans,
                    'total_fines': total_fines
                },
                'loan_history': loan_history
            }
            
            return jsonify(summary), 200
            
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error connecting to loan_service: {e}")
            return jsonify({
                'member': member_data,
                'loan_history': {'error': 'Gagal terhubung ke layanan peminjaman'}
            }), 200
            
    except Exception as e:
        app.logger.error(f"Error generating member summary: {e}")
        return jsonify({'error': 'Kesalahan server internal'}), 500

# --- Menjalankan Aplikasi ---
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)