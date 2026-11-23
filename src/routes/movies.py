import math

from fastapi import APIRouter, HTTPException, status, Request

from crud.movies import count_movies, all_movies
from dependencies.db import SessionDep
from dependencies.pagination import PaginationHelper
from schemas import MovieListResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_paginated_movies(
    db: SessionDep, pagination: PaginationHelper, request: Request
):
    total_movies = await count_movies(db=db)
    total_pages = math.ceil(total_movies / pagination.per_page)

    movies = await all_movies(
        db=db,
        skip=((pagination.page - 1) * pagination.per_page),
        limit=pagination.per_page,
    )

    if total_movies == 0:
        raise HTTPException(
            detail="No movies found.", status_code=status.HTTP_404_NOT_FOUND
        )

    prev_page = None
    next_page = None

    if pagination.page - 1 > 0:
        prev_page = (
            str(request.url.path)
            + f"?page={pagination.page - 1}&per_page={pagination.per_page}"
        )

    if pagination.page < total_pages:
        next_page = (
            str(request.url.path)
            + f"?page={pagination.page + 1}&per_page={pagination.per_page}"
        )

    return MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_movies,
    )
