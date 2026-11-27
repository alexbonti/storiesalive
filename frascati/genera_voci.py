#!/usr/bin/env python3
"""Genera gli mp3 delle voci con ElevenLabs e li salva in audio/.

Uso:
  export ELEVENLABS_API_KEY="..."        # la tua chiave (mai nella pagina web)
  export VOCE_CARDINALE="<voice_id>" VOCE_CUSTODE="<voice_id>" VOCE_OMBRA="<voice_id>"

  python3 genera_voci.py --voci [testo]        elenca le voci disponibili (filtra per testo, es. "italian")
  python3 genera_voci.py                       genera le battute mancanti
  python3 genera_voci.py --force               rigenera tutto
  python3 genera_voci.py --solo intro,t1_frammento   solo queste battute
  python3 genera_voci.py --campioni            1 battuta di prova per personaggio in audio/_campioni/
  python3 genera_voci.py --v3                  modello eleven_v3: più espressivo, usa i tag ([whispers]...)

La regia (stabilità, stile, velocità, tag) sta in storia.json → audio.regia.
Dopo la generazione le battute vengono normalizzate a -16 LUFS e ripulite dal silenzio iniziale (serve ffmpeg).
Se un mp3 manca, la pagina usa la voce del telefono come ripiego.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request

BASE = os.environ.get("ELEVENLABS_BASE", "https://api.elevenlabs.io")
KEY = os.environ.get("ELEVENLABS_API_KEY")
FORMATO = os.environ.get("FORMATO", "mp3_44100_128")        # con piano Creator o superiore: mp3_44100_192
base = pathlib.Path(__file__).parent
d = json.load(open(base / "storia.json", encoding="utf-8"))
A = d["audio"]
argv = sys.argv[1:]
v3 = "--v3" in argv
MODEL = "eleven_v3" if v3 else A.get("modello_voce", "eleven_multilingual_v2")


def chiama(metodo, percorso, corpo=None, params=None):
    url = BASE + percorso + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, method=metodo, headers={"xi-api-key": KEY or "", "Content-Type": "application/json", "Accept": "*/*"},
                                 data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Errore {e.code} da {percorso}: {e.read().decode('utf-8', 'replace')[:400]}")


def normalizza(f):
    if not shutil.which("ffmpeg"):
        return
    tmp = pathlib.Path(tempfile.mkdtemp()) / "n.mp3"
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", str(f), "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=11,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05",
                    "-ar", "44100", "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True, timeout=180)
    shutil.move(str(tmp), str(f))


def elenco_voci(filtro):
    voci = json.loads(chiama("GET", "/v1/voices"))["voices"]
    for v in voci:
        lab = v.get("labels", {})
        riga = " ".join(str(x) for x in [v.get("name"), lab.get("accent"), lab.get("gender"), lab.get("age"), lab.get("descriptive"), lab.get("use_case"), v.get("category")] if x)
        if not filtro or filtro.lower() in (riga + " " + json.dumps(v.get("verified_languages", []))).lower():
            print(f"{v['voice_id']}  {riga}")
            if v.get("preview_url"):
                print("    anteprima:", v["preview_url"])


if "--voci" in argv:
    i = argv.index("--voci")
    elenco_voci(argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else "")
    sys.exit()

VOCI = {k: os.environ.get("VOCE_" + k.upper()) or A["regia"][k].get("voice_id") for k in ("cardinale", "custode", "ombra")}   # ambiente oppure id salvato da crea_voci.py
jobs = [(d["intro"]["id"], d["intro"]["personaggio"], d["intro"]["testo"]),
        (d["chiusura"]["id"], d["chiusura"]["personaggio"], d["chiusura"]["testo"])]
for t in d["tappe"] + [d["finale"]]:
    jobs.append((t["id"] + "_frammento", t["personaggio"], t["frammento"]))
    for i, h in enumerate(t["suggerimenti"], 1):
        jobs.append((f"{t['id']}_sugg{i}", "custode", h))
for m in d.get("mostri", []):
    jobs.append(("mostro_" + m["id"], "ombra", m["frase"]))

out = base / "audio"
if "--campioni" in argv:
    out = out / "_campioni"
    prima = {}
    for id_, chi, testo in jobs:
        prima.setdefault(chi, (id_, chi, testo))
    jobs = list(prima.values())
if "--solo" in argv:
    voluti = set(argv[argv.index("--solo") + 1].split(","))
    jobs = [j for j in jobs if j[0] in voluti]
out.mkdir(parents=True, exist_ok=True)

if not KEY or not all(VOCI.values()):
    sys.exit("Mancano ELEVENLABS_API_KEY o gli id delle voci (VOCE_CARDINALE, VOCE_CUSTODE, VOCE_OMBRA, oppure python3 crea_voci.py).")

for id_, chi, testo in jobs:
    f = out / (id_ + ".mp3")
    if f.exists() and "--force" not in argv and "--campioni" not in argv:
        print("salto", f.name)
        continue
    r = A["regia"][chi]
    impost = {"stability": r["stabilita"], "similarity_boost": r["somiglianza"], "style": r["stile"], "use_speaker_boost": True, "speed": r["velocita"]}
    if v3:
        impost = {"stability": 0.5}                       # eleven_v3: 0 creativo, 0.5 naturale, 1 robusto
        testo = r.get("tag_v3", "") + testo
    audio = chiama("POST", f"/v1/text-to-speech/{VOCI[chi]}", {"text": testo, "model_id": MODEL, "language_code": "it", "voice_settings": impost},
                   {"output_format": FORMATO})
    f.write_bytes(audio)
    normalizza(f)
    print("ok", f.relative_to(base), f"{f.stat().st_size // 1024} KB")
