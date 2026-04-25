from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# ──────────────────────── Request Schemas ────────────────────────

class NarrativeAnalyzeRequest(BaseModel):
    narrative: str = Field(..., description="FIR narrative text (Malayalam or English)")
    top_k: int = Field(5, description="Number of similar FIRs to return")


class LegalQueryRequest(BaseModel):
    question: str = Field(..., description="Legal question from the officer")
    fir_id: Optional[int] = Field(None, description="Related FIR ID for context")


class TranslateRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_lang: str = Field("ml", description="Source language code (ml=Malayalam, en=English)")
    target_lang: str = Field("en", description="Target language code")


class BulkUploadResponse(BaseModel):
    total_files: int
    processed: int
    failed: int
    skipped_duplicates: int = 0
    errors: List[str] = []
    duplicates: List[str] = []  # filenames that were skipped as duplicates


# ──────────────────────── Response Schemas ────────────────────────

class AccusedResponse(BaseModel):
    id: int
    name: Optional[str] = None
    father_name: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


class FIRListItem(BaseModel):
    id: int
    file_name: Optional[str] = None
    fir_number: Optional[str] = None
    fir_date: Optional[date] = None
    district: Optional[str] = None
    police_station: Optional[str] = None
    place: Optional[str] = None
    crime_type: Optional[str] = None
    severity: Optional[str] = None

    narrative: Optional[str] = None
    summary_en: Optional[str] = None
    acts: Optional[list] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FIRDetail(FIRListItem):
    narrative_en: Optional[str] = None
    narrative_ml: Optional[str] = None
    full_text: Optional[str] = None
    recommended_steps: Optional[list] = None
    key_entities: Optional[dict] = None
    complainant: Optional[dict] = None
    accused: List[AccusedResponse] = []

    class Config:
        from_attributes = True


class SimilarFIR(BaseModel):
    id: int
    file_name: Optional[str] = None
    crime_type: Optional[str] = None
    severity: Optional[str] = None
    narrative: Optional[str] = None
    summary_en: Optional[str] = None
    similarity_score: float
    acts: Optional[list] = None


class AnalysisResult(BaseModel):
    crime_type: Optional[str] = None
    severity: Optional[str] = None

    narrative: Optional[str] = None  # The extracted/input narrative
    fir_number: Optional[str] = None
    summary_en: Optional[str] = None
    ipc_sections: Optional[list] = None
    recommended_steps: Optional[list] = None
    key_entities: Optional[dict] = None
    similar_firs: List[SimilarFIR] = []

    # Duplicate detection
    is_duplicate: bool = False
    duplicate_of_id: Optional[int] = None  # ID of the existing FIR if duplicate


class DashboardStats(BaseModel):
    total_firs: int = 0
    crime_type_breakdown: dict = {}
    severity_breakdown: dict = {}
    recent_firs: List[FIRListItem] = []
    monthly_trend: dict = {}


class MOPatternResponse(BaseModel):
    id: int
    pattern_name: str
    description: Optional[str] = None
    crime_type: Optional[str] = None
    occurrence_count: int
    linked_fir_ids: Optional[list] = None

    class Config:
        from_attributes = True


class LegalResponse(BaseModel):
    answer: str
    relevant_sections: Optional[list] = None
    source_firs: Optional[list] = None


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    engine: str = "none"  # 'bhashini', 'google', or 'none'
