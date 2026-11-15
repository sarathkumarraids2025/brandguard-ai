from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import DetectedIssue, ContentSubmission, AnalysisResult

class BrandMemoryEngine:
    def __init__(self, db: Session, org_id: int):
        self.db = db
        self.org_id = org_id

    def detect_recurring_errors(self) -> List[Dict[str, Any]]:
        """Identify systemic, recurrent brand violations across historical submissions."""
        # Query issues across submissions belonging to this org
        results = (
            self.db.query(
                DetectedIssue.title,
                DetectedIssue.dimension,
                ContentSubmission.department,
                func.count(DetectedIssue.id).label("issue_count")
            )
            .join(AnalysisResult, DetectedIssue.analysis_id == AnalysisResult.id)
            .join(ContentSubmission, AnalysisResult.submission_id == ContentSubmission.id)
            .filter(ContentSubmission.org_id == self.org_id)
            .group_by(DetectedIssue.title, DetectedIssue.dimension, ContentSubmission.department)
            .order_by(func.count(DetectedIssue.id).desc())
            .all()
        )

        # Aggregate across departments
        title_map = {}
        for row in results:
            title, dimension, dept, count = row[0], row[1], row[2], row[3]
            if title not in title_map:
                title_map[title] = {
                    "violation_title": title,
                    "dimension": dimension,
                    "total_count": 0,
                    "departments": set(),
                }
            title_map[title]["total_count"] += count
            if dept:
                title_map[title]["departments"].add(dept)

        recurring = []
        for title, data in title_map.items():
            depts = list(data["departments"])
            count = data["total_count"]
            dim = data["dimension"]
            
            # Actionable recommendations based on dimension and frequency
            if "Warranty" in title:
                action = f"Host a mandatory 15-minute warranty alignment session for {', '.join(depts)}. Ensure copywriters know lifetime warranty claims are strictly prohibited."
            elif "Contrast" in title:
                action = f"Provide {', '.join(depts)} creative teams with WCAG 2.1 AA contrast templates and Figma contrast checker tokens."
            elif "Terminology" in title or dim == "Terminology":
                action = f"Distribute updated approved terminology cheat-sheet to {', '.join(depts)} team leads."
            elif "SLA" in title or "Uptime" in title:
                action = f"Clarify to {', '.join(depts)} that our contractual SLA is 99.9%, never '100% uptime' or 'zero downtime'."
            else:
                action = f"Review guideline clarification for '{title}' across {', '.join(depts)}."

            recurring.append({
                "violation_title": title,
                "dimension": dim,
                "frequency": count,
                "affected_departments": depts or ["Marketing"],
                "suggested_action": action
            })

        # Sort by highest frequency
        recurring.sort(key=lambda x: x["frequency"], reverse=True)
        return recurring[:10]
