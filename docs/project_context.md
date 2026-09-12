# Digital Shield — Project Context

## Current architecture and direction

- One React + Vite browser frontend in `frontend/` (existing starter, product UI pending).
- One shared FastAPI backend.
- One planned lightweight verification agent with scam checker, URL checker, claim verifier, and vision tool.
- Planned autonomous claim verification, intelligent tool selection, and missing-information follow-up.
- English + Urdu, traffic-light results, and browser text-to-speech where supported.
- Free tools/resources only; no custom ML training, authentication, or database unless later required.

The browser application is the only frontend being developed. WhatsApp is a future integration vision shown through slide animation, not an implemented channel.

The former `digital-shield/` Vite starter was moved intact to `frontend/`.
Root-level `public/` contains preserved legacy chat-demo source and audio; it is
outside the active Vite app, is not part of the live prototype, and should not be
used as evidence that a messaging frontend is being built. See `public/README.md`.

## Backend foundation

The initial FastAPI backend is implemented in `backend/`. It provides one shared,
channel-independent API for the single React + Vite browser frontend.

- `GET /health` returns `{"status": "ok", "service": "digital-shield"}`.
- `POST /verify` validates JSON with required nonblank `content`, `language` (`en`
  or `ur`, default `en`), and optional nonblank `session_id`. Unknown fields are
  rejected. Invalid requests return standard FastAPI 422 validation errors.
- Responses contain `status` (`green`, `yellow`, or `red`), `label`, `summary`,
  string lists `reasons` and `actions`, `sources` (objects with `label` and HTTP(S)
  `url`), `needs_followup`, nullable `followup_question`, and `language`.
- `/verify` runs deterministic English scam analysis, extracts HTTP(S)/www URLs,
  and checks each URL locally through `backend/tools/url_checker.py`. Text and URL
  evidence are combined into one risk response without an agent.
  Sources remain empty, follow-up is false, and the follow-up question is null.
  The requested language is preserved; user-facing copy remains English.
- Swagger UI is available at `/docs`, with the API schema at `/openapi.json`.
  Opening `/` redirects to `/docs`.

The scam checker and URL checker are implemented. The verification agent, claim
verifier, vision tool, and follow-up handling are still pending. No LLM, external
API calls, image handling, session storage, database, or authentication is implemented.

## Deterministic scam checker

`check_scam(content)` returns typed evidence with unique `signals`, corresponding
`reasons`, a `score` counting distinct signals, and an Arabic-script coverage flag.
The score is not a probability. The tool does not generate the final API response
and can be reused by a future agent.

Signals cover payment requests, urgency, OTP requests, PIN/password requests,
prize/reward promises, account/legal threats, link or remote-access instructions,
and claims to represent an official organization. Wording patterns combine verbs
and objects; isolated words such as bank, prize, payment, and internship are not
enough. Matching normalizes case and Unicode, deduplicates signals, and skips
simple nearby negations such as "never share your OTP".

The text evidence contributes to risk as follows (URL combination is described below):

- Red: OTP or PIN/password request; or payment request combined with urgency,
  reward, or threat.
- Yellow: any other detected signal. Arabic-script content with no matched
  English signals also returns Yellow with an explicit coverage limitation.
- Green: no detected English signals and no Arabic-script coverage flag, with
  an explicit statement that this does not guarantee safety.

Actions reflect detected payment, credential, or link/software requests. Sources
are not invented, and an official-sounding claim is not proof of impersonation.

These bounded English patterns can miss paraphrases, obfuscation, Roman Urdu,
and other languages, and can flag legitimate requests. Negation handling is basic;
quotes, reported speech, and complex context are not understood. Arabic-script
presence is a coverage warning, not language identification or Urdu scam analysis.
Links are assessed only through local URL heuristics; they are never visited,
resolved, or expanded. Claims are not fact-checked.

## Deterministic URL checking and combined risk

`extract_urls(content)` recognizes HTTP(S) and `www.` links, trims surrounding
prose punctuation and unmatched closing brackets, preserves balanced URL
parentheses, and removes exact duplicates while keeping input order. Bare domains
without `www.` or a scheme, obfuscated links, and other protocols are not extracted.
`www.` links are parsed as HTTP because HTTPS was not specified.

`check_url(url)` returns typed evidence containing the original URL, unique signal
names, reasons, and a score counting signals (not a probability). Checks include:

- Missing HTTPS, numeric IP destinations, and three or more subdomain levels.
- A small shortener list and a demo caution list of endings (`xyz`, `top`, `click`,
  `work`, `zip`); neither proves a URL is malicious.
- Combinations of account/payment/reward keywords in the hostname and path.
- Brand/domain mismatch using only the brief's BISP, NADRA, and HEC demo domains,
  plus simple numeric lookalike substitutions. Official-domain matching uses a
  dot boundary and permits subdomains. A brand mention alone does not prove fraud.
- Embedded user information before `@`, encoded/internationalized hostnames,
  addresses over 200 characters, and malformed URLs.

Exact localhost names, `.localhost` subdomains, and loopback IP addresses are
development exceptions for HTTPS/IP/domain heuristics. Private network IPs such
as `192.168.1.20` are still reported as numeric destinations, without asserting they
are malicious. Confusing-address checks still apply to development URLs.

Combined risk preserves strong text results. It also becomes Red when one URL
has at least two of: brand mismatch, embedded credentials, IP destination, and
suspicious keyword combination; or when URL warning evidence accompanies urgency,
payment, reward, threat, or suspicious-action text. Other URL warnings produce
Yellow. Weak warnings on separate URLs are not added together to force Red.
Green requires no text or URL warnings and no Arabic-script coverage warning.
Duplicate reasons are removed. Suspicious links add simple actions to avoid the
link, visit the official website directly, and avoid entering credentials.

Limitations: the lists are small demo heuristics, not reputation data or a complete
official-domain registry. Subdomain counting uses a small suffix list rather than
a full public-suffix database. The checker cannot establish ownership, detect all
lookalikes, inspect destination content, follow redirects, or guarantee safety.
Legitimate sites and quoted examples can be flagged; undetected URLs can be unsafe.
The API contract, empty sources, disabled follow-up, and language preservation are
unchanged. No agent/AI orchestration, dependencies, or network services were added.

## Run locally

Use Python 3.10+ from the repository root:

On Windows, use standard CPython (tested with Python 3.13). The MSYS2 Python on
this machine could not install Pydantic's native dependency.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/docs and submit, for example:

```json
{"content": "Please check this message.", "language": "en"}
```

CORS defaults to `http://localhost:5173` and `http://127.0.0.1:5173`. Override
with comma-separated origins before starting the server, for example:

```powershell
$env:FRONTEND_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
```

Origins include scheme and port, without trailing slashes. Environment variables
are read at startup; no `.env` loader is installed. Credentials are not enabled.

## Foundation validation

Live Uvicorn/API checks passed: health payload, Swagger HTML, OpenAPI schema,
English and Urdu requests, default English language, and nine invalid-request
cases returning standard 422 errors (missing, empty, blank, numeric, or null content;
unsupported language; numeric session identifier; unsupported image field; old
`text` request field). The required input field is now `content`; the old `text`
field is not accepted. OpenAPI exposes source fields `label` and `url`.
CORS preflight passed for both default origins and rejected an unconfigured origin.
Pytest is not configured; no test dependency was added for this milestone.

## Scam-checker validation

Direct checks passed for ten evidence/false-positive cases, including signal
counts, deterministic output, simple negations, and harmless keyword mentions.
Live API checks passed for internship payment, OTP, and prize scams (Red);
assignment and past-payment messages (Green); urgency-only and payment-only
messages (Yellow); PIN/password requests (Red); safety advice (Green); and
official-sounding link instructions (Yellow). English patterns with `language: ur`
preserve that field; Arabic-script no-match content returns limited-coverage Yellow.
Nine invalid-request cases still return standard 422 errors. Health and Swagger
HTML checks passed. No dependencies were added.

## URL milestone validation

Seventeen direct URL cases passed, covering benign/development URLs, IPs,
shorteners, brand boundaries, lookalikes, keywords, subdomains, user information,
and malformed addresses. Extraction, punctuation, duplicate handling, deterministic
output, and deadline urgency checks passed.

Eighteen live API scenarios passed: government-style URL with deadline (Red),
Google (Green), IP login with urgency (Red), reward plus shortener (Red), brand
mismatch plus account/verify path (Red), mixed URLs reflecting stronger evidence,
and previous scam/benign regressions. Standalone weak URLs and warnings on separate
URLs stayed Yellow; localhost stayed Green. Duplicate reasons, Urdu preservation,
nine invalid-request cases (422), health, and Swagger HTML checks also passed.

## Browser API integration

The implemented browser UI is in `web-frontend/`. It calls `POST /verify` with
JSON `{ content, language: "en" }` using `VITE_API_URL` (default
`http://127.0.0.1:8000`). Loading lasts for the request; failures show a friendly
error and never fall back to mock data. Requests time out after 30 seconds and
are canceled when the page unmounts. Backend labels, reasons, actions, sources,
and any returned clarification question are displayed without frontend risk logic.
Images and multi-turn replies remain unsupported by the backend; `session_id`
is reserved and is not sent. Existing development CORS needs no changes.
See `web-frontend/README.md` for startup instructions.
