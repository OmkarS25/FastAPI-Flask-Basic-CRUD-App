from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/items", response_model=dict)
def create_item(payload: dict, db: Session = Depends(get_db)):
    item = Item(title=payload["title"], description=payload.get("description"))
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "title": item.title, "description": item.description}

@app.get("/items/{item_id}", response_model=dict)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": item.id, "title": item.title, "description": item.description}

@app.put("/items/{item_id}", response_model=dict)
def update_item(item_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    item.title = payload["title"]
    item.description = payload.get("description")
    db.commit()
    db.refresh(item)
    return {"id": item.id, "title": item.title, "description": item.description}

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return None