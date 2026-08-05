from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status,Query
from ..models import Movies
from ..database import SessionLocal
from starlette import status
from .auth import get_current_user
from starlette.responses import RedirectResponse
# from fastapi.templating import Jinja2Templates
from sqlalchemy import func, desc

# templates = Jinja2Templates(directory="App/templates")


router = APIRouter(prefix="/movies", tags=["movies"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


class MovieRequest(BaseModel):
    title: str = Field(min_length=4, max_length=20)
    description: str = Field(min_length=4, max_length=200)
    rating: int = Field(gt=0, lt=11)
    watched: bool
    genre: str = Field(min_length=4, max_length=20)


class MovieStats(BaseModel):
    total_movies: int
    watched_movies: int
    unwatched_movies: int
    average_rating: float


### Pages ###


# def redirect_to_login():
#     redirect_response = RedirectResponse(
#         url="/auth/login-page", status_code=status.HTTP_302_FOUND
#     )
#     redirect_response.delete_cookie(key="access_token")
#     return redirect_response


# @router.get("/movie-page")
# async def render_movie_page(request: Request, db: db_dep):
#     try:
#         user = await get_current_user(request.cookies.get("access_token"))
#         if user is None:
#             return redirect_to_login()
#         movies = db.query(Movies).filter(Movies.owner_id == user.get("id")).all()
#         return templates.TemplateResponse(
#             request=request,
#             name="movie.html",
#             context={"request": request, "movies": movies, "user": user},
#         )
#     except:
#         return redirect_to_login()


# @router.get("/add-movie-page")
# async def render_movie_page(request: Request):
#     try:
#         user = await get_current_user(request.cookies.get("access_token"))
#         if user is None:
#             return redirect_to_login()
#         return templates.TemplateResponse(
#             request=request,
#             name="add-movie.html",
#             context={"request": request, "user": user},
#         )
#     except:
#         return redirect_to_login()


# @router.get("/edit-movie-page/{movie_id}")
# async def render_edit_movie_page(request: Request, movie_id: int, db: db_dep):
#     try:
#         user = await get_current_user(request.cookies.get("access_token"))
#         if user is None:
#             return redirect_to_login()
#         movie = db.query(Movies).filter(Movies.id == movie_id).first()
#         return templates.TemplateResponse(
#             request=request,
#             name="edit-movie.html",
#             context={"request": request, "movie": movie, "user": user},
#         )
#     except:
#         return redirect_to_login()


### Endpoints ###


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(
    user: user_dep,
    db: db_dep,
    search: str =None,
    genre: str = None,
    watched: bool = None,
    sort_by: str = None,
    skip: int = Query(0,ge=0,),
    limit: int = Query(4,ge=0,le=48),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    query = db.query(Movies).filter(Movies.owner_id == user.get("id"))
    if genre:
        query = query.filter(Movies.genre == genre)
    if watched is not None:
        query = query.filter(Movies.watched == watched)
    if sort_by == "rating":
        query = query.order_by(desc(Movies.rating))
    elif sort_by == "title":
        query = query.order_by(Movies.title)
    elif sort_by == "id":
        query = query.order_by(Movies.id)
    if search:
        query=query.filter(Movies.title.ilike(f'%{search}%'))
    query=query.offset(skip).limit(limit)
    return query.all()


@router.get("/movie/{movie_id}", status_code=status.HTTP_200_OK)
async def read_movie(user: user_dep, db: db_dep, movie_id: int = Path(gt=0)):
    movie_model = (
        db.query(Movies)
        .filter(Movies.id == movie_id)
        .filter(Movies.owner_id == user.get("id"))
        .first()
    )
    if movie_model is not None:
        return movie_model
    raise HTTPException(status_code=404, detail="Movie Not Found")


@router.post("/movie", status_code=status.HTTP_201_CREATED)
async def create_movie(user: user_dep, db: db_dep, movie_request: MovieRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    existing_movie=db.query(Movies).filter(Movies.owner_id==user.get('id')).filter(Movies.title==movie_request.title).first()
    if existing_movie:
        raise HTTPException(status_code=400,detail='Movie Already Exists')
    movie_model = Movies(**movie_request.model_dump(), owner_id=user.get("id"))
    db.add(movie_model)
    db.commit()


@router.put("/movie/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_movie(
    user: user_dep, db: db_dep, movie_request: MovieRequest, movie_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    movie_model = (
        db.query(Movies)
        .filter(Movies.id == movie_id)
        .filter(Movies.owner_id == user.get("id"))
        .first()
    )
    if movie_model is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")
    movie_model.title = movie_request.title
    movie_model.description = movie_request.description
    movie_model.rating = movie_request.rating
    movie_model.watched = movie_request.watched

    db.add(movie_model)
    db.commit()


@router.delete("/movie/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(user: user_dep, db: db_dep, movie_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    movie_model = (
        db.query(Movies)
        .filter(Movies.id == movie_id)
        .filter(Movies.owner_id == user.get("id"))
        .first()
    )
    if movie_model is None:
        raise HTTPException(status_code=404, detail="Movie Not Found")
    db.query(Movies).filter(Movies.id == movie_id).filter(
        Movies.owner_id == user.get("id")
    ).delete()

    db.commit()


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats(user: user_dep, db: db_dep):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    total_movies = db.query(Movies).filter(Movies.owner_id == user.get("id")).count()
    watched_movies = (
        db.query(Movies)
        .filter(Movies.owner_id == user.get("id"))
        .filter(Movies.watched)
        .count()
    )
    unwatched_movies = total_movies - watched_movies
    # unwatched_movies = db.query(Movies).filter(Movies.owner_id == user.get("id")).filter(Movies.watched==False).count()
    average_rating = (
        db.query(func.avg(Movies.rating))
        .filter(Movies.owner_id == user.get("id"))
        .filter(Movies.watched == True)
        .scalar()
    )  # توضیح این خط رو تو آبسیدین کامل نوشتم
    average_rating = average_rating or 0
    return {
        "total_movies": total_movies,
        "watched_movies": watched_movies,
        "unwatched_movies": unwatched_movies,
        "average_rating": average_rating,
    }


@router.get('/group-by-genre')
async def group_by_genre(user:user_dep,db:db_dep):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    query=db.query(Movies.genre,func.count(Movies.id))
    query=query.filter(Movies.owner_id==user.get('id'))
    query=query.group_by(Movies.genre)
    
    result=query.all()
    
    return [
        {
            "genre": genre,
            "count": count
        }
        for genre, count in result
    ]