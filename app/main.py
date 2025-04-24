from fastapi import FastAPI
from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine
from .routers import post, user


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="turbodb",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was succesfully")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error", error)
        time.sleep(2)


""" my_posts: List[dict] = [
    Post(
        title="Desayuno", content="Me gustan los huevos con tosineta", id=1
    ).model_dump(),
    Post(
        title="Comidas rápidas", content="Me gusta la pizza hawaina", id=2
    ).model_dump(),
] """


""" def find_post(id: int):
    for p in my_posts:
        if p["id"] == id:
            return p """


""" def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i
    return None """


app.include_router(post.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "Hello there"}
