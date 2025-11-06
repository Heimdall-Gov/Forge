"""
Pytest configuration and fixtures for testing
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set up test environment variables
os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
os.environ["LLM_MODEL"] = "claude-sonnet-4-20250514"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from database import Base, get_db
from app import app
from questionnaire import QuestionnaireResponse


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function"""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_questionnaire_response():
    """Sample questionnaire response for testing"""
    return QuestionnaireResponse(
        organization_type="Startup",
        industry="Healthcare",
        regions=["EU", "US"],
        organization_size="50-200",
        main_purpose="Medical diagnosis support system using AI",
        data_types=["medical", "personal"],
        stage="development",
        developer="in-house",
        criticality="high",
        policies="No formal AI policies yet",
        designated_team="No",
        approval_process="Informal review by CTO",
        record_keeping="Version control for code only",
        affects_rights="Yes - healthcare decisions",
        human_oversight="Human-in-the-loop",
        testing="Basic accuracy testing",
        complaint_mechanism="No",
        goal="Compliance readiness",
        preference="Detailed framework",
        standards=["EU AI Act", "NIST AI RMF"]
    )


@pytest.fixture
def sample_eu_classification_result():
    """Sample EU AI Act classification result"""
    return {
        "eu_classification": "HIGH_RISK",
        "rationale": "The system is used for medical diagnosis, which falls under Annex III category 2 - healthcare critical infrastructure",
        "annex_iii_categories": ["Healthcare - medical diagnosis"],
        "confidence": 0.92,
        "ambiguities": []
    }


@pytest.fixture
def sample_eu_requirements_result():
    """Sample EU requirements result"""
    return {
        "applicable_articles": [9, 10, 11, 12, 13, 14, 15],
        "requirements": [
            {
                "article": 9,
                "title": "Risk Management System",
                "description": "Establish, implement, document risk management throughout lifecycle",
                "applies_to": "provider",
                "mandatory": True
            },
            {
                "article": 14,
                "title": "Human Oversight",
                "description": "Design system to enable effective human oversight",
                "applies_to": "provider",
                "mandatory": True
            }
        ]
    }


@pytest.fixture
def sample_nist_requirements_result():
    """Sample NIST requirements result"""
    return {
        "applicable_subcategories": ["GOVERN.1.1", "GOVERN.1.2", "MAP.1.1", "MAP.3.5", "MEASURE.2.4"],
        "priority_functions": ["GOVERN", "MAP", "MEASURE"],
        "subcategory_details": [
            {
                "id": "GOVERN.1.1",
                "function": "GOVERN",
                "category": "1",
                "description": "Legal and regulatory requirements understood and documented",
                "rationale": "System must comply with healthcare regulations"
            },
            {
                "id": "MAP.3.5",
                "function": "MAP",
                "category": "3",
                "description": "Human oversight processes defined",
                "rationale": "High-risk medical AI requires human oversight"
            }
        ]
    }


@pytest.fixture
def sample_gap_analysis_result():
    """Sample gap analysis result"""
    return {
        "gaps": [
            {
                "requirement_id": "Article_14",
                "framework": "EU_AI_ACT",
                "requirement_title": "Human Oversight",
                "status": "missing",
                "severity": "critical",
                "current_state": "No documented human oversight process",
                "recommendations": {
                    "implementation_steps": [
                        "Define roles: identify who monitors AI decisions",
                        "Implement override mechanism in system UI",
                        "Document human review procedures"
                    ],
                    "examples": [
                        "Healthcare AI: Radiologist reviews all AI-flagged cases"
                    ],
                    "effort_estimate": "4-6 weeks",
                    "resources_needed": [
                        "Human factors expert",
                        "UX designer for override interface"
                    ],
                    "common_mistakes": [
                        "Making override too difficult/time-consuming"
                    ]
                }
            }
        ],
        "compliance_score": 35,
        "score_breakdown": {
            "critical_gaps": 4,
            "high_gaps": 6,
            "medium_gaps": 5,
            "low_gaps": 2,
            "implemented": 3
        }
    }


@pytest.fixture
def sample_full_assessment_result(
    sample_eu_classification_result,
    sample_eu_requirements_result,
    sample_nist_requirements_result,
    sample_gap_analysis_result
):
    """Sample complete assessment result"""
    return {
        "timestamp": "2025-11-06T10:30:00Z",
        "organization_name": "Startup - Healthcare",
        "processing_time_seconds": 78,
        "eu_ai_act": {
            **sample_eu_classification_result,
            "applicable_articles": sample_eu_requirements_result["applicable_articles"],
            "requirements": sample_eu_requirements_result["requirements"]
        },
        "nist_ai_rmf": sample_nist_requirements_result,
        "gap_analysis": sample_gap_analysis_result,
        "cross_framework_mapping": {
            "eu_to_nist": {
                "Article_14": ["GOVERN.3.2", "MAP.3.5", "MANAGE.2.4"]
            },
            "nist_to_eu": {
                "MAP.3.5": ["Article_14"]
            }
        }
    }


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response for testing"""
    class MockContent:
        def __init__(self, input_data):
            self.type = "tool_use"
            self.input = input_data

    class MockResponse:
        def __init__(self, input_data):
            self.content = [MockContent(input_data)]

    return MockResponse
