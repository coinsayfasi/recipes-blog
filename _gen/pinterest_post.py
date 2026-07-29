#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple Skillet (recipes.tabserve.com.tr) — yeni tarif yazılarını Pinterest'e pinler.
Gerçek tarif hero fotoğrafını (assets/blog/<slug>.webp) doğrudan pin görseli olarak kullanır
— markalı kart yerine iştah açıcı gerçek yemek fotoğrafı, tarif pin'lerinde daha iyi performans gösterir.
Env: PINTEREST_APP_ID, PINTEREST_APP_SECRET, PINTEREST_REFRESH_TOKEN — yoksa DRY-RUN (sadece loglar).
"""
import json, os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pinterest_api import PinterestClient, refresh_access_token

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "_gen" / "pinterest_state.json"
POSTS_F = ROOT / "_gen" / "posts.json"
SITE = "https://recipes.tabserve.com.tr"
BOARD_NAME = "Easy Weeknight Recipes"
BOARD_DESC = "Tested, no-fuss recipes with exact times and temperatures — real ingredients, real results."
MAX_PER_RUN = int(os.environ.get("PINTEREST_PINS_PER_RUN", "3"))


def load(p, d):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else d


def hero_image_bytes(slug):
    for ext in ("webp", "jpg", "jpeg", "png"):
        f = ROOT / "assets" / "blog" / f"{slug}.{ext}"
        if f.exists():
            return f.read_bytes(), ext
    return None, None


def png_bytes(raw, ext):
    """Pinterest create_pin bu script'te PNG bekliyor; webp/jpg ise Pillow ile PNG'ye çevir."""
    if ext == "png":
        return raw
    from io import BytesIO
    from PIL import Image
    im = Image.open(BytesIO(raw)).convert("RGB")
    out = BytesIO()
    im.save(out, "PNG")
    return out.getvalue()


def main():
    state = load(STATE, {"pinned": []})
    pinned = set(state.get("pinned", []))
    posts = load(POSTS_F, [])
    targets = [p for p in posts if p["slug"] not in pinned][:MAX_PER_RUN]
    if not targets:
        print("yeni pin'lenecek yazı yok"); return

    app_id = os.environ.get("PINTEREST_APP_ID")
    secret = os.environ.get("PINTEREST_APP_SECRET")
    rt = os.environ.get("PINTEREST_REFRESH_TOKEN")
    dry = not (app_id and secret and rt)
    client, board_id = None, None
    if not dry:
        client = PinterestClient(refresh_access_token(app_id, secret, rt))
        board_id = client.ensure_board(BOARD_NAME, BOARD_DESC)

    made = 0
    for p in targets:
        slug, title, desc = p["slug"], p["title"], p.get("desc", "")
        raw, ext = hero_image_bytes(slug)
        if not raw:
            print(f"  {slug}: hero görseli yok, atlandı"); continue
        url = f"{SITE}/blog/{slug}/"
        pin_desc = f"{desc} 🍽️ Full recipe with exact times & temperatures on Simple Skillet. #recipe #dinner #easyrecipes #homecooking"[:480]
        if dry:
            print(f"  [DRY-RUN] would pin: {title} -> {url}")
            pinned.add(slug); made += 1; continue
        try:
            img_png = png_bytes(raw, ext)
            pin_id = client.create_pin(board_id, title=title, description=pin_desc, link=url,
                                        image_png=img_png, alt_text=title)
            print(f"  ✓ pinned: {title} (pin_id={pin_id})")
            pinned.add(slug); made += 1
        except Exception as e:
            print(f"  ✗ {slug}: {type(e).__name__}: {e}")

    state["pinned"] = sorted(pinned)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ {made} pin{'DRY-RUN' if dry else ''} · toplam pinlenmiş: {len(pinned)}")


if __name__ == "__main__":
    main()
