#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yeni Simple Skillet tarif yazılarını Bluesky'a postlar (başlık + açıklama + #etiket + görsel link kartı).
generate.py'nin yazdığı _gen/new_urls.txt'ten okur; yazı HTML'i repoda yerel.
Env: BLUESKY_IDENTIFIER, BLUESKY_PASSWORD (yoksa atlar)."""
import os, re, json, html, datetime, urllib.request, urllib.error
from pathlib import Path

GEN = Path(__file__).resolve().parent
ROOT = GEN.parent
NEW = GEN / "new_urls.txt"
PDS = "https://bsky.social"
esc = html.unescape

TAGS = "#recipe #dinner #easyrecipes #homecooking #weeknightdinner"
STORE_LINK = "https://pinterest.com/nedir_nasil"


def local_html(url):
    slug = url.rstrip("/").split("/blog/")[-1]
    p = ROOT / "blog" / slug / "index.html"
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


def meta(h, *pats):
    for p in pats:
        m = re.search(p, h, re.I | re.S)
        if m: return esc(re.sub(r"\s+", " ", m.group(1)).strip())
    return ""


def hashtag_facets(text):
    facets = []
    for m in re.finditer(r"#([^\s#]+)", text):
        s = len(text[:m.start()].encode()); e = len(text[:m.end()].encode())
        facets.append({"index": {"byteStart": s, "byteEnd": e},
                       "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": m.group(1)}]})
    return facets


def api(method, token, body=None, raw=None, ctype="application/json"):
    h = {"Content-Type": ctype}
    if token: h["Authorization"] = f"Bearer {token}"
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(f"{PDS}/xrpc/{method}", data=data, headers=h, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=40).read())


def main():
    ident = os.environ.get("BLUESKY_IDENTIFIER"); pw = os.environ.get("BLUESKY_PASSWORD")
    urls = [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines() if u.strip()] if NEW.exists() else []
    urls = [u for u in urls if "/blog/" in u]
    if not urls:
        print("Bluesky: yeni blog yazısı yok"); return
    if not (ident and pw):
        print("⚠️ BLUESKY_IDENTIFIER/PASSWORD yok → Bluesky atlandı"); return
    sess = api("com.atproto.server.createSession", None, {"identifier": ident, "password": pw})
    print(f"✓ Bluesky: {sess['handle']}")
    for url in urls:
        h = local_html(url)
        if not h: continue
        title = meta(h, r'og:title["\']\s+content=["\'](.*?)["\']', r"<title>(.*?)</title>").split(" | ")[0]
        desc = meta(h, r'og:description["\']\s+content=["\'](.*?)["\']', r'name=["\']description["\']\s+content=["\'](.*?)["\']')
        ogimg = meta(h, r'og:image["\']\s+content=["\'](.*?)["\']')
        cta = f"📌 Save it on Pinterest 👇 {STORE_LINK}"
        text = f"🏠 {title}\n\n{desc[:105]}\n{cta}\n\n{TAGS}"[:295]
        thumb = None
        if ogimg:
            try:
                img = urllib.request.urlopen(urllib.request.Request(ogimg, headers={"User-Agent": "bsky/1.0"}), timeout=25).read()
                mime = "image/png" if ogimg.lower().endswith("png") else "image/jpeg"
                thumb = api("com.atproto.repo.uploadBlob", sess["accessJwt"], raw=img, ctype=mime).get("blob")
            except Exception:
                pass
        ext = {"uri": url, "title": title[:280], "description": desc[:300]}
        if thumb: ext["thumb"] = thumb
        rec = {"$type": "app.bsky.feed.post", "text": text, "facets": hashtag_facets(text), "langs": ["en"],
               "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
               "embed": {"$type": "app.bsky.embed.external", "external": ext}}
        api("com.atproto.repo.createRecord", sess["accessJwt"],
            {"repo": sess["did"], "collection": "app.bsky.feed.post", "record": rec})
        print(f"  ✓ Bluesky'a postlandı: {url}")


if __name__ == "__main__":
    main()
