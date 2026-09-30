"""Authentication routes providing demo enterprise accounts and session verification."""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

DEMO_USERS = {
    "recruiter@joveo.com": {
        "id": "usr_001",
        "email": "recruiter@joveo.com",
        "name": "Sarah Chen",
        "role": "Lead Talent Acquisition & Media Buyer",
        "organization": "Joveo Partner Network",
        "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=120&auto=format&fit=crop&q=80",
        "password": "password123"
    },
    "admin@adopt.ai": {
        "id": "usr_002",
        "email": "admin@adopt.ai",
        "name": "Alex Mercer",
        "role": "Programmatic Advertising Director",
        "organization": "Global Recruitment Solutions",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80",
        "password": "password123"
    }
}


class LoginRequest(BaseModel):
    email: str
    password: str


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    organization: str
    avatar_url: str


class LoginResponse(BaseModel):
    token: str
    token_type: str = "Bearer"
    user: UserProfile


@router.post("/login", response_model=LoginResponse)
def login(creds: LoginRequest) -> LoginResponse:
    """Authenticate user with email and password, or accept any demo password."""
    email_clean = creds.email.strip().lower()
    user_record = DEMO_USERS.get(email_clean)

    # For demo ease, accept demo accounts with password123 or valid credentials
    if not user_record:
        # Fallback to create a demo profile dynamically if user types a custom email
        user_record = {
            "id": f"usr_{hash(email_clean) % 10000}",
            "email": email_clean,
            "name": email_clean.split("@")[0].replace(".", " ").title() or "Recruitment Specialist",
            "role": "Recruitment Campaign Manager",
            "organization": "Enterprise Employer",
            "avatar_url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=120&auto=format&fit=crop&q=80",
            "password": creds.password
        }

    # Verify password if specified in demo users
    if email_clean in DEMO_USERS and creds.password != DEMO_USERS[email_clean]["password"]:
        raise HTTPException(status_code=401, detail="Invalid password. For demo accounts use: password123")

    token = f"adopt_sec_{user_record['id']}_{hash(email_clean)}"
    profile = UserProfile(
        id=user_record["id"],
        email=user_record["email"],
        name=user_record["name"],
        role=user_record["role"],
        organization=user_record["organization"],
        avatar_url=user_record["avatar_url"]
    )

    return LoginResponse(token=token, user=profile)


@router.get("/me", response_model=UserProfile)
def get_current_user(token: Optional[str] = None):
    """Return default authenticated user profile."""
    default = DEMO_USERS["recruiter@joveo.com"]
    return UserProfile(
        id=default["id"],
        email=default["email"],
        name=default["name"],
        role=default["role"],
        organization=default["organization"],
        avatar_url=default["avatar_url"]
    )
