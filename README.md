

# 🛒 Shopee Review Scraper

Program ini berfungsi untuk mengambil data **ulasan pada sebuah toko di Shopee** menggunakan API Shopee.  
Hasil data scrap akan disimpan dalam bentuk file **CSV** yang berisi informasi detail tentang ulasan produk.

---

## 📊 Hasil Output

File CSV yang dihasilkan akan memiliki kolom-kolom berikut:

- **Username** → Nama pemberi ulasan (ada yang mungkin disensor oleh Shopee)  
- **Rating** → Jumlah bintang yang diberikan pada produk  
- **Tanggal** → Waktu pemberian ulasan (format lokal Asia/Jakarta)  
- **Product Name** → Nama produk yang diberi ulasan  
- **Message** → Isi teks ulasan dari pembeli  

---

## ⚙️ Prerequisites

- **Shop ID** dari toko di Shopee yang ingin diambil datanya.  
- **Python 3.8+** sudah terinstal di mesin Anda.  

---

## 📦 Instalasi Modul

Pastikan modul berikut sudah terinstal:  

```bash
pip install requests pytz urllib3
````

---

## 🔧 Konfigurasi Program

Semua konfigurasi ada di dalam file utama `shopee_review_scraper.py`.
Ubah sesuai kebutuhan:

```python
SHOP_ID = 37146675                  # Ganti dengan ID toko Shopee
OUTPUT_FILE = 'logitech_shop_ratings.csv'  # Nama file output CSV
BATCH_SIZE = 100                    # Jumlah data per batch (maks 100)
RATE_LIMIT = 1.5                    # Delay antar request (detik)
TARGET_RECORDS = 50000              # Target jumlah ulasan yang ingin diambil
```

---

## ▶️ Cara Menjalankan

Jalankan perintah berikut di terminal:

```bash
python shopee_review_scraper.py
```

Program akan:

1. Mengecek jumlah data yang sudah ada di file CSV.
2. Jika jumlah record **belum mencapai `TARGET_RECORDS`**, program akan melanjutkan scraping.
3. Jika **`TARGET_RECORDS` tercapai**, program akan berhenti otomatis dengan pesan:

   ```
   Scraping completed successfully. Target reached. Stopping program.
   ```

Hasil scraping akan tersimpan di file CSV sesuai nama `OUTPUT_FILE`.

---

## ℹ️ Keterangan Tambahan

* **BATCH\_SIZE = 100** adalah nilai maksimal per request API Shopee (disarankan).
* Jangan set nilai lebih dari 100 untuk menghindari error.


---




