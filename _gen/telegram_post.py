#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""recipes.tabserve.com.tr YENİ tarif yazılarını Telegram kanalına postlar.
Mail/şifre YOK — sadece bot token.
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID. Token yoksa güvenli atlar."""
import os, re, json, html, urllib.parse, urllib.request
from pathlib import Path

GEN = Path(__file__).resolve().parent
ROOT = GEN.parent
NEW = GEN / "new_urls.txt"
API = "https://api.telegram.org"
esc = html.unescape

TAGS = "#landlord #realestate #property #rental"
STORE_LINK = "https://pinterest.com/nedir_nasil"


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


def esc_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tg(method, payload, token):
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(f"{API}/bot{token}/{method}", data=data, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN"); chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        print("⚠️ TELEGRAM_BOT_TOKEN/CHAT_ID yok → Telegram atlandı"); return
    urls = [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines()
            if u.strip() and "/blog/" in u] if NEW.exists() else []
    if not urls:
        print("Telegram: yeni yazı yok"); return
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
        text = (f"🏠 <b>{esc_html(title)}</b>\n\n{esc_html(desc[:200])}\n\n{url}\n\n"
                f"📌 Save it: {STORE_LINK}\n\n{TAGS}")
        tg("sendMessage", {"chat_id": chat, "text": text[:1000], "parse_mode": "HTML",
                           "disable_web_page_preview": "false"}, token)
        print(f"  ✓ Telegram: {url}")


if __name__ == "__main__":
    main()
