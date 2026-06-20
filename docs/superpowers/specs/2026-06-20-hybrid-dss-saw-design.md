# EduDecision AI V2 - Hybrid DSS (SAW & K-Means Clustering) Design Specification

**Document Date:** June 20, 2026  
**Status:** Approved for Implementation Planning  
**Branch:** `feature/dss-hybrid-mariadb-gsheets`  
**Authors:** Gemini & Chotibul Umam Hanif  

---

## 1. Executive Summary & Context

To meet academic Decision Support System (SPK/DSS) syllabus standards, this specification details the design for updating the **EduDecision AI V2 Hybrid DSS** architecture. We are introducing a hybrid mathematical engine combining Multi-Attribute Decision Making (MADM) using the **Simple Additive Weighting (SAW)** method with unsupervised Machine Learning (ML) using **K-Means Clustering** in the backend. 

To handle distinct data flows and structural formats, this hybrid engine is deployed in **three isolated modules**:
1. **Sheets Module (Academic)**: Evaluates active student academic performance and attendance.
2. **Database SQL Module (Leads Prioritization)**: Ranks prospective student leads in the sales pipeline.
3. **Unified Module (Executive Overview)**: Integrates Sheets and SQL databases to identify critical student intervention candidates.

---

## 2. Mathematical Framework & Algorithms

The system uses a sequential hybrid process: **Objective Weighting / Fallback** $\rightarrow$ **SAW Calculation** $\rightarrow$ **K-Means Clustering** $\rightarrow$ **Cognitive LLM Explainability**.

```
+------------------------------------+
|  Step 1: Compute Feature weights   | (Dynamic correlation or fallback weights)
+-----------------+------------------+
                  |
                  v
+-----------------+------------------+
|    Step 2: Normalized Matrix R     | (Linear Max-Min normalization)
+-----------------+------------------+
                  |
                  v
+-----------------+------------------+
|   Step 3: SAW Preference (Vi)    | (Additive aggregation)
+-----------------+------------------+
                  |
                  v
+-----------------+------------------+
|   Step 4: K-Means Clustering     | (Machine Learning Risk Segmentation)
+-----------------+------------------+
                  |
                  v
+-----------------+------------------+
|   Step 5: Cognitive LLM Output   | (Gemini AI interpretation & strategy)
+-----------------+------------------+
```

### 2.1 Criteria Weighting ($W_j$)
To dynamically value criteria importance, we calculate the absolute Pearson/Point-Biserial correlation coefficient ($r_j$) between each active student metric and historical student churn/dropout (i.e., whether the student is listed in `DATA_KELUAR`):
$$w'_j = |r_j|$$
We normalize the weights to sum to 1.0:
$$w_j = \frac{w'_j}{\sum_{k=1}^{n} w'_k}$$

**Fallback Protocol:** If the historical dataset lacks sufficient variance or is too small, correlation coefficients might output `NaN`. In such cases, the system falls back to predefined expert-assigned weights for each module.

### 2.2 SAW Matrix Normalization ($r_{ij}$)
For any alternative $i$ and criterion $j$:
* **Benefit Criteria** (Higher is better):
  $$r_{ij} = \frac{x_{ij}}{\max_k(x_{kj})}$$
* **Cost Criteria** (Lower is better):
  $$r_{ij} = \frac{\min_k(x_{kj}) + 1}{x_{ij} + 1}$$
  *Note: $+1$ is a safety constant preventing division by zero when minimum metric is 0.*

### 2.3 Preference Score ($V_i$) & Clustering
The preference score is calculated as:
$$V_i = \sum_{j=1}^{m} w_j \cdot r_{ij}$$
This yields $V_i \in [0, 1]$. We then apply **K-Means Clustering ($K=3$)** using scikit-learn on the features `[V_i, Main_Criterion_1, Main_Criterion_2]` to dynamically segment alternatives into three clusters representing:
1. **Cluster 0: High Risk / High Urgency (Risiko Tinggi / Prioritas Utama)**
2. **Cluster 1: Medium Risk / Medium Urgency (Risiko Sedang)**
3. **Cluster 2: Safe / Stable / Low Risk (Aman / Prioritas Rendah)**

---

## 3. Modular System Architecture

### 3.1 Backend Utility Functions (`core/data_pipeline.py`)

A general SAW utility and dynamic clustering function will be added:

```python
def calculate_saw(df: pd.DataFrame, criteria: list, weights: dict, types: dict) -> pd.DataFrame:
    """
    Computes SAW preference score and ranks alternatives.
    Returns the DataFrame augmented with 'saw_score' and 'saw_rank'.
    """
```

```python
def apply_kmeans_risk(df: pd.DataFrame, features: list, n_clusters: int = 3) -> pd.DataFrame:
    """
    Applies scikit-learn K-Means clustering to partition entries.
    Auto-sorts cluster labels so that cluster 0 is always the highest risk/priority 
    and cluster 2 is the lowest risk/safe based on mean SAW scores.
    """
```

### 3.2 Sku-Specific SAW Implementations

#### 1. Sheets Module (Siswa Akademik)
* **Input Data**: `DATA_SISWA`, `DATA_NILAI`, `DATA_ABSENSI`.
* **Kriteria & Bobot (Fallback)**:
  * $C_1$: Rata-rata Nilai (`score`) $\rightarrow$ Benefit (Bobot: 0.40)
  * $C_2$: Persentase Kehadiran $\rightarrow$ Benefit (Bobot: 0.30)
  * $C_3$: Rasio Ujian Tuntas (Nilai $> 70$) $\rightarrow$ Benefit (Bobot: 0.20)
  * $C_4$: Frekuensi Terlambat/Alfa $\rightarrow$ Cost (Bobot: 0.10)
* **K-Means Features**: `[saw_score, score, attendance_rate]`
* **ML Interpretation**: Auto-categorizes active students into High Risk, Medium Risk, and Safe clusters.

#### 2. Database SQL Module (Prioritas Calon Siswa / Leads)
* **Input Data**: `calon_siswa`, `calon_siswa_bayar`, `calon_siswa_fo_detail`.
* **Kriteria & Bobot (Fallback)**:
  * $C_1$: Jumlah Bayar (`jumlah_bayar`) $\rightarrow$ Benefit (Bobot: 0.40)
  * $C_2$: Kelengkapan Status FO (`fo_status` == "Lengkap" $\rightarrow 1.0$, else $\rightarrow 0.0$) $\rightarrow$ Benefit (Bobot: 0.30)
  * $C_3$: Kecepatan Konfirmasi Pembayaran (Hari dari terdaftar ke terbayar) $\rightarrow$ Cost (Bobot: 0.20)
  * $C_4$: Panjang Catatan Awal FO (Kuantitas detail minat) $\rightarrow$ Benefit (Bobot: 0.10)
* **K-Means Features**: `[saw_score, jumlah_bayar, is_fo_lengkap]`
* **ML Interpretation**: Clusters leads into Hot Leads, Warm Leads, and Cold Leads.

#### 3. Unified Module (Intervensi Siswa Terpadu)
* **Input Data**: Sheets (`DATA_SISWA`, `DATA_NILAI`) joined with SQL Database (`catatan_siswa`).
* **Kriteria & Bobot (Fallback)**:
  * $C_1$: Rata-rata Nilai Akademik (Sheets) $\rightarrow$ Benefit (Bobot: 0.40)
  * $C_2$: Persentase Kehadiran (Sheets) $\rightarrow$ Benefit (Bobot: 0.30)
  * $C_3$: Kebutuhan Tindak Lanjut CS (`status_followup` == "NEED FURTHER OBSERVATION" $\rightarrow 1.0$, else $\rightarrow 0.0$) $\rightarrow$ Cost (Bobot: 0.20)
  * $C_4$: Jumlah Kasus CS Terbuka $\rightarrow$ Cost (Bobot: 0.10)
* **K-Means Features**: `[saw_score, score, has_open_cases]`
* **ML Interpretation**: Segments students into Critical Intervention, Under Observation, and Stable clusters.

---

## 4. LLM Cognitive Integration & Prompts (`core/llm_analyzer.py`)

The prompts for the Gemini engines will be modified to include the quantitative SAW and K-Means segmentation results:

### 4.1 Academic & Predictor Analysis
The prompt generators `get_academic_prompt` and `get_student_predictor_prompt` will receive a markdown-formatted table of the top 10 candidates in the **High Risk (Cluster 0)** category. Gemini will analyze the reasons for their scores and design custom pedagogical intervention strategies.

### 4.2 Operations & Leads Audit
`get_operations_prompt` will include the leads ranking table to guide Front Office strategies on optimizing Hot Leads conversions.

### 4.3 Unified Overview
`get_unified_overview_prompt` will ingest the top critical combined cases, mapping out organizational coordination tasks between the academic tutoring staff and the CS department.

---

## 5. UI/UX Streamlit Integration

The Calculated SAW rankings and clusters will be displayed in `app.py`:
1. **Interactive Data Tables**: Under the respective tabs, ranked tables will display names, SAW scores, and their ML risk clusters with color-coded status badges (e.g., Red for High Risk/Hot, Orange for Medium Risk/Warm, Green for Safe/Cold).
2. **Dynamic Triggering**: Standard data loaders will trigger the SAW + K-Means calculations automatically, caching the result in Streamlit's session state.

---

## 6. Verification and Testing Plan

1. **Unit Testing (`tests/test_data_pipeline.py`)**:
   * Create tests to verify the correctness of the mathematical normalization functions.
   * Verify that SAW calculations return correct priority ordering on mock datasets.
   * Verify K-Means partitions the datasets into exactly 3 clusters, and auto-sorting works correctly (Cluster 0 always contains the lowest average SAW scores).
2. **API Stability**:
   * Ensure that even if the scikit-learn KMeans fit fails (e.g., too few samples), it catches the exception and falls back to sorting by SAW score alone, returning a mock clustering schema. This guarantees 100% dashboard uptime.
3. **Execution Safety**:
   * All computations are read-only and memory-bounded (under 8GB baseline). No database write operations are performed.
