import pytest
from app.core.database import get_db
from sqlalchemy.orm import Session

def test_get_db_yields_session():
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    try:
        next(gen)
    except StopIteration:
        pass
    else:
        assert False, "get_db should stop after yielding one session"
