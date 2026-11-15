import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_user
from app.models.models import (
    User, BrandProfile, ContentSubmission, AnalysisResult,
    DetectedIssue, RewriteSuggestion, AuditLog
)
from app.schemas.schemas import ContentScanRequest, AnalysisResultOut, DetectedIssueOut
from app.services.nlp_engine import NLPEngine
from app.services.rewrite_engine import RewriteStudioEngine
from app.services.document_extractor import extract_from_file, extract_from_url

router = APIRouter(prefix="/scanner", tags=["Content Intelligence Scanner"])

@router.post("/scan")
def scan_content(
    payload: ContentScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No active Brand Profile found for organisation.")

    content_to_scan = payload.raw_text or ""
    source_url = payload.source_url

    # Handle URL input if provided
    if source_url:
        try:
            url_title, extracted = extract_from_url(source_url)
            if not content_to_scan:
                content_to_scan = extracted
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch content from URL: {str(e)}")

    if not content_to_scan.strip():
        raise HTTPException(status_code=400, detail="Content body or text cannot be empty.")

    # 1. Run Multidimensional Brand Audit
    nlp_engine = NLPEngine(db, profile.id)
    audit = nlp_engine.audit_content(
        text=content_to_scan,
        content_type=payload.content_type,
        language=payload.language
    )

    # Determine submission status: If critical/high issues exist, 'Review Required', else 'Draft' or 'Review Required'
    has_critical = any(i["severity"] in ("Critical", "High") for i in audit["issues"])
    initial_status = "Review Required" if has_critical else ("Review Required" if audit["issues"] else "Approved")

    # 2. Persist ContentSubmission
    submission = ContentSubmission(
        org_id=current_user.org_id,
        profile_id=profile.id,
        creator_id=current_user.id,
        title=payload.title,
        content_type=payload.content_type,
        raw_text=content_to_scan,
        corrected_text=content_to_scan,
        source_url=source_url,
        language=payload.language,
        department=payload.department or current_user.department,
        status=initial_status
    )
    db.add(submission)
    db.flush()

    # 3. Persist AnalysisResult
    result = AnalysisResult(
        submission_id=submission.id,
        overall_score=audit["overall_score"],
        voice_score=audit["voice_score"],
        factual_score=audit["factual_score"],
        visual_score=audit["visual_score"],
        accessibility_score=audit["accessibility_score"],
        terminology_score=audit["terminology_score"],
        risk_level=audit["risk_level"],
        score_breakdown=audit["score_breakdown"]
    )
    db.add(result)
    db.flush()

    # 4. Persist DetectedIssues & generate RewriteSuggestions
    rewrite_engine = RewriteStudioEngine()
    saved_issues = []

    for item in audit["issues"]:
        issue = DetectedIssue(
            analysis_id=result.id,
            dimension=item["dimension"],
            title=item["title"],
            severity=item["severity"],
            sentence=item["sentence"],
            explanation=item["explanation"],
            guideline_citation=item.get("guideline_citation"),
            evidence=item["evidence"],
            suggested_correction=item.get("suggested_correction"),
            confidence_score=item.get("confidence_score", 0.95),
            requires_human_verification=item.get("requires_human_verification", False)
        )
        db.add(issue)
        db.flush()

        # Generate 3 rewrite options
        options = rewrite_engine.generate_rewrites(
            sentence=item["sentence"],
            dimension=item["dimension"],
            guideline=item.get("guideline_citation", "")
        )
        for opt in options:
            db.add(RewriteSuggestion(
                issue_id=issue.id,
                option_type=opt["option_type"],
                rewritten_text=opt["rewritten_text"],
                rationale=opt["rationale"]
            ))

        saved_issues.append({
            "id": issue.id,
            **item,
            "rewrites": options
        })

    # Log action
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="SCAN_CONTENT",
        target_type="ContentSubmission",
        target_id=str(submission.id),
        details={"score": audit["overall_score"], "issues_found": len(audit["issues"])}
    ))

    db.commit()

    return {
        "submission_id": submission.id,
        "title": submission.title,
        "status": submission.status,
        "language": submission.language,
        "analysis": {
            "overall_score": audit["overall_score"],
            "voice_score": audit["voice_score"],
            "factual_score": audit["factual_score"],
            "visual_score": audit["visual_score"],
            "accessibility_score": audit["accessibility_score"],
            "terminology_score": audit["terminology_score"],
            "risk_level": audit["risk_level"],
            "score_breakdown": audit["score_breakdown"],
            "issues": saved_issues
        }
    }

@router.post("/upload")
async def upload_and_scan(
    file: UploadFile = File(...),
    title: str = Form(...),
    content_type: str = Form("general"),
    language: str = Form("en"),
    department: str = Form("Marketing"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload document (PDF, DOCX, TXT, CSV) and execute brand scan."""
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File extension '{ext}' not allowed.")

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(settings.UPLOAD_PATH, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_from_file(file_path)
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract readable text from document.")

        req = ContentScanRequest(
            title=title or filename,
            content_type=content_type,
            raw_text=extracted_text,
            language=language,
            department=department
        )
        result = scan_content(req, db, current_user)
        # Update submission with source file
        sub = db.query(ContentSubmission).filter(ContentSubmission.id == result["submission_id"]).first()
        if sub:
            sub.source_file = filename
            db.commit()

        return result
    finally:
        # Keep uploaded files in upload dir for records or remove if temporary
        pass

@router.get("/submissions")
def list_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List submissions for current organisation."""
    subs = db.query(ContentSubmission).filter(
        ContentSubmission.org_id == current_user.org_id
    ).order_by(ContentSubmission.created_at.desc()).all()

    output = []
    for s in subs:
        analysis = s.analysis_results[0] if s.analysis_results else None
        issue_count = len(analysis.issues) if analysis else 0
        output.append({
            "id": s.id,
            "title": s.title,
            "content_type": s.content_type,
            "creator_name": s.creator.full_name if s.creator else "Unknown",
            "department": s.department,
            "status": s.status,
            "language": s.language,
            "created_at": s.created_at.isoformat(),
            "overall_score": analysis.overall_score if analysis else None,
            "risk_level": analysis.risk_level if analysis else None,
            "issue_count": issue_count
        })
    return output

@router.get("/submissions/{submission_id}")
def get_submission_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(ContentSubmission).filter(
        ContentSubmission.id == submission_id,
        ContentSubmission.org_id == current_user.org_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    analysis = sub.analysis_results[0] if sub.analysis_results else None
    issues_out = []
    if analysis:
        for iss in analysis.issues:
            rewrites = [
                {"option_type": r.option_type, "rewritten_text": r.rewritten_text, "rationale": r.rationale}
                for r in iss.rewrites
            ]
            issues_out.append({
                "id": iss.id,
                "dimension": iss.dimension,
                "title": iss.title,
                "severity": iss.severity,
                "sentence": iss.sentence,
                "explanation": iss.explanation,
                "guideline_citation": iss.guideline_citation,
                "evidence": iss.evidence,
                "suggested_correction": iss.suggested_correction,
                "confidence_score": iss.confidence_score,
                "requires_human_verification": iss.requires_human_verification,
                "is_resolved": iss.is_resolved,
                "visual_bbox": iss.visual_bbox,
                "rewrites": rewrites
            })

    comments = [
        {
            "id": c.id,
            "user_name": c.user.full_name if c.user else "User",
            "user_role": c.user.role if c.user else "MEMBER",
            "content": c.content,
            "created_at": c.created_at.isoformat()
        }
        for c in sub.comments
    ]

    history = [
        {
            "id": a.id,
            "reviewer_name": a.reviewer.full_name if a.reviewer else "System",
            "action": a.action,
            "previous_status": a.previous_status,
            "new_status": a.new_status,
            "notes": a.notes,
            "created_at": a.created_at.isoformat()
        }
        for a in sub.review_actions
    ]

    return {
        "id": sub.id,
        "title": sub.title,
        "content_type": sub.content_type,
        "raw_text": sub.raw_text,
        "corrected_text": sub.corrected_text or sub.raw_text,
        "source_file": sub.source_file,
        "source_url": sub.source_url,
        "language": sub.language,
        "department": sub.department,
        "status": sub.status,
        "creator_name": sub.creator.full_name if sub.creator else "Creator",
        "created_at": sub.created_at.isoformat(),
        "analysis": {
            "overall_score": analysis.overall_score if analysis else 100.0,
            "voice_score": analysis.voice_score if analysis else 100.0,
            "factual_score": analysis.factual_score if analysis else 100.0,
            "visual_score": analysis.visual_score if analysis else 100.0,
            "accessibility_score": analysis.accessibility_score if analysis else 100.0,
            "terminology_score": analysis.terminology_score if analysis else 100.0,
            "risk_level": analysis.risk_level if analysis else "Low",
            "score_breakdown": analysis.score_breakdown if analysis else {},
            "issues": issues_out
        },
        "comments": comments,
        "history": history
    }
