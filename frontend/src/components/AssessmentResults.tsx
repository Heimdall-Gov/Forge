'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { AssessmentResult } from '@/types';
import { assessmentApi } from '@/lib/api';
import { downloadBlob, formatDate, getRiskLevelColor, getSeverityColor } from '@/lib/utils';
import {
  Download,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Shield,
  TrendingUp,
  BarChart3,
} from 'lucide-react';

interface AssessmentResultsProps {
  result: AssessmentResult;
  onNewAssessment: () => void;
}

export default function AssessmentResults({ result, onNewAssessment }: AssessmentResultsProps) {
  const [exportingPDF, setExportingPDF] = useState(false);

  const handleExportPDF = async () => {
    try {
      setExportingPDF(true);
      const blob = await assessmentApi.exportPDF(result.assessment_id);
      downloadBlob(blob, `assessment-${result.assessment_id}.pdf`);
    } catch (error) {
      alert('Failed to export PDF. Please try again.');
    } finally {
      setExportingPDF(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Needs Improvement';
    return 'Critical';
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header with Actions */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">AI Compliance Assessment Report</h1>
          <p className="text-muted-foreground mt-1">
            {result.organization_name} • {formatDate(result.timestamp)}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportPDF} disabled={exportingPDF}>
            <Download className="mr-2 h-4 w-4" />
            {exportingPDF ? 'Exporting...' : 'Export PDF'}
          </Button>
          <Button onClick={onNewAssessment}>
            <FileText className="mr-2 h-4 w-4" />
            New Assessment
          </Button>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <Shield className="mr-2 h-4 w-4 text-blue-500" />
              EU AI Act Classification
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Badge
                className={`${getRiskLevelColor(result.eu_ai_act.classification)} text-white`}
              >
                {result.eu_ai_act.classification}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {(result.eu_ai_act.confidence * 100).toFixed(0)}% confidence
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <BarChart3 className="mr-2 h-4 w-4 text-purple-500" />
              Compliance Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${getScoreColor(result.gap_analysis.compliance_score)}`}>
              {result.gap_analysis.compliance_score}
              <span className="text-lg">/100</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {getScoreLabel(result.gap_analysis.compliance_score)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center">
              <TrendingUp className="mr-2 h-4 w-4 text-green-500" />
              Processing Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{result.processing_time_seconds}s</div>
            <p className="text-xs text-muted-foreground mt-1">Analysis completed</p>
          </CardContent>
        </Card>
      </div>

      {/* EU AI Act Details */}
      <Card>
        <CardHeader>
          <CardTitle>EU AI Act Analysis</CardTitle>
          <CardDescription>Risk classification and applicable requirements</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Classification Rationale</h3>
            <p className="text-sm text-muted-foreground">{result.eu_ai_act.rationale}</p>
          </div>

          <div>
            <h3 className="font-semibold mb-3">
              Applicable Articles ({result.eu_ai_act.applicable_articles.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {result.eu_ai_act.applicable_articles.map((article) => (
                <Badge key={article} variant="outline">
                  Article {article}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-3">Key Requirements</h3>
            <div className="space-y-3">
              {result.eu_ai_act.requirements.slice(0, 5).map((req, index) => (
                <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-sm">
                        Article {req.article}: {req.title}
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">{req.description}</p>
                    </div>
                    {req.mandatory && (
                      <Badge variant="destructive" className="ml-2">
                        Mandatory
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* NIST AI RMF Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>NIST AI Risk Management Framework</CardTitle>
          <CardDescription>Applicable functions and subcategories</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-3">Priority Functions</h3>
            <div className="flex flex-wrap gap-2">
              {result.nist_ai_rmf.priority_functions.map((func) => (
                <Badge key={func} className="bg-purple-100 text-purple-700 border-purple-300">
                  {func}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-3">
              Applicable Subcategories ({result.nist_ai_rmf.applicable_subcategories.length})
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {result.nist_ai_rmf.applicable_subcategories.slice(0, 12).map((subcat) => (
                <Badge key={subcat} variant="outline" className="justify-center">
                  {subcat}
                </Badge>
              ))}
            </div>
            {result.nist_ai_rmf.applicable_subcategories.length > 12 && (
              <p className="text-sm text-muted-foreground mt-2">
                +{result.nist_ai_rmf.applicable_subcategories.length - 12} more subcategories
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Gap Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Compliance Gaps & Recommendations</CardTitle>
          <CardDescription>
            Identified gaps and actionable steps to achieve compliance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {result.gap_analysis.score_breakdown.critical_gaps}
              </div>
              <div className="text-xs text-muted-foreground">Critical</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {result.gap_analysis.score_breakdown.high_gaps}
              </div>
              <div className="text-xs text-muted-foreground">High</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {result.gap_analysis.score_breakdown.medium_gaps}
              </div>
              <div className="text-xs text-muted-foreground">Medium</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {result.gap_analysis.score_breakdown.low_gaps}
              </div>
              <div className="text-xs text-muted-foreground">Low</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {result.gap_analysis.score_breakdown.implemented}
              </div>
              <div className="text-xs text-muted-foreground">Implemented</div>
            </div>
          </div>

          <div className="space-y-4 mt-6">
            {result.gap_analysis.gaps.slice(0, 5).map((gap, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getSeverityColor(gap.severity)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold flex items-center gap-2">
                      {gap.severity === 'critical' && <AlertTriangle className="h-4 w-4" />}
                      {gap.status === 'implemented' && <CheckCircle2 className="h-4 w-4" />}
                      {gap.requirement_title}
                    </h4>
                    <p className="text-xs mt-1">
                      {gap.framework} • {gap.requirement_id}
                    </p>
                  </div>
                  <Badge variant="outline">{gap.severity}</Badge>
                </div>

                <div className="space-y-3 text-sm">
                  <div>
                    <p className="font-medium">Current State:</p>
                    <p className="text-muted-foreground">{gap.current_state}</p>
                  </div>

                  <div>
                    <p className="font-medium mb-2">Implementation Steps:</p>
                    <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                      {gap.recommendations.implementation_steps.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ol>
                  </div>

                  <div className="flex gap-4 text-xs">
                    <span className="font-medium">
                      Effort: {gap.recommendations.effort_estimate}
                    </span>
                    <span className="text-muted-foreground">
                      Resources: {gap.recommendations.resources_needed.length}
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {result.gap_analysis.gaps.length > 5 && (
              <p className="text-sm text-muted-foreground text-center">
                +{result.gap_analysis.gaps.length - 5} more gaps identified (see full PDF report)
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Cross-Framework Mapping */}
      <Card>
        <CardHeader>
          <CardTitle>Cross-Framework Mapping</CardTitle>
          <CardDescription>How EU AI Act and NIST AI RMF requirements align</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">
            <p>
              This assessment identified{' '}
              {Object.keys(result.cross_framework_mapping.eu_to_nist).length} EU AI Act articles
              that map to {Object.keys(result.cross_framework_mapping.nist_to_eu).length} NIST AI
              RMF subcategories, showing significant overlap in compliance requirements.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
