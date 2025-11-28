import os, json, re, html as h, pathlib
import google.generativeai as genai

MODEL = "models/gemini-2.5-flash"
PROMPT = """You are a brand-aware vision assistant. Given a business card image:
Return ONLY strict JSON: {"name":null|string,"title":null|string,"company":null|string,
"email":null|string,"phone":null|string,"website":null|string,"address":null|string,
"palette_hex":["#RRGGBB","#RRGGBB"]}"""

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>{company}</title><style>
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif;background:{bg};color:{fg};}}
.header{{background:{primary};color:#fff;padding:56px 20px;text-align:center}}
.header h1{{margin:0;font-size:44px}} .header p{{margin:10px 0 0;font-size:18px}}
.content{{max-width:880px;margin:32px auto;padding:0 16px}}
.card{{background:#fff;padding:20px;margin:16px 0;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.06)}}
.card h2{{margin:0 0 12px;color:{primary}}} a{{color:{primary}}}
</style></head><body>
<div class="header"><h1>{company}</h1><p>{title}</p></div>
<div class="content">{cards}</div></body></html>"""

def _palette(p):
    if not p or not isinstance(p, list): p = ["#2563eb", "#f3f4f6"]
    primary = p[0]; bg = p[1] if len(p) > 1 else "#f3f4f6"; fg = "#111827"
    return primary, bg, fg

def generate_html_from_card(image_path: str, model_name: str = MODEL) -> str:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name)

    img_path = pathlib.Path(image_path)
    file_ref = genai.upload_file(str(img_path))
    resp = model.generate_content([PROMPT, file_ref], request_options={"timeout": 90})

    try:
        data = json.loads(resp.text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", resp.text)
        data = json.loads(m.group(0)) if m else {}

    name    = (data.get("name") or "")
    title   = (data.get("title") or "")
    company = (data.get("company") or name or "Business Card")
    email   = (data.get("email") or "")
    phone   = (data.get("phone") or "")
    website = (data.get("website") or "")
    address = (data.get("address") or "")
    palette = data.get("palette_hex", [])

    primary, bg, fg = _palette(palette)

    cards = ""
    if email:   cards += f'<div class="card"><h2>Email</h2><p><a href="mailto:{h.escape(email)}">{h.escape(email)}</a></p></div>'
    if phone:   cards += f'<div class="card"><h2>Phone</h2><p><a href="tel:{h.escape(phone).replace(" ","")}">{h.escape(phone)}</a></p></div>'
    if website:
        href = website if website.startswith("http") else "https://" + website
        cards += f'<div class="card"><h2>Website</h2><p><a href="{h.escape(href)}">{h.escape(website)}</a></p></div>'
    if address: cards += f'<div class="card"><h2>Address</h2><p>{h.escape(address)}</p></div>'
    if not cards:
        cards = '<div class="card"><h2>Info</h2><p>Details will appear here.</p></div>'

    return HTML.format(company=h.escape(company), title=h.escape(title),
                       primary=primary, bg=bg, fg=fg, cards=cards)
