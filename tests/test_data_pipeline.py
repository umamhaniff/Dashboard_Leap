from core.data_pipeline import load_mariadb_data

def test_load_mariadb_data():
    dfs = load_mariadb_data()
    assert "siswa" in dfs
    assert "kursus_siswa" in dfs
    assert "web_statistik" in dfs
    assert not dfs["siswa"].empty
