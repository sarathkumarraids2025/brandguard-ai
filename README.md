# BRANDGUARD AI
### Intelligent Brand Governance & Content Intelligence Platform
> **Tagline:** Every Message Matters. Every Brand Deserves Consistency.

---

## 🌟 Executive Summary

**BRANDGUARD AI** is an enterprise-grade, full-stack AI-powered brand governance and content intelligence platform. Organizations publish content across thousands of distributed touchpoints: employees, agencies, marketing teams, and generative AI models. Without rigorous pre-publication governance, brands suffer from:

- Inconsistent brand voice and colloquial tone leakage.
- Contradictory product claims (e.g. advertising "lifetime warranty" when the approved warranty is 12 months).
- Outdated metrics (e.g. stating legacy data center counts or founding dates).
- Prohibited terminology and unsubstantiated superlatives (e.g. "cheap", "100% bug-free").
- Visual identity drift (off-brand color palettes, low WCAG contrast, missing logos).
- Premature unauthorized publication without human oversight.

BRANDGUARD AI enforces systematic, evidence-based quality control before content is published.

---

## 🚀 Unique Innovative Features

1. **Brand Intelligence Brain (Single Source of Truth):**
   - Central repository for brand identity, mission, values, tone guidelines, typography rules, approved facts, and terminology.
   - Every approved company fact is tied to a verified source document and verification date.
   - Built-in multi-format document parser (PDF, DOCX, TXT, CSV) to import knowledge.

2. **Multidimensional Brand Audit Engine (15 Dimensions):**
   - Evaluates content across Voice, Tone, Terminology, Approved Facts, Promotional Claims, Outdated Info, Messaging Alignment, Visual Consistency, Logo Usage, Palette Harmony, Typography, Accessibility (WCAG 2.1 AA), Readability (Flesch formula), Grammar, and Legal Risk.

3. **Evidence-Based Claim Verification (Major Innovation):**
   - Extracts factual assertions (warranty periods, infrastructure numbers, SLA percentages, founding years).
   - Classifies each claim: `Verified`, `Contradicted`, `Unsupported`, `Outdated`, or `Requires human review`.
   - Cites exact supporting evidence or displays transparently: `"Unable to verify against approved sources"`. **Never invents evidence.**

4. **Visual Brand Guardian (Computer Vision):**
   - Inspects uploaded creatives, posters, and banner graphics using Pillow and color science.
   - Quantizes dominant colors and measures Euclidean/Delta-E distance against the registered brand palette.
   - Calculates WCAG 2.1 relative luminance and contrast ratio (>= 4.5:1 AA threshold).
   - Analyzes header quadrant logo presence and returns interactive bounding box coordinates `[ymin, xmin, ymax, xmax]`.

5. **AI Smart Rewrite Studio:**
   - Generates three brand-compliant stylistic modes:
     1. **Professional Enterprise** (authoritative, compliant).
     2. **Friendly & Approachable** (warm, accessible).
     3. **Marketing-Oriented** (persuasive, legally safe).
   - Side-by-side diff comparison with user acceptance/rejection controls. Never replaces original text silently.

6. **Brand Guideline Clarity Analyzer (Meta-Audit Innovation):**
   - Cross-references brand guidelines to detect conflicting rules (e.g. formal corporate voice vs playful social tone without channel scoping), ambiguous wording, and missing facts.

7. **Brand Memory & Recurring Error Detection:**
   - Identifies recurring violation patterns across departments from past review records.
   - Generates actionable administrative coaching recommendations.

8. **Human Review & Approval Workflow (RBAC):**
   - Roles: **ADMIN**, **CREATOR**, **REVIEWER**.
   - State machine: `Draft` → `Analysing` → `Review Required` → `Revision Requested` → `Resubmitted` → `Approved`.
   - Immutable audit logs, revision comparison, reviewer feedback comments.

9. **Bilingual Experience (English + தமிழ் Tamil):**
   - Full toggle in the header: switches navigation, KPI cards, input instructions, explanations, severity badges, and charts between English and Tamil.
   - Supports bilingual content scanning with Tamil terminology and fact verification.

10. **Real Governance Analytics & CSV Reports:**
    - 5 Real Chart.js charts (Status Distribution Pie, Severity Doughnut, Category Violations Bar, Compliance Trend Line, Top Violations Horizontal Bar).
    - 100% database-derived analytics. No fabricated mock data.
    - Exportable CSV report via `/api/analytics/export-csv`.

---

## 🏗️ Architecture & Technology Stack

```
+-----------------------------------------------------------------------------------+
|                                 BRANDGUARD AI                                     |
+-----------------------------------------------------------------------------------+
|  FRONTEND LAYER                                                                   |
|  - Modern SPA: React 18, Tailwind CSS, Lucide Icons, Chart.js                     |
|  - Responsive Compact Sidebar (230px), Real 4K Hero Background with Overlay       |
|  - Full English + Tamil (தமிழ்) Localization Dictionary                           |
+-----------------------------------------------------------------------------------+
|  API ROUTING & SECURITY (FastAPI + Pydantic)                                      |
|  - /api/auth       (HS256 JWT, PBKDF2 Hashing, Instant 1-Click Demo Role Switcher)   |
|  - /api/scanner    (Text, PDF, DOCX, CSV, Safe SSRF URL Scraper)                   |
|  - /api/brand      (Guidelines, Approved Facts, Terminology, Asset Registry)     |
|  - /api/visual     (Dominant Color Extraction, Delta-E Match, WCAG Contrast Ratio)|
|  - /api/rewrite    (3 Style Modes, Side-by-Side Diff Alignment)                   |
|  - /api/review     (RBAC State Machine, Discussion Feed, Audit Logs)              |
|  - /api/analytics  (DB-derived Analytics, Real Chart Telemetry, CSV Export)       |
|  - /api/clarity    (Guideline Conflict & Ambiguity Detector)                      |
|  - /api/memory     (Recurring Departmental Error Telemetry)                       |
+-----------------------------------------------------------------------------------+
|  CORE ENGINES (Python 3.12)                                                       |
|  - NLP & Audit Engine    - Fact Verifier           - Visual Guardian Engine        |
|  - Document Extractor    - Rewrite Studio Engine   - Guideline Clarity Engine     |
+-----------------------------------------------------------------------------------+
|  DATABASE LAYER (SQLAlchemy ORM)                                                  |
|  - SQLite (Local Dev) / PostgreSQL (Cloud Deployment Compatible)                  |
|  - 15 Relational Tables: Users, Orgs, Profiles, Guidelines, Facts, Rules,        |
|    Assets, Submissions, Analyses, Issues, Rewrites, Comments, Actions, Logs     |
+-----------------------------------------------------------------------------------+
```

---

## ⚡ Quick Start & Local Execution

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Standard web browser (Chrome, Edge, Firefox, Safari)

### 2. Run the Platform
In the root directory, simply run:

```bash
python run.py
```

Open your browser to:
- **Web Application:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Alternative Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 3. Run Automated Quality Assurance Test Suite
The backend contains a 12-stage automated QA test suite verifying all critical components:

```bash
cd backend
python tests/run_tests.py
```

*Expected output: `ALL 12/12 QA TESTS PASSED SUCCESSFULLY! (100% PASS RATE)`*

---

## 👥 Demo Accounts & 1-Click Role Switcher

For instant testing by hackathon evaluators, BRANDGUARD AI features a **1-Click Role Switcher** in the left sidebar and header:

| Role | Demo Email | Password | Permissions |
|---|---|---|---|
| **ADMIN** | `admin@brandguard.ai` | `BrandGuard2026!` | Manage brand guidelines, facts, terminology, all submissions, analytics, clarity engine |
| **CREATOR** | `creator@brandguard.ai` | `BrandGuard2026!` | Scan content, view audit findings, generate rewrites, apply corrections, resubmit |
| **REVIEWER** | `reviewer@brandguard.ai` | `BrandGuard2026!` | Review submissions, add feedback comments, approve, request revisions, reject |

---

## 🧪 Step-by-Step Hackathon Verification Workflow

1. **Examine the Homepage:**
   - Notice the project-relevant high-resolution background image (`hero-bg.jpg`) with dark overlay.
   - Switch language to **தமிழ் (Tamil)** in the header: observe navigation, headlines, and buttons translating seamlessly.
2. **Launch Content Scanner:**
   - Click **"Load Sample Violations (EN)"** to load a test draft containing:
     - Lifetime warranty claim (contradicts approved 12-month policy).
     - "Cheap" and "foolproof" (prohibited brand terminology).
     - "Cuts costs by 99% guaranteed" (unsubstantiated promotional claim).
     - Informal slang "gonna" and excessive punctuation "!!!".
   - Click **"Analyse with BrandGuard AI"**: observe multi-stage analysis progress.
   - Review the Deep Audit Results:
     - Note the **48.5% compliance score** and **Critical Risk** classification.
     - Note the exact evidence citation for the warranty contradiction referencing `Legal Warranty Charter 2026`.
     - Note the transparent statement `"Unable to verify against approved sources"` on unverified claims.
3. **Open AI Smart Rewrite Studio:**
   - Click **"Rewrite Studio"** on any detected issue.
   - Inspect the three modes: **Professional**, **Friendly**, and **Marketing**.
   - Review the side-by-side Before & After comparison and accept the correction.
4. **Test Visual Brand Guardian:**
   - Navigate to **Visual Guardian**.
   - Click **"Load Creative with Violations"**:
     - View extracted dominant colors, off-brand palette warnings, and WCAG contrast failure (1.6:1).
     - Observe the highlighted bounding box overlays on the image canvas.
   - Click **"Load Compliant Creative"**:
     - Observe 100% brand color match, 8.2:1 contrast ratio, and approved top-left logo clearance.
5. **Human Review & Approval:**
   - Navigate to **Review & Approval Hub**.
   - Select a submission in `Review Required` or `Revision Requested` status.
   - Post a comment in the reviewer discussion thread.
   - Transition the workflow state to **Approved** or **Request Revision**: observe state change reflected in the immutable audit trail.
6. **Governance Analytics & CSV Export:**
   - Navigate to **Analytics**.
   - View the 5 real database-derived charts (Status Pie, Severity Doughnut, Category Bar, Compliance Trend Line, Top Violations Horizontal Bar).
   - Review the **Brand Memory & Recurring Error Telemetry** table.
   - Click **"Download CSV Governance Report"** to download the real spreadsheet.
7. **Guideline Clarity Analyzer:**
   - Navigate to **Brand Intelligence Brain** → **Guideline Clarity Analyzer** tab.
   - Observe the detected conflict between **[Voice] Authoritative Corporate Voice** and **[Tone] Playful and Casual Social Tone** with admin remediation advice.

---

## 🔒 Security & Responsible AI Commitments

- **SSRF Protection:** URL scanner validates IP addresses and blocks localhost, link-local (169.254.x), loopback, and private ranges.
- **NIST-Standard Authentication:** Passwords hashed with PBKDF2-HMAC-SHA256 (100,000 rounds) and RFC 7519 HS256 JWT tokens.
- **Explainable Scores:** Bounded mathematical formulas with explicit penalty accounting. Zero arbitrary hallucinated metrics.
- **Human-in-the-Loop:** System strictly mandates human review before critical enterprise publication.

---

## 📄 License
Developed for the **BRANDGUARD AI** Hackathon. Built with enterprise craftsmanship and precision.
