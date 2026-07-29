#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yeni blog URL'lerini Google Indexing API + IndexNow'a (Bing/Yandex) bildirir.
generate.py'nin yazdığı _gen/new_urls.txt'ten okur.
Env: GOOGLE_INDEXING_SA (service account JSON; yoksa Google ping atlanır)."""
import os, json, urllib.request
from pathlib import Path

GEN = Path(__file__).resolve().parent
NEW = GEN / "new_urls.txt"
HOST = "recipes.tabserve.com.tr"
INDEXNOW_KEY = "6b2c33a8ee47462a9c217f29a99ada33"

def read_urls():
    if not NEW.exists():
        return []
    return [u.strip() for u in NEW.read_text(encoding="utf-8").splitlines() if u.strip()]

def google_index(urls, sa_raw):
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        print("  ⚠️ google-auth kurulu değil → Google ping atlandı"); return
    creds = service_account.Credentials.from_service_account_info(
        json.loads(sa_raw), scopes=["https://www.googleapis.com/auth/indexing"])
    s = AuthorizedSession(creds)
    for u in urls:
        try:
            r = s.post("https://indexing.googleapis.com/v3/urlNotifications:publish",
                       json={"url": u, "type": "URL_UPDATED"}, timeout=30)
            print(f"  Google: {u} → {r.status_code}")
        except Exception as e:
            print(f"  Google hata ({u}): {type(e).__name__}")

def indexnow(urls):
    try:
        body = json.dumps({"host": HOST, "key": INDEXNOW_KEY,
                           "keyLocation": f"https://{HOST}/{INDEXNOW_KEY}.txt",
                           "urlList": urls}).encode()
        req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                     headers={"Content-Type": "application/json"}, method="POST")
        r = urllib.request.urlopen(req, timeout=30)
        print(f"  IndexNow (Bing/Yandex) → HTTP {r.status}")
    except Exception as e:
        print(f"  IndexNow hata: {type(e).__name__}")

def main():
    urls = read_urls()
    if not urls:
        print("yeni URL yok, ping atlanıyor"); return
    print(f"📤 {len(urls)} yeni URL indekse bildiriliyor:")
    sa = os.environ.get("GOOGLE_INDEXING_SA", "").strip()
    if sa:
        google_index(urls, sa)
    else:
        print("  ⚠️ GOOGLE_INDEXING_SA yok → Google ping atlandı")
    indexnow(urls)

if __name__ == "__main__":
    main()
