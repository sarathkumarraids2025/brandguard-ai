import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
FRONTEND_PUB = os.path.join(os.path.dirname(__file__), "frontend", "public")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(FRONTEND_PUB, exist_ok=True)

def create_hero_background():
    """Generate high-resolution (2400x1350) project-relevant hero background image."""
    width, height = 2400, 1350
    img = Image.new("RGB", (width, height), color=(10, 15, 30))
    draw = ImageDraw.Draw(img)

    # 1. Smooth gradient background (Deep Slate -> Cyber Indigo -> Royal Blue -> Midnight Violet)
    for y in range(height):
        ratio = y / height
        r = int(12 * (1 - ratio) + 20 * math.sin(ratio * math.pi) + 15 * ratio)
        g = int(18 * (1 - ratio) + 25 * math.sin(ratio * math.pi) + 22 * ratio)
        b = int(38 * (1 - ratio) + 85 * math.sin(ratio * math.pi) + 60 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Glowing Orb Accents in Brand Colors (#2563EB, #7C3AED, #06B6D4)
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    # Cyan Glow top-right
    for rad in range(600, 50, -30):
        alpha = int(18 * (1 - rad / 600))
        glow_draw.ellipse([width - 800 - rad, 100 - rad, width - 800 + rad, 100 + rad], fill=(6, 182, 212, alpha))

    # Royal Blue Glow center
    for rad in range(900, 50, -40):
        alpha = int(22 * (1 - rad / 900))
        glow_draw.ellipse([width // 2 - rad, height // 2 - rad, width // 2 + rad, height // 2 + rad], fill=(37, 99, 235, alpha))

    # Violet Glow bottom-left
    for rad in range(700, 50, -30):
        alpha = int(24 * (1 - rad / 700))
        glow_draw.ellipse([200 - rad, height - 300 - rad, 200 + rad, height - 300 + rad], fill=(124, 58, 237, alpha))

    img = Image.alpha_composite(img.convert("RGBA"), glow_layer).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 3. Perspective Cyber Grid / Brand Architecture Matrix
    grid_color = (255, 255, 255, 12)
    horizon_y = int(height * 0.55)
    
    # Horizontal grid lines with perspective spacing
    for i in range(18):
        y = horizon_y + int(math.pow(i / 18.0, 2.2) * (height - horizon_y))
        draw.line([(0, y), (width, y)], fill=(40, 70, 130))

    # Perspective vertical rays converging toward upper center
    center_x = width // 2
    for x in range(-width // 2, width * 3 // 2, 80):
        draw.line([(center_x, horizon_y - 200), (x, height)], fill=(35, 65, 120))

    # 4. Digital Nodes & Constellation of Brand Governance
    nodes = [
        (400, 300), (600, 220), (850, 350), (1100, 240), (1400, 280), (1700, 180),
        (1950, 320), (2150, 250), (520, 500), (800, 580), (1200, 520), (1600, 560),
        (1850, 480), (300, 750), (700, 800), (1150, 780), (1550, 820), (2000, 760)
    ]
    # Connect nearby nodes
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes):
            if i < j:
                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < 380:
                    draw.line([(x1, y1), (x2, y2)], fill=(45, 90, 180), width=1)

    for (x, y) in nodes:
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(6, 182, 212))
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255))

    # 5. Floating Geometric Shield & Holographic Brand Cards in Background
    # Central Brand Shield silhouette
    sx, sy = width // 2, int(height * 0.42)
    shield_pts = [
        (sx - 180, sy - 140),
        (sx + 180, sy - 140),
        (sx + 180, sy + 40),
        (sx, sy + 180),
        (sx - 180, sy + 40)
    ]
    draw.polygon(shield_pts, outline=(37, 99, 235), width=3)
    draw.polygon([(p[0], p[1]) for p in shield_pts], outline=(6, 182, 212), width=1)

    # Save to both static and frontend public
    out_static = os.path.join(STATIC_DIR, "hero-bg.jpg")
    out_pub = os.path.join(FRONTEND_PUB, "hero-bg.jpg")
    img.save(out_static, "JPEG", quality=92)
    img.save(out_pub, "JPEG", quality=92)
    print(f"[Assets] Created 4K Hero Background: {out_static}")

def create_brand_logo():
    """Create BrandGuard AI shield logo PNG."""
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gradient-like circular badge
    cx, cy = 256, 256
    for r in range(240, 200, -1):
        alpha = int(255 * (r - 200) / 40)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(37, 99, 235, 30))

    # Main Shield Shape
    shield = [
        (120, 100), (392, 100), (392, 280), (256, 420), (120, 280)
    ]
    draw.polygon(shield, fill=(26, 40, 80, 240), outline=(6, 182, 212, 255), width=6)

    # Inner check / intelligence mark
    draw.line([(180, 240), (235, 310)], fill=(16, 185, 129, 255), width=16)
    draw.line([(235, 310), (345, 170)], fill=(16, 185, 129, 255), width=16)

    # Nodes
    draw.ellipse([250, 120, 262, 132], fill=(6, 182, 212, 255))
    draw.ellipse([150, 160, 162, 172], fill=(124, 58, 237, 255))
    draw.ellipse([360, 160, 372, 172], fill=(124, 58, 237, 255))

    out_static = os.path.join(STATIC_DIR, "logo.png")
    out_pub = os.path.join(FRONTEND_PUB, "logo.png")
    img.save(out_static, "PNG")
    img.save(out_pub, "PNG")
    print(f"[Assets] Created Brand Logo: {out_static}")

def create_sample_creatives():
    """Create sample creatives for Visual Guardian demo."""
    # 1. Compliant Creative
    c1 = Image.new("RGB", (800, 800), color=(15, 23, 42))
    d1 = ImageDraw.Draw(c1)
    # Header zone in brand royal blue (#2563EB)
    d1.rectangle([0, 0, 800, 160], fill=(37, 99, 235))
    # Brand logo placeholder in top-left
    d1.rectangle([40, 40, 180, 120], fill=(255, 255, 255), outline=(6, 182, 212), width=3)
    # High contrast card in white (#FFFFFF)
    d1.rectangle([60, 220, 740, 720], fill=(255, 255, 255))
    # Brand headline in deep navy (Contrast > 12:1)
    d1.rectangle([100, 280, 700, 320], fill=(15, 23, 42))
    d1.rectangle([100, 360, 500, 385], fill=(71, 85, 105))
    d1.rectangle([100, 410, 620, 435], fill=(71, 85, 105))
    # Brand button in violet (#7C3AED)
    d1.rectangle([100, 520, 340, 590], fill=(124, 58, 237))

    c1_path = os.path.join(STATIC_DIR, "sample_creative_compliant.png")
    c1.save(c1_path, "PNG")

    # 2. Creative with intentional Brand Violations
    # Low resolution (450x450), off-brand orange/yellow colors, low contrast ratio
    c2 = Image.new("RGB", (450, 450), color=(255, 248, 220)) # Light beige
    d2 = ImageDraw.Draw(c2)
    # Off-brand orange header (#FF6600)
    d2.rectangle([0, 0, 450, 100], fill=(255, 102, 0))
    # Low contrast yellow text box on light beige background (Contrast ~1.6:1!)
    d2.rectangle([40, 160, 410, 240], fill=(255, 235, 100))
    # Random magenta off-brand shapes
    d2.ellipse([60, 280, 200, 420], fill=(255, 0, 128))
    # No logo in top-left quadrant

    c2_path = os.path.join(STATIC_DIR, "sample_creative_violation.png")
    c2.save(c2_path, "PNG")

    print("[Assets] Created sample creatives for Visual Guardian testing.")

if __name__ == "__main__":
    create_hero_background()
    create_brand_logo()
    create_sample_creatives()
