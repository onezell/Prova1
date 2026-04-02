# Email AI Classifier — Piano Prodotto Enterprise

## 1. Vision

Piattaforma enterprise per la gestione intelligente delle email aziendali: lettura automatica delle caselle, classificazione AI, risposte automatiche con approvazione, workflow configurabili e analytics avanzati.

---

## 2. Stato Attuale del POC

### Cosa c'è

| Area | Funzionalità |
|------|-------------|
| **Email Client** | Lettura IMAP (singola casella), invio SMTP |
| **Classificazione AI** | Singolo prompt LLM, 7 categorie, generazione risposta |
| **API REST** | 11 endpoint FastAPI (fetch, list, classify, reply, settings, stats) |
| **Dashboard React** | Lista email, dettaglio, statistiche con grafici, impostazioni |
| **Storage** | In-memory (dict Python) — si perde al restart |

### Gap critici rispetto all'enterprise

| Area | Gap |
|------|-----|
| **Sicurezza** | Zero autenticazione/autorizzazione, CORS aperto, nessun audit |
| **Persistenza** | Nessun database, nessuna deduplicazione |
| **Scalabilità** | Classificazione sincrona/bloccante, nessun task queue |
| **Multi-tenancy** | Singola casella, nessun concetto di organizzazione |
| **Testing** | Zero test di qualsiasi tipo |
| **Infrastruttura** | Nessun Docker, CI/CD, monitoring |

---

## 3. Architettura Target

```
                    [Load Balancer / Reverse Proxy]
                              Nginx / Traefik
                                    |
                 ┌──────────────────┴──────────────────┐
                 |                                      |
          [Frontend SPA]                         [API Gateway]
          React + TypeScript                     Rate limiting
          TanStack Query                         JWT validation
          Zustand state mgmt                     Request logging
                                                       |
                        ┌──────────┬───────────────────┴──────────┐
                        |          |                               |
                  [Auth Service]   [Email Service]          [AI Service]
                  JWT + RBAC       IMAP/SMTP/Graph API      LLM orchestration
                  SSO/SAML         Attachments               Prompt management
                                   Threading                 Feedback loop
                        |          |                               |
                        └──────────┴────────────┬─────────────────┘
                                                |
                                         [Message Queue]
                                         Redis + Celery
                                                |
                                  ┌─────────────┴─────────────┐
                                  |                           |
                           [PostgreSQL]                [Object Storage]
                           Dati, utenti, audit         Allegati (S3/MinIO)
                                  |
                           [Redis Cache]
                           Session, rate limit, pub/sub
```

### Stack tecnologico target

| Componente | Tecnologia |
|-----------|------------|
| Database | PostgreSQL + SQLAlchemy 2.0 + Alembic |
| Cache/Broker | Redis |
| Task Queue | Celery + Redis |
| Auth | Keycloak / Auth0 (JWT + RBAC + SSO) |
| Object Storage | S3 / MinIO (allegati) |
| Frontend | React + TypeScript + TanStack Query + Zustand |
| Monitoring | Prometheus + Grafana + Sentry |
| Container | Docker + docker-compose (dev), Kubernetes (prod) |
| CI/CD | GitHub Actions |

---

## 4. Piano Funzionalità Completo

### FASE 1 — Fondamenta (Sprint 1-3)

#### 1.1 Database e Persistenza
- [ ] PostgreSQL con SQLAlchemy 2.0 async
- [ ] Modelli: `Tenant`, `User`, `Mailbox`, `Email`, `Classification`, `Reply`, `AuditLog`
- [ ] Migrazioni Alembic
- [ ] Deduplicazione email per Message-ID
- [ ] Paginazione su tutti gli endpoint lista (cursor-based)
- [ ] Soft delete su tutte le entità

#### 1.2 Autenticazione e Autorizzazione
- [ ] Login con email/password + JWT (access + refresh token)
- [ ] Ruoli: `admin`, `manager`, `operator`, `viewer`
- [ ] Permessi granulari per azione (classificare, rispondere, modificare settings, ecc.)
- [ ] Protezione CORS con whitelist domini
- [ ] Rate limiting per utente e per endpoint
- [ ] Password hashing con bcrypt/argon2
- [ ] Sessioni invalidabili

#### 1.3 Multi-Tenancy e Multi-Casella
- [ ] Concetto di `Tenant` (organizzazione/azienda)
- [ ] Più caselle email per tenant (es. info@, support@, sales@)
- [ ] Isolamento dati completo tra tenant
- [ ] Configurazione IMAP/SMTP per casella
- [ ] Dashboard per casella e aggregata

#### 1.4 Infrastruttura Base
- [ ] Dockerfile backend + frontend
- [ ] docker-compose con PostgreSQL + Redis + backend + frontend
- [ ] GitHub Actions: lint, test, build, deploy
- [ ] Variabili ambiente con vault/secrets manager
- [ ] Health check avanzato (DB, Redis, IMAP connectivity)

---

### FASE 2 — Core Intelligence (Sprint 4-6)

#### 2.1 Classificazione Avanzata
- [ ] Pipeline di classificazione multi-step: lingua → categoria → urgenza → sentiment
- [ ] Confidence threshold configurabile per auto-azione
- [ ] Supporto multi-lingua (detect + classify nella lingua originale)
- [ ] Fallback chain tra provider LLM (primario → secondario → regole)
- [ ] Caching delle classificazioni per email simili
- [ ] Batch classification asincrono via Celery
- [ ] Prompt versioning e A/B testing
- [ ] Categorie personalizzabili per tenant/casella

#### 2.2 Feedback Loop e Apprendimento
- [ ] Correzione manuale della classificazione da UI
- [ ] Tracking accuracy: classificazione AI vs correzione umana
- [ ] Dashboard metriche di accuracy per categoria
- [ ] Export dati per fine-tuning del modello
- [ ] Few-shot learning: iniettare esempi corretti nel prompt
- [ ] Suggerimento automatico di nuove categorie basato su clustering

#### 2.3 Generazione Risposte Intelligenti
- [ ] Template di risposta per categoria (personalizzabili per tenant)
- [ ] Variabili dinamiche nei template (nome mittente, numero ticket, ecc.)
- [ ] Tono configurabile: formale, informale, tecnico
- [ ] Risposta in lingua del mittente (auto-detect)
- [ ] Suggerimento risposta basato su risposte precedenti simili
- [ ] Firma email configurabile per utente/casella

#### 2.4 Processing Asincrono
- [ ] Celery workers per classificazione batch
- [ ] Polling IMAP schedulato (intervallo configurabile per casella)
- [ ] Job di retry automatico per classificazioni fallite
- [ ] Progress tracking con WebSocket/SSE
- [ ] Dashboard coda di lavoro (job in attesa, completati, falliti)

---

### FASE 3 — Workflow e Automazione (Sprint 7-9)

#### 3.1 Rule Engine
- [ ] Editor regole visuale (if/then/else)
- [ ] Condizioni: categoria, confidenza, mittente, oggetto (regex), parole chiave, orario
- [ ] Azioni: auto-reply, assegna a operatore, escalation, tag, sposta in folder, notifica
- [ ] Priorità tra regole (ordine di esecuzione)
- [ ] Regole per casella e globali per tenant
- [ ] Dry-run mode: simula regole senza eseguirle
- [ ] Log di ogni regola eseguita nell'audit trail

#### 3.2 Workflow di Approvazione
- [ ] Coda di risposte in attesa di approvazione
- [ ] Ruolo "approver" con permesso di revisione
- [ ] Modifica della risposta prima dell'approvazione
- [ ] Auto-approvazione per risposte con confidenza > soglia
- [ ] Notifica all'approver (email, in-app, webhook)
- [ ] SLA configurabili: tempo massimo per risposta per categoria
- [ ] Escalation automatica se SLA superato

#### 3.3 Threading e Conversazioni
- [ ] Raggruppamento email per thread (In-Reply-To / References header)
- [ ] Vista conversazione nella UI
- [ ] Contesto conversazione passato all'LLM per risposte più pertinenti
- [ ] Stato conversazione: aperta, in attesa, risolta
- [ ] Assegnazione conversazione a operatore specifico

#### 3.4 Gestione Allegati
- [ ] Estrazione e salvataggio allegati su Object Storage (S3/MinIO)
- [ ] Preview allegati nella UI (immagini, PDF)
- [ ] Analisi allegati con AI (OCR, summarization)
- [ ] Allegati nella risposta
- [ ] Limite dimensione e tipo allegato configurabile
- [ ] Scansione antivirus/malware

---

### FASE 4 — Analytics e Reporting (Sprint 10-11)

#### 4.1 Dashboard Analytics
- [ ] Volume email nel tempo (giorno/settimana/mese)
- [ ] Distribuzione per categoria con trend
- [ ] Tempo medio di risposta per categoria
- [ ] Tasso di auto-risposta vs risposta manuale
- [ ] Accuracy classificazione nel tempo
- [ ] Heatmap: ore/giorni con più email
- [ ] Top mittenti e domini
- [ ] Filtri per casella, periodo, categoria, operatore

#### 4.2 Reporting
- [ ] Report schedulati via email (giornaliero, settimanale)
- [ ] Export CSV/Excel della lista email
- [ ] Report SLA compliance
- [ ] Report attività per operatore
- [ ] Report costi LLM (token consumati, costo stimato per classificazione)

#### 4.3 Observability
- [ ] Logging strutturato (JSON) con correlation ID
- [ ] Metriche Prometheus: latenza API, throughput, error rate, coda Celery
- [ ] Dashboard Grafana pre-configurata
- [ ] Alerting: email non processate > soglia, errori LLM, SLA breach
- [ ] Sentry per error tracking (backend + frontend)
- [ ] Distributed tracing con OpenTelemetry

---

### FASE 5 — Enterprise Features (Sprint 12-14)

#### 5.1 Integrazioni
- [ ] Microsoft Graph API (Outlook/365) oltre a IMAP
- [ ] Gmail API nativa (oltre a IMAP)
- [ ] Webhook in uscita (notifica sistemi esterni a ogni classificazione/risposta)
- [ ] Webhook in ingresso (trigger da sistemi esterni)
- [ ] Integrazione CRM: Salesforce, HubSpot (link email a contatto/deal)
- [ ] Integrazione ticketing: Jira, Zendesk (crea ticket da email)
- [ ] Integrazione Slack/Teams (notifiche, comandi)
- [ ] API pubblica documentata (OpenAPI) per integrazioni custom

#### 5.2 Sicurezza Avanzata
- [ ] SSO via SAML 2.0 / OpenID Connect
- [ ] MFA (TOTP, WebAuthn)
- [ ] IP whitelisting
- [ ] Audit log completo e immutabile (chi, cosa, quando, da dove)
- [ ] Audit log query/export per compliance
- [ ] Encryption at rest per dati sensibili (credenziali, corpo email)
- [ ] Data retention policy configurabile
- [ ] GDPR: export/delete dati utente su richiesta
- [ ] Penetration test e security audit

#### 5.3 Admin e Operations
- [ ] Pannello admin super-tenant per gestione globale
- [ ] Onboarding guidato nuovo tenant
- [ ] Billing/usage tracking per tenant
- [ ] Feature flags per rollout graduale
- [ ] Maintenance mode (disabilita processamento senza downtime)
- [ ] Backup automatico database con restore testato
- [ ] Horizontal scaling: multiple API instances, multiple workers

#### 5.4 UX Avanzata
- [ ] Migrazione frontend a TypeScript
- [ ] Dark mode
- [ ] Responsive/mobile
- [ ] Accessibilità WCAG 2.1 AA
- [ ] Keyboard shortcuts
- [ ] Ricerca full-text email (Elasticsearch / pg_trgm)
- [ ] Bulk actions (classifica/rispondi a selezione multipla)
- [ ] Drag & drop per riassegnazione
- [ ] Notifiche in-app real-time (WebSocket)
- [ ] Internazionalizzazione (i18n) — IT, EN, FR, DE, ES

---

## 5. Priorità e Roadmap

```
Mese 1-2    ██████████ FASE 1 — Fondamenta
             DB, Auth, Multi-tenancy, Docker, CI/CD

Mese 3-4    ██████████ FASE 2 — Core Intelligence
             Classificazione avanzata, Feedback loop, Async processing

Mese 5-6    ██████████ FASE 3 — Workflow e Automazione
             Rule engine, Approvazione, Threading, Allegati

Mese 7-8    ██████████ FASE 4 — Analytics e Reporting
             Dashboard analytics, Export, Observability

Mese 9-10   ██████████ FASE 5 — Enterprise Features
             Integrazioni, Sicurezza avanzata, Admin, UX
```

---

## 6. KPI di Successo

| KPI | Target |
|-----|--------|
| Accuracy classificazione | > 90% |
| Tempo medio risposta | < 5 min (auto), < 30 min (con approvazione) |
| Tasso auto-risposta | > 60% delle email |
| Uptime | 99.9% |
| Tempo onboarding nuovo tenant | < 1 giorno |
| Costo LLM per email | < €0.02 |
| NPS operatori | > 40 |

---

## 7. Rischi e Mitigazioni

| Rischio | Impatto | Mitigazione |
|---------|---------|-------------|
| Risposte AI inappropriate inviate a clienti | Critico | Workflow approvazione obbligatorio in fase iniziale, confidence threshold alto |
| Costi LLM fuori controllo | Alto | Budget cap per tenant, caching risposte simili, modelli economici per triage |
| Prompt injection via email malevole | Alto | Sanitizzazione input, sandboxing prompt, monitoring anomalie |
| Latenza classificazione con volumi alti | Medio | Workers Celery scalabili, batch processing, priorità per SLA |
| Lock-in su provider LLM | Medio | Architettura OpenAI-compatible, facile switch tra provider |
| GDPR compliance per dati email | Alto | Encryption at rest, retention policy, data export/delete, DPA con provider LLM |
