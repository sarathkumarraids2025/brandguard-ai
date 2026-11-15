from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, BrandProfile
from app.services.clarity_analyzer import GuidelineClarityAnalyzer

router = APIRouter(prefix="/clarity", tags=["Brand Guideline Clarity Analyzer"])

@router.get("/analyze")
def analyze_guideline_clarity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Scan brand guidelines for contradictions, ambiguities, and missing specifications."""
    profile = db.query(BrandProfile).filter(BrandProfile.org_id == current_user.org_id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Brand profile not found")

    analyzer = GuidelineClarityAnalyzer(db, profile.id)
    conflicts = analyzer.analyze_guidelines()

    return {
        "status": "success",
        "total_conflicts": len(conflicts),
        "conflicts": conflicts
    }
