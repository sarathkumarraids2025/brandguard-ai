import os
import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.models import (
    Organisation, User, BrandProfile, BrandGuideline, ApprovedFact,
    TerminologyRule, BrandAsset, ContentSubmission, AnalysisResult,
    DetectedIssue, RewriteSuggestion, Comment, ReviewAction, AuditLog
)

def seed_database():
    print("[BrandGuard AI] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Organisation).filter(Organisation.slug == "nexura").first():
            print("[BrandGuard AI] Database already contains seed data.")
            return

        print("[BrandGuard AI] Seeding Organisation and Users...")
        org = Organisation(
            name="Nexura Technologies",
            slug="nexura",
            industry="Enterprise Cloud & AI Software"
        )
        db.add(org)
        db.flush()

        # Users for 3 roles: ADMIN, CREATOR, REVIEWER
        admin_pwd = hash_password("BrandGuard2026!")
        user_admin = User(
            org_id=org.id,
            email="admin@brandguard.ai",
            password_hash=admin_pwd,
            full_name="Sarah Jenkins (Admin)",
            role="ADMIN",
            department="Executive",
            avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"
        )
        user_creator = User(
            org_id=org.id,
            email="creator@brandguard.ai",
            password_hash=admin_pwd,
            full_name="Alex Rivera (Creator)",
            role="CREATOR",
            department="Marketing",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
        )
        user_reviewer = User(
            org_id=org.id,
            email="reviewer@brandguard.ai",
            password_hash=admin_pwd,
            full_name="Marcus Vance (Reviewer)",
            role="REVIEWER",
            department="Brand Governance",
            avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150"
        )
        db.add_all([user_admin, user_creator, user_reviewer])
        db.flush()

        print("[BrandGuard AI] Seeding Brand Profile...")
        profile = BrandProfile(
            org_id=org.id,
            brand_name="Nexura Cloud Engine",
            tagline="Every Message Matters. Every Brand Deserves Consistency.",
            mission="Democratizing intelligent cloud orchestration with uncompromising reliability and ethical governance.",
            values="Transparency, Precision, Reliability, Inclusive Design, Empathy",
            tone_voice="Authoritative, empathetic, clear, precise; never hyperbolic, alarmist, or informal.",
            writing_style="Active voice, direct verbs, concise sentences (<25 words), evidence-based claims.",
            target_audience="Enterprise CTOs, Cloud Architects, Marketing Directors, Compliance Officers"
        )
        db.add(profile)
        db.flush()

        print("[BrandGuard AI] Seeding Brand Guidelines...")
        guidelines = [
            BrandGuideline(
                profile_id=profile.id,
                category="Voice",
                title="Authoritative & Direct Corporate Voice",
                rule_text="Maintain an authoritative, direct, and professional voice in all external communications. Avoid informal slang, conversational filler, and hyperbolic clickbait.",
                severity="High",
                rationale="Ensures institutional trust across enterprise buyers.",
                example_good="Nexura streamlines enterprise deployment workflows with automated governance.",
                example_bad="Nexura is gonna totally blow your mind, it's a badass tool!"
            ),
            BrandGuideline(
                profile_id=profile.id,
                category="Tone",
                title="Playful and Casual Social Tone",
                rule_text="Use a casual, humorous, and playful tone for every social media post to maximize engagement.",
                severity="Medium",
                rationale="Encourages viral engagement on social platforms.",
                example_good="Happy Friday tech fam! Ready to deploy without weekend drama?",
                example_bad="Corporate memorandum: operational maintenance commences Friday 18:00 UTC."
            ),
            BrandGuideline(
                profile_id=profile.id,
                category="Writing",
                title="Active Voice & Conciseness Standard",
                rule_text="Draft all sentences using active voice. Keep individual sentences below 25 words to optimize reading comprehension across all audience segments.",
                severity="Medium",
                rationale="Reduces cognitive load and improves accessibility.",
                example_good="Our platform secures multi-cloud environments automatically.",
                example_bad="The multi-cloud environments have been secured by our platform through a complex series of algorithmic operations that were designed by our team."
            ),
            BrandGuideline(
                profile_id=profile.id,
                category="Compliance",
                title="Mandatory Claim Substantiation",
                rule_text="Never state unverified claims such as '100% bug-free', 'zero downtime', or 'lifetime warranty'. Every promotional claim must reference a verified corporate fact.",
                severity="Critical",
                rationale="Prevents regulatory fines and contractual misrepresentation liabilities.",
                example_good="Our 99.9% uptime SLA is backed by 24/7 engineering support.",
                example_bad="We guarantee 100% uptime with zero downtime forever!"
            ),
            BrandGuideline(
                profile_id=profile.id,
                category="Visual",
                title="Logo Clearance & Quadrant Placement",
                rule_text="Approved brand logo must be positioned in the top-left or top-right quadrant with a minimum 24px exclusion zone on all marketing creatives.",
                severity="High",
                rationale="Maintains recognizable brand hierarchy.",
                example_good="Vector mark positioned top-left with generous whitespace.",
                example_bad="Logo stretched, rotated, or placed in bottom center obscuring imagery."
            ),
            BrandGuideline(
                profile_id=profile.id,
                category="Accessibility",
                title="WCAG 2.1 AA Contrast Ratio (>= 4.5:1)",
                rule_text="All text and graphical elements must maintain a minimum contrast ratio of 4.5:1 against their background.",
                severity="Critical",
                rationale="Legal accessibility compliance requirement under ADA and EU Accessibility Acts.",
                example_good="White text (#FFFFFF) on Primary Blue (#2563EB) yielding 8.2:1 contrast.",
                example_bad="Light cyan text (#67E8F9) on white background (#FFFFFF) yielding 1.4:1 contrast."
            )
        ]
        db.add_all(guidelines)
        db.flush()

        print("[BrandGuard AI] Seeding Approved Facts with sources & verified dates...")
        facts = [
            ApprovedFact(
                profile_id=profile.id,
                topic="Product Warranty Policy",
                fact_text="Product X offers a 12-month standard warranty with optional 24-month enterprise extension.",
                category="Warranty",
                source_doc="Legal Warranty Charter 2026",
                source_url="https://nexura.internal/legal/warranty-2026.pdf",
                verified_date="2026-11-10"
            ),
            ApprovedFact(
                profile_id=profile.id,
                topic="Global Cloud Infrastructure",
                fact_text="Nexura operates 14 global data centers across 6 continents.",
                category="Infrastructure",
                source_doc="Cloud Architecture Whitepaper Q4",
                source_url="https://nexura.internal/docs/infra-q4.pdf",
                verified_date="2026-11-01"
            ),
            ApprovedFact(
                profile_id=profile.id,
                topic="SLA Availability Commitment",
                fact_text="Our enterprise SLA guarantees 99.9% uptime with 24/7 dedicated engineering support.",
                category="SLA",
                source_doc="Master Service Agreement §4.1",
                source_url="https://nexura.internal/legal/msa.pdf",
                verified_date="2026-10-15"
            ),
            ApprovedFact(
                profile_id=profile.id,
                topic="Corporate History & Founding",
                fact_text="Nexura was founded in 2021 by Dr. Sarah Jenkins and David Chen.",
                category="Corporate",
                source_doc="SEC Regulatory Filing Form D",
                source_url="https://sec.gov/edgar/nexura",
                verified_date="2026-09-01"
            ),
            ApprovedFact(
                profile_id=profile.id,
                topic="Security & Compliance Certifications",
                fact_text="Certified with SOC-2 Type II, ISO 27001, and GDPR compliance.",
                category="Security",
                source_doc="Independent Audit Report by Ernst & Young",
                source_url="https://nexura.internal/compliance/audit-2026.pdf",
                verified_date="2026-10-20"
            )
        ]
        db.add_all(facts)
        db.flush()

        print("[BrandGuard AI] Seeding Terminology Rules...")
        terms = [
            TerminologyRule(
                profile_id=profile.id,
                preferred_term="cost-effective and high-value",
                prohibited_term="cheap",
                context="All commercial messaging",
                rationale="'Cheap' conveys inferior build quality; use 'cost-effective' or 'high-value'.",
                is_strict=True,
                language="en"
            ),
            TerminologyRule(
                profile_id=profile.id,
                preferred_term="robust and fail-safe",
                prohibited_term="foolproof",
                context="Product descriptions",
                rationale="Avoid implying that users or clients lack competence.",
                is_strict=False,
                language="en"
            ),
            TerminologyRule(
                profile_id=profile.id,
                preferred_term="rigorously validated and verified",
                prohibited_term="100% bug-free",
                context="Software guarantees",
                rationale="Software can never mathematically guarantee 100% absence of defects.",
                is_strict=True,
                language="en"
            ),
            TerminologyRule(
                profile_id=profile.id,
                preferred_term="measurable return on investment",
                prohibited_term="guaranteed wealth",
                context="Marketing and ROI statements",
                rationale="Financial regulatory guidelines prohibit claims guaranteeing wealth.",
                is_strict=True,
                language="en"
            ),
            TerminologyRule(
                profile_id=profile.id,
                preferred_term="unauthorized malicious actors",
                prohibited_term="hackers",
                context="Security advisories",
                rationale="Terminology accuracy: prefer formal threat actor designation.",
                is_strict=False,
                language="en"
            ),
            # Tamil Terminology Rules
            TerminologyRule(
                profile_id=profile.id,
                preferred_term="12 மாத நிலையான உத்தரவாதம்",
                prohibited_term="வாழ்நாள் உத்தரவாதம்",
                context="Tamil promotional material",
                rationale="அங்கீகரிக்கப்பட்ட உத்தரவாத விதிமுறைகளுக்கு இணங்க வேண்டும்.",
                is_strict=True,
                language="ta"
            ),
            TerminologyRule(
                profile_id=profile.id,
                preferred_term="வெளிப்படையான கட்டணத் திட்டம்",
                prohibited_term="100% இலவசம்",
                context="Tamil pricing copy",
                rationale="நிறுவனத்தின் வெளிப்படையான கட்டண விதிமுறைகளை பின்பற்றவும்.",
                is_strict=True,
                language="ta"
            )
        ]
        db.add_all(terms)
        db.flush()

        print("[BrandGuard AI] Seeding Brand Visual Assets & Palette...")
        assets = [
            BrandAsset(
                profile_id=profile.id,
                asset_type="LOGO",
                name="Nexura Primary Vector Mark",
                file_path="/static/logo.png",
                meta_info={"format": "PNG", "min_width": 200, "safe_margin_px": 24}
            ),
            BrandAsset(
                profile_id=profile.id,
                asset_type="COLOR_PALETTE",
                name="Primary Royal Blue",
                color_hex="#2563EB",
                meta_info={"rgb": [37, 99, 235], "role": "Primary Brand Color"}
            ),
            BrandAsset(
                profile_id=profile.id,
                asset_type="COLOR_PALETTE",
                name="Deep Violet",
                color_hex="#7C3AED",
                meta_info={"rgb": [124, 58, 237], "role": "Secondary Accent"}
            ),
            BrandAsset(
                profile_id=profile.id,
                asset_type="COLOR_PALETTE",
                name="Electric Cyan",
                color_hex="#06B6D4",
                meta_info={"rgb": [6, 182, 212], "role": "Feature Accent"}
            ),
            BrandAsset(
                profile_id=profile.id,
                asset_type="COLOR_PALETTE",
                name="Mint Emerald",
                color_hex="#10B981",
                meta_info={"rgb": [16, 185, 129], "role": "Success & Verification"}
            ),
            BrandAsset(
                profile_id=profile.id,
                asset_type="COLOR_PALETTE",
                name="Coral Rose",
                color_hex="#F43F5E",
                meta_info={"rgb": [244, 63, 94], "role": "Alert & Warning"}
            )
        ]
        db.add_all(assets)
        db.flush()

        print("[BrandGuard AI] Seeding Initial Content Submissions with Issues & Workflow...")
        # 1. Marketing Submission with critical issues
        sub1 = ContentSubmission(
            org_id=org.id,
            profile_id=profile.id,
            creator_id=user_creator.id,
            title="Q4 Enterprise Cloud Product Launch Announcement",
            content_type="press_release",
            raw_text="Nexura is proud to announce Product X. Product X offers a lifetime warranty with zero downtime forever! It is a cheap, foolproof solution that cuts costs by 99% guaranteed. Our revolutionary secret sauce is gonna blow away the competition!!!",
            corrected_text="Nexura is proud to announce Product X. Product X offers a 12-month standard warranty with 99.9% uptime SLA. It is a cost-effective, robust and fail-safe solution that significantly optimizes operational efficiency. Our validated cloud architecture accelerates enterprise growth.",
            language="en",
            department="Marketing",
            status="Review Required",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
        )
        db.add(sub1)
        db.flush()

        # Analysis for sub1
        res1 = AnalysisResult(
            submission_id=sub1.id,
            overall_score=48.5,
            voice_score=60.0,
            factual_score=35.0,
            visual_score=100.0,
            accessibility_score=80.0,
            terminology_score=45.0,
            risk_level="Critical",
            score_breakdown={
                "formula": "Deterministic weighted sum: 35% Facts + 25% Terminology + 20% Voice + 10% Accessibility + 10% Visual",
                "penalties_applied": {"critical": 2, "high": 2, "medium": 1, "low": 2}
            },
            scanned_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
        )
        db.add(res1)
        db.flush()

        # Issues for sub1
        iss1 = DetectedIssue(
            analysis_id=res1.id,
            dimension="Fact",
            title="Warranty Claim Contradiction",
            severity="Critical",
            sentence="Product X offers a lifetime warranty with zero downtime forever!",
            explanation="Submitted content asserts 'lifetime warranty', which directly conflicts with registered company warranty policy.",
            guideline_citation="Approved Fact #WF-01 (Product Warranty Policy)",
            evidence='Approved Fact [Legal Warranty Charter 2026, verified 2026-11-10]: "Product X offers a 12-month standard warranty with optional 24-month enterprise extension."',
            suggested_correction="Product X offers a 12-month standard warranty with 99.9% uptime SLA.",
            confidence_score=0.98,
            requires_human_verification=False
        )
        iss2 = DetectedIssue(
            analysis_id=res1.id,
            dimension="Fact",
            title="Absolute SLA / Uptime Misstatement",
            severity="Critical",
            sentence="Product X offers a lifetime warranty with zero downtime forever!",
            explanation="Absolute claims such as 'zero downtime forever' violate SLA compliance standards.",
            guideline_citation="Compliance Fact Sheet #SLA-02",
            evidence='Approved Fact [Master Service Agreement §4.1, verified 2026-10-15]: "Our enterprise SLA guarantees 99.9% uptime with 24/7 dedicated engineering support."',
            suggested_correction="backed by a 99.9% uptime SLA.",
            confidence_score=0.96,
            requires_human_verification=False
        )
        iss3 = DetectedIssue(
            analysis_id=res1.id,
            dimension="Terminology",
            title="Prohibited Term Detected: 'cheap'",
            severity="Critical",
            sentence="It is a cheap, foolproof solution that cuts costs by 99% guaranteed.",
            explanation="The term 'cheap' violates brand guidelines. 'Cheap' conveys inferior build quality; use 'cost-effective' or 'high-value'.",
            guideline_citation="Terminology Standard: Use 'cost-effective and high-value' instead of 'cheap'",
            evidence="Approved Terminology Registry: Prefer 'cost-effective and high-value'",
            suggested_correction="It is a cost-effective, robust and fail-safe solution that significantly optimizes operational efficiency.",
            confidence_score=0.99,
            requires_human_verification=False
        )
        iss4 = DetectedIssue(
            analysis_id=res1.id,
            dimension="Claim",
            title="Unsupported Promotional Superlative",
            severity="Critical",
            sentence="It is a cheap, foolproof solution that cuts costs by 99% guaranteed.",
            explanation="Statement contains absolute claim 'cuts costs by 99% guaranteed' without verifiable backing data.",
            guideline_citation="Advertising Standards & Substantiation Policy §3.1",
            evidence="Unable to verify against approved sources.",
            suggested_correction="significantly optimizes operational efficiency",
            confidence_score=0.92,
            requires_human_verification=True
        )
        iss5 = DetectedIssue(
            analysis_id=res1.id,
            dimension="Voice",
            title="Unprofessional / Informal Colloquialism",
            severity="Medium",
            sentence="Our revolutionary secret sauce is gonna blow away the competition!!!",
            explanation="Colloquial slang 'gonna' undermines enterprise credibility and violates brand tone guidelines.",
            guideline_citation="Tone of Voice Guide: Maintain professional, authoritative language.",
            evidence="Brand Guidelines §2.1",
            suggested_correction="Our cloud architecture delivers competitive differentiation.",
            confidence_score=0.92,
            requires_human_verification=False
        )
        db.add_all([iss1, iss2, iss3, iss4, iss5])
        db.flush()

        # Rewrites for iss1
        db.add_all([
            RewriteSuggestion(
                issue_id=iss1.id,
                option_type="Professional",
                rewritten_text="Product X offers a 12-month standard warranty backed by our enterprise SLA.",
                rationale="Authoritative, factual, and strictly compliant with legal warranty charter."
            ),
            RewriteSuggestion(
                issue_id=iss1.id,
                option_type="Friendly",
                rewritten_text="We are thrilled to support your team with our comprehensive 12-month standard warranty.",
                rationale="Approachable and customer-centric while maintaining factual accuracy."
            ),
            RewriteSuggestion(
                issue_id=iss1.id,
                option_type="Marketing",
                rewritten_text="Elevate your cloud operations with trusted 12-month warranty coverage on Product X.",
                rationale="Engaging marketing hook with substantiated policy terms."
            )
        ])

        # Comments and review action for sub1
        db.add(Comment(
            submission_id=sub1.id,
            user_id=user_reviewer.id,
            content="Alex, critical issues detected: lifetime warranty claim directly contradicts our legal warranty charter. Please apply the suggested 12-month warranty correction."
        ))
        db.add(ReviewAction(
            submission_id=sub1.id,
            reviewer_id=user_reviewer.id,
            action="REQUEST_REVISION",
            previous_status="Review Required",
            new_status="Revision Requested",
            notes="Warranty contradiction and unverified 99% cost claims must be amended before publication."
        ))

        # 2. Approved Technical Submission
        sub2 = ContentSubmission(
            org_id=org.id,
            profile_id=profile.id,
            creator_id=user_creator.id,
            title="Security Compliance & ISO-27001 Whitepaper",
            content_type="blog",
            raw_text="Nexura operates 14 global data centers across 6 continents. Certified with SOC-2 Type II, ISO 27001, and GDPR compliance, our architecture protects critical enterprise data with zero-trust access controls.",
            corrected_text="Nexura operates 14 global data centers across 6 continents. Certified with SOC-2 Type II, ISO 27001, and GDPR compliance, our architecture protects critical enterprise data with zero-trust access controls.",
            language="en",
            department="Product",
            status="Approved",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=7)
        )
        db.add(sub2)
        db.flush()

        res2 = AnalysisResult(
            submission_id=sub2.id,
            overall_score=98.5,
            voice_score=100.0,
            factual_score=100.0,
            visual_score=100.0,
            accessibility_score=95.0,
            terminology_score=100.0,
            risk_level="Low",
            score_breakdown={"formula": "Fully compliant with approved facts #INF-03 and #SEC-05"},
            scanned_at=datetime.datetime.utcnow() - datetime.timedelta(days=7)
        )
        db.add(res2)
        db.add(ReviewAction(
            submission_id=sub2.id,
            reviewer_id=user_reviewer.id,
            action="APPROVE",
            previous_status="Review Required",
            new_status="Approved",
            notes="Excellent submission. Facts perfectly verified against corporate compliance registers."
        ))

        # 3. Tamil Social Media Submission
        sub3 = ContentSubmission(
            org_id=org.id,
            profile_id=profile.id,
            creator_id=user_creator.id,
            title="Tamil Enterprise Solution Announcement (தமிழ்)",
            content_type="social",
            raw_text="நெக்சுரா கிளவுட் தளம் மூலம் உங்கள் நிறுவனத்தை பாதுகாக்கவும். 100% இலவசம் மற்றும் வாழ்நாள் உத்தரவாதம் வழங்குகிறோம்.",
            corrected_text="நெக்சுரா கிளவுட் தளம் மூலம் உங்கள் நிறுவனத்தை பாதுகாக்கவும். வெளிப்படையான கட்டணத் திட்டம் மற்றும் 12 மாத நிலையான உத்தரவாதம் வழங்குகிறோம்.",
            language="ta",
            department="Marketing",
            status="Revision Requested",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        db.add(sub3)
        db.flush()

        res3 = AnalysisResult(
            submission_id=sub3.id,
            overall_score=62.0,
            voice_score=75.0,
            factual_score=50.0,
            visual_score=100.0,
            accessibility_score=90.0,
            terminology_score=50.0,
            risk_level="High",
            score_breakdown={"formula": "Tamil terminology violations detected: வாழ்நாள் உத்தரவாதம், 100% இலவசம்"},
            scanned_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        db.add(res3)

        # Audit log for seed actions
        db.add(AuditLog(
            org_id=org.id,
            user_id=user_admin.id,
            user_name="System Seeder",
            action="INITIALIZE_SEED_DATA",
            target_type="System",
            target_id="NEXURA_01",
            details={"status": "seeded successfully"}
        ))

        db.commit()
        print("[BrandGuard AI] Seed data populated successfully!")
    except Exception as e:
        db.rollback()
        print(f"[BrandGuard AI] Seed error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
