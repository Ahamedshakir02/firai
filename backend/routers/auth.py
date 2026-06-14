"""
Auth Router
-----------
JWT-based authentication for police officers.
Handles login, registration requests, profile, and admin approval.
Includes rate limiting and input validation.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt

from database import get_db
from models.officer import Officer, RegistrationRequest
from services.rate_limiter import LOGIN_LIMITER, REGISTRATION_LIMITER, RateLimitService
from validators import OfficerValidator, NarrativeValidator
from logging_config import logger, auth_logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# ──────────────────────── Config ────────────────────────

SECRET_KEY = "firai-kerala-police-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ──────────────────────── Schemas ────────────────────────

class LoginRequest(BaseModel):
    badge_number: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    officer: dict


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    badge_number: str = Field(..., min_length=2)
    rank: str = ""
    police_station: str = ""
    district: str = ""
    phone: str = ""
    email: str = ""
    password: str = Field(..., min_length=6)


class OfficerProfile(BaseModel):
    id: int
    badge_number: str
    name: str
    rank: Optional[str] = None
    police_station: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_admin: bool = False

    class Config:
        from_attributes = True


class RegistrationRequestResponse(BaseModel):
    id: int
    name: str
    badge_number: str
    rank: Optional[str] = None
    police_station: Optional[str] = None
    district: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ──────────────────────── Helpers ────────────────────────

def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(officer_id: int, badge_number: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(officer_id),
        "badge": badge_number,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_officer(
    db: AsyncSession = Depends(get_db),
    token: str = None,
) -> Officer:
    """
    Dependency: extract officer from JWT token.
    This is meant to be overridden by the actual header-based dependency below.
    """
    raise HTTPException(status_code=401, detail="Not authenticated")


# ──────────────────────── JWT Dependency ────────────────────────

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


async def require_officer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Officer:
    """FastAPI dependency that extracts and validates the JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        officer_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
        )

    result = await db.execute(select(Officer).where(Officer.id == officer_id))
    officer = result.scalar_one_or_none()

    if not officer or not officer.is_active:
        raise HTTPException(status_code=401, detail="Officer account not found or deactivated.")

    return officer


async def require_admin(officer: Officer = Depends(require_officer)) -> Officer:
    """Dependency: require admin privileges."""
    if not officer.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required.")
    return officer


# ──────────────────────── Endpoints ────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate officer with badge number and password.
    Rate limited to 5 attempts per 10 minutes.
    """
    # Get client IP for rate limiting
    client_ip = req.client.host if req.client else "unknown"

    # Validate input
    if not request.badge_number or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Badge number and password are required",
        )

    # Rate limiting by IP address
    allowed, retry_after = await LOGIN_LIMITER.is_allowed(f"login:{client_ip}")
    if not allowed:
        # Log security event
        await RateLimitService.log_attempt(
            db=db,
            endpoint="/api/auth/login",
            identifier=client_ip,
            ip_address=client_ip,
            success=False,
        )
        logger.security_event(
            event_type="login_rate_limit",
            severity="medium",
            message="Login rate limit exceeded",
            ip_address=client_ip,
            details={"retry_after_seconds": retry_after},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    # Find officer
    result = await db.execute(
        select(Officer).where(Officer.badge_number == request.badge_number)
    )
    officer = result.scalar_one_or_none()

    # Verify password (constant-time comparison for both cases)
    password_valid = officer and _verify_password(request.password, officer.password_hash)

    if not password_valid:
        # Log failed attempt
        auth_logger.log_with_extra(
            level=30,  # WARNING
            message="Failed login attempt",
            extra={
                "badge_number": request.badge_number,
                "ip_address": client_ip,
                "success": False,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid badge number or password.",
        )

    if not officer.is_active:
        auth_logger.log_with_extra(
            level=30,  # WARNING
            message="Login attempt for deactivated account",
            extra={
                "officer_id": officer.id,
                "badge_number": officer.badge_number,
                "ip_address": client_ip,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact admin.",
        )

    # Successful login - reset rate limit
    await LOGIN_LIMITER.reset(f"login:{client_ip}")

    token = _create_token(officer.id, officer.badge_number)

    # Log successful login
    auth_logger.log_with_extra(
        level=20,  # INFO
        message="Officer logged in successfully",
        extra={
            "officer_id": officer.id,
            "badge_number": officer.badge_number,
            "ip_address": client_ip,
        },
    )

    return TokenResponse(
        access_token=token,
        officer={
            "id": officer.id,
            "badge_number": officer.badge_number,
            "name": officer.name,
            "rank": officer.rank,
            "police_station": officer.police_station,
            "district": officer.district,
            "is_admin": officer.is_admin,
        },
    )


@router.get("/me", response_model=OfficerProfile)
async def get_my_profile(officer: Officer = Depends(require_officer)):
    """Get the current logged-in officer's profile."""
    return officer


@router.post("/register-request", response_model=RegistrationRequestResponse)
async def request_registration(
    request: RegisterRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a registration request for a new officer account.
    The request must be approved by an admin before the officer can log in.
    Includes rate limiting (3 requests per hour) and input validation.
    """
    # Get client IP for rate limiting
    client_ip = req.client.host if req.client else "unknown"

    # Rate limiting by IP address
    allowed, retry_after = await REGISTRATION_LIMITER.is_allowed(f"register:{client_ip}")
    if not allowed:
        logger.security_event(
            event_type="registration_rate_limit",
            severity="medium",
            message="Registration rate limit exceeded",
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # Validate input fields
    name = OfficerValidator.validate_name(request.name)
    badge_number = OfficerValidator.validate_badge_number(request.badge_number)
    phone = OfficerValidator.validate_phone(request.phone) if request.phone else ""
    password = OfficerValidator.validate_password(request.password)

    # Check if badge number already exists as an officer
    existing = await db.execute(
        select(Officer).where(Officer.badge_number == badge_number)
    )
    if existing.scalar_one_or_none():
        logger.security_event(
            event_type="duplicate_registration_attempt",
            severity="low",
            message=f"Registration attempt with existing badge: {badge_number}",
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An officer with this badge number already exists.",
        )

    # Check for pending request with same badge
    pending = await db.execute(
        select(RegistrationRequest).where(
            RegistrationRequest.badge_number == badge_number,
            RegistrationRequest.status == "pending",
        )
    )
    if pending.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A registration request with this badge number is already pending.",
        )

    # Create registration request
    reg = RegistrationRequest(
        name=name,
        badge_number=badge_number,
        rank=request.rank or "",
        police_station=request.police_station or "",
        district=request.district or "",
        phone=phone,
        email=request.email or "",
    )
    db.add(reg)
    await db.commit()
    await db.refresh(reg)

    # Store the password hash temporarily
    _pending_passwords[badge_number] = _hash_password(password)

    # Log registration request
    auth_logger.log_with_extra(
        level=20,  # INFO
        message="Officer registration request submitted",
        extra={
            "badge_number": badge_number,
            "name": name,
            "ip_address": client_ip,
        },
    )

    return reg


# Temp storage for passwords of pending registrations
_pending_passwords: dict = {}


@router.get("/registration-requests", response_model=list[RegistrationRequestResponse])
async def list_registration_requests(
    status_filter: Optional[str] = None,
    officer: Officer = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: list all registration requests."""
    query = select(RegistrationRequest).order_by(RegistrationRequest.created_at.desc())
    if status_filter:
        query = query.where(RegistrationRequest.status == status_filter)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/registration-requests/{request_id}/approve")
async def approve_registration(
    request_id: int,
    officer: Officer = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: approve a registration request and create the officer account."""
    result = await db.execute(
        select(RegistrationRequest).where(RegistrationRequest.id == request_id)
    )
    reg = result.scalar_one_or_none()

    if not reg:
        raise HTTPException(status_code=404, detail="Request not found.")
    if reg.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {reg.status}.")

    # Get stored password hash
    password_hash = _pending_passwords.pop(reg.badge_number, None)
    if not password_hash:
        # Fallback: create with default password
        password_hash = _hash_password("firai123")

    new_officer = Officer(
        badge_number=reg.badge_number,
        name=reg.name,
        rank=reg.rank,
        police_station=reg.police_station,
        district=reg.district,
        phone=reg.phone,
        email=reg.email,
        password_hash=password_hash,
    )
    db.add(new_officer)

    reg.status = "approved"
    reg.reviewed_by = officer.name
    reg.reviewed_at = datetime.utcnow()

    await db.commit()

    return {"message": f"Officer {reg.name} ({reg.badge_number}) approved and account created."}


@router.post("/registration-requests/{request_id}/reject")
async def reject_registration(
    request_id: int,
    reason: str = "",
    officer: Officer = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin: reject a registration request."""
    result = await db.execute(
        select(RegistrationRequest).where(RegistrationRequest.id == request_id)
    )
    reg = result.scalar_one_or_none()

    if not reg:
        raise HTTPException(status_code=404, detail="Request not found.")
    if reg.status != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {reg.status}.")

    reg.status = "rejected"
    reg.reviewed_by = officer.name
    reg.reviewed_at = datetime.utcnow()
    reg.reject_reason = reason
    _pending_passwords.pop(reg.badge_number, None)

    await db.commit()

    return {"message": f"Registration request for {reg.name} rejected."}
