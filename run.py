import os
import sys

# Ensure backend directory is in sys.path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("  BRANDGUARD AI — Intelligent Brand Governance & Content Intelligence")
    print("  Tagline: Every Message Matters. Every Brand Deserves Consistency.")
    print("  URL: http://127.0.0.1:8000")
    print("  API Docs: http://127.0.0.1:8000/docs")
    print("=" * 65)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
