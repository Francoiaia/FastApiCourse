from typing import List

from fastapi import FastAPI, status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models
from ..database import engine, get_db
from .. import schemas
from .. import utils

router = APIRouter()


@router.get("/posts", response_model=List[schemas.Post])
def get_post(db: Session = Depends(get_db)):
    return db.query(models.Posts).all()


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Posts(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/posts/{id_post}", response_model=schemas.Post)
def get_post(id_post: int, db: Session = Depends(get_db)):
    if post := db.query(models.Posts).filter(models.Posts.id == id_post).first():
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")


@router.delete("/posts/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_post: int, db: Session = Depends(get_db)):
    post = db.query(models.Posts).filter(models.Posts.id == id_post)

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")

    post.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/posts/{id_post}", response_model=schemas.Post)
def update_post(id_post: int, post_in: schemas.PostCreate, db: Session = Depends(get_db)):
    query = db.query(models.Posts).filter(models.Posts.id == id_post)
    post = query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")
    query.update(post_in.model_dump(), synchronize_session=False)
    db.commit()

    return query.first()
