from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    research_items = relationship("ResearchItem", back_populates="project")

class ResearchItem(Base):
    __tablename__ = "research_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    embedding = Column(Text, nullable=True)  # Save FAISS embeddings as JSON strings

    project = relationship("Project", back_populates="research_items")
