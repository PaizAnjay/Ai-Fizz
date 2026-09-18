# Panduan Deploy ke Vercel

## 1. Struktur folder yang dibutuhkan

```
esp32-ai-assistant-vercel/
├── api/
│   └── index.py        (sudah disiapkan)
├── bin/
│   └── ffmpeg           (BINARY, kamu download & taruh sendiri — lihat langkah 2)
├── requirements.txt      (sudah disiapkan)
└── vercel.json           (sudah disiapkan)
```

## 2. Download & siapkan ffmpeg statis

Vercel tidak punya ffmpeg bawaan, jadi kita sertakan sendiri binary-nya
(khusus Linux 64-bit, karena itu OS yang dipakai server Vercel).

Di komputer kamu (Windows/Mac/Linux, bebas — ini cuma untuk download & taruh file):

1. Buka: https://johnvansickle.com/ffmpeg/
2. Download **"linux-amd64" → release build (static)** — file `.tar.xz`.
3. Ekstrak file itu (pakai 7-Zip / WinRAR / archive manager apapun).
4. Di dalam hasil ekstrak, cari file bernama **`ffmpeg`** (tanpa embel-embel, ukurannya sekitar 70-80 MB).
5. Copy file `ffmpeg` itu ke folder `bin/` di project kamu (ganti file placeholder yang ada).

## 3. Set permission executable (penting!)

File `ffmpeg` itu harus punya izin "bisa dijalankan" saat di-upload ke GitHub.
Kalau kamu upload lewat browser GitHub biasa, izin ini **tidak otomatis kesimpan**.

Cara paling aman: pakai `git` dari terminal/command prompt di komputer kamu:

```bash
git add bin/ffmpeg
git update-index --chmod=+x bin/ffmpeg
git commit -m "Tambah ffmpeg binary"
git push
```

Kalau belum pernah pakai `git` dari terminal, install dulu Git for Windows/Mac,
lalu `git clone` repo kamu, taruh file ffmpeg-nya, baru jalankan perintah di atas.

## 4. Deploy ke Vercel

1. Buka **vercel.com** → daftar (bisa pakai GitHub, gratis, tanpa kartu untuk Hobby plan).
2. Klik **Add New → Project** → pilih repo `esp32-ai-assistant` (yang sudah ada folder `api/`, `bin/`, dst).
3. Di halaman konfigurasi, buka **Environment Variables** → tambahkan:
   - Key: `GROQ_API_KEY`
   - Value: API key Groq kamu
4. Klik **Deploy**.
5. Setelah selesai, kamu dapat URL seperti `https://esp32-ai-assistant.vercel.app`.

## 5. Update kode ESP32

Ganti `SERVER_URL` di `esp32_ai_assistant.ino` jadi:

```
https://esp32-ai-assistant.vercel.app/chat
```

## Catatan

- Kalau deploy gagal dengan error ukuran function terlalu besar, kemungkinan
  besar karena binary ffmpeg + library Python gabungan lewat batas 250MB.
  Kabari saya errornya, kita cari ffmpeg build yang lebih kecil (ada versi
  "essentials" yang lebih ringkas dari John Van Sickle).
- Kalau responsnya lambat/timeout, itu wajar di percobaan pertama (cold start),
  tapi kalau selalu timeout di atas 60 detik, kabari saya juga.
