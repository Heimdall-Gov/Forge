"""
Assessment Engine for AI Compliance Assessment Platform
Implements the 4 sequential LLM calls as specified in the PRD
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import anthropic

from questionnaire import QuestionnaireResponse, filter_questionnaire_for_call
from cross_framework_mapping import build_cross_mapping

load_dotenv()


class AssessmentEngine:
    """
    Core assessment engine that orchestrates 4 sequential LLM calls:
    1. EU AI Act Classification
    2. EU AI Act Requirements
    3. NIST AI RMF Requirements
    4. Gap Analysis + Recommendations
    """

    def __init__(self):
        """Initialize the assessment engine with Anthropic client"""
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        self.framework_docs_dir = Path("framework-docs")

        # Load framework documents on initialization
        self.eu_classification_text = self._load_document("eu-ai-act/classification.txt")
        self.eu_requirements_text = self._load_document("eu-ai-act/requirements.txt")
        self.nist_govern_text = self._load_document("nist-ai-rmf/govern.txt")
        self.nist_map_text = self._load_document("nist-ai-rmf/map.txt")
        self.nist_measure_text = self._load_document("nist-ai-rmf/measure.txt")
        self.nist_manage_text = self._load_document("nist-ai-rmf/manage.txt")

    def _load_document(self, relative_path: str) -> str:
        """Load a framework document"""
        doc_path = self.framework_docs_dir / relative_path
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not load {relative_path}: {e}")
            return f"# Document {relative_path} not found"

    def _make_llm_call_with_retry(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        tools: List[Dict],
        tool_choice: Dict,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make an LLM call with retry logic for handling failures.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation
            tools: Tool definitions for structured output
            tool_choice: Tool choice configuration
            max_retries: Maximum number of retry attempts

        Returns:
            Parsed tool input as dictionary
        """
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    tools=tools,
                    tool_choice=tool_choice,
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract structured output from tool use
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        return content_block.input

                raise ValueError("No tool use found in response")

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"LLM call failed after {max_retries} attempts: {e}")

    def call_1_eu_classification(self, responses: QuestionnaireResponse) -> Dict[str, Any]:
        """
        Call #1: EU AI Act Classification
        Determines risk tier: PROHIBITED, HIGH_RISK, LIMITED_RISK, or MINIMAL_RISK
        """
        # Filter questionnaire for this call (classification needs everything)
        filtered_responses = filter_questionnaire_for_call(responses, 'classification')

        # Build prompt
        prompt = f"""You are an expert in EU AI Act compliance. Classify this AI system.

<EU_AI_ACT_CLASSIFICATION_RULES>
{self.eu_classification_text}
</EU_AI_ACT_CLASSIFICATION_RULES>

<QUESTIONNAIRE_RESPONSES>
{json.dumps(filtered_responses, indent=2)}
</QUESTIONNAIRE_RESPONSES>

Instructions:
1. Check if system matches prohibited practices (Article 5)
2. Check if high-risk (Article 6 + Annex III)
3. Check if requires transparency (Article 50)
4. Otherwise classify as minimal risk

Provide classification with clear reasoning. Be specific about which Annex III categories apply if high-risk."""

        # Define tool schema for structured output
        tools = [{
            "name": "output_eu_classification",
            "description": "Output the EU AI Act classification result",
            "input_schema": {
                "type": "object",
                "properties": {
                    "eu_classification": {
                        "type": "string",
                        "enum": ["PROHIBITED", "HIGH_RISK", "LIMITED_RISK", "MINIMAL_RISK"],
                        "description": "The EU AI Act risk classification"
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Detailed explanation of the classification"
                    },
                    "annex_iii_categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of matched Annex III categories if high-risk"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score between 0 and 1"
                    },
                    "ambiguities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of unclear areas or ambiguities"
                    }
                },
                "required": ["eu_classification", "rationale", "confidence"]
            }
        }]

        tool_choice = {"type": "tool", "name": "output_eu_classification"}

        # Make LLM call
        result = self._make_llm_call_with_retry(
            prompt=prompt,
            max_tokens=2000,
            temperature=0,
            tools=tools,
            tool_choice=tool_choice
        )

        return result

    def call_2_eu_requirements(
        self,
        responses: QuestionnaireResponse,
        classification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call #2: EU AI Act Requirements
        Identifies applicable articles and specific obligations
        """
        # Filter questionnaire for this call (only system characteristics)
        filtered_responses = filter_questionnaire_for_call(responses, 'eu_requirements')

        # Build prompt
        prompt = f"""You are an expert in EU AI Act compliance. Identify applicable requirements.

<EU_AI_ACT_REQUIREMENTS>
{self.eu_requirements_text}
</EU_AI_ACT_REQUIREMENTS>

<SYSTEM_CLASSIFICATION>
Classification: {classification_result['eu_classification']}
Rationale: {classification_result['rationale']}
Annex III Categories: {classification_result.get('annex_iii_categories', [])}
</SYSTEM_CLASSIFICATION>

<SYSTEM_CHARACTERISTICS>
{json.dumps(filtered_responses, indent=2)}
</SYSTEM_CHARACTERISTICS>

Instructions:
Based on the classification, identify:
1. All applicable articles
2. Specific requirements from each article
3. Whether obligations apply to provider, deployer, or both

Be comprehensive and precise. Only include articles that actually apply based on the classification."""

        # Define tool schema
        tools = [{
            "name": "output_eu_requirements",
            "description": "Output the EU AI Act requirements",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicable_articles": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of applicable article numbers"
                    },
                    "requirements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "article": {"type": "integer"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "applies_to": {
                                    "type": "string",
                                    "enum": ["provider", "deployer", "both"]
                                },
                                "mandatory": {"type": "boolean"}
                            },
                            "required": ["article", "title", "description", "applies_to", "mandatory"]
                        }
                    }
                },
                "required": ["applicable_articles", "requirements"]
            }
        }]

        tool_choice = {"type": "tool", "name": "output_eu_requirements"}

        # Make LLM call
        result = self._make_llm_call_with_retry(
            prompt=prompt,
            max_tokens=4000,
            temperature=0,
            tools=tools,
            tool_choice=tool_choice
        )

        return result

    def call_3_nist_requirements(
        self,
        responses: QuestionnaireResponse,
        classification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call #3: NIST AI RMF Requirements
        Identifies applicable NIST subcategories with pre-filtering
        """
        # Filter questionnaire for this call (only system characteristics)
        filtered_responses = filter_questionnaire_for_call(responses, 'nist_requirements')

        # Pre-filter NIST content based on stage and risk level
        nist_text = self._filter_nist_content(responses, classification_result)

        # Build prompt
        prompt = f"""You are an expert in NIST AI Risk Management Framework. Identify applicable requirements.

<NIST_AI_RMF>
{nist_text}
</NIST_AI_RMF>

<CONTEXT>
EU AI Act Classification: {classification_result['eu_classification']}
System Stage: {responses.stage}
System Type: {responses.main_purpose}
Risk Level: {responses.criticality}
</CONTEXT>

<SYSTEM_CHARACTERISTICS>
{json.dumps(filtered_responses, indent=2)}
</SYSTEM_CHARACTERISTICS>

Instructions:
Identify:
1. All applicable NIST subcategories (format: GOVERN.1.1, MAP.3.5, etc.)
2. Priority functions (GOVERN, MAP, MEASURE, MANAGE)
3. Specific requirements for each subcategory

Note: GOVERN always applies to all AI systems. MAP, MEASURE, MANAGE are context-dependent."""

        # Define tool schema
        tools = [{
            "name": "output_nist_requirements",
            "description": "Output the NIST AI RMF requirements",
            "input_schema": {
                "type": "object",
                "properties": {
                    "applicable_subcategories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of applicable subcategory IDs"
                    },
                    "priority_functions": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["GOVERN", "MAP", "MEASURE", "MANAGE"]
                        },
                        "description": "Priority functions for this system"
                    },
                    "subcategory_details": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "function": {"type": "string"},
                                "category": {"type": "string"},
                                "description": {"type": "string"},
                                "rationale": {"type": "string"}
                            },
                            "required": ["id", "function", "description", "rationale"]
                        }
                    }
                },
                "required": ["applicable_subcategories", "priority_functions", "subcategory_details"]
            }
        }]

        tool_choice = {"type": "tool", "name": "output_nist_requirements"}

        # Make LLM call
        result = self._make_llm_call_with_retry(
            prompt=prompt,
            max_tokens=6000,
            temperature=0,
            tools=tools,
            tool_choice=tool_choice
        )

        return result

    def _filter_nist_content(
        self,
        responses: QuestionnaireResponse,
        classification_result: Dict[str, Any]
    ) -> str:
        """
        Pre-filter NIST content based on stage and risk level to reduce token usage.
        This implements the pre-filtering logic from PRD Section 3.2 Call #3.
        """
        # Always include GOVERN
        content_parts = [self.nist_govern_text]

        # Stage-based filtering
        if responses.stage in ["design", "development", "testing"]:
            content_parts.append(self.nist_map_text)
            # Add subset of MEASURE for testing
            content_parts.append("# MEASURE (Testing subset)\n" + self.nist_measure_text[:5000])

        if responses.stage in ["deployment", "post-market monitoring"]:
            content_parts.append(self.nist_measure_text)
            content_parts.append(self.nist_manage_text)

        # High-risk/critical systems get everything
        if responses.criticality == "high" or classification_result['eu_classification'] == "HIGH_RISK":
            content_parts = [
                self.nist_govern_text,
                self.nist_map_text,
                self.nist_measure_text,
                self.nist_manage_text
            ]

        return "\n\n".join(content_parts)

    def call_4_gap_analysis(
        self,
        responses: QuestionnaireResponse,
        eu_requirements: Dict[str, Any],
        nist_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call #4: Gap Analysis + Recommendations
        Compares current state vs requirements and generates actionable recommendations
        """
        # Filter questionnaire for this call (only governance maturity)
        filtered_responses = filter_questionnaire_for_call(responses, 'gap_analysis')

        # Build prompt
        prompt = f"""You are an expert compliance auditor. Analyze gaps between current state and requirements.

<APPLICABLE_EU_REQUIREMENTS>
{json.dumps(eu_requirements, indent=2)}
</APPLICABLE_EU_REQUIREMENTS>

<APPLICABLE_NIST_REQUIREMENTS>
{json.dumps(nist_requirements, indent=2)}
</APPLICABLE_NIST_REQUIREMENTS>

<CURRENT_STATE_GOVERNANCE>
{json.dumps(filtered_responses, indent=2)}
</CURRENT_STATE_GOVERNANCE>

Instructions:
For each requirement from EU and NIST:
1. Determine status: missing, partial, or implemented
2. Assign severity: critical, high, medium, low
3. Describe current state briefly
4. Provide implementation recommendations:
   - Concrete steps (3-5 actionable items)
   - Real-world examples from similar organizations
   - Estimated effort (time and resources)
   - Resources needed (roles, tools)
   - Common mistakes to avoid

Calculate overall compliance score (0-100%) based on gap severity distribution.

Be comprehensive in recommendations - this is the most valuable output for users."""

        # Define tool schema
        tools = [{
            "name": "output_gap_analysis",
            "description": "Output the gap analysis and recommendations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "gaps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "requirement_id": {"type": "string"},
                                "framework": {
                                    "type": "string",
                                    "enum": ["EU_AI_ACT", "NIST_AI_RMF"]
                                },
                                "requirement_title": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["missing", "partial", "implemented"]
                                },
                                "severity": {
                                    "type": "string",
                                    "enum": ["critical", "high", "medium", "low"]
                                },
                                "current_state": {"type": "string"},
                                "recommendations": {
                                    "type": "object",
                                    "properties": {
                                        "implementation_steps": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "examples": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "effort_estimate": {"type": "string"},
                                        "resources_needed": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "common_mistakes": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    },
                                    "required": ["implementation_steps", "examples", "effort_estimate", "resources_needed"]
                                }
                            },
                            "required": ["requirement_id", "framework", "requirement_title", "status", "severity", "current_state", "recommendations"]
                        }
                    },
                    "compliance_score": {
                        "type": "integer",
                        "description": "Overall compliance score 0-100"
                    },
                    "score_breakdown": {
                        "type": "object",
                        "properties": {
                            "critical_gaps": {"type": "integer"},
                            "high_gaps": {"type": "integer"},
                            "medium_gaps": {"type": "integer"},
                            "low_gaps": {"type": "integer"},
                            "implemented": {"type": "integer"}
                        },
                        "required": ["critical_gaps", "high_gaps", "medium_gaps", "low_gaps", "implemented"]
                    }
                },
                "required": ["gaps", "compliance_score", "score_breakdown"]
            }
        }]

        tool_choice = {"type": "tool", "name": "output_gap_analysis"}

        # Make LLM call
        result = self._make_llm_call_with_retry(
            prompt=prompt,
            max_tokens=16000,
            temperature=0.5,  # Higher temperature for creative recommendations
            tools=tools,
            tool_choice=tool_choice
        )

        return result

    def run_complete_assessment(
        self,
        responses: QuestionnaireResponse
    ) -> Dict[str, Any]:
        """
        Run the complete 4-step assessment process.

        Returns:
            Complete assessment result matching PRD Section 3.4 format
        """
        start_time = time.time()

        try:
            # Call #1: EU AI Act Classification
            print("Running Call #1: EU AI Act Classification...")
            classification_result = self.call_1_eu_classification(responses)

            # Call #2: EU AI Act Requirements
            print("Running Call #2: EU AI Act Requirements...")
            eu_requirements_result = self.call_2_eu_requirements(responses, classification_result)

            # Call #3: NIST AI RMF Requirements
            print("Running Call #3: NIST AI RMF Requirements...")
            nist_requirements_result = self.call_3_nist_requirements(responses, classification_result)

            # Call #4: Gap Analysis
            print("Running Call #4: Gap Analysis and Recommendations...")
            gap_analysis_result = self.call_4_gap_analysis(
                responses,
                eu_requirements_result,
                nist_requirements_result
            )

            # Build cross-framework mapping
            print("Building cross-framework mapping...")
            cross_mapping = build_cross_mapping(
                eu_requirements_result['applicable_articles'],
                nist_requirements_result['applicable_subcategories']
            )

            # Calculate processing time
            processing_time = int(time.time() - start_time)

            # Assemble final result
            final_result = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "organization_name": getattr(responses, 'organization_type', 'Unknown'),
                "processing_time_seconds": processing_time,

                "eu_ai_act": {
                    "classification": classification_result['eu_classification'],
                    "rationale": classification_result['rationale'],
                    "annex_iii_categories": classification_result.get('annex_iii_categories', []),
                    "confidence": classification_result['confidence'],
                    "ambiguities": classification_result.get('ambiguities', []),
                    "applicable_articles": eu_requirements_result['applicable_articles'],
                    "requirements": eu_requirements_result['requirements']
                },

                "nist_ai_rmf": {
                    "applicable_subcategories": nist_requirements_result['applicable_subcategories'],
                    "priority_functions": nist_requirements_result['priority_functions'],
                    "subcategory_details": nist_requirements_result['subcategory_details']
                },

                "gap_analysis": {
                    "gaps": gap_analysis_result['gaps'],
                    "compliance_score": gap_analysis_result['compliance_score'],
                    "score_breakdown": gap_analysis_result['score_breakdown']
                },

                "cross_framework_mapping": cross_mapping
            }

            print(f"Assessment completed successfully in {processing_time} seconds")
            return final_result

        except Exception as e:
            print(f"Error during assessment: {e}")
            raise
