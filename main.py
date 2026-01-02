from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.note_routes import router as note_router
from routes.auth_routes import router as auth_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(note_router)
app.include_router(auth_router)
