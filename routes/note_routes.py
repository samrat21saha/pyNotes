from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
from bson import ObjectId

from config.db import conn
from schemas.note_schema import notes_entity
from utils.jwt import decode_access_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    token = request.cookies.get("access_token")
    payload = decode_access_token(token) if token else None

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "is_authenticated": bool(payload),
            "active_page": "home",
            "newDocs": [],
            "selectedNote": None,
        }
    )


@router.get("/my-notes", response_class=HTMLResponse)
async def my_notes(request: Request):
    token = request.cookies.get("access_token")
    payload = decode_access_token(token) if token else None

    if not payload:
        return RedirectResponse("/login", status_code=303)

    user_id = payload["user_id"]
    note_id = request.query_params.get("note_id")

    docs = conn.pynotes.notes.find({"user_id": user_id})
    new_docs = notes_entity(docs)

    selected_note = None
    if note_id:
        note = conn.pynotes.notes.find_one(
            {"_id": ObjectId(note_id), "user_id": user_id}
        )
        if note:
            note["_id"] = str(note["_id"])
            selected_note = note

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "is_authenticated": True,
            "active_page": "notes",
            "newDocs": new_docs,
            "selectedNote": selected_note,
        }
    )


@router.post("/note")
async def add_note(
    request: Request,
    title: str = Form(...),
    desc: str = Form(...),
    important: bool = Form(False),
):
    token = request.cookies.get("access_token")
    payload = decode_access_token(token) if token else None

    if not payload:
        return RedirectResponse("/login", status_code=303)

    conn.pynotes.notes.insert_one({
        "title": title,
        "desc": desc,
        "important": important,
        "user_id": payload["user_id"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })

    return RedirectResponse("/my-notes", status_code=303)


@router.post("/note/{note_id}/update")
async def update_note(
    request: Request,
    note_id: str,
    title: str = Form(...),
    desc: str = Form(...),
    important: bool = Form(False),
):
    token = request.cookies.get("access_token")
    payload = decode_access_token(token) if token else None

    if not payload:
        return RedirectResponse("/login", status_code=303)

    conn.pynotes.notes.update_one(
        {"_id": ObjectId(note_id), "user_id": payload["user_id"]},
        {"$set": {
            "title": title,
            "desc": desc,
            "important": important,
            "updated_at": datetime.now(timezone.utc),
        }}
    )

    return RedirectResponse("/my-notes", status_code=303)


@router.post("/note/{note_id}/delete")
async def delete_note(request: Request, note_id: str):
    token = request.cookies.get("access_token")
    payload = decode_access_token(token) if token else None

    if not payload:
        return RedirectResponse("/login", status_code=303)

    conn.pynotes.notes.delete_one(
        {"_id": ObjectId(note_id), "user_id": payload["user_id"]}
    )

    return RedirectResponse("/my-notes", status_code=303)
