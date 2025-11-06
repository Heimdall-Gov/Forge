import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# Database URL from environment or default to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./forge.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Assessment(Base):
    """
    Assessment model matching PRD database schema requirements.
    Stores the complete assessment including questionnaire responses and all LLM call results.
    """
    __tablename__ = "assessments"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Organization info
    organization_name = Column(String(255), index=True)

    # Questionnaire responses (full JSON)
    questionnaire_responses = Column(JSON, nullable=False)

    # Status tracking
    status = Column(String(50), default="pending", index=True)
    # Status values: pending, processing, completed, failed

    # Results from each LLM call
    eu_classification = Column(String(50))  # PROHIBITED, HIGH_RISK, LIMITED_RISK, MINIMAL_RISK
    eu_requirements = Column(JSON)  # Full EU requirements result
    nist_requirements = Column(JSON)  # Full NIST requirements result
    gaps = Column(JSON)  # Gap analysis result
    compliance_score = Column(Integer)  # 0-100 score
    cross_framework_mapping = Column(JSON)  # Cross-framework mapping

    # Full result for retrieval (combined result)
    full_result = Column(JSON)

    # Metadata
    processing_time_seconds = Column(Integer)
    error_message = Column(Text)

    def to_dict(self):
        """Convert assessment to dictionary for API responses"""
        return {
            "assessment_id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "organization_name": self.organization_name,
            "status": self.status,
            "eu_classification": self.eu_classification,
            "compliance_score": self.compliance_score,
            "processing_time_seconds": self.processing_time_seconds,
            "error_message": self.error_message,
            "full_result": self.full_result
        }


def init_db():
    """Initialize the database, creating all tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD operations
def create_assessment(db, questionnaire_responses: dict, organization_name: str = None) -> Assessment:
    """Create a new assessment record"""
    assessment = Assessment(
        id=str(uuid.uuid4()),
        organization_name=organization_name,
        questionnaire_responses=questionnaire_responses,
        status="pending"
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(db, assessment_id: str) -> Optional[Assessment]:
    """Get an assessment by ID"""
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()


def update_assessment(db, assessment_id: str, **kwargs) -> Optional[Assessment]:
    """Update an assessment with new data"""
    assessment = get_assessment(db, assessment_id)
    if assessment:
        for key, value in kwargs.items():
            if hasattr(assessment, key):
                setattr(assessment, key, value)
        db.commit()
        db.refresh(assessment)
    return assessment


def update_assessment_status(db, assessment_id: str, status: str, error_message: str = None) -> Optional[Assessment]:
    """Update assessment status"""
    return update_assessment(db, assessment_id, status=status, error_message=error_message)


def save_assessment_results(
    db,
    assessment_id: str,
    eu_classification: str,
    eu_requirements: dict,
    nist_requirements: dict,
    gaps: dict,
    compliance_score: int,
    cross_framework_mapping: dict,
    full_result: dict,
    processing_time_seconds: int
) -> Optional[Assessment]:
    """Save all assessment results to database"""
    return update_assessment(
        db,
        assessment_id,
        status="completed",
        eu_classification=eu_classification,
        eu_requirements=eu_requirements,
        nist_requirements=nist_requirements,
        gaps=gaps,
        compliance_score=compliance_score,
        cross_framework_mapping=cross_framework_mapping,
        full_result=full_result,
        processing_time_seconds=processing_time_seconds
    )


def list_assessments(db, skip: int = 0, limit: int = 100, organization_name: str = None):
    """List assessments with optional filtering"""
    query = db.query(Assessment)
    if organization_name:
        query = query.filter(Assessment.organization_name == organization_name)
    return query.order_by(Assessment.created_at.desc()).offset(skip).limit(limit).all()
