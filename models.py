from __future__ import annotations #Using for forward reference. There will be no error at run time anyway but this prevents breaking pylance
from datetime import datetime, UTC
from database import Base
from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pathlib import Path

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str|None] = mapped_column(String(200), nullable=True, default=None)
    posts: Mapped[list[Post]] = relationship(back_populates="author")

    @property
    def image_mount(self):
        return "media" if self.image_file else "static"

    @property
    def image_path(self):
        if self.image_file:
            return str(Path("/profile_pics" / self.image_file))
        return str(Path("/assets/default.svg"))
class Post(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    date_posted: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    author: Mapped[User] = relationship(back_populates="posts")