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
