from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
templates.env.cache = None 

api_router = APIRouter(prefix="/api", tags=["API"])

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


@api_router.get("/films")
async def get_films():
    return films_db

@api_router.get("/films/{film_id}")
async def get_film(film_id: int):
    film = get_film_by_id(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return film

@api_router.post("/films")
async def create_film(film: FilmCreate):
    new_id = max((f.id for f in films_db), default=0) + 1
    new_film = FilmModel(id=new_id, **film.model_dump())
    films_db.append(new_film)
    return new_film

@api_router.put("/films/{film_id}")
async def update_film(film_id: int, film_update: FilmUpdate):
    film = get_film_by_id(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")

    update_data = film_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(film, key, value)
    # id менять не нужно
    return film

@api_router.delete("/films/{film_id}")
async def delete_film(film_id: int):
    global films_db
    film = get_film_by_id(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    films_db = [f for f in films_db if f.id != film_id]
    return {"detail": "Фильм удалён"}

app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    total_count = len(films_db)

    most_liked_dict = None
    most_disliked_dict = None

    if films_db:
        most_liked = max(films_db, key=lambda f: f.likes)
        most_disliked = min(films_db, key=lambda f: f.dislikes)
        # Превращаем Pydantic-модели в обычные dict
        most_liked_dict = most_liked.model_dump()
        most_disliked_dict = most_disliked.model_dump()

    context = {
        "request": request,
        "total_count": total_count,
        "most_liked": most_liked_dict,
        "most_disliked": most_disliked_dict,
    }

    return templates.TemplateResponse("index.html", context)
