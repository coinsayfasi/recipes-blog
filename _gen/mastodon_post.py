#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recipes.tabserve.com.tr YENİ tarif yazılarını Mastodon'a postlar.
Mail/şifre YOK, sadece access token. Mastodon linkten og önizleme kartı üretir.
Env: MASTODON_INSTANCE, MASTODON_TOKEN. Yoksa güvenli atlar."""
import os, re, json, html, urllib.parse, urllib.request
from pathlib import Path

GEN = Path(__file__).resolve().parent
ROOT = GEN.parent
NEW = GEN / "new_urls.txt"
esc = html.unescape

TAGS = "#landlord #realestate #property #rental"
STORE_LINK = "https://pinterest.com/nedir_nasil"


def toot(instance, token, status, lang):
    data = urllib.parse.urlencode({"status": status, "visibility": "public",
                                   "language": lang}).encode()
    req = urllib.request.Request(
        f"{instance.rstrip('/')}/api/v1/statuses", data=data, method="POST",
        headers={"Authorization": f"Bearer {token}"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def local_html(url):
    slug = url.rstrip("/").split("/blog/")[-1]
    p = ROOT / "blog" / slug / "index.html"
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""


def meta(h, *pats):
    for p in pats:
        m = re.search(p, h, re.I | re.S)
        if m:
            return esc(re.sub(r"\s+", " ", m.group(1)).strip())
    return ""


def main():
    instance = os.environ.get("MASTODON_INSTANCE"); token = os.environ.get("MASTODON_TOKEN")
    if not (instance and token):
        print("⚠️ MASTODON_INSTANCE/TOKEN yok → Mastodon atlandı"); return
    urls = [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines()
            if u.strip() and "/blog/" in u] if NEW.exists() else []
    if not urls:
        print("Mastodon: yeni yazı yok"); return
    for url in urls:
        h = local_html(url)
        if not h:
            continue
        title = meta(h, r'og:title["\']\s+content=["\'](.*?)["\']',
                     r"<title>(.*?)</title>").split(" | ")[0]
        desc = meta(h, r'og:description["\']\s+content=["\'](.*?)["\']',
                    r'name=["\']description["\']\s+content=["\'](.*?)["\']')
        if not title:
            continue
        status = (f"🏠 {title}\n\n{desc[:170]}\n\n{url}\n\n"
                  f"📌 Save it: {STORE_LINK}\n\n{TAGS}")[:480]
        toot(instance, token, status, "en")
        print(f"  ✓ Mastodon: {url}")


if __name__ == "__main__":
    main()
