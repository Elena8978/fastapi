from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()


class FilmModel(BaseModel):
    id: int
    title: str
    likes: int
    dislikes: int
    publish_year: int
    genre: str


films = []


@app.post("/film", response_model=FilmModel)
def create_film(film: FilmModel):
    films.append(film)
    return film


@app.get("/films", response_model=List[FilmModel])
def get_films():
    return films


@app.get("/film/{id}", response_model=FilmModel)
def get_film(id: int):
    for film in films:
        if film.id == id:
            return film
    raise HTTPException(status_code=404, detail="Film not found")


@app.patch("/film/{id}", response_model=FilmModel)
def update_film(id: int, updated_film: FilmModel):
    for index, film in enumerate(films):
        if film.id == id:
            films[index] = updated_film
            return updated_film
    raise HTTPException(status_code=404, detail="Film not found")


@app.delete("/film/{id}")
def delete_film(id: int):
    for index, film in enumerate(films):
        if film.id == id:
            films.pop(index)
            return {"message": "Film deleted successfully"}
    raise HTTPException(status_code=404, detail="Film not found")