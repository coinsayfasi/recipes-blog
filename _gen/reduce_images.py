#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Görsel sayısını yazı başına en fazla 2 inpost (hero dahil 3) ile sınırlar.
- Fazla inpost görselleri (in3+) HTML'den ve diskten siler.
- gezi'de Wikimedia kaynaklı görselleri Pexels'e geri çevirir (atıf etiketini kaldırır).
- Kalan 2 görselin benzersizliğini korur.
Dosya adları (slug-in1/in2.webp) değişmez → HTML bozulmaz.
"""
import re, glob, html, sys, io, hashlib, json, urllib.request, urllib.parse
from pathlib import Path

GEN = Path(__file__).resolve().parent
sys.path.insert(0, str(GEN))
import generate as G

IS_TR = "gezi" in str(G.ROOT).lower()
UA = {"User-Agent": "tabserve-blog/1.0 (+https://tabserve.com.tr)"}
TARGET = 2

FIG_RE = re.compile(
    r'<figure class="inpost"><img src="([^"]+?-in(\d+)\.webp)"[^>]*?alt="([^"]*)"[^>]*?>'
    r'(?:<figcaption>.*?</figcaption>)?</figure>', re.S)


def ascii_fold(s):
    for a, b in (("ı", "i"), ("İ", "I"), ("ş", "s"), ("Ş", "S"), ("ğ", "g"),
                 ("Ğ", "G"), ("ü", "u"), ("Ü", "U"), ("ö", "o"), ("Ö", "O"), ("ç", "c"), ("Ç", "C")):
        s = s.replace(a, b)
    return s


def pexels_srcs(query):
    key = G.os.environ.get("PEXELS_API_KEY", "").strip()
    if not key:
        return []
    try:
        u = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
            {"query": query, "orientation": "landscape", "size": "large", "per_page": 15})
        r = json.loads(urllib.request.urlopen(urllib.request.Request(
            u, headers={"Authorization": key, **UA}), timeout=25).read())
        return [ph["src"].get("large") or ph["src"].get("large2x")
                for ph in (r.get("photos") or []) if ph.get("src")]
    except Exception:
        return []


def save_webp(src, dest):
    from PIL import Image
    raw = urllib.request.urlopen(urllib.request.Request(src, headers=UA), timeout=40).read()
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if im.width > 1000:
        im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "WEBP", quality=80)
    return hashlib.md5(dest.read_bytes()).hexdigest()


def main():
    aud = Path(G.ROOT) / "assets" / "blog"
    changed = removed = refetched = 0
    for f in sorted(glob.glob(str(G.ROOT / "blog/*/index.html"))):
        slug = Path(f).parent.name
        h = open(f, encoding="utf-8").read()
        t_m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
        topic = re.sub(r"<[^>]+>", "", t_m.group(1)).split(":")[0].split("—")[0].strip() if t_m else slug
        figs = sorted(FIG_RE.finditer(h), key=lambda m: int(m.group(2)))
        if not figs:
            continue
        keep, drop = figs[:TARGET], figs[TARGET:]
        art_changed = False
        # fazlaları sil
        for m in drop:
            h = h.replace(m.group(0), "", 1)
            (aud / f"{slug}-in{m.group(2)}.webp").unlink(missing_ok=True)
            removed += 1
            art_changed = True
        # kalanları düzelt (gezi: wiki->pexels + atıf temizle, benzersiz)
        used = set()
        for m in keep:
            idx, alt = m.group(2), m.group(3)
            fp = aud / f"{slug}-in{idx}.webp"
            has_wiki = "Kaynak: Wikimedia" in m.group(0)
            need_fetch = IS_TR or has_wiki
            if not need_fetch:
                if fp.exists():
                    used.add(hashlib.md5(fp.read_bytes()).hexdigest())
                continue
            cands = []
            for q in (f"{ascii_fold(topic)} Turkey", ascii_fold(topic),
                      "Turkey travel scenery", "Turkey landscape nature", "Turkey coast"):
                cands += pexels_srcs(q)
            chosen = None
            for src in cands:
                tmp = fp.with_name(fp.stem + ".tmp.webp")
                try:
                    hh = save_webp(src, tmp)
                except Exception:
                    continue
                if hh in used:
                    tmp.unlink(missing_ok=True)
                    continue
                tmp.replace(fp)
                chosen = hh
                break
            if chosen:
                used.add(chosen)
                refetched += 1
            # her hâlükârda atıfsız, temiz figure yaz
            newfig = (f'<figure class="inpost"><img src="{m.group(1)}" alt="{alt}" '
                      f'loading="lazy" decoding="async" width="1000" height="560">'
                      f'<figcaption>{alt}</figcaption></figure>')
            if newfig != m.group(0):
                h = h.replace(m.group(0), newfig, 1)
                art_changed = True
        if art_changed:
            open(f, "w", encoding="utf-8").write(h)
            changed += 1
            print(f"  ✓ {slug}: {len(keep)} görsel kaldı")
    print(f"\n✓ reduce: {changed} yazı | {removed} fazla görsel silindi | {refetched} görsel Pexels'e çevrildi")


if __name__ == "__main__":
    main()
