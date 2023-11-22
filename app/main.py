import psycopg2
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor
from .routers import post, user, auth
from . import models
from .database import engine, get_db

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

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
