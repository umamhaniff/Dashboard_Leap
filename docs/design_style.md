# 🎨 EduDecision AI V2 - Design Style Guide

Dokumen ini memandu implementasi gaya visual dan tata letak antarmuka pengguna (*User Interface*) untuk **EduDecision AI V2** berdasarkan prinsip **Genesis Design System**.

---

## 1. Filosofi Desain

EduDecision AI V2 mengusung filosofi **Genesis Design**: antarmuka editorial dengan presisi tinggi yang memadukan tipografi display tebal, ruang bernapas (*spacing*) yang lega, dan permukaan panel datar dengan border tipis minimalis. 

Tujuan utama dari gaya desain ini adalah memberikan kesan profesional, bersih, dan modern tanpa terasa kaku, serta menjaga keseimbangan antara kerapatan informasi tinggi (*high information density*) dengan kenyamanan visual.

---

## 2. Palet Warna (Color Palette)

Palet warna dikurasi secara harmonis untuk memberikan pengalaman premium, menghindari penggunaan warna dasar murni (*pure RGB*).

| Elemen | Kode Hex | Visual Representasi | Deskripsi & Penggunaan |
| :--- | :--- | :--- | :--- |
| **Primary** | `#6366F1` | 🟦 Indigo | Tombol utama (CTA), status aktif, tautan aktif, focus rings, dan interaksi highlight. |
| **Primary Hover** | `#4F46E5` | 🟦 Dark Indigo | Warna hover untuk elemen interaktif utama. |
| **Secondary** | `#20970B` | 🟩 Green | Highlight khusus merek/brand (misal dekorasi visual). |
| **Neutral Muted** | `#9C9C9C` | 🟨 Gray | Teks penjelas redup, placeholder, dan elemen non-aktif. |
| **Background** | `#FAFAFA` | ⬜ Off-White | Latar belakang halaman utama (abu-abu sangat terang dan hangat). |
| **Surface** | `#FFFFFF` | ⬜ Pure White | Latar belakang kartu (*cards*), panel kontrol, dan modal dialog. |
| **Text Primary** | `#0A0A0A` | ⬛ Near-Black | Judul utama, teks konten utama, dan label penting. |
| **Text Secondary**| `#6B6B6B` | ⬜ Slate Gray | Deskripsi sub-kriteria, meta-data, dan label sekunder. |
| **Border** | `#E8E8EC` | ⬜ Soft Gray | Border tipis pada kartu, input field, dan pembatas visual. |
| **Success** | `#10B981` | 🟩 Mint Green | Peringatan sukses, status terbit, indikator positif. |
| **Warning** | `#F59E0B` | 🟧 Amber | Status tertunda, peringatan kehati-hatian. |
| **Error** | `#EF4444` | 🟥 Coral Red | Tombol destruktif, peringatan kritis, validasi salah. |

---

## 3. Tipografi (Typography)

Sistem menggunakan kombinasi jenis huruf modern untuk membedakan struktur teks secara jelas:

* **Display & Headings**: **General Sans** (Bold / Semi-bold)
  * Karakteristik: Geometris, spasi antar huruf agak rapat (`-0.03em` hingga `-0.04em`) untuk memberikan efek editorial yang kuat.
* **Body & UI Text**: **DM Sans** (Regular / Medium)
  * Karakteristik: Humanis, mudah dibaca pada ukuran kecil hingga sedang.
* **Code, Keys, & CLI Commands**: **JetBrains Mono** (Regular)
  * Karakteristik: Monospace yang bersih untuk kode teknis atau format data khusus.

### Skala Ukuran Font:
* **Display**: `72px`
* **Headline / Judul Utama**: `60px`
* **Section Heading**: `32px`
* **Sub-Heading / Menu**: `24px`
* **Body / Konten Utama**: `15px`
* **Small / Keterangan**: `13px`
* **Caption / Overline**: `11px` (Uppercase)

---

## 4. Struktur UI & Layout Responsif

### 4.1 Halaman Login (Mobile First Approach - MFA)
Formulir Login didesain responsif menggunakan kontainer CSS khusus yang menyesuaikan lebar layar secara otomatis (*Mobile First*):
* **Desktop (`min-width: 1200px`)**: Lebar form login melebar hingga maksimal **`850px`** untuk pemanfaatan layar lebar.
* **Tablet (`min-width: 768px`)**: Lebar form login dibatasi maksimal **`680px`**.
* **Mobile / Ponsel**: Lebar form login dinamis **`100%`** memenuhi lebar layar dengan padding minimal di sisi kanan-kiri.

### 4.2 Navigasi Utama (Streamlit Sidebar)
Aplikasi memanfaatkan tata letak navigasi kiri berbasis sidebar bawaan Streamlit (`st.sidebar.radio`):
* Pilihan Modul Aktif secara langsung:
  * `🏠 Unified LKP Overview` (Ringkasan Data Hibrida)
  * `📊 Modul Akademik` (Google Sheets Data & Gemini Academic Engine)
  * `🗄️ Modul Operasional` (MariaDB web_statistik & Gemini Operations Engine)
* Tombol **Sign Out** terintegrasi secara visual di bagian bawah menu navigasi sidebar untuk mempermudah alur keluar pengguna.

---

## 5. Spacing & Border Radius

### Skala Spacing (Base Grid: 4px):
Semua margin, padding, dan gap harus mengikuti kelipatan 4px:
* **4px / 8px**: Jarak antar elemen mikro (label ke input field).
* **12px / 16px / 20px**: Padding dalam kartu atau tombol.
* **32px / 48px / 64px**: Spasi antar seksion konten (Mobile s.d. Desktop).

### Skala Kelengkungan Sudut (Border Radius):
* **4px**: Tag, chip, badge, dan potongan kode inline.
* **6px**: Tombol utama/sekunder dan kolom input field.
* **8px**: Dropdown menu, popover, dan panel kontrol kecil.
* **12px**: Kartu data utama (*Data Cards*), form login container, dan kolom pencarian.
* **9999px (Pill)**: Foto profil (avatar), lampu indikator status, dan tombol beralih (*toggle/switch*).

---

## 6. Elevasi & Efek Interaktif (Micro-Animations)

Genesis Design meminimalkan bayangan statis (*flat design representation*) dan memanfaatkan bayangan dinamis hanya untuk interaksi:
* **Hover State pada Kartu**: Kartu data datar dengan border tipis `1px` akan naik secara vertikal sebesar `-2px` (*vertical lift*) dan memunculkan bayangan halus (`0 8px 30px rgba(0,0,0,0.08)`) dengan durasi transisi `200ms`.
* **Hover State pada Tombol Utama**: Tombol indigo akan mendapatkan efek pendaran halus (`0 4px 12px rgba(99,102,241,0.35)`) dan sedikit naik `1px` saat disorot kursor.
* **Focus Ring pada Input**: Input field yang aktif mendapatkan border luar indigo dengan ring pendaran `3px rgba(99,102,241,0.12)`.
* **Navigasi Atas/Samping**: Menggunakan efek `backdrop-blur` (kaca buram transparan) alih-alih bayangan tebal untuk menggambarkan elevasi.
