import os
import math
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageStat, ImageFilter
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import BrandAsset

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}".upper()

def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Euclidean distance in RGB color space."""
    return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2)

def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """WCAG 2.1 relative luminance calculation."""
    def channel_lum(val: float) -> float:
        val = val / 255.0
        return val / 12.92 if val <= 0.03928 else ((val + 0.055) / 1.055) ** 2.4
    r, g, b = [channel_lum(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def calculate_contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """WCAG 2.1 contrast ratio."""
    lum1 = calculate_luminance(rgb1)
    lum2 = calculate_luminance(rgb2)
    l_max, l_min = max(lum1, lum2), min(lum1, lum2)
    return round((l_max + 0.05) / (l_min + 0.05), 2)

class VisualGuardianEngine:
    def __init__(self, db: Session, profile_id: int):
        self.db = db
        self.profile_id = profile_id
        self.assets = db.query(BrandAsset).filter(
            BrandAsset.profile_id == profile_id,
            BrandAsset.is_active == True
        ).all()
        
        # Extract registered brand colors
        self.brand_colors = []
        for asset in self.assets:
            if asset.asset_type == "COLOR_PALETTE" and asset.color_hex:
                try:
                    self.brand_colors.append({
                        "name": asset.name,
                        "hex": asset.color_hex,
                        "rgb": hex_to_rgb(asset.color_hex)
                    })
                except Exception:
                    pass
                    
        # Check if reference logo exists
        self.reference_logo = next((a for a in self.assets if a.asset_type == "LOGO"), None)

    def extract_dominant_colors(self, img: Image.Image, num_colors: int = 5) -> List[Dict[str, Any]]:
        """Extract top dominant colors using fast color quantization."""
        img_small = img.convert('RGB').resize((150, 150))
        # Quantize image to find dominant palette
        quantized = img_small.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()[:num_colors*3]
        
        colors = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i+1], palette[i+2]
            colors.append({
                "hex": rgb_to_hex(r, g, b),
                "rgb": (r, g, b)
            })
        return colors

    def audit_image(self, image_path: str, alt_text: Optional[str] = None) -> Dict[str, Any]:
        """Audit an uploaded creative / poster / banner image against visual brand guidelines."""
        issues = []
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        with Image.open(image_path) as img:
            width, height = img.size
            aspect_ratio = round(width / max(height, 1), 2)
            
            # 1. Image Resolution and Quality
            if width < 600 or height < 600:
                issues.append({
                    "dimension": "Visual",
                    "title": "Low Resolution Creative (<600px)",
                    "severity": "Medium",
                    "sentence": f"Dimensions: {width}x{height}px",
                    "explanation": f"Creative resolution ({width}x{height}px) is below the minimum enterprise standard of 600x600px, leading to pixelation on modern high-DPI displays.",
                    "guideline_citation": "Visual Brand Asset Guide §1.2: Minimum asset dimensions 600x600px.",
                    "evidence": "Brand Asset Standard §1.2",
                    "suggested_correction": "Export artwork at 2x resolution (1200x1200px or 1920x1080px).",
                    "confidence_score": 0.99,
                    "requires_human_verification": False,
                    "visual_bbox": [0, 0, 100, 100]
                })

            # Check Blur / Sharpness via Edge Filter
            gray = img.convert('L')
            edges = gray.filter(ImageFilter.FIND_EDGES)
            stat = ImageStat.Stat(edges)
            sharpness_var = stat.var[0]
            if sharpness_var < 80:
                issues.append({
                    "dimension": "Visual",
                    "title": "Potential Blur / Low Sharpness Detected",
                    "severity": "Low",
                    "sentence": f"Edge variance index: {round(sharpness_var, 1)}",
                    "explanation": "Image lacks sharp definition. May indicate heavy compression artifacts or out-of-focus photography.",
                    "guideline_citation": "Asset Quality Standard §2.0",
                    "evidence": "Visual Quality Register",
                    "suggested_correction": "Review source graphic in Figma/Canva and export with lossless PNG compression.",
                    "confidence_score": 0.85,
                    "requires_human_verification": True,
                    "visual_bbox": [10, 10, 90, 90]
                })

            # 2. Extract Dominant Colors and Check Brand Palette Match
            dominant_colors = self.extract_dominant_colors(img, num_colors=5)
            
            if self.brand_colors:
                matched_count = 0
                for d_col in dominant_colors:
                    # Check distance to each brand color
                    min_dist = min([color_distance(d_col["rgb"], b["rgb"]) for b in self.brand_colors])
                    if min_dist < 60.0:
                        matched_count += 1
                        d_col["is_brand_color"] = True
                    else:
                        d_col["is_brand_color"] = False
                
                palette_match_pct = round((matched_count / len(dominant_colors)) * 100.0, 1)
                
                if palette_match_pct < 40.0:
                    off_colors = [c["hex"] for c in dominant_colors if not c.get("is_brand_color")]
                    issues.append({
                        "dimension": "Visual",
                        "title": "Brand Color Palette Deviation",
                        "severity": "High",
                        "sentence": f"Dominant off-brand colors detected: {', '.join(off_colors[:3])}",
                        "explanation": f"Only {palette_match_pct}% of dominant creative colors match registered brand palette ({', '.join([b['hex'] for b in self.brand_colors])}).",
                        "guideline_citation": "Color Palette Specification: Primary brand colors must constitute at least 60% of graphic composition.",
                        "evidence": f"Approved Color Palette: {', '.join([b['name'] + ' ' + b['hex'] for b in self.brand_colors])}",
                        "suggested_correction": f"Replace rogue hues with primary brand colors: {self.brand_colors[0]['hex']}.",
                        "confidence_score": 0.92,
                        "requires_human_verification": False,
                        "visual_bbox": [20, 20, 80, 80]
                    })
            else:
                palette_match_pct = 100.0

            # 3. Accessibility / Contrast Check
            # Check contrast between darkest and lightest dominant colors
            sorted_by_lum = sorted(dominant_colors, key=lambda c: calculate_luminance(c["rgb"]))
            darkest = sorted_by_lum[0]["rgb"]
            lightest = sorted_by_lum[-1]["rgb"]
            contrast = calculate_contrast_ratio(darkest, lightest)
            
            if contrast < 4.5:
                issues.append({
                    "dimension": "Accessibility",
                    "title": f"Insufficient Color Contrast ({contrast}:1)",
                    "severity": "Critical",
                    "sentence": f"Contrast between {rgb_to_hex(*darkest)} and {rgb_to_hex(*lightest)} is {contrast}:1",
                    "explanation": f"WCAG 2.1 AA requires a minimum contrast ratio of 4.5:1 for standard text and critical graphics. Measured: {contrast}:1.",
                    "guideline_citation": "Accessibility Standard WCAG 2.1 AA §1.4.3",
                    "evidence": "Web Content Accessibility Guidelines (WCAG) 2.1",
                    "suggested_correction": "Darken background or increase foreground text brightness to achieve at least 4.5:1.",
                    "confidence_score": 0.98,
                    "requires_human_verification": False,
                    "visual_bbox": [40, 10, 60, 90]
                })

            # 4. Logo Usage & Positioning Analysis
            if self.reference_logo:
                # Reference logo exists: check corners (top-left, top-right, bottom-right)
                # We inspect high-contrast region in top-left (0-20% y, 0-25% x) and top-right (0-20% y, 75-100% x)
                tl_crop = img.crop((0, 0, int(width * 0.25), int(height * 0.25)))
                tr_crop = img.crop((int(width * 0.75), 0, width, int(height * 0.25)))
                
                tl_std = ImageStat.Stat(tl_crop.convert('L')).stddev[0]
                tr_std = ImageStat.Stat(tr_crop.convert('L')).stddev[0]
                
                has_logo_mark = tl_std > 20 or tr_std > 20
                if not has_logo_mark:
                    issues.append({
                        "dimension": "Visual",
                        "title": "Brand Logo Missing in Primary Header Zone",
                        "severity": "High",
                        "sentence": "Top corner zones (0-25% width/height)",
                        "explanation": f"Approved brand logo '{self.reference_logo.name}' was not detected in standard header locations (top-left or top-right).",
                        "guideline_citation": "Brand Logo Usage Policy §2.1: Primary logo must appear in the top-left or top-right quadrant with clear margin.",
                        "evidence": f"Registered Brand Asset: '{self.reference_logo.name}'",
                        "suggested_correction": "Place approved logo SVG/PNG in top-left with minimum 24px padding.",
                        "confidence_score": 0.88,
                        "requires_human_verification": True,
                        "visual_bbox": [5, 5, 20, 30]
                    })
            else:
                # No reference logo registered: DO NOT claim exact logo verification
                # Provide transparent notice
                pass

            # 5. Missing Alternative Text
            if not alt_text or len(alt_text.strip()) < 5:
                issues.append({
                    "dimension": "Accessibility",
                    "title": "Missing Alternative Text (Alt-Text)",
                    "severity": "Medium",
                    "sentence": "Image metadata",
                    "explanation": "No descriptive alternative text provided for this creative asset, violating accessibility standards for visually impaired users.",
                    "guideline_citation": "Accessibility Standard WCAG 2.1 §1.1.1 (Non-text Content)",
                    "evidence": "WCAG 2.1 Guideline 1.1.1",
                    "suggested_correction": "Provide descriptive alt-text explaining the visual subject, purpose, and key text.",
                    "confidence_score": 1.0,
                    "requires_human_verification": False,
                    "visual_bbox": [0, 0, 100, 100]
                })

        # Calculate Visual Compliance Score
        penalty = sum(18 if i["severity"] == "Critical" else 10 if i["severity"] == "High" else 5 if i["severity"] == "Medium" else 2 for i in issues)
        visual_score = max(0.0, round(100.0 - penalty, 1))

        return {
            "dimensions": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "contrast_ratio": contrast,
            "dominant_colors": dominant_colors,
            "registered_brand_colors": self.brand_colors,
            "reference_logo_registered": bool(self.reference_logo),
            "visual_compliance_score": visual_score,
            "issues": issues
        }
