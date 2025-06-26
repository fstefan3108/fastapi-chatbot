from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# reading db url from config.settings #
sql_alchemy_url = settings.database_url

# engine creation #
engine = create_engine(sql_alchemy_url)

# declaring Base that models will inherit #
Base = declarative_base()

