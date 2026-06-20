from core.data_pipeline import load_mariadb_data, calculate_saw, apply_kmeans_risk
import pandas as pd

def test_load_mariadb_data():
    dfs = load_mariadb_data()
    assert "siswa" in dfs
    assert "kursus_siswa" in dfs
    assert "web_statistik" in dfs
    assert not dfs["siswa"].empty

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

def test_calculate_saw_missing_config_raises_value_error():
    import pytest
    data = pd.DataFrame([{"id": 1, "c1": 80.0}])
    criteria = ["c1"]
    
    with pytest.raises(ValueError, match="types"):
        calculate_saw(data, criteria, weights={}, types={})
        
    with pytest.raises(ValueError, match="weights"):
        calculate_saw(data, criteria, weights={}, types={"c1": "benefit"})

def test_apply_kmeans_risk_missing_saw_score_fallback():
    data = pd.DataFrame({
        "feature1": [10, 50, 95]
    })
    result = apply_kmeans_risk(data, ["feature1"], n_clusters=3)
    assert "risk_cluster" in result.columns
    assert result.loc[0, "risk_cluster"] == 0
    assert result.loc[1, "risk_cluster"] == 1
    assert result.loc[2, "risk_cluster"] == 2

def test_sku_specific_saw_kmeans():
    from core.data_pipeline import (
        calculate_sheets_saw_kmeans,
        calculate_db_saw_kmeans,
        calculate_unified_saw_kmeans
    )
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



