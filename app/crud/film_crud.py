from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.models import Film
from app.schemas.film_schemas import FilmCreate, FilmUpdate

def create_film(db: Session, film: FilmCreate) -> Film:
    db_film = Film(**film.model_dump())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return db_film

def get_films(db: Session, skip: int = 0, limit: int = 100) -> List[Film]:
    return db.query(Film).offset(skip).limit(limit).all()

def get_film_by_id(db: Session, film_id: int) -> Optional[Film]:
    return db.query(Film).filter(Film.id == film_id).first()

def get_films_by_genre(db: Session, genre: str) -> List[Film]:
    return db.query(Film).filter(Film.genre == genre).all()

def get_all_genres(db: Session) -> List[str]:
    genres = db.query(Film.genre).distinct().all()
    return [g[0] for g in genres]

def update_film(db: Session, film_id: int, film_update: FilmUpdate) -> Optional[Film]:
    db_film = get_film_by_id(db, film_id)
    if not db_film:
        return None
    
    update_data = film_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_film, key, value)
    
    db.commit()
    db.refresh(db_film)
    return db_film

def delete_film(db: Session, film_id: int) -> bool:
    db_film = get_film_by_id(db, film_id)
    if not db_film:
        return False
    
    db.delete(db_film)
    db.commit()
    return True

def get_film_stats(db: Session) -> dict:
    total_count = db.query(Film).count()
    
    most_liked = db.query(Film).order_by(Film.likes.desc()).first()
    most_disliked = db.query(Film).order_by(Film.dislikes.desc()).first()
    
    return {
        "total_count": total_count,
        "most_liked": most_liked,
        "most_disliked": most_disliked,
    }