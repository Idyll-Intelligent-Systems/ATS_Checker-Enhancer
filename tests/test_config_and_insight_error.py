import os
import importlib
import json
from pathlib import Path

from src.core import config as cfg
from src.core import ats_analyzer as analyzer_mod


def test_user_role_and_preferences_roundtrip(tmp_path, monkeypatch):
    # Point preferences file to temp path
    prefs_file = tmp_path / "user_prefs.json"
    monkeypatch.setattr(cfg.settings, "preferences_file", str(prefs_file))
    # Clear caches
    import importlib
    import sys
    importlib.reload(cfg)

    # Basic set/get
    cfg.set_user_preference("theme", "dark")
    assert cfg.get_user_preference("theme") == "dark"

    # User-scoped
    cfg.set_user_scoped_preference("u1", "accent", "#ff00aa")
    assert cfg.get_user_scoped_preference("u1", "accent") == "#ff00aa"

    # Roles default & add
    assert cfg.get_user_roles("uX") == [cfg.settings.default_role]
    cfg.add_user_role("u1", "admin")
    assert cfg.user_has_role("u1", "admin")
    assert cfg.require_role("u1", "admin") is True


def test_is_production_and_cors(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setattr(cfg.settings, "debug", False)
    assert cfg.is_production() is True
    origins = cfg.get_cors_origins()
    assert all(o.startswith("https://") for o in origins)


def test_insight_wrapper_error_path(monkeypatch):
    # Force model.predict to raise
    class Boom:
        def predict(self, _payload):
            raise RuntimeError("forced insight failure")

    monkeypatch.setattr(analyzer_mod.inhouse_registry, "get", lambda _k: Boom())
    a = analyzer_mod.ATSAnalyzer()
    import asyncio
    out = asyncio.run(a._get_inhouse_insights_wrapper("Short resume text"))  # noqa: SLF001
    assert out["insights"].get("error") == "forced insight failure"


def test_insight_wrapper_success_path():
    # Ensure normal path returns insights dict without error (covers return lines after payload build)
    a = analyzer_mod.ATSAnalyzer()
    import asyncio
    out = asyncio.run(a._get_inhouse_insights_wrapper("Python developer with AWS and Docker experience"))  # noqa: SLF001
    assert "insights" in out and isinstance(out["insights"], dict)
    assert "error" not in out["insights"]


def test_parse_supported_formats_variants(monkeypatch):
    # Recreate settings with string list input
    from src.core.config import Settings
    # Directly invoke validator function (method expects (cls, v) due to design)
    parsed_list = Settings.parse_supported_formats(Settings, '["pdf","docx","txt"]')  # type: ignore[arg-type]
    assert parsed_list == ["pdf","docx","txt"]
    parsed_all = Settings.parse_supported_formats(Settings, 'all')  # type: ignore[arg-type]
    assert "latex" in parsed_all and "wav" in parsed_all
    passthrough = Settings.parse_supported_formats(Settings, ["png","jpg"])  # type: ignore[arg-type]
    assert passthrough == ["png","jpg"]
    default_fallback = Settings.parse_supported_formats(Settings, 123)  # type: ignore[arg-type]
    assert default_fallback == ["pdf","docx","txt"]


def test_config_getters_and_helpers():
    from src.core import config as c
    # Database/redis getters (simple pass-through but cover lines)
    assert c.get_database_url().startswith("sqlite")
    assert ":6379" in c.get_redis_url()
    # Settings accessor
    st = c.get_settings()
    assert hasattr(st, "app_name")


def test_is_production_false_branch(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    from src.core import config as c2
    assert c2.is_production() is False
