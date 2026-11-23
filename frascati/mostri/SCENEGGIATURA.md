# Combattimenti: sceneggiatura per i video AI

Ogni mostro è un piccolo film interattivo, girato tutto in **prima persona** (la telecamera è la squadra).
Il film si ferma sull'ultimo fotogramma di ogni clip: lì compare il segno e i giocatori hanno circa un secondo e mezzo per fare il gesto.

```
intro ──► [K1: gesto 1] ──ok_1──► [K2: gesto 2] ──ok_2──► [K3: gesto 3] ──vittoria──► fine
              │                        │                        │
              └────────── ko (qualunque gesto sbagliato o tempo scaduto) ──────────┘
```

Per ogni mostro servono **5 clip**: `intro`, `ok_1`, `ok_2`, `ko` e `vittoria`.
In tutto fanno 15 clip per tre mostri.

## Regole che contano

1. **Prima le immagini, poi i video.** Generate per ogni mostro un'immagine di riferimento e le 5 immagini chiave (A, K1, K2, K3, V) descritte sotto. Poi generate ogni clip con la funzione *da immagine a video* indicando **fotogramma iniziale e finale**.
2. **Le clip si agganciano.** La clip che finisce su K1 è `intro`, e da K1 partono sia `ok_1` sia `ko`. Se il generatore non rispetta bene il fotogramma finale, convertite la clip con `prepara_video.py`: salva l'ultimo fotogramma vero (`*_ultimo.png`), da usare come partenza della clip seguente.
3. **Fermi negli ultimi 0,5 secondi.** Ogni clip che finisce su un momento decisivo deve chiudere con il mostro *fermo a metà gesto*, un istante prima di colpire. Aggiungete al prompt: *"the creature freezes mid-motion and holds the pose for the last half second"*.
4. **Il mostro sempre uguale.** Riusate l'immagine di riferimento in ogni generazione e lo stesso blocco di stile.
5. **Centro dello schermo libero.** Il segno del gesto (un cerchio d'oro) compare al centro. Tenete il muso del mostro un po' più in alto o di lato.
6. **Verticale 9:16**, qualunque risoluzione: la conversione la fa lo script.

### Cosa vuol dire ogni gesto (serve a capire da dove arriva l'attacco)

| Gesto del giocatore | Cosa fa la squadra | Quindi il mostro attacca… |
|---|---|---|
| scorre a **destra** | schiva a destra | da **sinistra** dell'inquadratura |
| scorre a **sinistra** | schiva a sinistra | da **destra** |
| scorre **su** | salta | **basso**, strisciando verso la camera |
| scorre **giù** | si abbassa | **alto**, saltando dall'alto |
| **tocca** | gesto sacro (croce, luce, curva) | di **fronte**, vicinissimo |

### Blocco di stile (da copiare in ogni prompt)

> *Dark gothic illustration, old town of Frascati near Rome at night, 17th-century Italian stone buildings, narrow alley, wet cobblestones, single warm street lamp, deep green-black palette with gold and dark wine-red accents, heavy film grain, subtle flicker, vertical 9:16, first-person point of view at eye level, cinematic horror, no text, no people visible.*

I prompt sono in inglese perché i generatori video li seguono meglio. Se preferite il pixel art come nel resto del gioco, sostituite la prima frase con *"detailed 16-bit pixel art, limited palette"*.

---

## 1. Il Profondo (squadra Dagon e Azathoth)
Un uomo-pesce risalito dalle fontane. Pelle verde-nera lucida, occhi gialli enormi senza palpebre, branchie sul collo, mani palmate con artigli. Gocciola sempre.
Gesti: **destra → giù → tocco**. Premio: *Sale benedetto*.

**Riferimento:** *full-body concept of a fish-like humanoid creature, glossy green-black skin, huge yellow lidless eyes, gills on the neck, webbed clawed hands, dripping water, hunched posture, [stile]*

| Immagine | Descrizione |
|---|---|
| A | Vicolo vuoto, una fontanella di pietra a sinistra, l'acqua esce *verso l'alto*. |
| K1 | Il Profondo a sinistra, vicinissimo, braccio alzato con gli artigli pronti a colpire verso destra. |
| K2 | Il Profondo in alto, su un balcone o un arco, piegato e pronto a saltare giù sulla camera. |
| K3 | Il Profondo di fronte, a un metro, a braccia spalancate, bocca aperta. |
| V | La fontanella, una pozza d'acqua nera che si ritira in un tombino. Vicolo vuoto. |

| Clip | Durata | Da → a | Gesto atteso alla fine | Prompt |
|---|---|---|---|---|
| `intro` | 4–6 s | A → K1 | destra | *The water of the stone fountain flows upward, then a fish-like creature rises from the basin and lunges in from the left side of the frame, raising its clawed hand to strike. The creature freezes mid-motion and holds the pose for the last half second. [stile]* |
| `ok_1` | 3–4 s | K1 → K2 | giù | *The camera dodges quickly to the right, the claw slashes past and hits the wall. The creature climbs fast up onto a stone balcony above and crouches, ready to leap down at the camera. Freezes mid-motion for the last half second. [stile]* |
| `ok_2` | 3–4 s | K2 → K3 | tocco | *The camera ducks, the creature leaps over and lands in front of the camera, rising to its full height with arms wide open and mouth gaping. Freezes mid-motion for the last half second. [stile]* |
| `ko` | 2–3 s | (qualunque) → nero | — | *The creature suddenly lunges straight into the camera, filling the frame, water splashing, the image turns dark red then cuts to black. [stile]* |
| `vittoria` | 4–5 s | K3 → V | — | *A golden light like a crucifix glow hits the creature, it screams silently and melts into black water that drains away into a sewer grate. The alley is empty and quiet. [stile]* |

---

## 2. L'Ombra del Cardinale (squadra Nyarlathotep e Dagon)
L'ombra che il cardinale lasciò nella galleria. Una sagoma piatta da cardinale (zucchetto, mantella), nera con riflessi viola, occhi verdi pallidi. Si muove sui muri e sul selciato come un'ombra vera.
Gesti: **sinistra → su → tocco**. Premio: *Rosario d'osso*.

**Riferimento:** *a flat living shadow shaped like a 17th-century cardinal with skullcap and cape, pitch black with faint purple sheen, two pale green glowing eyes, it lies on walls and floors like a real shadow but moves on its own, [stile]*

| Immagine | Descrizione |
|---|---|
| A | Vicolo con un lampione acceso a destra; sul muro di destra un'ombra di troppo. |
| K1 | L'ombra si stacca dal muro di destra, mezza fuori, mani lunghe tese verso la camera. |
| K2 | L'ombra stesa sul selciato, che striscia velocissima verso i piedi della camera. |
| K3 | L'ombra in piedi di fronte, altissima, la mantella aperta che copre il lampione. |
| V | Il lampione brilla forte, una crepa nel muro, il vicolo vuoto. |

| Clip | Durata | Da → a | Gesto atteso alla fine | Prompt |
|---|---|---|---|---|
| `intro` | 4–6 s | A → K1 | sinistra | *The street lamp flickers. On the right wall there is one shadow too many, shaped like a cardinal. Its eyes open, pale green, and it peels itself off the wall, reaching out with long arms from the right side of the frame. Freezes mid-motion for the last half second. [stile]* |
| `ok_1` | 3–4 s | K1 → K2 | su | *The camera dodges to the left, the shadow hands grab the empty air. The shadow drops flat onto the cobblestones and slides fast along the ground toward the camera's feet. Freezes mid-motion for the last half second. [stile]* |
| `ok_2` | 3–4 s | K2 → K3 | tocco | *The camera jumps, the shadow passes underneath, then rises in front of the camera, towering, its cape spreading wide and covering the light of the lamp. Freezes mid-motion for the last half second. [stile]* |
| `ko` | 2–3 s | (qualunque) → nero | — | *The shadow wraps around the camera like a black cloth, everything goes dark purple then black, two green eyes linger for a moment. [stile]* |
| `vittoria` | 4–5 s | K3 → V | — | *The street lamp suddenly blazes with bright warm light, the shadow shrinks, twists and is sucked back into a crack in the stone wall. The alley is empty and quiet. [stile]* |

---

## 3. Il cane di Tindalos (squadra Nyarlathotep e Azathoth)
Viene dagli angoli acuti. Magro, scheletrico, fatto di spigoli e fumo blu-grigio, lingua lunga e affilata. Si muove a scatti, come se mancassero dei fotogrammi.
Gesti: **giù → destra → tocco**. Premio: *Lanterna cieca*.

**Riferimento:** *an emaciated angular hound-like creature made of sharp edges and blue-grey smoke, no fur, long needle-like tongue, glowing pale yellow eyes, it moves in jerky stuttering motion, [stile]*

| Immagine | Descrizione |
|---|---|
| A | Vicolo con lo spigolo vivo di un palazzo in primo piano a sinistra. Fumo blu che esce dall'angolo. |
| K1 | Il cane sopra la camera, uscito dallo spigolo in alto, in pieno salto verso il basso. |
| K2 | Il cane a sinistra, basso, pronto a balzare verso destra da un angolo di un portone. |
| K3 | Il cane di fronte, ringhiante, lingua fuori, a un metro. |
| V | Un angolo del muro, il fumo che si ripiega dentro come risucchiato. |

| Clip | Durata | Da → a | Gesto atteso alla fine | Prompt |
|---|---|---|---|---|
| `intro` | 4–6 s | A → K1 | giù | *Blue-grey smoke pours out of the sharp corner of a stone building. An angular hound-like creature unfolds from the corner high above, in stuttering jerky motion, and leaps down toward the camera. Freezes mid-leap for the last half second. [stile]* |
| `ok_1` | 3–4 s | K1 → K2 | destra | *The camera ducks, the creature flies overhead and lands behind, then appears again from the sharp corner of a doorway on the left, low and ready to spring to the right. Freezes mid-motion for the last half second. [stile]* |
| `ok_2` | 3–4 s | K2 → K3 | tocco | *The camera dodges to the right, the creature skids on the cobblestones, turns and faces the camera, snarling, long tongue out. Freezes mid-motion for the last half second. [stile]* |
| `ko` | 2–3 s | (qualunque) → nero | — | *The creature jumps at the camera, its tongue shoots forward, the frame cracks into sharp angular shards, then black. [stile]* |
| `vittoria` | 4–5 s | K3 → V | — | *A perfectly round silver mirror is raised in front of the camera, the creature recoils from the curve, folds into sharp angles and is sucked back into the corner of the wall like smoke. The alley is empty. [stile]* |

---

## Come portarli nel gioco

1. Salvate le clip grezze, per esempio in `grezzi/profondo/intro.mp4`. Fuori dal repo va benissimo.
2. Lanciate la conversione:
   ```bash
   python3 prepara_video.py profondo grezzi/profondo/
   ```
   Per tagliare una clip: `python3 prepara_video.py profondo grezzi/profondo/ok_1.mp4 --taglia 0.3:4.2`
3. Il risultato finisce in `mostri/profondo/` e sostituisce le clip provvisorie. Provate con `index.html?test`, poi "Test: fai apparire il mostro". Con `?test&lento` le finestre durano il triplo.
4. Se una mossa arriva troppo presto o troppo tardi, cambiate `finestra` (in millisecondi) del passo in `storia.json`.

**Peso:** sotto i 4 MB per mostro (lo script avvisa). Le clip vengono scaricate mentre la squadra cammina verso il mostro.
**Audio:** se il generatore crea il sonoro, lo script lo tiene; con `--muto` lo toglie.
**Rigenerare le clip provvisorie:** `python3 genera_segnaposto.py`. Attenzione: sovrascrive tutto in `mostri/`.
