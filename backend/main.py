from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.search import router as search_router
from routes.employees import router as employees_router
from routes.tasks import router as tasks_router
from routes.optimize import router as optimize_router
import os

app = FastAPI(title="Smart Workforce Optimizer API")

# Enable CORS for cross-origin requests (e.g. if the user runs frontend separately)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register API routers first
app.include_router(search_router, prefix="/search")
app.include_router(employees_router, prefix="/employees")
app.include_router(tasks_router, prefix="/tasks")
app.include_router(optimize_router, prefix="/optimize")

# Mount frontend static files at / so that index.html, search.html, etc. are served directly
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir, exist_ok=True)

app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
