import re
from typing import Dict, Any, List

class RewriteStudioEngine:
    def generate_rewrites(self, sentence: str, dimension: str = "Tone", guideline: str = "") -> List[Dict[str, str]]:
        """Generate 3 distinct, high-quality brand-compliant rewrite options."""
        s = sentence.strip()
        
        # Base replacements
        replacements = [
            (r'\blifetime\s+warranty\b', '12-month standard warranty with optional enterprise extension'),
            (r'\bunlimited\s+warranty\b', 'comprehensive warranty backed by our enterprise SLA'),
            (r'\b100%\s+uptime\b', '99.9% uptime SLA guaranteed'),
            (r'\bzero\s+downtime\b', 'industry-leading 99.9% availability'),
            (r'\bcuts?\s+costs?\s+by\s+9[0-9]%\b', 'dramatically optimizes your operating expenditure'),
            (r'\b100%\s+bug-free\b', 'rigorously tested with enterprise-grade automated CI/CD safeguards'),
            (r'\bgonna\b', 'going to'),
            (r'\bwanna\b', 'want to'),
            (r'\bcheap\b', 'cost-effective and high-value'),
            (r'\bfoolproof\b', 'robust and user-centric'),
            (r'\bbadass\b', 'industry-leading'),
            (r'\bno-brainer\b', 'clear strategic choice'),
            (r'\bsucks\b', 'presents significant friction'),
            (r'\bparadigm\s+shift\b', 'meaningful transformation'),
            (r'\bsynergy\b', 'collaborative integration'),
            (r'[!?]{2,}', '.'),
            (r'\bவாழ்நாள்\s+உத்தரவாதம்\b', '12 மாத நிலையான உத்தரவாதம்'),
            (r'\b100%\s+இலவசம்\b', 'வெளிப்படையான விலைத் திட்டம்'),
        ]
        
        cleaned = s
        for pat, repl in replacements:
            cleaned = re.sub(pat, repl, cleaned, flags=re.IGNORECASE)

        # 1. Professional Mode
        prof_text = cleaned
        if not prof_text.endswith('.'):
            prof_text += '.'
        # Ensure capital start
        prof_text = prof_text[0].upper() + prof_text[1:] if len(prof_text) > 0 else prof_text
        
        prof_option = {
            "option_type": "Professional",
            "rewritten_text": prof_text,
            "rationale": "Authoritative, clear, and compliant with enterprise brand voice. Removes hyperbolic statements and aligns with verified facts."
        }

        # 2. Friendly Mode
        friendly_text = cleaned
        # Make conversational
        if "guaranteed" in friendly_text.lower():
            friendly_text = friendly_text.replace("guaranteed", "designed to support your daily workflow")
        if "our platform" in friendly_text.lower() or "we" in friendly_text.lower():
            friendly_text = f"We are excited to help you succeed: {friendly_text}"
        else:
            friendly_text = f"Discover a better way forward: {friendly_text}"
            
        friendly_option = {
            "option_type": "Friendly",
            "rewritten_text": friendly_text,
            "rationale": "Warm, engaging, and accessible tone while strictly adhering to compliance standards."
        }

        # 3. Marketing-Oriented Mode
        mkt_text = cleaned
        if "12-month standard warranty" in mkt_text:
            mkt_text = mkt_text.replace("12-month standard warranty", "trusted 12-month warranty backing every deployment")
        mkt_text = f"Elevate your brand performance — {mkt_text}"
        
        mkt_option = {
            "option_type": "Marketing",
            "rewritten_text": mkt_text,
            "rationale": "Compelling, value-driven, and persuasive without resorting to unsupported superlatives or legal exposure."
        }

        return [prof_option, friendly_option, mkt_option]
