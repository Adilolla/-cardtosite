import os
import argparse
import pathlib
import json
import re
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
except ImportError:
    raise SystemExit("Please install: pip install google-generativeai")

MODEL = "models/gemini-2.5-flash"

PROMPT = """
You are a brand-aware vision assistant. Given a business card image:

1) Extract structured fields as strict JSON:
{
  "name": null | string,
  "title": null | string,
  "company": null | string,
  "email": null | string,
  "phone": null | string,
  "website": null | string,
  "address": null | string,
  "palette_hex": [ "#RRGGBB", "#RRGGBB" ]
}

2) Return ONLY the JSON. No prose. If unsure, use null.
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{company}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ 
      margin: 0; 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
      background: {bg}; 
      color: {fg}; 
      line-height: 1.6;
    }}
    .header {{ 
      background: linear-gradient(135deg, {primary} 0%, {primary_dark} 100%);
      color: white; 
      padding: 80px 20px; 
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    .header h1 {{ 
      margin: 0; 
      font-size: clamp(32px, 5vw, 52px);
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header p {{ 
      margin: 15px 0 0; 
      font-size: clamp(16px, 3vw, 22px);
      opacity: 0.95;
      font-weight: 300;
    }}
    .content {{ 
      max-width: 900px; 
      margin: 50px auto; 
      padding: 0 20px; 
    }}
    .card {{ 
      background: white; 
      padding: 35px; 
      margin: 25px 0; 
      border-radius: 16px; 
      box-shadow: 0 2px 16px rgba(0,0,0,0.08);
      border-left: 5px solid {primary};
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }}
    .card h2 {{ 
      margin: 0 0 12px; 
      color: {primary}; 
      font-size: 22px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .card p {{ 
      margin: 0; 
      line-height: 1.7;
      font-size: 17px;
      color: #374151;
    }}
    .card a {{
      color: {primary};
      text-decoration: none;
      word-break: break-all;
      transition: opacity 0.2s;
    }}
    .card a:hover {{
      opacity: 0.8;
      text-decoration: underline;
    }}
    .footer {{
      text-align: center;
      padding: 50px 20px;
      color: #6b7280;
      font-size: 14px;
    }}
    .icon {{
      display: inline-block;
      font-size: 24px;
    }}
    @media (max-width: 640px) {{
      .header {{ padding: 60px 15px; }}
      .card {{ padding: 25px; margin: 15px 0; }}
      .content {{ margin: 30px auto; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{company}</h1>
    <p>{title}</p>
  </div>
  <div class="content">
    {cards}
  </div>
  <div class="footer">
    <p>Generated with Card→Site ✨</p>
  </div>
</body>
</html>"""


def darken_color(hex_color: str, factor: float = 0.7) -> str:
    """Darken a hex color by a factor (0-1)."""
    hex_color = hex_color.lstrip('#')
    try:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        return "#1e40af"  # Fallback dark blue


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text, handling markdown code blocks."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON in markdown code block
    patterns = [
        r'```json\s*(\{[\s\S]*?\})\s*```',
        r'```\s*(\{[\s\S]*?\})\s*```',
        r'(\{[\s\S]*\})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    
    raise ValueError("Could not extract valid JSON from response")


def main():
    ap = argparse.ArgumentParser(
        description='Generate a website from a business card image',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--image", 
        default="/Users/adityalolla/Desktop/projects/business_card.webp",
        help="Path to business card image"
    )
    ap.add_argument(
        "--output",
        default="/Users/adityalolla/Desktop/projects/index.html",
        help="Output HTML file path"
    )
    ap.add_argument(
        "--api-key",
        default=None,
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )
    args = ap.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv('GEMINI_API_KEY') or "AIzaSyAVqJceLXpzd0T3-e3PTwzu_pJnhCazmg0"
    
    if not api_key:
        raise SystemExit("Error: No API key provided. Use --api-key or set GEMINI_API_KEY environment variable")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL)

    img_path = pathlib.Path(args.image)
    if not img_path.exists():
        raise SystemExit(f"Image not found: {img_path}")

    print("Uploading image...")
    file_ref = genai.upload_file(str(img_path))

    print("Analyzing card...")
    resp = model.generate_content([PROMPT.strip(), file_ref], request_options={"timeout": 90})

    # Parse response
    try:
        data = extract_json_from_text(resp.text)
    except ValueError as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {resp.text[:200]}...")
        raise SystemExit("Failed to extract JSON from API response")

    # Extract fields with fallbacks
    name = data.get("name") or ""
    title = data.get("title") or ""
    company = data.get("company") or name or "Business Card"
    email = data.get("email") or ""
    phone = data.get("phone") or ""
    website = data.get("website") or ""
    address = data.get("address") or ""
    palette = data.get("palette_hex", [])

    # Color scheme
    primary = palette[0] if palette else "#2563eb"
    primary_dark = darken_color(primary, 0.7)
    bg = palette[1] if len(palette) > 1 else "#f9fafb"
    fg = "#111827"

    # Ensure website has protocol
    if website and not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    # Build contact cards
    cards = ""
    card_configs = [
        (email, "📧", "Email", f'<a href="mailto:{email}">{email}</a>'),
        (phone, "📞", "Phone", f'<a href="tel:{phone.replace(" ", "").replace("-", "")}">{phone}</a>'),
        (website, "🌐", "Website", f'<a href="{website}" target="_blank" rel="noopener">{website}</a>'),
        (address, "📍", "Address", address),
    ]

    for value, icon, label, content in card_configs:
        if value:
            cards += f'''
    <div class="card">
      <h2><span class="icon">{icon}</span> {label}</h2>
      <p>{content}</p>
    </div>'''

    if not cards:
        cards = '<div class="card"><h2>Contact Information</h2><p>See business card for details.</p></div>'

    # Generate HTML
    html_out = HTML_TEMPLATE.format(
        company=company,
        title=title or "Professional Services",
        primary=primary,
        primary_dark=primary_dark,
        bg=bg,
        fg=fg,
        cards=cards
    )

    # Write output
    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")

    print(f"Done! File saved to: {out_path}")
    print(f"\nExtracted information:")
    print(f"  Company: {company}")
    if title:
        print(f"  Title: {title}")
    if email:
        print(f"  Email: {email}")
    if phone:
        print(f"  Phone: {phone}")
    if website:
        print(f"  Website: {website}")


if __name__ == "__main__":
    main()