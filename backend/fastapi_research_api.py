import os
import json
import time
import requests
import hashlib
import threading
import subprocess
import logging
import numpy as np
import faiss
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import Project, ResearchItem  # Ensure your models include Project

# ✅ Load environment variables
load_dotenv()
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "default_key")

# ✅ Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ✅ Initialize FAISS index (Fix for add_with_ids issue)
DIMENSION = 384
base_index = faiss.IndexFlatL2(DIMENSION)  # Base index
index = faiss.IndexIDMap(base_index)  # ID Mapping to allow add_with_ids

# ✅ Dictionary to store metadata for FAISS embeddings
stored_metadata = {}

# ✅ Initialize FastAPI
app = FastAPI()


# Sample database of projects
projects_db = [
    {"id": 1, "name": "AI Research", "description": "Developing AI-powered search", "last_updated": "2025-03-05", "timeline": ["Jan", "Feb", "Mar"], "data": [20, 40, 80]},
    {"id": 2, "name": "Data Pipeline", "description": "Building scalable data pipeline", "last_updated": "2025-03-04", "timeline": ["Feb", "Mar", "Apr"], "data": [10, 30, 60]},
    {"id": 3, "name": "UI Overhaul", "description": "Redesigning dashboard UI", "last_updated": "2025-03-03", "timeline": ["Mar", "Apr", "May"], "data": [5, 15, 40]},
]

# ✅ Add CORS Middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3091"],  # Allows frontend requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# ✅ Load SentenceTransformer model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# ✅ Dependency to get database session (Move this ABOVE API Endpoints)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from datetime import datetime  # Ensure this is at the top

@app.post("/save_research_item/")
def save_research_item(item_data: dict, db: Session = Depends(get_db)):
    """Save a new research item to the database, ensuring no duplicate URLs."""
    
    # ✅ Convert timestamp from string to datetime object
    timestamp_str = item_data.get("timestamp", datetime.utcnow().isoformat())  # Default to now if missing
    timestamp = datetime.fromisoformat(timestamp_str)  # Convert to datetime

    # ✅ Check if a research item with the same URL already exists
    existing_item = db.query(ResearchItem).filter(ResearchItem.url == item_data["url"]).first()

    if existing_item:
        return {"message": "Research item already exists", "id": existing_item.id}

    try:
        # ✅ Create new research item
        new_research_item = ResearchItem(
            title=item_data["title"],
            url=item_data["url"],
            project_id=item_data["project_id"],
            timestamp=timestamp  # ✅ Pass as a datetime object
        )

        db.add(new_research_item)
        db.commit()
        db.refresh(new_research_item)

        return {"message": "Research item saved successfully", "id": new_research_item.id}
    
    except IntegrityError:
        db.rollback()  # ✅ Rollback transaction if error occurs
        return {"error": "This research item already exists."}

# ✅ Endpoint to retrieve all projects
@app.get("/get_projects/")
def get_projects(db: Session = Depends(get_db)):
    logger.info("🔍 get_projects() called!")  # Debugging line
    projects = db.query(Project).all()
    return {"projects": [{"id": proj.id, "name": proj.name} for proj in projects]}



@app.get("/chat_context/{project_id}")
async def get_chat_context(project_id: int, db: Session = Depends(get_db)):
    """Fetch project context for LibreChat conversations"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all research items for this project
    research_items = project.research_items
    
    # Format context for chat
    context = {
        "project_name": project.name,
        "research_summary": [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "timestamp": item.get("timestamp", "")
            }
            for item in research_items
        ]
    }
    
    return context


# ✅ Endpoint to retrieve all research items for a specific project
@app.get("/get_project_research/")
def get_project_research(project_id: int, db: Session = Depends(get_db)):
    """Fetch research items belonging to a specific project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"project_id": project.id, "project_name": project.name, "research_items": project.research_items}

@app.post("/create_project/")
def create_project(project_data: dict, db: Session = Depends(get_db)):
    new_project = Project(name=project_data["name"])
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"id": new_project.id, "name": new_project.name}

@app.get("/get_top_projects")
def get_top_projects():
    return {"projects": projects_db[:3]}


@app.post("/assign_tab_to_project/")
def assign_tab_to_project(tab_id: int = Body(...), project_id: int = Body(...), db: Session = Depends(get_db)):
    """Assigns a tab to a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Store tab assignment in the database (assuming you track tab-project assignments)
    return {"message": f"Tab {tab_id} assigned to project {project_id}"}



# ✅ Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_saved_tabs():
    """Load saved research items from the database into FAISS."""
    db = SessionLocal()
    research_items = db.query(ResearchItem).all()

    print(f"🔄 Restoring {len(research_items)} saved tabs into FAISS index...")

    for item in research_items:
        try:
            embedding = np.array(json.loads(item.embedding), dtype=np.float32)
            tab_id = int(hashlib.md5(item.url.encode()).hexdigest(), 16) % (10**10)
            index.add_with_ids(np.array([embedding]), np.array([tab_id], dtype=np.int64))
        except Exception as e:
            print(f"❌ Error restoring embedding for {item.url}: {e}")

    print("✅ All saved research items loaded into FAISS.")

# ✅ Call this function on startup
load_saved_tabs()


# ✅ Function to generate embeddings
def generate_embedding(text):
    return embedding_model.encode(text).astype(np.float32)

# ✅ Find the most relevant project for a tab
def find_relevant_project(title, url):
    """Finds the most relevant project based on semantic similarity."""
    response = requests.get("http://127.0.0.1:8000/get_projects/")
    projects = response.json().get("projects", [])

    if not projects:
        return None  # No projects exist yet

    tab_text = f"{title} {url}"
    tab_embedding = np.array([generate_embedding(tab_text)], dtype=np.float32)

    project_embeddings = []
    project_ids = []

    for project in projects:
        if "embedding" in project:
            project_embedding = np.array(json.loads(project["embedding"]), dtype=np.float32)
            project_embeddings.append(project_embedding)
            project_ids.append(project["id"])

    if not project_embeddings:
        return None

    project_embeddings = np.array(project_embeddings, dtype=np.float32)
    index = faiss.IndexFlatL2(tab_embedding.shape[1])
    index.add(project_embeddings)

    distances, indices = index.search(tab_embedding, k=3)  # Find top 3 closest projects
    best_match_idx = indices[0][0]
    best_project_id = project_ids[best_match_idx]

    similarity_score = 1 - distances[0][0]  # Convert distance to similarity score

    return best_project_id if similarity_score > 0.7 else None  # Only return if above threshold

# ✅ Function to get open tabs from Chrome (Mac users)
def get_open_tabs():
    try:
        script = '''
        tell application "Google Chrome"
            set tabList to "["
            repeat with w in (windows)
                repeat with t in (tabs of w)
                    set tabList to tabList & "{\\"title\\": \\"" & title of t & "\\", \\"url\\": \\"" & URL of t & "\\"},"
                end repeat
            end repeat
            set tabList to text 1 thru -2 of tabList -- Remove last comma
            set tabList to tabList & "]"
            return tabList
        end tell
        '''
        response = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        output = response.stdout.strip()

        if not output:
            logger.warning("❌ No open tabs detected!")
            return []

        return json.loads(output)

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}. Raw response: {response.stdout}")
        return []
    except Exception as e:
        logger.error(f"❌ Error retrieving tabs: {e}")
        return []

def prompt_for_project_assignment(tab_id, title, url):
    """Prompts the user to assign a tab to an existing or new project."""
    print(f"\n📝 Assign tab '{title}' ({url}) to a project? (yes/no)")
    choice = input().strip().lower()

    if choice != "yes":
        return None  # Skip assignment

    # ✅ Get projects
    response = requests.get("http://127.0.0.1:8000/get_projects/")
    projects = response.json().get("projects", [])

    if projects:
        print("\n📂 Existing Projects:")
        for idx, project in enumerate(projects, 1):
            print(f"{idx}. {project['name']} (ID: {project['id']})")

        while True:
            print("\n➡️ Choose an option:")
            print("1️⃣ Assign to an existing project")
            print("2️⃣ Create a new project")

            project_choice = input("Enter 1 or 2: ").strip()

            if project_choice == "1":
                while True:
                    try:
                        selected_index = int(input("\n📂 Select a project by number: ").strip()) - 1
                        if 0 <= selected_index < len(projects):
                            return projects[selected_index]["id"]
                        else:
                            print("❌ Invalid selection. Choose a valid project number.")
                    except ValueError:
                        print("❌ Please enter a valid number.")
            elif project_choice == "2":
                new_project_name = input("\n✏️ Enter new project name: ").strip()
                response = requests.post("http://127.0.0.1:8000/create_project/", json={"name": new_project_name})
                if response.status_code == 200:
                    return response.json()["id"]
            else:
                print("❌ Invalid choice. Enter 1 or 2.")

    return None  # No project was assigned


def check_project_overlap(tab_id, title, url):
    """Checks if the tab's content overlaps with research in any existing project."""
    
    # Get all projects first
    projects_response = requests.get("http://127.0.0.1:8000/get_projects/")
    projects = projects_response.json().get("projects", [])

    if not projects:
        return None  # No projects exist yet

    tab_text = f"{title} {url}"
    tab_embedding = np.array([generate_embedding(tab_text)], dtype=np.float32)

    project_embeddings = []
    project_ids = []

    # Loop through each project and get research items
    for project in projects:
        project_id = project["id"]
        research_response = requests.get(f"http://127.0.0.1:8000/get_project_research/?project_id={project_id}")
        
        if research_response.status_code != 200:
            continue  # Skip if project research retrieval fails
        
        research_items = research_response.json().get("research_items", [])
        
        for research_item in research_items:
            if "embedding" in research_item:
                research_embedding = np.array(json.loads(research_item["embedding"]), dtype=np.float32)
                project_embeddings.append(research_embedding)
                project_ids.append(project_id)

    if not project_embeddings:
        return None  # No research embeddings available for comparison

    project_embeddings = np.array(project_embeddings, dtype=np.float32)
    index = faiss.IndexFlatL2(tab_embedding.shape[1])
    index.add(project_embeddings)

    distances, indices = index.search(tab_embedding, k=3)  # Find top 3 closest research pieces
    best_match_idx = indices[0][0]
    best_project_id = project_ids[best_match_idx]

    similarity_score = 1 - distances[0][0]  # Convert distance to similarity score

    return best_project_id if similarity_score > 0.8 else None  # Only return if above threshold


# ✅ Modify auto_save_tabs() to include prompting
def auto_save_tabs():
    db = SessionLocal()  # Create a database session

    while True:
        print("🔄 Auto-saving open tabs...")
        tabs = get_open_tabs()
        current_time = datetime.utcnow().isoformat()

        for tab in tabs:
            title = tab.get("title", "").strip()
            url = tab.get("url", "").strip()
            if not title or not url:
                continue

            tab_id = int(hashlib.md5(url.encode()).hexdigest(), 16) % (10**10)
            embedding = generate_embedding(title + " " + url)
            embedding_np = np.array([embedding], dtype=np.float32)

            # ✅ Check if tab is already saved in the DB
            existing_item = db.query(ResearchItem).filter(ResearchItem.url == url).first()
            if existing_item:
                print(f"🟢 Tab already saved: {title} ({url})")
                continue  # Skip if already saved

            # ✅ Step 1: Prompt for project assignment
            project_id = prompt_for_project_assignment(tab_id, title, url)

            # ✅ Step 2: Check for relevant project merge
            merged_project_id = check_project_overlap(tab_id, title, url)

            if merged_project_id and merged_project_id != project_id:
                print(f"🔗 Suggesting tab merge into project {merged_project_id}. Merging now...")
                project_id = merged_project_id  # Set merged project as the final assignment

            # ✅ Step 3: Store metadata in the database
            new_research_item = ResearchItem(
                title=title,
                url=url,
                project_id=project_id,
                timestamp=datetime.utcnow(),
                embedding=json.dumps(embedding.tolist())  # Store embedding as JSON
            )

            db.add(new_research_item)
            db.commit()

            # ✅ Step 4: Save to FAISS
            index.add_with_ids(embedding_np, np.array([tab_id], dtype=np.int64))

            print(f"✅ Research item saved for project {project_id}")

        print("✅ Tabs saved successfully.")
        time.sleep(300)  # Run every 5 minutes
  # Run every 5 minutes


# ✅ Start background tasks
threading.Thread(target=auto_save_tabs, daemon=True).start()

#INITATE uvicorn fastapi_research_api:app --host 0.0.0.0 --port 8000 --reload
