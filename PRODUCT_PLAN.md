# Email AI Classifier — Piano POC

## Vision

POC per la gestione intelligente delle email aziendali: lettura automatica, classificazione AI, workflow di approvazione e risposta.

---

## Architettura POC

```
    [Frontend SPA]              [Backend API]
    React + Vite          ←→    FastAPI + SQLite
    Tailwind CSS                Background tasks
                                OpenAI-compatible API
                                IMAP/SMTP
```

Nessuna infrastruttura esterna richiesta. SQLite come DB, background tasks nativi FastAPI, zero Redis/Celery/Kubernetes.

---

## FASE 1 — Solidificare (1 settimana)

### 1.1 Persistenza con SQLite
- [ ] SQLAlchemy 2.0 async con aiosqlite
- [ ] Modelli DB: `User`, `Mailbox`, `Email`, `Classification`, `ReplyLog`
- [ ] Migrazioni Alembic
- [ ] Deduplicazione email per Message-ID
- [ ] Paginazione server-side sugli endpoint lista

### 1.2 Autenticazione JWT
- [ ] Login con username/password (utente configurato da .env)
- [ ] JWT access token + refresh token
- [ ] Middleware di protezione su tutti gli endpoint
- [ ] Pagina di login nel frontend
- [ ] CORS ristretto

### 1.3 Docker
- [ ] Dockerfile backend (Python)
- [ ] Dockerfile frontend (Node build + nginx)
- [ ] docker-compose.yml (backend + frontend)

---

## FASE 2 — Funzionalità Core (1 settimana)

### 2.1 Polling e Background Tasks
- [ ] Scheduler interno (asyncio) per polling IMAP a intervallo configurabile
- [ ] Classificazione in background task (FastAPI BackgroundTasks)
- [ ] Auto-classificazione delle nuove email al fetch

### 2.2 Workflow di Approvazione
- [ ] Stati email estesi: new → classified → pending_approval → approved → replied
- [ ] Coda di risposte da approvare nella dashboard
- [ ] Modifica risposta prima dell'invio
- [ ] Auto-approvazione opzionale se confidenza > soglia configurabile

### 2.3 Template Risposte
- [ ] CRUD template per categoria (titolo + corpo con variabili)
- [ ] Variabili: {{mittente}}, {{oggetto}}, {{categoria}}
- [ ] Pagina gestione template nella UI
- [ ] Suggerimento template in base alla classificazione

---

## FASE 3 — Demo-Ready (1 settimana)

### 3.1 Dashboard Avanzata
- [ ] Statistiche reali da DB (non in-memory)
- [ ] Grafici: volume nel tempo, distribuzione categorie, tempo medio risposta
- [ ] Coda approvazioni con counter nel menu laterale
- [ ] Filtri: per casella, periodo, categoria

### 3.2 Feedback Classificazione
- [ ] Bottone "Correggi categoria" nel dettaglio email
- [ ] Salvataggio correzione in DB (categoria_ai vs categoria_umana)
- [ ] Statistiche accuracy: % classificazioni corrette
- [ ] Few-shot: inietta le ultime N correzioni nel prompt

### 3.3 Multi-Casella
- [ ] Supporto N caselle IMAP nella stessa istanza
- [ ] CRUD caselle dalla UI (Impostazioni)
- [ ] Filtro per casella nella lista email e dashboard
- [ ] Polling indipendente per ogni casella

### 3.4 Export
- [ ] Export CSV della lista email (con filtri applicati)
- [ ] Export statistiche

---

## KPI di Successo del POC

| KPI | Target |
|-----|--------|
| Accuracy classificazione | > 85% |
| Email processate senza intervento umano | > 50% |
| Tempo setup POC (docker-compose up) | < 5 minuti |
| Costo LLM per email | < €0.02 |

---

## Cosa NON è nel POC

- Kubernetes, Helm, CI/CD avanzato
- Redis, Celery, message queue
- Multi-tenancy (organizzazioni separate)
- SSO/SAML, MFA
- Elasticsearch, full-text search avanzato
- Integrazioni CRM/ticketing
- Internazionalizzazione
