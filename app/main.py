from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    id: Optional[int] = 0
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


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


my_posts: List[dict] = [
    Post(
        title="Desayuno", content="Me gustan los huevos con tosineta", id=1
    ).model_dump(),
    Post(
        title="Comidas rápidas", content="Me gusta la pizza hawaina", id=2
    ).model_dump(),
]


def find_post(id: int):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i
    return None


@app.get("/")
def root():
    return {"message": "Hello there"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    print("alchemy", posts)

    return {"data": "success"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""select * from posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # cursor.execute(
    # """insert into posts (title, content, published) values (%s, %s, %s) returning *""",
    # (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(
        title=post.title, content=post.content, published=post.published
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post}


@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts) - 1]
    return {"detail": post}


@app.get("/posts/{id}")
def get_post(id: str):
    cursor.execute("""select * from posts where id=%s""", (str(id)))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    return post


@app.delete("/posts/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int):
    cursor.execute("""delete from posts where id = %s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    return {"message": f"Post with id: {id} was successfully deleted"}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """update posts set title = %s, content = %s, published = %s where id = %s returning *""",
        (post.title, post.content, post.published, str(id)),
    )

    updated_post = cursor.fetchone()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    return updated_post
