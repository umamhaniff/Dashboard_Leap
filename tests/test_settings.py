from config.settings import get_config

def test_settings_load():
    config = get_config()
    assert "DATA_SISWA" in config["sheet_names"]
    assert "DATA_KELUAR" in config["sheet_names"]
    assert "mariadb" in config
    assert config["mariadb"]["port"] in [3077, 3307]
