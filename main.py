import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import Request
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()


class AuthRequest(BaseModel):
    email: str | None = None
    password: str | None = None


@app.get("/")
def home():
    return {
        "message": "Server running and connected to Supabase"
    }


@app.post("/auth/signup", status_code=201)
def signup(request: AuthRequest):

    # Server-side validation
    if not request.email or not request.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    # Supabase signup
    response = supabase.auth.sign_up({
        "email": request.email,
        "password": request.password
    })

    return response.user


@app.post("/auth/login")
def login(request: AuthRequest):

    # Server-side validation
    if not request.email or not request.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        # Supabase login
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )

@app.get("/public/info", status_code=200)
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


@app.get("/protected/profile", status_code=200)
def protected_profile(request: Request):
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"}
        )

    # Extract token
    token = auth_header.split(" ", 1)[1].strip()

    if not token:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"}
        )

    try:
        # Ask Supabase to verify the token
        response = supabase.auth.get_user(token)

        user = response.user

        if not user:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token"}
            )

        # Return only safe user information
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"}
        )