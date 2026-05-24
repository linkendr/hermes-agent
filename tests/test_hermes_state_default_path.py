"""Regression tests for SessionDB default path isolation."""

from pathlib import Path


def test_sessiondb_default_path_resolves_hermes_home_at_construction(tmp_path, monkeypatch):
    """SessionDB() must not use an import-time DEFAULT_DB_PATH snapshot.

    Pytest sets HERMES_HOME in an autouse fixture after test modules have been
    imported. If SessionDB() reuses hermes_state.DEFAULT_DB_PATH, any earlier
    import can freeze the real ~/.hermes/state.db and gateway tests can create
    fixture sessions in the live DB.
    """
    import hermes_state

    stale_home = tmp_path / "stale-home"
    current_home = tmp_path / "current-home"
    stale_home.mkdir()
    current_home.mkdir()

    monkeypatch.setattr(hermes_state, "DEFAULT_DB_PATH", stale_home / "state.db")
    monkeypatch.setenv("HERMES_HOME", str(current_home))

    db = hermes_state.SessionDB()
    try:
        assert db.db_path == current_home / "state.db"
        assert Path(db.db_path).exists()
        assert not (stale_home / "state.db").exists()
    finally:
        db.close()
