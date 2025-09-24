from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# =====================
# User Profile Models
# =====================

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    DIPLOMA = "diploma"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"

class UserProfile(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=16, le=35)
    education_level: EducationLevel
    field_of_study: str = Field(..., min_length=2, max_length=100)
    skills: List[str] = Field(..., min_items=1, max_items=10)
    interests: List[str] = Field(..., min_items=1, max_items=8)
    location: str = Field(..., min_length=2, max_length=100)
    preferred_locations: List[str] = Field(default=[], max_items=5)
    experience_level: str = Field(default="beginner")
    language_preference: str = Field(default="english")

# =====================
# Internship Models
# =====================

class Internship(BaseModel):
    id: str
    title: str
    company: str
    location: str
    sector: str
    duration: str
    stipend: Optional[str]
    description: str
    required_skills: List[str]
    education_requirement: str
    experience_required: str
    remote_option: bool
    application_deadline: str

# =====================
# Recommendation Models
# =====================

class Recommendation(BaseModel):
    internship: Internship
    match_score: float
    match_reasons: List[str]

class RecommendationResponse(BaseModel):
    user_name: str
    recommendations: List[Recommendation]
    total_matches: int

# =====================
# Application Models
# =====================

class Application(BaseModel):
    application_id: str
    user_id: str
    internship_id: str
    status: str = "Applied"

class ApplicationResponse(BaseModel):
    applications: List[Application]
    total: int
