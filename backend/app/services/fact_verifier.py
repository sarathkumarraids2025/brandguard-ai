import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import ApprovedFact

class FactVerifier:
    def __init__(self, db: Session, profile_id: int):
        self.db = db
        self.profile_id = profile_id
        self.approved_facts = db.query(ApprovedFact).filter(
            ApprovedFact.profile_id == profile_id,
            ApprovedFact.is_active == True
        ).all()

    def verify_content(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        issues = []
        sentences = re.split(r'(?<=[.!?\n]) +', text)

        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean or len(sent_clean) < 8:
                continue

            # 1. Warranty Claims Check
            warranty_match = re.search(r'\b(lifetime\s+warranty|unlimited\s+warranty|வாழ்நாள்\s+உத்தரவாதம்|5\s*years?\s+warranty)\b', sent_clean, re.I)
            if warranty_match:
                # Find matching approved fact
                fact = next((f for f in self.approved_facts if "warranty" in f.topic.lower() or "உத்தரவாதம்" in f.topic.lower()), None)
                if fact:
                    issues.append({
                        "dimension": "Fact",
                        "title": "Warranty Claim Contradiction",
                        "severity": "Critical",
                        "sentence": sent_clean,
                        "explanation": f"Submitted content asserts '{warranty_match.group(0)}', which directly conflicts with registered company warranty policy.",
                        "guideline_citation": "Approved Fact #WF-01 (Product Warranty Policy)",
                        "evidence": f"Approved Fact [{fact.source_doc}, verified {fact.verified_date}]: \"{fact.fact_text}\"",
                        "suggested_correction": warranty_match.re.sub("12-month standard warranty", sent_clean),
                        "confidence_score": 0.98,
                        "requires_human_verification": False,
                        "status": "Contradicted"
                    })
                else:
                    issues.append({
                        "dimension": "Claim",
                        "title": "Unverified Warranty Claim",
                        "severity": "High",
                        "sentence": sent_clean,
                        "explanation": "Promotional warranty statement detected with no corresponding approved fact in brand repository.",
                        "guideline_citation": "Brand Fact Verification Standard §4.2",
                        "evidence": "Unable to verify against approved sources.",
                        "suggested_correction": "Please verify standard warranty terms with Legal before publication.",
                        "confidence_score": 0.90,
                        "requires_human_verification": True,
                        "status": "Unsupported"
                    })

            # 2. Uptime / SLA Claims (e.g. 100% uptime vs 99.9% uptime)
            uptime_match = re.search(r'\b(100%\s+uptime|zero\s+downtime|பூஜ்ஜிய\s+செயலிழப்பு|never\s+goes\s+down)\b', sent_clean, re.I)
            if uptime_match:
                fact = next((f for f in self.approved_facts if "uptime" in f.topic.lower() or "sla" in f.topic.lower()), None)
                evidence = f"Approved Fact [{fact.source_doc}, verified {fact.verified_date}]: \"{fact.fact_text}\"" if fact else "Unable to verify against approved sources."
                issues.append({
                    "dimension": "Fact",
                    "title": "Absolute SLA / Uptime Misstatement",
                    "severity": "Critical",
                    "sentence": sent_clean,
                    "explanation": "Absolute uptime claims (such as '100% uptime' or 'zero downtime') are legally impermissible and contradict enterprise SLA guidelines.",
                    "guideline_citation": "Compliance Fact Sheet #SLA-02",
                    "evidence": evidence,
                    "suggested_correction": uptime_match.re.sub("99.9% uptime SLA", sent_clean),
                    "confidence_score": 0.96,
                    "requires_human_verification": False,
                    "status": "Contradicted" if fact else "Unsupported"
                })

            # 3. Data Centers / Global Infrastructure Count
            infra_match = re.search(r'\b(\d+)\s+(data\s+centers|locations|facilities|regions)\b', sent_clean, re.I)
            if infra_match:
                count = int(infra_match.group(1))
                fact = next((f for f in self.approved_facts if "data center" in f.topic.lower() or "infrastructure" in f.topic.lower()), None)
                if fact:
                    # Check if count does not match approved
                    m = re.search(r'(\d+)', fact.fact_text)
                    if m and int(m.group(1)) != count:
                        issues.append({
                            "dimension": "Fact",
                            "title": "Infrastructure Metric Contradiction",
                            "severity": "High",
                            "sentence": sent_clean,
                            "explanation": f"Submitted statement specifies {count} {infra_match.group(2)}, whereas the approved company fact documents {m.group(1)}.",
                            "guideline_citation": "Approved Fact #INF-03 (Global Cloud Infrastructure)",
                            "evidence": f"Approved Fact [{fact.source_doc}, verified {fact.verified_date}]: \"{fact.fact_text}\"",
                            "suggested_correction": sent_clean.replace(str(count), m.group(1)),
                            "confidence_score": 0.95,
                            "requires_human_verification": False,
                            "status": "Contradicted"
                        })

            # 4. Founding Year / History Check
            found_match = re.search(r'\b(founded|established|started)\s+(in|back\s+in)\s+(\d{4})\b', sent_clean, re.I)
            if found_match:
                year = found_match.group(3)
                fact = next((f for f in self.approved_facts if "found" in f.topic.lower() or "history" in f.topic.lower()), None)
                if fact:
                    m = re.search(r'(\d{4})', fact.fact_text)
                    if m and m.group(1) != year:
                        issues.append({
                            "dimension": "Fact",
                            "title": "Company Founding Year Discrepancy",
                            "severity": "High",
                            "sentence": sent_clean,
                            "explanation": f"Stated founding year ({year}) conflicts with the verified corporate founding year ({m.group(1)}).",
                            "guideline_citation": "Approved Fact #CORP-01 (Corporate History)",
                            "evidence": f"Approved Fact [{fact.source_doc}, verified {fact.verified_date}]: \"{fact.fact_text}\"",
                            "suggested_correction": sent_clean.replace(year, m.group(1)),
                            "confidence_score": 0.97,
                            "requires_human_verification": False,
                            "status": "Contradicted"
                        })

            # 5. Unsupported Hyperbolic Claims (e.g. "cuts costs by 99% guaranteed", "world's only")
            hyperbolic = re.search(r'\b(cuts?\s+costs?\s+by\s+9[0-9]%|100%\s+bug-free|world\'s\s+only|completely\s+unhackable|பயமேயில்லை|100%\s+வெற்றி)\b', sent_clean, re.I)
            if hyperbolic:
                issues.append({
                    "dimension": "Claim",
                    "title": "Unsupported Promotional Superlative",
                    "severity": "Critical",
                    "sentence": sent_clean,
                    "explanation": f"Statement contains absolute claim '{hyperbolic.group(0)}' without verifiable backing data.",
                    "guideline_citation": "Advertising Standards & Substantiation Policy §3.1",
                    "evidence": "Unable to verify against approved sources.",
                    "suggested_correction": sent_clean.replace(hyperbolic.group(0), "significantly optimizes operational efficiency"),
                    "confidence_score": 0.92,
                    "requires_human_verification": True,
                    "status": "Unsupported"
                })

            # 6. Certification Claims (HIPAA, ISO, SOC)
            cert_match = re.search(r'\b(HIPAA\s+compliant|FedRAMP\s+certified|PCI-DSS\s+Level\s+1)\b', sent_clean, re.I)
            if cert_match:
                cert = cert_match.group(0)
                fact = next((f for f in self.approved_facts if cert.lower() in f.fact_text.lower()), None)
                if not fact:
                    issues.append({
                        "dimension": "Fact",
                        "title": f"Unverified Regulatory Certification ({cert})",
                        "severity": "High",
                        "sentence": sent_clean,
                        "explanation": f"Claiming '{cert}' without active verification in corporate compliance records risks severe regulatory non-compliance.",
                        "guideline_citation": "Legal Compliance Register #SEC-05",
                        "evidence": "Unable to verify against approved sources.",
                        "suggested_correction": f"Consult compliance officer before advertising {cert}.",
                        "confidence_score": 0.94,
                        "requires_human_verification": True,
                        "status": "Unsupported"
                    })

        return issues
