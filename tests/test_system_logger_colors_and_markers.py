import logging
import re

import pytest

from src.utils import system_logger as sl
from src.utils.system_logger import init_system_logger, log_api_event


def _reset_logger():
    for h in list(sl._base_logger.handlers):
        sl._base_logger.removeHandler(h)
    sl._base_logger.setLevel(logging.NOTSET)


@pytest.mark.parametrize(
    "log_type,ansi_code",
    [
        ("INFO", "[32m"),
        ("DEBUG", "[36m"),
        ("REMARK", "[35m"),
        ("METRIC", "[94m"),
        ("ALERT", "[33m"),
        ("ERROR", "[31m"),
    ],
)
def test_log_type_color_codes_in_output(capsys, log_type, ansi_code):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=True)
    log_api_event(log_type, "get", "/color", 200, 1.0, remark="OK")
    out = capsys.readouterr().out
    # Expect ANSI color sequence applied to the log type token
    assert ansi_code in out


def test_markers_for_status_and_error(capsys):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=False)

    # Success marker
    log_api_event("INFO", "get", "/ok", 200, 1.0, remark="OK")
    parts = [p.strip() for p in capsys.readouterr().out.strip().split("|")]
    assert parts[-1] == "✔"

    # Alert marker for 4xx
    log_api_event("INFO", "get", "/warn", 429, 1.0)
    parts = [p.strip() for p in capsys.readouterr().out.strip().split("|")]
    assert parts[-1] == "⚠"

    # Error marker for error text
    log_api_event("INFO", "get", "/err", 200, 1.0, error="boom")
    parts = [p.strip() for p in capsys.readouterr().out.strip().split("|")]
    assert parts[-1] == "✖"


def test_no_ansi_when_colors_disabled(capsys):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=False)
    log_api_event("INFO", "get", "/plain", 200, 1.0, remark="OK")
    out = capsys.readouterr().out
    assert "\x1b[" not in out
