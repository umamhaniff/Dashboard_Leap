from core.llm_analyzer import get_academic_prompt, get_operations_prompt

def test_prompts():
    assert "ACADEMIC" in get_academic_prompt({})
    assert "SISWA" in get_operations_prompt({})
