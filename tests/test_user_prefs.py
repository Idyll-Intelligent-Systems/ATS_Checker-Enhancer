from src.core.config import (
    load_user_preferences,
    set_user_preference,
    get_user_preference,
    set_user_scoped_preference,
    get_user_scoped_preference,
    add_user_role,
    get_user_roles,
    user_has_role,
)
import os


def test_global_preference_roundtrip(tmp_path, monkeypatch):
    # Redirect preferences file
    prefs_path = tmp_path / 'prefs.json'
    monkeypatch.setenv('PREFS_FILE_OVERRIDE', str(prefs_path))
    # Direct manipulate underlying module globals
    set_user_preference('dark_mode', True)
    assert get_user_preference('dark_mode') is True


def test_user_scoped_preferences_and_roles(tmp_path, monkeypatch):
    user_id = 'u123'
    set_user_scoped_preference(user_id, 'note', 'hello')
    assert get_user_scoped_preference(user_id, 'note') == 'hello'
    add_user_role(user_id, 'admin')
    roles = get_user_roles(user_id)
    assert 'admin' in roles
    assert user_has_role(user_id, 'admin')
