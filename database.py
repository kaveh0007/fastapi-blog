import os
from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

engine = create_async_engine(
    os.getenv("SQLALCHEMY_DATABASE_URL"),
    connect_args = {"check_same_thread": False},
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    autoflush=False, 
    expire_on_commit=False
    # class_=AsyncSession What does this do?
    )

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db