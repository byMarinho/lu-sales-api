from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Garante que as transações sejam propagadas corretamente.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit automático se não houver erros
    except:
        db.rollback()  # Rollback em caso de erro
        raise
    finally:
        db.close()
