#!/usr/bin/env python3
"""Prepara i video generati con l'AI per i combattimenti.

Prende le clip grezze (mp4, mov, webm…), le porta a 540x960 verticale, H.264 leggero
con audio mono, e le salva in mostri/<id>/ con il nome che il gioco si aspetta.
Per ogni clip salva anche il primo e l'ultimo fotogramma come PNG accanto al file
grezzo: l'ultimo è l'immagine da cui generare la clip successiva.

Uso:
  python3 prepara_video.py profondo grezzi/profondo/
      converte tutti i file della cartella. I nomi devono iniziare come le clip:
      intro, ok_1, ok_2, ko, vittoria (es. "ok_1 v3.mp4" va bene).
  python3 prepara_video.py profondo grezzi/profondo/intro.mp4 --taglia 0.4:5.8
      converte un solo file, tenendo solo da 0,4 s a 5,8 s.
  python3 prepara_video.py --fotogrammi grezzi/profondo/intro.mp4
      estrae solo primo e ultimo fotogramma, senza convertire.

Opzioni: --taglia INIZIO:FINE (secondi, uno dei due può mancare), --muto (toglie l'audio),
--qualita N (CRF, default 26: più alto = più leggero).
Richiede ffmpeg.
"""
import argparse, json, pathlib, subprocess, sys

base = pathlib.Path(__file__).parent
ESTENSIONI = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
NOMI = ["intro", "ok_1", "ok_2", "ok_3", "ok_4", "attesa_1", "attesa_2", "attesa_3", "attesa_4", "ko_1", "ko_2", "ko_3", "ko", "vittoria"]


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def ha_audio(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def fotogrammi(f):
    f = pathlib.Path(f)
    primo, ultimo = f.with_name(f.stem + "_primo.png"), f.with_name(f.stem + "_ultimo.png")
    ff("-i", str(f), "-frames:v", "1", str(primo))
    ff("-sseof", "-0.25", "-i", str(f), "-update", "1", str(ultimo))
    print(f"  fotogrammi: {primo.name}, {ultimo.name}")


def nome_clip(f):
    s = f.stem.lower().replace(" ", "_").replace("-", "_")
    for n in sorted(NOMI, key=len, reverse=True):
        if s.startswith(n):
            return n
    return None


def converti(mid, f, taglia=None, muto=False, crf=26):
    n = nome_clip(f)
    if not n:
        print(f"  salto {f.name}: il nome deve iniziare con uno di {', '.join(NOMI)}")
        return 0
    out_dir = base / "mostri" / mid
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (n + ".mp4")
    pre = []
    if taglia:
        a, _, b = taglia.partition(":")
        if a:
            pre += ["-ss", a]
        if b:
            pre += ["-to", b]
    vf = "scale=540:960:force_original_aspect_ratio=increase,crop=540:960,fps=24"
    audio = ["-an"] if muto or not ha_audio(f) else ["-c:a", "aac", "-b:a", "80k", "-ac", "1"]
    ff(*pre, "-i", str(f), "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-profile:v", "main",
       "-pix_fmt", "yuv420p", "-movflags", "+faststart", *audio, str(out))
    kb = out.stat().st_size // 1024
    print(f"  {f.name} -> {out.relative_to(base)}  {kb} KB")
    fotogrammi(f)
    return kb


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mostro", nargs="?", help="id del mostro (profondo, ombra, tindalos…)")
    ap.add_argument("sorgenti", nargs="*", help="file o cartelle di clip grezze")
    ap.add_argument("--taglia")
    ap.add_argument("--muto", action="store_true")
    ap.add_argument("--qualita", type=int, default=26)
    ap.add_argument("--fotogrammi", action="store_true")
    a = ap.parse_args()

    if a.fotogrammi:
        for s in ([a.mostro] if a.mostro else []) + a.sorgenti:
            fotogrammi(s)
        return
    ids = [m["id"] for m in json.loads((base / "storia.json").read_text(encoding="utf-8"))["mostri"]]
    if a.mostro not in ids:
        sys.exit(f"Mostro sconosciuto: {a.mostro}. In storia.json ci sono: {', '.join(ids)}")
    files = []
    for s in map(pathlib.Path, a.sorgenti):
        files += sorted(x for x in s.iterdir() if x.suffix.lower() in ESTENSIONI) if s.is_dir() else [s]
    if a.taglia and len(files) > 1:
        sys.exit("--taglia funziona con un file alla volta.")
    tot = sum(converti(a.mostro, f, a.taglia, a.muto, a.qualita) for f in files)
    print(f"Totale convertito: {tot} KB")
    tutto = sum(f.stat().st_size for f in (base / "mostri" / a.mostro).glob("*.mp4")) // 1024
    print(f"Peso del mostro {a.mostro}: {tutto} KB" + ("  ATTENZIONE: oltre 4 MB, alzate --qualita" if tutto > 4096 else ""))


if __name__ == "__main__":
    main()
