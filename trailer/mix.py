#!/usr/bin/env python3
"""Mixa voce, musica ed effetti (trailer.json) e li unisce al video.

Uso: python3 mix.py video.mp4 trailer.mp4
La musica si abbassa quando parla l'annunciatore (sidechain). Gli effetti marcati con @ vengono da ../frascati/audio/sfx/.
"""
import json, pathlib, subprocess, sys
aqui = pathlib.Path(__file__).parent
T = json.load(open(aqui / "trailer.json", encoding="utf-8"))
video, out = sys.argv[1], sys.argv[2]
DUR = T["durata"]
wav = out + ".tmp.wav"
inputs, filtri = [], []
def aggiungi(path, ritardo, vol):
    i = len(inputs) // 2; inputs.extend(["-i", str(path)])
    filtri.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay={int(ritardo*1000)}|{int(ritardo*1000)},volume={vol}[a{i}]")
    return f"[a{i}]"
mus = aggiungi(aqui / "audio" / "musica.mp3", 0, 0.95)
vo = [aggiungi(aqui / "audio" / (b["id"] + ".mp3"), b["t"], 1.0) for b in T["voce"]["battute"]]
fx = []
for c in T["cue"]:
    s = c["sfx"]; f = (aqui.parent / "frascati" / "audio" / "sfx" / (s[1:] + ".mp3")) if s.startswith("@") else aqui / "audio" / (s + ".mp3")
    fx.append(aggiungi(f, c["t"], c["vol"]))
filtri.append("".join(vo) + f"amix=inputs={len(vo)}:normalize=0:dropout_transition=0[vo]")
filtri.append("[vo]asplit=2[vo1][vo2]")
filtri.append(f"{mus}[vo1]sidechaincompress=threshold=0.02:ratio=7:attack=15:release=350:makeup=1[md]")
filtri.append("".join(fx) + f"amix=inputs={len(fx)}:normalize=0:dropout_transition=0,volume=0.9[fx]")
filtri.append(f"[md][vo2][fx]amix=inputs=3:normalize=0:dropout_transition=0,volume=0.85,alimiter=limit=0.95,atrim=0:{DUR},afade=t=out:st={DUR-0.25}:d=0.25[mix]")
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filtri), "-map", "[mix]", "-ar", "44100", wav], check=True)
subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), out], check=True)
pathlib.Path(wav).unlink(missing_ok=True)
print("scritto", out)
