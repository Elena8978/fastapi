from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

ALLOWED_GENRES = {"ужасы", "приключение", "драма", "боевик", "комедия", "фантастика"}

# Базовые схемы
class FilmBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    likes: int = Field(0, ge=0)
    dislikes: int = Field(0, ge=0)
    publish_year: int = Field(..., ge=1888)
    genre: str

    @field_validator("title")
    @classmethod
    def check_title_not_only_spaces(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Название не должно состоять только из пробелов.")
        return v

    @field_validator("genre")
    @classmethod
    def check_genre_allowed(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in ALLOWED_GENRES:
            raise ValueError(f"Жанр должен быть одним из: {', '.join(ALLOWED_GENRES)}")
        return v_clean


class FilmCreate(FilmBase):
    pass

class FilmUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    likes: Optional[int] = Field(None, ge=0)
    dislikes: Optional[int] = Field(None, ge=0)
    publish_year: Optional[int] = Field(None, ge=1888)
    genre: Optional[str] = None

    @field_validator("title", mode="before")
    @classmethod
    def check_title_before(cls, v):
        if isinstance(v, str) and v.strip() == "":
            raise ValueError("Название не должно состоять только из пробелов.")
        return v

    @field_validator("genre", mode="before")
    @classmethod
    def check_genre_before(cls, v):
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean not in ALLOWED_GENRES:
                raise ValueError(f"Жанр должен быть одним из: {', '.join(ALLOWED_GENRES)}")
            return v_clean
        return v

class FilmResponse(FilmBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  