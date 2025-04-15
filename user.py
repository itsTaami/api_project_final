from fastapi import APIRouter, HTTPException, Query
from models import FilmResponse, UserCreate
from supabase_client import supabase
from typing import List
import logging

router = APIRouter(prefix='/user', tags=['user'])
logger = logging.getLogger(__name__)

@router.post("/register/", status_code=201)
async def register_user(user: UserCreate):
    try:
        user_data = user.dict(exclude_unset=True)
        existing = supabase.table("users").select("*").eq("username", user_data['username']).execute()
        if existing.data:
            raise HTTPException(400, "Username already exists")

        result = supabase.table("users").insert(user_data).execute()
        if not result.data:
            raise HTTPException(400, "Failed to create user")
        return {"message": "User created successfully", "user_id": result.data[0]["id"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to register user")
        raise HTTPException(500, "Failed to register user") from e

from fastapi import APIRouter, HTTPException, Query
from models import FilmCreate, FilmUpdate, FilmResponse
from supabase_client import supabase
from typing import List
import logging

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[FilmResponse])
async def get_all_films():
    """Retrieve all films"""
    try:
        result = supabase.table("films").select("*").execute()
        
        if not hasattr(result, 'data'):
            raise HTTPException(status_code=500, detail="Invalid server response")
        
        return result.data or []
    
    except Exception as e:
        logger.exception("Failed to fetch films")
        raise HTTPException(status_code=500, detail="Failed to fetch films")
        
@router.get("/search", response_model=List[FilmResponse])
async def search_films(id: str = Query(None), title: str = Query(None), rt_score: int = Query(None), release_date: int = Query(None)):
    try:
        query = supabase.table("films").select("*")
        if title:
            query = query.ilike("title", f"%{title}%")
        if rt_score is not None:
            query = query.ilike("rt_score", f"%{rt_score}%")
        if release_date is not None:
            query = query.ilike("release_date", f"%{release_date}%")
        result = query.execute()
        if not hasattr(result, 'data'):
            logger.error("Invalid response format from Supabase")
            raise HTTPException(500, "Invalid server response")
        return result.data or []
    except Exception as e:
        logger.exception("Failed to search films")
        raise HTTPException(500, "Failed to search films") from e

@router.post("/films/", response_model=FilmResponse, status_code=201)
async def create_film(film: FilmCreate):
    try:
        film_data = film.dict(exclude_unset=True)
        film_data.pop('id', None)
        required_fields = ['title', 'movie_banner', 'description', 'director', 'producer', 'release_date', 'rt_score']
        if not all(field in film_data for field in required_fields):
            raise HTTPException(400, f"Missing required fields. Required: {required_fields}")
        result = supabase.table("films").insert(film_data).execute()
        if not result.data:
            raise HTTPException(400, "Failed to create film")
        return result.data[0]
    except Exception as e:
        logger.exception("Failed to create film")
        if 'null value' in str(e):
            raise HTTPException(400, "Database error: Required field missing")
        raise HTTPException(500, f"Failed to create film: {str(e)}")

@router.put("/films/{film_id}")
async def update_film(film_id: int, film: FilmUpdate):
    try:
        existing = supabase.table("films").select("*").eq("id", film_id).execute()
        if not existing.data:
            raise HTTPException(404, "Film not found")
        update_data = film.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(400, "No update data provided")
        supabase.table("films").update(update_data).eq("id", film_id).execute()
        return {"message": "Film updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update film {film_id}")
        raise HTTPException(500, "Failed to update film") from e

@router.delete("/films/{film_id}")
async def delete_film(film_id: int):
    try:
        existing = supabase.table("films").select("*").eq("id", film_id).execute()
        if not existing.data:
            raise HTTPException(404, "Film not found")
        supabase.table("films").delete().eq("id", film_id).execute()
        return {"message": "Film deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete film {film_id}")
        raise HTTPException(500, "Failed to delete film") from e

@router.get("/users/", response_model=List[dict])
async def get_all_users():
    try:
        result = supabase.table("users").select("*").execute()
        if not hasattr(result, 'data'):
            raise HTTPException(500, "Invalid server response")
        return result.data or []
    except Exception as e:
        logger.exception("Failed to fetch users")
        raise HTTPException(500, "Failed to fetch users") from e

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        existing = supabase.table("users").select("*").eq("id", user_id).execute()
        if not existing.data:
            raise HTTPException(404, "User not found")
        supabase.table("favorites").delete().eq("user_id", user_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        return {"message": "User deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete user {user_id}")
        raise HTTPException(500, "Failed to delete user") from e


@router.get("/search", response_model=List[FilmResponse])
async def search_films(title: str = Query(None), rt_score: int = Query(None), release_date: int = Query(None)):
    try:
        query = supabase.table("films").select("*")
        if title:
            query = query.ilike("title", f"%{title}%")
        if rt_score is not None:
            query = query.ilike("rt_score", f"%{rt_score}%")
        if release_date is not None:
            query = query.ilike("release_date", f"%{release_date}%")
        result = query.execute()
        if not hasattr(result, 'data'):
            logger.error("Invalid response format from Supabase")
            raise HTTPException(500, "Invalid server response")
        return result.data or []
    except Exception as e:
        logger.exception("Failed to search films")
        raise HTTPException(500, "Failed to search films") from e

@router.post("/favorites/{user_id}/{film_id}", status_code=201)
async def add_favorite_film(user_id: int, film_id: int):
    try:
        film = supabase.table("films").select("*").eq("id", film_id).execute()
        if not film.data:
            raise HTTPException(404, "Film not found")
        user = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user.data:
            raise HTTPException(404, "User not found")
        existing = supabase.table("favorites").select("*").eq("user_id", user_id).eq("film_id", film_id).execute()
        if existing.data:
            raise HTTPException(400, "Film already in favorites")
        result = supabase.table("favorites").insert({"user_id": user_id, "film_id": film_id}).execute()
        if not result.data:
            raise HTTPException(400, "Failed to add favorite")
        return {"message": "Film added to favorites"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to add favorite film {film_id} for user {user_id}")
        raise HTTPException(500, "Failed to add favorite film") from e

@router.get("/favorites/{user_id}", response_model=List[FilmResponse])
async def get_favorite_films(user_id: int):
    try:
        favorites_result = supabase.table("favorites").select("film_id").eq("user_id", user_id).execute()
        if not hasattr(favorites_result, 'data'):
            raise HTTPException(500, "Invalid server response")
        if not favorites_result.data:
            return []
        film_ids = [fav["film_id"] for fav in favorites_result.data]
        films_result = supabase.table("films").select("*").in_("id", film_ids).execute()
        if not hasattr(films_result, 'data'):
            raise HTTPException(500, "Invalid server response")
        return films_result.data or []
    except Exception as e:
        logger.exception(f"Failed to get favorite films for user {user_id}")
        raise HTTPException(500, "Failed to get favorite films") from e

@router.delete("/favorites/{user_id}/{film_id}")
async def remove_favorite_film(user_id: int, film_id: int):
    try:
        existing = supabase.table("favorites").select("*").eq("user_id", user_id).eq("film_id", film_id).execute()
        if not existing.data:
            raise HTTPException(404, "Favorite not found")
        supabase.table("favorites").delete().eq("user_id", user_id).eq("film_id", film_id).execute()
        return {"message": "Film removed from favorites"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to remove favorite film {film_id} for user {user_id}")
        raise HTTPException(500, "Failed to remove favorite film") from e
