#!/usr/bin/env python3
"""Genera clip provvisorie in pixel art per i combattimenti (mostri/<id>/*.mp4).

Servono solo a provare tempi e gesti per strada finché non arrivano i video veri.
Gli sprite e i colori vengono letti da index.html, le mosse da storia.json.
Richiede Pillow e ffmpeg.

Uso: python3 genera_segnaposto.py [id_mostro ...]
Attenzione: sovrascrive i file in mostri/<id>/. Non lanciarlo dopo aver messo i video veri.
"""
import json, math, pathlib, random, re, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw

base = pathlib.Path(__file__).parent
html = (base / "index.html").read_text(encoding="utf-8")
D = json.loads((base / "storia.json").read_text(encoding="utf-8"))

pal_src = re.search(r"const PAL=\{(.*?)\};", html, re.S).group(1)
PAL = {k: v for k, v in re.findall(r"(\w|'\.'):'(#[0-9a-fA-F]{6})'", pal_src)}
spr_src = re.search(r"const SPR=\{(.*?)\n\};", html, re.S).group(1)
SPR = {n: re.findall(r'"([^"]{16})"', body) for n, body in re.findall(r"(\w+):\[(.*?)\]", spr_src, re.S)}

W, H, FPS, SCALA = 135, 240, 12, 4          # disegno a 135x240, esporto a 540x960
TINTE = {"profondo": (20, 46, 44), "ombra": (40, 30, 24), "tindalos": (18, 26, 40)}
POSE = {"destra": (38, 128, 6), "sinistra": (97, 128, 6), "su": (67, 178, 6), "giu": (67, 84, 6), "tocco": (67, 124, 8)}


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def sprite(mid):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(SPR[mid]):
        for x, ch in enumerate(row):
            if ch in PAL:
                im.putpixel((x, y), hexrgb(PAL[ch]) + (255,))
    return im


def sfondo(mid, luce=1.0):
    t = TINTE.get(mid, (20, 30, 24))
    im = Image.new("RGB", (W, H), tuple(int(c * .5 * luce) for c in t))
    d = ImageDraw.Draw(im)
    for y in range(0, 70):                                   # cielo
        k = 1 - y / 90
        d.line([(0, y), (W, y)], fill=tuple(int(c * k * .7 * luce) for c in t))
    muro = tuple(int(c * 1.5 * luce) for c in t)
    d.polygon([(0, 30), (34, 60), (34, 190), (0, 240)], fill=muro)          # vicolo in prospettiva
    d.polygon([(W, 30), (101, 60), (101, 190), (W, 240)], fill=muro)
    for y in range(70, 180, 22):                                            # finestre
        for x0, x1 in ((8, 18), (117, 127)):
            on = random.random() < .15
            d.rectangle([x0, y, x1, y + 10], fill=(200, 165, 87) if on else tuple(int(c * .6) for c in t))
    d.polygon([(34, 190), (101, 190), (W, 240), (0, 240)], fill=tuple(int(c * 1.1 * luce) for c in t))
    for i in range(6):                                                      # selciato
        y = 192 + i * i * 1.4
        d.line([(0, y), (W, y)], fill=tuple(int(c * .7 * luce) for c in t))
    if mid == "ombra":                                                      # lampione
        d.line([(110, 70), (110, 190)], fill=(20, 20, 20), width=2)
        d.ellipse([104, 62, 116, 74], fill=(255, 223, 138) if luce > .6 else (90, 80, 50))
    if mid == "profondo":                                                   # fontanella
        d.rectangle([40, 168, 52, 190], fill=(60, 70, 66))
        d.line([(46, 172), (46, 190)], fill=(120, 190, 170))
    if mid == "tindalos":                                                   # spigolo vivo
        d.polygon([(34, 60), (52, 110), (34, 190)], fill=tuple(int(c * 2.2 * luce) for c in t))
    return im


def vignetta(im, forza=.75):
    v = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(v)
    for r in range(40):
        a = int(255 * forza * (r / 40) ** 2)
        d.ellipse([-r * 3 - 30, -r * 4 - 40, W + r * 3 + 30, H + r * 4 + 40], outline=a, width=4)
    nero = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(nero, im, v)


def posa(im, spr, x, y, s, alfa=1.0, buchi=0.0, caduta=0.0):
    s = max(1, int(round(s)))
    sp = spr.resize((16 * s, 16 * s), Image.NEAREST)
    if buchi > 0:                                         # dissolvenza a pixel
        px = sp.load()
        rnd = random.Random(7)
        for by in range(16):
            for bx in range(16):
                if rnd.random() < buchi:
                    for yy in range(by * s, by * s + s):
                        for xx in range(bx * s, bx * s + s):
                            px[xx, yy] = (0, 0, 0, 0)
    if alfa < 1:
        a = sp.split()[3].point(lambda v: int(v * alfa))
        sp.putalpha(a)
    im.paste(sp, (int(x - 8 * s), int(y - 8 * s + caduta)), sp)


def ease(t):
    return 1 - (1 - t) ** 3


def clip(nome, frames, cartella):
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i, f in enumerate(frames):
        f.save(tmp / f"f{i:03d}.png")
    out = cartella / nome
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmp / "f%03d.png"),
                    "-vf", f"scale={W*SCALA}:{H*SCALA}:flags=neighbor", "-c:v", "libx264", "-preset", "slow",
                    "-crf", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out)], check=True)
    shutil.rmtree(tmp)
    print(f"  {out.relative_to(base)}  {out.stat().st_size // 1024} KB, {len(frames) / FPS:.1f} s")


def genera(m):
    mid = m["id"]
    random.seed(mid)
    spr = sprite(mid)
    cart = base / m["cartella"]
    cart.mkdir(parents=True, exist_ok=True)
    pose = [POSE[p["mossa"]] for p in m["passi"]]
    print(m["nome"])

    def frame(x, y, s, luce=1.0, flash=None, **kw):
        im = sfondo(mid, luce * (0.85 + 0.15 * random.random()))
        posa(im, spr, x, y, s, **kw)
        im = vignetta(im)
        if flash:
            im = Image.blend(im, Image.new("RGB", (W, H), flash[0]), flash[1])
        return im

    # intro: dal buio fino al primo momento decisivo (3 s)
    fr, x1, y1, s1 = [], *pose[0]
    n = FPS * 3
    for i in range(n):
        t = ease(i / (n - 1))
        fr.append(frame(67 + (x1 - 67) * t, 130 + (y1 - 130) * t, 2 + (s1 - 2) * t, luce=.6 + .4 * t, alfa=.25 + .75 * t))
    clip(m["intro"], fr, cart)

    # ok_N: contraccolpo e passaggio alla posa successiva (2 s)
    for i, p in enumerate(m["passi"]):
        if not p.get("ok"):
            continue
        (xa, ya, sa), (xb, yb, sb) = pose[i], pose[min(i + 1, len(pose) - 1)]
        fr = []
        for k in range(FPS * 2):
            if k < 3:
                fr.append(frame(xa, ya, sa * .85, flash=((236, 230, 214), .55 - k * .15)))
                continue
            t = ease((k - 3) / (FPS * 2 - 4))
            fr.append(frame(xa + (xb - xa) * t, ya + (yb - ya) * t, sa * .85 + (sb - sa * .85) * t))
        clip(p["ok"], fr, cart)

    # ko: il mostro vi viene addosso, rosso, buio (1,6 s)
    fr = []
    n = int(FPS * 1.6)
    for k in range(n):
        t = k / (n - 1)
        rosso = min(1, t * 1.4)
        im = frame(67, 124, 7 + 18 * ease(min(1, t * 1.6)), flash=((140, 20, 30), .2 + .6 * rosso))
        if t > .75:
            im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), (t - .75) / .25)
        fr.append(im)
    clip(m["ko"], fr, cart)

    # vittoria: lampi, il mostro si sfalda e cade (3 s)
    fr, (xl, yl, sl) = [], pose[-1]
    n = FPS * 3
    for k in range(n):
        t = k / (n - 1)
        fl = ((236, 230, 214), .5) if k in (0, 2, 5) else None
        fr.append(frame(xl, yl, sl, luce=1 - .5 * t, flash=fl, buchi=min(1, t * 1.2), caduta=30 * t * t, alfa=1 - t * .6))
    clip(m["vittoria"], fr, cart)


if __name__ == "__main__":
    scelti = sys.argv[1:]
    for m in D["mostri"]:
        if not scelti or m["id"] in scelti:
            genera(m)
