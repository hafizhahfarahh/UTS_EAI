Dokumentasi API Perpustakaan_Service

**Deskripsi Umum**
Perpustakaan_Service adalah sebuah layanan terintegrasi berbasis arsitektur microservices yang dirancang untuk mengelola berbagai aktivitas dalam sebuah sistem perpustakaan digital. Sistem ini dibangun menggunakan Flask-RESTful dan database SQLite, serta terdiri dari beberapa layanan terpisah yang saling berkomunikasi melalui REST API menggunakan format JSON.

**Struktur Layanan**
Sistem ini terdiri dari 4 layanan utama, yaitu:
1. **Book_Service**, yaitu untuk mengelola data buku.
2. **Member_Service**, yaitu untuk mengelola data anggota perpustakaan.
3. **Loan_Service**, yaitu untuk mengelola aktivitas peminjaman buku oleh angggota.
4. **Review_Service**, yaitu untuk mengelola ulasan atau review yang diberikan oleh anggota terhadap buku yang telah dipinjam.

**Book_Service**


**Member_Service**


**Loan_Service**


**Review_Service**

*Dokumentasi API*

    Base URL: http://localhost:5004

    1. POST /reviews
    Deskripsi: Membuat review baru oleh anggota yang pernah melakukan peminjaman untuk buku tertentu

    **-** Request Header: Content-Type: application/json
    **-** Request Body:
    {
    "book_id": 1,
    "member_id": 1,
    "reviewer": "Hafizhah",
    "rating": 4,
    "comment": "Buku ini sangat informatif dan mudah dipahami!"
    }
    **-** Response (201 Created): *contoh
    {
    "review_id": 1,
    "book": {
        "id": 1,
        "title": "Rentang Kisah",
        "author": "Gita Savitri Devi"
    },
    "reviewer": "Hafizhah",
    "rating": 5,
    "comment": "Buku ini sangat bagus!"
    }
    **-** Status Code:
        - 400 Bad Request jika payload tidak lengkap atau tidak JSON
        - 403 Forbidden jika member tidak aktif atau belum pernah meminjam buku
        - 500 Internal Server Error jika terjadi kegagalan di server

    2. GET /reviews/book/<book_id>
    Deskripsi: Mengambil seluruh review untuk buku tertentu, beserta informasi buku

    **-** Path Parameter: book_id (integer)
    **-** Response (200 OK): *contoh
    {
    "book": {
        "id": 1,
        "title": "Rentang Kisah",
        "author": "Gita Savitri Devi"
    },
    "reviews": [
        {
        "id": 1,
        "book_id": 1,
        "member_id": 1,
        "reviewer": "Hafizhah",
        "rating": 4,
        "comment": "Buku ini sangat bagus!"
        }
    ]
    }
    **-** Status Code:
        - 200 OK jika berhasil
        - 500 Internal Server Error jika terjadi kegagalan di server

    3. PUT /reviews/<book_id>
    Deskripsi: Memperbarui rating dan/atau komentar pada review tertentu

    **-** Path Parameter: book_id (integer)
    **-** Request Header: application/json
    **-** Request Body:
    {
    "rating": 5,
    "comment": "Setelah dibaca, saya semakin suka buku ini!"
    }
    **-** Response (200 OK):
    {
    "message": "Review berhasil diperbarui"
    }
    **-** Status Code:
        - 400 Bad Request jika rating tidak disertakan
        - 404 Not Found jika review_id tidak ditemukan
        - 500 Internal Server Error jika terjadi kegagalan di server

    4. DELETE /reviews/<review_id>
    Deskripsi: Menghapus review berdasarkan ID

    **-** Path Parameter: book_id (integer)
    **-** Response (200 OK): *contoh
    {
    "message": "Review ID 1 berhasil dihapus"
    }
    **-** Status Code:
        - 404 Not Found jika review_id tidak ditemukan
        - 500 Internal Server Error jika terjadi kegagalan di server


*Dokumentasi Komunikasi Antar Layanan*

    **-** Review-Service adalah consumer saat mengambil data dari Book_Service, Member_Service, dan Loan_Service. Berikut interaksinya:
        **-** Book_Service: GET /books/<book_id> (mengambil title dan author buku)
        **-** Member_Service: GET /members/<member_id> (validasi member valid/aktif)
        **-** Loan_Service: GET /loans (memeriksa apakah member/anggota pernah meminjam buku tersebut)
    **-** Review_Service adalah provider bagi front-end/dashboard yang menampilkan atau mengelola review (jika ada)
        **-** Front-end: /reviews, /reviews/book, PUT, DELETE (menyediakan data review untuk UI atau Dashboard)

