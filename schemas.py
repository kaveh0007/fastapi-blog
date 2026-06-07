from pydantic import BaseModel, Field, ConfigDict

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)

class PostRetrieve(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date_posted: str

class PostCreate(PostBase):
    pass