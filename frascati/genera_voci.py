#!/usr/bin/env python3
"""Genera gli mp3 delle voci con ElevenLabs e li salva in audio/.

Uso:
  export ELEVENLABS_API_KEY="..."        # la tua chiave (non metterla mai nella pagina web)
  export VOCE_CARDINALE="<voice_id>"     # voce del Cardinale
  export VOCE_CUSTODE="<voice_id>"       # voce del Custode
  export VOCE_OMBRA="<voice_id>"         # voce dell'Ombra
  python3 genera_voci.py [--force]

Gli id delle voci si copiano dalla libreria voci di ElevenLabs (Voice ID).
Se un mp3 manca, la pagina usa la voce del telefono come ripiego.
"""
import json, os, sys, urllib.request, pathlib

KEY = os.environ.get("ELEVENLABS_API_KEY")
VOCI = {k: os.environ.get("VOCE_" + k.upper()) for k in ("cardinale", "custode", "ombra")}
MODEL = "eleven_multilingual_v2"
force = "--force" in sys.argv
base = pathlib.Path(__file__).parent
out = base / "audio"; out.mkdir(exist_ok=True)
d = json.load(open(base / "storia.json", encoding="utf-8"))

jobs = [(d["intro"]["id"], d["intro"]["personaggio"], d["intro"]["testo"]),
        (d["chiusura"]["id"], d["chiusura"]["personaggio"], d["chiusura"]["testo"])]
for t in d["tappe"] + [d["finale"]]:
    jobs.append((t["id"] + "_frammento", t["personaggio"], t["frammento"]))
    for i, h in enumerate(t["suggerimenti"], 1):
        jobs.append((f"{t['id']}_sugg{i}", "custode", h))

if not KEY or not all(VOCI.values()):
    sys.exit("Mancano ELEVENLABS_API_KEY o gli id delle voci (VOCE_CARDINALE, VOCE_CUSTODE, VOCE_OMBRA).")

for id_, chi, testo in jobs:
    f = out / (id_ + ".mp3")
    if f.exists() and not force:
        print("salto", f.name); continue
    body = json.dumps({"text": testo, "model_id": MODEL,
                       "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.3}}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOCI[chi]}?output_format=mp3_44100_128",
        data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req) as r:
        f.write_bytes(r.read())
    print("ok", f.name)
