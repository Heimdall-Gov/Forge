"""
Tests for database.py
"""

import pytest
from datetime import datetime
from database import (
    Assessment,
    create_assessment,
    get_assessment,
    update_assessment,
    update_assessment_status,
    save_assessment_results,
    list_assessments
)


class TestAssessmentModel:
    """Test Assessment database model"""

    def test_create_assessment_record(self, test_db):
        """Test creating an assessment record"""
        questionnaire_data = {
            "organization_type": "Startup",
            "industry": "Healthcare"
        }

        assessment = create_assessment(
            test_db,
            questionnaire_responses=questionnaire_data,
            organization_name="Test Org"
        )

        assert assessment.id is not None
        assert assessment.organization_name == "Test Org"
        assert assessment.status == "pending"
        assert assessment.questionnaire_responses == questionnaire_data
        assert assessment.created_at is not None

    def test_assessment_to_dict(self, test_db):
        """Test converting assessment to dictionary"""
        questionnaire_data = {"test": "data"}
        assessment = create_assessment(
            test_db,
            questionnaire_responses=questionnaire_data,
            organization_name="Test Org"
        )

        result = assessment.to_dict()

        assert isinstance(result, dict)
        assert result["assessment_id"] == assessment.id
        assert result["organization_name"] == "Test Org"
        assert result["status"] == "pending"

    def test_assessment_default_values(self, test_db):
        """Test that assessment has correct default values"""
        questionnaire_data = {"test": "data"}
        assessment = create_assessment(
            test_db,
            questionnaire_responses=questionnaire_data
        )

        assert assessment.status == "pending"
        assert assessment.eu_classification is None
        assert assessment.compliance_score is None
        assert assessment.processing_time_seconds is None
        assert assessment.error_message is None


class TestGetAssessment:
    """Test get_assessment function"""

    def test_get_existing_assessment(self, test_db):
        """Test retrieving an existing assessment"""
        questionnaire_data = {"test": "data"}
        created = create_assessment(
            test_db,
            questionnaire_responses=questionnaire_data,
            organization_name="Test Org"
        )

        retrieved = get_assessment(test_db, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.organization_name == "Test Org"

    def test_get_nonexistent_assessment(self, test_db):
        """Test retrieving a non-existent assessment"""
        result = get_assessment(test_db, "nonexistent-id")
        assert result is None

    def test_get_assessment_preserves_data(self, test_db):
        """Test that retrieved assessment has all original data"""
        questionnaire_data = {
            "organization_type": "Enterprise",
            "industry": "Finance",
            "criticality": "high"
        }

        created = create_assessment(
            test_db,
            questionnaire_responses=questionnaire_data,
            organization_name="Financial Corp"
        )

        retrieved = get_assessment(test_db, created.id)

        assert retrieved.questionnaire_responses == questionnaire_data
        assert retrieved.questionnaire_responses["criticality"] == "high"


class TestUpdateAssessment:
    """Test update_assessment function"""

    def test_update_assessment_status(self, test_db):
        """Test updating assessment status"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        updated = update_assessment(test_db, assessment.id, status="processing")

        assert updated.status == "processing"

    def test_update_multiple_fields(self, test_db):
        """Test updating multiple fields at once"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        updated = update_assessment(
            test_db,
            assessment.id,
            status="completed",
            eu_classification="HIGH_RISK",
            compliance_score=75,
            processing_time_seconds=90
        )

        assert updated.status == "completed"
        assert updated.eu_classification == "HIGH_RISK"
        assert updated.compliance_score == 75
        assert updated.processing_time_seconds == 90

    def test_update_nonexistent_assessment(self, test_db):
        """Test updating a non-existent assessment"""
        result = update_assessment(test_db, "nonexistent-id", status="completed")
        assert result is None

    def test_update_preserves_other_fields(self, test_db):
        """Test that update preserves fields not being updated"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"},
            organization_name="Test Org"
        )

        updated = update_assessment(test_db, assessment.id, status="processing")

        assert updated.organization_name == "Test Org"
        assert updated.questionnaire_responses == {"test": "data"}


class TestUpdateAssessmentStatus:
    """Test update_assessment_status function"""

    def test_update_status_to_processing(self, test_db):
        """Test updating status to processing"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        updated = update_assessment_status(test_db, assessment.id, "processing")

        assert updated.status == "processing"
        assert updated.error_message is None

    def test_update_status_to_failed_with_error(self, test_db):
        """Test updating status to failed with error message"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        error_msg = "LLM API timeout"
        updated = update_assessment_status(
            test_db,
            assessment.id,
            "failed",
            error_msg
        )

        assert updated.status == "failed"
        assert updated.error_message == error_msg

    def test_update_status_to_completed(self, test_db):
        """Test updating status to completed"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        updated = update_assessment_status(test_db, assessment.id, "completed")

        assert updated.status == "completed"


class TestSaveAssessmentResults:
    """Test save_assessment_results function"""

    def test_save_complete_results(self, test_db, sample_full_assessment_result):
        """Test saving complete assessment results"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        eu_requirements = {
            "applicable_articles": [9, 10, 14],
            "requirements": []
        }

        nist_requirements = {
            "applicable_subcategories": ["GOVERN.1.1"],
            "priority_functions": ["GOVERN"]
        }

        gaps = {
            "gaps": [],
            "compliance_score": 85,
            "score_breakdown": {}
        }

        mapping = {"eu_to_nist": {}, "nist_to_eu": {}}

        updated = save_assessment_results(
            test_db,
            assessment.id,
            eu_classification="HIGH_RISK",
            eu_requirements=eu_requirements,
            nist_requirements=nist_requirements,
            gaps=gaps,
            compliance_score=85,
            cross_framework_mapping=mapping,
            full_result=sample_full_assessment_result,
            processing_time_seconds=78
        )

        assert updated.status == "completed"
        assert updated.eu_classification == "HIGH_RISK"
        assert updated.compliance_score == 85
        assert updated.processing_time_seconds == 78
        assert updated.eu_requirements == eu_requirements
        assert updated.nist_requirements == nist_requirements
        assert updated.gaps == gaps
        assert updated.full_result == sample_full_assessment_result

    def test_save_results_updates_all_fields(self, test_db):
        """Test that save_assessment_results updates all relevant fields"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        eu_req = {"applicable_articles": [14]}
        nist_req = {"applicable_subcategories": ["GOVERN.1.1"]}
        gaps_data = {"gaps": [], "compliance_score": 50}
        mapping = {}
        full_result = {"test": "result"}

        updated = save_assessment_results(
            test_db,
            assessment.id,
            eu_classification="MINIMAL_RISK",
            eu_requirements=eu_req,
            nist_requirements=nist_req,
            gaps=gaps_data,
            compliance_score=50,
            cross_framework_mapping=mapping,
            full_result=full_result,
            processing_time_seconds=60
        )

        # Verify all fields are set
        assert updated.eu_classification is not None
        assert updated.eu_requirements is not None
        assert updated.nist_requirements is not None
        assert updated.gaps is not None
        assert updated.compliance_score is not None
        assert updated.cross_framework_mapping is not None
        assert updated.full_result is not None
        assert updated.processing_time_seconds is not None


class TestListAssessments:
    """Test list_assessments function"""

    def test_list_empty_assessments(self, test_db):
        """Test listing when no assessments exist"""
        results = list_assessments(test_db)
        assert results == []

    def test_list_single_assessment(self, test_db):
        """Test listing a single assessment"""
        create_assessment(
            test_db,
            questionnaire_responses={"test": "data"},
            organization_name="Org 1"
        )

        results = list_assessments(test_db)

        assert len(results) == 1
        assert results[0].organization_name == "Org 1"

    def test_list_multiple_assessments(self, test_db):
        """Test listing multiple assessments"""
        for i in range(5):
            create_assessment(
                test_db,
                questionnaire_responses={"test": f"data{i}"},
                organization_name=f"Org {i}"
            )

        results = list_assessments(test_db)

        assert len(results) == 5

    def test_list_assessments_ordered_by_created_at(self, test_db):
        """Test that assessments are ordered by created_at descending"""
        # Create assessments in sequence
        first = create_assessment(
            test_db,
            questionnaire_responses={"test": "first"},
            organization_name="First"
        )

        second = create_assessment(
            test_db,
            questionnaire_responses={"test": "second"},
            organization_name="Second"
        )

        results = list_assessments(test_db)

        # Most recent should be first
        assert results[0].id == second.id
        assert results[1].id == first.id

    def test_list_assessments_with_limit(self, test_db):
        """Test listing assessments with limit"""
        for i in range(10):
            create_assessment(
                test_db,
                questionnaire_responses={"test": f"data{i}"}
            )

        results = list_assessments(test_db, limit=5)

        assert len(results) == 5

    def test_list_assessments_with_skip(self, test_db):
        """Test listing assessments with skip offset"""
        for i in range(10):
            create_assessment(
                test_db,
                questionnaire_responses={"test": f"data{i}"}
            )

        results = list_assessments(test_db, skip=5)

        assert len(results) == 5

    def test_list_assessments_pagination(self, test_db):
        """Test pagination with skip and limit"""
        for i in range(20):
            create_assessment(
                test_db,
                questionnaire_responses={"test": f"data{i}"}
            )

        # Get first page
        page1 = list_assessments(test_db, skip=0, limit=5)
        # Get second page
        page2 = list_assessments(test_db, skip=5, limit=5)

        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id

    def test_list_assessments_filter_by_organization(self, test_db):
        """Test filtering assessments by organization name"""
        create_assessment(
            test_db,
            questionnaire_responses={"test": "data1"},
            organization_name="Healthcare Corp"
        )

        create_assessment(
            test_db,
            questionnaire_responses={"test": "data2"},
            organization_name="Finance Corp"
        )

        create_assessment(
            test_db,
            questionnaire_responses={"test": "data3"},
            organization_name="Healthcare Corp"
        )

        results = list_assessments(test_db, organization_name="Healthcare Corp")

        assert len(results) == 2
        for assessment in results:
            assert assessment.organization_name == "Healthcare Corp"


class TestDatabaseIntegration:
    """Integration tests for database operations"""

    def test_complete_assessment_lifecycle(self, test_db):
        """Test complete lifecycle of an assessment"""
        # 1. Create assessment
        questionnaire_data = {
            "organization_type": "Startup",
            "industry": "Healthcare"
        }

        assessment = create_assessment(
            test_db,
            questionnaire_responses=questionnaire_data,
            organization_name="MedTech Startup"
        )

        assert assessment.status == "pending"

        # 2. Update to processing
        update_assessment_status(test_db, assessment.id, "processing")

        retrieved = get_assessment(test_db, assessment.id)
        assert retrieved.status == "processing"

        # 3. Save results
        eu_req = {"applicable_articles": [9, 14]}
        nist_req = {"applicable_subcategories": ["GOVERN.1.1", "MAP.3.5"]}
        gaps_data = {
            "gaps": [],
            "compliance_score": 75,
            "score_breakdown": {
                "critical_gaps": 2,
                "high_gaps": 3,
                "medium_gaps": 5,
                "low_gaps": 1,
                "implemented": 10
            }
        }
        mapping = {"eu_to_nist": {"Article_14": ["MAP.3.5"]}}
        full_result = {
            "eu_ai_act": {},
            "nist_ai_rmf": {},
            "gap_analysis": gaps_data
        }

        save_assessment_results(
            test_db,
            assessment.id,
            eu_classification="HIGH_RISK",
            eu_requirements=eu_req,
            nist_requirements=nist_req,
            gaps=gaps_data,
            compliance_score=75,
            cross_framework_mapping=mapping,
            full_result=full_result,
            processing_time_seconds=85
        )

        # 4. Verify final state
        final = get_assessment(test_db, assessment.id)

        assert final.status == "completed"
        assert final.eu_classification == "HIGH_RISK"
        assert final.compliance_score == 75
        assert final.processing_time_seconds == 85
        assert final.full_result == full_result

    def test_failed_assessment_scenario(self, test_db):
        """Test handling a failed assessment"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        # Update to processing
        update_assessment_status(test_db, assessment.id, "processing")

        # Simulate failure
        error_message = "LLM API returned error 500"
        update_assessment_status(test_db, assessment.id, "failed", error_message)

        failed = get_assessment(test_db, assessment.id)

        assert failed.status == "failed"
        assert failed.error_message == error_message
        assert failed.compliance_score is None
        assert failed.full_result is None

    def test_multiple_organizations_tracking(self, test_db):
        """Test tracking assessments for multiple organizations"""
        # Create assessments for different organizations
        orgs = ["Org A", "Org B", "Org C"]

        for org in orgs:
            for i in range(3):
                create_assessment(
                    test_db,
                    questionnaire_responses={"test": f"data{i}"},
                    organization_name=org
                )

        # Verify total count
        all_assessments = list_assessments(test_db)
        assert len(all_assessments) == 9

        # Verify per-organization filtering
        org_a_assessments = list_assessments(test_db, organization_name="Org A")
        assert len(org_a_assessments) == 3

        for assessment in org_a_assessments:
            assert assessment.organization_name == "Org A"
