import axios from 'axios';
import type {
  QuestionnaireResponse,
  AssessmentStatusResponse,
  AssessmentResult,
  Question,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const assessmentApi = {
  // Get questionnaire questions
  getQuestions: async (): Promise<{ questions: Question[]; total: number; sections: string[] }> => {
    const response = await api.get('/api/questions');
    return response.data;
  },

  // Create new assessment
  createAssessment: async (
    responses: QuestionnaireResponse
  ): Promise<{
    status: string;
    assessment_id: string;
    message: string;
    status_url: string;
    estimated_time_seconds: number;
  }> => {
    const response = await api.post('/api/assessment', {
      questionnaire_responses: responses,
    });
    return response.data;
  },

  // Get assessment status
  getAssessmentStatus: async (assessmentId: string): Promise<AssessmentStatusResponse> => {
    const response = await api.get(`/api/assessment/${assessmentId}/status`);
    return response.data;
  },

  // Get assessment result
  getAssessmentResult: async (assessmentId: string): Promise<AssessmentResult> => {
    const response = await api.get(`/api/assessment/${assessmentId}`);
    return response.data;
  },

  // Export assessment as PDF
  exportPDF: async (assessmentId: string): Promise<Blob> => {
    const response = await api.get(`/api/assessment/${assessmentId}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<{ status: string; timestamp: string; service: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
