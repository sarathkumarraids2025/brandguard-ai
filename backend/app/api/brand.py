import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_user, require_role
from app.models.models import User, BrandProfile, BrandGuideline, ApprovedFact, TerminologyRule, BrandAsset, AuditLog
from app.schemas.schemas import (
    BrandProfileCreate, BrandGuidelineCreate, ApprovedFactCreate,
    TerminologyRuleCreate, BrandAssetCreate
)
from app.services.document_extractor import extract_from_file

router = APIRouter(prefix="/brand", tags=["Brand Intelligence Brain"])

@router.get("/profile")
def get_brand_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return profile

@router.put("/profile")
def update_brand_profile(
    data: BrandProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        profile = BrandProfile(org_id=current_user.org_id, **data.dict())
        db.add(profile)
    else:
        for k, v in data.dict(exclude_unset=True).items():
            setattr(profile, k, v)
    
    # Audit Log
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="UPDATE_BRAND_PROFILE",
        target_type="BrandProfile",
        target_id=str(profile.id),
        details={"brand_name": profile.brand_name}
    ))
    db.commit()
    db.refresh(profile)
    return profile

# ----------------- Guidelines -----------------
@router.get("/guidelines")
def get_guidelines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        return []
    return db.query(BrandGuideline).filter(BrandGuideline.profile_id == profile.id).all()

@router.post("/guidelines")
def create_guideline(
    data: BrandGuidelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Brand profile must be configured first")
        
    guideline = BrandGuideline(profile_id=profile.id, **data.dict())
    db.add(guideline)
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="CREATE_GUIDELINE",
        target_type="BrandGuideline",
        target_id=data.title,
        details={"category": data.category}
    ))
    db.commit()
    db.refresh(guideline)
    return guideline

@router.delete("/guidelines/{guideline_id}")
def delete_guideline(
    guideline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    guideline = db.query(BrandGuideline).filter(BrandGuideline.id == guideline_id).first()
    if not guideline:
        raise HTTPException(status_code=404, detail="Guideline not found")
    db.delete(guideline)
    db.commit()
    return {"status": "success", "message": "Guideline removed"}

# ----------------- Approved Facts -----------------
@router.get("/facts")
def get_approved_facts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        return []
    return db.query(ApprovedFact).filter(ApprovedFact.profile_id == profile.id).all()

@router.post("/facts")
def create_approved_fact(
    data: ApprovedFactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Brand profile must be configured first")
        
    fact = ApprovedFact(profile_id=profile.id, **data.dict())
    db.add(fact)
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="ADD_APPROVED_FACT",
        target_type="ApprovedFact",
        target_id=data.topic,
        details={"source": data.source_doc}
    ))
    db.commit()
    db.refresh(fact)
    return fact

@router.delete("/facts/{fact_id}")
def delete_approved_fact(
    fact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    fact = db.query(ApprovedFact).filter(ApprovedFact.id == fact_id).first()
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    db.delete(fact)
    db.commit()
    return {"status": "success", "message": "Fact deleted"}

# ----------------- Terminology -----------------
@router.get("/terminology")
def get_terminology(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        return []
    return db.query(TerminologyRule).filter(TerminologyRule.profile_id == profile.id).all()

@router.post("/terminology")
def create_terminology(
    data: TerminologyRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Brand profile must be configured first")
        
    term = TerminologyRule(profile_id=profile.id, **data.dict())
    db.add(term)
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="ADD_TERMINOLOGY",
        target_type="TerminologyRule",
        target_id=f"{data.prohibited_term} -> {data.preferred_term}",
        details={"language": data.language}
    ))
    db.commit()
    db.refresh(term)
    return term

@router.delete("/terminology/{term_id}")
def delete_terminology(
    term_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    term = db.query(TerminologyRule).filter(TerminologyRule.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Terminology rule not found")
    db.delete(term)
    db.commit()
    return {"status": "success", "message": "Terminology rule deleted"}

# ----------------- Brand Assets -----------------
@router.get("/assets")
def get_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        return []
    return db.query(BrandAsset).filter(BrandAsset.profile_id == profile.id).all()

@router.post("/assets")
def create_asset(
    data: BrandAssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Brand profile must be configured first")
        
    asset = BrandAsset(profile_id=profile.id, **data.dict())
    db.add(asset)
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="ADD_BRAND_ASSET",
        target_type="BrandAsset",
        target_id=data.name,
        details={"asset_type": data.asset_type}
    ))
    db.commit()
    db.refresh(asset)
    return asset

# ----------------- Document Import -----------------
@router.post("/import-document")
async def import_brand_document(
    file: UploadFile = File(...),
    import_type: str = Form("facts"),  # facts or guidelines
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """Extract and import structured knowledge from uploaded brand documents (PDF/DOCX/TXT/CSV)."""
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Brand profile not found")
        
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")
        
    temp_path = os.path.join(settings.UPLOAD_PATH, f"import_{filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        extracted_text = extract_from_file(temp_path)
        lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
        
        imported_count = 0
        if import_type == "facts":
            for line in lines[:20]:
                if len(line) > 15 and ":" in line:
                    topic, fact_text = line.split(":", 1)
                    db.add(ApprovedFact(
                        profile_id=profile.id,
                        topic=topic.strip()[:100],
                        fact_text=fact_text.strip(),
                        category="Imported",
                        source_doc=filename,
                        verified_date="2026-11-14",
                        is_active=True
                    ))
                    imported_count += 1
        else:
            for line in lines[:15]:
                if len(line) > 20:
                    db.add(BrandGuideline(
                        profile_id=profile.id,
                        category="Writing",
                        title=f"Imported Guideline ({filename})",
                        rule_text=line.strip(),
                        severity="Medium",
                        rationale="Extracted from brand policy document",
                        is_active=True
                    ))
                    imported_count += 1
                    
        db.commit()
        return {
            "status": "success",
            "message": f"Successfully extracted and imported {imported_count} {import_type} from {filename}",
            "imported_count": imported_count
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
