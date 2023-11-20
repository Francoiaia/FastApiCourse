from random import randrange
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, status, HTTPException, Response
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


try:
    conn = psycopg2.connect(host='localhost',
                            port=9898,
                            database='FastApiCourse',
                            user='postgres',
                            password='admin',
                            cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connected")
except Exception as e:

    print(e)

my_posts = [{"title": "title of the post 1", "content": "content of post 1", "id": 1},
            {"title": "title of the post 2", "content": "content of post 2", "id": 2}]


def find_post(id_post):
    for post in my_posts:
        if post['id'] == id_post:
            return post


def find_index_post(id_post):
    for i, p in enumerate(my_posts):
        if p['id'] == id_post:
            return i


@app.get("/posts")
def get_post():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published)VALUES(%s,%s,%s) RETURNING *""",
                   (post.title, post.content, post.published))

    new_post = cursor.fetchone()
    conn.commit()
    # post_dict = post.model_dump()
    # post_dict['id'] = randrange(0, 1000000)
    # my_posts.append(post_dict)

    return {"data": new_post}


@app.get("/posts/{id_post}")
def get_post(id_post: int):
    cursor.execute("""SELECT * FROM posts where id = %s""", (str(id_post)))
    if posts := cursor.fetchone():
        return posts
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_post: int):
    cursor.execute("""DELETE FROM posts where id = %s RETURNING *""", (str(id_post)))
    post = cursor.fetchone()
    conn.commit()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id_post}")
def update_post(id_post: int, post: Post):
    cursor.execute("""UPDATE posts  set title =%s, content=%s,published =%s where id = %s returning *""",
                   (post.title, post.content, post.published, str(id_post)))
    post = cursor.fetchone()
    conn.commit()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")

    return {"data": post}
