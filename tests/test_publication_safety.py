"""CI guardrails for the standalone public portfolio demo."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FILES = ["app.py", "run.py", "README.md", "static/index.html"]
# Catches references to employer brands or historical internal table identifiers.
FORBIDDEN = [r"(?i)anytime", r"(?i)d-mobility", r"(?i)userwcustomerdata",
             r"(?i)amountfromcardinkops", r"(?i)rentstartdatetime"]


def test_no_employer_specific_identifiers():
    for path in FILES:
        source = (ROOT / path).read_text(encoding="utf-8")
        for pattern in FORBIDDEN:
            assert re.search(pattern, source) is None, f"Sensitive identifier in {path}: {pattern}"


def test_demo_has_no_network_credentials_configuration():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    for name in ("DB_PASSWORD", "OPENAI_API_KEY", "DB_HOST", "GOOGLE_APPLICATION_CREDENTIALS"):
        assert name not in source
