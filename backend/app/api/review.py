from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user, require_role
from app.models.models import User, ContentSubmission, ReviewAction, Comment, Notification, AuditLog
from app.schemas.schemas import ReviewActionRequest, CommentCreate

router = APIRouter(prefix="/review", tags=["Review and Approval Workflow"])

# State machine mapping for actions
ACTION_STATE_MAP = {
    "APPROVE": "Approved",
    "REQUEST_REVISION": "Revision Requested",
    "REJECT": "Rejected",
    "RESUBMIT": "Resubmitted",
    "SUBMIT_FOR_REVIEW": "Review Required"
}

@router.post("/action/{submission_id}")
def perform_review_action(
    submission_id: int,
    req: ReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(ContentSubmission).filter(
        ContentSubmission.id == submission_id,
        ContentSubmission.org_id == current_user.org_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    action_key = req.action.upper()
    if action_key not in ACTION_STATE_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{req.action}'. Allowed: {', '.join(ACTION_STATE_MAP.keys())}"
        )

    # RBAC rules
    if action_key in ("APPROVE", "REJECT", "REQUEST_REVISION"):
        if current_user.role not in ("ADMIN", "REVIEWER"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Reviewers and Admins are permitted to approve, reject, or request revisions."
            )
    elif action_key == "RESUBMIT":
        if current_user.role not in ("ADMIN", "CREATOR"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Creators or Admins can resubmit content."
            )

    prev_status = sub.status
    new_status = ACTION_STATE_MAP[action_key]
    sub.status = new_status

    # Record Review Action
    action_record = ReviewAction(
        submission_id=sub.id,
        reviewer_id=current_user.id,
        action=action_key,
        previous_status=prev_status,
        new_status=new_status,
        notes=req.notes
    )
    db.add(action_record)

    # Notify Creator or Reviewers
    recipient_id = sub.creator_id if current_user.id != sub.creator_id else 1
    db.add(Notification(
        user_id=recipient_id,
        title=f"Submission {new_status}: {sub.title}",
        message=f"{current_user.full_name} marked this submission as '{new_status}'. Notes: {req.notes or 'No notes.'}",
        link=f"/review/{sub.id}"
    ))

    # Audit Log
    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action=f"WORKFLOW_{action_key}",
        target_type="ContentSubmission",
        target_id=str(sub.id),
        details={"previous": prev_status, "new": new_status, "notes": req.notes}
    ))

    db.commit()

    return {
        "status": "success",
        "action": action_key,
        "previous_status": prev_status,
        "new_status": new_status,
        "notes": req.notes
    }

@router.post("/comment/{submission_id}")
def add_comment(
    submission_id: int,
    req: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sub = db.query(ContentSubmission).filter(
        ContentSubmission.id == submission_id,
        ContentSubmission.org_id == current_user.org_id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    comment = Comment(
        submission_id=sub.id,
        user_id=current_user.id,
        content=req.content.strip()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "user_name": current_user.full_name,
        "user_role": current_user.role,
        "content": comment.content,
        "created_at": comment.created_at.isoformat()
    }
