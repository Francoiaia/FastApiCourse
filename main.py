from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [{"title": "title of the post 1", "content": "content of post 1", "id": 1},
            {"title": "title of the post 2", "content": "content of post 2", "id": 2}]


@app.get("/posts")
def get_post():
    return {"data": my_posts}


@app.post("/posts")
def create_post(post: Post):
    return {"data": post}
