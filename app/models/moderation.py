from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ModerationResult(Base):
    """
    Database model for storing moderation results.
    """
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    flagged = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
