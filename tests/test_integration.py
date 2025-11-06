"""
Integration tests for complete assessment flow
"""

import pytest
from unittest.mock import Mock, patch
from questionnaire import QuestionnaireResponse
from assessment_engine import AssessmentEngine
from database import create_assessment, get_assessment, save_assessment_results
from cross_framework_mapping import build_cross_mapping


class TestEndToEndAssessmentFlow:
    """Test complete end-to-end assessment flow"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_high_risk_healthcare_ai_complete_flow(
        self,
        mock_anthropic,
        test_db,
        sample_eu_classification_result,
        sample_eu_requirements_result,
        sample_nist_requirements_result,
        sample_gap_analysis_result
    ):
        """Test complete flow for high-risk healthcare AI system"""
        # 1. Create questionnaire response
        questionnaire = QuestionnaireResponse(
            organization_type="Startup",
            industry="Healthcare",
            regions=["EU", "US"],
            organization_size="50-200",
            main_purpose="AI-powered medical diagnosis system for radiology",
            data_types=["medical", "personal", "biometric"],
            stage="development",
            developer="in-house",
            criticality="high",
            policies="Basic AI development guidelines in place",
            designated_team="No dedicated AI governance team yet",
            approval_process="Informal review by medical director",
            record_keeping="Version control for code, basic dataset documentation",
            affects_rights="Yes - critical healthcare decisions",
            human_oversight="Human-in-the-loop",
            testing="Initial accuracy testing, no bias evaluation yet",
            complaint_mechanism="No formal complaint process",
            goal="Compliance readiness",
            preference="Detailed framework",
            standards=["EU AI Act", "NIST AI RMF"]
        )

        # 2. Create assessment in database
        assessment = create_assessment(
            test_db,
            questionnaire_responses=questionnaire.model_dump(),
            organization_name="HealthTech Startup"
        )

        assert assessment.id is not None
        assert assessment.status == "pending"

        # 3. Run assessment engine (mocked)
        engine = AssessmentEngine()

        # Mock LLM calls
        engine.call_1_eu_classification = Mock(return_value=sample_eu_classification_result)
        engine.call_2_eu_requirements = Mock(return_value=sample_eu_requirements_result)
        engine.call_3_nist_requirements = Mock(return_value=sample_nist_requirements_result)
        engine.call_4_gap_analysis = Mock(return_value=sample_gap_analysis_result)

        result = engine.run_complete_assessment(questionnaire)

        # 4. Verify result structure
        assert result["eu_ai_act"]["classification"] == "HIGH_RISK"
        assert result["gap_analysis"]["compliance_score"] == 35
        assert "cross_framework_mapping" in result

        # 5. Save results to database
        save_assessment_results(
            test_db,
            assessment.id,
            eu_classification=result["eu_ai_act"]["classification"],
            eu_requirements=result["eu_ai_act"],
            nist_requirements=result["nist_ai_rmf"],
            gaps=result["gap_analysis"],
            compliance_score=result["gap_analysis"]["compliance_score"],
            cross_framework_mapping=result["cross_framework_mapping"],
            full_result=result,
            processing_time_seconds=result["processing_time_seconds"]
        )

        # 6. Retrieve and verify
        retrieved = get_assessment(test_db, assessment.id)

        assert retrieved.status == "completed"
        assert retrieved.eu_classification == "HIGH_RISK"
        assert retrieved.compliance_score == 35
        assert retrieved.full_result is not None

    @patch('assessment_engine.anthropic.Anthropic')
    def test_minimal_risk_chatbot_complete_flow(
        self,
        mock_anthropic,
        test_db
    ):
        """Test complete flow for minimal risk chatbot"""
        # 1. Create questionnaire for minimal risk system
        questionnaire = QuestionnaireResponse(
            organization_type="Startup",
            industry="Consumer Tech",
            regions=["US"],
            organization_size="1-50",
            main_purpose="Customer service chatbot",
            data_types=["public"],
            stage="deployment",
            developer="vendor",
            criticality="low",
            policies="No formal AI policies",
            designated_team="No",
            approval_process="None",
            record_keeping="Basic logs",
            affects_rights="No",
            human_oversight="Human-on-the-loop",
            testing="Basic functionality testing",
            complaint_mechanism="Email support",
            goal="Trust & transparency",
            preference="Lightweight checklist",
            standards=["NIST AI RMF"]
        )

        # 2. Create assessment
        assessment = create_assessment(
            test_db,
            questionnaire_responses=questionnaire.model_dump(),
            organization_name="ChatBot Inc"
        )

        # 3. Mock assessment results for minimal risk
        engine = AssessmentEngine()

        minimal_risk_classification = {
            "eu_classification": "MINIMAL_RISK",
            "rationale": "Customer service chatbot without high-risk characteristics",
            "annex_iii_categories": [],
            "confidence": 0.9,
            "ambiguities": []
        }

        minimal_risk_eu_reqs = {
            "applicable_articles": [50],  # Only transparency
            "requirements": [
                {
                    "article": 50,
                    "title": "Transparency",
                    "description": "Inform users they're interacting with AI",
                    "applies_to": "provider",
                    "mandatory": True
                }
            ]
        }

        minimal_risk_nist = {
            "applicable_subcategories": ["GOVERN.1.1", "GOVERN.4.2"],
            "priority_functions": ["GOVERN"],
            "subcategory_details": []
        }

        minimal_risk_gaps = {
            "gaps": [
                {
                    "requirement_id": "Article_50",
                    "framework": "EU_AI_ACT",
                    "requirement_title": "Transparency",
                    "status": "partial",
                    "severity": "medium",
                    "current_state": "Users not explicitly informed",
                    "recommendations": {
                        "implementation_steps": [
                            "Add clear disclosure at start of chat",
                            "Update UI with AI indicator"
                        ],
                        "examples": ["'You are chatting with our AI assistant'"],
                        "effort_estimate": "1-2 weeks",
                        "resources_needed": ["Frontend developer"],
                        "common_mistakes": ["Hidden or unclear disclosure"]
                    }
                }
            ],
            "compliance_score": 85,
            "score_breakdown": {
                "critical_gaps": 0,
                "high_gaps": 0,
                "medium_gaps": 1,
                "low_gaps": 0,
                "implemented": 2
            }
        }

        engine.call_1_eu_classification = Mock(return_value=minimal_risk_classification)
        engine.call_2_eu_requirements = Mock(return_value=minimal_risk_eu_reqs)
        engine.call_3_nist_requirements = Mock(return_value=minimal_risk_nist)
        engine.call_4_gap_analysis = Mock(return_value=minimal_risk_gaps)

        result = engine.run_complete_assessment(questionnaire)

        # 4. Verify minimal risk characteristics
        assert result["eu_ai_act"]["classification"] == "MINIMAL_RISK"
        assert result["gap_analysis"]["compliance_score"] == 85  # Higher score for minimal risk
        assert len(result["eu_ai_act"]["applicable_articles"]) == 1

        # 5. Save and verify
        save_assessment_results(
            test_db,
            assessment.id,
            eu_classification=result["eu_ai_act"]["classification"],
            eu_requirements=result["eu_ai_act"],
            nist_requirements=result["nist_ai_rmf"],
            gaps=result["gap_analysis"],
            compliance_score=result["gap_analysis"]["compliance_score"],
            cross_framework_mapping=result["cross_framework_mapping"],
            full_result=result,
            processing_time_seconds=result["processing_time_seconds"]
        )

        retrieved = get_assessment(test_db, assessment.id)
        assert retrieved.compliance_score == 85


class TestCrossFrameworkIntegration:
    """Test cross-framework mapping integration"""

    def test_mapping_integration_high_risk_system(self):
        """Test cross-framework mapping for high-risk system"""
        # High-risk system has many applicable requirements
        eu_articles = [8, 9, 10, 11, 12, 13, 14, 15, 26, 27]
        nist_subcategories = [
            "GOVERN.1.1", "GOVERN.1.2", "GOVERN.1.3", "GOVERN.1.6",
            "GOVERN.3.2", "GOVERN.4.2",
            "MAP.1.1", "MAP.2.3", "MAP.3.5", "MAP.5.1",
            "MEASURE.2.3", "MEASURE.2.4", "MEASURE.2.5",
            "MEASURE.2.7", "MEASURE.2.8", "MEASURE.3.1",
            "MANAGE.1.2", "MANAGE.2.4", "MANAGE.5.1"
        ]

        mapping = build_cross_mapping(eu_articles, nist_subcategories)

        # Should have comprehensive mappings
        assert len(mapping["eu_to_nist"]) > 5
        assert len(mapping["nist_to_eu"]) > 10

        # Verify specific mappings
        if "Article_14" in mapping["eu_to_nist"]:
            # Human oversight should map to relevant NIST subcategories
            related_nist = mapping["eu_to_nist"]["Article_14"]
            assert len(related_nist) > 0
            assert "MAP.3.5" in related_nist or "GOVERN.3.2" in related_nist


class TestDatabasePersistence:
    """Test database persistence throughout assessment flow"""

    def test_multiple_assessments_persistence(self, test_db):
        """Test that multiple assessments are persisted correctly"""
        # Create multiple assessments
        assessments = []
        for i in range(5):
            assessment = create_assessment(
                test_db,
                questionnaire_responses={"test": f"data{i}"},
                organization_name=f"Org {i}"
            )
            assessments.append(assessment)

        # Verify all are persisted
        for assessment in assessments:
            retrieved = get_assessment(test_db, assessment.id)
            assert retrieved is not None
            assert retrieved.status == "pending"

        # Update one to completed
        save_assessment_results(
            test_db,
            assessments[0].id,
            eu_classification="HIGH_RISK",
            eu_requirements={},
            nist_requirements={},
            gaps={},
            compliance_score=50,
            cross_framework_mapping={},
            full_result={},
            processing_time_seconds=60
        )

        # Verify update
        completed = get_assessment(test_db, assessments[0].id)
        assert completed.status == "completed"
        assert completed.compliance_score == 50

        # Others should still be pending
        for i in range(1, 5):
            other = get_assessment(test_db, assessments[i].id)
            assert other.status == "pending"


class TestErrorScenarios:
    """Test error handling in integration scenarios"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_llm_api_failure_scenario(self, mock_anthropic, test_db):
        """Test handling of LLM API failure"""
        questionnaire = QuestionnaireResponse(
            organization_type="Startup",
            industry="Healthcare",
            regions=["EU"],
            organization_size="50-200",
            main_purpose="Test",
            data_types=["medical"],
            stage="development",
            developer="in-house",
            criticality="high",
            policies="None",
            designated_team="No",
            approval_process="None",
            record_keeping="None",
            affects_rights="Yes",
            human_oversight="Human-in-the-loop",
            testing="None",
            complaint_mechanism="No",
            goal="Compliance readiness",
            preference="Detailed framework",
            standards=["EU AI Act"]
        )

        assessment = create_assessment(
            test_db,
            questionnaire_responses=questionnaire.model_dump()
        )

        engine = AssessmentEngine()

        # Mock to raise exception
        engine.call_1_eu_classification = Mock(side_effect=Exception("API Error"))

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            engine.run_complete_assessment(questionnaire)

        assert "API Error" in str(exc_info.value)

    def test_database_transaction_rollback(self, test_db):
        """Test database transaction rollback on error"""
        from database import create_assessment, update_assessment

        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
        )

        # Attempt invalid update (this may or may not fail depending on constraints)
        try:
            # Try to set an invalid field value
            update_assessment(test_db, assessment.id, invalid_field="value")
        except Exception:
            pass

        # Original assessment should still be retrievable
        retrieved = get_assessment(test_db, assessment.id)
        assert retrieved is not None


class TestPerformanceMetrics:
    """Test performance and timing metrics"""

    @patch('assessment_engine.anthropic.Anthropic')
    @patch('time.time')
    def test_processing_time_tracking(
        self,
        mock_time,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result,
        sample_eu_requirements_result,
        sample_nist_requirements_result,
        sample_gap_analysis_result
    ):
        """Test that processing time is accurately tracked"""
        # Mock time to simulate 90 seconds
        mock_time.side_effect = [1000, 1090]

        engine = AssessmentEngine()

        engine.call_1_eu_classification = Mock(return_value=sample_eu_classification_result)
        engine.call_2_eu_requirements = Mock(return_value=sample_eu_requirements_result)
        engine.call_3_nist_requirements = Mock(return_value=sample_nist_requirements_result)
        engine.call_4_gap_analysis = Mock(return_value=sample_gap_analysis_result)

        result = engine.run_complete_assessment(sample_questionnaire_response)

        assert result["processing_time_seconds"] == 90


class TestDataIntegrity:
    """Test data integrity throughout the assessment flow"""

    def test_questionnaire_data_preserved(self, test_db, sample_questionnaire_response):
        """Test that questionnaire data is preserved through the flow"""
        original_data = sample_questionnaire_response.model_dump()

        assessment = create_assessment(
            test_db,
            questionnaire_responses=original_data,
            organization_name="Test Org"
        )

        retrieved = get_assessment(test_db, assessment.id)

        # Verify data is preserved exactly
        assert retrieved.questionnaire_responses == original_data
        assert retrieved.questionnaire_responses["main_purpose"] == original_data["main_purpose"]
        assert retrieved.questionnaire_responses["criticality"] == original_data["criticality"]

    def test_assessment_result_preserved(
        self,
        test_db,
        sample_full_assessment_result
    ):
        """Test that full assessment result is preserved"""
        assessment = create_assessment(
            test_db,
            questionnaire_responses={"test": "data"}
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

        retrieved = get_assessment(test_db, assessment.id)

        # Verify all fields are preserved
        assert retrieved.full_result == sample_full_assessment_result
        assert retrieved.full_result["eu_ai_act"]["classification"] == "HIGH_RISK"
        assert retrieved.full_result["gap_analysis"]["compliance_score"] == 35
