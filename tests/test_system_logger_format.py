import asyncio
import logging
import re
from typing import List

import pytest

# Import module to access internals for controlled setup in tests
from src.utils import system_logger as sl
from src.utils.system_logger import (
    init_system_logger,
    log_api_event,
    log_function,
)


def _reset_logger():
    # Ensure clean logger between tests
    for h in list(sl._base_logger.handlers):
        sl._base_logger.removeHandler(h)
    sl._base_logger.setLevel(logging.NOTSET)


def _split_log(line: str) -> List[str]:
    return [part.strip() for part in line.strip().split("|")]


def test_api_log_success_format(capsys):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=False)

    log_api_event(
        log_type="INFO",
        method="get",
        api="/health",
        status_code=200,
        latency_ms=12.34,
        remark="OK",
    )

    out = capsys.readouterr().out.strip()
    # Example: ATS-SYSTEM-LOG | INFO | GET | /health | 200 | 12.34 ms | OK | ✔
    parts = _split_log(out)
    assert parts[0] == "ATS-SYSTEM-LOG"
    assert parts[1] == "INFO"
    assert parts[2] == "GET"
    assert parts[3] == "/health"
    assert parts[4] == "200"
    # For API logs, latency is at index 5
    assert parts[5].endswith("ms")
    assert parts[6] == "OK"
    assert parts[7] in ("✔", "⚠", "✖")


def test_api_log_error_markers(capsys):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=False)

    # Client error
    log_api_event("ALERT", "post", "/upload", 429, 5.0, error=None, remark=None)
    out1 = capsys.readouterr().out.strip()
    parts1 = _split_log(out1)
    assert parts1[7] == "⚠"

    # Server error
    log_api_event("ERROR", "post", "/upload", 500, 5.0, error="boom")
    out2 = capsys.readouterr().out.strip()
    parts2 = _split_log(out2)
    assert parts2[7] == "✖"


def test_function_log_success_and_error_sync(capsys):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=False)

    @log_function("INFO", "OK_DONE")
    def add(a: int, b: int) -> int:
        return a + b

    @log_function("INFO")
    def fail(_: int) -> None:
        raise RuntimeError("bad")

    # Success
    assert add(2, 3) == 5
    out1 = capsys.readouterr().out.strip()
    parts = _split_log(out1)
    # ATS-SYSTEM-LOG | INFO | add | a=2(int), b=3(int) | <start> | <end> | <ms> | <caller> | <called> | int | OK_DONE | - | ✔
    assert parts[0] == "ATS-SYSTEM-LOG"
    assert parts[1] == "INFO"
    assert parts[2] == "add"
    assert "a=2(int)" in parts[3]
    assert "b=3(int)" in parts[3]
    # For function logs, latency is at index 6
    assert parts[6].endswith("ms")
    assert parts[9] in ("int", "int")
    assert parts[10] in ("OK_DONE", "SUCCESS", "OK")
    assert parts[12] in ("✔", "⚠", "✖")

    # Error path
    with pytest.raises(RuntimeError):
        fail(1)
    out2 = capsys.readouterr().out.strip()
    parts_err = _split_log(out2)
    assert parts_err[1] == "ERROR"
    assert parts_err[2] == "fail"
    assert parts_err[12] == "✖"


def test_function_log_async_success(capsys):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=False)

    @log_function("DEBUG", "ASYNC_OK")
    async def work(x: int) -> str:
        await asyncio.sleep(0)
        return str(x)

    res = asyncio.run(work(7))
    assert res == "7"
    out = capsys.readouterr().out.strip()
    parts = _split_log(out)
    assert parts[0] == "ATS-SYSTEM-LOG"
    assert parts[1] == "DEBUG"
    assert parts[2] == "work"
    assert "x=7(int)" in parts[3]
    assert parts[9] in ("str",)
    assert parts[12] in ("✔", "⚠", "✖")


def test_color_enabled_contains_ansi(capsys):
    _reset_logger()
    # Force colors enabled
    init_system_logger(level=logging.DEBUG, enable_colors=True)
    log_api_event("INFO", "get", "/ansi", 200, 1.0, remark="OK")
    out = capsys.readouterr().out
    # Expect ANSI escape sequence present
    assert "\x1b[" in out


def test_init_idempotent_does_not_duplicate(capsys):
    _reset_logger()
    init_system_logger(level=logging.DEBUG, enable_colors=False)
    # Second init should not add another handler
    init_system_logger(level=logging.DEBUG, enable_colors=False)

    log_api_event("INFO", "get", "/one", 200, 1.0, remark="OK")
    out1 = capsys.readouterr().out

    log_api_event("INFO", "get", "/two", 200, 1.0, remark="OK")
    out2 = capsys.readouterr().out

    # Each call should produce exactly one line
    assert out1.count("ATS-SYSTEM-LOG") == 1
    assert out2.count("ATS-SYSTEM-LOG") == 1
