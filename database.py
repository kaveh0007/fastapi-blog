import os
from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

#  connect_args is a dictionary passed to create_engine() that supplies keyword arguments directly to the underlying DBAPI's connect() function to configure the low-level connection behaviour
# The sqlite3 DBAPI by default prohibits the use of a particular connection in a thread which is not the one in which it was created. 
# engine = create_engine(
#     os.getenv("SQLALCHEMY_DATABASE_URL"),
#     connect_args = {"check_same_thread": False},
#     pool_pre_ping=True
#     )

engine = create_async_engine(
    os.getenv("SQLALCHEMY_DATABASE_URL"),
    connect_args = {"check_same_thread": False},
    pool_pre_ping=True
)

# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# class Base(AsyncAttrs, DeclarativeBase):
#     pass

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db