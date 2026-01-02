from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone

from config.db import conn
from utils.jwt import (
    create_access_token,
    hash_password,
    verify_password
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# =========================
# GET: SIGNUP PAGE
# =========================
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request}
    )


# =========================
# POST: SIGNUP
# =========================
@router.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    existing_user = conn.pynotes.users.find_one({"username": username})

    if existing_user:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Username already exists. Please login or use a different username."
            }
        )

    user = {
        "username": username,
        "password": hash_password(password),  # ✅ CRITICAL FIX
        "created_at": datetime.now(timezone.utc),
    }

    result = conn.pynotes.users.insert_one(user)

    token = create_access_token({"user_id": str(result.inserted_id)})

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return response


# =========================
# GET: LOGIN PAGE
# =========================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# =========================
# POST: LOGIN
# =========================
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = conn.pynotes.users.find_one({"username": username})

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password."
            }
        )

    # ✅ SAFE verification (hashed vs plain)
    if not verify_password(password, user["password"]):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password."
            }
        )

    token = create_access_token({"user_id": str(user["_id"])})

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return response


# =========================
# POST: LOGOUT
# =========================
@router.post("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response
