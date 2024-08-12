from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    description: Optional[str]

class ItemCreate(BaseModel):
    name: str
    description: Optional[str]

class ItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

DATABASE_URL = "sqlite:///test.db"

class Base(DeclarativeBase):
    pass

class DBItem(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return "Server is running"

@app.post("/items")
def create_item(item: ItemCreate, db: Session = Depends(get_db)) -> Item:
    # db = SessionLocal()
    db_item = DBItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    # db.close()

    return Item(**db_item.__dict__)

@app.get("/items/{iem_id}")
def read_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    # db = SessionLocal()
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    # db.close()
    return Item(**db_item.__dict__)

@app.put("/items/{iem_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)) -> Item:
    # db = SessionLocal()
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    # db.close()

    return Item(**db_item.__dict__)

@app.delete("/items/{iem_id}")
def read_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    # db = SessionLocal()
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    # db.close()

    return Item(**db_item.__dict__)