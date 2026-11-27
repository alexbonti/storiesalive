#!/usr/bin/env python3
"""Genera l'audio del trailer con ElevenLabs: voce da annunciatore, musica synthwave e gli effetti.

Uso (la chiave sta nel proxy dell'ambiente: ELEVENLABS_API_KEY=proxy-injected):
  python3 genera_audio.py            genera i file mancanti in audio/
  python3 genera_audio.py --force    rigenera tutto
  python3 genera_audio.py --solo vo3,boom
I testi e i tempi sono in trailer.json.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request, urllib.error

BASE = os.environ.get("ELEVENLABS_BASE", "https://api.elevenlabs.io")
KEY = os.environ.get("ELEVENLABS_API_KEY", "")
aqui = pathlib.Path(__file__).parent
T = json.load(open(aqui / "trailer.json", encoding="utf-8"))
out = aqui / "audio"; out.mkdir(exist_ok=True)
argv = sys.argv[1:]
solo = set(argv[argv.index("--solo") + 1].split(",")) if "--solo" in argv else None


def chiama(percorso, corpo):
    req = urllib.request.Request(BASE + percorso + "?output_format=mp3_44100_128", method="POST", data=json.dumps(corpo).encode(),
                                 headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Errore {e.code} da {percorso}: {e.read().decode('utf-8', 'replace')[:300]}")


def norm(f, lufs):
    tmp = pathlib.Path(tempfile.mkdtemp()) / "n.mp3"
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(f), "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=9", "-ar", "44100", "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True, timeout=180)
    shutil.move(str(tmp), str(f))


def fai(id_, genera, lufs):
    f = out / (id_ + ".mp3")
    if solo and id_ not in solo:
        return
    if f.exists() and "--force" not in argv:
        print("salto", id_); return
    f.write_bytes(genera()); norm(f, lufs); print("ok", id_, f"{f.stat().st_size // 1024} KB")


for v in T["voce"]["battute"]:
    fai(v["id"], lambda v=v: chiama("/v1/text-to-speech/" + T["voce"]["voice_id"], {"text": v["testo"], "model_id": "eleven_multilingual_v2", "language_code": "en",
         "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.55, "use_speaker_boost": True, "speed": 1.0}}), -16)
fai("musica", lambda: chiama("/v1/music", {"prompt": T["musica"]["prompt"], "music_length_ms": T["musica"]["durata"] * 1000, "force_instrumental": True, "model_id": "music_v1"}), -18)
for e in T["effetti"]:
    fai(e["id"], lambda e=e: chiama("/v1/sound-generation", {"text": e["prompt"], "duration_seconds": e["durata"], "prompt_influence": 0.6}), -14)
