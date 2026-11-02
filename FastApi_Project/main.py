from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas
from auth import token_verify, create_token

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

#Db Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login():
    return {"access_token": create_token({"sub": "admin"}),
            "token_type": "bearer"
            }


#CREATE BLOG(Protected Route)
@app.post("/blogs", response_model=schemas.Blog)
def create_blog(blog: schemas.BlogCreate, db: Session = Depends(get_db), current_user: str = Depends(token_verify)):
    db_blog = models.Blog(title=blog.title, content=blog.content)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog


#Read All Blogs
@app.get("/blogs")
def get_blogs(page: int = 1,
        limit: int = 10,
        search: str = Query(default="", description="Search query for blog title"),
        db: Session = Depends(get_db)):
    
    blogs = db.query(models.Blog)
    if search:
        blogs = blogs.filter(models.Blog.title.ilike(f"%{search}%"))

    total_blogs = blogs.count()
    start = (page - 1) * limit
    blogs = blogs.offset(start).limit(limit).all()
    return {
        "total": total_blogs,
        "page": page,
        "limit": limit,
        "blogs": blogs
    }


#Read Blog by ID
@app.get("/blogs/{blog_id}", response_model=schemas.Blog)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

#Update Blog Api(Protected Route)
@app.put("/blogs/{blog_id}", response_model=schemas.Blog)
def update_blog(blog_id: int, updated_blog: schemas.BlogCreate, db: Session = Depends(get_db), current_user: str = Depends(token_verify)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog.title = updated_blog.title
    blog.content = updated_blog.content
    db.commit()
    db.refresh(blog)
    return blog 

#Delete Blog Api(Protected Route)
@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: str = Depends(token_verify)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(blog)
    db.commit()
    return {"message": "Blog deleted successfully"}