'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { assessmentApi } from '@/lib/api';
import type { AssessmentStatusResponse } from '@/types';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';

interface AssessmentStatusProps {
  assessmentId: string;
  onComplete: () => void;
}

export default function AssessmentStatus({ assessmentId, onComplete }: AssessmentStatusProps) {
  const [status, setStatus] = useState<AssessmentStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        const statusData = await assessmentApi.getAssessmentStatus(assessmentId);
        setStatus(statusData);

        if (statusData.status === 'completed') {
          clearInterval(interval);
          setTimeout(onComplete, 1000); // Small delay before showing results
        } else if (statusData.status === 'failed') {
          clearInterval(interval);
          setError(statusData.error_message || 'Assessment failed');
        }
      } catch (err) {
        setError('Failed to fetch assessment status');
        clearInterval(interval);
      }
    };

    // Initial poll
    pollStatus();

    // Poll every 3 seconds
    interval = setInterval(pollStatus, 3000);

    return () => clearInterval(interval);
  }, [assessmentId, onComplete]);

  const getStatusIcon = () => {
    if (!status) return <Loader2 className="h-8 w-8 animate-spin text-blue-500" />;

    switch (status.status) {
      case 'completed':
        return <CheckCircle2 className="h-8 w-8 text-green-500" />;
      case 'failed':
        return <XCircle className="h-8 w-8 text-red-500" />;
      case 'processing':
        return <Loader2 className="h-8 w-8 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusBadge = () => {
    if (!status) return null;

    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'secondary',
      processing: 'default',
      completed: 'outline',
      failed: 'destructive',
    };

    return (
      <Badge variant={variants[status.status] || 'default'} className="text-sm">
        {status.status.toUpperCase()}
      </Badge>
    );
  };

  const getStatusMessage = () => {
    if (!status) return 'Initializing assessment...';

    switch (status.status) {
      case 'pending':
        return 'Your assessment is queued and will begin shortly...';
      case 'processing':
        return 'Analyzing your AI system against compliance frameworks...';
      case 'completed':
        return 'Assessment complete! Loading your results...';
      case 'failed':
        return error || 'Assessment failed. Please try again.';
      default:
        return 'Processing...';
    }
  };

  const processingSteps = [
    { label: 'EU AI Act Classification', complete: status?.status !== 'pending' },
    { label: 'NIST AI RMF Analysis', complete: status?.status === 'completed' || status?.status === 'failed' },
    { label: 'Gap Analysis', complete: status?.status === 'completed' },
    { label: 'Generating Report', complete: status?.status === 'completed' },
  ];

  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">{getStatusIcon()}</div>
          <CardTitle className="text-2xl">Processing Your Assessment</CardTitle>
          <CardDescription>{getStatusMessage()}</CardDescription>
          <div className="flex justify-center mt-4">{getStatusBadge()}</div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground text-center">
              Assessment ID: <span className="font-mono">{assessmentId}</span>
            </div>

            {status?.status === 'processing' && (
              <div className="space-y-3">
                <p className="text-sm font-medium text-center">Processing Steps</p>
                {processingSteps.map((step, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div
                      className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        step.complete ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                      }`}
                    >
                      {step.complete ? (
                        <CheckCircle2 className="h-5 w-5" />
                      ) : (
                        <div className="h-2 w-2 bg-current rounded-full" />
                      )}
                    </div>
                    <div
                      className={`flex-1 ${step.complete ? 'text-foreground' : 'text-muted-foreground'}`}
                    >
                      {step.label}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {status?.processing_time_seconds && (
              <div className="text-center text-sm text-muted-foreground">
                Processing time: {status.processing_time_seconds}s
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
              <p className="font-medium mb-1">💡 Did you know?</p>
              <p>
                This assessment analyzes your AI system against both EU AI Act requirements and NIST AI
                Risk Management Framework guidelines to provide comprehensive compliance insights.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
