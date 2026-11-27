# Il Diario del Cardinale — caccia lovecraftiana a Frascati

Web app statica (HTML/CSS/JS vanilla + Leaflet vendorizzato), pensata per telefono. 6 giocatori, 3 squadre da 2 (Nyarlathotep, Dagon, Azathoth). Lingua: italiano. Tono: diretto.

## File
- `index.html`: tutto il gioco (stile, sprite pixel art, logica, minigiochi).
- `storia.json`: contenuti (tappe, enigmi, suggerimenti, coordinate, punteggi, filtro mappa).
- `genera_voci.py`: genera gli mp3 ElevenLabs in `audio/` (env `ELEVENLABS_API_KEY`, `VOCE_CARDINALE`, `VOCE_CUSTODE`, `VOCE_OMBRA`). Opzioni: `--voci [testo]` elenca le voci, `--campioni` una battuta di prova per personaggio, `--solo`, `--force`, `--v3`. Normalizza a -16 LUFS. Regia per personaggio in `storia.json` → `audio.regia`. Fallback: speechSynthesis del browser.
- `genera_musica.py`: genera le 6 tracce (`audio/musica/`: tema, esplorazione, enigma, tensione, sala, vittoria) e 5 effetti (`audio/sfx/`: segno, ok, ko, ruggito, porta) dai prompt in `storia.json` → `audio.musica` / `audio.effetti`. Se un file manca il gioco resta in silenzio (gli effetti tornano ai bip sintetici).
- `pubblica_herenow.py`: pubblicazione anonima su here.now.
- `vendor/`: Leaflet e font (offline).
- `mostri/<id>/`: clip dei combattimenti (`intro`, `ok_1`, `ok_2`, `ko`, `vittoria`.mp4). Ora sono segnaposto pixel art.
- `mostri/SCENEGGIATURA.md`: storyboard e prompt per generare i video con l'AI.
- `prepara_video.py`: converte le clip AI (540x960 H.264, audio mono) e ne estrae primo/ultimo fotogramma.
- `genera_segnaposto.py`: rigenera le clip provvisorie (sovrascrive `mostri/`).

## Stato
- Tappe: 1 Piazza Marconi (tessere scorrevoli, VILLA), 2 Scuderie Aldobrandini (ruota Cesare, OCCHIO), 3 Cattedrale (lucchetto a 4 ruote, codice 8427, CORONA), 4 Chiesa del Gesù (specchio Atbash VXL, ECO), finale (barili 3/5 L, VOCE). Ogni squadra ha un ordine diverso delle tappe.
- Punti: 100 per enigma, -20 per suggerimento, -10 per errore. Penalità tempo: suggerimento +120 s, errore +60 s.
- Mostri: combattimenti a film interattivo (QTE) tra le tappe. Ogni squadra ne incontra 2, sulle tratte 1 e 3 (`squadre[].mostri` in storia.json): compaiono a circa metà strada (distanza ≤ 55% di quella iniziale) o, se non è successo, all'arrivo. Gesti: scorrere su/giù/sinistra/destra o toccare; da tastiera frecce e spazio. Errore → clip `ko`, Sanità -15, si riprova; 2 sconfitte → fuga (-10). Vittoria → +50 punti e una reliquia. Se un video manca si vede lo sprite: il gioco non si blocca.
- Cutscene: 6 scene in pixel art animate dal codice (`SCENE` in index.html, tela 120x160, nessun file video): `intro` dopo la scelta squadra, `t1`-`t4` dopo aver risolto ogni tappa (legate alla tappa, quindi valgono per tutti gli ordini), `finale` prima della schermata finale. Didascalie in `storia.json` → `cutscene`. Tasto Salta, poi Continua; con `prefers-reduced-motion` si vede il fotogramma finale. In `?test` ci sono i pulsanti "Scena …" per rivederle.
- Musica (index.html, sezione "Musica"): Web Audio, loop con sovrapposizione di 3 s, dissolvenze tra tracce, volume al 30% mentre parla una voce, pulsante muto nella barra (preferenza in localStorage `diario_mus_off`). Mappa: schermata iniziale → tema; viaggio/frammento → esplorazione; enigma → enigma; scontro → tensione; finale → sala; fine partita → vittoria. Parte al primo tocco (iOS).
- Sanità: parte da 100. Errore -5. Sotto 60 il testo trema, sotto 30 lo schermo si arrossa. Con poca Sanità le finestre dei gesti si accorciano fino al 70%. Punteggio finale = punti + Sanità.
- Reliquie: Rosario d'osso (+25 Sanità), Lanterna cieca (suggerimento senza penalità), Sale benedetto (salta un mostro senza premio).
- Test: aggiungere `?test` all'URL (simula presenza, reset, tocco sulla mappa per leggere le coordinate, "fai apparire il mostro"). `?test&lento` triplica le finestre dei gesti. In `?test` ogni enigma ha "Test: salta questo gioco" (risolve e invia la risposta giusta, con i punti normali) e ogni scontro ha "Test: salta lo scontro" (vittoria con reliquia).
- Stato in localStorage `diario_cardinale_v2`.

## Da fare
1. Pubblicato su GitHub Pages dal branch `main`: https://alexbonti.github.io/storiesalive/ (GPS richiede https).
2. Generare gli mp3 con `genera_voci.py` (include le frasi dei mostri, voce Ombra) e musica/effetti con `genera_musica.py`. Prima scegliere le voci: `--voci italian`, poi `--campioni`.
2b. Generare i video dei mostri seguendo `mostri/SCENEGGIATURA.md`, poi `prepara_video.py`.
3. Sopralluogo: verificare coordinate (Piazza Marconi, Scuderie, finale), orari Scuderie, lapide in cattedrale, falsa cupola del Gesù, fraschetta del finale.
4. Aggiornare documento e slide con i nuovi enigmi.
5. Idee: più giochi interattivi in stile Professor Layton, battute tra personaggi.

## Convenzioni
- Nessuna dipendenza esterna a runtime. Font e Leaflet restano in `vendor/`.
- Mappa: tessere OSM con filtro CSS verde (CARTO richiede chiave, non usarlo).
- Prima di consegnare: provare con Playwright a 390x780, nessun errore in console.
