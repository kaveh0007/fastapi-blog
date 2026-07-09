import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

#  connect_args is a dictionary passed to create_engine() that supplies keyword arguments directly to the underlying DBAPI's connect() function to configure the low-level connection behaviour
# The sqlite3 DBAPI by default prohibits the use of a particular connection in a thread which is not the one in which it was created. 
engine = create_engine(
    os.getenv("SQLALCHEMY_DATABASE_URL"),
    connect_args = {"check_same_thread": False}
    )
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db