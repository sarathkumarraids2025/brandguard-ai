import os
import shutil
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_user
from app.models.models import User, BrandProfile, AuditLog
from app.services.visual_engine import VisualGuardianEngine

router = APIRouter(prefix="/visual", tags=["Visual Brand Guardian"])

@router.post("/audit-image")
async def audit_image_file(
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Audit creative poster or banner image against visual brand guidelines."""
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Brand profile not found")

    filename = file.filename
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    if ext not in ("png", "jpg", "jpeg", "webp", "bmp"):
        raise HTTPException(status_code=400, detail=f"Invalid image format '{ext}'. Supported: PNG, JPG, WEBP")

    unique_name = f"creative_{uuid.uuid4().hex[:12]}_{filename}"
    file_path = os.path.join(settings.UPLOAD_PATH, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        engine = VisualGuardianEngine(db, profile.id)
        report = engine.audit_image(file_path, alt_text=alt_text)

        # Log audit action
        db.add(AuditLog(
            org_id=current_user.org_id,
            user_id=current_user.id,
            user_name=current_user.full_name,
            action="VISUAL_AUDIT",
            target_type="BrandAsset",
            target_id=filename,
            details={"score": report["visual_compliance_score"], "issues": len(report["issues"])}
        ))
        db.commit()

        # Provide accessible web URL for the image
        image_url = f"/uploads/{unique_name}"
        return {
            "image_url": image_url,
            "filename": filename,
            **report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual audit processing error: {str(e)}")
