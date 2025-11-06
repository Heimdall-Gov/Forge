"""
Tests for questionnaire.py
"""

import pytest
from pydantic import ValidationError
from questionnaire import (
    QuestionnaireResponse,
    get_questions,
    filter_questionnaire_for_call,
    OrganizationType,
    Industry,
    AIStage,
    Criticality
)


class TestQuestionnaireEnums:
    """Test enum definitions"""

    def test_organization_type_enum(self):
        """Test OrganizationType enum has all expected values"""
        assert OrganizationType.STARTUP == "Startup"
        assert OrganizationType.ENTERPRISE == "Enterprise"
        assert OrganizationType.ACADEMIC == "Academic"
        assert OrganizationType.GOVERNMENT == "Government"

    def test_industry_enum(self):
        """Test Industry enum has all expected values"""
        assert Industry.HEALTHCARE == "Healthcare"
        assert Industry.FINANCE == "Finance"
        assert Industry.ENERGY == "Energy"

    def test_ai_stage_enum(self):
        """Test AIStage enum has all expected values"""
        assert AIStage.DESIGN == "design"
        assert AIStage.DEVELOPMENT == "development"
        assert AIStage.TESTING == "testing"
        assert AIStage.DEPLOYMENT == "deployment"
        assert AIStage.POST_MARKET == "post-market monitoring"

    def test_criticality_enum(self):
        """Test Criticality enum has all expected values"""
        assert Criticality.LOW == "low"
        assert Criticality.MEDIUM == "medium"
        assert Criticality.HIGH == "high"


class TestQuestionnaireResponse:
    """Test QuestionnaireResponse model"""

    def test_valid_questionnaire_response(self, sample_questionnaire_response):
        """Test creating a valid questionnaire response"""
        assert sample_questionnaire_response.organization_type == "Startup"
        assert sample_questionnaire_response.industry == "Healthcare"
        assert "EU" in sample_questionnaire_response.regions
        assert sample_questionnaire_response.criticality == "high"

    def test_questionnaire_response_validation(self):
        """Test that validation works for required fields"""
        with pytest.raises(ValidationError):
            QuestionnaireResponse(
                # Missing required fields
                organization_type="Startup"
            )

    def test_questionnaire_with_all_fields(self):
        """Test questionnaire with all fields populated"""
        response = QuestionnaireResponse(
            organization_type="Enterprise",
            industry="Finance",
            regions=["US", "Canada"],
            organization_size="1000+",
            main_purpose="Fraud detection system",
            data_types=["financial", "behavioral"],
            stage="deployment",
            developer="vendor",
            criticality="high",
            policies="Comprehensive AI governance framework",
            designated_team="Yes - AI Ethics Board",
            approval_process="Multi-stage review process",
            record_keeping="Full audit trail maintained",
            affects_rights="Yes - credit decisions",
            human_oversight="Human-on-the-loop",
            testing="Comprehensive bias and fairness testing",
            complaint_mechanism="Yes - formal complaint process",
            goal="Certification preparation",
            preference="Both",
            standards=["EU AI Act", "NIST AI RMF", "ISO/IEC 42001"]
        )

        assert response.organization_type == "Enterprise"
        assert response.criticality == "high"
        assert len(response.standards) == 3

    def test_questionnaire_model_dump(self, sample_questionnaire_response):
        """Test converting questionnaire to dictionary"""
        data = sample_questionnaire_response.model_dump()

        assert isinstance(data, dict)
        assert data["organization_type"] == "Startup"
        assert data["industry"] == "Healthcare"
        assert isinstance(data["regions"], list)


class TestGetQuestions:
    """Test get_questions function"""

    def test_get_questions_returns_list(self):
        """Test that get_questions returns a list"""
        questions = get_questions()
        assert isinstance(questions, list)
        assert len(questions) > 0

    def test_get_questions_count(self):
        """Test that we have 20 questions as per PRD"""
        questions = get_questions()
        assert len(questions) == 20

    def test_question_structure(self):
        """Test that each question has required fields"""
        questions = get_questions()

        for question in questions:
            assert "key" in question
            assert "label" in question
            assert "type" in question
            assert "required" in question
            assert "section" in question

    def test_question_sections(self):
        """Test that questions are organized into correct sections"""
        questions = get_questions()
        sections = set(q["section"] for q in questions)

        expected_sections = {
            "Organization & Context",
            "AI System Characteristics",
            "Governance Maturity",
            "Risk, Impact & Oversight",
            "Outcome Preferences"
        }

        assert sections == expected_sections

    def test_question_types(self):
        """Test that questions have valid types"""
        questions = get_questions()
        valid_types = {"select", "multi-select", "text", "boolean"}

        for question in questions:
            assert question["type"] in valid_types

    def test_select_questions_have_options(self):
        """Test that select questions have options"""
        questions = get_questions()

        for question in questions:
            if question["type"] in ["select", "multi-select"]:
                assert "options" in question
                assert len(question["options"]) > 0

    def test_required_fields_marked(self):
        """Test that all questions in PRD are marked as required"""
        questions = get_questions()

        # All questions should be required except additional context
        optional_keys = []  # Currently all are required

        for question in questions:
            if question["key"] not in optional_keys:
                assert question["required"] is True


class TestFilterQuestionnaireForCall:
    """Test filter_questionnaire_for_call function"""

    def test_filter_classification_returns_all(self, sample_questionnaire_response):
        """Test that classification filter returns all fields"""
        filtered = filter_questionnaire_for_call(sample_questionnaire_response, 'classification')

        # Should return all fields
        assert "organization_type" in filtered
        assert "main_purpose" in filtered
        assert "policies" in filtered
        assert "affects_rights" in filtered
        assert "goal" in filtered

    def test_filter_eu_requirements_system_only(self, sample_questionnaire_response):
        """Test that EU requirements filter returns only system characteristics"""
        filtered = filter_questionnaire_for_call(sample_questionnaire_response, 'eu_requirements')

        # Should include system characteristics
        assert "main_purpose" in filtered
        assert "data_types" in filtered
        assert "stage" in filtered
        assert "criticality" in filtered
        assert "regions" in filtered

        # Should NOT include governance maturity
        assert "policies" not in filtered
        assert "designated_team" not in filtered
        assert "approval_process" not in filtered

    def test_filter_nist_requirements_system_only(self, sample_questionnaire_response):
        """Test that NIST requirements filter returns only system characteristics"""
        filtered = filter_questionnaire_for_call(sample_questionnaire_response, 'nist_requirements')

        # Should include system characteristics
        assert "main_purpose" in filtered
        assert "stage" in filtered
        assert "criticality" in filtered
        assert "data_types" in filtered

        # Should NOT include governance maturity
        assert "policies" not in filtered
        assert "designated_team" not in filtered

    def test_filter_gap_analysis_governance_only(self, sample_questionnaire_response):
        """Test that gap analysis filter returns only governance fields"""
        filtered = filter_questionnaire_for_call(sample_questionnaire_response, 'gap_analysis')

        # Should include governance maturity
        assert "policies" in filtered
        assert "designated_team" in filtered
        assert "approval_process" in filtered
        assert "record_keeping" in filtered
        assert "human_oversight" in filtered
        assert "testing" in filtered
        assert "complaint_mechanism" in filtered

        # Should NOT include system characteristics
        assert "main_purpose" not in filtered
        assert "data_types" not in filtered
        assert "stage" not in filtered

    def test_filter_invalid_call_type_returns_all(self, sample_questionnaire_response):
        """Test that invalid call type returns all fields"""
        filtered = filter_questionnaire_for_call(sample_questionnaire_response, 'invalid_type')

        # Should return all fields as fallback
        assert "organization_type" in filtered
        assert "main_purpose" in filtered
        assert "policies" in filtered

    def test_filter_preserves_data_types(self, sample_questionnaire_response):
        """Test that filtering preserves correct data types"""
        filtered = filter_questionnaire_for_call(sample_questionnaire_response, 'classification')

        # Check data types are preserved
        assert isinstance(filtered["regions"], list)
        assert isinstance(filtered["data_types"], list)
        assert isinstance(filtered["main_purpose"], str)


class TestQuestionnaireIntegration:
    """Integration tests for questionnaire functionality"""

    def test_end_to_end_questionnaire_flow(self):
        """Test complete flow from questions to response to filtering"""
        # Get questions
        questions = get_questions()
        assert len(questions) == 20

        # Create response based on questions
        response_data = {
            "organization_type": "Startup",
            "industry": "Healthcare",
            "regions": ["EU"],
            "organization_size": "50-200",
            "main_purpose": "Medical diagnosis",
            "data_types": ["medical"],
            "stage": "development",
            "developer": "in-house",
            "criticality": "high",
            "policies": "None",
            "designated_team": "No",
            "approval_process": "None",
            "record_keeping": "Basic",
            "affects_rights": "Yes",
            "human_oversight": "Human-in-the-loop",
            "testing": "Basic",
            "complaint_mechanism": "No",
            "goal": "Compliance readiness",
            "preference": "Detailed framework",
            "standards": ["EU AI Act"]
        }

        # Validate response
        response = QuestionnaireResponse(**response_data)
        assert response.organization_type == "Startup"

        # Filter for each call type
        classification_data = filter_questionnaire_for_call(response, 'classification')
        eu_data = filter_questionnaire_for_call(response, 'eu_requirements')
        nist_data = filter_questionnaire_for_call(response, 'nist_requirements')
        gap_data = filter_questionnaire_for_call(response, 'gap_analysis')

        # Verify filtering worked
        assert len(classification_data) == 20  # All fields
        assert len(eu_data) == 8  # System characteristics only
        assert len(nist_data) == 7  # System characteristics only
        assert len(gap_data) == 8  # Governance only

    def test_multiple_regions_handling(self):
        """Test handling of multiple regions"""
        response = QuestionnaireResponse(
            organization_type="Enterprise",
            industry="Finance",
            regions=["EU", "US", "UK", "Canada"],
            organization_size="1000+",
            main_purpose="Fraud detection",
            data_types=["financial"],
            stage="deployment",
            developer="in-house",
            criticality="high",
            policies="Comprehensive",
            designated_team="Yes",
            approval_process="Formal",
            record_keeping="Complete",
            affects_rights="Yes",
            human_oversight="Human-in-the-loop",
            testing="Comprehensive",
            complaint_mechanism="Yes",
            goal="Compliance readiness",
            preference="Both",
            standards=["EU AI Act", "NIST AI RMF"]
        )

        assert len(response.regions) == 4
        assert "EU" in response.regions

    def test_multiple_data_types_handling(self):
        """Test handling of multiple data types"""
        response = QuestionnaireResponse(
            organization_type="Healthcare",
            industry="Healthcare",
            regions=["EU"],
            organization_size="200-1000",
            main_purpose="Patient care",
            data_types=["medical", "personal", "biometric", "behavioral"],
            stage="deployment",
            developer="hybrid approach",
            criticality="high",
            policies="Comprehensive",
            designated_team="Yes",
            approval_process="Formal",
            record_keeping="Complete",
            affects_rights="Yes",
            human_oversight="Human-in-the-loop",
            testing="Comprehensive",
            complaint_mechanism="Yes",
            goal="Compliance readiness",
            preference="Detailed framework",
            standards=["EU AI Act"]
        )

        assert len(response.data_types) == 4
        assert "biometric" in response.data_types
