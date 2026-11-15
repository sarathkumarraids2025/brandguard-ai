from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ----------------- Auth Schemas -----------------
class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str

class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str
    full_name: str
    role: str = "CREATOR"  # ADMIN, CREATOR, REVIEWER
    department: str = "Marketing"
    org_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    department: str
    org_id: int
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Brand Brain Schemas -----------------
class BrandProfileCreate(BaseModel):
    brand_name: str
    tagline: Optional[str] = None
    mission: Optional[str] = None
    values: Optional[str] = None
    tone_voice: Optional[str] = None
    writing_style: Optional[str] = None
    target_audience: Optional[str] = None

class BrandGuidelineCreate(BaseModel):
    category: str  # Voice, Tone, Writing, Compliance, Visual, Accessibility
    title: str
    rule_text: str
    severity: str = "Medium"  # Critical, High, Medium, Low
    rationale: Optional[str] = None
    example_good: Optional[str] = None
    example_bad: Optional[str] = None

class ApprovedFactCreate(BaseModel):
    topic: str
    fact_text: str
    category: str = "Product"
    source_doc: str
    source_url: Optional[str] = None
    verified_date: str

class TerminologyRuleCreate(BaseModel):
    preferred_term: str
    prohibited_term: str
    context: Optional[str] = None
    rationale: Optional[str] = None
    is_strict: bool = True
    language: str = "en"

class BrandAssetCreate(BaseModel):
    asset_type: str  # LOGO, COLOR_PALETTE, TYPOGRAPHY
    name: str
    file_path: Optional[str] = None
    color_hex: Optional[str] = None
    meta_info: Optional[Dict[str, Any]] = None

# ----------------- Content Scanner Schemas -----------------
class ContentScanRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content_type: str  # email, ad, social, website, blog, press_release, product_description, poster
    raw_text: Optional[str] = None
    source_url: Optional[str] = None
    language: str = "en"
    department: str = "Marketing"
    profile_id: Optional[int] = None

class DetectedIssueOut(BaseModel):
    id: Optional[int] = None
    dimension: str
    title: str
    severity: str
    sentence: str
    explanation: str
    guideline_citation: Optional[str] = None
    evidence: str
    suggested_correction: Optional[str] = None
    confidence_score: float
    requires_human_verification: bool
    is_resolved: bool = False
    visual_bbox: Optional[Any] = None

class AnalysisResultOut(BaseModel):
    id: Optional[int] = None
    submission_id: Optional[int] = None
    overall_score: float
    voice_score: float
    factual_score: float
    visual_score: float
    accessibility_score: float
    terminology_score: float
    risk_level: str
    score_breakdown: Optional[Dict[str, Any]] = None
    issues: List[DetectedIssueOut] = []
    scanned_at: Optional[datetime] = None

# ----------------- Rewrite Studio Schemas -----------------
class RewriteOption(BaseModel):
    option_type: str  # Professional, Friendly, Marketing
    rewritten_text: str
    rationale: str

class RewriteRequest(BaseModel):
    sentence: str
    context: Optional[str] = None
    dimension: Optional[str] = "Tone"
    guideline: Optional[str] = None

class RewriteResponse(BaseModel):
    original_sentence: str
    options: List[RewriteOption]

class ApplyCorrectionRequest(BaseModel):
    submission_id: int
    corrected_text: str

# ----------------- Workflow & Review Schemas -----------------
class ReviewActionRequest(BaseModel):
    action: str  # APPROVE, REQUEST_REVISION, REJECT, RESUBMIT
    notes: Optional[str] = None

class CommentCreate(BaseModel):
    content: str

# ----------------- Analytics Schemas -----------------
class AnalyticsOverview(BaseModel):
    total_scanned: int
    approved_count: int
    pending_count: int
    rejected_count: int
    critical_issues_count: int
    average_compliance_score: float
    status_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    category_violations: Dict[str, int]
    top_violations: List[Dict[str, Any]]
    department_stats: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]

# ----------------- Guideline Clarity & Memory Schemas -----------------
class ClarityConflict(BaseModel):
    type: str  # Contradiction, Ambiguity, Missing Term, Missing Fact, Missing Example
    guideline_a: str
    guideline_b: Optional[str] = None
    explanation: str
    recommendation: str
    severity: str

class RecurringError(BaseModel):
    violation_title: str
    category: str
    frequency: int
    affected_departments: List[str]
    suggested_action: str
