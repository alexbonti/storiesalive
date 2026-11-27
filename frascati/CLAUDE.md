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
- `../trailer/`: trailer di 45 s in stile spot anni '80 (pixel art 320x180 → MP4 1280x720). `trailer.html` disegna tutto dal codice riusando gli sprite di `frascati/index.html` (si vede nel browser; `?t=12.5` mostra un fotogramma). `genera_audio.py` crea voce da annunciatore, musica synthwave ed effetti con ElevenLabs (testi, tempi e cue in `trailer.json`). `render.js` esporta il video, `mix.py` mixa l'audio e produce `trailer.mp4`. Per rifarlo: `node render.js /tmp/v.mp4 && python3 mix.py /tmp/v.mp4 trailer.mp4`. Se cambi una scena o un tempo di `trailer.json`, rifai entrambi i passi.

## Stato
- Tappe: 1 Piazza Marconi (tessere scorrevoli, VILLA), 2 Scuderie Aldobrandini (percorso del cavallo su scacchiera 5x5, OCCHIO; trappola: OCCASO), 3 Cattedrale (lucchetto a 4 ruote, codice 8427, CORONA), 4 Chiesa del Gesù (specchio Atbash VXL, ECO), 5 Piazza San Rocco (nove calici e bilancia, due pesate, CONTAGIO; nessuna lettera, dà il Rosario), finale al Ristorante Pasquino (barili 3/5 L, VOCE dalle lettere V O C E). Ogni squadra ha un ordine diverso: Nyarlathotep 1-2-5-3-4, Dagon 3-1-4-2-5, Azathoth 5-4-3-2-1.
- Cavallo (tappa 2): la scacchiera è in `storia.json` (`griglia`, `partenza`, `parola`, `trappole`), generata con uno script che garantisce una sola strada per OCCHIO e una per OCCASO. Per cambiarla servono una nuova griglia e la verifica che i percorsi di 6 caselle spellino la parola una volta sola. Il cavallo non penalizza i tentativi.
- Calici (tappa 5): il calice avvelenato è casuale e si rimescola a ogni errore (-1 minuto, Sanità -5). Tre errori non bloccano il gioco.
- Punti: 100 per enigma, -20 per suggerimento, -10 per errore. Penalità tempo: suggerimento +120 s, errore +60 s.
- Mostri: combattimenti a film interattivo (QTE) tra le tappe. Ogni squadra ne incontra 3, tutti e tre i tipi (`squadre[].mostri` in storia.json: la chiave è la tratta, la numero 0 è quella verso la prima tappa): compaiono a circa metà strada (distanza ≤ 55% di quella iniziale) o, se non è successo, all'arrivo. Gesti: scorrere su/giù/sinistra/destra o toccare; da tastiera frecce e spazio. Errore → clip `ko`, Sanità -15, si riprova; 2 sconfitte → fuga (-10). Vittoria → +50 punti e una reliquia. Se un video manca si vede lo sprite: il gioco non si blocca.
- Cutscene: 6 scene in pixel art animate dal codice (`SCENE` in index.html, tela 120x160, nessun file video): `intro` dopo la scelta squadra, `t1`-`t4` dopo aver risolto ogni tappa (legate alla tappa, quindi valgono per tutti gli ordini), `finale` prima della schermata finale. Didascalie in `storia.json` → `cutscene`. Tasto Salta, poi Continua; con `prefers-reduced-motion` si vede il fotogramma finale. In `?test` ci sono i pulsanti "Scena …" per rivederle.
- Musica (index.html, sezione "Musica"): Web Audio, loop con sovrapposizione di 3 s, dissolvenze tra tracce, volume al 30% mentre parla una voce, pulsante muto nella barra (preferenza in localStorage `diario_mus_off`). Mappa: schermata iniziale → tema; viaggio/frammento → esplorazione; enigma → enigma; scontro → tensione; finale → sala; fine partita → vittoria. Parte al primo tocco (iOS).
- Sanità: parte da 100. Errore -5. Sotto 60 il testo trema, sotto 30 lo schermo si arrossa. Con poca Sanità le finestre dei gesti si accorciano fino al 70%. Punteggio finale = punti + Sanità.
- Reliquie: Rosario d'osso (+25 Sanità), Lanterna cieca (suggerimento senza penalità), Sale benedetto (salta un mostro senza premio).
- Test: aggiungere `?test` all'URL (simula presenza, reset, tocco sulla mappa per leggere le coordinate, "fai apparire il mostro"). `?test&lento` triplica le finestre dei gesti. In `?test` ogni enigma ha "Test: salta questo gioco" (risolve e invia la risposta giusta, con i punti normali) e ogni scontro ha "Test: salta lo scontro" (vittoria con reliquia).
- Stato in localStorage `diario_cardinale_v2`. Tasto Ricomincia (icona freccia circolare) nella barra in alto durante la partita, e a fine gioco: chiede conferma, cancella lo stato e ricarica. La preferenza della musica resta.

## Da fare
1. Pubblicato su GitHub Pages dal branch `main`: https://alexbonti.github.io/storiesalive/ (GPS richiede https).
2. Fatto: 25 voci in `audio/*.mp3`, 6 tracce in `audio/musica/`, 5 effetti in `audio/sfx/`. Voci della libreria ElevenLabs (id in `storia.json` → `audio.regia.<nome>.voice_id`): Cardinale = Elian, Custode = Paolo Margari, Ombra = Tommaso Eramo; scelte senza ascolto, da verificare. L'account ElevenLabs ha 10/10 voci personalizzate, quindi `crea_voci.py salva` fallisce finché non si libera un posto. Per cambiare una voce: modificare il `voice_id` e rilanciare `genera_voci.py --force --solo ...`. In questo ambiente la chiave vive nel proxy: usare `ELEVENLABS_API_KEY=proxy-injected`.
2b. Generare i video dei mostri seguendo `mostri/SCENEGGIATURA.md`, poi `prepara_video.py`.
3. Sopralluogo: verificare coordinate (Piazza Marconi, Scuderie, Piazza San Rocco, finale). Piazza San Rocco (41.80964, 12.67927) viene da una fonte esterna, non è ancora controllata sul posto: confermarla con `?test`, orari Scuderie, lapide in cattedrale, falsa cupola del Gesù. Il finale è al Ristorante Pasquino (Via Sepolcro di Lucullo 6): coordinate stimate (41.8069, 12.6824), da correggere sul posto con `?test`; avvisare il gestore, controllare orari e prenotare per 6.
4. Aggiornare documento e slide con i nuovi enigmi.
5. Idee: più giochi interattivi in stile Professor Layton, battute tra personaggi.

## Convenzioni
- Nessuna dipendenza esterna a runtime. Font e Leaflet restano in `vendor/`.
- Mappa: tessere OSM con filtro CSS verde (CARTO richiede chiave, non usarlo).
- Prima di consegnare: provare con Playwright a 390x780, nessun errore in console.
