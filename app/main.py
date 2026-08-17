from fastapi import FastAPI, HTTPException, Request, APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database.db import engine, get_db, Base
from app.database.models import Film as FilmModel
from app.schemas.film_schemas import FilmCreate, FilmUpdate, FilmResponse
from app.crud import film_crud

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
templates.env.cache = None

api_router = APIRouter(prefix="/api", tags=["API"])


@api_router.get("/films", response_model=List[FilmResponse])
async def get_films(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    return film_crud.get_films(db, skip=skip, limit=limit)

@api_router.get("/films/{film_id}", response_model=FilmResponse)
async def get_film(film_id: int, db: Session = Depends(get_db)):
    
    film = film_crud.get_film_by_id(db, film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return film

@api_router.post("/films", response_model=FilmResponse, status_code=201)
async def create_film(film: FilmCreate, db: Session = Depends(get_db)):
    
    return film_crud.create_film(db, film)

@api_router.put("/films/{film_id}", response_model=FilmResponse)
async def update_film(film_id: int, film_update: FilmUpdate, db: Session = Depends(get_db)):
    
    updated_film = film_crud.update_film(db, film_id, film_update)
    if not updated_film:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return updated_film

@api_router.delete("/films/{film_id}")
async def delete_film(film_id: int, db: Session = Depends(get_db)):
    
    deleted = film_crud.delete_film(db, film_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return {"detail": "Фильм удалён"}

@api_router.get("/films/genres/all")
async def get_genres(db: Session = Depends(get_db)):
    return film_crud.get_all_genres(db)

@api_router.get("/films/genre/{genre}", response_model=List[FilmResponse])
async def get_films_by_genre(genre: str, db: Session = Depends(get_db)):
   return film_crud.get_films_by_genre(db, genre)

app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):

    stats = film_crud.get_film_stats(db)
    
    context = {
        "request": request,
        "total_count": stats["total_count"],
        "most_liked": stats["most_liked"],
        "most_disliked": stats["most_disliked"],
    }
    return templates.TemplateResponse("index.html", context)

@app.get("/catalog", response_class=HTMLResponse)
async def catalog(request: Request, db: Session = Depends(get_db)):
    
    films = film_crud.get_films(db)
    genres = film_crud.get_all_genres(db)
    
    context = {
        "request": request,
        "films": films,
        "genres": genres,
    }
    return templates.TemplateResponse("catalog.html", context)

@app.get("/catalog/{genre}", response_class=HTMLResponse)
async def catalog_by_genre(request: Request, genre: str, db: Session = Depends(get_db)):
    
    filtered_films = film_crud.get_films_by_genre(db, genre)
    genres = film_crud.get_all_genres(db)
    
    context = {
        "request": request,
        "films": filtered_films,
        "genres": genres,
        "current_genre": genre,
    }
    return templates.TemplateResponse("catalog.html", context)










