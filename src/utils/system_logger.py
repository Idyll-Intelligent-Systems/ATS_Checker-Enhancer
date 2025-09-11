"""Central ATS System Logging Utilities
Structured, color-coded logging for API and function instrumentation.

Log Formats:
API:
  ATS-SYSTEM-LOG | <LogType> | <Method> | <API> | <Response Code> | <Latency ms> | <Error Description / Remark> | <Marker>
Function:
  ATS-SYSTEM-LOG | <LogType> | <Function> | <Parameters with type> | <Start Time> | <End Time> | <Latency ms> | <Caller> | <Called> | <Response Type> | <Success Remarks> | <Error Description> | <Marker>

Log Types: INFO, DEBUG, REMARK, METRIC, ALERT, ERROR
Markers: ✔ success (green), ⚠ warning/alert (yellow), ✖ failure (red)
"""
from __future__ import annotations
import logging
import sys
import functools
import inspect
import asyncio
from datetime import datetime
from time import perf_counter
from typing import Any, Callable, Dict

# ANSI Colors
RESET = "\033[0m"
COLORS: Dict[str, str] = {
    "INFO": "\033[32m",      # Green
    "DEBUG": "\033[36m",     # Cyan
    "REMARK": "\033[35m",    # Magenta
    "METRIC": "\033[94m",    # Bright Blue
    "ALERT": "\033[33m",     # Yellow/Orange
    "ERROR": "\033[31m",     # Red
}
MARKERS = {
    "success": "\033[32m✔\033[0m",
    "alert": "\033[33m⚠\033[0m",
    "error": "\033[31m✖\033[0m",
}

LOGGER_NAME = "ats.system"
_base_logger = logging.getLogger(LOGGER_NAME)


def init_system_logger(level: int = logging.INFO, enable_colors: bool | None = None) -> None:
    """Initialize system logger with color support once.

    On Windows terminals, attempts to enable ANSI colors via colorama if present.
    """
    global _base_logger
    if enable_colors is None:
        enable_colors = sys.stdout.isatty()
    if _base_logger.handlers:
        return  # Already initialized
    _base_logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)

    # Best-effort enable ANSI colors on Windows if possible
    if enable_colors and sys.platform.startswith("win"):
        try:  # optional dependency
            import colorama  # type: ignore
            colorama.just_fix_windows_console()
        except Exception:  # pragma: no cover - optional improvement only
            pass

    class _PassthroughFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:  # noqa: D401
            msg = record.getMessage()
            if not enable_colors:
                # Strip ANSI if disabled
                import re as _re
                msg = _re.sub(r"\x1b\[[0-9;]*m", "", msg)
            return msg

    handler.setFormatter(_PassthroughFormatter())
    _base_logger.addHandler(handler)
    _base_logger.propagate = False


def _colorize(log_type: str, text: str) -> str:
    color = COLORS.get(log_type.upper(), "")
    return f"{color}{text}{RESET}" if color else text


def _select_marker(log_type: str, status_code: int | None = None, error: str | None = None) -> str:
    if error or log_type.upper() == "ERROR" or (status_code and status_code >= 500):
        return MARKERS["error"]
    if log_type.upper() == "ALERT" or (status_code and 400 <= status_code < 500):
        return MARKERS["alert"]
    return MARKERS["success"]


def log_api_event(
    log_type: str,
    method: str,
    api: str,
    status_code: int,
    latency_ms: float,
    error: str | None = None,
    remark: str | None = None,
) -> None:
    """Emit a structured API log line."""
    log_type_up = log_type.upper()
    marker = _select_marker(log_type_up, status_code=status_code, error=error)
    desc = error or remark or "-"
    line = " | ".join([
        "ATS-SYSTEM-LOG",
        _colorize(log_type_up, log_type_up),
        method.upper(),
        api,
        str(status_code),
        f"{latency_ms:.2f} ms",
        desc,
        marker,
    ])
    _base_logger.log(_map_level(log_type_up), line)


def log_function_event(
    log_type: str,
    function: str,
    params: str,
    start_time: datetime,
    end_time: datetime,
    latency_ms: float,
    caller: str,
    called: str,
    response_type: str,
    success_remark: str | None,
    error: str | None,
) -> None:
    log_type_up = log_type.upper()
    marker = _select_marker(log_type_up, error=error)
    line = " | ".join([
        "ATS-SYSTEM-LOG",
        _colorize(log_type_up, log_type_up),
        function,
        params or "-",
        start_time.isoformat(timespec="milliseconds"),
        end_time.isoformat(timespec="milliseconds"),
        f"{latency_ms:.2f} ms",
        caller,
        called,
        response_type,
        success_remark or ("-" if error else "OK"),
        error or "-",
        marker,
    ])
    _base_logger.log(_map_level(log_type_up), line)


def _map_level(log_type: str) -> int:
    return {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "REMARK": logging.INFO,
        "METRIC": logging.INFO,
        "ALERT": logging.WARNING,
        "ERROR": logging.ERROR,
    }.get(log_type, logging.INFO)


def _format_params(bound_args: inspect.BoundArguments) -> str:
    parts = []
    for name, value in bound_args.arguments.items():
        try:
            rep = repr(value)
            if len(rep) > 120:
                rep = rep[:117] + "..."
        except Exception:  # pragma: no cover
            rep = "<unrepr>"
        parts.append(f"{name}={rep}({type(value).__name__})")
    joined = ", ".join(parts)
    return joined if len(joined) <= 400 else joined[:397] + "..."


def log_function(log_type: str = "DEBUG", success_remark: str | None = "SUCCESS") -> Callable:
    """Decorator to log function start/end with latency & outcome.
    Supports sync & async functions.
    """
    def decorator(fn: Callable) -> Callable:
        is_coro = asyncio.iscoroutinefunction(fn)

        @functools.wraps(fn)
        def _sync_wrapper(*args, **kwargs):
            start_perf = perf_counter()
            start_dt = datetime.utcnow()
            sig = inspect.signature(fn)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = _format_params(bound)
            caller_fn = inspect.stack()[1].function
            called = f"{fn.__module__}.{fn.__name__}"
            try:
                result = fn(*args, **kwargs)
                end_dt = datetime.utcnow()
                latency = (perf_counter() - start_perf) * 1000
                log_function_event(log_type, fn.__name__, params, start_dt, end_dt, latency, caller_fn, called, type(result).__name__, success_remark, None)
                return result
            except Exception as e:  # noqa: BLE001
                end_dt = datetime.utcnow()
                latency = (perf_counter() - start_perf) * 1000
                log_function_event("ERROR", fn.__name__, params, start_dt, end_dt, latency, caller_fn, called, "-", None, str(e))
                raise

        @functools.wraps(fn)
        async def _async_wrapper(*args, **kwargs):
            start_perf = perf_counter()
            start_dt = datetime.utcnow()
            sig = inspect.signature(fn)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = _format_params(bound)
            caller_fn = inspect.stack()[1].function
            called = f"{fn.__module__}.{fn.__name__}"
            try:
                result = await fn(*args, **kwargs)
                end_dt = datetime.utcnow()
                latency = (perf_counter() - start_perf) * 1000
                log_function_event(log_type, fn.__name__, params, start_dt, end_dt, latency, caller_fn, called, type(result).__name__, success_remark, None)
                return result
            except Exception as e:  # noqa: BLE001
                end_dt = datetime.utcnow()
                latency = (perf_counter() - start_perf) * 1000
                log_function_event("ERROR", fn.__name__, params, start_dt, end_dt, latency, caller_fn, called, "-", None, str(e))
                raise

        return _async_wrapper if is_coro else _sync_wrapper

    return decorator

# Convenience alias for METRIC heavy functions
def log_metric_function(success_remark: str | None = "SUCCESS") -> Callable:
    return log_function("METRIC", success_remark)

__all__ = [
    "init_system_logger",
    "log_api_event",
    "log_function",
    "log_metric_function",
]
