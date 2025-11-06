'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { QuestionnaireResponse } from '@/types';
import { Loader2 } from 'lucide-react';

interface QuestionnaireFormProps {
  onSubmit: (data: QuestionnaireResponse) => Promise<void>;
  isLoading?: boolean;
}

export default function QuestionnaireForm({ onSubmit, isLoading = false }: QuestionnaireFormProps) {
  const [formData, setFormData] = useState<Partial<QuestionnaireResponse>>({
    organization_type: '',
    industry: '',
    regions: [],
    organization_size: '',
    main_purpose: '',
    data_types: [],
    stage: '',
    developer: '',
    criticality: '',
    policies: '',
    designated_team: '',
    approval_process: '',
    record_keeping: '',
    affects_rights: '',
    human_oversight: '',
    testing: '',
    complaint_mechanism: '',
    goal: '',
    preference: '',
    standards: [],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData as QuestionnaireResponse);
  };

  const handleMultiSelect = (field: keyof QuestionnaireResponse, value: string) => {
    const currentValues = (formData[field] as string[]) || [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter((v) => v !== value)
      : [...currentValues, value];
    setFormData({ ...formData, [field]: newValues });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Organization Information */}
      <Card>
        <CardHeader>
          <CardTitle>Organization Information</CardTitle>
          <CardDescription>Tell us about your organization</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Organization Type</label>
              <select
                className="w-full p-3 border rounded-md bg-white"
                value={formData.organization_type}
                onChange={(e) => setFormData({ ...formData, organization_type: e.target.value })}
                required
              >
                <option value="">Select type...</option>
                <option value="Startup">Startup</option>
                <option value="SME">SME</option>
                <option value="Enterprise">Enterprise</option>
                <option value="Government">Government</option>
                <option value="Non-profit">Non-profit</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Industry</label>
              <select
                className="w-full p-3 border rounded-md bg-white"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                required
              >
                <option value="">Select industry...</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Finance">Finance</option>
                <option value="Education">Education</option>
                <option value="Retail">Retail</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Technology">Technology</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Organization Size</label>
              <select
                className="w-full p-3 border rounded-md bg-white"
                value={formData.organization_size}
                onChange={(e) => setFormData({ ...formData, organization_size: e.target.value })}
                required
              >
                <option value="">Select size...</option>
                <option value="1-10">1-10 employees</option>
                <option value="11-50">11-50 employees</option>
                <option value="50-200">50-200 employees</option>
                <option value="200-1000">200-1000 employees</option>
                <option value="1000+">1000+ employees</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Regions of Operation</label>
              <div className="space-y-2">
                {['EU', 'US', 'UK', 'Asia', 'Other'].map((region) => (
                  <label key={region} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={(formData.regions || []).includes(region)}
                      onChange={() => handleMultiSelect('regions', region)}
                      className="rounded"
                    />
                    <span className="text-sm">{region}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI System Information */}
      <Card>
        <CardHeader>
          <CardTitle>AI System Information</CardTitle>
          <CardDescription>Describe your AI system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Main Purpose of AI System</label>
            <textarea
              className="w-full p-3 border rounded-md bg-white"
              rows={3}
              value={formData.main_purpose}
              onChange={(e) => setFormData({ ...formData, main_purpose: e.target.value })}
              placeholder="Describe the main purpose and functionality of your AI system..."
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Development Stage</label>
              <select
                className="w-full p-3 border rounded-md bg-white"
                value={formData.stage}
                onChange={(e) => setFormData({ ...formData, stage: e.target.value })}
                required
              >
                <option value="">Select stage...</option>
                <option value="concept">Concept/Planning</option>
                <option value="development">Development</option>
                <option value="testing">Testing</option>
                <option value="production">Production/Deployed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Criticality Level</label>
              <select
                className="w-full p-3 border rounded-md bg-white"
                value={formData.criticality}
                onChange={(e) => setFormData({ ...formData, criticality: e.target.value })}
                required
              >
                <option value="">Select criticality...</option>
                <option value="low">Low - Minimal impact on users</option>
                <option value="medium">Medium - Moderate impact</option>
                <option value="high">High - Significant impact on safety/rights</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Data Types Used</label>
            <div className="grid grid-cols-2 gap-2">
              {['Personal', 'Medical', 'Financial', 'Biometric', 'Other'].map((type) => (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={(formData.data_types || []).includes(type.toLowerCase())}
                    onChange={() => handleMultiSelect('data_types', type.toLowerCase())}
                    className="rounded"
                  />
                  <span className="text-sm">{type}</span>
                </label>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Governance & Compliance */}
      <Card>
        <CardHeader>
          <CardTitle>Governance & Compliance</CardTitle>
          <CardDescription>Current governance practices</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Human Oversight</label>
              <select
                className="w-full p-3 border rounded-md bg-white"
                value={formData.human_oversight}
                onChange={(e) => setFormData({ ...formData, human_oversight: e.target.value })}
                required
              >
                <option value="">Select oversight level...</option>
                <option value="Human-in-the-loop">Human-in-the-loop (review each decision)</option>
                <option value="Human-on-the-loop">Human-on-the-loop (can intervene)</option>
                <option value="Human-over-the-loop">Human-over-the-loop (monitor overall)</option>
                <option value="None">No human oversight</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Testing Practices</label>
              <select
                className="w-full p-3 border rounded-md bg-white"
                value={formData.testing}
                onChange={(e) => setFormData({ ...formData, testing: e.target.value })}
                required
              >
                <option value="">Select testing level...</option>
                <option value="Comprehensive">Comprehensive testing & validation</option>
                <option value="Basic">Basic testing</option>
                <option value="Ad-hoc">Ad-hoc testing</option>
                <option value="None">No formal testing</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Current AI Policies</label>
            <textarea
              className="w-full p-3 border rounded-md bg-white"
              rows={3}
              value={formData.policies}
              onChange={(e) => setFormData({ ...formData, policies: e.target.value })}
              placeholder="Describe any existing AI governance policies or practices..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Compliance Standards of Interest</label>
            <div className="space-y-2">
              {['EU AI Act', 'NIST AI RMF', 'ISO/IEC 42001', 'Other'].map((standard) => (
                <label key={standard} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={(formData.standards || []).includes(standard)}
                    onChange={() => handleMultiSelect('standards', standard)}
                    className="rounded"
                  />
                  <span className="text-sm">{standard}</span>
                </label>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Button type="submit" size="lg" className="w-full" disabled={isLoading}>
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Creating Assessment...
          </>
        ) : (
          'Start Compliance Assessment'
        )}
      </Button>
    </form>
  );
}
