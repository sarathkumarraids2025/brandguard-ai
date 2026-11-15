import pytest
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.database import SessionLocal
from app.models.models import User, ContentSubmission, BrandProfile
from app.services.nlp_engine import NLPEngine
from app.services.fact_verifier import FactVerifier
from app.services.visual_engine import VisualGuardianEngine
from app.services.clarity_analyzer import GuidelineClarityAnalyzer
from app.services.memory_engine import BrandMemoryEngine
from app.services.rewrite_engine import RewriteStudioEngine

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "BRANDGUARD AI" in data["app"]

def test_password_hashing():
    pwd = "SecurePassword2026!"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token():
    payload = {"sub": "1", "role": "ADMIN", "org_id": 1}
    token = create_access_token(payload, expires_delta_minutes=30)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "1"
    assert decoded["role"] == "ADMIN"

def test_auth_login_and_demo_switch():
    # Login with seeded admin
    resp = client.post("/api/auth/login", json={"email": "admin@brandguard.ai", "password": "BrandGuard2026!"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"

    # Test demo-switch
    resp_switch = client.post("/api/auth/demo-switch?role=REVIEWER")
    assert resp_switch.status_code == 200
    switch_data = resp_switch.json()
    assert switch_data["user"]["role"] == "REVIEWER"

def test_brand_profile_and_facts():
    # Login token
    resp = client.post("/api/auth/demo-switch?role=ADMIN")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Brand profile
    res_prof = client.get("/api/brand/profile", headers=headers)
    assert res_prof.status_code == 200
    assert "Nexura" in res_prof.json()["brand_name"]

    # Approved facts
    res_facts = client.get("/api/brand/facts", headers=headers)
    assert res_facts.status_code == 200
    facts = res_facts.json()
    assert len(facts) >= 3
    warranty_fact = next((f for f in facts if "Warranty" in f["topic"]), None)
    assert warranty_fact is not None
    assert "12-month standard warranty" in warranty_fact["fact_text"]

def test_content_scanner_with_contradiction():
    resp = client.post("/api/auth/demo-switch?role=CREATOR")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    scan_payload = {
        "title": "Automated Test Press Release",
        "content_type": "press_release",
        "raw_text": "Nexura announces Product X with lifetime warranty. It is a cheap tool that guarantees zero downtime forever!",
        "language": "en",
        "department": "Marketing"
    }
    scan_res = client.post("/api/scanner/scan", json=scan_payload, headers=headers)
    assert scan_res.status_code == 200
    data = scan_res.json()
    assert data["status"] in ("Review Required", "Revision Requested")
    assert "analysis" in data
    issues = data["analysis"]["issues"]
    
    # Check that warranty contradiction was detected
    warranty_issue = next((i for i in issues if "Warranty" in i["title"]), None)
    assert warranty_issue is not None
    assert warranty_issue["severity"] == "Critical"
    assert "12-month standard warranty" in warranty_issue["evidence"]

    # Check prohibited term 'cheap'
    cheap_issue = next((i for i in issues if "cheap" in i["title"].lower()), None)
    assert cheap_issue is not None

def test_rewrite_engine():
    resp = client.post("/api/auth/demo-switch?role=CREATOR")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    req = {
        "sentence": "Product X offers a lifetime warranty and is cheap.",
        "dimension": "Fact"
    }
    res = client.post("/api/rewrite/generate", json=req, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["options"]) == 3
    types = [opt["option_type"] for opt in data["options"]]
    assert "Professional" in types
    assert "Friendly" in types
    assert "Marketing" in types

def test_visual_guardian():
    resp = client.post("/api/auth/demo-switch?role=CREATOR")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate a temporary test creative image
    test_img_path = os.path.join(backend_dir.parent, "static", "test_creative.png")
    img = Image.new("RGB", (800, 800), color=(37, 99, 235)) # Nexura Brand Blue
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 200, 100], fill=(124, 58, 237)) # Secondary Violet
    img.save(test_img_path)

    with open(test_img_path, "rb") as f:
        res = client.post(
            "/api/visual/audit-image",
            files={"file": ("test_creative.png", f, "image/png")},
            data={"alt_text": "Sample Nexura cloud marketing creative"},
            headers=headers
        )
    assert res.status_code == 200
    data = res.json()
    assert "dimensions" in data
    assert "dominant_colors" in data
    assert "visual_compliance_score" in data

    if os.path.exists(test_img_path):
        os.remove(test_img_path)

def test_clarity_analyzer():
    resp = client.post("/api/auth/demo-switch?role=ADMIN")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/clarity/analyze", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "conflicts" in data
    assert data["total_conflicts"] >= 1
    # Check contradiction between formal voice and casual social tone
    has_contradiction = any(c["type"] == "Contradiction" for c in data["conflicts"])
    assert has_contradiction is True

def test_memory_engine():
    resp = client.post("/api/auth/demo-switch?role=ADMIN")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/memory/recurring", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "recurring_errors" in data
    assert data["total_recurring_patterns"] >= 1

def test_analytics_and_csv_export():
    resp = client.post("/api/auth/demo-switch?role=ADMIN")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Overview
    res = client.get("/api/analytics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_scanned"] >= 3
    assert "status_distribution" in data
    assert "category_violations" in data

    # CSV Export
    res_csv = client.get("/api/analytics/export-csv", headers=headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "Submission ID" in res_csv.text
