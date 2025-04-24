from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from typing import List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db


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


@app.get("/")
def root():
    return {"message": "Hello there"}


@app.get("/posts", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""select * from posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post(
    "/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
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

    return new_post


""" @app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts) - 1]
    return {"detail": post} """


@app.get("/posts/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""select * from posts where id=%s""", (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    return post


@app.delete("/posts/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""delete from posts where id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    post.delete(synchronize_session=False)
    db.commit()

    return {"message": f"Post with id: {id} was successfully deleted"}


@app.put("/posts/{id}", response_model=schemas.PostResponse)
def update_post(id: int, new_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(
    #   """update posts set title = %s, content = %s, published = %s where id = %s returning *""",
    #    (post.title, post.content, post.published, str(id)),
    # )

    # updated_post = cursor.fetchone()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    # Usar las columnas del modelo como claves
    update_data = {
        getattr(models.Post, key): value
        for key, value in new_post.model_dump().items()
        if key in models.Post.__table__.columns
    }

    post_query.update(update_data, synchronize_session=False)
    db.commit()

    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(
        email=user.email,
        password=user.password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
