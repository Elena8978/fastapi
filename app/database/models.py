from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.db import Base

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    dislikes = Column(Integer, default=0, nullable=False)
    publish_year = Column(Integer, nullable=False)
    genre = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Film(id={self.id}, title='{self.title}', genre='{self.genre}')>"