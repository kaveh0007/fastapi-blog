from fastapi import FastAPI, Request, status, HTTPException
from typing import List, Dict
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from schemas import PostRetrieve, PostCreate

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount('/static', StaticFiles(directory="static"), name='static')

posts : List[Dict] = [
    {        
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    }
]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html", context={"posts" : posts})

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(post_id: int, request: Request):
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(request, "post_page.html", {"title": post.get('title'), "post": post})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=[{"error": "post not found"}])

@app.get("/api/posts", response_model=list[PostRetrieve])
def get_posts():
    return posts

@app.post("/api/posts", response_model=PostRetrieve)
def create_posts(post: PostCreate):
    id = len(posts) + 1 if posts else 1
    post = {
        "id": id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "June 10, 2026"
    }
    posts.append(post)
    return post

@app.get("/api/posts/{post_id}", response_model=PostRetrieve)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=[{"error": "post not Found"}])

@app.exception_handler(StarletteHTTPException)
def handle_HTTPException(request: Request, exception: StarletteHTTPException):
    if exception.detail:
        if isinstance(exception.detail, List):
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