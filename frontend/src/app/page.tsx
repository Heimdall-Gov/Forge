'use client';

import { useState } from 'react';
import QuestionnaireForm from '@/components/QuestionnaireForm';
import AssessmentStatus from '@/components/AssessmentStatus';
import AssessmentResults from '@/components/AssessmentResults';
import { assessmentApi } from '@/lib/api';
import type { QuestionnaireResponse, AssessmentResult } from '@/types';
import { Shield } from 'lucide-react';

type AppState = 'questionnaire' | 'processing' | 'results';

export default function Home() {
  const [appState, setAppState] = useState<AppState>('questionnaire');
  const [assessmentId, setAssessmentId] = useState<string>('');
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleQuestionnaireSubmit = async (data: QuestionnaireResponse) => {
    setIsSubmitting(true);
    try {
      const response = await assessmentApi.createAssessment(data);
      setAssessmentId(response.assessment_id);
      setAppState('processing');
    } catch (error) {
      alert('Failed to create assessment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAssessmentComplete = async () => {
    try {
      const assessmentResult = await assessmentApi.getAssessmentResult(assessmentId);
      setResult(assessmentResult);
      setAppState('results');
    } catch (error) {
      alert('Failed to fetch assessment results. Please try again.');
    }
  };

  const handleNewAssessment = () => {
    setAppState('questionnaire');
    setAssessmentId('');
    setResult(null);
  };

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Forge
                </h1>
                <p className="text-xs text-muted-foreground">AI Compliance Platform</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="hidden md:flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <div className="h-2 w-2 rounded-full bg-green-500" />
                  System Online
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        {appState === 'questionnaire' && (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">
                AI Compliance Assessment
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Get automated compliance analysis for EU AI Act and NIST AI RMF. Complete the
                questionnaire below to receive a comprehensive assessment of your AI system.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white rounded-lg p-6 border shadow-sm">
                <div className="text-3xl mb-2">🎯</div>
                <h3 className="font-semibold mb-2">Comprehensive Analysis</h3>
                <p className="text-sm text-muted-foreground">
                  Multi-framework assessment covering EU AI Act and NIST AI RMF requirements
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 border shadow-sm">
                <div className="text-3xl mb-2">⚡</div>
                <h3 className="font-semibold mb-2">Fast Results</h3>
                <p className="text-sm text-muted-foreground">
                  Receive your detailed compliance report in approximately 90 seconds
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 border shadow-sm">
                <div className="text-3xl mb-2">📊</div>
                <h3 className="font-semibold mb-2">Actionable Insights</h3>
                <p className="text-sm text-muted-foreground">
                  Get specific recommendations and implementation steps for each gap
                </p>
              </div>
            </div>

            <QuestionnaireForm onSubmit={handleQuestionnaireSubmit} isLoading={isSubmitting} />
          </div>
        )}

        {appState === 'processing' && (
          <AssessmentStatus
            assessmentId={assessmentId}
            onComplete={handleAssessmentComplete}
          />
        )}

        {appState === 'results' && result && (
          <AssessmentResults result={result} onNewAssessment={handleNewAssessment} />
        )}
      </div>

      {/* Footer */}
      <footer className="border-t mt-20 py-8 bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-sm text-muted-foreground">
              © 2024 Heimdall Gov. Open source AI governance platform.
            </div>
            <div className="flex gap-6 text-sm">
              <a
                href="https://github.com/Heimdall-Gov/Forge"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                GitHub
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Documentation
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                API
              </a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
