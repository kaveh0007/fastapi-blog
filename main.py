import models
from fastapi import FastAPI, Request, status, HTTPException, Depends
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from schemas import PostResponse, PostCreate, UserResponse, UserCreate
from database import engine, Base, get_db
from sqlalchemy import select
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount('/static', StaticFiles(directory="static"), name='static')
app.mount('/media', StaticFiles(directory="media"), name='media')

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    posts = db.scalars(select(models.Post))
    return templates.TemplateResponse(request=request, name="home.html", context={"posts" : posts})

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(post_id: int, request: Request, db: Annotated[Session, Depends(get_db)]):
    post = db.scalars(select(models.Post).where(models.Post.id == post_id)).first()
    if post:
        return templates.TemplateResponse(request=request, name="post_page.html", context={"title": post.title, "post": post})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=[{"error": "post not found"}])

@app.get("/api/users", response_model=list[UserResponse])
def get_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(models.User)).all()
    return users

@app.post("/api/users", response_model=UserResponse)
def create_users(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    new_user = models.User(
        username = user.username,
        email = user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/user/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "no user found"})

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    posts = db.scalars(select(models.Post)).all()
    return posts

@app.post("/api/posts", response_model=PostResponse)
def create_posts(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    new_post = models.Post(
        user_id = post.user_id,
        title = post.title,
        content = post.content
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    print(new_post.author)
    return new_post

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.scalars(select(models.Post).where(models.Post.id == post_id)).first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=[{"error": "post not found"}])

@app.get("/api/posts/by/{user_id}")
def user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_posts = db.scalars(select(models.Post).where(models.Post.user_id == user_id)).all()
    if user_posts:
        return user_posts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "this user has not posted yet"})

@app.exception_handler(StarletteHTTPException)
def handle_HTTPException(request: Request, exception: StarletteHTTPException):
    if exception.detail:
        if isinstance(exception.detail, list):
            message = exception.detail[0].get("error")
        else:
            message = exception.detail
    else:
        message = "Aw Snap! An error occured, please try again."

    if request.url.path.startswith("/api"):
        return JSONResponse(
            content={"detail": message},
            status_code = exception.status_code
            )
    return templates.TemplateResponse(
        request, 
        "error.html",
        {"status_code": exception.status_code, "message": message}, status_code = exception.status_code
        )

@app.exception_handler(RequestValidationError)
def handle_ValidationError(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            content = exception.errors(),
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
            )
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": status.HTTP_422_UNPROCESSABLE_CONTENT, "message": exception.errors()[0].get("msg")},
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        )