import io
import csv
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, ContentSubmission, AnalysisResult, DetectedIssue

router = APIRouter(prefix="/analytics", tags=["Governance Analytics"])

@router.get("/overview")
def get_analytics_overview(
    department: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compute 100% database-derived brand governance analytics."""
    query = db.query(ContentSubmission).filter(ContentSubmission.org_id == current_user.org_id)
    if department:
        query = query.filter(ContentSubmission.department == department)
    if content_type:
        query = query.filter(ContentSubmission.content_type == content_type)
    if status_filter:
        query = query.filter(ContentSubmission.status == status_filter)

    submissions = query.all()
    sub_ids = [s.id for s in submissions]

    total_scanned = len(submissions)
    approved_count = sum(1 for s in submissions if s.status == "Approved")
    pending_count = sum(1 for s in submissions if s.status in ("Review Required", "Revision Requested", "Resubmitted", "Draft"))
    rejected_count = sum(1 for s in submissions if s.status == "Rejected")

    # Status distribution (Pie Chart)
    status_distribution = {}
    for s in submissions:
        status_distribution[s.status] = status_distribution.get(s.status, 0) + 1

    # Analysis results & scores
    analyses = db.query(AnalysisResult).filter(AnalysisResult.submission_id.in_(sub_ids)).all() if sub_ids else []
    analysis_ids = [a.id for a in analyses]

    avg_score = round(sum(a.overall_score for a in analyses) / max(len(analyses), 1), 1) if analyses else 100.0

    # Issues breakdown
    issues = db.query(DetectedIssue).filter(DetectedIssue.analysis_id.in_(analysis_ids)).all() if analysis_ids else []
    critical_issues_count = sum(1 for i in issues if i.severity == "Critical")

    # Severity distribution (Doughnut Chart)
    severity_distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for iss in issues:
        sev = iss.severity if iss.severity in severity_distribution else "Medium"
        severity_distribution[sev] += 1

    # Category violations (Bar Chart)
    category_violations = {}
    for iss in issues:
        dim = iss.dimension or "General"
        category_violations[dim] = category_violations.get(dim, 0) + 1

    # Top violations (Horizontal Bar Chart)
    top_viol_map = {}
    for iss in issues:
        title = iss.title
        top_viol_map[title] = top_viol_map.get(title, 0) + 1
    top_violations = sorted(
        [{"title": k, "count": v} for k, v in top_viol_map.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:8]

    # Department stats
    dept_map = {}
    for s in submissions:
        d = s.department or "Marketing"
        if d not in dept_map:
            dept_map[d] = {"department": d, "total": 0, "approved": 0, "issues": 0}
        dept_map[d]["total"] += 1
        if s.status == "Approved":
            dept_map[d]["approved"] += 1

    for a in analyses:
        sub = next((s for s in submissions if s.id == a.submission_id), None)
        if sub and sub.department in dept_map:
            dept_map[sub.department]["issues"] += len(a.issues)
    department_stats = list(dept_map.values())

    # Monthly / Timeline Compliance Trends (Line Chart)
    # Aggregate by month
    monthly_map = {}
    for s in submissions:
        m_key = s.created_at.strftime("%b %Y")
        analysis = next((a for a in analyses if a.submission_id == s.id), None)
        score = analysis.overall_score if analysis else 100.0
        if m_key not in monthly_map:
            monthly_map[m_key] = {"month": m_key, "scores": [], "count": 0}
        monthly_map[m_key]["scores"].append(score)
        monthly_map[m_key]["count"] += 1

    monthly_trends = []
    for k, v in monthly_map.items():
        monthly_trends.append({
            "month": v["month"],
            "avg_score": round(sum(v["scores"]) / len(v["scores"]), 1),
            "submissions": v["count"]
        })

    return {
        "total_scanned": total_scanned,
        "approved_count": approved_count,
        "pending_count": pending_count,
        "rejected_count": rejected_count,
        "critical_issues_count": critical_issues_count,
        "average_compliance_score": avg_score,
        "status_distribution": status_distribution,
        "severity_distribution": severity_distribution,
        "category_violations": category_violations,
        "top_violations": top_violations,
        "department_stats": department_stats,
        "monthly_trends": monthly_trends
    }

@router.get("/export-csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and download a comprehensive CSV governance report."""
    submissions = db.query(ContentSubmission).filter(
        ContentSubmission.org_id == current_user.org_id
    ).order_by(ContentSubmission.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Submission ID", "Title", "Content Type", "Creator", "Department",
        "Language", "Status", "Compliance Score", "Risk Level", "Issue Count", "Created At"
    ])

    for s in submissions:
        analysis = s.analysis_results[0] if s.analysis_results else None
        score = analysis.overall_score if analysis else "N/A"
        risk = analysis.risk_level if analysis else "N/A"
        issue_count = len(analysis.issues) if analysis else 0
        creator_name = s.creator.full_name if s.creator else "Unknown"
        writer.writerow([
            s.id, s.title, s.content_type, creator_name, s.department,
            s.language, s.status, score, risk, issue_count, s.created_at.isoformat()
        ])

    csv_data = output.getvalue()
    filename = f"BrandGuard_Governance_Report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
