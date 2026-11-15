export type Role = 'ADMIN' | 'CREATOR' | 'REVIEWER';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  department: string;
  org_id: number;
  avatar_url?: string;
  organisation_name?: string;
}

export type Severity = 'Critical' | 'High' | 'Medium' | 'Low';
export type RiskLevel = 'Low' | 'Moderate' | 'High' | 'Critical';
export type SubmissionStatus = 'Draft' | 'Analysing' | 'Review Required' | 'Revision Requested' | 'Resubmitted' | 'Approved' | 'Rejected';

export interface DetectedIssue {
  id?: number;
  dimension: string;
  title: string;
  severity: Severity;
  sentence: string;
  explanation: string;
  guideline_citation?: string;
  evidence: string;
  suggested_correction?: string;
  confidence_score: number;
  requires_human_verification: boolean;
  visual_bbox?: [number, number, number, number];
}

export interface AnalysisResult {
  overall_score: number;
  voice_score: number;
  factual_score: number;
  visual_score: number;
  accessibility_score: number;
  terminology_score: number;
  risk_level: RiskLevel;
  score_breakdown?: Record<string, any>;
  issues: DetectedIssue[];
}
