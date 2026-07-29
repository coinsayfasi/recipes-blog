#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tabserve blog — AI ile ÖZGÜN, tam-SEO yazı üretici (Claude API, stdlib).
Kurallar: hedef anahtar kelime=title=H1; H2→H3→H4(→H5); 600+ KELİME; özgün (spin değil);
app CTA + internal link; Article schema. Doğrulama geçmezse YAYINLAMAZ.
Kullanım:
  ANTHROPIC_API_KEY=... python _gen/generate.py            # 1 yeni yazı üret+yayınla
  python _gen/generate.py --rebuild                         # API'siz: listeleme+sitemap yeniden kur
Env: ANTHROPIC_API_KEY, BLOG_MODEL (ops, varsayılan claude-sonnet-4-6), BLOG_COUNT (ops)."""
import os, re, sys, json, html, time, datetime, urllib.request, urllib.error, urllib.parse
from pathlib import Path

SOCIAL = [("YouTube","https://youtube.com/@tabserve"),("Instagram","https://instagram.com/tabservee"),
          ("TikTok","https://tiktok.com/@tabserve"),("Pinterest","https://pinterest.com/nedir_nasil")]

def _svg(d): return f'<svg viewBox="0 0 24 24" width="19" height="19" fill="currentColor" aria-hidden="true"><path d="{d}"/></svg>'
ICON = {
 "X":_svg("M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"),
 "f":_svg("M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"),
 "P":_svg("M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"),
 "W":_svg("M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51l-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.71.306 1.263.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884"),
 "in":_svg("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.848 3.37-1.848 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"),
 "YouTube":_svg("M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"),
 "Instagram":_svg("M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069M12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12s.014 3.668.072 4.948c.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24s3.668-.014 4.948-.072c4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948s-.014-3.667-.072-4.947c-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0m0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324M12 16a4 4 0 110-8 4 4 0 010 8m6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881"),
 "TikTok":_svg("M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"),
 "Bluesky":_svg("M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.267-4.308 1.172-6.498-2.74-7.078 2.67.297 5.568-.628 6.383-3.364.246-.828.624-5.79.624-6.478 0-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3 1.24C16.046 4.748 13.087 8.687 12 10.8Z"),
}
ICON["Pinterest"] = ICON["P"]

COOKIE_BANNER = '''<div id="cookie-banner" style="display:none;position:fixed;left:0;right:0;bottom:0;z-index:60;background:#ffffff;border-top:1px solid #ece8e1;box-shadow:0 -6px 24px rgba(31,39,51,.08);padding:14px 18px;font-size:13.5px;color:#384250;line-height:1.5">
  <div style="max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">
    <span>We use cookies for analytics and advertising (incl. Google AdSense). See our <a href="/cookies.html" style="color:#2f6bff">Cookie Policy</a>.</span>
    <span><button onclick="cookieOK(0)" style="background:none;border:1px solid #d5d9e0;color:#384250;padding:7px 14px;border-radius:9px;cursor:pointer;margin-right:8px">Reject</button><button onclick="cookieOK(1)" style="background:linear-gradient(110deg,#2f6bff,#8b5cf6);border:0;color:#fff;padding:7px 16px;border-radius:9px;cursor:pointer;font-weight:600">Accept</button></span>
  </div>
</div>
<script>(function(){try{if(!localStorage.getItem("cookie_consent"))document.getElementById("cookie-banner").style.display="block";}catch(e){}})();
function cookieOK(v){try{localStorage.setItem("cookie_consent",v?"accepted":"rejected");}catch(e){}if(window.__grantConsent)__grantConsent(!!v);document.getElementById("cookie-banner").style.display="none";}</script>'''


def post_extras(url, title):
    """Alt paylaş çubuğu + yazar kutusu + sol kayan çubuk (SVG ikonlu)."""
    u = urllib.parse.quote(url, safe=''); t = urllib.parse.quote(title, safe='')
    S = [("X",f"https://twitter.com/intent/tweet?url={u}&amp;text={t}"),("f",f"https://www.facebook.com/sharer/sharer.php?u={u}"),
         ("P",f"https://pinterest.com/pin/create/button/?url={u}&amp;description={t}"),("W",f"https://wa.me/?text={t}%20{u}"),
         ("in",f"https://www.linkedin.com/sharing/share-offsite/?url={u}")]
    lbl = {"X":"X","f":"Facebook","P":"Pinterest","W":"WhatsApp","in":"LinkedIn"}
    share = '<div class="share"><span>Share this post:</span>' + ''.join(
        f'<a class="ico" href="{h}" target="_blank" rel="noopener" aria-label="{lbl[n]}">{ICON[n]}</a>' for n,h in S) + '</div>'
    follow = ''.join(f'<a class="ico" href="{lu}" target="_blank" rel="noopener" aria-label="{ln}">{ICON.get(ln,ln)}</a>' for ln,lu in SOCIAL)
    author = ('<div class="author-box"><img class="ab-logo" src="/assets/logo.svg" alt="Aycan Merve Güneş" width="56" height="56">'
              f'<div class="ab-body"><b>Written by <a href="https://www.tabserve.com.tr/author.html">Aycan Merve Güneş</a></b>'
              f'<p style="color:var(--muted);font-size:13px;margin:2px 0 8px">Founder of {SITE_NAME}</p>'
              f'<p>Aycan tests every recipe on {SITE_NAME} at home before it\'s published — real ingredients, '
              f'real timing, no filler.</p><div class="follow"><span>Follow us:</span>{follow}</div></div></div>')
    rail = '<div class="share-rail" aria-label="Share this post">' + ''.join(
        f'<a href="{h}" target="_blank" rel="noopener" aria-label="{lbl[n]}">{ICON[n]}</a>' for n,h in S) + '</div>'
    return share + author, rail

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "_gen"
BLOG = ROOT / "blog"
TOPICS = json.loads((GEN / "topics.json").read_text(encoding="utf-8"))
POSTS_F = GEN / "posts.json"
STATE_F = GEN / "state.json"
SITE = "https://recipes.tabserve.com.tr"
SITE_NAME = "Simple Skillet"
# Sağlayıcı: GEMINI (ücretsiz) öncelikli; yoksa Claude.
# Fallback zinciri — bir model deprecate olursa sıradakini dener (routevia prod gemini-flash-latest kullanıyor).
GEMINI_CANDIDATES = [m for m in [
    os.environ.get("GEMINI_MODEL"), "gemini-flash-latest", "gemini-3.5-flash",
    "gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-pro-latest",
] if m]
CLAUDE_MODEL = os.environ.get("BLOG_MODEL", "claude-sonnet-4-6")
_gemini_ok = None  # çalıştığı doğrulanan model (cache)

APPS = {
 "recipes": {"tag":"Recipes", "cta":'<div class="appcta"><b>📌 Loved this recipe?</b><p>Save it to Pinterest so you can find it again next time you\'re planning dinner — and follow along for a new easy recipe a few times a week.</p><div class="appbadges"><a class="ghost" href="https://pinterest.com/nedir_nasil">Follow on Pinterest →</a></div></div>',
              "name":SITE_NAME,"one":"a home cooking blog with tested, no-fuss weeknight recipes"},
}

ALL_APPS_STRIP = ""


def load(p, d): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else d
def slugify(s): return re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")[:70]
def words(htmlstr): return len(re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",htmlstr)).split())

PROMPT = """You are an expert food blogger and recipe developer writing an ORIGINAL recipe article for {name}, {one}.

TARGET KEYWORD: "{kw}"
ANGLE: {angle}
A small "save to Pinterest" promo box is added automatically afterwards — just write the article body.

STRICT RULES — follow every one:
0. START the body with: <div class="tldr"><b>⚡ Quick summary</b><p>2-3 sentences: what this recipe is, why it works, and how long it takes total.</p></div>
0b. LENGTH: the body must total 2200-2800 words of real text (count WORDS, not characters) — this includes the intro, recipe card, and every section after it. Do NOT pad with fluff; add real value instead: more substitutions, more troubleshooting detail, more FAQ entries, a deeper "why this works" section. Use at least 5-7 <h2> sections AFTER the recipe card (not counting "Recipe Card" and "Key Takeaways" themselves) plus at least 4 <h3> subheadings total across the article (ingredient notes, variations, etc. can be <h3> under a <h2>).
1. The target keyword "{kw}" must appear in the TITLE and be the clear topic. The title doubles as the page H1 — do NOT output an <h1>. Title should read like a real recipe title (e.g. "Garlic Butter Baked Chicken Thighs (Crispy Skin)"). CRITICAL: the "title" field MUST be complete and between 40 and 58 characters total — never write a longer title expecting it to be cut off.
2. Right after the intro, add a "Key Takeaways" box with EXACTLY this structure:
<div class="quickfacts"><h2>Key Takeaways</h2><ul>
<li>...</li><li>...</li><li>...</li>
</ul></div>
(3-5 bullets: total time, difficulty, storage life, best pairing, or the #1 tip.)
3. Write 2-3 short intro paragraphs (why this recipe, what makes it work, a personal/practical note) BEFORE the recipe card — real cooking knowledge, no fluff.
4. Then insert the RECIPE CARD with EXACTLY this structure and these exact class/data-attribute names (fill in realistic values, times in "PT#M" ISO 8601 duration format for the data-attributes but human-readable text inside the visible tags):
<div class="recipe-card" data-prep="PT15M" data-cook="PT25M" data-total="PT40M" data-servings="4" data-category="{{Main Course/Side Dish/Dessert/Breakfast/etc}}" data-cuisine="{{American/Italian/Mexican/etc}}" data-calories="{{integer kcal per serving, realistic estimate}}">
<h2>Recipe Card</h2>
<p class="recipe-meta">Prep: 15 minutes · Cook: 25 minutes · Total: 40 minutes · Serves: 4</p>
<h3>Ingredients</h3>
<ul class="ingredients">
<li>1.5 lbs boneless chicken thighs</li>
<li>...(8-14 realistic ingredients with quantities)</li>
</ul>
<h3>Instructions</h3>
<ol class="instructions">
<li>...(6-10 clear numbered steps, each one real actionable instruction with time/temperature where relevant)</li>
</ol>
</div>
5. AFTER the recipe card, continue with 5-8 more <h2> sections covering: substitutions/variations, storage & reheating instructions, serving suggestions, make-ahead/freezer tips, and a <h2>Common Mistakes to Avoid</h2> (4-6 real mistakes with the fix, <ul>). Every section must add concrete value — exact temperatures, times, ratios, textures to look for.
6. Include ONE comparison <table> where it genuinely helps (e.g. ingredient swaps, cook-method comparison: Method | Time | Texture result | Best for).
7. End with an <h2>Frequently Asked Questions</h2> section: 6-8 LONG-TAIL cooking questions (can I freeze this, can I use X instead of Y, why did my X turn out Z) — each question as <h3>, its answer as a <p>. Then a short concluding paragraph.
8. ORIGINAL and specific — real, tested-sounding cooking guidance. Do NOT fabricate nutrition studies or brand claims. No repetition, no generic filler.
8b. BANNED phrases: "unforgettable", "life-changing", "you won't believe", "hidden gem", "look no further", "in today's world". Replace hype with concrete utility: exact temps, times, textures, substitution ratios.
9. Allowed body tags ONLY: h2, h3, h4, h5, p, ul, li, ol, strong, a, table, thead, tbody, tr, th, td, div (only for the two required div wrappers: tldr, quickfacts, recipe-card), and the class/data attributes specified above. No markdown, no <h1>, no <html>/<head>/<style>.
10. Include 1 outbound link to a GENUINELY AUTHORITATIVE source if genuinely relevant (e.g. USDA food safety temperature guide, or a relevant Wikipedia article on an ingredient/technique). Only use well-known, stable URLs you are confident exist — prefer https://en.wikipedia.org/wiki/<Topic> or https://www.fsis.usda.gov/. NEVER invent specific deep URLs. Place it naturally inside a sentence.
11. WRITE FOR A HUMAN READER FIRST, not for search engines. Vary sentence rhythm and structure between recipes — do not reuse the same phrasing patterns or section framing across different recipes. This site publishes many recipes; each one must read as independently written, not a variation of a template.
12. Where genuinely relevant, include first-hand-sounding practical detail (a specific texture/timing cue, a common mistake and why it happens, a nuance that only comes from actually cooking the dish) rather than generic textbook statements. Do not fabricate specific personal anecdotes — ground advice in concrete, verifiable specifics (exact temperatures/times, cause-and-effect reasoning) so it reads as real cooking expertise, not filler.

Output ONLY valid minified JSON (no code fences, no commentary), exactly these keys:
{{"title":"...","meta_description":"max 155 chars, includes the keyword, written like an appetizing recipe meta description","keywords":"4-6 comma-separated keywords","slug":"kebab-case-from-title","img_queries":["5 separate stock photo searches, 2-4 English words each, each matching a DIFFERENT section/step of the recipe (spread across the whole piece): 1) finished dish plated 2) key ingredient close-up 3) cooking action/process 4) another angle of finished dish 5) another concrete cooking scene (e.g. [\"baked chicken thighs plated\",\"raw chicken thighs seasoning\",\"searing chicken skillet\"])"],"body":"the article HTML"}}"""

def _post(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    for attempt in range(4):
        try:
            return json.loads(urllib.request.urlopen(req, timeout=90).read())
        except urllib.error.HTTPError as e:
            if e.code in (429,529,500,503) and attempt < 3:
                time.sleep(8*(attempt+1)); continue
            # Gerçek hata gövdesini logla — aksi halde "HTTP Error 400: Bad Request"
            # dışında hiçbir bilgi kalmıyor ve kök neden asla görülemiyor.
            try:
                detail = e.read().decode("utf-8", "replace")[:800]
            except Exception:
                detail = "(gövde okunamadı)"
            print(f"  ⚠️ API hata detayı ({e.code}): {detail}")
            raise
    raise RuntimeError("API başarısız")

def call_gemini(prompt, key):
    global _gemini_ok
    cands = ([_gemini_ok] if _gemini_ok else []) + [m for m in GEMINI_CANDIDATES if m != _gemini_ok]
    last = None
    for m in cands:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        try:
            r = _post(url, {"contents":[{"parts":[{"text":prompt}]}],
                            "generationConfig":{"maxOutputTokens":8192,"temperature":0.75,"thinkingConfig":{"thinkingBudget":0}}},
                      {"content-type":"application/json"})
            cands_out = r.get("candidates")
            if not cands_out or not cands_out[0].get("content",{}).get("parts"):
                last = RuntimeError(f"{m}: boş yanıt ({r.get('promptFeedback','')})"); continue
            _gemini_ok = m
            print(f"  (model: {m})")
            return cands_out[0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code in (404, 400):
                # 404: model deprecate/erişilemez. 400: bu modelin desteklemediği
                # bir istek alanı (örn. thinkingConfig) veya geçersiz model adı
                # olabilir — her iki durumda da sıradaki modeli dene, tüm işi
                # tek bir modelin uyumsuzluğu yüzünden çökertme.
                last = e; continue
            raise
    raise last or RuntimeError("hiçbir Gemini modeli çalışmadı")

def call_claude(prompt, key):
    r = _post("https://api.anthropic.com/v1/messages",
        {"model":CLAUDE_MODEL,"max_tokens":2600,"messages":[{"role":"user","content":prompt}]},
        {"x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"})
    return r["content"][0]["text"]

def call_llm(prompt):
    gk = os.environ.get("GEMINI_API_KEY")
    if gk: return call_gemini(prompt, gk)
    ck = os.environ.get("ANTHROPIC_API_KEY")
    if ck: return call_claude(prompt, ck)
    sys.exit("⚠️ GEMINI_API_KEY (ücretsiz) veya ANTHROPIC_API_KEY gerekli")

def parse_json(txt):
    txt = txt.strip()
    if txt.startswith("```"): txt = re.sub(r"^```\w*\s*|\s*```$","",txt)
    i,j = txt.find("{"), txt.rfind("}")
    return json.loads(txt[i:j+1])

def validate(d, kw):
    b = d.get("body","")
    wc = words(b.replace("{{APP_CTA}}",""))
    h2,h3,h4 = len(re.findall(r"<h2",b)),len(re.findall(r"<h3",b)),len(re.findall(r"<h4",b))
    errs=[]
    if wc < 2000: errs.append(f"kelime {wc}<2000")
    if h2 < 4: errs.append(f"H2 {h2}<4")
    if h3 < 4: errs.append(f"H3 {h3}<4")
    if kw.split()[0].lower() not in d.get("title","").lower(): errs.append("anahtar kelime title'da yok")
    return errs, wc, (h2,h3,h4)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLETAG__</title>
<meta name="description" content="__DESC__">
<meta name="keywords" content="__KW__">
<link rel="canonical" href="__URL__">__APPMETA__
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__URL__">
<meta property="og:image" content="__OGIMG__">
<meta property="og:image:alt" content="__TITLE__">
<meta property="og:site_name" content="Simple Skillet">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__DESC__">
<meta name="twitter:image" content="__OGIMG__">
<meta name="twitter:image:alt" content="__TITLE__">
<link rel="alternate" type="application/rss+xml" title="Simple Skillet Recipes RSS" href="/feed.xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#059669">
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">



<style>:root{--bg:#fbfaf7;--card:#fff;--ink:#1f2733;--muted:#69727f;--accent:#059669;--accent2:#34d399;--accent3:#047857;--line:#ece8e1;--shadow:0 6px 24px rgba(31,39,51,.07)}*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--ink);line-height:1.75;-webkit-font-smoothing:antialiased;overflow-x:hidden}.wrap{max-width:1080px;margin:0 auto;padding:0 22px}nav{position:sticky;top:0;z-index:40;background:rgba(251,250,247,.82);border-bottom:1px solid var(--line)}nav .nwrap{max-width:1080px;margin:0 auto;padding:0 22px;display:flex;align-items:center;justify-content:space-between;height:64px}.logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:19px;color:var(--ink);text-decoration:none}.logo img{width:30px;height:30px;border-radius:9px}.nav-links a{color:var(--muted);text-decoration:none;font-size:14.5px;font-weight:600;margin-left:24px}h1,h2{font-family:'Sora',sans-serif}.page{padding:46px 0 30px}.aurora{position:fixed;inset:0;z-index:-2;background:var(--bg)}a{color:var(--accent);text-decoration:none}.site-footer{margin-top:64px;border-top:1px solid var(--line);background:#fff}.foot-grid{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:32px;padding:46px 22px 32px;max-width:1080px;margin:0 auto}@media(max-width:640px){.foot-grid{grid-template-columns:1fr 1fr}}.foot-col a{display:block;color:var(--muted);font-size:14px;margin-bottom:11px}.foot-brand p{color:var(--muted);font-size:14px;margin-top:12px;max-width:280px}.fh{font-size:12.5px;text-transform:uppercase;letter-spacing:.1em;color:var(--ink);font-weight:700;margin-bottom:14px}.foot-bottom{border-top:1px solid var(--line)}.foot-bottom .wrap{display:flex;justify-content:space-between;padding:18px 22px;font-size:13px;color:var(--muted)}.chipwrap{text-align:center}.chiplbl{display:block;font-size:12px;letter-spacing:.22em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:12px}.chips{display:flex;gap:9px;flex-wrap:wrap;justify-content:center;margin-bottom:24px}.chips a{font-size:13.5px;font-weight:600;padding:8px 15px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink)}.posts{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:22px}.pcard{display:block;background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;color:var(--ink)}.pcard p{color:var(--muted);font-size:14.5px}.appbadges{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:14px}.appbadges a{font-size:13.5px;font-weight:700;padding:10px 16px;border-radius:11px;background:#111827;color:#fff}.related{border:1px solid var(--line);border-radius:16px;padding:22px 24px;background:#fff;margin:36px 0 10px}.related ul{list-style:none;margin:0;padding:0}.related a{display:block;padding:12px 2px;color:var(--ink);font-weight:600}.share{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:26px 0 6px;padding-top:18px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}.share .ico{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:50%;border:1px solid var(--line);color:var(--muted)}</style>
<link rel="preload" href="/assets/blog.css?v=15" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="preload" as="font" type="font/woff2" href="/assets/fonts/sora.woff2" crossorigin><link rel="preload" as="font" type="font/woff2" href="/assets/fonts/inter.woff2" crossorigin><link rel="stylesheet" href="/assets/blog.css?v=15"></noscript>
<script type="application/ld+json">__SCHEMA__</script>
<script src="/assets/analytics.js?v=3" defer></script><script src="/assets/enhance.js?v=7" defer></script>
</head>
<body>
<div class="aurora"></div>
<nav><div class="nwrap">
  <a class="logo" href="/"><img src="/assets/logo.svg" alt="Simple Skillet" width="28" height="28">Simple Skillet</a>
  <div class="nav-links"><a href="/">Home</a><a href="/blog/">Recipes</a><a href="/#about">About</a></div>
</div></nav>
<main class="wrap page">
__RAIL__
  <div class="crumb"><a href="/">Home</a> › <a href="/blog/">Blog</a> › __CRUMB__</div>
  <article class="post">
    <h1 class="title">__TITLE__</h1>
    <p class="meta">__TAG__ · __READ__ min read · Updated __NICE__</p>
__BODY__
  </article>
</main>
<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="logo" href="/"><img src="/assets/logo.svg" alt="Simple Skillet" width="30" height="30">Simple Skillet</a>
      <p>Tested, no-fuss weeknight recipes — real ingredients, real timing, no filler.</p>
    </div>
    <div class="foot-col">
      <p class="fh">Recipes</p>
      <a href="/blog/">All Recipes</a>
      <a href="https://pinterest.com/nedir_nasil">Pinterest</a>
    </div>
    <div class="foot-col">
      <p class="fh">Company</p>
      <a href="/#about">About</a>
      <a href="mailto:teknopattv@gmail.com">Contact</a>
    </div>
    <div class="foot-col">
      <p class="fh">Legal</p>
      <a href="/privacy.html">Privacy Policy</a>
      <a href="/cookies.html">Cookie Policy</a>
      <a href="/terms.html">Terms of Use</a>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap">
    <span>© 2026 Simple Skillet · Built by Aycan Merve Güneş</span>
    <span>Made with ♥ · <a rel="me" href="https://mastodon.social/@tabserve">Mastodon</a></span>
  </div></div>
</footer>
<div id="cookie-banner" style="display:none;position:fixed;left:0;right:0;bottom:0;z-index:60;background:#0d1426;border-top:1px solid rgba(255,255,255,.1);padding:14px 18px;font-size:13.5px;color:#cdd5ea;line-height:1.5">
  <div style="max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">
    <span>We use cookies for analytics and advertising (incl. Google AdSense). See our <a href="/cookies.html" style="color:#6a9bff">Cookie Policy</a>.</span>
    <span><button onclick="cookieOK(0)" style="background:none;border:1px solid rgba(255,255,255,.25);color:#cdd5ea;padding:7px 14px;border-radius:9px;cursor:pointer;margin-right:8px">Reject</button><button onclick="cookieOK(1)" style="background:linear-gradient(110deg,#6a9bff,#b27bff);border:0;color:#fff;padding:7px 16px;border-radius:9px;cursor:pointer;font-weight:600">Accept</button></span>
  </div>
</div>
<script>(function(){try{if(!localStorage.getItem('cookie_consent'))document.getElementById('cookie-banner').style.display='block';}catch(e){}})();
function cookieOK(v){try{localStorage.setItem('cookie_consent',v?'accepted':'rejected');}catch(e){}if(window.__grantConsent)__grantConsent(!!v);document.getElementById('cookie-banner').style.display='none';}</script>
</body>
</html>
"""

def insert_cta(body, cta):
    if "{{APP_CTA}}" in body:
        return body.replace("{{APP_CTA}}", cta, 1)
    pos = [m.start() for m in re.finditer(r"<h2", body)]
    if len(pos) >= 2:
        i = pos[len(pos)//2]; return body[:i] + cta + body[i:]
    return body + cta

def gemini_verify_image(img_bytes, expected, mime="image/jpeg"):
    """Gemini Vision ile indirilen fotoğrafın konuya uygunluğunu doğrular.
    GEMINI_API_KEY yoksa veya hata olursa sessizce True döner (eski davranış — engellemez)."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key: return True
    try:
        import base64
        b64 = base64.b64encode(img_bytes).decode()
        prompt = (f'Does this photo clearly and appropriately show "{expected}" for a recipe/food blog article? '
                  'Reject if it is unrelated, a screenshot, a logo, a chart, text-heavy, low quality, or contains '
                  'people\'s faces prominently. Reply with ONLY one word: YES or NO.')
        body = {"contents":[{"parts":[{"text":prompt},{"inline_data":{"mime_type":mime,"data":b64}}]}],
                "generationConfig":{"maxOutputTokens":200,"temperature":0}}
        m = _gemini_ok or (GEMINI_CANDIDATES[0] if GEMINI_CANDIDATES else "gemini-flash-latest")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
        r = _post(url, body, {"content-type":"application/json"})
        parts = r["candidates"][0]["content"].get("parts", [])
        txt = "".join(p.get("text", "") for p in parts).strip().upper()
        if not txt:
            raise KeyError("no text in any part (model likely exhausted token budget thinking)")
        ok = txt.startswith("YES")
        print(f"    (görsel doğrulama: {txt[:20]} · {expected[:40]})")
        return ok
    except Exception as e:
        print(f"    (görsel doğrulama atlandı: {type(e).__name__}: {e})")
        return True

def fetch_hero(query, slug):
    """Pexels'ten (yoksa Openverse/Wikimedia'dan) konuya uygun YATAY görsel indir
    (Gemini Vision ile doğrulanmış) → assets/blog/<slug>.webp (1600w) + <slug>-800.webp.
    Hiçbir kaynakta uygun görsel yoksa sessizce görselsiz devam eder."""
    out = ROOT / "assets" / "blog"
    if any((out / f"{slug}.{e}").exists() for e in ("webp","jpg","jpeg","png")):
        return True
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    raw, photographer, source = None, "?", "Pexels"
    if key:
        try:
            u = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
                {"query": query, "orientation": "landscape", "size": "large", "per_page": 5})
            r = json.loads(urllib.request.urlopen(
                urllib.request.Request(u, headers={"Authorization": key, "User-Agent": "tabserve-blog/1.0"}), timeout=25).read())
            for cand in (r.get("photos") or []):
                src = cand["src"].get("large2x") or cand["src"].get("large")
                try:
                    cand_raw = urllib.request.urlopen(urllib.request.Request(
                        src, headers={"User-Agent": "tabserve-blog/1.0"}), timeout=40).read()
                except Exception:
                    continue
                if gemini_verify_image(cand_raw, query):
                    raw, photographer = cand_raw, cand.get("photographer", "?"); break
        except Exception as e:
            print(f"  (Pexels hatası: {type(e).__name__})")
    if raw is None:  # Pexels'te bulunamadı/key yok → ücretsiz Openverse (Wikimedia dahil)
        source = "Openverse"
        for cand in _openverse(query, 5):
            try:
                cand_raw = urllib.request.urlopen(urllib.request.Request(
                    cand["url"], headers={"User-Agent": "tabserve-blog/1.0"}), timeout=40).read()
            except Exception:
                continue
            if gemini_verify_image(cand_raw, query):
                raw, photographer = cand_raw, cand.get("creator", "Unknown"); break
    if raw is None: return False
    try:
        out.mkdir(parents=True, exist_ok=True)
        try:
            import io
            from PIL import Image
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            for w_, suf in ((1600, ""), (800, "-800")):
                img = im if im.width <= w_ else im.resize(
                    (w_, round(im.height * w_ / im.width)), Image.LANCZOS)
                img.save(out / f"{slug}{suf}.webp", "WEBP", quality=82)
        except ImportError:
            (out / f"{slug}.jpg").write_bytes(raw)
        print(f"  🖼  {source}: {slug} <- {query} (by: {photographer})")
        return True
    except Exception as e:
        print(f"  (görsel atlandı: {type(e).__name__})")
        return False

def fetch_inpost(query, slug, idx):
    """In-content image: single 1000w, lazy — assets/blog/<slug>-in<idx>.webp
    (Pexels'te bulunamazsa Openverse/Wikimedia'ya düşer, Gemini Vision ile doğrulanmış)"""
    out = ROOT / "assets" / "blog"
    f = out / f"{slug}-in{idx}.webp"
    if f.exists(): return f"/assets/blog/{f.name}"
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    raw = None
    if key:
        try:
            u = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
                {"query": query, "orientation": "landscape", "size": "large", "per_page": 3})
            r = json.loads(urllib.request.urlopen(urllib.request.Request(
                u, headers={"Authorization": key, "User-Agent": "tabserve-blog/1.0"}), timeout=25).read())
            for cand in (r.get("photos") or []):
                src = cand["src"].get("large") or cand["src"].get("large2x")
                try:
                    cand_raw = urllib.request.urlopen(urllib.request.Request(
                        src, headers={"User-Agent": "tabserve-blog/1.0"}), timeout=40).read()
                except Exception:
                    continue
                if gemini_verify_image(cand_raw, query):
                    raw = cand_raw; break
        except Exception as e:
            print(f"  (Pexels hatası: {type(e).__name__})")
    if raw is None:
        for cand in _openverse(query, 3):
            try:
                cand_raw = urllib.request.urlopen(urllib.request.Request(
                    cand["url"], headers={"User-Agent": "tabserve-blog/1.0"}), timeout=40).read()
            except Exception:
                continue
            if gemini_verify_image(cand_raw, query):
                raw = cand_raw; break
    if raw is None: return None
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width > 1000:
            im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
        out.mkdir(parents=True, exist_ok=True)
        im.save(f, "WEBP", quality=80)
        print(f"  🖼  in-content {idx}: {slug} <- {query}")
        return f"/assets/blog/{f.name}"
    except Exception as e:
        print(f"  (in-content skipped: {type(e).__name__})"); return None

def insert_inpost_images(body, slug, queries, alt_base, keywords=""):
    """Insert in-content figures spread across the article (before 2nd,4th,6th,8th H2)."""
    pos = [m.start() for m in re.finditer(r"<h2", body)]
    _kws = [k.strip() for k in keywords.split(",") if k.strip()] or [alt_base]
    spots = [i for i in (1, 3, 5, 7) if i < len(pos)][:len(queries)]
    for k in reversed(range(len(spots))):
        rel = fetch_inpost(queries[k], slug, k + 1)
        if not rel: continue
        _kw = _kws[(k + 1) % len(_kws)]
        _alt = html.escape(_kw[:1].upper() + _kw[1:])
        fig = (f'<figure class="inpost"><img src="{rel}" alt="{_alt}" '
               f'loading="lazy" decoding="async" width="1000" height="560"><figcaption>{_alt}</figcaption></figure>')
        i = pos[spots[k]]
        body = body[:i] + fig + body[i:]
    return body

def _openverse(q, n):
    out = []
    try:
        u = "https://api.openverse.org/v1/images/?q=" + q.replace(" ", "+") + "&license_type=commercial&size=medium&page_size=18"
        r = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"tabserve-blog/1.0"}), timeout=20).read())
        seen = set()
        for it in r.get("results", []):
            img = it.get("url") or it.get("thumbnail") or ""
            if img and img not in seen:
                seen.add(img)
                out.append({"url": img, "creator": it.get("creator") or "Unknown", "license": (it.get("license") or "CC").upper()})
            if len(out) >= n: break
    except Exception as e:
        print(f"  (görsel hata: {type(e).__name__})")
    return out

def get_images(query, n=3, fallback="travel"):
    """Anahtarsız Openverse görselleri — uzun sorgu sonuç vermezse kısaltıp/fallback dener."""
    ws = query.split()
    for q in [" ".join(ws[:3]), " ".join(ws[:2]), fallback]:
        if not q.strip(): continue
        out = _openverse(q, n)
        if out: return out
    return []

def _figure(img, alt, caption_text, hero=False):
    cap = (html.escape(caption_text) + " — " if caption_text else "") + f"Photo: {html.escape(img['creator'])} (Openverse, {html.escape(img['license'])})"
    w, h = (1200, 630) if hero else (1000, 560)
    perf = ' fetchpriority="high"' if hero else ' decoding="async"'  # LCP boost / async decode
    return (f'<figure class="{"hero" if hero else "inpost"}"><img src="{html.escape(img["url"])}" '
            f'alt="{html.escape(alt)}" loading="{"eager" if hero else "lazy"}"{perf} width="{w}" height="{h}">'
            f'<figcaption>{cap}</figcaption></figure>')

def _h2_text(body, p):
    m = re.match(r'<h2[^>]*>(.*?)</h2>', body[p:], re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

def recipe_schema(body, title, description, image, url):
    """Recipe JSON-LD extracted from the article's own .recipe-card markup (rich results: time, servings, ratings)."""
    m = re.search(r'<div class="recipe-card"([^>]*)>([\s\S]*?)</div>\s*(?=<h2|$)', body)
    if not m: return None
    attrs_raw, inner = m.group(1), m.group(2)
    attrs = dict(re.findall(r'data-(\w+)="([^"]*)"', attrs_raw))
    strip = lambda s: re.sub(r'<[^>]+>', '', s).strip()
    ingredients = [strip(x) for x in re.findall(r'<li>(.*?)</li>', re.search(r'<ul class="ingredients">([\s\S]*?)</ul>', inner).group(1))] \
        if re.search(r'<ul class="ingredients">([\s\S]*?)</ul>', inner) else []
    steps = [strip(x) for x in re.findall(r'<li>(.*?)</li>', re.search(r'<ol class="instructions">([\s\S]*?)</ol>', inner).group(1))] \
        if re.search(r'<ol class="instructions">([\s\S]*?)</ol>', inner) else []
    if not ingredients or not steps: return None
    d = {"@context":"https://schema.org","@type":"Recipe","name":title,"description":description,"image":[image],
         "author":{"@type":"Person","name":"Aycan Merve Güneş"},
         "recipeIngredient":ingredients,
         "recipeInstructions":[{"@type":"HowToStep","text":s} for s in steps]}
    if attrs.get("prep"): d["prepTime"] = attrs["prep"]
    if attrs.get("cook"): d["cookTime"] = attrs["cook"]
    if attrs.get("total"): d["totalTime"] = attrs["total"]
    if attrs.get("servings"): d["recipeYield"] = attrs["servings"]
    if attrs.get("category"): d["recipeCategory"] = attrs["category"]
    if attrs.get("cuisine"): d["recipeCuisine"] = attrs["cuisine"]
    if attrs.get("calories"):
        d["nutrition"] = {"@type":"NutritionInformation","calories": f'{attrs["calories"]} calories'}
    return d

def add_pin_buttons(body, title, url):
    """Wrap hero/in-post <figure><img> with a Pinterest 'Save' overlay button (no JS needed — direct pin share intent)."""
    def _wrap(m):
        fig_open, img_tag, rest = m.group(1), m.group(2), m.group(3)
        src_m = re.search(r'src="([^"]+)"', img_tag)
        if not src_m: return m.group(0)
        img_url = src_m.group(1)
        if img_url.startswith("/"): img_url = SITE + img_url
        pin_url = ("https://pinterest.com/pin/create/button/?url=" + urllib.parse.quote(url, safe="")
                   + "&media=" + urllib.parse.quote(img_url, safe="") + "&description=" + urllib.parse.quote(title, safe=""))
        pin_btn = f'<a class="pin-save" href="{pin_url}" target="_blank" rel="noopener" aria-label="Save to Pinterest">{ICON["P"]} Save</a>'
        return f'{fig_open}<div class="pin-wrap">{img_tag}{pin_btn}</div>{rest}'
    return re.sub(r'(<figure class="(?:hero|inpost)">)(<img[^>]+>)(.*?</figure>)', _wrap, body)

def faq_schema(body):
    """FAQPage JSON-LD from the article's own FAQ section (rich results)."""
    m = re.search(r'<h2[^>]*>[^<]*Frequently Asked Questions[^<]*</h2>([\s\S]*)', body, re.I)
    if not m: return None
    strip = lambda s: re.sub(r'<[^>]+>', '', s).strip()
    qas = re.findall(r'<h3[^>]*>([\s\S]*?)</h3>\s*<p[^>]*>([\s\S]*?)</p>', m.group(1))
    items = [{"@type":"Question","name":strip(q),
              "acceptedAnswer":{"@type":"Answer","text":strip(a)}}
             for q, a in qas if strip(q) and strip(a)]
    if not items: return None
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":items}

def related_block(posts, current_slug, tag=None, n=4):
    """'More Recipes' — internal linking to other posts."""
    others = [p for p in posts if p["slug"] != current_slug]
    if tag:
        same = [p for p in others if p.get("tag") == tag]
        rest = [p for p in others if p.get("tag") != tag]
        others = same + rest
    others = others[:n]
    if not others: return ""
    lis = "".join(f'<li><a href="/blog/{p["slug"]}/">{html.escape(p["title"].split(":")[0].strip())}</a></li>'
                  for p in others)
    return ('<section class="related"><h2>More Recipes</h2><ul>'
            + lis + '</ul></section>')

def insert_toc(body, label="Contents"):
    """Builds a jump-link Table of Contents from H2 sections (long articles; .toc CSS ready)."""
    n = [0]; ids = []
    def _add(m):
        n[0] += 1; aid = f"s{n[0]}"
        t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        ids.append((aid, t)); return f'<h2 id="{aid}">{m.group(1)}</h2>'
    body = re.sub(r"<h2\b[^>]*>(.*?)</h2>", _add, body, flags=re.S)
    if len(ids) < 3:
        return body
    toc = '<details class="toc" open><summary>' + label + '</summary><ol>' + "".join(
        f'<li><a href="#{a}">{html.escape(t)}</a></li>' for a, t in ids) + '</ol></details>'
    i = body.find('<h2 id="s1">')
    return body if i < 0 else body[:i] + toc + body[i:]

def write_post(d, app, posts=()):
    slug = d["slug"]; url = f"{SITE}/blog/{slug}/"
    body = insert_cta(insert_toc(d["body"], "Contents"), APPS[app]["cta"])
    ogimg = f"{SITE}/assets/tabserve-og.png"
    # Görsel: kullanıcı assets/blog/<slug>.(jpg|png|webp) yüklerse hero olarak kullanılır; yoksa görselsiz (temiz).
    for ext in ("webp","jpg","jpeg","png"):
        ip = ROOT / "assets" / "blog" / f"{slug}.{ext}"
        if ip.exists():
            rel = f"/assets/blog/{slug}.{ext}"
            small = ROOT / "assets" / "blog" / f"{slug}-800.{ext}"
            srcset = (f' srcset="/assets/blog/{slug}-800.{ext} 800w, {rel} 1600w"'
                      f' sizes="(max-width:820px) 100vw, 780px"') if small.exists() else ""
            body = (f'<figure class="hero"><img src="{rel}"{srcset} alt="{html.escape(d["title"])}" loading="eager" fetchpriority="high" '
                    f'width="1200" height="630"><figcaption>{html.escape(d["meta_description"])}</figcaption></figure>') + body
            ogimg = SITE + rel
            break
    body = add_pin_buttons(body, d["title"], url)
    today = datetime.date.today()
    recipe = recipe_schema(body, d["title"], d["meta_description"], ogimg, url)
    schemas = [recipe] if recipe else [{"@context":"https://schema.org","@type":"Article","headline":d["title"],
        "description":d["meta_description"],"image":ogimg,"author":{"@type":"Person","name":"Aycan Merve Güneş","jobTitle":"Independent Full Stack Developer","url":"https://www.tabserve.com.tr/author.html"},
        "publisher":{"@type":"Organization","name":"Tabserve","logo":{"@type":"ImageObject","url":f"{SITE}/assets/tabserve-og.png"}},
        "datePublished":today.isoformat(),"dateModified":today.isoformat(),"mainEntityOfPage":url}]
    faq = faq_schema(body)
    if faq: schemas.append(faq)
    schemas.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":f"{SITE}/"},
        {"@type":"ListItem","position":2,"name":"Blog","item":f"{SITE}/blog/"},
        {"@type":"ListItem","position":3,"name":d["title"]}]})
    schema = json.dumps(schemas, ensure_ascii=False)
    read = max(4, round(words(body)/180))
    extras, rail = post_extras(url, d["title"])
    body = body + related_block(posts, slug, tag=APPS[app]["tag"]) + extras
    _ttl=d["title"]; _sfx=" | Tabserve"; _ttag=(_ttl+_sfx) if len(_ttl+_sfx)<=60 else (_ttl if len(_ttl)<=60 else (_ttl[:60].rsplit(" ",1)[0].rstrip(",:;-") or _ttl[:57]+"...")); page = (PAGE.replace("__TITLETAG__", html.escape(_ttag)).replace("__TITLE__", html.escape(d["title"])).replace("__DESC__", html.escape(d["meta_description"]))
        .replace("__KW__", html.escape(d["keywords"])).replace("__URL__", url).replace("__OGIMG__", html.escape(ogimg))
        .replace("__APPMETA__", "").replace("__SCHEMA__", schema).replace("__CRUMB__", html.escape(d["title"] if len(d["title"]) <= 42 else d["title"][:42].rsplit(" ", 1)[0] + "…"))
        .replace("__TAG__", APPS[app]["tag"]).replace("__READ__", str(read)).replace("__RAIL__", rail)
        .replace("__NICE__", "Published: " + today.strftime("%b %d, %Y") + " · Updated: " + today.strftime("%b %d, %Y")).replace("__BODY__", body))
    (BLOG / slug).mkdir(parents=True, exist_ok=True)
    (BLOG / slug / "index.html").write_text(page, encoding="utf-8")

PER_PAGE = 9  # listeleme sayfası başına yazı

# Site GENELİ arama: /assets/search.json'dan tüm yazılarda arar (sayfalamadan bağımsız)
SEARCH = """
<div class="psearch" style="max-width:540px;margin:0 auto 26px;position:relative">
  <input id="q" type="search" placeholder="Search articles…" aria-label="Search articles" autocomplete="off"
    style="width:100%;box-sizing:border-box;padding:13px 20px 13px 46px;border-radius:999px;border:1px solid rgba(120,120,140,.28);background:rgba(255,255,255,.75);font:inherit;font-size:15px;outline:none">
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" style="position:absolute;left:17px;top:50%;transform:translateY(-50%);opacity:.5" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
  <p id="qn" style="display:none;text-align:center;color:var(--muted);margin:14px 0 0">No results — try a different word.</p>
</div>
<div id="qres" class="posts" style="display:none"></div>
<script>document.addEventListener('DOMContentLoaded',function(){var q=document.getElementById('q');if(!q)return;
var grid=document.querySelector('.posts:not(#qres)'),nav=document.querySelector('.pagenav'),res=document.getElementById('qres'),qn=document.getElementById('qn'),idx=null;
function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML}
q.addEventListener('input',function(){var v=q.value.trim().toLowerCase();
 if(!v){res.style.display='none';res.innerHTML='';if(grid)grid.style.display='';if(nav)nav.style.display='';qn.style.display='none';return}
 function run(){var hits=idx.filter(function(p){return (p.t+' '+p.d).toLowerCase().indexOf(v)>-1}).slice(0,30);
  if(grid)grid.style.display='none';if(nav)nav.style.display='none';
  if(!hits.length){res.style.display='none';res.innerHTML='';qn.style.display='block';return}
  qn.style.display='none';
  res.innerHTML=hits.map(function(p){return '<a class="pcard in" href="'+p.u+'"><h3>'+esc(p.t)+'</h3><p>'+esc(p.d)+'</p></a>'}).join('');
  res.style.display='';}
 if(idx){run()}else{fetch('/assets/search.json').then(function(r){return r.json()}).then(function(j){idx=j;run()}).catch(function(){})}
});
var qp=new URLSearchParams(location.search).get("q");
if(qp){q.value=qp;q.dispatchEvent(new Event("input"));}});</script>
"""

def guide_label(t):
    """Popular Guides çipleri için temiz, tam okunur etiket — kelime ortasından kesmez."""
    main = t.split(":")[0].strip()          # ':' öncesi ana başlık
    if len(main) <= 58:
        return main
    return main[:58].rsplit(" ", 1)[0] + "…"  # kelime sınırında kes

def rebuild_index(posts):
    def card(p):
        return (f'    <a class="pcard" href="/blog/{p["slug"]}/"><span class="tag">{html.escape(p["tag"])}</span>'
                f'<h3>{html.escape(p["title"])}</h3><p>{html.escape(p["desc"])}</p></a>')
    # site geneli arama index'i
    (ROOT / "assets" / "search.json").write_text(json.dumps(
        [{"t": p["title"], "d": p["desc"], "u": f"/blog/{p['slug']}/"} for p in posts],
        ensure_ascii=False), encoding="utf-8")

    head = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="blogarama-site-verification" content="blogarama-a9ce490b-b35d-4df8-be42-dde71c7e9a94">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7579691213276550" crossorigin="anonymous"></script>
<title>__T__ | Simple Skillet</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__CANON__">__PREVNEXT__
<meta property="og:type" content="website"><meta property="og:title" content="__T__ | Simple Skillet">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__CANON__"><meta property="og:image" content="{SITE}/assets/tabserve-og.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE}/assets/tabserve-og.png">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"Simple Skillet","url":"{SITE}/","inLanguage":"en","potentialAction":{{"@type":"SearchAction","target":"{SITE}/blog/?q={{search_term_string}}","query-input":"required name=search_term_string"}}}}</script>__XSCHEMA__
<link rel="alternate" type="application/rss+xml" title="Simple Skillet Recipes RSS" href="/feed.xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#059669">
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">


<style>:root{{--bg:#fbf9f6;--card:#fff;--ink:#1a1a1a;--muted:#5b5b5b;--brand:#234386;--accent:#234386;--accent2:#ed7328;--accent3:#ffc400;--line:rgba(0,0,0,.12);--shadow:0 8px 24px rgba(0,0,0,.07)}}body{{background:var(--bg);color:var(--ink)}}.chipwrap{{text-align:center}}.chiplbl{{display:block;font-size:12px;letter-spacing:.22em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:12px}}.chips{{display:flex;gap:9px;flex-wrap:wrap;justify-content:center;margin-bottom:24px}}.chips a{{font-size:13.5px;font-weight:600;padding:8px 15px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink)}}.pcard{{background:#fff;border:none;border-radius:8px;padding:16px;color:var(--ink)}}.related{{border:1px solid var(--line);border-radius:8px;padding:22px 24px;background:#fff}}</style>
<link rel="preload" href="/assets/blog.css?v=15" as="style" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="preload" as="font" type="font/woff2" href="/assets/fonts/sora.woff2" crossorigin><link rel="preload" as="font" type="font/woff2" href="/assets/fonts/inter.woff2" crossorigin><link rel="stylesheet" href="/assets/blog.css?v=15"></noscript><script src="/assets/analytics.js?v=3" defer></script><script src="/assets/enhance.js?v=7" defer></script>
</head>
<body>
<div class="aurora"></div>
<nav><div class="nwrap"><a class="logo" href="/"><img src="/assets/logo.svg" alt="Simple Skillet" width="28" height="28">Simple Skillet</a>
<div class="nav-links"><a href="/">Home</a><a href="/blog/">Recipes</a><a href="/#about">About</a></div></div></nav>"""
    foot = """<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="logo" href="/"><img src="/assets/logo.svg" alt="Simple Skillet" width="30" height="30">Simple Skillet</a>
      <p>Tested, no-fuss weeknight recipes — real ingredients, real timing, no filler.</p>
    </div>
    <div class="foot-col">
      <p class="fh">Recipes</p>
      <a href="/blog/">All Recipes</a>
      <a href="https://pinterest.com/nedir_nasil">Pinterest</a>
    </div>
    <div class="foot-col">
      <p class="fh">Company</p>
      <a href="/#about">About</a>
      <a href="mailto:teknopattv@gmail.com">Contact</a>
    </div>
    <div class="foot-col">
      <p class="fh">Legal</p>
      <a href="/privacy.html">Privacy Policy</a>
      <a href="/cookies.html">Cookie Policy</a>
      <a href="/terms.html">Terms of Use</a>
    </div>
  </div>
  <div class="foot-bottom"><div class="wrap">
    <span>© 2026 Simple Skillet · Built by Aycan Merve Güneş</span>
    <span>Made with ♥ · <a rel="me" href="https://mastodon.social/@tabserve">Mastodon</a></span>
  </div></div>
</footer>
<script>const io=new IntersectionObserver(e=>e.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12});document.querySelectorAll('.pcard,.reveal').forEach((el,i)=>{el.style.transitionDelay=(i%4*70)+'ms';io.observe(el)});</script>
<noscript><style>.pcard,.reveal{opacity:1;transform:none}</style></noscript>
""" + COOKIE_BANNER + "\n</body></html>\n"

    # ── Sayfalamalı listeleme: /blog/ (p.1), /blog/page/2/ ... ────────────────
    chunks = [posts[i:i+PER_PAGE] for i in range(0, len(posts), PER_PAGE)] or [[]]
    total = len(chunks)
    page_url  = lambda n: f"{SITE}/blog/" if n == 1 else f"{SITE}/blog/page/{n}/"
    page_href = lambda n: "/blog/" if n == 1 else f"/blog/page/{n}/"

    for n, chunk in enumerate(chunks, 1):
        cards = "\n".join(card(p) for p in chunk)
        prevnext = ""
        if n > 1:     prevnext += f'\n<link rel="prev" href="{page_url(n-1)}">'
        if n < total: prevnext += f'\n<link rel="next" href="{page_url(n+1)}">'
        pagenav = ""
        if total > 1:
            items = [f'<a href="{page_href(n-1)}" aria-label="Previous">‹</a>' if n > 1 else '<span class="dis">‹</span>']
            items += [('<span class="cur">%d</span>' % i) if i == n else f'<a href="{page_href(i)}">{i}</a>' for i in range(1, total+1)]
            items.append(f'<a href="{page_href(n+1)}" aria-label="Next">›</a>' if n < total else '<span class="dis">›</span>')
            pagenav = '<nav class="pagenav" aria-label="Pages">' + "".join(items) + '</nav>'
        title = "Blog — Travel, trips &amp; landlord tips" if n == 1 else f"Blog — Page {n}"
        # <svg class="ico" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4"/></svg> Popular Guides (yalnız s.1): app çeşitliliğiyle curated iç-link bloğu
        poptips = ""
        if n == 1 and posts:
            seen, picks = set(), []
            for p in posts:  # önce her app'ten ilki (tag çeşitliliği)
                t = p.get("tag", "")
                if t and t not in seen:
                    seen.add(t); picks.append(p)
            picks += [p for p in posts if p not in picks]
            picks = picks[:6]
            chips = "".join(f'<a href="/blog/{p["slug"]}/">{html.escape(guide_label(p["title"]))}</a>' for p in picks)
            poptips = ('<div class="chipwrap" style="margin-top:30px"><span class="chiplbl">'
                       '<svg class="ico" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4"/></svg> Popular Guides</span><nav class="chips" aria-label="Popular guides">'
                       + chips + '</nav></div>')
        body = f"""
<main class="wrap page">
  <div class="crumb"><a href="/">Home</a> › Blog{'' if n == 1 else f' › Page {n}'}</div>
  <h1 class="title">Simple Skillet Recipes</h1>
  <p class="meta">Tested, no-fuss weeknight recipes — real ingredients, real timing, no filler.{f' ({len(posts)} recipes)' if n == 1 else ''}</p>
{SEARCH}
  <div class="posts">
{cards}
  </div>
{poptips}
  {pagenav}
</main>
"""
        xsch = ('<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"CollectionPage","name":"Simple Skillet Recipes","url":page_url(n),"inLanguage":"en"}, ensure_ascii=False) + '</script>'
                '<script type="application/ld+json">' + json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},{"@type":"ListItem","position":2,"name":"Blog" if n==1 else f"Blog — Page {n}","item":page_url(n)}]}, ensure_ascii=False) + '</script>')
        list_desc = ("Tested, no-fuss weeknight recipes — real ingredients, real timing, no filler." if n == 1 else f"Weeknight recipes from Simple Skillet — page {n}. Tested, practical recipes with exact times and temperatures.")
        page = head.replace("__T__", title).replace("__DESC__", list_desc).replace("__CANON__", page_url(n)).replace("__PREVNEXT__", prevnext).replace("__XSCHEMA__", xsch) + body + foot
        outdir = BLOG if n == 1 else BLOG / "page" / str(n)
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "index.html").write_text(page, encoding="utf-8")

    # yazı azalırsa bayat sayfa dizinlerini temizle
    pd = BLOG / "page"
    if pd.exists():
        for d in pd.iterdir():
            if d.is_dir() and d.name.isdigit() and int(d.name) > total:
                for f in d.iterdir(): f.unlink()
                d.rmdir()

    # ── RSS feed ─────────────────────────────────────────────────────────────
    items = "".join(
        f"<item><title>{html.escape(pp['title'])}</title><link>{SITE}/blog/{pp['slug']}/</link>"
        f"<guid>{SITE}/blog/{pp['slug']}/</guid><description>{html.escape(pp['desc'])}</description>"
        f"<pubDate>{datetime.datetime.strptime(pp.get('date','2026-06-25'), '%Y-%m-%d').strftime('%a, %d %b %Y')} 09:00:00 GMT</pubDate></item>"
        for pp in posts[:20])
    (ROOT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
        f'<title>Simple Skillet Recipes</title><link>{SITE}/</link>'
        '<description>Tested weeknight recipes by Simple Skillet</description>'
        f'<language>en</language>{items}</channel></rss>', encoding="utf-8")

    # ── Landing "From the blog" vitrini (index.html marker'ları arasına) ─────
    lp = ROOT / "index.html"
    if lp.exists():
        lc = lp.read_text(encoding="utf-8")
        import re as _re
        A, B = "<!--BLOG_TEASER_START-->", "<!--BLOG_TEASER_END-->"
        if A in lc and B in lc:
            t3 = posts[:9]
            teaser = A + '\n<section class="wrap" id="blogteaser" style="padding:26px 22px 8px"><h3 style="font-family:\'Sora\',sans-serif;font-size:26px;text-align:center;margin-bottom:20px">Fresh from the blog</h3><div class="grid" style="padding:0 0 8px">' + "".join(
                f'<article class="card in" style="opacity:1;transform:none"><h3 style="font-size:18px">{html.escape(pp["title"])}</h3>'
                f'<p>{html.escape(pp["desc"][:130])}…</p>'
                f'<a class="more" href="/blog/{pp["slug"]}/">Read the guide →</a></article>' for pp in t3
            ) + '</div><p style="text-align:center;margin:6px 0 26px"><a class="more" href="/blog/" style="font-size:15px">All guides →</a></p></section>\n' + B
            lc = _re.sub(_re.escape(A) + r"[\s\S]*?" + _re.escape(B), teaser, lc, count=1)
        # ── Popular Guides çipleri: her gün 12 rehber DÖNER (35 arasında rotasyon) ──
        CA, CB = "<!--POPGUIDES_START-->", "<!--POPGUIDES_END-->"
        if CA in lc and CB in lc and posts:
            off = datetime.date.today().toordinal() % len(posts)
            picks = (posts + posts)[off:off + 12]
            def _clabel(t):
                m = t.split(":")[0].strip()
                for pre in ("The Ultimate ", "The ", "A "):
                    if m.startswith(pre):
                        m = m[len(pre):]; break
                return m if len(m) <= 30 else m[:30].rsplit(" ", 1)[0] + "…"
            chips = "".join(f'<a href="/blog/{p["slug"]}/">{html.escape(_clabel(p["title"]))}</a>' for p in picks)
            blk = CA + '<section class="wrap reveal" style="padding:6px 22px 2px"><div class="chipwrap" style="margin-top:6px"><span class="chiplbl"><svg class="ico" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4"/></svg> Popular Guides</span><nav class="chips" aria-label="Popular guides">' + chips + '</nav></div></section>' + CB
            lc = _re.sub(_re.escape(CA) + r"[\s\S]*?" + _re.escape(CB), blk, lc, count=1)
        lp.write_text(lc, encoding="utf-8")

    # sitemap
    static = [("/","1.0","weekly"),("/blog/","0.8","weekly"),("/privacy.html","0.3","yearly")]
    urls = "".join(f'  <url><loc>{SITE}{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>\n' for u,p,c in static)
    urls += "".join(f'  <url><loc>{SITE}/blog/page/{n}/</loc><changefreq>weekly</changefreq><priority>0.5</priority></url>\n' for n in range(2, total+1))
    urls += "".join(f'  <url><loc>{SITE}/blog/{po["slug"]}/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n' for po in posts)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")

def main():
    posts = load(POSTS_F, [])
    if "--rebuild" in sys.argv:
        rebuild_index(posts); print(f"✓ listeleme+sitemap yeniden kuruldu ({len(posts)} yazı)"); return
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        sys.exit("⚠️ GEMINI_API_KEY (ücretsiz) veya ANTHROPIC_API_KEY gerekli")
    state = load(STATE_F, {"used":[]}); used = set(state["used"])
    n = int(os.environ.get("BLOG_COUNT","1")); made = 0; new_urls = []
    targets = [t for t in TOPICS if t["keyword"] not in used][:n]
    for topic in targets:
        kw, app = topic["keyword"], topic["app"]
        print(f"\n📝 [{app}] {kw}")
        prompt = PROMPT.format(kw=kw, angle=topic["angle"], one=APPS[app]["one"], name=APPS[app]["name"])
        d = None
        for tryi in range(2):
            txt = call_llm(prompt if tryi==0 else prompt+"\n\nYour previous attempt failed validation. Ensure 600+ WORDS and H2/H3/H4 hierarchy and the {{APP_CTA}} token.")
            try: cand = parse_json(txt)
            except Exception as e: print(f"  JSON parse hatası: {e}"); continue
            errs, wc, hh = validate(cand, kw)
            if not errs: d = cand; print(f"  ✓ {wc} kelime · H2/H3/H4={hh}"); break
            print(f"  ✗ doğrulama: {', '.join(errs)} → tekrar")
        if not d:
            print("  ⚠️ bu konu atlandı (kalite tutmadı)"); used.add(kw); continue
        d["slug"] = slugify(d.get("slug") or d["title"])
        iqs = d.get("img_queries") or ([d["img_query"]] if d.get("img_query") else [])
        fetch_hero((iqs[0] if iqs else kw), d["slug"])
        if len(iqs) > 1:
            d["body"] = insert_inpost_images(d["body"], d["slug"], iqs[1:3], d["title"], d.get("keywords", ""))
        write_post(d, app, posts)
        posts.insert(0, {"slug":d["slug"],"title":d["title"],"desc":d["meta_description"],
                         "tag":APPS[app]["tag"],"date":datetime.date.today().isoformat()})
        used.add(kw); made += 1
        new_urls.append(f"{SITE}/blog/{d['slug']}/")
        print(f"  ✓ yayınlandı: /blog/{d['slug']}/")
    # dedup posts by slug (en yeni kalsın)
    seen=set(); uniq=[]
    for p in posts:
        if p["slug"] in seen: continue
        seen.add(p["slug"]); uniq.append(p)
    POSTS_F.write_text(json.dumps(uniq, ensure_ascii=False, indent=1), encoding="utf-8")
    STATE_F.write_text(json.dumps({"used":list(used)}, ensure_ascii=False, indent=1), encoding="utf-8")
    rebuild_index(uniq)
    (GEN / "new_urls.txt").write_text("\n".join(new_urls), encoding="utf-8")  # index_ping.py için
    print(f"\n✓ {made} yeni yazı · toplam {len(uniq)} · {len(used)}/{len(TOPICS)} konu kullanıldı")

if __name__ == "__main__":
    main()
