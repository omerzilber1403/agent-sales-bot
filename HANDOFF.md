# AGENT — Cursor Handoff Brief

## 0) TL;DR
A small FastAPI backend that simulates a sales/chat agent in Hebrew. It exposes REST endpoints, a minimal in‑browser dev chat UI (`/dev`), simple guardrails for pricing questions → handoff, an in‑memory conversation log (for a lightweight coach view), and an optional fallback to a local LLM (Ollama / LM Studio) via an OpenAI‑compatible client. All responses are UTF‑8 safe for Windows PowerShell.

## 1) Repo layout (what exists now)
```
backend/
  main.py                       # FastAPI app (UTF-8 JSON), mounts routers
  config.py                     # pydantic-settings BaseSettings (ENV)
  config_loader.py              # loads agent.config.yaml (optional knobs)
  schemas.py                    # MessageIn/MessageOut pydantic models
  utils/
    logger.py                   # loguru, file logs in logs/app.log
  services/
    memory.py                   # in-memory Store: conversations + stats
    whatsapp_parser.py          # extract text/from_user from webhook payload
    llm_client.py               # OpenAI-compatible client (Ollama/LMStudio/OpenAI)
  routes/
    agent.py                    # POST /api/v1/agent/reply (rules + logging)
    webhook.py                  # POST /webhook/whatsapp (parses → reply)
    coach.py                    # GET coach endpoints (list/stats/convo)
    devui.py                    # GET /dev – simple web chat for developers
  graph/
    sales_graph.py              # LangGraph: detect_handoff → craft_reply → LLM fallback

agent.config.yaml               # feature toggles + guardrail keywords (optional)
.env            # provider/model/env setup
requirements.txt                # minimal deps
.gitignore                      # ignores .venv, __pycache__, logs, .env
logs/                           # log files
```

## 2) Runtime & encoding (Windows-friendly)
- Python 3.13 + venv. `uvicorn` with `--reload`.
- Responses default to `application/json; charset=utf-8` via a `JSONUTF8Response` in `backend/main.py` to stop Hebrew mojibake.
- PowerShell: when calling HTTP from terminal, we set UTF‑8 explicitly:
  ```powershell
  chcp 65001 > $null; [Console]::InputEncoding=[Text.Encoding]::UTF8; [Console]::OutputEncoding=[Text.Encoding]::UTF8; $OutputEncoding=[Text.Encoding]::UTF8
  ```

## 3) Key endpoints (current)
### Health
- `GET /health` → `{ "status": "ok" }`

### Agent (primary entry point)
- `POST /api/v1/agent/reply`
  - **Request** (`MessageIn`):
    ```json
    {"channel":"web","from_user":"972501234567","text":"שלום"}
    ```
  - **Response** (`MessageOut`):
    ```json
    {
      "channel":"web",
      "to_user":"972501234567",
      "text":"…",
      "handoff":false,
      "handoff_reason":null,
      "tone":"guide"
    }
    ```
  - Logic: rules → (optionally) LLM fallback. Always logs to memory store.

### WhatsApp webhook (simulator)
- `POST /webhook/whatsapp` (expects WA‑like body, uses `services.whatsapp_parser`)
- Returns `MessageOut` identical to `/agent/reply`.

### Coach (very lightweight)
- `GET /api/v1/coach/conversations` → `[ { user_id, count } ]`
- `GET /api/v1/coach/conversations/{user_id}` → `{ user_id, messages: [{ts,role,text,handoff,meta}] }`
- `GET /api/v1/coach/stats` → `{ total_messages, handoffs }`

### Dev UI
- `GET /dev` → single HTML page (no bundler) that:
  - renders history for a `user_id` via coach API
  - posts messages to `/api/v1/agent/reply`
  - chips for presets (שלום / מה המחיר / לקבוע שיחה)
  - shows `HANDOFF` badge when `handoff=true`
  - blocked in prod (`ENV=prod`) for safety

## 4) Guardrails & reply strategy
- **No invention** on sensitive fields: *price*, *discount*, *availability* (from `agent.config.yaml`).
- Hebrew keywords trigger handoff (examples: "מחיר", "עלות", "תמחור", etc.).
- If handoff is needed → canned reply asking for full name & phone and `handoff=true` with `handoff_reason` (e.g., `guardrails_price`).
- If greeting/info/meeting keywords → deterministic short replies (free, no LLM call).
- Otherwise → **optional** LLM fallback:
  - `services/llm_client.chat()` uses OpenAI SDK pointed at **Ollama / LM Studio** (`/v1` OpenAI‑compat) or real OpenAI.
  - System prompt (Hebrew): polite, short, no prices. Max tokens ~256, temp 0.3.
  - If LLM disabled/unavailable → polite default fallback.

## 5) Local LLM setup (Ollama)
- Install Ollama (Windows). In a separate terminal:
  ```powershell
  ollama serve
  ollama pull llama3.2:3b-instruct   # light + good enough for Hebrew basics
  # or: ollama pull qwen2.5:7b-instruct  # better multi‑lingual, heavier
  ```
- Quick ping:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method GET
  ```
- Direct test (OpenAI‑compat):
  ```powershell
  $body = @{ model="llama3.2:3b-instruct"; messages=@(
    @{role="system";content="ענה בעברית, קצר ומנומס."},
    @{role="user";content="שלום! איך אתה מרגיש היום?"}
  ) } | ConvertTo-Json -Compress
  Invoke-RestMethod -Uri "http://127.0.0.1:11434/v1/chat/completions" -Method POST `
    -Body ([Text.Encoding]::UTF8.GetBytes($body)) `
    -ContentType "application/json; charset=utf-8"
  ```

## 6) Environment variables (.env)
Example `.env` for free local runs:
```
ENV=dev
LLM_PROVIDER=ollama
LLM_BASE_URL=http://127.0.0.1:11434/v1
LLM_MODEL=llama3.2:3b-instruct
LLM_API_KEY=nokey
```
Switching to LM Studio:
```
LLM_PROVIDER=lmstudio
LLM_BASE_URL=http://127.0.0.1:1234/v1
```
Switching to OpenAI (paid):
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4.1-mini   # or any model
```

## 7) How replies are produced (LangGraph path)
LangGraph (`graph/sales_graph.py`) defines:
- **State**: `{ text, tone, needs_handoff, handoff_reason, reply, cfg }`
- **Nodes**:
  1) `detect_handoff(state)`: uses `backend.guardrails.need_handoff` + config
  2) `craft_reply(state)`: rules → (optional) `llm_client.chat()` → fallback string
- **Edges**: `START → detect_handoff → craft_reply → END`

If the project route uses the simple `routes/agent.py` (rule‑only), it still **logs** all turns to `services.memory.Store`.

## 8) In‑memory store (temporary persistence)
`services/memory.py` (class `Store` as `store` singleton):
- `conversations: Dict[user_id, List[{ts, role, text, handoff, meta}]]`
- `stats: { total_messages, handoffs }`
- Methods: `log(user_id, role, text, handoff=False, meta=None)` → appends & bumps counters.
- Volatile: cleared on process restart (good for dev).

## 9) Dev UI internals (`routes/devui.py`)
- Static HTML/JS (no framework) served at `/dev`.
- Calls `GET /api/v1/coach/conversations/{user_id}` on load.
- Sends user text to `POST /api/v1/agent/reply` and renders the assistant’s reply.
- Shows `HANDOFF` badge if `handoff=true` (+ title with `handoff_reason`).
- Has preset chips for quick testing.

## 10) Typical local workflow
1) **Start local LLM** (optional): `ollama serve` + `ollama pull MODEL`
2) **Set .env** to Ollama/LM Studio/OpenAI
3) **Run API**: `python -m uvicorn backend.main:app --reload --port 8080`
4) **Open UI**: http://127.0.0.1:8080/dev
5) **PowerShell test helper**:
   ```powershell
   function Send-Agent([string]$text, [string]$user="972501234567"){
     $b = @{ channel="web"; from_user=$user; text=$text } | ConvertTo-Json -Compress
     Invoke-RestMethod -Uri "http://127.0.0.1:8080/api/v1/agent/reply" -Method POST `
       -Body ([Text.Encoding]::UTF8.GetBytes($b)) `
       -ContentType "application/json; charset=utf-8"
   }
   ```
6) **Coach view quick checks**:
   - `GET /api/v1/coach/stats` → totals
   - `GET /api/v1/coach/conversations` → list
   - `GET /api/v1/coach/conversations/{user}` → full transcript

## 11) Troubleshooting notes
- **Hebrew turns to gibberish**: ensure `JSONUTF8Response` is used (it is), and PowerShell body is sent as UTF‑8 bytes with the `charset=utf-8` header.
- **`127.0.0.1 refused connection`**: uvicorn not running (or port mismatch).
- **`ModuleNotFoundError: backend.routes.coach`**: file not created/renamed; re‑add `routes/coach.py` or adjust import.
- **Ollama `Unable to connect`**: the `ollama serve` window must stay open; firewall may prompt on first run; default API at `127.0.0.1:11434`.
- **Stats remain zero**: make sure you call `/api/v1/agent/reply` (which logs) rather than only hitting `/webhook/whatsapp` without valid payload.

## 12) What remains / suggested next steps (backlog)
- **Structured memory**: swap `services/memory.py` with SQLite (or Postgres) and keep the same interface; add retention control from `agent.config.yaml`.
- **Coach dashboard**: small HTML page to list conversations + drill‑down (similar to `/dev`, but read‑only + filters & export).
- **RBAC & auth**: basic auth or token for `/coach/*` and `/dev` (hide in prod).
- **Handoff sink**: accumulate handoffs (name + phone) and push to a queue/CRM (toggle via config).
- **LLM prompt library**: move system prompts to YAML, allow per‑tone profiles.
- **Unit tests**: for guardrails, webhook parser, and LLM fallback handler.
- **Rate limiting** & basic abuse protection.

## 13) Design choices worth knowing
- Keep the **rule‑based** replies for common flows to run free, fast, and deterministic. Only fall back to LLM when rules miss.
- Everything is **OpenAI‑compatible** → swapping Ollama/LM Studio/OpenAI is only `.env` changes.
- Hebrew is a first‑class citizen: encoding fixed end‑to‑end, system prompts in Hebrew, UI right‑to‑left.

## 14) Hand‑off expectations for Cursor
- Cursor can ingest this brief + the codebase and:
  1) Implement DB‑backed Store keeping the same `Store` interface.
  2) Expand `sales_graph.py` with more nodes (e.g., intent detect → slot fill → action).
  3) Add `/coach` HTML UI (filters by `handoff=true`, export CSV).
  4) Add `auth` middleware and hide `/dev` when `ENV=prod`.
  5) Improve prompts + add per‑tone (direct/guide) variations.

---
**Contact string for quick sanity test**
- Open http://127.0.0.1:8080/dev, set `user_id = 972501234567`, send:
  - "מה המחיר?" → expect `handoff=true` with price handoff message
  - "שלום, אשמח לפרטים" → canned greeting
  - "לא אני צריך שתדבר איתי על משהו" → if rules miss, LLM fallback (if enabled)

