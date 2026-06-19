import os
import re
import sys
import time
import pandas as pd

# Tambahkan root project ke sys.path agar bisa import core.llm_analyzer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. Load API Key dari .streamlit/secrets.toml
api_key = ""
secrets_path = os.path.join(".streamlit", "secrets.toml")
if os.path.exists(secrets_path):
    with open(secrets_path, "r") as f:
        content = f.read()
        match = re.search(r'GEMINI_API_KEY\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            api_key = match.group(1)

if not api_key:
    # Coba dari environment variable
    api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    print("ERROR: API Key tidak ditemukan di .streamlit/secrets.toml maupun environment variable!")
    sys.exit(1)

print(f"Menggunakan API Key: {api_key[:8]}...{api_key[-8:]}")

from core.llm_analyzer import analyze_feature
from google import genai

# Inisialisasi client
client = genai.Client(api_key=api_key)
model_utama = 'models/gemini-3.1-flash-lite-preview'

print(f"\n[1/2] Mulai mengirim spam ke {model_utama} agar kuotanya habis (429)...")
rate_limit_triggered = False

for i in range(1, 40):
    try:
        print(f"Kirim request spam ke-{i}...", end="", flush=True)
        client.models.generate_content(
            model=model_utama,
            contents="Say hello quickly"
        )
        print(" [SUKSES]")
    except Exception as e:
        err_str = str(e)
        print(" [GAGAL]")
        if "429" in err_str:
            print("\n[INFO] Berhasil memicu Rate Limit (429) pada model pertama!")
            print(f"Detail Error Google: {err_str}")
            rate_limit_triggered = True
            break
        else:
            print(f"Error lain: {err_str}")
            time.sleep(0.5)

if not rate_limit_triggered:
    print("\nWARNING: Limit 429 belum tercapai setelah 40 request.")
    print("Mencoba langsung panggil analyze_feature()...\n")
else:
    print("\n[2/2] Memanggil analyze_feature() untuk melihat perpindahan model secara langsung...")

dummy_data = {
    "DATA_SISWA": pd.DataFrame(),
    "DATA_NILAI": pd.DataFrame(),
    "DATA_KELUAR": pd.DataFrame()
}

start_time = time.time()
hasil = analyze_feature(dummy_data, "academic_perf")
duration = time.time() - start_time

print(f"\nHasil analisis didapatkan dalam {duration:.2f} detik:")
print("-" * 60)
print(hasil)
print("-" * 60)
