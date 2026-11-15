from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User
from app.services.memory_engine import BrandMemoryEngine

router = APIRouter(prefix="/memory", tags=["Brand Memory & Recurring Errors"])

@router.get("/recurring")
def get_recurring_errors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Surface systemic recurrent brand mistakes across historical submissions."""
    engine = BrandMemoryEngine(db, current_user.org_id)
    recurring_issues = engine.detect_recurring_errors()

    return {
        "status": "success",
        "total_recurring_patterns": len(recurring_issues),
        "recurring_errors": recurring_issues
    }
