from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from .. import schemas
from .. import utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id_users}", response_model=schemas.UserResponse)
def get_user(id_users: int, db: Session = Depends(get_db)):
    if user := db.query(models.User).filter(models.User.id == id_users).first():
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID NOT FOUND")


@router.get("/", response_model=list[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
