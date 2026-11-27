#!/usr/bin/env python3
"""Genera la musica e gli effetti sonori con ElevenLabs.

Uso:
  export ELEVENLABS_API_KEY="..."
  python3 genera_musica.py                  genera le tracce e gli effetti mancanti
  python3 genera_musica.py --force          rigenera tutto
  python3 genera_musica.py --solo tema,porta   solo questi id
  python3 genera_musica.py --musica | --effetti   solo una delle due famiglie

I prompt e le durate stanno in storia.json → audio.musica / audio.effetti. Cambiali lì e rigenera con --solo.
Tracce → audio/musica/<id>.mp3 (normalizzate a -20 LUFS, sotto la voce). Effetti → audio/sfx/<id>.mp3 (-14 LUFS).
Il gioco le carica da solo; quelle che mancano restano in silenzio (gli effetti tornano ai bip sintetici).
Richiede ffmpeg per la normalizzazione. Costa crediti ElevenLabs: prova prima con --solo.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request

BASE = os.environ.get("ELEVENLABS_BASE", "https://api.elevenlabs.io")
KEY = os.environ.get("ELEVENLABS_API_KEY")
FORMATO = os.environ.get("FORMATO", "mp3_44100_128")
base = pathlib.Path(__file__).parent
A = json.load(open(base / "storia.json", encoding="utf-8"))["audio"]
argv = sys.argv[1:]
if not KEY:
    sys.exit("Manca ELEVENLABS_API_KEY.")


def chiama(percorso, corpo):
    req = urllib.request.Request(BASE + percorso + "?" + urllib.parse.urlencode({"output_format": FORMATO}), method="POST",
                                 headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"}, data=json.dumps(corpo).encode())
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Errore {e.code} da {percorso}: {e.read().decode('utf-8', 'replace')[:400]}")


def normalizza(f, lufs):
    if not shutil.which("ffmpeg"):
        return
    tmp = pathlib.Path(tempfile.mkdtemp()) / "n.mp3"
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(f), "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=9", "-ar", "44100", "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True, timeout=300)
    shutil.move(str(tmp), str(f))


voluti = set(argv[argv.index("--solo") + 1].split(",")) if "--solo" in argv else None
fam = []
if "--effetti" not in argv:
    fam.append(("musica", "musica", -20, A["musica"]))
if "--musica" not in argv:
    fam.append(("sfx", "effetti", -14, A["effetti"]))
for cartella, nome, lufs, lista in fam:
    (base / "audio" / cartella).mkdir(parents=True, exist_ok=True)
    for t in lista:
        if voluti and t["id"] not in voluti:
            continue
        f = base / "audio" / cartella / (t["id"] + ".mp3")
        if f.exists() and "--force" not in argv:
            print("salto", f.name)
            continue
        if cartella == "musica":
            dati = chiama("/v1/music", {"prompt": t["prompt"], "music_length_ms": int(t["durata"] * 1000), "force_instrumental": True, "model_id": "music_v1"})
        else:
            dati = chiama("/v1/sound-generation", {"text": t["prompt"], "duration_seconds": t["durata"], "prompt_influence": 0.6})
        f.write_bytes(dati)
        normalizza(f, lufs)
        print("ok", f.relative_to(base), f"{f.stat().st_size // 1024} KB")
