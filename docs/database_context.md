# 📌 Comprehensive Project Context: DataLeap ERP v5 Migration
> **Database Engine:** MariaDB v11.5.2 (Win64)  
> **Source Document:** `dataleap_v5_finish.sql`  
> **Default Configuration:** Charset `utf8mb4`, Collate `utf8mb4_unicode_ci`  

# 📊 DATA ARCHITECTURE & BI DASHBOARD BLUEPRINT

## PART 1: Deskripsi Detail & Kamus Data Tabel Utama

Berdasarkan berkas *database migration* (`dataleap_v5_finish.sql`) yang dianalisis, sistem ini dirancang untuk mendukung operasional lembaga pendidikan/kursus (seperti LEAP English & Digital Class). Cakupan datanya meliputi manajemen akademik, absensi internal, manajemen prospek siswa, hingga log operasional harian hibrida (*online/offline*).

Berikut adalah penjelasan fungsi detail dari setiap entitas/tabel utama:

### 1. Modul Pengguna & Struktur Organisasi
* **`users`**: Menyimpan data akun pengguna utama sistem (karyawan, guru, admin).
* **`divisions`**: Daftar divisi kerja di dalam perusahaan (misal: Akademik, FO, HR, IT, Marketing).
* **`division_user`**: Tabel *junction* yang menghubungkan `users` dengan `divisions` dan peran (`id_role`) tertentu.

### 2. Modul Core Academic (Kursus & Penjadwalan)
* **`kursus`**: Menyimpan master data program studi/kursus yang ditawarkan (contoh: *Coding Class*, *English Program*).
* **`kursus_level` & `rapor_level_config`**: Menyimpan tingkatan dari tiap kursus (misal: *Gogo 1, Step Out, Winner, Basic*) serta format penilaian rapornya.
* **`jadwal`**: Master data kelas/rombongan belajar yang aktif, mengikat program kursus, level, periode, dan sesi standar.
* **`jadwal_hari`**: Menyimpan informasi hari pelaksanaan dari suatu jadwal kelas (misal: Senin & Rabu).
* **`jadwal_detail`**: Berisi detail *instance* pertemuan harian dari sebuah kelas, menyimpan tautan kelas online (Zoom link), status pengerjaan, dan *operational data*.

### 3. Modul Kesiswaan (Siswa Aktif & Rekrutmen Calon Siswa)
* **`calon_siswa`**: Basis data prospek/pendaftar baru, merekam data demografi lengkap (provinsi, kabupaten, kecamatan, kelurahan), asal sekolah, dan status kelengkapan berkas.
* **`calon_siswa_akademik`**: Menghubungkan calon siswa dengan kursus, periode, dan level yang mereka minati/pilih saat mendaftar.
* **`calon_siswa_bayar`**: Catatan transaksi pembayaran biaya pendaftaran atau cicilan awal calon siswa.
* **`calon_siswa_ortu` & `calon_siswa_fo_detail`**: Menyimpan data latar belakang orang tua (pekerjaan, penghasilan) serta catatan tindak lanjut oleh tim *Front Office* (FO).

### 4. Modul Operasional Kelas & Penilaian (*Classroom Log*)
* **`catatan_kelas`**: Berisi log jurnal harian yang diisi oleh guru/instruktur setelah selesai mengajar (topik diskusi, catatan kemajuan siswa).
* **`catatan_siswa` & `catatan_remidi_siswa`**: Catatan khusus perkembangan performa per individu siswa di kelas tertentu serta penanganan program remedial.

### 5. Modul HR & Manajemen Kehadiran Karyawan
* **`absensi`**: Tabel penampung data presensi harian karyawan (jam masuk, jam keluar, tipe absensi seperti *Fingerprint*, catatan kerja WFH/WFO, dan status keterlambatan).
* **`izin_karyawan` & `verifikasi_izin`**: Pengajuan dispensasi/izin kerja karyawan beserta alur persetujuan (*approval*) dari kepala divisi terkait.

---

## PART 2: Analisis Koneksi & Relasi Antar Tabel (*Entity Relationship*)

Berikut adalah alur data logis dan ketergantungan *foreign key* utama di dalam sistem:

*   **Relasi Akademik (`jadwal` ──> `jadwal_detail`)**: Satu baris di tabel `jadwal` (*One-to-Many*) melahirkan banyak baris di `jadwal_detail`. Setiap kelas yang dibuat akan dipecah menjadi puluhan sesi pertemuan sesuai kalender akademik di `jadwal_detail`.
*   **Relasi Pelaporan Guru (`jadwal_detail` ──> `catatan_kelas` ──> `users`)**: Setiap *instance* pertemuan (`id_jadwal_detail`) mereferensikan satu baris `catatan_kelas`. Di sini terjadi pengecekan produktivitas guru: baris ini mencatat akun guru (`id_karyawan`/`users`) yang bertugas beserta ulasan teks performa kelas.
*   **Relasi Corong Penjualan (*Sales Funnel*) Calon Siswa (`calon_siswa` ──> `akademik` ──> `bayar`)**: Data induk pendaftar di `calon_siswa` terikat dengan pilihan programnya di `calon_siswa_akademik`. Dari entitas akademik tersebut, sistem mencatat riwayat transaksi di `calon_siswa_bayar` untuk memantau konversi piutang menjadi pendapatan perusahaan.
*   **Relasi Kontrol HR (`users` ──> `absensi` <── `izin_karyawan`)**: Setiap record di tabel `absensi` wajib merujuk ke pengguna aktif di `users` (`id_karyawan`). Jika status absensi dinyatakan "Izin", maka kolom `id_izin` akan terisi secara opsional, menghubungkannya langsung dengan tabel persetujuan `izin_karyawan`.

---

## PART 3: Analisis Data untuk Kebutuhan Dashboard (BI Insight)

Untuk mengintegrasikan database ini ke alat visualisasi data seperti Looker Studio atau Tableau, data mentah di atas harus dikelompokkan ke dalam 4 sudut pandang matriks analisis utama (*Dimension & Metrics*):

### 1. Dashboard Rekrutmen & Pemasaran (*Marketing & Front Office Dashboard*)
*   **Tingkat Konversi Prospek (*Conversion Rate*):** Persentase perubahan status dari pendaftar baru (`calon_siswa`) menjadi siswa bayar (`calon_siswa_bayar`).
*   **Analisis Saluran Akuisisi (*Marketing Source Channels*):** Mengetahui dari mana calon siswa mengetahui lembaga ini (berdasarkan kolom referensi seperti *Instagram, Website, Tiktok, Teman*).
*   **Segmentasi Geografis & Sosio-Ekonomi:** Memetakan konsentrasi domisili pendaftar terbanyak (analisis `id_kabupaten`/`id_kecamatan`) serta profil pekerjaan dan rentang pendapatan orang tua untuk penentuan strategi promosi.

### 2. Dashboard Produktivitas & Akademik (*Academic & Teaching Dashboard*)
*   **Utilisasi Kelas & Kelas Populer:** Menghitung jumlah kelas aktif per kategori program kursus (`id_kursus`) dan level (`id_level`) untuk melihat tren minat pasar.
*   **Rasio Kepatuhan Mengajar (*Teacher Compliance Rate*):** Membandingkan jumlah total sesi terjadwal (`jadwal_detail`) dengan jumlah sesi yang sukses terlaksana dan memiliki `catatan_kelas`. Jika `catatan_kelas` kosong, berarti guru belum mengisi laporan pasca-mengajar.
*   **Analisis Sentimen Jurnal Kelas:** Ekstraksi kata kunci atau pengelompokan dari teks `catatan_kelas` (misal: mendeteksi nama siswa yang sering disebut membutuhkan perhatian khusus seperti *"slow learner"* atau *"remedial"*).

### 3. Dashboard Manajemen SDM (*HR & Attendance Executive Dashboard*)
*   **Rasio Keterlambatan Kerja (*Late Attendance Ratio*):** Menghitung persentase kemunculan status 'Terlambat' pada tabel `absensi` per divisi atau per individu karyawan.
*   **Analisis Jam Kerja Efektif:** Selisih antara `jam_keluar` dan `jam_masuk` untuk mengukur durasi kerja lembur atau kekurangan jam kerja reguler.
*   **Tren Pengajuan Izin Semusim:** Pola frekuensi ketidakhadiran kerja karyawan berdasarkan waktu persetujuan di tabel `izin_karyawan` untuk mengoptimalkan manajemen kapasitas staf saat musim liburan.

### 4. Dashboard Keuangan Calon Siswa (*Revenue Sales Pipeline Dashboard*)
*   **Total Pendapatan Kotor Kursus Baru:** Agregasi kuantitatif dari nilai nominal uang yang masuk di tabel `calon_siswa_bayar`.
*   **Kecepatan Siklus Penjualan (*Sales Velocity*):** Durasi rata-rata waktu yang dibutuhkan dari pembuatan akun pendaftar (`calon_siswa.created_at`) hingga transaksi pembayaran pertama berhasil diverifikasi.
