from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import sys

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:turbodb@localhost/fastapi"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        print("✅ Conexión exitosa a la base de datos.")
except OperationalError as e:
    print("❌ Error: Falló la conexión a la base de datos")
    print("Detalle:", e)
    sys.exit(1)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
