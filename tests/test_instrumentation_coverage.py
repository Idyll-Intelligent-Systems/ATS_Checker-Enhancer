import re
from pathlib import Path

import pytest

SRC = Path("src")


@pytest.mark.parametrize(
    "file_rel,expected_min",
    [
        ("core/ats_analyzer.py", 5),
    ("utils/file_validator.py", 8),
        ("utils/keyword_extractor.py", 6),
        ("utils/sentiment_analyzer.py", 4),
        ("utils/text_processing.py", 6),
        ("auth/jwt_handler.py", 8),
        ("database/connection.py", 6),
        ("dashboard/pdf_export.py", 1),
    ],
)
def test_decorator_presence(file_rel, expected_min):
    path = SRC / file_rel
    assert path.exists(), f"Missing file: {file_rel}"
    text = path.read_text(encoding="utf-8")
    count = len(re.findall(r"@log_function\(", text))
    assert count >= expected_min, f"Expected at least {expected_min} @log_function in {file_rel}, found {count}"


def test_api_middleware_present():
    main_py = Path("main.py").read_text(encoding="utf-8")
    assert "@app.middleware(\"http\")" in main_py
    assert "log_api_event(" in main_py
