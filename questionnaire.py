from typing import Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class CompanySize(str, Enum):
    STARTUP = "startup"
    SME = "sme"
    ENTERPRISE = "enterprise"


class Industry(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    EDUCATION = "education"
    GOVERNMENT = "government"
    TECHNOLOGY = "technology"
    OTHER = "other"


class AIUseCase(str, Enum):
    CUSTOMER_SERVICE = "customer_service"
    DECISION_MAKING = "decision_making"
    CONTENT_GENERATION = "content_generation"
    PREDICTION = "prediction"
    AUTOMATION = "automation"
    OTHER = "other"


class GeographicLocation(str, Enum):
    US = "us"
    EU = "eu"
    UK = "uk"
    CANADA = "canada"
    ASIA = "asia"
    OTHER = "other"


class ComplianceLevel(str, Enum):
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"


class QuestionnaireResponse(BaseModel):
    company_size: CompanySize = Field(..., description="Size of the organization")
    industry: Industry = Field(..., description="Primary industry sector")
    ai_use_case: AIUseCase = Field(..., description="Primary AI use case")
    user_facing: bool = Field(..., description="Is the AI system user-facing?")
    handles_personal_data: bool = Field(..., description="Does the system handle personal data?")
    high_risk: bool = Field(..., description="Is this a high-risk application?")
    geographic_location: GeographicLocation = Field(..., description="Primary geographic location")
    existing_compliance: ComplianceLevel = Field(..., description="Current compliance maturity")
    additional_context: str = Field(default="", description="Additional context or requirements")


def get_questions() -> List[Dict[str, Any]]:
    """Return the list of questions for the UI"""
    return [
        {
            "key": "company_size",
            "label": "What is your organization size?",
            "type": "select",
            "options": [
                {"value": "startup", "label": "Startup (1-50 employees)"},
                {"value": "sme", "label": "SME (51-500 employees)"},
                {"value": "enterprise", "label": "Enterprise (500+ employees)"}
            ],
            "required": True
        },
        {
            "key": "industry",
            "label": "What is your primary industry?",
            "type": "select",
            "options": [
                {"value": "healthcare", "label": "Healthcare"},
                {"value": "finance", "label": "Finance & Banking"},
                {"value": "retail", "label": "Retail & E-commerce"},
                {"value": "education", "label": "Education"},
                {"value": "government", "label": "Government & Public Sector"},
                {"value": "technology", "label": "Technology"},
                {"value": "other", "label": "Other"}
            ],
            "required": True
        },
        {
            "key": "ai_use_case",
            "label": "What is your primary AI use case?",
            "type": "select",
            "options": [
                {"value": "customer_service", "label": "Customer Service & Support"},
                {"value": "decision_making", "label": "Decision Support Systems"},
                {"value": "content_generation", "label": "Content Generation"},
                {"value": "prediction", "label": "Prediction & Forecasting"},
                {"value": "automation", "label": "Process Automation"},
                {"value": "other", "label": "Other"}
            ],
            "required": True
        },
        {
            "key": "user_facing",
            "label": "Is your AI system directly user-facing?",
            "type": "boolean",
            "required": True
        },
        {
            "key": "handles_personal_data",
            "label": "Does your system handle personal or sensitive data?",
            "type": "boolean",
            "required": True
        },
        {
            "key": "high_risk",
            "label": "Would you classify this as a high-risk AI application? (e.g., healthcare decisions, financial lending, hiring)",
            "type": "boolean",
            "required": True
        },
        {
            "key": "geographic_location",
            "label": "What is your primary geographic location/market?",
            "type": "select",
            "options": [
                {"value": "us", "label": "United States"},
                {"value": "eu", "label": "European Union"},
                {"value": "uk", "label": "United Kingdom"},
                {"value": "canada", "label": "Canada"},
                {"value": "asia", "label": "Asia Pacific"},
                {"value": "other", "label": "Other"}
            ],
            "required": True
        },
        {
            "key": "existing_compliance",
            "label": "What is your current compliance/governance maturity?",
            "type": "select",
            "options": [
                {"value": "none", "label": "No formal governance"},
                {"value": "basic", "label": "Basic policies in place"},
                {"value": "advanced", "label": "Comprehensive governance framework"}
            ],
            "required": True
        },
        {
            "key": "additional_context",
            "label": "Any additional context or specific requirements? (Optional)",
            "type": "text",
            "required": False
        }
    ]


def determine_relevant_frameworks(responses: QuestionnaireResponse) -> List[str]:
    """Determine which frameworks are most relevant based on questionnaire responses"""
    frameworks = ["nist_ai_rmf"]  # NIST is always relevant
    
    if responses.geographic_location == GeographicLocation.EU:
        frameworks.append("eu_ai_act")
    
    if responses.industry == Industry.HEALTHCARE:
        frameworks.append("healthcare_ai_guidelines")
    elif responses.industry == Industry.FINANCE:
        frameworks.append("financial_ai_governance")
    
    if responses.high_risk:
        frameworks.append("high_risk_ai_requirements")
    
    if responses.handles_personal_data:
        frameworks.append("data_privacy_guidelines")
    
    return frameworks