"""
Unit tests for the rule-based misconception diagnostic engine.
"""

from app.intelligence.misconception_engine import MisconceptionEngine
from app.content.dsa_misconceptions import get_default_dsa_rules


def test_diagnose_off_by_one_error():
    """Verify that array length boundary mistakes are detected."""
    engine = MisconceptionEngine(rules=get_default_dsa_rules())
    buggy_code = """
    for (int i = 0; i <= arr.length; i++) {
        System.out.println(arr[i]);
    }
    """
    diagnosed = engine.diagnose(code=buggy_code)
    rule_codes = [d["rule_code"] for d in diagnosed]
    assert "DSA-ERR-OFF-BY-ONE" in rule_codes


def test_diagnose_runtime_null_pointer():
    """Verify that NullPointerException in error logs is detected."""
    engine = MisconceptionEngine(rules=get_default_dsa_rules())
    code = "current = current.next.next;"
    diagnosed = engine.diagnose(
        code=code,
        runtime_error="Exception in thread main java.lang.NullPointerException",
    )
    rule_codes = [d["rule_code"] for d in diagnosed]
    assert "DSA-ERR-NULL-DEREF" in rule_codes
