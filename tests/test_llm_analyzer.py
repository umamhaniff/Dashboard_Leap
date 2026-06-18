from core.llm_analyzer import (
    get_academic_prompt, get_operations_prompt,
    get_academic_performance_prompt, get_attendance_prompt, get_student_predictor_prompt,
    get_marketing_prompt, get_academic_compliance_prompt, get_hr_attendance_prompt, get_revenue_pipeline_prompt
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

