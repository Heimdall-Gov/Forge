"""
Tests for API endpoints in app.py
"""

import pytest
from unittest.mock import Mock, patch
import json


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_200(self, client):
        """Test that root endpoint returns 200"""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_api_info(self, client):
        """Test that root endpoint returns API information"""
        response = client.get("/")
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert isinstance(data["endpoints"], dict)

    def test_root_lists_endpoints(self, client):
        """Test that root lists all available endpoints"""
        response = client.get("/")
        data = response.json()

        endpoints = data["endpoints"]
        assert "/api/questions" in endpoints
        assert "/api/assessment" in endpoints
        assert "/health" in endpoints


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_returns_200(self, client):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        """Test that health endpoint returns status"""
        response = client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data


class TestQuestionsEndpoint:
    """Test /api/questions endpoint"""

    def test_get_questions_returns_200(self, client):
        """Test that questions endpoint returns 200"""
        response = client.get("/api/questions")
        assert response.status_code == 200

    def test_get_questions_structure(self, client):
        """Test that questions endpoint returns correct structure"""
        response = client.get("/api/questions")
        data = response.json()

        assert "questions" in data
        assert "total" in data
        assert "sections" in data
        assert isinstance(data["questions"], list)
        assert isinstance(data["sections"], list)

    def test_get_questions_count(self, client):
        """Test that questions endpoint returns 20 questions"""
        response = client.get("/api/questions")
        data = response.json()

        assert data["total"] == 20
        assert len(data["questions"]) == 20

    def test_get_questions_has_sections(self, client):
        """Test that questions are organized into sections"""
        response = client.get("/api/questions")
        data = response.json()

        sections = data["sections"]
        assert len(sections) == 5
        assert "Organization & Context" in sections


class TestCreateAssessmentEndpoint:
    """Test POST /api/assessment endpoint"""

    @patch('app.assessment_engine')
    def test_create_assessment_returns_202(self, mock_engine, client, sample_questionnaire_response):
        """Test that creating assessment returns 202 Accepted"""
        request_data = {
            "questionnaire_responses": sample_questionnaire_response.model_dump()
        }

        response = client.post("/api/assessment", json=request_data)

        assert response.status_code == 202

    @patch('app.assessment_engine')
    def test_create_assessment_response_structure(self, mock_engine, client, sample_questionnaire_response):
        """Test that create assessment returns correct response structure"""
        request_data = {
            "questionnaire_responses": sample_questionnaire_response.model_dump()
        }

        response = client.post("/api/assessment", json=request_data)
        data = response.json()

        assert "status" in data
        assert "assessment_id" in data
        assert "status_url" in data
        assert "estimated_time_seconds" in data
        assert data["status"] == "accepted"

    @patch('app.assessment_engine')
    def test_create_assessment_stores_in_database(self, mock_engine, client, test_db, sample_questionnaire_response):
        """Test that assessment is stored in database"""
        request_data = {
            "questionnaire_responses": sample_questionnaire_response.model_dump()
        }

        response = client.post("/api/assessment", json=request_data)
        data = response.json()

        assessment_id = data["assessment_id"]

        # Check that assessment exists in database
        from database import get_assessment
        assessment = get_assessment(test_db, assessment_id)

        assert assessment is not None
        assert assessment.status == "pending"

    def test_create_assessment_invalid_data(self, client):
        """Test that invalid data returns 422"""
        invalid_data = {
            "questionnaire_responses": {
                "invalid_field": "invalid_value"
            }
        }

        response = client.post("/api/assessment", json=invalid_data)

        assert response.status_code == 422

    def test_create_assessment_missing_fields(self, client):
        """Test that missing required fields returns 422"""
        incomplete_data = {
            "questionnaire_responses": {
                "organization_type": "Startup"
                # Missing all other required fields
            }
        }

        response = client.post("/api/assessment", json=incomplete_data)

        assert response.status_code == 422


class TestGetAssessmentStatusEndpoint:
    """Test GET /api/assessment/{id}/status endpoint"""

    def test_get_status_pending_assessment(self, client, test_db):
        """Test getting status of pending assessment"""
        from database import create_assessment

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"},
            organization_name="Test Org"
        )

        response = client.get(f"/api/assessment/{assessment.id}/status")

        assert response.status_code == 200
        data = response.json()

        assert data["assessment_id"] == assessment.id
        assert data["status"] == "pending"

    def test_get_status_processing_assessment(self, client, test_db):
        """Test getting status of processing assessment"""
        from database import create_assessment, update_assessment_status

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        update_assessment_status(test_db, assessment.id, "processing")

        response = client.get(f"/api/assessment/{assessment.id}/status")
        data = response.json()

        assert data["status"] == "processing"

    def test_get_status_completed_assessment(self, client, test_db):
        """Test getting status of completed assessment"""
        from database import create_assessment, save_assessment_results

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        save_assessment_results(
            test_db,
            assessment.id,
            eu_classification="HIGH_RISK",
            eu_requirements={},
            nist_requirements={},
            gaps={},
            compliance_score=75,
            cross_framework_mapping={},
            full_result={},
            processing_time_seconds=60
        )

        response = client.get(f"/api/assessment/{assessment.id}/status")
        data = response.json()

        assert data["status"] == "completed"
        assert data["compliance_score"] == 75
        assert data["processing_time_seconds"] == 60

    def test_get_status_nonexistent_assessment(self, client):
        """Test getting status of non-existent assessment"""
        response = client.get("/api/assessment/nonexistent-id/status")

        assert response.status_code == 404


class TestGetAssessmentResultEndpoint:
    """Test GET /api/assessment/{id} endpoint"""

    def test_get_result_completed_assessment(self, client, test_db, sample_full_assessment_result):
        """Test getting result of completed assessment"""
        from database import create_assessment, save_assessment_results

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"},
            organization_name="Test Org"
        )

        save_assessment_results(
            test_db,
            assessment.id,
            eu_classification="HIGH_RISK",
            eu_requirements=sample_full_assessment_result["eu_ai_act"],
            nist_requirements=sample_full_assessment_result["nist_ai_rmf"],
            gaps=sample_full_assessment_result["gap_analysis"],
            compliance_score=35,
            cross_framework_mapping=sample_full_assessment_result["cross_framework_mapping"],
            full_result=sample_full_assessment_result,
            processing_time_seconds=78
        )

        response = client.get(f"/api/assessment/{assessment.id}")

        assert response.status_code == 200
        data = response.json()

        assert "eu_ai_act" in data
        assert "nist_ai_rmf" in data
        assert "gap_analysis" in data
        assert "cross_framework_mapping" in data
        assert data["organization_name"] == "Test Org"

    def test_get_result_pending_assessment_returns_400(self, client, test_db):
        """Test that getting result of pending assessment returns 400"""
        from database import create_assessment

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        response = client.get(f"/api/assessment/{assessment.id}")

        assert response.status_code == 400
        assert "not completed" in response.json()["detail"]

    def test_get_result_processing_assessment_returns_400(self, client, test_db):
        """Test that getting result of processing assessment returns 400"""
        from database import create_assessment, update_assessment_status

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        update_assessment_status(test_db, assessment.id, "processing")

        response = client.get(f"/api/assessment/{assessment.id}")

        assert response.status_code == 400

    def test_get_result_nonexistent_assessment(self, client):
        """Test getting result of non-existent assessment"""
        response = client.get("/api/assessment/nonexistent-id")

        assert response.status_code == 404


class TestExportPDFEndpoint:
    """Test GET /api/assessment/{id}/pdf endpoint"""

    def test_export_pdf_completed_assessment(self, client, test_db, sample_full_assessment_result):
        """Test exporting PDF of completed assessment"""
        from database import create_assessment, save_assessment_results

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"},
            organization_name="Test Org"
        )

        save_assessment_results(
            test_db,
            assessment.id,
            eu_classification="HIGH_RISK",
            eu_requirements=sample_full_assessment_result["eu_ai_act"],
            nist_requirements=sample_full_assessment_result["nist_ai_rmf"],
            gaps=sample_full_assessment_result["gap_analysis"],
            compliance_score=35,
            cross_framework_mapping=sample_full_assessment_result["cross_framework_mapping"],
            full_result=sample_full_assessment_result,
            processing_time_seconds=78
        )

        response = client.get(f"/api/assessment/{assessment.id}/pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_export_pdf_pending_assessment_returns_400(self, client, test_db):
        """Test that exporting PDF of pending assessment returns 400"""
        from database import create_assessment

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        response = client.get(f"/api/assessment/{assessment.id}/pdf")

        assert response.status_code == 400

    def test_export_pdf_nonexistent_assessment(self, client):
        """Test exporting PDF of non-existent assessment"""
        response = client.get("/api/assessment/nonexistent-id/pdf")

        assert response.status_code == 404


class TestAPIIntegration:
    """Integration tests for API endpoints"""

    @patch('app.assessment_engine.run_complete_assessment')
    def test_complete_assessment_workflow(
        self,
        mock_assessment,
        client,
        test_db,
        sample_questionnaire_response,
        sample_full_assessment_result
    ):
        """Test complete workflow from creation to retrieval"""
        # Configure mock
        mock_assessment.return_value = sample_full_assessment_result

        # 1. Create assessment
        request_data = {
            "questionnaire_responses": sample_questionnaire_response.model_dump()
        }

        create_response = client.post("/api/assessment", json=request_data)
        assert create_response.status_code == 202

        assessment_id = create_response.json()["assessment_id"]

        # 2. Check initial status (should be pending or processing)
        status_response = client.get(f"/api/assessment/{assessment_id}/status")
        assert status_response.status_code == 200
        assert status_response.json()["status"] in ["pending", "processing"]

        # 3. Simulate assessment completion
        from database import save_assessment_results
        save_assessment_results(
            test_db,
            assessment_id,
            eu_classification="HIGH_RISK",
            eu_requirements=sample_full_assessment_result["eu_ai_act"],
            nist_requirements=sample_full_assessment_result["nist_ai_rmf"],
            gaps=sample_full_assessment_result["gap_analysis"],
            compliance_score=35,
            cross_framework_mapping=sample_full_assessment_result["cross_framework_mapping"],
            full_result=sample_full_assessment_result,
            processing_time_seconds=78
        )

        # 4. Check completed status
        status_response = client.get(f"/api/assessment/{assessment_id}/status")
        assert status_response.json()["status"] == "completed"
        assert status_response.json()["compliance_score"] == 35

        # 5. Get full results
        result_response = client.get(f"/api/assessment/{assessment_id}")
        assert result_response.status_code == 200
        result_data = result_response.json()
        assert result_data["gap_analysis"]["compliance_score"] == 35

        # 6. Export PDF
        pdf_response = client.get(f"/api/assessment/{assessment_id}/pdf")
        assert pdf_response.status_code == 200

    def test_error_handling_workflow(self, client, test_db):
        """Test error handling in workflow"""
        from database import create_assessment, update_assessment_status

        # Create assessment
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        # Simulate failure
        update_assessment_status(
            test_db,
            assessment.id,
            "failed",
            "LLM API timeout"
        )

        # Check status shows error
        status_response = client.get(f"/api/assessment/{assessment.id}/status")
        data = status_response.json()

        assert data["status"] == "failed"
        assert data["error_message"] == "LLM API timeout"

        # Trying to get results should fail
        result_response = client.get(f"/api/assessment/{assessment.id}")
        assert result_response.status_code == 400


class TestAPIValidation:
    """Test API input validation"""

    def test_questionnaire_validation_empty_lists(self, client):
        """Test that empty lists are rejected"""
        invalid_data = {
            "questionnaire_responses": {
                "organization_type": "Startup",
                "industry": "Healthcare",
                "regions": [],  # Empty list should be invalid
                "organization_size": "50-200",
                "main_purpose": "Test",
                "data_types": [],  # Empty list should be invalid
                "stage": "development",
                "developer": "in-house",
                "criticality": "high",
                "policies": "None",
                "designated_team": "No",
                "approval_process": "None",
                "record_keeping": "None",
                "affects_rights": "No",
                "human_oversight": "Human-in-the-loop",
                "testing": "None",
                "complaint_mechanism": "No",
                "goal": "Compliance readiness",
                "preference": "Detailed framework",
                "standards": []  # Empty list should be invalid
            }
        }

        response = client.post("/api/assessment", json=invalid_data)
        # Should fail validation or process with defaults
        assert response.status_code in [422, 202]

    def test_questionnaire_validation_invalid_enum(self, client):
        """Test that invalid enum values are rejected"""
        invalid_data = {
            "questionnaire_responses": {
                "organization_type": "InvalidType",  # Invalid enum value
                "industry": "Healthcare",
                "regions": ["EU"],
                "organization_size": "50-200",
                "main_purpose": "Test",
                "data_types": ["medical"],
                "stage": "development",
                "developer": "in-house",
                "criticality": "high",
                "policies": "None",
                "designated_team": "No",
                "approval_process": "None",
                "record_keeping": "None",
                "affects_rights": "No",
                "human_oversight": "Human-in-the-loop",
                "testing": "None",
                "complaint_mechanism": "No",
                "goal": "Compliance readiness",
                "preference": "Detailed framework",
                "standards": ["EU AI Act"]
            }
        }

        response = client.post("/api/assessment", json=invalid_data)
        assert response.status_code == 422
