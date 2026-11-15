from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, ContentSubmission, DetectedIssue, AuditLog
from app.schemas.schemas import RewriteRequest, RewriteResponse, ApplyCorrectionRequest
from app.services.rewrite_engine import RewriteStudioEngine
from app.services.nlp_engine import NLPEngine

router = APIRouter(prefix="/rewrite", tags=["AI Smart Rewrite Studio"])

@router.post("/generate", response_model=RewriteResponse)
def generate_rewrites(
    req: RewriteRequest,
    current_user: User = Depends(get_current_user)
):
    engine = RewriteStudioEngine()
    options = engine.generate_rewrites(
        sentence=req.sentence,
        dimension=req.dimension or "Tone",
        guideline=req.guideline or ""
    )
    return {
        "original_sentence": req.sentence,
        "options": options
    }

@router.post("/apply")
def apply_correction(
    req: ApplyCorrectionRequest,
    issue_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(ContentSubmission).filter(
        ContentSubmission.id == req.submission_id,
        ContentSubmission.org_id == current_user.org_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    sub.corrected_text = req.corrected_text

    # Mark issue resolved if provided
    if issue_id:
        issue = db.query(DetectedIssue).filter(DetectedIssue.id == issue_id).first()
        if issue:
            issue.is_resolved = True

    # Audit log
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="APPLY_REWRITE_CORRECTION",
        target_type="ContentSubmission",
        target_id=str(sub.id),
        details={"text_length": len(req.corrected_text)}
    ))

    db.commit()

    return {
        "status": "success",
        "message": "Content updated successfully with revised text.",
        "corrected_text": sub.corrected_text
    }
