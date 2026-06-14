from core.llm_analyzer import (
    get_academic_prompt, get_operations_prompt,
    get_academic_performance_prompt, get_attendance_prompt, get_churn_prompt,
    get_rombel_prompt, get_cs_cases_prompt, get_remedial_audit_prompt
)

def test_prompts():
    assert "ACADEMIC" in get_academic_prompt({})
    assert "SISWA" in get_operations_prompt({})
    assert "Academic" in get_academic_performance_prompt({})
    assert "absensi" in get_attendance_prompt({})
    assert "churn" in get_churn_prompt({})
    assert "rombel" in get_rombel_prompt({})
    assert "CS" in get_cs_cases_prompt({})
    assert "remedial" in get_remedial_audit_prompt({})

