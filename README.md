Dokumentasi komunikasi antar layanan:

---

# 📚 Dokumentasi Komunikasi Antar Layanan - Sistem Manajemen Perpustakaan

## Overview
Proyek ini terdiri dari **4 microservices** berbasis Flask:
- **Book Service** (`port 5001`) - Mengelola data buku.
- **Member Service** (`port 5002`) - Mengelola data anggota.
- **Loan Service** (`port 5003`) - Mengelola peminjaman dan pengembalian buku.
- **Review Service** (`port 5004`) - Mengelola ulasan buku.

Masing-masing layanan memiliki database SQLite lokal.

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
