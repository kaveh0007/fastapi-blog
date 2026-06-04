from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from typing import List, Dict
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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

@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False, name='home')
def home(request: Request):
    return templates.TemplateResponse(request=request, name="home.html", context={"posts" : posts})

@app.get("/api/posts")
def get_posts():
    return posts