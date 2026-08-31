from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.entities import Field, FieldRole, FieldSkill, User
from app.schemas.field import (
    FieldRead, FieldCreate, FieldUpdate, FieldRoleRead, FieldSkillRead,
    ProfileAnalysisRequest, FieldDetectionResponse, DetectedFieldItem
)
from app.schemas.common import StandardResponse, MessageResponse
from app.ai.field_registry import UniversalFieldRegistry
from app.ai.field_detector import FieldDetectionEngine
from app.api.deps import get_current_user, require_permission

router = APIRouter(prefix="/fields", tags=["Universal Professional Fields"])


@router.get("", response_model=StandardResponse[List[Dict[str, Any]]])
async def list_all_fields(
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns full list of available professional career fields from both the
    registry and custom database entries.
    """
    all_fields = UniversalFieldRegistry.get_all_fields()

    # Also load custom fields from DB
    db_fields = (await db.execute(select(Field).where(Field.is_active == True))).scalars().all()
    existing_names = {f["name"].lower() for f in all_fields}

    for dbf in db_fields:
        if dbf.name.lower() not in existing_names:
            all_fields.append({
                "id": dbf.id,
                "name": dbf.name,
                "slug": dbf.slug,
                "category": dbf.category,
                "icon": dbf.icon or "Briefcase",
                "description": dbf.description or "",
                "roles": [r.role_name for r in dbf.roles] if dbf.roles else [f"{dbf.name} Specialist"],
                "skills": [s.skill_name for s in dbf.skills] if dbf.skills else [dbf.name],
                "interview_types": ["Technical", "Problem Solving", "Behavioral", "Mixed"],
                "scoring_weights": {"technical": 0.40, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.15},
                "is_custom": dbf.is_custom
            })

    # Optional search filtering
    if search:
        s_lower = search.lower().strip()
        all_fields = [
            f for f in all_fields
            if s_lower in f["name"].lower()
            or s_lower in f.get("category", "").lower()
            or any(s_lower in r.lower() for r in f.get("roles", []))
            or any(s_lower in sk.lower() for sk in f.get("skills", []))
        ]

    if category:
        all_fields = [f for f in all_fields if f.get("category", "").lower() == category.lower()]

    return StandardResponse(data=all_fields)


@router.get("/{field_name}", response_model=StandardResponse[Dict[str, Any]])
async def get_field_details(
    field_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves full role options, skills, and interview types for a specific field.
    """
    data = UniversalFieldRegistry.get_field_data(field_name)
    if not data:
        # Check DB
        db_f = (await db.execute(select(Field).where(Field.name.ilike(field_name)))).scalars().first()
        if db_f:
            data = {
                "name": db_f.name,
                "slug": db_f.slug,
                "category": db_f.category,
                "icon": db_f.icon or "Briefcase",
                "description": db_f.description or "",
                "roles": [r.role_name for r in db_f.roles] if db_f.roles else [f"{db_f.name} Specialist"],
                "skills": [s.skill_name for s in db_f.skills] if db_f.skills else [db_f.name],
                "interview_types": ["Technical", "Problem Solving", "Behavioral", "Mixed"],
                "scoring_weights": {"technical": 0.40, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.15},
                "is_custom": db_f.is_custom
            }
        else:
            # Dynamically construct fallback for niche or custom field
            data = UniversalFieldRegistry.register_custom_field(field_name)

    return StandardResponse(data=data)


@router.post("", response_model=StandardResponse[Dict[str, Any]])
async def create_field(
    payload: FieldCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new field into the universal ecosystem.
    Can be used by Super Admin or candidate requesting a custom field.
    """
    existing = (await db.execute(select(Field).where(Field.name.ilike(payload.name)))).scalars().first()
    if existing:
        return StandardResponse(message="Field already exists", data={"id": existing.id, "name": existing.name})

    slug = payload.name.lower().replace(" ", "-").replace("&", "and")
    new_field = Field(
        name=payload.name,
        slug=slug,
        category=payload.category,
        description=payload.description or f"Professional career field for {payload.name}.",
        icon=payload.icon or "Briefcase",
        is_custom=True,
        is_active=True
    )
    db.add(new_field)
    await db.flush()

    # Add roles
    roles = payload.roles or [f"{payload.name} Specialist", f"{payload.name} Lead"]
    for r_name in roles:
        db.add(FieldRole(field_id=new_field.id, role_name=r_name))

    # Add skills
    skills = payload.skills or [payload.name, "Domain Analysis", "Problem Solving"]
    for s_name in skills:
        db.add(FieldSkill(field_id=new_field.id, skill_name=s_name))

    await db.flush()

    # Also register in runtime registry
    registered = UniversalFieldRegistry.register_custom_field(
        field_name=payload.name,
        category=payload.category,
        description=payload.description,
        roles=roles,
        skills=skills
    )

    return StandardResponse(
        message="New professional career field successfully registered",
        data={"id": new_field.id, **registered}
    )


@router.post("/detect", response_model=StandardResponse[FieldDetectionResponse])
async def detect_candidate_fields(
    payload: ProfileAnalysisRequest
):
    """
    Analyzes resume text, skill list, and education using internal NLP to recommend
    ranked career fields with internal confidence ranking indicators.
    Zero external LLM API dependencies.
    """
    detector = FieldDetectionEngine()
    detected = detector.detect_fields(
        resume_text=payload.resume_text,
        skills=payload.skills,
        job_title=payload.job_title,
        job_description=payload.job_description,
        education=payload.education
    )

    top_field = detected[0]["field"] if detected else "Software Engineering"

    # Extract clean skills
    skills_extracted = payload.skills
    if not skills_extracted and payload.resume_text:
        # Simple token extraction
        raw_words = payload.resume_text.replace(",", " ").split()
        skills_extracted = [w for w in raw_words if len(w) > 3][:8]

    return StandardResponse(
        message="Candidate profile analyzed successfully",
        data=FieldDetectionResponse(
            detected_fields=[DetectedFieldItem(**d) for d in detected],
            top_recommended_field=top_field,
            skills_extracted=skills_extracted
        )
    )
