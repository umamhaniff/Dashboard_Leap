from unittest.mock import MagicMock, patch
from core.llm_analyzer import (
    get_academic_prompt, get_operations_prompt, get_unified_overview_prompt,
    get_academic_performance_prompt, get_attendance_prompt, get_student_predictor_prompt,
    get_marketing_prompt, get_academic_compliance_prompt, get_hr_attendance_prompt, get_revenue_pipeline_prompt,
    analyze_feature
)

def test_prompts():
    assert "ACADEMIC" in get_academic_prompt({})
    assert "SISWA" in get_operations_prompt({})
    assert "Academic" in get_academic_performance_prompt({})
    assert "absensi" in get_attendance_prompt({})
    assert "siswa" in get_student_predictor_prompt({}).lower()
    assert "rekrutmen" in get_marketing_prompt({}).lower()
    assert "kepatuhan" in get_academic_compliance_prompt({}).lower()
    assert "karyawan" in get_hr_attendance_prompt({}).lower()
    assert "pendapatan" in get_revenue_pipeline_prompt({}).lower()


@patch("core.llm_analyzer.get_api_key", return_value="fake_api_key")
@patch("core.llm_analyzer.genai.Client")
def test_analyze_feature_failover_first_model_429(mock_client_class, mock_get_key):
    """Test failover ketika model pertama limit (429) tapi model kedua sukses."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = "Hasil analisis dari model kedua"
    
    def generate_content_side_effect(model, contents, config=None):
        if model == 'models/gemini-3.1-flash-lite-preview':
            raise Exception("429 Resource Exhausted / Rate Limit Exceeded")
        return mock_response

    mock_client.models.generate_content.side_effect = generate_content_side_effect
    
    result = analyze_feature({}, "academic_perf")
    
    assert "models/gemini-3-flash-preview" in result
    assert "Hasil analisis dari model kedua" in result
    assert mock_client.models.generate_content.call_count == 2


@patch("core.llm_analyzer.get_api_key", return_value="fake_api_key")
@patch("core.llm_analyzer.genai.Client")
def test_analyze_feature_failover_all_models_429(mock_client_class, mock_get_key):
    """Test failover ketika semua model limit (429)."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_client.models.generate_content.side_effect = Exception("429 Resource Exhausted")
    
    result = analyze_feature({}, "academic_perf")
    
    assert "ERROR: Semua model di list sedang sibuk. Silakan tunggu 1 menit." in result
    # Harus mencoba semua model (total ada 9 model di list)
    assert mock_client.models.generate_content.call_count == 9

def test_prompts_with_saw_data():
    import pandas as pd
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


