Dokumentasi Komunikasi Antar Layanan:

---

# 📚 Dokumentasi Komunikasi Antar Layanan - Sistem Manajemen Perpustakaan

Perpustakaan_System adalah sebuah sistem terintegrasi berbasis arsitektur microservices yang dirancang untuk mengelola berbagai aktivitas utama dalam sebuah sistem perpustakaan digital, seperti pengelolaan buku, anggota, peminjaman buku, dan ulasan buku.

Sistem ini dikembangkan dengan prinsip service-to-service communication menggunakan REST API dengan format JSON, sehingga masing-masing layanan dapat berjalan secara independen namun tetap saling berinteraksi.

## Teknologi yang Digunakan
- Bahasa Pemrograman: Python versi 3.11.x
- Framework Backend: Flask versi 3.1.0 (Flask-RESTful)
- Database: SQLite (menggunakan SQLite3, embedded database di Python)
- HTTP Client: requests versi 2.31.0 (untuk komunikasi antar layanan)
- Environment Manager: Virtual Environment (venv) Python
- API Testing & Interaksi: Command Line (CMD) menggunakan curl untuk request API
- Format Data: JSON (JavaScript Object Notation)


## Overview
Proyek ini terdiri dari **4 microservices** berbasis Flask:
- **Book Service** (`port 5001`) - Mengelola data buku.
- **Member Service** (`port 5002`) - Mengelola data anggota.
- **Loan Service** (`port 5003`) - Mengelola peminjaman dan pengembalian buku.
- **Review Service** (`port 5004`) - Mengelola ulasan buku.

Masing-masing layanan memiliki database SQLite lokal.
- **Book Service**: book_data.db
- **Member Service**: book_data.db
- **Loan Service**: book_data.db
- **Review Service**: book_data.db

## Struktur Folder
perpustakaan_system/
├── book_service/
│   ├── app.py
│   ├── book_data.db
│   └── requirements.txt
│
├── member_service/
│   ├── app.py
│   ├── member_data.db
│   └── requirements.txt
│
├── loan_service/
│   ├── app.py
│   ├── loan_data.db
│   └── requirements.txt
│
├── review_service/
│   ├── app.py
│   ├── review_data.db
│   └── requirements.txt
│
└── README.md

---

## Komunikasi Antar Layanan

Berikut adalah daftar interaksi antar service:

| Source Service | Target Service | Endpoint | Tujuan |
|:---------------|:---------------|:---------|:-------|
| Loan Service | Member Service | `GET /members/<member_id>` | Memvalidasi keberadaan anggota sebelum membuat peminjaman |
| Loan Service | Book Service | `GET /books/<book_id>` | Memvalidasi keberadaan buku sebelum membuat peminjaman |
| Book Service | Loan Service | `GET /books/<book_id>/check_availability` | Mengecek apakah buku tersedia untuk dipinjam |
| Book Service | Review Service | `GET /reviews/book/<book_id>` | Mengambil daftar ulasan untuk buku tertentu |
| Member Service | Loan Service | `GET /loans/history/<member_id>` | Mengambil riwayat peminjaman anggota |
| Member Service | Book Service | `GET /books/<book_id>` | Mengambil informasi buku saat menampilkan riwayat peminjaman |
| Review Service | Book Service | `GET /books/<book_id>` | Menampilkan informasi buku saat membuat review |
| Review Service | Member Service | `GET /members/<member_id>` | Validasi anggota saat membuat review |
| Review Service | Loan Service | `GET /loans` | Memastikan anggota pernah meminjam buku sebelum membuat review |

---

## Detail Implementasi Request antar Layanan

### 1. Loan Service → Member Service
**Validasi anggota saat membuat peminjaman:**
```python
member_resp = requests.get(f"http://localhost:5002/members/{member_id}")
```

### 2. Loan Service → Book Service
**Validasi buku saat membuat peminjaman:**
```python
book_resp = requests.get(f"http://localhost:5001/books/{book_id}")
```

### 3. Book Service → Loan Service
**Cek status ketersediaan buku:**
```python
response = requests.get(f"http://localhost:5003/books/{book_id}/check_availability")
```

### 4. Book Service → Review Service
**Mengambil ulasan buku:**
```python
response = requests.get(f"http://localhost:5004/reviews/book/{book_id}")
```

### 5. Member Service → Loan Service
**Mengambil riwayat peminjaman anggota:**
```python
response = requests.get(f"http://localhost:5003/loans/history/{member_id}")
```

### 6. Member Service → Book Service
**Ambil info buku di riwayat peminjaman anggota:**
```python
response = requests.get(f"http://localhost:5001/books/{book_id}")
```

### 7. Review Service → Book Service
**Ambil info buku saat membuat review:**
```python
response = requests.get(f"http://localhost:5001/books/{book_id}")
```

### 8. Review Service → Member Service
**Validasi member saat membuat review:**
```python
response = requests.get(f"http://localhost:5002/members/{member_id}")
```

### 9. Review Service → Loan Service
**Cek apakah member sudah meminjam buku sebelum membuat review:**
```python
response = requests.get(f"http://localhost:5003/loans")
```

---

Book_Service sebagai Provider
Book_Service menyediakan data buku yang dapat diakses oleh layanan lain maupun front-end:

- GET /books: Memberikan daftar semua buku ke front-end atau service lain.
- GET /books/{book_id}: Memberikan detail sebuah buku berdasarkan ID ke front-end atau service lain.
- GET /books/{book_id}/reviews: Menyediakan data buku beserta ulasan dari Review_Service (menggabungkan data lokal + data dari review_service).
- GET /books/{book_id}/loan_status: Menyediakan data buku beserta status ketersediaannya dari Loan_Service (menggabungkan data lokal + data dari loan_service).

Book_Service sebagai Consumer
Book_Service membutuhkan data dari layanan lain untuk melengkapi informasi buku:

Review_Service
- GET http://localhost:5004/reviews/book/{book_id}: Mengambil semua ulasan terkait buku tertentu dari review_service untuk ditampilkan pada endpoint /books/{book_id}/reviews.

Loan_Service
- GET http://localhost:5003/books/{book_id}/check_availability: Mengambil informasi ketersediaan buku dari loan_service untuk ditampilkan pada endpoint /books/{book_id}/loan_status.

Member Service sebagai Provider:
Menyediakan data anggota untuk layanan lain melalui endpoint:
- GET /members/<member_id>:  Digunakan oleh Loan Service untuk validasi member_id sebelum membuat peminjaman.)

Member Service sebagai Consumer:
- Mengambil riwayat peminjaman dari:
        - Loan Service: GET /loans/history/<member_id>  (Untuk mendapatkan daftar peminjaman anggota tertentu.)
- Mengambil informasi buku dari:
        - Book Service: GET /books/<book_id>  (Untuk melengkapi data peminjaman dengan informasi detail buku (judul, penulis, dll).)


Loan-Service adalah consumer saat mengambil data dari Book-Service dan Member-Service. 
Berikut interaksinya:
- Book-Service: GET `/books/<book_id>` (mengambil title dan author buku)
- Member-Service: GET `/members/<member_id>` (validasi member valid/aktif)
    
Loan-Service adalah provider bagi front-end/dashboard yang menampilkan atau mengelola data peminjaman, seperti:
- POST `/loans` (membuat peminjaman baru)
- GET `/loans` (menampilkan daftar peminjaman)
- PATCH `/loans/<loan_id>/return` (mengembalikan buku)
- DELETE `/loans/<loan_id>/cancel` (membatalkan peminjaman)


Review-Service adalah consumer saat mengambil data dari Book_Service, Member_Service, dan Loan_Service.
Berikut interaksinya:
- Book_Service: GET /books/<book_id> (mengambil detail buku yaitu title dan author buku saat membuat atau menampilkam review)
- Member_Service: GET /members/<member_id> (validasi member valid/aktif)
- Loan_Service: GET /loans (memastikan bahwa member sudah pernah meminjam buku tersebut sebelum diperbolehkan membuat review)
        
Review_Service menyediakan API yang bisa digunakan oleh layanan lain atau pengguna eksternal.
  Berikut interaksinya
- Book_Service: GET /reviews/book/<book_id> (menyediakan daftar review untuk buku tertentu)
- Member_Service: GET /reviews/member/<member_id> (menyediakan daftar review yang dibuat oleh seorang member)
- Frontend: POST /reviews (membuat daftar review yang dibuat oleh seorang member)
- Frontend: PUT /reviews/<review_id> (memperbarui atau mengedit isi review)
- Frontend: DELETE /reviews/<review_id> (menghapus review tertentu)

---
## Catatan Tambahan
- Semua komunikasi menggunakan protokol HTTP lokal (`localhost`).
- Semua request antar service bersifat **synchronous** (menggunakan `requests` Python).
- Tidak ada message queue atau event-driven architecture.
- Port:
  - Book Service: `5001`
  - Member Service: `5002`
  - Loan Service: `5003`
  - Review Service: `5004`
- Jika salah satu service mati, fitur yang tergantung pada service tersebut akan mengembalikan error JSON.
