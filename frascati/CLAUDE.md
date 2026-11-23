# Il Diario del Cardinale — caccia lovecraftiana a Frascati

Web app statica (HTML/CSS/JS vanilla + Leaflet vendorizzato), pensata per telefono. 6 giocatori, 3 squadre da 2 (Nyarlathotep, Dagon, Azathoth). Lingua: italiano. Tono: diretto.

## File
- `index.html`: tutto il gioco (stile, sprite pixel art, logica, minigiochi).
- `storia.json`: contenuti (tappe, enigmi, suggerimenti, coordinate, punteggi, filtro mappa).
- `genera_voci.py`: genera gli mp3 ElevenLabs in `audio/` (env `ELEVENLABS_API_KEY`, `VOCE_CARDINALE`, `VOCE_CUSTODE`, `VOCE_OMBRA`). Fallback: speechSynthesis del browser.
- `pubblica_herenow.py`: pubblicazione anonima su here.now.
- `vendor/`: Leaflet e font (offline).

## Stato
- Tappe: 1 Piazza Marconi (tessere scorrevoli, VILLA), 2 Scuderie Aldobrandini (ruota Cesare, OCCHIO), 3 Cattedrale (lucchetto a 4 ruote, codice 8427, CORONA), 4 Chiesa del Gesù (specchio Atbash VXL, ECO), finale (barili 3/5 L, VOCE). Ogni squadra ha un ordine diverso delle tappe.
- Punti: 100 per enigma, -20 per suggerimento, -10 per errore. Penalità tempo: suggerimento +120 s, errore +60 s.
- Test: aggiungere `?test` all'URL (simula presenza, reset, tocco sulla mappa per leggere le coordinate).
- Stato in localStorage `diario_cardinale_v2`.

## Da fare
1. Pubblicare (GitHub Pages o Netlify). GPS richiede https.
2. Generare gli mp3 con `genera_voci.py`.
3. Sopralluogo: verificare coordinate (Piazza Marconi, Scuderie, finale), orari Scuderie, lapide in cattedrale, falsa cupola del Gesù, fraschetta del finale.
4. Aggiornare documento e slide con i nuovi enigmi.
5. Idee: più giochi interattivi in stile Professor Layton, battute tra personaggi.

## Convenzioni
- Nessuna dipendenza esterna a runtime. Font e Leaflet restano in `vendor/`.
- Mappa: tessere OSM con filtro CSS verde (CARTO richiede chiave, non usarlo).
- Prima di consegnare: provare con Playwright a 390x780, nessun errore in console.
