"""
Input Validation
----------------
Validate all user inputs at API boundaries.
"""

import re
from typing import Optional, List
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator


# ──────────────────────── Narrative Validation ────────────────────────

class NarrativeValidator:
    """Validate FIR narrative text."""

    MAX_LENGTH = 10000
    MIN_LENGTH = 10
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # JavaScript
        r"javascript:",  # JavaScript protocol
        r"on\w+\s*=",  # Event handlers
        r"DROP\s+TABLE",  # SQL injection
        r"DELETE\s+FROM",  # SQL injection
        r"EXEC\s*\(",  # SQL injection
    ]

    @staticmethod
    def validate(narrative: str) -> str:
        """Validate narrative text."""
        if not narrative or not isinstance(narrative, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Narrative must be a non-empty string",
            )

        # Check length
        if len(narrative) < NarrativeValidator.MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Narrative must be at least {NarrativeValidator.MIN_LENGTH} characters",
            )

        if len(narrative) > NarrativeValidator.MAX_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Narrative must be less than {NarrativeValidator.MAX_LENGTH} characters",
            )

        # Check for dangerous patterns
        narrative_upper = narrative.upper()
        for pattern in NarrativeValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, narrative_upper, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Narrative contains invalid content",
                )

        return narrative.strip()


# ──────────────────────── File Upload Validation ────────────────────────

class FileValidator:
    """Validate file uploads."""

    MAX_SIZE_MB = 50
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/tiff",
        "image/bmp",
        "image/webp",
    }

    @staticmethod
    def validate_extension(filename: str) -> str:
        """Validate file extension."""
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # Get extension
        parts = filename.rsplit(".", 1)
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename must have an extension",
            )

        ext = f".{parts[1].lower()}"
        if ext not in FileValidator.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}",
            )

        return ext

    @staticmethod
    def validate_size(size_bytes: int) -> None:
        """Validate file size."""
        if size_bytes > FileValidator.MAX_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {FileValidator.MAX_SIZE_MB}MB limit",
            )

    @staticmethod
    def validate_mime_type(mime_type: str) -> None:
        """Validate MIME type."""
        if mime_type not in FileValidator.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File MIME type not allowed",
            )


# ──────────────────────── Officer Registration Validation ────────────────────────

class OfficerValidator:
    """Validate officer registration and profile data."""

    NAME_MIN_LENGTH = 2
    NAME_MAX_LENGTH = 200
    BADGE_MIN_LENGTH = 3
    BADGE_MAX_LENGTH = 20
    PHONE_PATTERN = r"^\d{10}$"  # 10 digits only

    @staticmethod
    def validate_name(name: str) -> str:
        """Validate officer name."""
        if not name or not isinstance(name, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name is required",
            )

        name = name.strip()

        if len(name) < OfficerValidator.NAME_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Name must be at least {OfficerValidator.NAME_MIN_LENGTH} characters",
            )

        if len(name) > OfficerValidator.NAME_MAX_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Name must not exceed {OfficerValidator.NAME_MAX_LENGTH} characters",
            )

        # Check for SQL injection patterns
        if any(c in name.lower() for c in ["'", '"', ";", "--", "/*", "*/"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name contains invalid characters",
            )

        return name

    @staticmethod
    def validate_badge_number(badge_number: str) -> str:
        """Validate badge number."""
        if not badge_number or not isinstance(badge_number, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Badge number is required",
            )

        badge_number = badge_number.strip().upper()

        if len(badge_number) < OfficerValidator.BADGE_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Badge number must be at least {OfficerValidator.BADGE_MIN_LENGTH} characters",
            )

        if len(badge_number) > OfficerValidator.BADGE_MAX_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Badge number must not exceed {OfficerValidator.BADGE_MAX_LENGTH} characters",
            )

        # Alphanumeric only
        if not re.match(r"^[A-Z0-9]+$", badge_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Badge number must contain only alphanumeric characters",
            )

        return badge_number

    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate phone number."""
        if not phone or not isinstance(phone, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number is required",
            )

        phone = phone.strip()

        if not re.match(OfficerValidator.PHONE_PATTERN, phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number must be 10 digits",
            )

        return phone

    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength."""
        if not password or not isinstance(password, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required",
            )

        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters",
            )

        # Check for complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper and has_lower and has_digit):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain uppercase, lowercase, and numbers",
            )

        return password


# ──────────────────────── IPC/BNS Section Validation ────────────────────────

class LegalSectionValidator:
    """Validate IPC/BNS section references."""

    VALID_ACTS = {"IPC", "BNS", "CrPC", "BNSS", "NDPS", "POCSO", "MVA", "KERALA_ABKARI"}
    SECTION_PATTERN = r"^[0-9]+[A-Z]*$"  # e.g., "379", "376D"

    @staticmethod
    def validate_act(act: str) -> str:
        """Validate act name."""
        if not act or not isinstance(act, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Act is required",
            )

        act = act.strip().upper()

        if act not in LegalSectionValidator.VALID_ACTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid act. Allowed acts: {', '.join(LegalSectionValidator.VALID_ACTS)}",
            )

        return act

    @staticmethod
    def validate_section(section: str) -> str:
        """Validate section number."""
        if not section or not isinstance(section, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Section is required",
            )

        section = section.strip().upper()

        if not re.match(LegalSectionValidator.SECTION_PATTERN, section):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid section format (e.g., '379', '376D')",
            )

        return section

    @staticmethod
    def validate_act_section(act_section: str) -> tuple:
        """Validate and parse 'ACT:SECTION' format."""
        if not act_section or not isinstance(act_section, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Act:Section format required (e.g., 'IPC:379')",
            )

        parts = act_section.split(":")
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format must be 'ACT:SECTION' (e.g., 'IPC:379')",
            )

        act = LegalSectionValidator.validate_act(parts[0])
        section = LegalSectionValidator.validate_section(parts[1])

        return act, section


# ──────────────────────── Email Validation ────────────────────────

class EmailValidator:
    """Validate email addresses."""

    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    @staticmethod
    def validate(email: str) -> str:
        """Validate email address."""
        if not email or not isinstance(email, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required",
            )

        email = email.strip().lower()

        if not re.match(EmailValidator.EMAIL_PATTERN, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format",
            )

        if len(email) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is too long",
            )

        return email


# ──────────────────────── FIR Metadata Validation ────────────────────────

class FIRValidator:
    """Validate FIR metadata."""

    FIR_NUMBER_PATTERN = r"^\d{4}/\d{4}$"  # e.g., "0017/2025"

    @staticmethod
    def validate_fir_number(fir_number: str) -> str:
        """Validate FIR number format."""
        if not fir_number or not isinstance(fir_number, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FIR number is required",
            )

        fir_number = fir_number.strip()

        if not re.match(FIRValidator.FIR_NUMBER_PATTERN, fir_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="FIR number must be in format: XXXX/YYYY (e.g., 0017/2025)",
            )

        return fir_number

    @staticmethod
    def validate_police_station(station: str) -> str:
        """Validate police station name."""
        if not station or not isinstance(station, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Police station is required",
            )

        station = station.strip()

        if len(station) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Police station name too long",
            )

        # Check for SQL injection
        if any(c in station.lower() for c in ["'", '"', ";", "--"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Police station contains invalid characters",
            )

        return station
