def test_import_prompt():
    from app.prompt import SYSTEM_PROMPT
    assert "ممنوع اختراع" in SYSTEM_PROMPT
    assert "اللهجة الأردنية" in SYSTEM_PROMPT


def test_training_committee_rule_present():
    from app.prompt import SYSTEM_PROMPT
    assert "أحمد البطاينة" in SYSTEM_PROMPT
    assert "آلاء خصاونة" in SYSTEM_PROMPT
    assert "زياد اللبابنة" in SYSTEM_PROMPT


def test_answer_cleaner_removes_internal_markup():
    from app.openai_service import _clean_answer
    raw = "**نص مهم** fileciteturn0file1L1-L2"
    cleaned = _clean_answer(raw)
    assert "**" not in cleaned
    assert "filecite" not in cleaned
    assert cleaned == "نص مهم"
