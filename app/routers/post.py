from typing import List, Optional

from fastapi import FastAPI, status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session

from . import oauth2
from .. import models
from ..database import engine, get_db
from .. import schemas
from .. import utils

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.Post])
def get_post(limit: int = 10,
             skip: int = 0,
             search: Optional[str] = "",
             db: Session = Depends(get_db)):
    return db.query(models.Posts).filter(models.Posts.title.contains(search)).limit(limit).offset(skip).all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)):
    new_post = models.Posts(user_id_fkey=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id_post}", response_model=schemas.Post)
def get_post(id_post: int,
             db: Session = Depends(get_db)):
    if post := db.query(models.Posts).filter(models.Posts.id == id_post).first():
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")


@router.delete("/{id_post}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_post: int,
                db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)):
    post_query = db.query(models.Posts).filter(models.Posts.id == id_post)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")

    if post.user_id_fkey != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not autorized")

    post_query.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id_post}", response_model=schemas.Post)
def update_post(id_post: int,
                post_in: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)):
    query = db.query(models.Posts).filter(models.Posts.id == id_post)
    post = query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")

    if post.user_id_fkey != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not autorized")

    query.update(post_in.model_dump(), synchronize_session=False)
    db.commit()

    return query.first()
