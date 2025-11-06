"""
Tests for assessment_engine.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from assessment_engine import AssessmentEngine


class TestAssessmentEngineInit:
    """Test AssessmentEngine initialization"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_engine_initialization(self, mock_anthropic):
        """Test that engine initializes correctly"""
        engine = AssessmentEngine()

        assert engine.client is not None
        assert engine.model == "claude-sonnet-4-20250514"
        assert engine.framework_docs_dir.name == "framework-docs"

    @patch('assessment_engine.anthropic.Anthropic')
    def test_loads_framework_documents(self, mock_anthropic):
        """Test that framework documents are loaded on init"""
        engine = AssessmentEngine()

        # Should have loaded EU documents
        assert engine.eu_classification_text is not None
        assert engine.eu_requirements_text is not None

        # Should have loaded NIST documents
        assert engine.nist_govern_text is not None
        assert engine.nist_map_text is not None
        assert engine.nist_measure_text is not None
        assert engine.nist_manage_text is not None


class TestMakeLLMCallWithRetry:
    """Test _make_llm_call_with_retry method"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_successful_llm_call(self, mock_anthropic):
        """Test successful LLM call on first attempt"""
        engine = AssessmentEngine()

        # Mock response
        mock_content = Mock()
        mock_content.type = "tool_use"
        mock_content.input = {"test": "data"}

        mock_response = Mock()
        mock_response.content = [mock_content]

        engine.client.messages.create = Mock(return_value=mock_response)

        result = engine._make_llm_call_with_retry(
            prompt="Test prompt",
            max_tokens=1000,
            temperature=0,
            tools=[],
            tool_choice={}
        )

        assert result == {"test": "data"}
        assert engine.client.messages.create.call_count == 1

    @patch('assessment_engine.anthropic.Anthropic')
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_retry_on_failure(self, mock_sleep, mock_anthropic):
        """Test retry logic when LLM call fails"""
        engine = AssessmentEngine()

        # Mock to fail twice, then succeed
        mock_content = Mock()
        mock_content.type = "tool_use"
        mock_content.input = {"success": True}

        mock_response = Mock()
        mock_response.content = [mock_content]

        engine.client.messages.create = Mock(
            side_effect=[
                Exception("API Error"),
                Exception("API Error"),
                mock_response
            ]
        )

        result = engine._make_llm_call_with_retry(
            prompt="Test",
            max_tokens=1000,
            temperature=0,
            tools=[],
            tool_choice={},
            max_retries=3
        )

        assert result == {"success": True}
        assert engine.client.messages.create.call_count == 3

    @patch('assessment_engine.anthropic.Anthropic')
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_anthropic):
        """Test that exception is raised after max retries"""
        engine = AssessmentEngine()

        engine.client.messages.create = Mock(side_effect=Exception("API Error"))

        with pytest.raises(Exception) as exc_info:
            engine._make_llm_call_with_retry(
                prompt="Test",
                max_tokens=1000,
                temperature=0,
                tools=[],
                tool_choice={},
                max_retries=3
            )

        assert "failed after 3 attempts" in str(exc_info.value)


class TestCall1EuClassification:
    """Test call_1_eu_classification method"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_eu_classification_call(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result
    ):
        """Test EU classification LLM call"""
        engine = AssessmentEngine()

        # Mock the LLM response
        engine._make_llm_call_with_retry = Mock(return_value=sample_eu_classification_result)

        result = engine.call_1_eu_classification(sample_questionnaire_response)

        assert result["eu_classification"] == "HIGH_RISK"
        assert result["confidence"] == 0.92
        assert isinstance(result["rationale"], str)
        assert isinstance(result["annex_iii_categories"], list)

    @patch('assessment_engine.anthropic.Anthropic')
    def test_eu_classification_uses_correct_temperature(
        self,
        mock_anthropic,
        sample_questionnaire_response
    ):
        """Test that EU classification uses temperature 0"""
        engine = AssessmentEngine()

        # Mock to capture call arguments
        engine._make_llm_call_with_retry = Mock(return_value={
            "eu_classification": "HIGH_RISK",
            "rationale": "Test",
            "confidence": 0.9
        })

        engine.call_1_eu_classification(sample_questionnaire_response)

        # Verify temperature = 0 was used
        call_args = engine._make_llm_call_with_retry.call_args
        assert call_args[1]["temperature"] == 0

    @patch('assessment_engine.anthropic.Anthropic')
    def test_eu_classification_max_tokens(
        self,
        mock_anthropic,
        sample_questionnaire_response
    ):
        """Test that EU classification uses correct max_tokens"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value={
            "eu_classification": "HIGH_RISK",
            "rationale": "Test",
            "confidence": 0.9
        })

        engine.call_1_eu_classification(sample_questionnaire_response)

        # Verify max_tokens = 2000 as per PRD
        call_args = engine._make_llm_call_with_retry.call_args
        assert call_args[1]["max_tokens"] == 2000


class TestCall2EuRequirements:
    """Test call_2_eu_requirements method"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_eu_requirements_call(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result,
        sample_eu_requirements_result
    ):
        """Test EU requirements LLM call"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value=sample_eu_requirements_result)

        result = engine.call_2_eu_requirements(
            sample_questionnaire_response,
            sample_eu_classification_result
        )

        assert "applicable_articles" in result
        assert "requirements" in result
        assert isinstance(result["applicable_articles"], list)
        assert len(result["requirements"]) > 0

    @patch('assessment_engine.anthropic.Anthropic')
    def test_eu_requirements_max_tokens(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result
    ):
        """Test that EU requirements uses correct max_tokens"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value={
            "applicable_articles": [],
            "requirements": []
        })

        engine.call_2_eu_requirements(
            sample_questionnaire_response,
            sample_eu_classification_result
        )

        # Verify max_tokens = 4000 as per PRD
        call_args = engine._make_llm_call_with_retry.call_args
        assert call_args[1]["max_tokens"] == 4000


class TestCall3NistRequirements:
    """Test call_3_nist_requirements method"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_nist_requirements_call(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result,
        sample_nist_requirements_result
    ):
        """Test NIST requirements LLM call"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value=sample_nist_requirements_result)

        result = engine.call_3_nist_requirements(
            sample_questionnaire_response,
            sample_eu_classification_result
        )

        assert "applicable_subcategories" in result
        assert "priority_functions" in result
        assert "subcategory_details" in result
        assert isinstance(result["applicable_subcategories"], list)

    @patch('assessment_engine.anthropic.Anthropic')
    def test_nist_requirements_max_tokens(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result
    ):
        """Test that NIST requirements uses correct max_tokens"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value={
            "applicable_subcategories": [],
            "priority_functions": [],
            "subcategory_details": []
        })

        engine.call_3_nist_requirements(
            sample_questionnaire_response,
            sample_eu_classification_result
        )

        # Verify max_tokens = 6000 as per PRD
        call_args = engine._make_llm_call_with_retry.call_args
        assert call_args[1]["max_tokens"] == 6000


class TestCall4GapAnalysis:
    """Test call_4_gap_analysis method"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_gap_analysis_call(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_requirements_result,
        sample_nist_requirements_result,
        sample_gap_analysis_result
    ):
        """Test gap analysis LLM call"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value=sample_gap_analysis_result)

        result = engine.call_4_gap_analysis(
            sample_questionnaire_response,
            sample_eu_requirements_result,
            sample_nist_requirements_result
        )

        assert "gaps" in result
        assert "compliance_score" in result
        assert "score_breakdown" in result
        assert isinstance(result["compliance_score"], int)
        assert 0 <= result["compliance_score"] <= 100

    @patch('assessment_engine.anthropic.Anthropic')
    def test_gap_analysis_max_tokens(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_requirements_result,
        sample_nist_requirements_result
    ):
        """Test that gap analysis uses correct max_tokens"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value={
            "gaps": [],
            "compliance_score": 50,
            "score_breakdown": {}
        })

        engine.call_4_gap_analysis(
            sample_questionnaire_response,
            sample_eu_requirements_result,
            sample_nist_requirements_result
        )

        # Verify max_tokens = 16000 as per PRD
        call_args = engine._make_llm_call_with_retry.call_args
        assert call_args[1]["max_tokens"] == 16000

    @patch('assessment_engine.anthropic.Anthropic')
    def test_gap_analysis_temperature(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_requirements_result,
        sample_nist_requirements_result
    ):
        """Test that gap analysis uses temperature 0.5"""
        engine = AssessmentEngine()

        engine._make_llm_call_with_retry = Mock(return_value={
            "gaps": [],
            "compliance_score": 50,
            "score_breakdown": {}
        })

        engine.call_4_gap_analysis(
            sample_questionnaire_response,
            sample_eu_requirements_result,
            sample_nist_requirements_result
        )

        # Verify temperature = 0.5 as per PRD (for creative recommendations)
        call_args = engine._make_llm_call_with_retry.call_args
        assert call_args[1]["temperature"] == 0.5


class TestFilterNistContent:
    """Test _filter_nist_content method"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_filter_for_design_stage(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result
    ):
        """Test NIST filtering for design stage"""
        engine = AssessmentEngine()

        sample_questionnaire_response.stage = "design"

        filtered_content = engine._filter_nist_content(
            sample_questionnaire_response,
            sample_eu_classification_result
        )

        # Should include GOVERN and MAP
        assert "GOVERN" in filtered_content
        assert "MAP" in filtered_content

    @patch('assessment_engine.anthropic.Anthropic')
    def test_filter_for_deployment_stage(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result
    ):
        """Test NIST filtering for deployment stage"""
        engine = AssessmentEngine()

        sample_questionnaire_response.stage = "deployment"

        filtered_content = engine._filter_nist_content(
            sample_questionnaire_response,
            sample_eu_classification_result
        )

        # Should include GOVERN, MEASURE, and MANAGE
        assert "GOVERN" in filtered_content
        assert "MEASURE" in filtered_content
        assert "MANAGE" in filtered_content

    @patch('assessment_engine.anthropic.Anthropic')
    def test_filter_for_high_risk(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result
    ):
        """Test NIST filtering for high-risk systems"""
        engine = AssessmentEngine()

        sample_questionnaire_response.criticality = "high"

        filtered_content = engine._filter_nist_content(
            sample_questionnaire_response,
            sample_eu_classification_result
        )

        # High-risk should get all content
        assert "GOVERN" in filtered_content
        assert "MAP" in filtered_content
        assert "MEASURE" in filtered_content
        assert "MANAGE" in filtered_content


class TestRunCompleteAssessment:
    """Test run_complete_assessment method"""

    @patch('assessment_engine.anthropic.Anthropic')
    @patch('assessment_engine.build_cross_mapping')
    def test_complete_assessment_workflow(
        self,
        mock_build_mapping,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result,
        sample_eu_requirements_result,
        sample_nist_requirements_result,
        sample_gap_analysis_result
    ):
        """Test complete assessment workflow"""
        engine = AssessmentEngine()

        # Mock each LLM call
        engine.call_1_eu_classification = Mock(return_value=sample_eu_classification_result)
        engine.call_2_eu_requirements = Mock(return_value=sample_eu_requirements_result)
        engine.call_3_nist_requirements = Mock(return_value=sample_nist_requirements_result)
        engine.call_4_gap_analysis = Mock(return_value=sample_gap_analysis_result)

        # Mock cross-mapping
        mock_build_mapping.return_value = {
            "eu_to_nist": {"Article_14": ["MAP.3.5"]},
            "nist_to_eu": {"MAP.3.5": ["Article_14"]}
        }

        result = engine.run_complete_assessment(sample_questionnaire_response)

        # Verify all calls were made in sequence
        assert engine.call_1_eu_classification.called
        assert engine.call_2_eu_requirements.called
        assert engine.call_3_nist_requirements.called
        assert engine.call_4_gap_analysis.called

        # Verify result structure
        assert "timestamp" in result
        assert "eu_ai_act" in result
        assert "nist_ai_rmf" in result
        assert "gap_analysis" in result
        assert "cross_framework_mapping" in result
        assert "processing_time_seconds" in result

    @patch('assessment_engine.anthropic.Anthropic')
    def test_complete_assessment_result_structure(
        self,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result,
        sample_eu_requirements_result,
        sample_nist_requirements_result,
        sample_gap_analysis_result
    ):
        """Test that complete assessment returns correct structure"""
        engine = AssessmentEngine()

        # Mock all calls
        engine.call_1_eu_classification = Mock(return_value=sample_eu_classification_result)
        engine.call_2_eu_requirements = Mock(return_value=sample_eu_requirements_result)
        engine.call_3_nist_requirements = Mock(return_value=sample_nist_requirements_result)
        engine.call_4_gap_analysis = Mock(return_value=sample_gap_analysis_result)

        result = engine.run_complete_assessment(sample_questionnaire_response)

        # Check EU AI Act section
        assert result["eu_ai_act"]["classification"] == "HIGH_RISK"
        assert result["eu_ai_act"]["rationale"] is not None
        assert result["eu_ai_act"]["applicable_articles"] == [9, 10, 11, 12, 13, 14, 15]

        # Check NIST section
        assert result["nist_ai_rmf"]["applicable_subcategories"] is not None
        assert result["nist_ai_rmf"]["priority_functions"] is not None

        # Check gap analysis section
        assert result["gap_analysis"]["compliance_score"] == 35
        assert result["gap_analysis"]["gaps"] is not None

    @patch('assessment_engine.anthropic.Anthropic')
    def test_complete_assessment_error_handling(
        self,
        mock_anthropic,
        sample_questionnaire_response
    ):
        """Test error handling in complete assessment"""
        engine = AssessmentEngine()

        # Mock first call to fail
        engine.call_1_eu_classification = Mock(side_effect=Exception("API Error"))

        with pytest.raises(Exception) as exc_info:
            engine.run_complete_assessment(sample_questionnaire_response)

        assert "API Error" in str(exc_info.value)

    @patch('assessment_engine.anthropic.Anthropic')
    @patch('time.time')
    def test_complete_assessment_timing(
        self,
        mock_time,
        mock_anthropic,
        sample_questionnaire_response,
        sample_eu_classification_result,
        sample_eu_requirements_result,
        sample_nist_requirements_result,
        sample_gap_analysis_result
    ):
        """Test that processing time is calculated correctly"""
        engine = AssessmentEngine()

        # Mock time to return specific values
        mock_time.side_effect = [1000, 1078]  # 78 second difference

        # Mock all calls
        engine.call_1_eu_classification = Mock(return_value=sample_eu_classification_result)
        engine.call_2_eu_requirements = Mock(return_value=sample_eu_requirements_result)
        engine.call_3_nist_requirements = Mock(return_value=sample_nist_requirements_result)
        engine.call_4_gap_analysis = Mock(return_value=sample_gap_analysis_result)

        result = engine.run_complete_assessment(sample_questionnaire_response)

        assert result["processing_time_seconds"] == 78


class TestAssessmentEngineIntegration:
    """Integration tests for assessment engine"""

    @patch('assessment_engine.anthropic.Anthropic')
    def test_full_high_risk_assessment_flow(
        self,
        mock_anthropic,
        sample_questionnaire_response
    ):
        """Test full assessment flow for high-risk system"""
        engine = AssessmentEngine()

        # Create realistic mock responses
        classification = {
            "eu_classification": "HIGH_RISK",
            "rationale": "Medical diagnosis system",
            "annex_iii_categories": ["Healthcare"],
            "confidence": 0.95,
            "ambiguities": []
        }

        eu_reqs = {
            "applicable_articles": [9, 10, 12, 14, 15],
            "requirements": [
                {
                    "article": 9,
                    "title": "Risk Management",
                    "description": "Test",
                    "applies_to": "provider",
                    "mandatory": True
                }
            ]
        }

        nist_reqs = {
            "applicable_subcategories": ["GOVERN.1.1", "MAP.3.5"],
            "priority_functions": ["GOVERN", "MAP"],
            "subcategory_details": []
        }

        gaps = {
            "gaps": [],
            "compliance_score": 60,
            "score_breakdown": {
                "critical_gaps": 2,
                "high_gaps": 3,
                "medium_gaps": 5,
                "low_gaps": 1,
                "implemented": 10
            }
        }

        engine.call_1_eu_classification = Mock(return_value=classification)
        engine.call_2_eu_requirements = Mock(return_value=eu_reqs)
        engine.call_3_nist_requirements = Mock(return_value=nist_reqs)
        engine.call_4_gap_analysis = Mock(return_value=gaps)

        result = engine.run_complete_assessment(sample_questionnaire_response)

        # Verify complete result
        assert result["eu_ai_act"]["classification"] == "HIGH_RISK"
        assert result["gap_analysis"]["compliance_score"] == 60
        assert "cross_framework_mapping" in result
