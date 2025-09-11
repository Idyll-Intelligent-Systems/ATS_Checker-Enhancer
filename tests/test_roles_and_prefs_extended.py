from src.core.config import (
    add_user_role,
    get_user_roles,
    user_has_role,
    set_user_scoped_preference,
    get_user_scoped_preference,
)


def test_role_fallback_default():
    roles = get_user_roles('nonexistent-user-xyz')
    assert roles == ['user']


def test_add_multiple_roles():
    uid = 'multi-role-user'
    add_user_role(uid, 'admin')
    add_user_role(uid, 'auditor')
    roles = get_user_roles(uid)
    # Default 'user' role may not auto-append until first retrieval; ensure fallback logic works separately
    assert 'admin' in roles and 'auditor' in roles


def test_user_scoped_preference_isolated():
    u1, u2 = 'userA', 'userB'
    set_user_scoped_preference(u1, 'color', 'red')
    set_user_scoped_preference(u2, 'color', 'blue')
    assert get_user_scoped_preference(u1, 'color') == 'red'
    assert get_user_scoped_preference(u2, 'color') == 'blue'
