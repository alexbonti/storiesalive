#!/usr/bin/env python3
"""Progetta le voci dei personaggi con ElevenLabs Voice Design, a partire dalle descrizioni in storia.json.

Uso:
  export ELEVENLABS_API_KEY="..."
  python3 crea_voci.py anteprime [cardinale|custode|ombra ...]    genera 3 anteprime a testa in audio/_campioni/voci/
  python3 crea_voci.py salva cardinale 2                           salva l'anteprima n.2 come voce permanente e scrive l'id in storia.json
  python3 genera_voci.py                                           usa gli id salvati (o VOCE_* nell'ambiente)

La descrizione di ogni personaggio è in storia.json → audio.regia.<nome>.descrizione. Cambiala e rigenera le anteprime
finché la voce non ti convince. Le anteprime provano il testo reale di una battuta del gioco.
"""
import base64, json, os, pathlib, sys, urllib.error, urllib.request

BASE = os.environ.get("ELEVENLABS_BASE", "https://api.elevenlabs.io")
KEY = os.environ.get("ELEVENLABS_API_KEY", "")
base = pathlib.Path(__file__).parent
STORIA = base / "storia.json"
d = json.load(open(STORIA, encoding="utf-8"))
A = d["audio"]
cart = base / "audio" / "_campioni" / "voci"


def chiama(percorso, corpo):
    req = urllib.request.Request(BASE + percorso, method="POST", data=json.dumps(corpo).encode(),
                                 headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Errore {e.code} da {percorso}: {e.read().decode('utf-8', 'replace')[:500]}")


def testo_prova(chi):
    """Battute vere del gioco, almeno 110 caratteri (minimo richiesto dall'API)."""
    if chi == "cardinale":
        return d["tappe"][0]["frammento"]
    if chi == "ombra":
        return d["finale"]["frammento"] + " " + d["mostri"][1]["frase"]
    t = ""
    for tp in d["tappe"]:
        for h in tp["suggerimenti"]:
            t += h + " "
            if len(t) >= 110:
                return t.strip()
    return t.strip()


def anteprime(chi):
    r = A["regia"][chi]
    corpo = {"voice_description": r["descrizione"] + " Italiano madrelingua, registrazione pulita da studio, adatta a una narrazione di audiogioco.",
             "text": testo_prova(chi), "model_id": "eleven_multilingual_ttv_v2"}
    ris = chiama("/v1/text-to-voice/design", corpo)
    cart.mkdir(parents=True, exist_ok=True)
    mappa = json.load(open(cart / "mappa.json")) if (cart / "mappa.json").exists() else {}
    mappa[chi] = []
    for i, p in enumerate(ris["previews"], 1):
        f = cart / f"{chi}_{i}.mp3"
        f.write_bytes(base64.b64decode(p["audio_base_64"]))
        mappa[chi].append(p["generated_voice_id"])
        print(f"  {f.relative_to(base)}  ({p.get('duration_secs', 0):.1f} s)")
    json.dump(mappa, open(cart / "mappa.json", "w"), indent=1)


def salva(chi, n):
    mappa = json.load(open(cart / "mappa.json"))
    gid = mappa[chi][n - 1]
    r = A["regia"][chi]
    ris = chiama("/v1/text-to-voice", {"voice_name": "Diario del Cardinale - " + chi.capitalize(), "voice_description": r["descrizione"],
                                        "generated_voice_id": gid})
    r["voice_id"] = ris["voice_id"]
    json.dump(d, open(STORIA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Voce salvata: {ris['voice_id']} ({chi}). Scritta in storia.json → audio.regia.{chi}.voice_id")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not KEY:
        sys.exit("Manca ELEVENLABS_API_KEY.")
    if a[:1] == ["anteprime"]:
        for chi in (a[1:] or ["cardinale", "custode", "ombra"]):
            print(chi)
            anteprime(chi)
    elif a[:1] == ["salva"] and len(a) == 3:
        salva(a[1], int(a[2]))
    else:
        sys.exit(__doc__)
