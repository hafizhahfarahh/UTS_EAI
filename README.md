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
Dokumentasi API
Base URL : http://localhost:5003
    1.  GET /books/<int:book_id>/check_availability
    Deskripsi:
    Memeriksa apakah buku tertentu tersedia untuk dipinjam.

    Parameter:
    book_id (integer): ID buku yang ingin dicek.

    Response (200 OK):
    {
    "message": "Buku tersedia"
    }

    Status Code:
    - 400 Bad Request → jika buku tidak tersedia.
    - 500 Internal Server Error → jika terjadi kesalahan server.

    2. POST /loans
    Deskripsi:
    Membuat peminjaman baru oleh anggota.

    Header:

    Content-Type: application/json
    Body :
    {
     "member_id": 1,
     "book_id": 1
    }

    reponse : 201 Created
    {
     "message": "Peminjaman berhasil dibuat"
    }

    Status Code:
    - 400 Bad Request → jika member_id atau book_id tidak disertakan.
    - 404 Not Found → jika anggota atau buku tidak ditemukan.
    - 500 Internal Server Error → jika terjadi kesalahan server.

3. GET /loans
    Deskripsi:
    Mengambil seluruh data peminjaman beserta informasi anggota dan buku terkait.

    Response (200 OK):
    [
    {
    "loan_id": 1,
    "member": {
      "id": 1,
      "name": "Hafizhah"
    },
    "book": {
      "id": 1,
      "title": "Rentang Kisah",
      "author": "Gita Savitri Devi"
    },
    "tanggal_peminjaman": "2025-04-25",
    "tanggal_jatuh_tempo": "2025-05-02",
    "tanggal_pengembalian": null,
    "status": "dipinjam",
    "denda": 0
     }
    ]

    Status Code (200 OK)
    500 Internal Server Error

    4. PATCH /loans/<int:loan_id>/return
    Deskripsi:
    Mengembalikan buku yang dipinjam dan menghitung denda jika terlambat.

    Parameter:
    loan_id (integer): ID peminjaman.
    Response (200 OK):

    {
    "message": "Pengembalian berhasil",
    "denda": 1000
    }

    Status Code:
    - 404 Not Found → jika peminjaman tidak ditemukan atau sudah dikembalikan.
    - 500 Internal Server Error

    5. DELETE /loans/<int:loan_id>/cancel
    Deskripsi:
    Membatalkan peminjaman yang belum dikembalikan.

    Parameter:

    loan_id (integer)

    Response (200 OK):
    {
    "message": "Peminjaman berhasil dibatalkan"
    }

    Status Code:
    - 404 Not Found → jika tidak ditemukan atau sudah dikembalikan.
    - 500 Internal Server Error

    6. GET /loans/history/<int:member_id>
    Deskripsi:
    Mengambil riwayat peminjaman buku oleh anggota tertentu.

    Parameter:

    member_id (integer)

    Response (200 OK):

    [
  {
    "loan_id": 1,
    "book_id": 1,
    "tanggal_peminjaman": "2025-04-25",
    "tanggal_jatuh_tempo": "2025-05-02",
    "tanggal_pengembalian": null,
    "status": "dipinjam",
    "denda": 0
  }
]

Status Code (200 OK)
500 Internal Server Error

Dokumentasi Komunikasi Antar Layanan
Loan-Service sebagai Consumer
    - GET /books/<book_id> → dari Book-Service Untuk mengambil informasi buku seperti title, author, dan year.

    - GET /members/<member_id> → dari Member-Service Untuk validasi apakah member aktif dan valid.

Loan-Service sebagai Provider
Digunakan oleh front-end/dashboard:
    - POST /loans → membuat peminjaman baru.
    - GET /loans → menampilkan daftar peminjaman lengkap.
    - PATCH /loans/<loan_id>/return → mengembalikan buku.
    - DELETE /loans/<loan_id>/cancel → membatalkan peminjaman.
    - GET /loans/history/<member_id> → menampilkan riwayat peminjaman anggota.

Contoh Data Uji
Book-Service:
http://127.0.0.1:5001/books

[
  {
    "author": "Brian Khrisna",
    "id": 1,
    "title": "Seporsi Mie Ayam sebelum Mati",
    "year": 2024
  }
]

Member-Service:
http://127.0.0.1:5002/members/4

{
  "id": 4,
  "name": "Dhimas Faza"
}

Loan-Service:
http://127.0.0.1:5003/loans
[
  {
    "loan_id": 1,
    "member": {
      "id": 1,
      "name": "Hafizhah"
    },
    "book": {
      "id": 1,
      "title": "Seporsi Mie Ayam sebelum Mati",
      "author": "Brian Khrisna",
      "year": 2024
    },
    "tanggal_peminjaman": "2025-04-25",
    "tanggal_jatuh_tempo": "2025-05-02",
    "tanggal_pengembalian": "2025-04-25",
    "status": "dikembalikan",
    "denda": 0
  },
  {
    "loan_id": 3,
    "member": {
      "id": 1,
      "name": "Hafizhah"
    },
    "book": {
      "id": 1,
      "title": "Seporsi Mie Ayam sebelum Mati",
      "author": "Brian Khrisna",
      "year": 2024
    },
    "tanggal_peminjaman": "2025-04-25",
    "tanggal_jatuh_tempo": "2025-05-02",
    "tanggal_pengembalian": "2025-04-25",
    "status": "dikembalikan",
    "denda": 0
  }
]

Review-Service:
http://127.0.0.1:5004/reviews/book/1

{
  "book": {
    "author": "Brian Khrisna",
    "id": 1,
    "title": "Seporsi Mie Ayam sebelum Mati",
    "year": 2024
  },
  "reviews": [
    {
      "book_id": 1,
      "comment": "Buku ini sangat bagus!",
      "id": 1,
      "member_id": 1,
      "rating": 5,
      "reviewer": "Hafizhah"
    },
    {
      "book_id": 1,
      "comment": "Great service!",
      "id": 3,
      "member_id": 1,
      "rating": 5,
      "reviewer": "Dhimas Faza"
    },
    {
      "book_id": 1,
      "comment": "Bukunya Bagus!",
      "id": 4,
      "member_id": 1,
      "rating": 5,
      "reviewer": "Dhimas Faza"
    }
  ]
}



**Member_Service**


**Loan_Service**

*Dokumentasi API*

    Base URL: http://localhost:5003
    1. GET /books/<int:book_id>/check_availability
    Deskripsi: Memeriksa apakah buku tertentu tersedia untuk dipinjam.
    
    - Path Parameter: book_id (integer)
    - Response (200 OK):
    {
    "message": "Buku tersedia"
    }

    - Status Code:
        - 400 Bad Request jika buku tidak tersedia.
        - 500 Internal Server Error jika terjadi kegagalan di server.

    2. POST /loans
    Deskripsi: Membuat peminjaman baru oleh anggota.
    
    - Request Header: Content-Type: application/json
    - Request Body:
    {
    "member_id": 1,
    "book_id": 1
    }

    Response (201 Created):
    {
    "message": "Peminjaman berhasil dibuat"
    }

    - Status Code:
        - 400 Bad Request jika member_id atau book_id tidak disertakan.
        - 404 Not Found jika anggota atau buku tidak ditemukan.
        - 500 Internal Server Error jika terjadi kegagalan di server.

    3. GET /loans
    Deskripsi: Mengambil seluruh data peminjaman beserta informasi anggota dan buku terkait.
    
    - Response (200 OK):
    [
      {
        "loan_id": 1,
        "member": {
          "id": 1,
          "name": "Hafizhah"
        },
        "book": {
          "id": 1,
          "title": "Rentang Kisah",
          "author": "Gita Savitri Devi"
        },
        "tanggal_peminjaman": "2025-04-25",
        "tanggal_jatuh_tempo": "2025-05-02",
        "tanggal_pengembalian": null,
        "status": "dipinjam",
        "denda": 0
      }
    ]

    - Status Code:
        - 200 OK jika berhasil.
        - 500 Internal Server Error jika terjadi kegagalan di server.

    4. PATCH /loans/<int:loan_id>/return
    Deskripsi: Mengembalikan buku yang dipinjam dan menghitung denda jika terlambat.
    
    - Path Parameter: loan_id (integer)
    - Request Body: Tidak ada body request, hanya loan_id yang dibutuhkan di URL.
    - Response (200 OK):
    {
    "message": "Pengembalian berhasil",
      "denda": 1000
    }

    - Status Code:
        - 404 Not Found jika peminjaman tidak ditemukan atau sudah dikembalikan.
        - 500 Internal Server Error jika terjadi kegagalan di server.

    5. DELETE /loans/<int:loan_id>/cancel
    Deskripsi: Membatalkan peminjaman yang belum dikembalikan.
    
    - Path Parameter: loan_id (integer)
    - Response (200 OK):
    {
      "message": "Peminjaman berhasil dibatalkan"
    }
    
    - Status Code:
        - 404 Not Found jika peminjaman tidak ditemukan atau sudah dikembalikan.
        - 500 Internal Server Error jika terjadi kegagalan di server.

    6. GET /loans/history/<int:member_id>
    Deskripsi: Mengambil riwayat peminjaman buku oleh anggota tertentu.
    
    - Path Parameter: member_id (integer)
    - Response (200 OK):
    [
      {
        "loan_id": 1,
        "book_id": 1,
        "tanggal_peminjaman": "2025-04-25",
        "tanggal_jatuh_tempo": "2025-05-02",
        "tanggal_pengembalian": null,
        "status": "dipinjam",
        "denda": 0
      }
    ]

    - Status Code:
        -200 OK jika berhasil.
        - 500 Internal Server Error jika terjadi kegagalan di server.
        

*Dokumentasi Komunikasi Antar Layanan*

    - Loan-Service adalah consumer saat mengambil data dari Book-Service dan Member-Service. 
    Berikut interaksinya:
        - Book-Service: GET `/books/<book_id>` (mengambil title dan author buku)
        - Member-Service: GET `/members/<member_id>` (validasi member valid/aktif)
    
    - Loan-Service adalah provider bagi front-end/dashboard yang menampilkan atau mengelola data peminjaman, seperti:
        - POST `/loans` (membuat peminjaman baru)
        - GET `/loans` (menampilkan daftar peminjaman)
        - PATCH `/loans/<loan_id>/return` (mengembalikan buku)
        - DELETE `/loans/<loan_id>/cancel` (membatalkan peminjaman)
        

**Review_Service**

*Dokumentasi API*

    Base URL: http://localhost:5004

    1. POST /reviews
    Deskripsi: Membuat review baru oleh anggota yang pernah melakukan peminjaman untuk buku tertentu

    - Request Header: Content-Type: application/json
    - Request Body:
    {
    "book_id": 1,
    "member_id": 1,
    "reviewer": "Hafizhah",
    "rating": 4,
    "comment": "Buku ini sangat informatif dan mudah dipahami!"
    }

    - Response (201 Created): *contoh
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

    - Status Code:
        - 400 Bad Request jika payload tidak lengkap atau tidak JSON
        - 403 Forbidden jika member tidak aktif atau belum pernah meminjam buku
        - 500 Internal Server Error jika terjadi kegagalan di server

    2. GET /reviews/book/<book_id>
    Deskripsi: Mengambil seluruh review untuk buku tertentu, beserta informasi buku

    - Path Parameter: book_id (integer)
    - Response (200 OK): *contoh
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

    - Status Code:
        - 200 OK jika berhasil
        - 500 Internal Server Error jika terjadi kegagalan di server

    3. PUT /reviews/<book_id>
    Deskripsi: Memperbarui rating dan/atau komentar pada review tertentu

    - Path Parameter: book_id (integer)
    - Request Header: application/json
    - Request Body:
    {
    "rating": 5,
    "comment": "Setelah dibaca, saya semakin suka buku ini!"
    }

    - Response (200 OK):
    {
    "message": "Review berhasil diperbarui"
    }

    - Status Code:
        - 400 Bad Request jika rating tidak disertakan
        - 404 Not Found jika review_id tidak ditemukan
        - 500 Internal Server Error jika terjadi kegagalan di server

    4. DELETE /reviews/<review_id>
    Deskripsi: Menghapus review berdasarkan ID

    - Path Parameter: book_id (integer)
    - Response (200 OK): *contoh
    {
    "message": "Review ID 1 berhasil dihapus"
    }

    - Status Code:
        - 404 Not Found jika review_id tidak ditemukan
        - 500 Internal Server Error jika terjadi kegagalan di server


*Dokumentasi Komunikasi Antar Layanan*

    - Review-Service adalah consumer saat mengambil data dari Book_Service, Member_Service, dan Loan_Service. Berikut interaksinya:
        - Book_Service: GET /books/<book_id> (mengambil title dan author buku)
        - Member_Service: GET /members/<member_id> (validasi member valid/aktif)
        - Loan_Service: GET /loans (memeriksa apakah member/anggota pernah meminjam buku tersebut)
        
    - Review_Service adalah provider bagi front-end/dashboard yang menampilkan atau mengelola review (jika ada)
        **-** Front-end: /reviews, /reviews/book, PUT, DELETE (menyediakan data review untuk UI atau Dashboard)

