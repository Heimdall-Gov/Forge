from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class OrganizationType(str, Enum):
    STARTUP = "Startup"
    ENTERPRISE = "Enterprise"
    ACADEMIC = "Academic"
    GOVERNMENT = "Government"
    NONPROFIT = "Nonprofit"
    REGULATED_ENTITY = "Regulated Entity"
    OTHER = "Other"


class Industry(str, Enum):
    HEALTHCARE = "Healthcare"
    FINANCE = "Finance"
    ENERGY = "Energy"
    DEFENSE = "Defense"
    CONSUMER_TECH = "Consumer Tech"
    RETAIL = "Retail"
    EDUCATION = "Education"
    TRANSPORTATION = "Transportation"
    MANUFACTURING = "Manufacturing"
    OTHER = "Other"


class OrganizationSize(str, Enum):
    SMALL = "1-50"
    MEDIUM = "50-200"
    LARGE = "200-1000"
    ENTERPRISE = "1000+"


class AIStage(str, Enum):
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    POST_MARKET = "post-market monitoring"


class Developer(str, Enum):
    IN_HOUSE = "in-house"
    VENDOR = "vendor"
    OPEN_SOURCE = "open-source model"
    HYBRID = "hybrid approach"


class Criticality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HumanOversight(str, Enum):
    HUMAN_IN_THE_LOOP = "Human-in-the-loop"
    HUMAN_ON_THE_LOOP = "Human-on-the-loop"
    FULLY_AUTOMATED = "Fully automated"


class Goal(str, Enum):
    COMPLIANCE_READINESS = "Compliance readiness"
    TRUST_TRANSPARENCY = "Trust & transparency"
    OPERATIONAL_GOVERNANCE = "Operational governance"
    CERTIFICATION_PREP = "Certification preparation"


class PreferenceType(str, Enum):
    LIGHTWEIGHT = "Lightweight checklist"
    DETAILED = "Detailed framework"
    BOTH = "Both"


class QuestionnaireResponse(BaseModel):
    """
    Comprehensive questionnaire response matching PRD requirements.
    This captures all information needed for the 4 LLM calls.
    """
    # Organization & Context
    organization_type: OrganizationType = Field(..., description="Type of organization")
    industry: Industry = Field(..., description="Primary industry or domain")
    regions: List[str] = Field(..., description="Countries or regions where AI system will be used")
    organization_size: OrganizationSize = Field(..., description="Organization size by headcount")

    # AI System Characteristics
    main_purpose: str = Field(..., description="Main purpose of the AI system")
    data_types: List[str] = Field(..., description="Types of data used (personal, biometric, medical, etc.)")
    stage: AIStage = Field(..., description="Current stage of AI system development")
    developer: Developer = Field(..., description="Who developed the AI system")
    criticality: Criticality = Field(..., description="How critical the system is to business or safety")

    # Governance Maturity
    policies: str = Field(..., description="Current policies for AI, data governance, or model documentation")
    designated_team: str = Field(..., description="Whether there's a designated team/role for AI risk/ethics/compliance")
    approval_process: str = Field(..., description="Formal process for reviewing or approving AI models before release")
    record_keeping: str = Field(..., description="Records maintained for training data, model versions, and system updates")

    # Risk, Impact & Oversight
    affects_rights: str = Field(..., description="Whether AI could affect human rights, safety, or access to services")
    human_oversight: HumanOversight = Field(..., description="Level of human oversight present")
    testing: str = Field(..., description="Testing or bias/fairness evaluation performed")
    complaint_mechanism: str = Field(..., description="Mechanism for handling user complaints or incidents")

    # Outcome Preferences
    goal: Goal = Field(..., description="Main goal with AI governance")
    preference: PreferenceType = Field(..., description="Preferred type of framework output")
    standards: List[str] = Field(..., description="Specific standards to align with")


def get_questions() -> List[Dict[str, Any]]:
    """Return the comprehensive list of questions for the UI matching PRD requirements"""
    return [
        # ===== ORGANIZATION & CONTEXT =====
        {
            "key": "organization_type",
            "section": "Organization & Context",
            "label": "What type of organization are you?",
            "type": "select",
            "options": [
                {"value": "Startup", "label": "Startup"},
                {"value": "Enterprise", "label": "Enterprise"},
                {"value": "Academic", "label": "Academic"},
                {"value": "Government", "label": "Government"},
                {"value": "Nonprofit", "label": "Nonprofit"},
                {"value": "Regulated Entity", "label": "Regulated Entity"},
                {"value": "Other", "label": "Other"}
            ],
            "required": True
        },
        {
            "key": "industry",
            "section": "Organization & Context",
            "label": "Which industry or domain do you primarily operate in?",
            "type": "select",
            "options": [
                {"value": "Healthcare", "label": "Healthcare"},
                {"value": "Finance", "label": "Finance"},
                {"value": "Energy", "label": "Energy"},
                {"value": "Defense", "label": "Defense"},
                {"value": "Consumer Tech", "label": "Consumer Tech"},
                {"value": "Retail", "label": "Retail"},
                {"value": "Education", "label": "Education"},
                {"value": "Transportation", "label": "Transportation"},
                {"value": "Manufacturing", "label": "Manufacturing"},
                {"value": "Other", "label": "Other"}
            ],
            "required": True
        },
        {
            "key": "regions",
            "section": "Organization & Context",
            "label": "In which countries or regions will your AI system be developed, deployed, or used?",
            "type": "multi-select",
            "options": [
                {"value": "EU", "label": "European Union"},
                {"value": "US", "label": "United States"},
                {"value": "UK", "label": "United Kingdom"},
                {"value": "Canada", "label": "Canada"},
                {"value": "Asia", "label": "Asia Pacific"},
                {"value": "Latin America", "label": "Latin America"},
                {"value": "Middle East", "label": "Middle East"},
                {"value": "Africa", "label": "Africa"},
                {"value": "Other", "label": "Other"}
            ],
            "required": True
        },
        {
            "key": "organization_size",
            "section": "Organization & Context",
            "label": "Roughly how large is your organization?",
            "type": "select",
            "options": [
                {"value": "1-50", "label": "1-50 employees"},
                {"value": "50-200", "label": "50-200 employees"},
                {"value": "200-1000", "label": "200-1000 employees"},
                {"value": "1000+", "label": "1000+ employees"}
            ],
            "required": True
        },

        # ===== AI SYSTEM CHARACTERISTICS =====
        {
            "key": "main_purpose",
            "section": "AI System Characteristics",
            "label": "What is the main purpose of the AI system?",
            "type": "text",
            "placeholder": "e.g., automating decisions, generating content, detecting anomalies, predicting outcomes",
            "required": True
        },
        {
            "key": "data_types",
            "section": "AI System Characteristics",
            "label": "What kind of data does it use?",
            "type": "multi-select",
            "options": [
                {"value": "personal", "label": "Personal data"},
                {"value": "biometric", "label": "Biometric data"},
                {"value": "medical", "label": "Medical/health data"},
                {"value": "financial", "label": "Financial data"},
                {"value": "behavioral", "label": "Behavioral data"},
                {"value": "synthetic", "label": "Synthetic data"},
                {"value": "public", "label": "Public data"},
                {"value": "other", "label": "Other"}
            ],
            "required": True
        },
        {
            "key": "stage",
            "section": "AI System Characteristics",
            "label": "At what stage is the AI system?",
            "type": "select",
            "options": [
                {"value": "design", "label": "Design"},
                {"value": "development", "label": "Development"},
                {"value": "testing", "label": "Testing"},
                {"value": "deployment", "label": "Deployment"},
                {"value": "post-market monitoring", "label": "Post-market monitoring"}
            ],
            "required": True
        },
        {
            "key": "developer",
            "section": "AI System Characteristics",
            "label": "Who developed the AI system?",
            "type": "select",
            "options": [
                {"value": "in-house", "label": "In-house team"},
                {"value": "vendor", "label": "External vendor"},
                {"value": "open-source model", "label": "Open-source model"},
                {"value": "hybrid approach", "label": "Hybrid approach"}
            ],
            "required": True
        },
        {
            "key": "criticality",
            "section": "AI System Characteristics",
            "label": "How critical is this system to business or safety?",
            "type": "select",
            "options": [
                {"value": "low", "label": "Low - minimal impact"},
                {"value": "medium", "label": "Medium - moderate impact"},
                {"value": "high", "label": "High - critical impact on safety/business"}
            ],
            "required": True
        },

        # ===== GOVERNANCE MATURITY =====
        {
            "key": "policies",
            "section": "Governance Maturity",
            "label": "Do you currently have any policies for AI, data governance, or model documentation?",
            "type": "text",
            "placeholder": "Describe your current policies or state 'None'",
            "required": True
        },
        {
            "key": "designated_team",
            "section": "Governance Maturity",
            "label": "Is there a designated team or role responsible for AI risk, ethics, or compliance?",
            "type": "text",
            "placeholder": "Yes/No and details if applicable",
            "required": True
        },
        {
            "key": "approval_process",
            "section": "Governance Maturity",
            "label": "Do you have a formal process for reviewing or approving AI models before release?",
            "type": "text",
            "placeholder": "Describe your approval process or state 'None'",
            "required": True
        },
        {
            "key": "record_keeping",
            "section": "Governance Maturity",
            "label": "Do you maintain records of training data, model versions, and system updates?",
            "type": "text",
            "placeholder": "Describe your record-keeping practices",
            "required": True
        },

        # ===== RISK, IMPACT & OVERSIGHT =====
        {
            "key": "affects_rights",
            "section": "Risk, Impact & Oversight",
            "label": "Could your AI system directly affect human rights, safety, or access to services?",
            "type": "text",
            "placeholder": "e.g., hiring, credit, healthcare, justice",
            "required": True
        },
        {
            "key": "human_oversight",
            "section": "Risk, Impact & Oversight",
            "label": "What level of human oversight is present?",
            "type": "select",
            "options": [
                {"value": "Human-in-the-loop", "label": "Human-in-the-loop (human makes final decision)"},
                {"value": "Human-on-the-loop", "label": "Human-on-the-loop (human monitors)"},
                {"value": "Fully automated", "label": "Fully automated"}
            ],
            "required": True
        },
        {
            "key": "testing",
            "section": "Risk, Impact & Oversight",
            "label": "Have you performed any testing or bias/fairness evaluation yet?",
            "type": "text",
            "placeholder": "Describe testing performed or state 'None'",
            "required": True
        },
        {
            "key": "complaint_mechanism",
            "section": "Risk, Impact & Oversight",
            "label": "Do you have a mechanism for handling user complaints or incidents involving AI outcomes?",
            "type": "text",
            "placeholder": "Yes/No and details if applicable",
            "required": True
        },

        # ===== OUTCOME PREFERENCES =====
        {
            "key": "goal",
            "section": "Outcome Preferences",
            "label": "What is your main goal with AI governance right now?",
            "type": "select",
            "options": [
                {"value": "Compliance readiness", "label": "Compliance readiness"},
                {"value": "Trust & transparency", "label": "Trust & transparency"},
                {"value": "Operational governance", "label": "Operational governance"},
                {"value": "Certification preparation", "label": "Certification preparation"}
            ],
            "required": True
        },
        {
            "key": "preference",
            "section": "Outcome Preferences",
            "label": "Would you prefer a lightweight checklist, a detailed governance framework, or both?",
            "type": "select",
            "options": [
                {"value": "Lightweight checklist", "label": "Lightweight checklist"},
                {"value": "Detailed framework", "label": "Detailed framework"},
                {"value": "Both", "label": "Both"}
            ],
            "required": True
        },
        {
            "key": "standards",
            "section": "Outcome Preferences",
            "label": "Do you want your framework aligned to specific standards?",
            "type": "multi-select",
            "options": [
                {"value": "NIST AI RMF", "label": "NIST AI RMF"},
                {"value": "EU AI Act", "label": "EU AI Act"},
                {"value": "ISO/IEC 42001", "label": "ISO/IEC 42001"},
                {"value": "OECD Principles", "label": "OECD Principles"},
                {"value": "IEEE 7000", "label": "IEEE 7000"},
                {"value": "Privacy regulations", "label": "Privacy regulations (GDPR, etc.)"},
                {"value": "Cybersecurity regulations", "label": "Cybersecurity regulations"}
            ],
            "required": True
        }
    ]


def filter_questionnaire_for_call(responses: QuestionnaireResponse, call_type: str) -> Dict[str, Any]:
    """
    Filter questionnaire responses based on what's needed for each LLM call.
    This implements the input filtering strategy from the PRD.
    """

    if call_type == 'classification':
        # Call #1 needs everything for classification
        return responses.model_dump()

    elif call_type == 'eu_requirements':
        # Call #2: Only system characteristics
        return {
            'main_purpose': responses.main_purpose,
            'data_types': responses.data_types,
            'stage': responses.stage,
            'developer': responses.developer,
            'criticality': responses.criticality,
            'affects_rights': responses.affects_rights,
            'regions': responses.regions,
            'industry': responses.industry
        }

    elif call_type == 'nist_requirements':
        # Call #3: Only system characteristics
        return {
            'main_purpose': responses.main_purpose,
            'stage': responses.stage,
            'criticality': responses.criticality,
            'developer': responses.developer,
            'affects_rights': responses.affects_rights,
            'data_types': responses.data_types,
            'industry': responses.industry
        }

    elif call_type == 'gap_analysis':
        # Call #4: Only governance maturity
        return {
            'policies': responses.policies,
            'designated_team': responses.designated_team,
            'approval_process': responses.approval_process,
            'record_keeping': responses.record_keeping,
            'human_oversight': responses.human_oversight,
            'testing': responses.testing,
            'complaint_mechanism': responses.complaint_mechanism,
            'goal': responses.goal
        }

    else:
        # Default: return everything
        return responses.model_dump()
