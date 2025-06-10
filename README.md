# 🤖 Chatbot Assistant dengan Konteks Dokumen
Selamat datang di Chatbot Assistant! Aplikasi web interaktif ini dibangun menggunakan Streamlit dan didukung oleh model AI canggih dari OpenRouter. Chatbot ini tidak hanya mampu menjawab pertanyaan umum, tetapi juga dapat membaca dan memahami konten dari berbagai jenis dokumen yang Anda unggah, menjadikannya asisten yang sangat berguna untuk membahas, menganalisis, atau meringkas informasi dari file Anda.

## ✨ Fitur Utama
- Antarmuka Percakapan Streaming: Respons dari chatbot ditampilkan kata per kata, memberikan pengalaman interaksi yang dinamis dan alami.
- Dukungan Multi-Dokumen: Unggah dan diskusikan konten dari berbagai format file, termasuk:
  - Teks (.txt, .md)
  - PDF (.pdf)
  - Microsoft Word (.docx)
  - Microsoft PowerPoint (.pptx)
  - Microsoft Excel (.xlsx, .xls)
- Jawaban Kontekstual: Bot secara otomatis menggunakan konten dari dokumen yang diunggah sebagai basis pengetahuan untuk menjawab pertanyaan Anda yang relevan.
- Manajemen Sesi: Anda dapat dengan mudah memulai percakapan baru kapan saja, yang akan menghapus riwayat obrolan dan konteks file sebelumnya.
- Integrasi OpenRouter: Memanfaatkan kekuatan berbagai model bahasa besar (LLM) yang tersedia melalui platform OpenRouter.

## ⚙️ Cara Kerja
Aplikasi ini dirancang dengan alur kerja yang sederhana namun kuat:

1. Inisialisasi: Saat aplikasi dimulai, ia akan memeriksa kunci API OpenRouter yang tersimpan di Streamlit Secrets untuk menginisialisasi klien OpenAI.
2. Unggah File (Opsional): Pengguna dapat mengunggah dokumen melalui sidebar.
3. Ekstraksi Teks: Bergantung pada ekstensi file, aplikasi menggunakan library Python yang sesuai (seperti PyPDF2 untuk PDF atau pandas untuk Excel) untuk mengekstrak konten teks dari file tersebut.
4. Manajemen Konteks: Teks yang diekstrak disimpan dalam status sesi (st.session_state).
5. Interaksi dengan AI:
  - Saat pengguna mengirimkan pesan, aplikasi akan mengambil seluruh riwayat percakapan.
  - Jika ada konten file yang tersimpan, konten tersebut akan ditambahkan di awal payload sebagai "pesan sistem". Ini memberikan konteks penuh kepada model AI tentang dokumen yang sedang dibahas.
  - Permintaan lengkap dikirim ke model AI (misalnya, Deepseek R1) melalui OpenRouter.
6. Tampilan Respons: Respons dari model AI diterima dalam bentuk stream dan ditampilkan secara real-time di antarmuka obrolan.

## 🚀 Instalasi dan Cara Menjalankan
Untuk menjalankan aplikasi ini di lingkungan lokal Anda, ikuti langkah-langkah berikut:
### 1. Prasyarat
- Pastikan Anda memiliki Python 3.8+ terinstal di sistem Anda.
- Anda memerlukan kunci API OpenRouter. Anda bisa mendapatkannya secara gratis di situs web OpenRouter.
### 2. Unduh atau Clone Proyek
Unduh semua file proyek (app.py, dll.) atau clone repositori jika tersedia.
### 3. Buat File requirements.txt
Buat sebuah file bernama requirements.txt di direktori yang sama dengan app.py dan tambahkan library berikut di dalamnya:
- streamlit
- openai
- pypdf2
- python-docx
- python-pptx
- pandas
- openpyxl
### 4. Instal Ketergantungan
- Buka terminal atau command prompt, navigasi ke direktori proyek Anda, dan jalankan perintah berikut untuk menginstal semua library yang dibutuhkan:
pip install -r requirements.txt
### 5. Konfigurasi Kunci API
Aplikasi ini dirancang untuk mengambil kunci API dari Streamlit Secrets. Buat sebuah folder bernama .streamlit di dalam direktori proyek Anda, dan di dalamnya, buat file bernama secrets.toml.
Isi file secrets.toml dengan format berikut:
# .streamlit/secrets.toml
OPENROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
Ganti sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx dengan kunci API OpenRouter Anda yang sebenarnya.
### 6. Jalankan Aplikasi
Setelah semuanya siap, jalankan aplikasi menggunakan perintah berikut di terminal Anda:
streamlit run app.py
Aplikasi akan otomatis terbuka di browser default Anda!

🛠️ Teknologi yang Digunakan
Framework: Streamlit

Model AI: Deepseek R1 (via OpenRouter API)

Library Python:

openai: Untuk berinteraksi dengan API OpenRouter.

pypdf2, python-docx, python-pptx, pandas: Untuk mengekstrak teks dari berbagai format dokumen.

Dibuat oleh Mohammad Aris Darmawan
