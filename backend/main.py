from fastapi import FastAPI
from routes import projects, research_items
from fastapi_research_api import app as research_api

app = FastAPI()

# Include routers from other files
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(research_items.router, prefix="/research", tags=["Research"])

# Include research API
app.mount("/", research_api)  # ✅ This allows `fastapi_research_api.py` endpoints to work



# Run the app with: uvicorn main:app --reload
