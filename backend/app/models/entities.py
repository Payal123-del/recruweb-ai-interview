import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Any, Dict
from sqlalchemy import (
    String, Boolean, Integer, Float, Text, ForeignKey, DateTime, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Enums
class CompanyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class UserRoleType(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    RECRUITER = "RECRUITER"
    INTERVIEWER = "INTERVIEWER"
    CANDIDATE = "CANDIDATE"


class JobStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class CandidateStatus(str, Enum):
    INVITED = "INVITED"
    REGISTERED = "REGISTERED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEW_STARTED = "INTERVIEW_STARTED"
    INTERVIEW_COMPLETED = "INTERVIEW_COMPLETED"
    UNDER_REVIEW = "UNDER_REVIEW"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"


class InterviewStatus(str, Enum):
    PENDING = "PENDING"
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    EVALUATING = "EVALUATING"
    EVALUATED = "EVALUATED"
    REPORT_GENERATED = "REPORT_GENERATED"
    EVALUATION_FAILED = "EVALUATION_FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class InterviewType(str, Enum):
    TECHNICAL = "TECHNICAL"
    HR = "HR"
    BEHAVIORAL = "BEHAVIORAL"
    MIXED = "MIXED"
    ROBOTICS_SPECIALIZED = "ROBOTICS_SPECIALIZED"


class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    EXPERT = "EXPERT"


class QuestionType(str, Enum):
    TECHNICAL = "TECHNICAL"
    HR = "HR"
    BEHAVIORAL = "BEHAVIORAL"
    COMMUNICATION = "COMMUNICATION"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    SITUATIONAL = "SITUATIONAL"


class RecommendationType(str, Enum):
    STRONG_HIRE = "STRONG_HIRE"
    HIRE = "HIRE"
    CONSIDER = "CONSIDER"
    REJECT = "REJECT"
    STRONG_REJECT = "STRONG_REJECT"


class DatasetStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class ModelStatus(str, Enum):
    TRAINING = "TRAINING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    ARCHIVED = "ARCHIVED"


# 1. Company / Tenant
class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    status: Mapped[str] = mapped_column(String(50), default=CompanyStatus.ACTIVE.value, index=True)
    subscription_plan: Mapped[str] = mapped_column(String(50), default="ENTERPRISE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="company", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="company", cascade="all, delete-orphan")
    custom_questions = relationship("Question", back_populates="company", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="company", cascade="all, delete-orphan")


# 2. RBAC Permissions & Roles
class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    permission_id: Mapped[str] = mapped_column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), index=True)
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)


# 3. User
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRoleType.RECRUITER.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    company = relationship("Company", back_populates="users")


# 4. Job
class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(100), default="Remote")
    employment_type: Mapped[str] = mapped_column(String(50), default="Full-time")
    experience_level: Mapped[str] = mapped_column(String(50), default="Mid-Senior")
    required_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    salary_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=JobStatus.PUBLISHED.value, index=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    company = relationship("Company", back_populates="jobs")
    interviews = relationship("Interview", back_populates="job", cascade="all, delete-orphan")


# 5. Candidate
class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resume_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    experience_years: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    education: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_field: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    detected_fields: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(50), default=CandidateStatus.INVITED.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    company = relationship("Company", back_populates="candidates")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_candidate_tenant_email"),)


# 5.1 Universal Professional Fields
class Field(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="Engineering & Tech")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), default="Briefcase")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    roles = relationship("FieldRole", back_populates="field", cascade="all, delete-orphan")
    skills = relationship("FieldSkill", back_populates="field", cascade="all, delete-orphan")


class FieldRole(Base):
    __tablename__ = "field_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    field_id: Mapped[str] = mapped_column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    role_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    experience_levels: Mapped[List[str]] = mapped_column(JSON, default=lambda: ["Fresher (0-1 yrs)", "Junior (1-3 yrs)", "Mid-Level (3-5 yrs)", "Senior (5-8 yrs)", "Lead/Principal (8+ yrs)"])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    field = relationship("Field", back_populates="roles")


class FieldSkill(Base):
    __tablename__ = "field_skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    field_id: Mapped[str] = mapped_column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), default="Technical")
    importance_weight: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    field = relationship("Field", back_populates="skills")


class FieldCompetencyFramework(Base):
    __tablename__ = "field_competencies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    field_id: Mapped[str] = mapped_column(String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    competency_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_weight: Mapped[float] = mapped_column(Float, default=0.25)
    rubric_guidelines: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)


# 6. Question Bank (Global and Company-Specific across all Fields)
class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True)
    field_name: Mapped[str] = mapped_column(String(100), index=True, default="Universal")
    role_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(100), index=True, default="General")
    subfield: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), default=QuestionType.TECHNICAL.value, index=True)
    difficulty: Mapped[str] = mapped_column(String(50), default=DifficultyLevel.MEDIUM.value, index=True)
    experience_level: Mapped[str] = mapped_column(String(50), default="Mid-Level")
    skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    expected_topics: Mapped[List[str]] = mapped_column(JSON, default=list)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, default=120)
    scoring_rubric: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    followup_rules: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    company = relationship("Company", back_populates="custom_questions")


# 7. Interview & Secure Invitation
class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), default="Universal", index=True)
    target_role: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    interview_type: Mapped[str] = mapped_column(String(50), default=InterviewType.TECHNICAL.value)
    difficulty: Mapped[str] = mapped_column(String(50), default=DifficultyLevel.MEDIUM.value)
    is_adaptive: Mapped[bool] = mapped_column(Boolean, default=False)
    focus_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    num_questions: Mapped[int] = mapped_column(Integer, default=5)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, default=45)
    camera_required: Mapped[bool] = mapped_column(Boolean, default=True)
    mic_required: Mapped[bool] = mapped_column(Boolean, default=True)
    recording_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_candidate_result_view: Mapped[bool] = mapped_column(Boolean, default=True)
    scoring_weights: Mapped[Dict[str, float]] = mapped_column(JSON, default=lambda: {
        "technical": 0.45,
        "problem_solving": 0.25,
        "communication": 0.15,
        "behavioral": 0.15
    })
    candidate_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=InterviewStatus.PENDING.value, index=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    company = relationship("Company", back_populates="interviews")
    job = relationship("Job", back_populates="interviews")
    candidate = relationship("Candidate", back_populates="interviews")
    invitations = relationship("Invitation", back_populates="interview", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="interview", cascade="all, delete-orphan")
    evaluation = relationship("Evaluation", back_populates="interview", uselist=False, cascade="all, delete-orphan")
    report = relationship("Report", back_populates="interview", uselist=False, cascade="all, delete-orphan")


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_email: Mapped[str] = mapped_column(String(255), nullable=False)
    secure_token: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    interview = relationship("Interview", back_populates="invitations")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1)
    allocated_seconds: Mapped[int] = mapped_column(Integer, default=120)

    interview = relationship("Interview", back_populates="interview_questions")
    question = relationship("Question")


# 8. Answers & Recordings
class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    interview = relationship("Interview", back_populates="answers")
    question = relationship("Question")
    recording = relationship("Recording", back_populates="answer", uselist=False, cascade="all, delete-orphan")


class Recording(Base):
    __tablename__ = "recordings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_id: Mapped[str] = mapped_column(String(36), ForeignKey("answers.id", ondelete="CASCADE"), nullable=False, unique=True)
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    mime_type: Mapped[str] = mapped_column(String(100), default="video/webm")
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    answer = relationship("Answer", back_populates="recording")


# 9. AI Evaluations & Candidate Reports
class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    evaluation_status: Mapped[str] = mapped_column(String(50), default="COMPLETED", index=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    technical_score: Mapped[float] = mapped_column(Float, default=0.0)
    communication_score: Mapped[float] = mapped_column(Float, default=0.0)
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0)
    problem_solving_score: Mapped[float] = mapped_column(Float, default=0.0)
    behavioral_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_indicator: Mapped[float] = mapped_column(Float, default=0.90)
    strengths: Mapped[List[str]] = mapped_column(JSON, default=list)
    weaknesses: Mapped[List[str]] = mapped_column(JSON, default=list)
    missing_topics: Mapped[List[str]] = mapped_column(JSON, default=list)
    question_breakdown: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(String(50), default=RecommendationType.CONSIDER.value)
    engine_version: Mapped[str] = mapped_column(String(50), default="internal-v1")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    interview = relationship("Interview", back_populates="evaluation")
    question_evaluations = relationship("QuestionEvaluation", back_populates="evaluation", cascade="all, delete-orphan")


class QuestionEvaluation(Base):
    __tablename__ = "question_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluation_id: Mapped[str] = mapped_column(String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    technical_score: Mapped[float] = mapped_column(Float, default=0.0)
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0)
    communication_score: Mapped[float] = mapped_column(Float, default=0.0)
    problem_solving_score: Mapped[float] = mapped_column(Float, default=0.0)
    behavioral_score: Mapped[float] = mapped_column(Float, default=0.0)
    detected_topics: Mapped[List[str]] = mapped_column(JSON, default=list)
    missing_topics: Mapped[List[str]] = mapped_column(JSON, default=list)
    positive_indicators: Mapped[List[str]] = mapped_column(JSON, default=list)
    negative_indicators: Mapped[List[str]] = mapped_column(JSON, default=list)
    strengths: Mapped[List[str]] = mapped_column(JSON, default=list)
    weaknesses: Mapped[List[str]] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    evaluation = relationship("Evaluation", back_populates="question_evaluations")
    question = relationship("Question")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    pdf_storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    recruiter_decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recruiter_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_published_to_candidate: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    interview = relationship("Interview", back_populates="report")


# 10. AI Datasets & Models
class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="Question Dataset")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    records_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default=DatasetStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    file_storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    records_count: Mapped[int] = mapped_column(Integer, default=0)
    validation_status: Mapped[str] = mapped_column(String(50), default="PASSED")
    validation_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)

    dataset = relationship("Dataset", back_populates="versions")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version_tag: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), default="Deterministic-NLP-Rubric")
    status: Mapped[str] = mapped_column(String(50), default=ModelStatus.PRODUCTION.value)
    metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)


# 11. Immutable Audit Log
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, index=True)

    company = relationship("Company", back_populates="audit_logs")


# 12. Notifications & System Settings
class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="INFO")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)
