from bot.access import is_allowed


def test_is_allowed_for_listed_user(monkeypatch):
    monkeypatch.setenv("ALLOWED_USER_IDS", "111,222")
    assert is_allowed(111)
    assert is_allowed(222)


def test_is_allowed_rejects_unlisted_user(monkeypatch):
    monkeypatch.setenv("ALLOWED_USER_IDS", "111,222")
    assert not is_allowed(333)


def test_is_allowed_rejects_everyone_when_unset(monkeypatch):
    monkeypatch.delenv("ALLOWED_USER_IDS", raising=False)
    assert not is_allowed(111)


def test_is_allowed_ignores_stray_whitespace_and_empty_entries(monkeypatch):
    monkeypatch.setenv("ALLOWED_USER_IDS", " 111, ,222 ")
    assert is_allowed(111)
    assert is_allowed(222)
