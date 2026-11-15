import os
import re
import socket
import urllib.parse
from typing import Tuple, Optional
import pypdf
import docx
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image

def is_safe_url(url: str) -> Tuple[bool, str]:
    """Validate URL against SSRF and private IP address attacks."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, "Only HTTP and HTTPS protocols are permitted."
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid host in URL."
            
        # Check against blacklisted hostnames
        forbidden_names = {"localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal"}
        if hostname.lower() in forbidden_names or hostname.endswith(".local") or hostname.endswith(".internal"):
            return False, "Access to internal hosts is strictly forbidden."

        # Resolve IP to check for private or link-local ranges
        ip = socket.gethostbyname(hostname)
        parts = list(map(int, ip.split('.')))
        
        # Check private networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16)
        if parts[0] == 10:
            return False, "Private IP addresses are restricted."
        if parts[0] == 127:
            return False, "Loopback addresses are restricted."
        if parts[0] == 169 and parts[1] == 254:
            return False, "Link-local cloud metadata addresses are restricted."
        if parts[0] == 172 and (16 <= parts[1] <= 31):
            return False, "Private IP addresses are restricted."
        if parts[0] == 192 and parts[1] == 168:
            return False, "Private IP addresses are restricted."
            
        return True, "Safe URL"
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"

def extract_from_url(url: str, timeout: int = 5) -> Tuple[str, str]:
    """Safely fetch and extract clean main text from a web page."""
    safe, msg = is_safe_url(url)
    if not safe:
        raise ValueError(msg)
        
    headers = {"User-Agent": "BRANDGUARD-AI-Bot/2.0 (+https://brandguard.ai)"}
    resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=False)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    for script_or_style in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        script_or_style.decompose()
        
    title = soup.title.string.strip() if soup.title and soup.title.string else "Web Document"
    text = soup.get_text(separator="\n", strip=True)
    clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return title, clean_text[:20000]

def extract_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pypdf."""
    text_content = []
    reader = pypdf.PdfReader(file_path)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_content.append(extracted)
    return "\n".join(text_content).strip()

def extract_from_docx(file_path: str) -> str:
    """Extract text from DOCX document."""
    doc = docx.Document(file_path)
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            lines.append(" | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()]))
    return "\n".join(lines).strip()

def extract_from_csv(file_path: str) -> str:
    """Extract content from CSV file."""
    df = pd.read_csv(file_path)
    # Convert first few columns/rows to structured text
    summary = []
    summary.append(f"Columns: {', '.join(df.columns)}")
    for idx, row in df.head(50).iterrows():
        row_str = " ; ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
        summary.append(row_str)
    return "\n".join(summary)

def extract_from_file(file_path: str) -> str:
    """Detect file type and extract textual contents."""
    ext = os.path.splitext(file_path)[1].lower().lstrip(".")
    if ext == "pdf":
        return extract_from_pdf(file_path)
    elif ext in ("docx", "doc"):
        return extract_from_docx(file_path)
    elif ext == "csv":
        return extract_from_csv(file_path)
    elif ext in ("txt", "md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        # Generic fallback
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
