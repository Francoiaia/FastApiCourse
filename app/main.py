from random import randrange
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, status, HTTPException, Response, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db
from . import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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


@app.get("/posts")
def get_post(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Posts).all()

    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published)VALUES(%s,%s,%s) RETURNING *""",
    #                (post.title, post.content, post.published))
    #
    # new_post = cursor.fetchone()
    # conn.commit()
    # # post_dict = post.model_dump()
    # # post_dict['id'] = randrange(0, 1000000)
    # # my_posts.append(post_dict)

    new_post = models.Posts(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.get("/posts/{id_post}")
def get_post(id_post: int, db: Session = Depends(get_db)):
    if (
            post := db.query(models.Posts)
                    .filter(models.Posts.id == id_post)
                    .first()
    ):
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")


@app.delete("/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_post: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where id = %s RETURNING *""", (str(id_post)))
    # post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Posts).filter(models.Posts.id == id_post)

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")

    post.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id_post}")
def update_post(id_post: int, post_in: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts  set title =%s, content=%s,published =%s where id = %s returning *""",
    #                (post.title, post.content, post.published, str(id_post)))
    # post = cursor.fetchone()
    # conn.commit()

    query = db.query(models.Posts).filter(models.Posts.id == id_post)
    post = query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")
    query.update(post_in.model_dump(), synchronize_session=False)
    db.commit()

    return query.first()
