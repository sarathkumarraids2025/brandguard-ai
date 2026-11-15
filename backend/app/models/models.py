import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    industry = Column(String(100), default="Technology")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="organisation", cascade="all, delete-orphan")
    brand_profiles = relationship("BrandProfile", back_populates="organisation", cascade="all, delete-orphan")
    submissions = relationship("ContentSubmission", back_populates="organisation", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organisation", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="CREATOR")  # ADMIN, CREATOR, REVIEWER
    department = Column(String(100), default="Marketing")
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="users")
    submissions = relationship("ContentSubmission", back_populates="creator")
    comments = relationship("Comment", back_populates="user")
    review_actions = relationship("ReviewAction", back_populates="reviewer")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    brand_name = Column(String(255), nullable=False)
    tagline = Column(String(255), default="Every Message Matters. Every Brand Deserves Consistency.")
    mission = Column(Text, nullable=True)
    values = Column(Text, nullable=True)
    tone_voice = Column(Text, nullable=True)
    writing_style = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="brand_profiles")
    guidelines = relationship("BrandGuideline", back_populates="profile", cascade="all, delete-orphan")
    approved_facts = relationship("ApprovedFact", back_populates="profile", cascade="all, delete-orphan")
    terminology_rules = relationship("TerminologyRule", back_populates="profile", cascade="all, delete-orphan")
    assets = relationship("BrandAsset", back_populates="profile", cascade="all, delete-orphan")
    submissions = relationship("ContentSubmission", back_populates="brand_profile")

class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    category = Column(String(100), nullable=False)  # Voice, Tone, Writing, Compliance, Visual, Accessibility
    title = Column(String(255), nullable=False)
    rule_text = Column(Text, nullable=False)
    severity = Column(String(50), default="Medium")  # Critical, High, Medium, Low
    rationale = Column(Text, nullable=True)
    example_good = Column(Text, nullable=True)
    example_bad = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    profile = relationship("BrandProfile", back_populates="guidelines")
    detected_issues = relationship("DetectedIssue", back_populates="guideline")

class ApprovedFact(Base):
    __tablename__ = "approved_facts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    topic = Column(String(150), nullable=False)
    fact_text = Column(Text, nullable=False)
    category = Column(String(100), default="Product")  # Product, Company, Security, Pricing, Warranty
    source_doc = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=True)
    verified_date = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("BrandProfile", back_populates="approved_facts")

class TerminologyRule(Base):
    __tablename__ = "terminology_rules"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    preferred_term = Column(String(200), nullable=False)
    prohibited_term = Column(String(200), nullable=False)
    context = Column(Text, nullable=True)
    rationale = Column(Text, nullable=True)
    is_strict = Column(Boolean, default=True)
    language = Column(String(20), default="en")  # en, ta
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("BrandProfile", back_populates="terminology_rules")

class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    asset_type = Column(String(50), nullable=False)  # LOGO, COLOR_PALETTE, TYPOGRAPHY
    name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=True)
    color_hex = Column(String(50), nullable=True)  # E.g. "#2563EB"
    meta_info = Column(JSON, nullable=True)  # RGB, min_contrast, usage_rules
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profile = relationship("BrandProfile", back_populates="assets")

class ContentSubmission(Base):
    __tablename__ = "content_submissions"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)  # email, ad, social, website, blog, press_release, product_description, poster
    raw_text = Column(Text, nullable=True)
    corrected_text = Column(Text, nullable=True)
    source_file = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)
    language = Column(String(20), default="en")  # en, ta
    department = Column(String(100), default="Marketing")
    status = Column(String(50), default="Draft")  # Draft, Analysing, Review Required, Revision Requested, Resubmitted, Approved, Rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="submissions")
    brand_profile = relationship("BrandProfile", back_populates="submissions")
    creator = relationship("User", back_populates="submissions")
    analysis_results = relationship("AnalysisResult", back_populates="submission", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="submission", cascade="all, delete-orphan")
    review_actions = relationship("ReviewAction", back_populates="submission", cascade="all, delete-orphan")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("content_submissions.id"), nullable=False)
    overall_score = Column(Float, default=100.0)
    voice_score = Column(Float, default=100.0)
    factual_score = Column(Float, default=100.0)
    visual_score = Column(Float, default=100.0)
    accessibility_score = Column(Float, default=100.0)
    terminology_score = Column(Float, default=100.0)
    risk_level = Column(String(50), default="Low")  # Low, Moderate, High, Critical
    score_breakdown = Column(JSON, nullable=True)
    scanned_at = Column(DateTime, default=datetime.datetime.utcnow)

    submission = relationship("ContentSubmission", back_populates="analysis_results")
    issues = relationship("DetectedIssue", back_populates="analysis", cascade="all, delete-orphan")

class DetectedIssue(Base):
    __tablename__ = "detected_issues"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"), nullable=False)
    guideline_id = Column(Integer, ForeignKey("brand_guidelines.id"), nullable=True)
    dimension = Column(String(100), nullable=False)  # Voice, Terminology, Fact, Claim, Visual, Accessibility, Readability
    title = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False)  # Critical, High, Medium, Low
    sentence = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    guideline_citation = Column(Text, nullable=True)
    evidence = Column(Text, nullable=False)  # Verified fact quote or "Unable to verify against approved sources"
    suggested_correction = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.95)
    requires_human_verification = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    visual_bbox = Column(JSON, nullable=True)  # [ymin, xmin, ymax, xmax] or visual tag
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("AnalysisResult", back_populates="issues")
    guideline = relationship("BrandGuideline", back_populates="detected_issues")
    rewrites = relationship("RewriteSuggestion", back_populates="issue", cascade="all, delete-orphan")

class RewriteSuggestion(Base):
    __tablename__ = "rewrite_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("detected_issues.id"), nullable=False)
    option_type = Column(String(50), nullable=False)  # Professional, Friendly, Marketing
    rewritten_text = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    is_accepted = Column(Boolean, default=False)

    issue = relationship("DetectedIssue", back_populates="rewrites")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("content_submissions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submission = relationship("ContentSubmission", back_populates="comments")
    user = relationship("User", back_populates="comments")

class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("content_submissions.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # APPROVE, REQUEST_REVISION, REJECT, COMMENT, RESUBMIT
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submission = relationship("ContentSubmission", back_populates="review_actions")
    reviewer = relationship("User", back_populates="review_actions")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    user_name = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=False)
    target_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organisation = relationship("Organisation", back_populates="audit_logs")
