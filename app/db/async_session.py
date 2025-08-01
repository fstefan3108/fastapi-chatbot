from sqlalchemy.ext.asyncio import async_sessionmaker
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(settings.database_url_async)
AsyncSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)