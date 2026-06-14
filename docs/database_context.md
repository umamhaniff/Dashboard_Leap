# 📌 Comprehensive Project Context: DataLeap ERP v5 Migration
> **Database Engine:** MariaDB v11.5.2 (Win64)  
> **Source Document:** `dataleap_v5_migration.sql`  
> **Default Configuration:** Charset `utf8mb4`, Collate `utf8mb4_unicode_ci`  

---

## 🗺️ 1. Complete Domain & Entity Blueprint
Seluruh tabel dalam skema ini dipetakan ke dalam 6 sub-sistem utama yang saling berelasi:

[Core User/RBAC] <---> [HR & Staff Management]
^                         ^
|                         |
v                         v
[CRM/Leads Pipeline] ---> [Academic & Schedule Engine] <---> [Sarpras / Regional Master]
|
v
[Business Development]


---

## 🗂️ 2. Detailed Data Dictionary (All Tables Included)

### 🔑 A. Sub-Sistem Autentikasi & RBAC (Role-Based Access Control)
Menangani otentikasi akun, pemetaan divisi kerja internal, dan pembatasan hak akses menu sistem.

#### 1. `users`
* **Deskripsi**: Tabel akun pengguna utama untuk staf internal maupun pihak terkait.
* **Karakteristik Skema**:
    * `id_user`: `varchar(15)` (PK)
    * `username`, `email`: `varchar(255)` (Unique)
    * `password`: `varchar(255)`
    * `status_aktif`: `tinyint(1)` (Default: 1)

#### 2. `roles`
* **Deskripsi**: Daftar tingkatan hak akses (misal: Superadmin, Admin, Staff, Evaluator).
* **Karakteristik Skema**:
    * `id`: `bigint(20) unsigned` (PK)
    * `name`, `guard_name`: `varchar(255)`

#### 3. `divisions`
* **Deskripsi**: Master data divisi internal perusahaan (misal: Front Office, Akademik, BusDev, HR).
* **Karakteristik Skema**:
    * `id_division`: `bigint(20) unsigned` (PK)
    * `name_division`: `varchar(100)`
    * `is_active`: `tinyint(1)` (Default: 1)

#### 4. `division_user`
* **Deskripsi**: Tabel jembatan (*Many-to-Many*) yang mengikat satu user ke divisi dan role tertentu.
* **Karakteristik Skema**:
    * Hubungan Relasi: `id_division_user` (FK ke `users.id_user`), `id_division` (FK ke `divisions`), dan `id_role` (FK ke `roles.id`).
    * Aturan Hapus: `ON DELETE CASCADE` untuk seluruh *foreign key*.

---

### 🎯 B. Sub-Sistem CRM, Leads, & Pipeline Calon Siswa
Modul FO (Front Office) untuk menyaring ketertarikan calon pelanggan dari kontak awal hingga konversi pembayaran.

#### 5. `kontak_prospek`
* **Deskripsi**: Data mentah leads awal (*cold/warm leads*) yang masuk melalui media promosi.
* **Karakteristik Skema**:
    * `id_kontak_prospek`: `bigint(20) unsigned` (PK)
    * `kode_kontak`: `varchar(50)` (Unique)
    * `status_kontak`: `varchar(50)` (Default: 'baru', misal: 'dihubungi', 'loss', 'naik_calon')
    * `id_admin_fo`: `varchar(15)` (FK ke `users.id_user` via `ON DELETE SET NULL`).

#### 6. `calon_siswa`
* **Deskripsi**: Entitas profil personal calon siswa yang naik tingkat dari kontak prospek.
* **Karakteristik Skema**:
    * `id_calon`: `bigint(20) unsigned` (PK)
    * `kode_unik`: `varchar(50)` (Unique)
    * FK Wilayah: `id_provinsi`, `id_kabupaten`, `id_kecamatan`, `id_kelurahan` (Relasi ke Master Wilayah).
    * FK Sales: `assigned_fo` dan `assigned_akademik` (FK ke `users.id_user`).

#### 7. `calon_siswa_fo_detail`
* **Deskripsi**: Penyimpanan terisolasi (*Snapshot JSON*) untuk keperluan pengisian mandiri oleh tim FO.
* **Karakteristik Skema**:
    * `id_calon`: (FK ke `calon_siswa.id_calon` via `ON DELETE CASCADE`).
    * `pilihan_program_snapshot`: `longtext` dengan validasi struktur data `CHECK (json_valid(...))`.

#### 8. `calon_siswa_akademik`
* **Deskripsi**: Menampung instansi data sekolah, kurikulum asal, preferensi belajar, hingga asessment kapabilitas dasar komputer/gadget calon siswa.
* **Karakteristik Skema**:
    * `id_calon_akademik`: `bigint(20) unsigned` (PK)
    * `submission_state`: `enum('draft','submitted','withdrawn','invalid')`
    * Unique Constraint: Kombinasi `id_calon` dan `id_kursus` tidak boleh kembar.

#### 9. `calon_siswa_ortu`
* **Deskripsi**: Lembar instansi profil, pekerjaan, jenjang pendidikan, dan tingkat penghasilan orang tua/wali calon siswa.
* **Karakteristik Skema**:
    * `id_calon`: (FK ke `calon_siswa.id_calon`).
    * Enums: `pekerjaan_ayah`/`ibu`/`wali` dan `penghasilan_ayah`/`ibu`/`wali` (`kurang_1jt`, `1jt_3jt`, `3jt_5jt`, `lebih_5jt`).

#### 10. `calon_siswa_kursus`
* **Deskripsi**: Menampung urutan pilihan minat program multi-bahasa atau teknologi.
* **Karakteristik Skema**:
    * `jenis_program`: `enum('English','Digital','Both','Others')`.

#### 11. `calon_siswa_proses`
* **Deskripsi**: Log engine pelacak trial class, placement test, follow-up staff, dan status kelulusan pipeline pendaftaran.
* **Karakteristik Skema**:
    * `id_calon_akademik`: `bigint(20) unsigned` (Unique, FK ke `calon_siswa_akademik`).
    * Tracking state: `status_pipeline`, `status_diterima`, `status_form_pendaftaran`.

#### 12. `calon_siswa_bayar`
* **Deskripsi**: Catatan administrasi invoice, bank pembayaran, serta kesiapan bulan belajar awal.
* **Karakteristik Skema**:
    * `id_calon_akademik`: (FK ke `calon_siswa_akademik`).

#### 13. `calon_siswa_jadwal`
* **Deskripsi**: Rekaman milestone tanggal penting calon siswa (kontak pertama, wawancara, bayar, hingga tanggal keluar jika withdraw).
* **Karakteristik Skema**:
    * `id_calon_akademik`: (FK ke `calon_siswa_akademik`).

#### 14. `calon_siswa_form_programs` & `calon_siswa_form_program_requirements`
* **Deskripsi**: Dinamis formulir pendaftaran. Menentukan apakah suatu kursus membutuhkan jadwal trial, bukti kemampuan office, editing, atau prasyarat dokumen kustom lainnya.
* **Karakteristik Skema**:
    * Relasi: `calon_siswa_form_program_requirements` terikat secara cascade ke `calon_siswa_form_programs` via `calon_siswa_form_program_id`.

#### 15. `calon_siswa_proses_logs` & `calon_siswa_status_logs`
* **Deskripsi**: Audit trail ketat untuk melacak siapa yang mengubah status pipeline siswa, kapan dilakukan, dan catatan perubahannya.
* **Karakteristik Skema**:
    * `diubah_oleh`: (FK ke `users.id_user` via `ON DELETE SET NULL`).

---

### 🏫 C. Sub-Sistem Akademik, Rombel, & Penjadwalan Engine
Core utama penggerak kelas kursus, penjadwalan harian pengajar, presensi kelas, hingga histori ketuntasan nilai.

#### 16. `kursus`
* **Deskripsi**: Master rumpun keilmuan kursus utama.
* **Karakteristik Skema**:
    * `id_kursus`: `varchar(15)` (PK)
    * `tipe_kursus`: `enum('B2C','B2B')`

#### 17. `level`
* **Deskripsi**: Tingkatan kompetensi di dalam kursus (misal: Beginner, Intermediate, Advanced).
* **Karakteristik Skema**:
    * `id_level`: `varchar(15)` (PK).

#### 18. `kursus_level`
* **Deskripsi**: Tabel jembatan relasi *Many-to-Many* antara kursus dengan level kelulusan.

#### 19. `periode`
* **Deskripsi**: Pengaturan batch waktu aktif pembelajaran akademik.
* **Karakteristik Skema**:
    * `id_periode`: `varchar(15)` (PK).

#### 20. `sesi`
* **Deskripsi**: Pengaturan master jam operasional belajar mengajar.
* **Karakteristik Skema**:
    * `id_sesi`: `varchar(15)` (PK).

#### 21. `libur` & `kursus_libur`
* **Deskripsi**: Master tanggal libur nasional/kondisional yang digunakan untuk mengecualikan atau menjeda penjadwalan otomatis.

#### 22. `siswa`
* **Deskripsi**: Profil final siswa aktif hasil migrasi data / hasil konversi lulus pipeline CRM.
* **Karakteristik Skema**:
    * `id_siswa`: `bigint(20) unsigned` (PK).

#### 23. `kursus_siswa`
* **Deskripsi**: Mapping peminjaman program/kursus yang diambil siswa beserta status keaktifan dan kelulusannya.
* **Karakteristik Skema**:
    * Indexing khusus pada gabungan status aktif, status lulus, dan id siswa untuk optimalisasi query database.

#### 24. `jadwal`
* **Deskripsi**: Template/Induk rombongan belajar (Rombel).
* **Karakteristik Skema**:
    * `id_jadwal`: `bigint(20) unsigned` (PK)
    * FK Induk: Terikat ke `id_kursus`, `id_periode`, `id_level`, `id_sesi`.
    * `metode_belajar_jadwal`: `enum('Online','Offline','Hybrid')`.

#### 25. `jadwal_hari`
* **Deskripsi**: Pemetaan hari aktif dalam satu minggu untuk rombel template `jadwal`.

#### 26. `jadwal_pengajar`
* **Deskripsi**: Pivot penugasan staff tentor/guru ke dalam rombel template `jadwal`.
* **Karakteristik Skema**:
    * `id_user`: (FK ke `users.id_user` via `ON DELETE CASCADE`).

#### 27. `jadwal_siswa`
* **Deskripsi**: Peta jembatan siswa yang bergabung ke dalam rombel template beserta kelengkapan rapor dan ketuntasannya.
* **Karakteristik Skema**:
    * `id_jadwal_siswa`: `bigint(20) unsigned` (PK)
    * Status flag: `status_keluar`, `is_acc_rapor`, `status_ketuntasan`.

#### 28. `jadwal_detail`
* **Deskripsi**: Instansiasi harian/sesi aktual dari template induk `jadwal` (kalender kelas berjalan harian).
* **Karakteristik Skema**:
    * `id_jadwal_detail`: `bigint(20) unsigned` (PK)
    * `id_sesi_override`: (FK ke `sesi` jika ada jam belajar yang diganti mendadak khusus hari itu tanpa mengubah master template `jadwal`).
    * `original_jadwal_detail_id`: Swa-relasi (*Self-referencing FK*) ke dirinya sendiri untuk melacak riwayat pemisahan sesi.

#### 29. `jadwal_detail_logs`
* **Deskripsi**: Audit log khusus pelacakan mutasi perubahan tanggal, pergantian sesi pengajar, atau pembatalan sesi kelas harian.

#### 30. `catatan_kelas` & `topik_diskusi` & `catatan_kelas_tag`
* **Deskripsi**: Sistem pelaporan guru setelah mengajar, berisi rangkuman bab, topik diskusi, dan tag klasifikasi keilmuan.

#### 31. `catatan_siswa` & `followup_cs`
* **Deskripsi**: Catatan perkembangan perilaku/kendala siswa di kelas yang membutuhkan tindak lanjut observasi khusus (CRM/Academic Case Tracking).
* **Karakteristik Skema**:
    * `status_followup`: `enum('NEED FURTHER OBSERVATION','CASE CLOSED')`.

#### 32. `catatan_remidi_siswa`
* **Deskripsi**: Log khusus siswa yang membutuhkan perbaikan nilai, mencatat nilai sebelum, sesudah, dan persetujuan guru pengajar.

---

### 👥 D. Sub-Sistem HR, Karyawan, & Log Aktivitas Internal
Mengelola seluruh internal human resources, shift waktu kerja, pengajuan absensi, lembur, dan izin staff.

#### 33. `karyawan`
* **Deskripsi**: Data detail profile master kepegawaian internal perusahaan.
* **Karakteristik Skema**:
    * `id_karyawan`: `bigint(20) unsigned` (PK)
    * Strict Unique: `id_user` (`1:1 relationship` dengan tabel `users`), `kode_karyawan`, dan `nik_ktp`.
    * Fields Medis & Legal: `riwayat_kesehatan`, `nomor_npwp`, `bpjs_ketenagakerjaan`, `bpjs_kesehatan`.

#### 34. `keluarga_karyawan`
* **Deskripsi**: Data kontak darurat dan hubungan keluarga inti staff karyawan.

#### 35. `shift_kerja`
* **Deskripsi**: Pengaturan master jam masuk, jam pulang, dan toleransi keterlambatan presensi karyawan.

#### 36. `absensi` & `verifikasi_absensi`
* **Deskripsi**: Pencatatan riwayat presensi harian karyawan beserta status kalkulasinya.
* **Karakteristik Skema**:
    * `status_absensi`: `enum('Tepat Waktu','Izin','Terlambat','Hadir')`.
    * Relasi khusus: Jika ijin dihapus, status absensi diset null (`ON DELETE SET NULL`) agar log presensi tidak hilang.

#### 37. `izin_karyawan`
* **Deskripsi**: Pengajuan sakit, cuti, lembur, atau ijin mendadak.
* **Karakteristik Skema**:
    * `jenis_izin`: `enum('Ijin','Ijin Darurat','Lembur','Sakit')`.

#### 38. `pengajuan_karyawan` & `histori_pengajuan`
* **Deskripsi**: Alur pengajuan berkas / kebijakan internal yang memerlukan persetujuan bertingkat.
* **Karakteristik Skema**:
    * `status_verifikasi_pengajuan`: `enum('Diajukan','Revisi','Sudah Revisi','Diterima','Disetujui','Ditolak')`.

#### 39. `karyawan_resign`
* **Deskripsi**: Berkas dokumentasi alasan pengunduran diri staf.

#### 40. `catatan_mingguan`
* **Deskripsi**: Pelaporan ringkasan evaluasi kerja mingguan per akun user.

#### 41. `activity_log`
* **Deskripsi**: Log track sistem bawaan framework, mencatat deskripsi event create/update/delete data lengkap beserta payload data lama dan baru dalam kolom JSON.
* **Karakteristik Skema**:
    * `properties`: `longtext` dengan check `json_valid`.

---

### 🤝 E. Sub-Sistem Business Development (Kemitraan External)
Mengelola relasi link form, pengajuan progress kerjasama, dan verifikasi mitra B2B corporate.

#### 42. `busdev_bidang` & `bidang_kategori` & `bidang_link`
* **Deskripsi**: Pengelompokan jenis bidang industri kemitraan beserta tautan berkas drive digital yang dibagikan.

#### 43. `mitra` & `mitra_progres` & `kemitraan_verifikator`
* **Deskripsi**: Manajemen entitas korporasi eksternal, log progres deal kerjasama, dan penugasan verifikator internal.

---

### 🗺️ F. Sub-Sistem Data Master Regional & Sarpras
Master regional geografis seluruh Indonesia yang digunakan bersama oleh modul CRM dan HR.

#### 44. `provinsi`
#### 45. `kabupaten` (Berelasi ke `provinsi`)
#### 46. `kecamatan` (Berelasi ke `kabupaten`)
#### 47. `kelurahan` (Berelasi ke `kecamatan`)
* **Deskripsi**: Skema hierarki data wilayah Indonesia berskala penuh.

#### 48. `admin_sarpras`
* **Deskripsi**: Kontak whatsapp penanggung jawab sarana dan prasarana penunjang operasional.

#### 49. `cache` & `cache_locks`
* **Deskripsi**: Framework data storage untuk optimalisasi kecepatan query sistem.

#### 50. `failed_jobs`, `jobs`, `job_batches`
* **Deskripsi**: Queue driver database untuk menangani proses pengiriman email massal atau otomasi kalkulasi kelas di latar belakang (*Asynchronous Background Process*).

---

## ⛓️ 3. Strict Architectural Foreign Key Rules

1. **Cascade Cleansing (`ON DELETE CASCADE`)**:
   Diterapkan secara ketat pada tabel pivot hubungan *Many-to-Many* atau riwayat logs harian (seperti `division_user`, `jadwal_pengajar`, `jadwal_siswa`, `calon_siswa_proses_logs`, `calon_siswa_fo_detail`). Tujuannya agar apabila entitas induk (`users`, `jadwal`, atau `calon_siswa`) dihapus, database otomatis membersihkan sampah data jembatan agar memori 8GB RAM di baseline hardware tetap hemat dan terjaga efisiensinya.
2. **Historical Shielding (`ON DELETE SET NULL`)**:
   Diterapkan pada tabel yang merekam jejak audit keuangan atau kehadiran pegawai (seperti field `id_izin` di tabel `absensi`, atau field `id_admin_fo` di tabel `kontak_prospek`). Aturan ini menjamin bahwa meskipun dokumen ijin atau akun staff FO dihapus, baris data log absensi dan pipelines statistik CRM masa lalu tetap utuh sebagai riwayat historis laporan eksekutif.
