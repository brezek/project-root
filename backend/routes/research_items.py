from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ResearchItem
from pydantic import BaseModel

router = APIRouter()

class ResearchItemCreate(BaseModel):
    title: str
    url: str = None

class UpdateResearchStatus(BaseModel):
    status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{project_id}/items/", response_model=dict)
def add_research_item(project_id: int, item: ResearchItemCreate, db: Session = Depends(get_db)):
    db_item = ResearchItem(project_id=project_id, title=item.title, url=item.url)
    db.add(db_item)
    db.commit()
    return {"message": "Research item added successfully"}

@router.patch("/{project_id}/items/{item_id}/status/", response_model=dict)
def update_research_status(project_id: int, item_id: int, status: UpdateResearchStatus, db: Session = Depends(get_db)):
    db.query(ResearchItem).filter_by(project_id=project_id, item_id=item_id).update({"status": status.status})
    db.commit()
    return {"message": "Research item status updated"}
