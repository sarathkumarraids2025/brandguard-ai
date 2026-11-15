import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import BrandGuideline, ApprovedFact, TerminologyRule

class GuidelineClarityAnalyzer:
    def __init__(self, db: Session, profile_id: int):
        self.db = db
        self.profile_id = profile_id
        self.guidelines = db.query(BrandGuideline).filter(
            BrandGuideline.profile_id == profile_id,
            BrandGuideline.is_active == True
        ).all()
        self.facts = db.query(ApprovedFact).filter(
            ApprovedFact.profile_id == profile_id,
            ApprovedFact.is_active == True
        ).all()
        self.terms = db.query(TerminologyRule).filter(
            TerminologyRule.profile_id == profile_id
        ).all()

    def analyze_guidelines(self) -> List[Dict[str, Any]]:
        """Identify contradictions, ambiguities, and missing specifications in brand guidelines."""
        findings = []

        # 1. Contradiction Detection across rules
        for i, g1 in enumerate(self.guidelines):
            for j, g2 in enumerate(self.guidelines):
                if i >= j:
                    continue

                text1 = (g1.title + " " + g1.rule_text).lower()
                text2 = (g2.title + " " + g2.rule_text).lower()

                # Tone contradiction: Formal/Professional vs Casual/Humorous
                is_g1_formal = bool(re.search(r'\b(professional|formal|authoritative|serious)\b', text1))
                is_g2_casual = bool(re.search(r'\b(casual|humorous|informal|playful|funny)\b', text2))
                
                is_g2_formal = bool(re.search(r'\b(professional|formal|authoritative|serious)\b', text2))
                is_g1_casual = bool(re.search(r'\b(casual|humorous|informal|playful|funny)\b', text1))

                if (is_g1_formal and is_g2_casual) or (is_g2_formal and is_g1_casual):
                    findings.append({
                        "type": "Contradiction",
                        "severity": "High",
                        "guideline_a": f"[{g1.category}] {g1.title}",
                        "guideline_b": f"[{g2.category}] {g2.title}",
                        "explanation": f"Rule '{g1.title}' mandates formal/authoritative tone, while rule '{g2.title}' encourages casual or humorous expression without explicit channel scoping.",
                        "recommendation": "Clarify channel-specific exceptions: specify that casual tone is restricted strictly to social media replies, while corporate web and PR maintain formal tone."
                    })

                # Strict active voice vs passive permission
                if ("strictly active voice" in text1 and "passive voice" in text2 and "acceptable" in text2) or \
                   ("strictly active voice" in text2 and "passive voice" in text1 and "acceptable" in text1):
                    findings.append({
                        "type": "Contradiction",
                        "severity": "Medium",
                        "guideline_a": f"[{g1.category}] {g1.title}",
                        "guideline_b": f"[{g2.category}] {g2.title}",
                        "explanation": "Conflicting guidance regarding active vs passive voice usage across writing rules.",
                        "recommendation": "Unify voice guidelines: adopt active voice as default and designate technical documentation as the only exception for passive voice."
                    })

        # 2. Ambiguity Detection (vague instructions)
        vague_phrases = ["use your judgment", "as appropriate", "reasonable effort", "generally good", "whenever possible", "good taste"]
        for g in self.guidelines:
            rule_lower = g.rule_text.lower()
            for vp in vague_phrases:
                if vp in rule_lower:
                    findings.append({
                        "type": "Ambiguity",
                        "severity": "Medium",
                        "guideline_a": f"[{g.category}] {g.title}",
                        "guideline_b": None,
                        "explanation": f"Guideline contains subjective phrasing '{vp}' without actionable criteria, causing inconsistent reviews.",
                        "recommendation": f"Replace '{vp}' with measurable criteria (e.g. contrast ratio >= 4.5:1, sentence length < 25 words)."
                    })

        # 3. Rules Missing Practical Examples
        for g in self.guidelines:
            if not g.example_good or not g.example_bad:
                findings.append({
                    "type": "Missing Example",
                    "severity": "Low",
                    "guideline_a": f"[{g.category}] {g.title}",
                    "guideline_b": None,
                    "explanation": f"Guideline lacks verified positive or negative examples. Content creators frequently misinterpret abstract rules.",
                    "recommendation": "Add at least one approved ('Do this') and one prohibited ('Don't do this') example."
                })

        # 4. Missing Approved Facts for Key Claims
        # If guidelines mention warranty or security but no fact is registered
        has_warranty_rule = any("warranty" in (g.title + g.rule_text).lower() for g in self.guidelines)
        has_warranty_fact = any("warranty" in f.topic.lower() for f in self.facts)
        if has_warranty_rule and not has_warranty_fact:
            findings.append({
                "type": "Missing Fact",
                "severity": "High",
                "guideline_a": "Brand Guideline mentions Warranty Policy",
                "guideline_b": None,
                "explanation": "Guidelines discuss warranty representation, but no verified warranty fact exists in the Approved Facts repository.",
                "recommendation": "Register an official warranty fact with source document and last-updated date in Brand Intelligence Brain."
            })

        return findings
