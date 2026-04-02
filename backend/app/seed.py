"""Mock data: email fake per una cantina di vini (B2B, B2C, visite guidate)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

MOCK_EMAILS = [
    # ── B2B ────────────────────────────────────────────
    {
        "subject": "Richiesta listino prezzi B2B - Enoteca Rossi",
        "sender": "Marco Rossi <marco.rossi@enotecarossi.it>",
        "body": """Buongiorno,

sono Marco Rossi, titolare dell'Enoteca Rossi di Milano. Siamo una catena di 12 punti vendita specializzati in vini italiani di qualità.

Vorremmo ricevere il vostro listino prezzi aggiornato per ordini B2B, con particolare interesse per:
- Brunello di Montalcino Riserva
- Chianti Classico Gran Selezione
- Rosso di Montalcino

Lavoriamo con ordini minimi di 200 bottiglie per referenza. Sarebbe possibile organizzare una degustazione per il nostro team acquisti?

Cordiali saluti,
Marco Rossi
Enoteca Rossi Srl""",
        "category": "preventivo",
        "confidence": 0.95,
        "summary": "Richiesta listino B2B da catena di enoteche (12 punti vendita) per Brunello, Chianti Classico e Rosso di Montalcino.",
        "suggested_reply": """Gentile Sig. Rossi,

La ringraziamo per l'interesse nei nostri vini. Siamo lieti di inviarle il nostro listino B2B aggiornato, che troverà in allegato.

Per ordini superiori a 200 bottiglie per referenza, possiamo applicare condizioni particolarmente vantaggiose. Saremo felici di organizzare una degustazione dedicata al vostro team acquisti presso la nostra cantina.

Le proponiamo le seguenti date per la degustazione:
- Martedì o giovedì della prossima settimana
- Durata: circa 2 ore con visita ai vigneti

Resto a disposizione per ogni chiarimento.

Cordiali saluti""",
    },
    {
        "subject": "Ordine rifornimento Q2 - Ristorante Bellavista",
        "sender": "Giulia Ferretti <g.ferretti@bellavista-ristorante.com>",
        "body": """Buongiorno,

come concordato telefonicamente con il vostro agente Luca, vorremmo procedere con l'ordine per il secondo trimestre:

- 48 bt. Vernaccia di San Gimignano DOCG 2023
- 36 bt. Chianti Classico DOCG 2021
- 24 bt. Brunello di Montalcino DOCG 2019
- 12 bt. Vin Santo del Chianti DOC 2018

Consegna desiderata: entro il 15 del mese prossimo.
Fatturazione: come da accordo quadro, pagamento 60gg data fattura.

Confermate disponibilità e tempi?

Grazie,
Giulia Ferretti
Ristorante Bellavista - Firenze""",
        "category": "preventivo",
        "confidence": 0.92,
        "summary": "Ordine trimestrale da ristorante fiorentino: 120 bottiglie totali tra Vernaccia, Chianti, Brunello e Vin Santo.",
        "suggested_reply": """Gentile Sig.ra Ferretti,

Confermiamo la ricezione del vostro ordine per il Q2. Abbiamo verificato la disponibilità:

- Vernaccia di San Gimignano DOCG 2023: disponibile
- Chianti Classico DOCG 2021: disponibile
- Brunello di Montalcino DOCG 2019: disponibile
- Vin Santo del Chianti DOC 2018: disponibile (ultime 15 bottiglie dell'annata)

Consegna confermata entro il 15 del mese. Fatturazione secondo accordo quadro.

Procediamo con la conferma d'ordine?

Cordiali saluti""",
    },
    {
        "subject": "Proposta distribuzione esclusiva Norvegia",
        "sender": "Erik Nordahl <erik@nordicwines.no>",
        "body": """Dear Cantina team,

I am Erik Nordahl, purchasing manager at Nordic Wines AS, the leading Italian wine importer in Scandinavia. We distribute to over 500 restaurants and Vinmonopolet (Norwegian wine monopoly) stores.

We recently tasted your Brunello di Montalcino 2019 at Vinitaly and were very impressed. We would like to discuss an exclusive distribution agreement for Norway.

Could we arrange a meeting, either at your winery or via video call, to discuss:
1. Exclusive distribution terms for Norway
2. Annual volume commitments
3. Marketing support and co-branding opportunities
4. Pricing and logistics

We typically work with 3-year contracts and guarantee minimum volumes.

Best regards,
Erik Nordahl
Nordic Wines AS - Oslo""",
        "category": "collaborazione",
        "confidence": 0.91,
        "summary": "Proposta di distribuzione esclusiva per la Norvegia da importatore scandinavo, dopo degustazione a Vinitaly.",
        "suggested_reply": """Dear Mr. Nordahl,

Thank you for your interest in our wines and the kind words about our Brunello di Montalcino 2019.

We are very interested in exploring a distribution partnership for the Norwegian market. Nordic Wines' established network with Vinmonopolet and the restaurant channel makes this a compelling opportunity.

We would be delighted to welcome you at our winery for a comprehensive tasting and business meeting. Alternatively, we can start with a video call to discuss the key terms.

Could you suggest a few dates that work for you in the coming weeks?

Kind regards""",
    },
    # ── B2C ────────────────────────────────────────────
    {
        "subject": "Spedizione danneggiata - ordine #4521",
        "sender": "Laura Bianchi <laura.bianchi@gmail.com>",
        "body": """Buongiorno,

ho ricevuto oggi il mio ordine #4521 (6 bottiglie di Chianti Classico Riserva 2020) ma purtroppo 2 bottiglie sono arrivate rotte. Il cartone era visibilmente danneggiato dal corriere.

Ho scattato delle foto che posso inviarvi. Vorrei sapere come procedere per la sostituzione delle 2 bottiglie danneggiate.

È la prima volta che mi capita con voi, sono cliente da 3 anni e sempre soddisfatta.

Laura Bianchi
Tel: 333-1234567""",
        "category": "reclamo",
        "confidence": 0.97,
        "summary": "Cliente B2C lamenta 2 bottiglie rotte su 6 nella spedizione. Cliente fidelizzata da 3 anni.",
        "suggested_reply": """Gentile Sig.ra Bianchi,

Ci scusiamo sinceramente per l'inconveniente. Siamo dispiaciuti che la spedizione sia arrivata danneggiata — non è lo standard che vogliamo offrire ai nostri clienti.

Provvederemo immediatamente alla rispedizione gratuita delle 2 bottiglie di Chianti Classico Riserva 2020 danneggiate. In aggiunta, vorremmo inviarle una bottiglia omaggio del nostro Rosso di Montalcino come gesto di scuse.

Le chiediamo gentilmente di inviarci le foto del danno rispondendo a questa email, per la pratica con il corriere.

La nuova spedizione partirà entro 24 ore dalla ricezione delle foto.

Cordiali saluti""",
    },
    {
        "subject": "Consiglio per regalo anniversario",
        "sender": "Paolo Verdi <paolo.verdi@outlook.it>",
        "body": """Salve,

tra due settimane è il mio anniversario di matrimonio (25 anni!) e vorrei regalare a mia moglie qualcosa di speciale dalla vostra cantina.

Lei ama i vini rossi strutturati ma non troppo tannici. Budget intorno ai 150-200 euro per una confezione regalo.

Avete qualche suggerimento? Magari una verticale o una selezione speciale? Se possibile vorrei anche una confezione regalo elegante.

Grazie mille!
Paolo""",
        "category": "richiesta_info",
        "confidence": 0.88,
        "summary": "Cliente chiede consiglio per regalo anniversario 25 anni. Budget 150-200€, preferenza rossi strutturati non tannici.",
        "suggested_reply": """Gentile Sig. Verdi,

Che bella occasione! Per un anniversario così importante, le suggeriamo la nostra "Selezione Anniversario" che include:

- 1 bt. Brunello di Montalcino DOCG 2018 (elegante e setoso, perfetto per chi ama i rossi strutturati)
- 1 bt. Chianti Classico Gran Selezione 2019 (il nostro fiore all'occhiello)
- 1 bt. Rosso di Montalcino DOC 2021 (fresco e immediato, ideale per apertura anticipata)

Il cofanetto in legno pregiato con incisione personalizzabile è incluso. Prezzo: €185.

La spedizione espressa in 48h garantisce la consegna in tempo. Possiamo anche aggiungere un biglietto personalizzato.

Procediamo con l'ordine?

Cordiali saluti""",
    },
    {
        "subject": "Iscrizione wine club - info",
        "sender": "Alessandra Conti <ale.conti@yahoo.it>",
        "body": """Ciao!

Ho visitato la vostra cantina il mese scorso durante una gita in Toscana e sono rimasta innamorata dei vostri vini! La guida ci ha parlato del vostro Wine Club ma non ho avuto tempo di informarmi meglio.

Potreste spiegarmi come funziona? In particolare:
- Costo annuale
- Quante spedizioni all'anno
- Che vini includete
- Ci sono vantaggi per le visite in cantina?

Grazie!
Alessandra""",
        "category": "richiesta_info",
        "confidence": 0.93,
        "summary": "Ex-visitatrice richiede info sul Wine Club: costi, frequenza spedizioni, selezione vini e vantaggi.",
        "suggested_reply": """Cara Alessandra,

Che piacere sapere che la visita ti è rimasta nel cuore! Il nostro Wine Club funziona così:

- Quota annuale: €299
- 4 spedizioni stagionali (marzo, giugno, settembre, dicembre)
- Ogni spedizione include 3 bottiglie selezionate dal nostro enologo, tra cui anteprime e edizioni limitate
- Sconto 15% su tutti gli acquisti in cantina e online
- 2 visite guidate gratuite all'anno con degustazione premium
- Invito esclusivo alla Festa della Vendemmia (settembre)

L'iscrizione si può fare direttamente dal nostro sito nella sezione "Wine Club" o rispondendo a questa email.

Ti aspettiamo!

Cordiali saluti""",
    },
    # ── VISITE GUIDATE ─────────────────────────────────
    {
        "subject": "Prenotazione visita guidata gruppo 20 persone",
        "sender": "Francesca Moretti <f.moretti@incentivetravel.it>",
        "body": """Buongiorno,

sono Francesca Moretti di Incentive Travel, organizziamo eventi aziendali ed esperienze per team building.

Un nostro cliente (azienda tech di Milano, 20 persone) vorrebbe organizzare una visita in cantina come attività di team building. Le date preferite sarebbero:
- Venerdì 18 o 25 del prossimo mese
- Arrivo previsto: ore 10:00
- Durata ideale: mezza giornata

Vorremmo includere:
1. Visita ai vigneti e alla cantina
2. Degustazione guidata (almeno 5 vini)
3. Pranzo tipico toscano in cantina
4. Possibilità di acquisto vini con sconto gruppo

Potete farci avere un preventivo dettagliato?

Grazie,
Francesca Moretti
Incentive Travel Srl""",
        "category": "preventivo",
        "confidence": 0.94,
        "summary": "Richiesta preventivo visita team building aziendale per 20 persone con degustazione e pranzo toscano.",
        "suggested_reply": """Gentile Sig.ra Moretti,

Grazie per averci contattato! Siamo specializzati in esperienze di team building in cantina e saremo lieti di ospitare il vostro gruppo.

Ecco la nostra proposta per 20 persone:

PACCHETTO "TEAM BUILDING IN VIGNA"
- 10:00 - Accoglienza con calice di benvenuto (Vernaccia di San Gimignano)
- 10:30 - Passeggiata guidata tra i vigneti
- 11:30 - Visita alla cantina e ai locali di affinamento
- 12:30 - Degustazione guidata di 6 vini con abbinamento formaggi locali
- 13:30 - Pranzo toscano nel nostro giardino (4 portate + vini in abbinamento)
- 15:30 - Momento shopping con sconto 20% per il gruppo

Prezzo: €95 a persona (IVA inclusa)

Entrambe le date proposte sono disponibili. Quale preferite?

Cordiali saluti""",
    },
    {
        "subject": "Visita e degustazione per 2 - sabato prossimo",
        "sender": "Thomas Müller <t.mueller@web.de>",
        "body": """Hello,

my wife and I are spending a week in Tuscany and we would love to visit your winery next Saturday afternoon.

We are wine enthusiasts and would be interested in:
- A tour of the vineyard and cellar
- A tasting of your premium wines (especially Brunello)
- The possibility to buy wines to ship to Germany

Is it possible to book for 2 people around 14:00-15:00?

Thank you!
Thomas & Ingrid Müller""",
        "category": "richiesta_info",
        "confidence": 0.90,
        "summary": "Coppia tedesca in vacanza in Toscana chiede visita e degustazione per sabato pomeriggio. Interessati anche a spedizione in Germania.",
        "suggested_reply": """Dear Thomas and Ingrid,

Welcome to Tuscany! We would be delighted to host you next Saturday.

We can book you for our "Premium Tasting Experience" at 14:30:
- Guided walk through the vineyards (30 min)
- Cellar tour with our winemaker (20 min)
- Premium tasting of 6 wines including our Brunello di Montalcino and Riserva (45 min)
- Price: €35 per person

Regarding shipping to Germany: yes, we regularly ship to Germany via temperature-controlled transport. Minimum order: 6 bottles, shipping cost: €15.

Shall we confirm the booking for 2 at 14:30?

Kind regards""",
    },
    {
        "subject": "Complimenti per la visita di ieri",
        "sender": "Roberto Sala <r.sala@libero.it>",
        "body": """Buonasera,

volevo solo ringraziarvi per la splendida esperienza di ieri in cantina. La guida (credo si chiamasse Elena) è stata fantastica, competente e simpaticissima.

Il Brunello Riserva 2017 che abbiamo degustato è eccezionale. Ne ho ordinato una cassa ma volevo chiedervi: è possibile riservarne un'altra cassa per Natale? So che è una produzione limitata.

Lascerò sicuramente una recensione a 5 stelle su TripAdvisor!

Grazie ancora,
Roberto""",
        "category": "richiesta_info",
        "confidence": 0.85,
        "summary": "Cliente soddisfatto della visita, chiede di riservare una cassa di Brunello Riserva 2017 per Natale.",
        "suggested_reply": """Gentile Sig. Sala,

Grazie mille per le sue parole! Riferiremo sicuramente i complimenti a Elena, ne sarà felicissima.

Per quanto riguarda il Brunello Riserva 2017: ha ottimo gusto! Confermiamo che è una produzione limitata (solo 3.000 bottiglie). Possiamo senz'altro riservare una cassa (6 bottiglie) per il periodo natalizio.

Le confermeremo la prenotazione via email e la contatteremo a inizio dicembre per concordare la spedizione.

Grazie anche per la recensione su TripAdvisor — ogni feedback ci aiuta a migliorare!

A presto in cantina,
Cordiali saluti""",
    },
    # ── SPAM / ALTRO ───────────────────────────────────
    {
        "subject": "OFFERTA IMPERDIBILE: Software gestionale cantina -70%",
        "sender": "promo@wineerp-solutions.biz",
        "body": """OFFERTA LIMITATA!!!

Il software gestionale WineERP è in SUPER SCONTO del 70%!
Solo per oggi: da €5.000 a soli €1.500!

Gestisci magazzino, ordini, fatture e tracciabilità dei lotti tutto in un unico software!

CLICCA QUI PER APPROFITTARE DELL'OFFERTA >>> [link rimosso]

Non perdere questa occasione!
Team WineERP Solutions""",
        "category": "spam",
        "confidence": 0.99,
        "summary": "Email promozionale spam per software gestionale con sconto aggressivo.",
        "suggested_reply": "",
    },
    {
        "subject": "Collaborazione food blogger - visita in cantina",
        "sender": "Valentina De Luca <vale.deluca.blog@gmail.com>",
        "body": """Ciao!

Mi chiamo Valentina e gestisco il food & wine blog "Calice e Forchetta" (85.000 follower su Instagram, 40.000 iscritti YouTube).

Sto pianificando una serie di contenuti sulle cantine toscane e mi piacerebbe dedicare un episodio alla vostra realtà. L'idea sarebbe:
- Un video-tour della cantina e dei vigneti (15-20 min per YouTube)
- Stories e reel per Instagram
- Un articolo dettagliato sul blog con link al vostro e-commerce

In cambio chiedo:
- Ospitalità per 2 persone (io + videomaker) per una giornata
- Degustazione completa
- Pranzo

Naturalmente vi forniremo tutto il materiale prodotto e i diritti di utilizzo.

Che ne pensate?

Valentina De Luca
@calice_e_forchetta""",
        "category": "collaborazione",
        "confidence": 0.93,
        "summary": "Food blogger (85K Instagram, 40K YouTube) propone collaborazione: video-tour cantina in cambio di ospitalità e degustazione.",
        "suggested_reply": """Cara Valentina,

Grazie per la proposta! Abbiamo visitato il tuo profilo e ci piace molto il tuo stile di racconto — genuino e professionale.

Siamo interessati alla collaborazione. Possiamo offrirti:
- Una giornata completa in cantina con accesso a tutti gli spazi (vigneti, barricaia, bottaia)
- Degustazione guidata dal nostro enologo con 8 vini, inclusi alcuni non ancora in commercio
- Pranzo nel nostro ristorante con menu degustazione abbinato
- Ospitalità per 2 persone

In cambio chiediamo:
- Tag e menzione in tutti i contenuti
- Condivisione materiale per i nostri canali social
- Un link al nostro e-commerce nell'articolo del blog

Quando pensi di venire in Toscana? Così blocchiamo una data.

A presto!""",
    },
    {
        "subject": "Problema con il sito - non riesco a completare l'ordine",
        "sender": "Anna Galli <anna.galli@hotmail.com>",
        "body": """Buongiorno,

da ieri sera sto cercando di fare un ordine sul vostro sito ma al momento del pagamento con carta di credito ricevo sempre l'errore "Transazione non riuscita - codice ERR_PAY_042".

Ho provato con due carte diverse e anche con PayPal ma niente. Il carrello contiene:
- 3x Chianti Classico 2021
- 2x Vernaccia 2023

Potete aiutarmi? Vorrei ricevere i vini entro venerdì per una cena.

Grazie,
Anna Galli""",
        "category": "supporto_tecnico",
        "confidence": 0.96,
        "summary": "Cliente non riesce a completare un ordine online per errore pagamento (ERR_PAY_042). Urgente: serve entro venerdì.",
        "suggested_reply": """Gentile Sig.ra Galli,

Ci scusiamo per il disagio. Abbiamo verificato e stiamo riscontrando un problema temporaneo con il gateway di pagamento che il nostro team tecnico sta risolvendo.

Nel frattempo, per non farle perdere tempo, possiamo:

1. Registrare il suo ordine manualmente (3x Chianti Classico 2021 + 2x Vernaccia 2023)
2. Inviarle un link di pagamento diretto via email
3. Garantire la spedizione espressa per consegna entro giovedì

Conferma che possiamo procedere così?

Ci scusiamo ancora per l'inconveniente.

Cordiali saluti""",
    },
]


def generate_mock_emails() -> list[dict]:
    """Generate mock email dicts ready for DB insertion."""
    now = datetime.now(timezone.utc)
    result = []

    for i, mock in enumerate(MOCK_EMAILS):
        email_date = now - timedelta(hours=i * 6, minutes=i * 13)
        result.append(
            {
                "id": str(uuid.uuid4()),
                "message_id": f"<mock-{i:04d}@cantina-test.it>",
                "uid": 1000 + i,
                "mailbox": "default",
                "subject": mock["subject"],
                "sender": mock["sender"],
                "date": email_date,
                "body": mock["body"],
                "body_html": "",
                "status": "classified" if mock.get("category") else "new",
                "category": mock.get("category"),
                "confidence": mock.get("confidence"),
                "summary": mock.get("summary"),
                "suggested_reply": mock.get("suggested_reply"),
            }
        )

    return result
