// Backend API Types
export interface QuestionnaireResponse {
  organization_type: string;
  industry: string;
  regions: string[];
  organization_size: string;
  main_purpose: string;
  data_types: string[];
  stage: string;
  developer: string;
  criticality: string;
  policies: string;
  designated_team: string;
  approval_process: string;
  record_keeping: string;
  affects_rights: string;
  human_oversight: string;
  testing: string;
  complaint_mechanism: string;
  goal: string;
  preference: string;
  standards: string[];
}

export interface AssessmentRequest {
  questionnaire_responses: QuestionnaireResponse;
}

export interface AssessmentStatusResponse {
  assessment_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  processing_time_seconds?: number;
  error_message?: string;
  compliance_score?: number;
}

export interface Requirement {
  article: number;
  title: string;
  description: string;
  applies_to: string;
  mandatory: boolean;
}

export interface EUAIAct {
  classification: string;
  confidence: number;
  rationale: string;
  applicable_articles: number[];
  requirements: Requirement[];
}

export interface NISTSubcategoryDetail {
  id: string;
  function: string;
  category: string;
  description: string;
  rationale: string;
}

export interface NISTRMF {
  applicable_subcategories: string[];
  priority_functions: string[];
  subcategory_details: NISTSubcategoryDetail[];
}

export interface GapRecommendations {
  implementation_steps: string[];
  examples: string[];
  effort_estimate: string;
  resources_needed: string[];
  common_mistakes?: string[];
}

export interface Gap {
  requirement_id: string;
  framework: string;
  requirement_title: string;
  status: string;
  severity: string;
  current_state: string;
  recommendations: GapRecommendations;
}

export interface ScoreBreakdown {
  critical_gaps: number;
  high_gaps: number;
  medium_gaps: number;
  low_gaps: number;
  implemented: number;
}

export interface GapAnalysis {
  gaps: Gap[];
  compliance_score: number;
  score_breakdown: ScoreBreakdown;
}

export interface CrossFrameworkMapping {
  eu_to_nist: Record<string, string[]>;
  nist_to_eu: Record<string, string[]>;
}

export interface AssessmentResult {
  assessment_id: string;
  organization_name: string;
  timestamp: string;
  processing_time_seconds: number;
  eu_ai_act: EUAIAct;
  nist_ai_rmf: NISTRMF;
  gap_analysis: GapAnalysis;
  cross_framework_mapping: CrossFrameworkMapping;
}

export interface Question {
  id: string;
  text: string;
  type: string;
  options?: string[];
  section?: string;
  required?: boolean;
}
