from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Project, ResearchTab
from pydantic import BaseModel
from typing import List

router = APIRouter()

# ✅ Request model for assigning a tab to a project
class AssignTabToProjectRequest(BaseModel):
    tab_id: int
    project_id: int

# ✅ Endpoint: Create a new research project
@router.post("/projects/")
def create_project(name: str, db: Session = Depends(get_db)):
    project = Project(name=name)
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"message": "Project created", "project_id": project.id}

# ✅ Endpoint: Assign a tab to a project
@router.post("/assign_tab_to_project/")
def assign_tab_to_project(request: AssignTabToProjectRequest, db: Session = Depends(get_db)):
    tab = db.query(ResearchTab).filter(ResearchTab.id == request.tab_id).first()
    if not tab:
        raise HTTPException(status_code=404, detail="Tab not found")
    
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tab.project_id = request.project_id
    db.commit()
    return {"message": "Tab assigned to project successfully"}
