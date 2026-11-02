from pydantic import BaseModel

#Input Schema
class BlogCreate(BaseModel):
    title: str
    content: str

#Output Schema
class Blog(BlogCreate):
    id: int

    class Config:
        from_attributes = True