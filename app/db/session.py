from sqlalchemy.orm import sessionmaker
from app.db.base import engine

# session creation #
LocalSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)