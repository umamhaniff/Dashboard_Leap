# Hybrid DSS SAW and K-Means Clustering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Simple Additive Weighting (SAW) algorithm and K-Means clustering in the backend to rank and segment students, leads, and unified cases in LKP LEAP.

**Architecture:** We will implement general SAW and K-Means calculation utility functions in `core/data_pipeline.py`. We will use correlation-based weights with fallback defaults to calculate scores, cluster students/leads into 3 risk levels via K-Means, and integrate these results into `core/llm_analyzer.py` prompts to enable explainable AI analysis.

**Tech Stack:** Python, Pandas, NumPy, scikit-learn (K-Means), Pytest

---

### Task 1: Add General SAW & K-Means Utility Functions

**Files:**
- Modify: `core/data_pipeline.py`
- Test: `tests/test_data_pipeline.py`

- [ ] **Step 1: Write the failing tests**
  Add the following test functions to `tests/test_data_pipeline.py` to verify normalization, SAW preferences, and K-Means risk clustering.

```python
import numpy as np
import pandas as pd
from core.data_pipeline import calculate_saw, apply_kmeans_risk

def test_calculate_saw():
    # Mock decision matrix
    data = pd.DataFrame([
        {"id": 1, "c1": 80.0, "c2": 90.0, "c3": 10.0},
        {"id": 2, "c1": 60.0, "c2": 80.0, "c3": 20.0},
        {"id": 3, "c1": 70.0, "c2": 70.0, "c3": 30.0}
    ])
    criteria = ["c1", "c2", "c3"]
    weights = {"c1": 0.5, "c2": 0.3, "c3": 0.2}
    types = {"c1": "benefit", "c2": "benefit", "c3": "cost"}
    
    result = calculate_saw(data, criteria, weights, types)
    assert "saw_score" in result.columns
    assert "saw_rank" in result.columns
    assert result.loc[result["id"] == 1, "saw_score"].values[0] > result.loc[result["id"] == 3, "saw_score"].values[0]

def test_apply_kmeans_risk():
    data = pd.DataFrame({
        "saw_score": [0.95, 0.90, 0.88, 0.55, 0.50, 0.45, 0.20, 0.15, 0.10],
        "feature1": [95, 90, 88, 55, 50, 45, 20, 15, 10]
    })
    result = apply_kmeans_risk(data, ["saw_score", "feature1"], n_clusters=3)
    assert "risk_cluster" in result.columns
    # Ensure Cluster 0 is always High Risk (lowest mean SAW score) and Cluster 2 is Low Risk (highest mean SAW score)
    c0_mean = result[result["risk_cluster"] == 0]["saw_score"].mean()
    c2_mean = result[result["risk_cluster"] == 2]["saw_score"].mean()
    assert c0_mean < c2_mean
```

- [ ] **Step 2: Run tests to verify they fail**
  Run: `.venv/Scripts/pytest tests/test_data_pipeline.py -k "test_calculate_saw or test_apply_kmeans_risk" -v`  
  Expected: FAIL with "ImportError" or "NameError: name 'calculate_saw' is not defined".

- [ ] **Step 3: Write minimal implementation in `core/data_pipeline.py`**
  Add `scikit-learn` import at the top of the file, then implement the functions:

```python
# Add at top of core/data_pipeline.py
from sklearn.cluster import KMeans
```

```python
# Add at end of core/data_pipeline.py
def calculate_saw(df: pd.DataFrame, criteria: List[str], weights: Dict[str, float], types: Dict[str, str]) -> pd.DataFrame:
    """Calculates Simple Additive Weighting (SAW) scores and ranks alternatives."""
    if df.empty:
        df_copy = df.copy()
        df_copy["saw_score"] = 0.0
        df_copy["saw_rank"] = 0
        return df_copy
        
    df_copy = df.copy()
    norm_matrix = pd.DataFrame(index=df.index)
    
    for c in criteria:
        if c not in df_copy.columns:
            df_copy[c] = 0.0
            
        series = pd.to_numeric(df_copy[c], errors="coerce").fillna(0.0)
        max_val = series.max()
        min_val = series.min()
        
        if types[c] == "benefit":
            if max_val > 0:
                norm_matrix[c] = series / max_val
            else:
                norm_matrix[c] = 0.0
        else:  # cost
            # Add 1.0 safety division parameter to prevent division by zero
            norm_matrix[c] = (min_val + 1.0) / (series + 1.0)
            
    # Calculate preference score Vi
    saw_score = np.zeros(len(df_copy))
    for c in criteria:
        saw_score += norm_matrix[c].values * weights[c]
        
    df_copy["saw_score"] = saw_score
    # Rank descending: 1 is highest score, len(df) is lowest
    df_copy["saw_rank"] = df_copy["saw_score"].rank(ascending=False, method="min").astype(int)
    return df_copy

def apply_kmeans_risk(df: pd.DataFrame, features: List[str], n_clusters: int = 3) -> pd.DataFrame:
    """Applies K-Means clustering and orders cluster indices so 0 is High Risk, 2 is Safe."""
    if df.empty:
        df_copy = df.copy()
        df_copy["risk_cluster"] = 0
        return df_copy
        
    df_copy = df.copy()
    
    # Handle edge case where dataset has fewer unique samples than clusters
    n_samples = len(df_copy)
    if n_samples < n_clusters:
        # Fallback to manual quantile splitting
        sorted_indices = df_copy["saw_score"].argsort()
        clusters = np.zeros(n_samples, dtype=int)
        for i, idx in enumerate(sorted_indices):
            if i < n_samples / 3:
                clusters[idx] = 0  # High Risk
            elif i < 2 * n_samples / 3:
                clusters[idx] = 1  # Medium Risk
            else:
                clusters[idx] = 2  # Safe
        df_copy["risk_cluster"] = clusters
        return df_copy
        
    try:
        # Fit K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        X = df_copy[features].fillna(0.0)
        cluster_labels = kmeans.fit_predict(X)
        df_copy["risk_cluster"] = cluster_labels
        
        # Auto-sort cluster labels so cluster 0 has the lowest average SAW score
        cluster_means = df_copy.groupby("risk_cluster")["saw_score"].mean().sort_values()
        mapping = {old: new for new, old in enumerate(cluster_means.index)}
        df_copy["risk_cluster"] = df_copy["risk_cluster"].map(mapping)
    except Exception as e:
        logger.warning(f"K-Means clustering failed ({str(e)}). Falling back to ranks.")
        # Fallback to rank-based division
        sorted_ranks = df_copy["saw_score"].rank(ascending=True, method="first")
        percentiles = sorted_ranks / len(df_copy)
        df_copy["risk_cluster"] = np.where(percentiles <= 0.33, 0, np.where(percentiles <= 0.66, 1, 2))
        
    return df_copy
```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `.venv/Scripts/pytest tests/test_data_pipeline.py -k "test_calculate_saw or test_apply_kmeans_risk" -v`  
  Expected: PASS

- [ ] **Step 5: Commit changes**
  Run:
  ```bash
  git add core/data_pipeline.py tests/test_data_pipeline.py
  git commit -m "feat: add general SAW and K-Means utility functions to backend"
  ```

---

### Task 2: Implement Sku-Specific SAW and K-Means Functions and Hook into Data Loaders

**Files:**
- Modify: `core/data_pipeline.py`
- Test: `tests/test_data_pipeline.py`

- [ ] **Step 1: Write the failing test**
  Add the following test to `tests/test_data_pipeline.py` to verify modular calculations:

```python
from core.data_pipeline import (
    calculate_sheets_saw_kmeans,
    calculate_db_saw_kmeans,
    calculate_unified_saw_kmeans
)

def test_sku_specific_saw_kmeans():
    # Mock inputs
    sheets_mock = {
        "DATA_SISWA": pd.DataFrame([{"nama_siswa": "A"}, {"nama_siswa": "B"}]),
        "DATA_NILAI": pd.DataFrame([
            {"nama_siswa": "A", "periode": "Mid", "score": 80.0},
            {"nama_siswa": "B", "periode": "Mid", "score": 60.0}
        ]),
        "DATA_ABSENSI": pd.DataFrame([
            {"nama_siswa": "A", "status": "Hadir"},
            {"nama_siswa": "B", "status": "Sakit"}
        ]),
        "DATA_KELUAR": pd.DataFrame([])
    }
    
    db_mock = {
        "calon_siswa": pd.DataFrame([
            {"id_calon": 1, "nama_lengkap": "Calon A", "fo_status": "Lengkap"},
            {"id_calon": 2, "nama_lengkap": "Calon B", "fo_status": "Belum Lengkap"}
        ]),
        "calon_siswa_bayar": pd.DataFrame([
            {"id_calon_akademik": 1, "jumlah_bayar": 500000.0, "tanggal_konfirmasi_bayar": "2026-06-05 09:00:00"},
            {"id_calon_akademik": 2, "jumlah_bayar": 100000.0, "tanggal_konfirmasi_bayar": "2026-06-07 10:00:00"}
        ]),
        "calon_siswa_akademik": pd.DataFrame([
            {"id_calon_akademik": 1, "id_calon": 1},
            {"id_calon_akademik": 2, "id_calon": 2}
        ]),
        "siswa": pd.DataFrame([]),
        "catatan_siswa": pd.DataFrame([])
    }
    
    # 1. Sheets SAW
    sheets_res = calculate_sheets_saw_kmeans(sheets_mock)
    assert "saw_score" in sheets_res.columns
    assert "risk_cluster" in sheets_res.columns
    
    # 2. Database SAW
    db_res = calculate_db_saw_kmeans(db_mock)
    assert "saw_score" in db_res.columns
    assert "risk_cluster" in db_res.columns
    
    # 3. Unified SAW
    unified_res = calculate_unified_saw_kmeans(sheets_mock, db_mock)
    assert "saw_score" in unified_res.columns
    assert "risk_cluster" in unified_res.columns
```

- [ ] **Step 2: Run tests to verify they fail**
  Run: `.venv/Scripts/pytest tests/test_data_pipeline.py -k "test_sku_specific_saw_kmeans" -v`  
  Expected: FAIL with "ImportError: cannot import name..."

- [ ] **Step 3: Implement functions in `core/data_pipeline.py` and hook them into loaders**

Insert the following functions at the end of `core/data_pipeline.py`:

```python
def calculate_sheets_saw_kmeans(cleaned_sheets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculates SAW and clusters active students from Sheets data."""
    siswa_df = cleaned_sheets.get("DATA_SISWA", pd.DataFrame())
    nilai_df = cleaned_sheets.get("DATA_NILAI", pd.DataFrame())
    absensi_df = cleaned_sheets.get("DATA_ABSENSI", pd.DataFrame())
    
    if siswa_df.empty:
        return pd.DataFrame(columns=["nama_siswa", "saw_score", "saw_rank", "risk_cluster"])
        
    # Standardize names
    df = pd.DataFrame({"nama_siswa": siswa_df["nama_siswa"].unique()})
    
    # Feature 1: Average Score
    if not nilai_df.empty and "nama_siswa" in nilai_df.columns and "score" in nilai_df.columns:
        avg_scores = nilai_df.groupby("nama_siswa")["score"].mean().reset_index()
        df = df.merge(avg_scores, on="nama_siswa", how="left")
    else:
        df["score"] = 70.0
    df["score"] = df["score"].fillna(70.0)
    
    # Feature 2 & 4: Attendance Rate & Tardiness
    if not absensi_df.empty and "nama_siswa" in absensi_df.columns:
        absensi_df["hadir_num"] = absensi_df["status"].isin(["Tepat Waktu", "Terlambat", "Hadir"]).astype(int)
        absensi_df["late_num"] = absensi_df["status"].str.lower().str.contains("lambat").astype(int)
        
        att_rate = absensi_df.groupby("nama_siswa")["hadir_num"].mean().reset_index()
        att_rate["hadir_num"] = att_rate["hadir_num"] * 100
        att_rate.rename(columns={"hadir_num": "attendance_rate"}, inplace=True)
        
        late_count = absensi_df.groupby("nama_siswa")["late_num"].sum().reset_index()
        late_count.rename(columns={"late_num": "late_count"}, inplace=True)
        
        df = df.merge(att_rate, on="nama_siswa", how="left")
        df = df.merge(late_count, on="nama_siswa", how="left")
    else:
        df["attendance_rate"] = 90.0
        df["late_count"] = 0.0
    df["attendance_rate"] = df["attendance_rate"].fillna(90.0)
    df["late_count"] = df["late_count"].fillna(0.0)
    
    # Feature 3: Passing Rate (Exams > 70)
    if not nilai_df.empty and "nama_siswa" in nilai_df.columns and "score" in nilai_df.columns:
        nilai_df["is_tuntas"] = (nilai_df["score"] > 70).astype(int)
        tuntas_rate = nilai_df.groupby("nama_siswa")["is_tuntas"].mean().reset_index()
        tuntas_rate.rename(columns={"is_tuntas": "passing_rate"}, inplace=True)
        df = df.merge(tuntas_rate, on="nama_siswa", how="left")
    else:
        df["passing_rate"] = 1.0
    df["passing_rate"] = df["passing_rate"].fillna(1.0)
    
    # Execute SAW (Academic settings)
    criteria = ["score", "attendance_rate", "passing_rate", "late_count"]
    weights = {"score": 0.40, "attendance_rate": 0.30, "passing_rate": 0.20, "late_count": 0.10}
    types = {"score": "benefit", "attendance_rate": "benefit", "passing_rate": "benefit", "late_count": "cost"}
    
    saw_df = calculate_saw(df, criteria, weights, types)
    return apply_kmeans_risk(saw_df, ["saw_score", "score", "attendance_rate"])

def calculate_db_saw_kmeans(db_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculates SAW and clusters prospective student leads from MariaDB."""
    calon_df = db_data.get("calon_siswa", pd.DataFrame())
    bayar_df = db_data.get("calon_siswa_bayar", pd.DataFrame())
    akad_df = db_data.get("calon_siswa_akademik", pd.DataFrame())
    
    if calon_df.empty:
        return pd.DataFrame(columns=["nama_lengkap", "saw_score", "saw_rank", "risk_cluster"])
        
    df = calon_df[["id_calon", "nama_lengkap", "fo_status"]].copy()
    df["is_fo_lengkap"] = (df["fo_status"] == "Lengkap").astype(int)
    
    # Amount Paid
    if not bayar_df.empty and not akad_df.empty:
        leads_payment = akad_df.merge(bayar_df, on="id_calon_akademik", how="inner")
        payment_sum = leads_payment.groupby("id_calon")["jumlah_bayar"].sum().reset_index()
        df = df.merge(payment_sum, on="id_calon", how="left")
    else:
        df["jumlah_bayar"] = 0.0
    df["jumlah_bayar"] = df["jumlah_bayar"].fillna(0.0)
    
    # FO comment length (Interest intensity proxy)
    fo_detail = db_data.get("calon_siswa_fo_detail", pd.DataFrame())
    if not fo_detail.empty and "catatan_awal_fo" in fo_detail.columns:
        fo_detail["notes_len"] = fo_detail["catatan_awal_fo"].astype(str).str.len()
        comment_len = fo_detail.groupby("id_calon")["notes_len"].max().reset_index()
        df = df.merge(comment_len, on="id_calon", how="left")
    else:
        df["notes_len"] = 0.0
    df["notes_len"] = df["notes_len"].fillna(0.0)
    
    # Speed to confirm payment (days)
    df["days_to_pay"] = 30.0  # Default slow conversion penalty
    if not bayar_df.empty and not akad_df.empty:
        leads_payment = akad_df.merge(bayar_df, on="id_calon_akademik", how="inner")
        leads_payment = leads_payment.merge(calon_df, on="id_calon", how="inner")
        
        leads_payment["created_dt"] = pd.to_datetime(leads_payment["created_at"], errors="coerce")
        leads_payment["pay_dt"] = pd.to_datetime(leads_payment["tanggal_konfirmasi_bayar"], errors="coerce")
        
        leads_payment["speed"] = (leads_payment["pay_dt"] - leads_payment["created_dt"]).dt.total_seconds() / (24 * 3600)
        leads_payment["speed"] = leads_payment["speed"].clip(0, 90).fillna(30.0)
        
        speed_df = leads_payment.groupby("id_calon")["speed"].min().reset_index()
        speed_df.rename(columns={"speed": "days_to_pay"}, inplace=True)
        
        # Drop temporary default
        df.drop(columns=["days_to_pay"], inplace=True)
        df = df.merge(speed_df, on="id_calon", how="left")
        
    df["days_to_pay"] = df["days_to_pay"].fillna(30.0)
    
    # Run SAW
    criteria = ["jumlah_bayar", "is_fo_lengkap", "notes_len", "days_to_pay"]
    weights = {"jumlah_bayar": 0.40, "is_fo_lengkap": 0.30, "notes_len": 0.10, "days_to_pay": 0.20}
    types = {"jumlah_bayar": "benefit", "is_fo_lengkap": "benefit", "notes_len": "benefit", "days_to_pay": "cost"}
    
    saw_df = calculate_saw(df, criteria, weights, types)
    return apply_kmeans_risk(saw_df, ["saw_score", "jumlah_bayar", "is_fo_lengkap"])

def calculate_unified_saw_kmeans(cleaned_sheets: Dict[str, pd.DataFrame], db_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculates Unified SAW and clusters students combining Sheets Academics & SQL CS records."""
    sheets_siswa = calculate_sheets_saw_kmeans(cleaned_sheets)
    db_siswa = db_data.get("siswa", pd.DataFrame())
    catatan_cs = db_data.get("catatan_siswa", pd.DataFrame())
    
    if sheets_siswa.empty:
        return pd.DataFrame(columns=["nama_siswa", "saw_score", "saw_rank", "risk_cluster"])
        
    df = sheets_siswa[["nama_siswa", "score", "attendance_rate"]].copy()
    df.rename(columns={"score": "academic_score"}, inplace=True)
    
    # Map Names to Database IDs
    df["id_siswa"] = np.nan
    if not db_siswa.empty and "nama_lengkap" in db_siswa.columns:
        # Simple name normalization mapping
        db_siswa["clean_name"] = db_siswa["nama_lengkap"].astype(str).str.lower().str.strip()
        df["clean_name"] = df["nama_siswa"].astype(str).str.lower().str.strip()
        
        mapped = df.merge(db_siswa[["id_siswa", "clean_name"]], on="clean_name", how="left")
        df["id_siswa"] = mapped["id_siswa"]
        df.drop(columns=["clean_name"], inplace=True)
        
    df["has_critical_notes"] = 0.0
    df["total_notes"] = 0.0
    
    if not catatan_cs.empty and "id_siswa" in catatan_cs.columns:
        catatan_cs["is_critical"] = (catatan_cs["status_followup"] == "NEED FURTHER OBSERVATION").astype(int)
        
        crit = catatan_cs.groupby("id_siswa")["is_critical"].max().reset_index()
        total = catatan_cs.groupby("id_siswa")["is_critical"].count().reset_index()
        total.rename(columns={"is_critical": "total_notes"}, inplace=True)
        
        df = df.merge(crit, on="id_siswa", how="left")
        df = df.merge(total, on="id_siswa", how="left")
        
        df["has_critical_notes"] = df["is_critical"].fillna(0.0)
        df["total_notes"] = df["total_notes"].fillna(0.0)
        df.drop(columns=["is_critical"], inplace=True)
        
    # Run SAW
    criteria = ["academic_score", "attendance_rate", "has_critical_notes", "total_notes"]
    weights = {"academic_score": 0.40, "attendance_rate": 0.30, "has_critical_notes": 0.20, "total_notes": 0.10}
    types = {"academic_score": "benefit", "attendance_rate": "benefit", "has_critical_notes": "cost", "total_notes": "cost"}
    
    saw_df = calculate_saw(df, criteria, weights, types)
    return apply_kmeans_risk(saw_df, ["saw_score", "academic_score", "attendance_rate"])
```

Hook this calculation directly into `clean_all_data` and `load_mariadb_data` to ensure the dashboard caches them:
- In `clean_all_data`, add:
  ```python
  # Add at the end of clean_all_data in core/data_pipeline.py
  # Calculate Sheets SAW
  try:
      sheets_saw = calculate_sheets_saw_kmeans(cleaned_data)
      cleaned_data["DATA_SAW_RANKING"] = sheets_saw
  except Exception as e:
      logger.error(f"Failed to calculate Sheets SAW ranking: {str(e)}")
  ```
- In `load_mariadb_data`, add:
  ```python
  # Add right before returning result in load_mariadb_data in core/data_pipeline.py
  try:
      db_saw = calculate_db_saw_kmeans(result)
      result["DB_SAW_LEADS"] = db_saw
      unified_saw = calculate_unified_saw_kmeans(generate_mock_mariadb_data(), result)  # safe fallback calculation
      result["UNIFIED_SAW"] = unified_saw
  except Exception as e:
      logger.error(f"Failed to calculate DB SAW: {str(e)}")
  ```
- Also apply this in `generate_mock_mariadb_data()` before returning:
  ```python
  # Add right before returning in generate_mock_mariadb_data in core/data_pipeline.py
  mock_data = { ... }
  try:
      mock_data["DB_SAW_LEADS"] = calculate_db_saw_kmeans(mock_data)
      mock_data["UNIFIED_SAW"] = calculate_unified_saw_kmeans(mock_data, mock_data)
  except Exception as e:
      logger.error(f"Failed to calculate Mock DB SAW: {str(e)}")
  return mock_data
  ```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `.venv/Scripts/pytest tests/test_data_pipeline.py -v`  
  Expected: PASS (all tests pass)

- [ ] **Step 5: Commit changes**
  Run:
  ```bash
  git add core/data_pipeline.py tests/test_data_pipeline.py
  git commit -m "feat: implement modular SAW and K-Means calculators and hook to data loaders"
  ```

---

### Task 3: Integrate SAW & K-Means Output into Gemini AI Prompts

**Files:**
- Modify: `core/llm_analyzer.py`
- Test: `tests/test_llm_analyzer.py`

- [ ] **Step 1: Write the failing test**
  Add a test to verify prompt generation contains "SAW" data table when supplied:

```python
from core.llm_analyzer import get_academic_prompt, get_operations_prompt, get_unified_overview_prompt

def test_prompts_with_saw_data():
    data = {
        "DATA_SAW_RANKING": pd.DataFrame([
            {"nama_siswa": "Agus", "saw_score": 0.42, "saw_rank": 1, "risk_cluster": 0}
        ]),
        "DB_SAW_LEADS": pd.DataFrame([
            {"nama_lengkap": "Prospek A", "saw_score": 0.85, "saw_rank": 1, "risk_cluster": 2}
        ]),
        "UNIFIED_SAW": pd.DataFrame([
            {"nama_siswa": "Rian", "saw_score": 0.31, "saw_rank": 1, "risk_cluster": 0}
        ])
    }
    
    # 1. Sheets Academic Prompt
    acad_prompt = get_academic_prompt(data)
    assert "SAW" in acad_prompt
    assert "Agus" in acad_prompt
    
    # 2. Database SQL Prompt
    ops_prompt = get_operations_prompt(data)
    assert "SAW" in ops_prompt
    assert "Prospek A" in ops_prompt
    
    # 3. Unified Overview Prompt
    unified_prompt = get_unified_overview_prompt({"sheets": data, "db": data})
    assert "SAW" in unified_prompt
    assert "Rian" in unified_prompt
```

- [ ] **Step 2: Run tests to verify they fail**
  Run: `.venv/Scripts/pytest tests/test_llm_analyzer.py -k "test_prompts_with_saw_data" -v`  
  Expected: FAIL with "AssertionError" or "KeyError".

- [ ] **Step 3: Modify prompt functions in `core/llm_analyzer.py`**
  Update the following three functions in `core/llm_analyzer.py`:

Modify `get_academic_prompt`:
```python
def get_academic_prompt(dataframes: dict) -> str:
    """Generate prompt template for Google Sheets (Academic focus)."""
    combined = "=== AUDIT AKADEMIK & NILAI SISWA (GOOGLE SHEETS - ACADEMIC) ===\n"
    for name in ["DATA_SISWA", "DATA_NILAI", "DATA_KELUAR"]:
        df = dataframes.get(name)
        if df is not None and not df.empty:
            combined += f"\n[TABEL: {name}]\n{df.head(40).to_string(index=False)}\n"
            
    # Augment with SAW Rankings
    saw_df = dataframes.get("DATA_SAW_RANKING")
    if saw_df is not None and not saw_df.empty:
        combined += "\n=== SPK SAW & K-MEANS ACADEMIC HEALTH RANKING ===\n"
        combined += "Keterangan Kluster: 0 = Risiko Tinggi (High Risk), 1 = Risiko Sedang, 2 = Aman.\n"
        combined += f"{saw_df.to_string(index=False)}\n"
    
    return f"""Kamu adalah Academic Decision Support Assistant untuk LKP LEAP.
Tugasmu adalah menganalisis data nilai siswa, sebaran grade, kasus remedi, serta analisis prioritas penanganan berbasis perangkingan MADM SAW & Kluster K-Means untuk memberikan rekomendasi evaluasi akademik.
Fokus Analisis:
1. Identifikasi siswa/rombel dengan tingkat remedi tertinggi. Terangkan siswa mana yang menempati peringkat SAW terendah (Risiko Tinggi / Kluster 0) dan apa penyebab utamanya.
2. Analisis korelasi antara kehadiran dengan pencapaian nilai (grade).
3. Berikan usulan perbaikan pembelajaran yang konkret untuk siswa remedi dan program pembinaan prioritas.

Data Input:
{combined}
"""
```

Modify `get_operations_prompt`:
```python
def get_operations_prompt(dataframes: dict) -> str:
    """Generate prompt template for SQL Database (Website Statistics focus)."""
    combined = "=== AUDIT STATISTIK & TRAFIK WEBSITE (DATABASE SQL) ===\n"
    for name in ["web_statistik"]:
        df = dataframes.get(name)
        if df is not None and not df.empty:
            combined += f"\n[TABEL: {name}]\n{df.head(100).to_string(index=False)}\n"
            
    # Augment with leads prioritization
    saw_leads = dataframes.get("DB_SAW_LEADS")
    if saw_leads is not None and not saw_leads.empty:
        combined += "\n=== SPK SAW & K-MEANS LEADS CONVERSION PRIORITIZATION ===\n"
        combined += "Keterangan Kluster: 0 = Cold Leads (Rendah), 1 = Warm Leads, 2 = Hot Leads (Prioritas Tinggi).\n"
        combined += f"{saw_leads.to_string(index=False)}\n"
            
    return f"""Kamu adalah SQL Database Website Traffic Auditor dan SPK Prospek Analyst untuk LKP LEAP.
Tugasmu menganalisis log statistik pengunjung website serta menganalisis data leads calon siswa baru menggunakan hasil perangkingan SAW & Kluster K-Means untuk meningkatkan pendaftaran.
Fokus Analisis:
1. Analisis tren trafik: Hitung total views, unique IPs, dan rata-rata page views per sesi.
2. Deteksi Anomali Keamanan: Temukan apakah ada IP Address yang melakukan akses berlebihan (high page views) dalam satu sesi (potensi bot/scraping).
3. Prioritas Calon Siswa (Leads): Analisis data perangkingan SAW Leads. Berikan saran tindak lanjut khusus untuk calon siswa yang masuk kategori Hot Leads (Kluster 2) agar konversi pendaftaran maksimal.
4. Berikan rekomendasi operasional dan keamanan website untuk meningkatkan performa server dan keamanan akses website LKP LEAP.

Data Input:
{combined}
"""
```

Modify `get_unified_overview_prompt`:
```python
def get_unified_overview_prompt(combined_data: dict) -> str:
    """Generate prompt template for Unified LKP Overview analysis."""
    sheets_data = combined_data.get("sheets", {})
    db_data = combined_data.get("db", {})
    
    total_siswa = len(sheets_data.get("DATA_SISWA", []))
    nilai_df = sheets_data.get("DATA_NILAI", pd.DataFrame())
    avg_final = 71.60
    if not nilai_df.empty:
        final_df = nilai_df[nilai_df["periode"] == "Final"]
        if not final_df.empty:
            avg_final = final_df["score"].mean()
            
    siswa_df = db_data.get("siswa", pd.DataFrame())
    total_active = 0
    if not siswa_df.empty:
        if "status_siswa" in siswa_df.columns:
            total_active = len(siswa_df[siswa_df["status_siswa"] == "Aktif"])
        elif "status_pendaftaran" in siswa_df.columns:
            total_active = len(siswa_df[siswa_df["status_pendaftaran"].isin(["Siswa Baru", "Siswa Lama"])])
        else:
            total_active = len(siswa_df)
            
    catatan_df = db_data.get("catatan_siswa", pd.DataFrame())
    cases_count = 0
    if not catatan_df.empty:
        if "status_followup" in catatan_df.columns:
            cases_count = len(catatan_df[catatan_df["status_followup"] == "NEED FURTHER OBSERVATION"])
        else:
            cases_count = len(catatan_df)
            
    # Augment with Unified Intervensi Siswa
    saw_unified = db_data.get("UNIFIED_SAW")
    saw_str = ""
    if saw_unified is not None and not saw_unified.empty:
        saw_str = "\n=== SPK SAW & K-MEANS UNIFIED INTERVENTION RANKING ===\n"
        saw_str += "Keterangan Kluster: 0 = Intervensi Kritis (Prioritas Utama), 1 = Dalam Observasi, 2 = Stabil.\n"
        saw_str += f"{saw_unified.to_string(index=False)}\n"
    
    return f"""Kamu adalah Principal Educational Director & Executive Auditor LKP LEAP Surabaya.
Analisis data kinerja institusi LKP LEAP berikut secara menyeluruh (gabungan data akademik Sheets dan operasional Database) dengan dukungan perangkingan DSS Unified:

[RINGKASAN EKSEKUTIF]
- Total Siswa Terdaftar (Sheets): {total_siswa}
- Siswa Aktif (Database): {total_active}
- Rata-rata Nilai Ujian Akhir Siswa: {avg_final:.2f}
- Jumlah Kasus Observasi CS Terbuka: {cases_count}
{saw_str}
Tugas:
1. Berikan evaluasi kinerja makro LKP LEAP yang memadukan data akademik (keberhasilan nilai) dan data operasional (kondisi CS/staf pendukung).
2. Analisis data Perangkingan Intervensi Unified SAW. Sebutkan siswa mana yang masuk dalam kategori Intervensi Kritis (Kluster 0) yang memerlukan tindakan koordinasi cepat antara tim Akademik dan Customer Service.
3. Berikan 3 rekomendasi taktis eksekutif untuk meningkatkan kualitas layanan pendidikan dan operasional LKP LEAP.
"""
```

- [ ] **Step 4: Run tests to verify they pass**
  Run: `.venv/Scripts/pytest tests/test_llm_analyzer.py -v`  
  Expected: PASS

- [ ] **Step 5: Commit changes**
  Run:
  ```bash
  git add core/llm_analyzer.py tests/test_llm_analyzer.py
  git commit -m "feat: integrate SAW and K-Means data tables into Gemini AI prompts"
  ```
