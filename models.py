from pydantic import BaseModel
from typing import Optional

class FilmCreate(BaseModel):
    title: str
    movie_banner: str
    description: str
    director: str
    producer: str
    release_date: int
    rt_score: int

class FilmUpdate(BaseModel):
    title: Optional[str] = None
    movie_banner: Optional[str] = None
    description: Optional[str] = None
    director: Optional[str] = None
    producer: Optional[str] = None
    release_date: Optional[int] = None
    rt_score: Optional[int] = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class FilmResponse(BaseModel):
    id: int
    title: str
    movie_banner: str
    description: str
    director: str
    producer: str
    release_date: int
    rt_score: int

class FavoriteCreate(BaseModel):
    film_id: int

class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    film_id: int
    film_details: FilmResponse