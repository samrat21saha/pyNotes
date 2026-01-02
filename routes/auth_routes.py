from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone

from config.db import conn
from utils.jwt import create_access_token, hash_password, verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# =========================
# SIGNUP PAGE
# =========================
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


# =========================
# SIGNUP LOGIC
# =========================
@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if conn.pynotes.users.find_one({"username": username}):
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Username already exists. Please login or use another username."
            }
        )

    result = conn.pynotes.users.insert_one({
        "username": username,
        "password": hash_password(password),
        "created_at": datetime.now(timezone.utc),
    })

    token = create_access_token({"user_id": str(result.inserted_id)})

    response = RedirectResponse("/", status_code=303)
    response.set_cookie("access_token", token, httponly=True)
    return response


# =========================
# LOGIN PAGE
# =========================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# =========================
# LOGIN LOGIC
# =========================
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = conn.pynotes.users.find_one({"username": username})

    if not user or not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password."
            }
        )

    token = create_access_token({"user_id": str(user["_id"])})

    response = RedirectResponse("/", status_code=303)
    response.set_cookie("access_token", token, httponly=True)
    return response


# =========================
# LOGOUT
# =========================
@router.post("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response
