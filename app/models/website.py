from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base

# Website DB Model #

class Website(Base):
    __tablename__ = 'websites'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    url = Column(String)
    chunks = Column(JSONB)
    owner_id = Column(Integer, ForeignKey("users.id"))

