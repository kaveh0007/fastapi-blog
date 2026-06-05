from fastapi import FastAPI, Request, status, HTTPException
from typing import List, Dict
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

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

@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=[{"error": "post not Found"}])

@app.exception_handler(HTTPException)
def handle_HTTPException(request: Request, exception: HTTPException):
    print(request.url.path)
    if request.url.path.startswith("/api"):
        return JSONResponse(exception.detail, exception.status_code)
    return templates.TemplateResponse(request, "error.html", {"status_code": exception.status_code, "message": exception.detail[0].get("error")})