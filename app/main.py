from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

app = FastAPI()

ALLOWED_GENRES = {"ужасы", "приключение", "драма", "боевик", "комедия", "фантастика"}


class FilmModel(BaseModel):
    id: int
    title: str
    likes: int
    dislikes: int
    publish_year: int
    genre: str


class FilmCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    likes: int = 0
    dislikes: int = 0
    publish_year: int
    genre: str

    @field_validator("title")
    @classmethod
    def check_title_not_only_spaces(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Название не должно состоять только из пробелов.")
        return v

    @field_validator("likes", "dislikes")
    @classmethod
    def check_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Количество лайков/дизлайков не может быть меньше нуля.")
        return v

    @field_validator("publish_year")
    @classmethod
    def check_year_min(cls, v: int) -> int:
        if v < 1888:
            raise ValueError("Год выпуска должен быть не раньше 1888.")
        return v

    @field_validator("genre")
    @classmethod
    def check_genre_allowed(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in ALLOWED_GENRES:
            raise ValueError(f"Жанр должен быть одним из: {', '.join(ALLOWED_GENRES)}")
        return v_clean


class FilmUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    publish_year: Optional[int] = None
    genre: Optional[str] = None


    @field_validator("title", mode="before")
    @classmethod
    def check_title_before(cls, v):
        if isinstance(v, str) and v.strip() == "":
            raise ValueError("Название не должно состоять только из пробелов.")
        return v

    @field_validator("likes", "dislikes", mode="before")
    @classmethod
    def check_likes_dislikes_before(cls, v):
        if isinstance(v, int) and v < 0:
            raise ValueError("Значение не может быть меньше нуля.")
        return v

    @field_validator("publish_year", mode="before")
    @classmethod
    def check_year_before(cls, v):
        if isinstance(v, int) and v < 1888:
            raise ValueError("Год выпуска должен быть не раньше 1888.")
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


films_db: List[FilmModel] = [
    FilmModel(id=1, title="Inception", likes=120, dislikes=15, publish_year=2010, genre="фантастика"),
    FilmModel(id=2, title="The Dark Knight", likes=250, dislikes=20, publish_year=2008, genre="боевик"),
    FilmModel(id=3, title="Interstellar", likes=180, dislikes=10, publish_year=2014, genre="фантастика"),
]


def get_film_by_id(film_id: int) -> Optional[FilmModel]:
    for film in films_db:
        if film.id == film_id:
            return film
    return None


@app.get("/films", response_model=List[FilmModel])
def get_films():
    return films_db


@app.get("/film/{id}", response_model=FilmModel)
def get_film(id: int):
    film = get_film_by_id(id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return film


@app.post("/film", response_model=FilmModel, status_code=201)
def create_film(film: FilmCreate):
    new_id = 1
    if films_db:
        new_id = max(f.id for f in films_db) + 1

    
    if get_film_by_id(new_id):
        raise HTTPException(status_code=500, detail="Сгенерированный ID уже существует.")

    new_film = FilmModel(id=new_id, **film.model_dump())
    films_db.append(new_film)
    return new_film


@app.patch("/film/{id}", response_model=FilmModel)
def update_film(id: int, film_update: FilmUpdate):
    film = get_film_by_id(id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")

    update_data = film_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(film, key, value)

    return film


@app.delete("/film/{id}", status_code=204)
def delete_film(id: int):
    global films_db
    film = get_film_by_id(id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    films_db = [f for f in films_db if f.id != id]
    return None
