from fastapi import APIRouter, HTTPException, Query
from models import FilmResponse, UserCreate
from supabase_client import supabase
from typing import List
import logging

router = APIRouter(prefix='/user', tags=['user'])
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

@router.get("/search", response_model=List[FilmResponse])
async def search_films(
    id: str = Query(None),
    title: str = Query(None),
    rt_score: int = Query(None),
    release_date: int = Query(None)
):
    try:
        query = supabase.table("films").select("*")
        
        if id:
            query = query.eq("id", id)
        if title:
            query = query.ilike("title", f"%{title}%")
        if rt_score:
            query = query.eq("rt_score", rt_score)
        if release_date:
            query = query.eq("release_date", release_date)

        result = query.execute()

        if not hasattr(result, 'data'):
            logger.error("Invalid response format from Supabase")
            raise HTTPException(500, "Invalid server response")

        return result.data or []

    except Exception as e:
        logger.exception("Failed to search films")
        raise HTTPException(500, "Failed to search films") from e

@router.post("/favorites/{user_id}/{film_id}", status_code=201)
async def add_favorite_song(user_id: int, film_id: int):
    """Add a song to user's favorites """
    try:

        song = supabase.table("films").select("*").eq("id", film_id).execute()
        if not film.data:
            raise HTTPException(404, "Film not found")
            

        user = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user.data:
            raise HTTPException(404, "User not found")
            

        existing = supabase.table("favorites").select("*").eq("user_id", user_id).eq("film_id", film_id).execute()
        if existing.data:
            raise HTTPException(400, "Film already in favorites")
            

        result = supabase.table("favorites").insert({
            "user_id": user_id,
            "film_id": film_id
        }).execute()
        
        if not result.data:
            raise HTTPException(400, "Failed to add favorite")
            
        return {"message": "Film added to favorites"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to add favorite song {film_id} for user {user_id}")
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
