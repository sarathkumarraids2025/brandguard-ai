import re
import math
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.models import TerminologyRule, BrandGuideline, BrandProfile
from app.services.fact_verifier import FactVerifier

# Common English & Tamil banned / risky phrases
CLICHE_PHRASES = [
    "paradigm shift", "synergy", "game-changer", "revolutionary secret",
    "miracle cure", "get rich quick", "100% guaranteed", "foolproof solution",
    "secret sauce", "think outside the box", "disrupt the universe"
]

INFORMAL_SLANG = [
    "gonna", "wanna", "kinda", "crap", "sucks", "bro", "dude", "lol", "omg",
    "no-brainer", "freaking", "badass", "legit", "super cool"
]

TAMIL_INFORMAL_SLANG = [
    "சும்மா", "வெட்டி", "கலக்கு", "மச்சான்", "தாறுமாறு", "கட்டாயம் நம்புங்க"
]

class NLPEngine:
    def __init__(self, db: Session, profile_id: int):
        self.db = db
        self.profile_id = profile_id
        self.profile = db.query(BrandProfile).filter(BrandProfile.id == profile_id).first()
        self.terminology_rules = db.query(TerminologyRule).filter(
            TerminologyRule.profile_id == profile_id
        ).all()
        self.guidelines = db.query(BrandGuideline).filter(
            BrandGuideline.profile_id == profile_id,
            BrandGuideline.is_active == True
        ).all()
        self.fact_verifier = FactVerifier(db, profile_id)

    def calculate_readability(self, text: str) -> Dict[str, Any]:
        """Calculate Flesch Reading Ease & Flesch-Kincaid Grade Level."""
        words = re.findall(r'\b[a-zA-Z0-9_\u0B80-\u0BFF]+\b', text)
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
        
        num_words = max(len(words), 1)
        num_sentences = max(len(sentences), 1)
        
        # Approximate syllable counting
        def count_syllables(word: str) -> int:
            word = word.lower()
            count = len(re.findall(r'[aeiouy]+', word))
            if word.endswith('e') and not word.endswith('le') and count > 1:
                count -= 1
            return max(count, 1)

        syllables = sum(count_syllables(w) for w in words)
        
        # Flesch Reading Ease Formula
        words_per_sent = num_words / num_sentences
        syllables_per_word = syllables / num_words
        
        flesch_score = 206.835 - (1.015 * words_per_sent) - (84.6 * syllables_per_word)
        flesch_score = round(max(0.0, min(100.0, flesch_score)), 1)
        
        # Flesch-Kincaid Grade Level
        grade_level = (0.39 * words_per_sent) + (11.8 * syllables_per_word) - 15.59
        grade_level = round(max(1.0, min(18.0, grade_level)), 1)
        
        return {
            "flesch_reading_ease": flesch_score,
            "grade_level": grade_level,
            "total_words": num_words,
            "total_sentences": num_sentences,
            "avg_words_per_sentence": round(words_per_sent, 1)
        }

    def check_terminology(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        """Check content against prohibited and preferred brand terminology."""
        issues = []
        sentences = re.split(r'(?<=[.!?\n]) +', text)

        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue

            for rule in self.terminology_rules:
                # Prohibited term detection (Unicode-aware for Tamil & English)
                is_ascii = all(ord(c) < 128 for c in rule.prohibited_term)
                if is_ascii:
                    pattern = r'\b' + re.escape(rule.prohibited_term) + r'\b'
                else:
                    pattern = re.escape(rule.prohibited_term)
                    
                match = re.search(pattern, sent_clean, re.IGNORECASE)
                if match:
                    issues.append({
                        "dimension": "Terminology",
                        "title": f"Prohibited Term Detected: '{rule.prohibited_term}'",
                        "severity": "Critical" if rule.is_strict else "High",
                        "sentence": sent_clean,
                        "explanation": f"The term '{rule.prohibited_term}' violates brand guidelines. {rule.rationale or 'Brand standards require official terminology.'}",
                        "guideline_citation": f"Terminology Standard: Use '{rule.preferred_term}' instead of '{rule.prohibited_term}'",
                        "evidence": f"Approved Terminology Registry: Prefer '{rule.preferred_term}'",
                        "suggested_correction": re.sub(pattern, rule.preferred_term, sent_clean, flags=re.I),
                        "confidence_score": 0.99,
                        "requires_human_verification": False
                    })
        return issues

    def check_tone_and_voice(self, text: str, content_type: str, language: str = "en") -> List[Dict[str, Any]]:
        """Evaluate tone of voice against brand guidelines."""
        issues = []
        sentences = re.split(r'(?<=[.!?\n]) +', text)

        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue

            # 1. Slang and informal speech check
            for slang in (TAMIL_INFORMAL_SLANG if language == "ta" else INFORMAL_SLANG):
                if re.search(r'\b' + re.escape(slang) + r'\b', sent_clean, re.I):
                    issues.append({
                        "dimension": "Voice",
                        "title": "Unprofessional / Informal Colloquialism",
                        "severity": "Medium",
                        "sentence": sent_clean,
                        "explanation": f"Colloquial slang '{slang}' undermines enterprise credibility and violates brand tone guidelines.",
                        "guideline_citation": "Tone of Voice Guide: Maintain professional, authoritative, and respectful language.",
                        "evidence": "Brand Guidelines §2.1 (Tone & Vocabulary)",
                        "suggested_correction": sent_clean.replace(slang, "[Professional alternative]"),
                        "confidence_score": 0.92,
                        "requires_human_verification": False
                    })

            # 2. Clichés and overhyped buzzwords
            for cliche in CLICHE_PHRASES:
                if re.search(r'\b' + re.escape(cliche) + r'\b', sent_clean, re.I):
                    issues.append({
                        "dimension": "Voice",
                        "title": f"Overused Buzzword: '{cliche}'",
                        "severity": "Low",
                        "sentence": sent_clean,
                        "explanation": f"Marketing cliché '{cliche}' reduces messaging distinctiveness.",
                        "guideline_citation": "Editorial Guide §1.4: Favor concrete evidence over buzzwords.",
                        "evidence": "Brand Guidelines §1.4",
                        "suggested_correction": sent_clean.replace(cliche, "tangible innovation"),
                        "confidence_score": 0.88,
                        "requires_human_verification": False
                    })

            # 3. Aggressive or Fear-Mongering language
            fear_match = re.search(r'\b(disaster\s+awaits|catastrophic\s+failure|you\s+will\s+regret|அழிந்துவிடும்|மோசமான\s+விளைவு)\b', sent_clean, re.I)
            if fear_match:
                issues.append({
                    "dimension": "Tone",
                    "title": "Fear-Inducing / Negative Framing",
                    "severity": "High",
                    "sentence": sent_clean,
                    "explanation": f"Alarmist phrasing '{fear_match.group(0)}' conflicts with our brand pillar of empowering, constructive customer empathy.",
                    "guideline_citation": "Brand Values: Empowering, constructive, and forward-looking.",
                    "evidence": "Brand Guidelines §2.3 (Emotional Resonance)",
                    "suggested_correction": "Reframe the scenario around risk mitigation and proactive protection.",
                    "confidence_score": 0.94,
                    "requires_human_verification": False
                })

            # 4. Excessive punctuation (e.g. "!!!" or "???")
            if re.search(r'[!?]{2,}', sent_clean):
                issues.append({
                    "dimension": "Voice",
                    "title": "Excessive Punctuation",
                    "severity": "Low",
                    "sentence": sent_clean,
                    "explanation": "Multiple exclamation marks or question marks degrade professional brand presentation.",
                    "guideline_citation": "Editorial Style Guide §5.2 (Punctuation)",
                    "evidence": "Brand Guidelines §5.2",
                    "suggested_correction": re.sub(r'[!?]{2,}', '.', sent_clean),
                    "confidence_score": 0.99,
                    "requires_human_verification": False
                })

            # 5. ALL CAPS SHOUTING
            caps_words = [w for w in re.findall(r'\b[A-Z]{3,}\b', sent_clean) if w not in ("API", "SDK", "SOC", "ISO", "SLA", "CRM", "CEO", "CTO", "CIO", "AI", "ML")]
            if len(caps_words) >= 2:
                issues.append({
                    "dimension": "Voice",
                    "title": "All-Caps Yelling Detected",
                    "severity": "Medium",
                    "sentence": sent_clean,
                    "explanation": f"Words in ALL-CAPS ({', '.join(caps_words[:3])}) feel aggressive and harm readability.",
                    "guideline_citation": "Typography & Formatting Standard §3.1",
                    "evidence": "Brand Guidelines §3.1",
                    "suggested_correction": sent_clean.capitalize(),
                    "confidence_score": 0.96,
                    "requires_human_verification": False
                })

        return issues

    def check_readability_and_style(self, text: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audit sentence complexity, length, and readability."""
        issues = []
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]

        for sent in sentences:
            words = sent.split()
            # Very long sentence (> 32 words)
            if len(words) > 32:
                issues.append({
                    "dimension": "Readability",
                    "title": "Run-On Sentence (>32 words)",
                    "severity": "Medium",
                    "sentence": sent,
                    "explanation": f"This sentence contains {len(words)} words. Long sentences severely diminish reader comprehension and accessibility.",
                    "guideline_citation": "Accessibility & Readability Standard: Keep sentences under 25 words.",
                    "evidence": "Brand Writing Standard §3.0",
                    "suggested_correction": "Split this into two concise, clear sentences.",
                    "confidence_score": 0.95,
                    "requires_human_verification": False
                })

            # Passive voice indicator
            if re.search(r'\b(is\s+being|was\s+being|has\s+been|were\s+made|was\s+done\s+by)\b', sent, re.I):
                issues.append({
                    "dimension": "Readability",
                    "title": "Passive Voice Overuse",
                    "severity": "Low",
                    "sentence": sent,
                    "explanation": "Passive voice weakens ownership and clarity. Prefer active, direct verbs.",
                    "guideline_citation": "Writing Style: Use active voice to convey confidence.",
                    "evidence": "Brand Writing Standard §1.2",
                    "suggested_correction": "Rewrite with an active subject.",
                    "confidence_score": 0.85,
                    "requires_human_verification": False
                })

        # Check overall readability score
        if metrics["flesch_reading_ease"] < 40.0:
            issues.append({
                "dimension": "Readability",
                "title": f"Low Reading Ease ({metrics['flesch_reading_ease']}/100)",
                "severity": "Medium",
                "sentence": "Overall Document",
                "explanation": f"The document has a Flesch Reading Ease of {metrics['flesch_reading_ease']} (College graduate level). Recommended target is 60-70 for commercial communications.",
                "guideline_citation": "Accessibility Standard: Target Flesch Reading Ease > 60",
                "evidence": "Global Accessibility Guidelines §4.1",
                "suggested_correction": "Simplify vocabulary and reduce complex nested clauses.",
                "confidence_score": 0.90,
                "requires_human_verification": False
            })

        return issues

    def audit_content(self, text: str, content_type: str = "general", language: str = "en") -> Dict[str, Any]:
        """Execute full multidimensional brand audit."""
        metrics = self.calculate_readability(text)
        
        # 1. Fact Verification
        fact_issues = self.fact_verifier.verify_content(text, language=language)
        
        # 2. Terminology Compliance
        term_issues = self.check_terminology(text, language=language)
        
        # 3. Tone and Voice
        voice_issues = self.check_tone_and_voice(text, content_type=content_type, language=language)
        
        # 4. Readability and Style
        readability_issues = self.check_readability_and_style(text, metrics)
        
        all_issues = fact_issues + term_issues + voice_issues + readability_issues
        
        # Calculate Category-wise scores
        # Mathematical formula:
        # Base = 100
        # Penalties: Critical: -18, High: -10, Medium: -5, Low: -2
        def score_for_issues(issue_list):
            penalty = 0
            for iss in issue_list:
                sev = iss.get("severity", "Medium")
                if sev == "Critical":
                    penalty += 18
                elif sev == "High":
                    penalty += 10
                elif sev == "Medium":
                    penalty += 5
                else:
                    penalty += 2
            return max(0.0, round(100.0 - penalty, 1))

        voice_score = score_for_issues(voice_issues)
        factual_score = score_for_issues(fact_issues)
        terminology_score = score_for_issues(term_issues)
        accessibility_score = score_for_issues(readability_issues)
        visual_score = 100.0  # Will be adjusted by visual module if creative
        
        # Weighted overall compliance score
        # 35% Facts, 25% Terminology, 20% Voice, 10% Readability, 10% Visual
        overall_score = round(
            (factual_score * 0.35) +
            (terminology_score * 0.25) +
            (voice_score * 0.20) +
            (accessibility_score * 0.10) +
            (visual_score * 0.10),
            1
        )
        
        # Determine explainable Risk Level
        if overall_score >= 85:
            risk_level = "Low"
        elif overall_score >= 70:
            risk_level = "Moderate"
        elif overall_score >= 50:
            risk_level = "High"
        else:
            risk_level = "Critical"
            
        score_breakdown = {
            "formula": "Deterministic weighted sum: 35% Facts + 25% Terminology + 20% Voice + 10% Accessibility + 10% Visual with exact guideline penalties",
            "penalties_applied": {
                "critical_count": sum(1 for i in all_issues if i["severity"] == "Critical"),
                "high_count": sum(1 for i in all_issues if i["severity"] == "High"),
                "medium_count": sum(1 for i in all_issues if i["severity"] == "Medium"),
                "low_count": sum(1 for i in all_issues if i["severity"] == "Low"),
            },
            "metrics": metrics
        }
        
        return {
            "overall_score": overall_score,
            "voice_score": voice_score,
            "factual_score": factual_score,
            "terminology_score": terminology_score,
            "accessibility_score": accessibility_score,
            "visual_score": visual_score,
            "risk_level": risk_level,
            "score_breakdown": score_breakdown,
            "issues": all_issues
        }
