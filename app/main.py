from pathlib import Path

from routes.academic_periods_routes import router as academic_periods_router
from routes.users_routes import router as users_router
from routes.faculties_routes import router as faculties_router
from routes.roles_routes import router as roles_router
from routes.grades_routes import router as grades_router
from routes.courses_routes import router as courses_router
from routes.classrooms_routes import router as classrooms_router
from routes.enrollments_routes import router as enrollments_router
from routes.status_routes import router as status_router
from routes.certificates_routes import router as certificates_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(academic_periods_router)
app.include_router(enrollments_router)
app.include_router(faculties_router)
app.include_router(grades_router)
app.include_router(courses_router)
app.include_router(classrooms_router)
app.include_router(status_router)
app.include_router(certificates_router)
app.include_router(roles_router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

from fastapi.responses import HTMLResponse
import os

# Create the dist directory if it doesn't exist yet to prevent startup errors during development
os.makedirs(FRONTEND_DIR / "assets", exist_ok=True)
if not (FRONTEND_DIR / "index.html").exists():
    (FRONTEND_DIR / "index.html").write_text("<html><body>Building...</body></html>")

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    index_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(index_path.read_text())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)