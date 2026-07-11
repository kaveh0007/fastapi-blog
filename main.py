import models
from fastapi import FastAPI, Request, status, HTTPException, Depends
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from schemas import PostResponse, PostCreate, UserResponse, UserCreate, PostUpdate, UserUpdate
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
    posts = db.scalars(select(models.Post)).all()
    return templates.TemplateResponse(request=request, name="home.html", context={"posts" : posts, "title" : "Home"})

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(post_id: int, request: Request, db: Annotated[Session, Depends(get_db)]):
    post = db.scalars(select(models.Post).where(models.Post.id == post_id)).first()
    if post:
        return templates.TemplateResponse(request=request, name="post_page.html", context={"title": post.title, "post": post})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

@app.get("/users/{user_id}/posts", include_in_schema=False)
def user_posts_page(user_id: int, request: Request, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    posts = db.scalars(select(models.Post).where(models.Post.user_id == user_id)).all()
    return templates.TemplateResponse(request=request, name="user_posts.html", context={"posts": posts, "title": f"posts by {user.username}"})

@app.get("/api/users", response_model=list[UserResponse])
def get_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(models.User)).all()
    return users

@app.post("/api/users", response_model=UserResponse)
def create_users(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.scalars(select(models.User).where(models.User.username == user.username)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username is taken") #Implement this logic using the instragram approach later
    existing_user = db.scalars(select(models.User).where(models.User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email id in already in use")
    new_user = models.User(
        username = user.username,
        email = user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no user found")

@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_data: UserUpdate, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    db.delete(user)
    db.commit()
    return{}


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(models.User).where(models.User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    user_posts = db.scalars(select(models.Post).where(models.Post.user_id == user_id)).all()
    return user_posts

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    posts = db.scalars(select(models.Post)).all()
    return posts

@app.post("/api/posts", response_model=PostResponse)
def create_posts(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    user = db.scalars(select(models.User).where(models.User.id == post.user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    new_post = models.Post(
        user_id = post.user_id,
        title = post.title,
        content = post.content
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.scalars(select(models.Post).where(models.Post.id == post_id)).first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(post_id: int, updated_data: PostCreate, db: Annotated[Session, Depends(get_db)]):
    post = db.scalars(select(models.Post).where(models.Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    intended_user = db.scalars(select(models.User).where(models.User.id == updated_data.user_id)).first()
    if not intended_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="the intended user does not exist")
    
    for key, value in updated_data.model_dump().items():
        setattr(post, key, value)

    db.add(post)
    db.commit()
    db.refresh(post)

    return post

@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(post_id: int, updated_data: PostUpdate, db: Annotated[Session, Depends(get_db)]):
    post = db.scalars(select(models.Post).where(models.Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    
    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)

    return post

@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.scalars(select(models.Post).where(models.Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    # stmt = delete(models.Post).where(models.Post.id == post_id)
    # db.execute(stmt)
    db.delete(post)
    db.commit()
    return {}

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