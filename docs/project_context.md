# Digital Shield — Project Context

## Current architecture and direction

- One React + Vite browser frontend in `frontend/` (existing starter, product UI pending).
- One shared FastAPI backend.
- One verifier selecting scam, URL, claim, and image/video tools according to available input evidence.
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
- `/verify` delegates to `backend/agent/verifier.py`. The deterministic verifier
  runs English scam analysis, extracts HTTP(S)/www URLs, checks only the extracted
  URLs, detects factual claim candidates, and checks detected claims with Tavily.
  Trusted claim sources populate `sources`; follow-up remains false and its question null.
  The requested language is preserved; user-facing copy remains English.
- Swagger UI is available at `/docs`, with the API schema at `/openapi.json`.
  Opening `/` redirects to `/docs`.

The deterministic verification agent, scam checker, and URL checker are implemented.
Claim candidate detection and an independent Tavily claim tool are implemented.
Image/video evidence extraction uses Gemini. The verifier now routes to these
tools for media and reuses their extracted text, URLs, and claims. Follow-up,
session storage, database, and authentication remain unimplemented.

## Deterministic scam checker

`check_scam(content)` returns typed evidence with unique `signals`, corresponding
`reasons`, a `score` counting distinct signals, and an Arabic-script coverage flag.
The score is not a probability. The tool does not generate the final API response
and is reused by the verification agent.

Signals cover payment requests, urgency, OTP requests, PIN/password requests,
prize/reward promises, account/legal threats, link or remote-access instructions,
and claims to represent an official organization. Wording patterns combine verbs
and objects; isolated words such as bank, prize, payment, and internship are not
enough. Matching normalizes case and Unicode, deduplicates signals, and skips
simple nearby negations such as "never share your OTP".

The text evidence contributes to risk as follows (URL combination is described below):

- Red: OTP or PIN/password request; or payment request combined with urgency,
  reward, or threat.
- Yellow: any other detected signal. With no text or URL warnings, requested
  Urdu (`language: ur`) or Arabic-script content returns Yellow with an explicit
  English-only coverage limitation, even when the script flag is false.
- Green: no detected English signals, no Arabic-script coverage flag, and no Urdu request, with
  an explicit statement that this does not guarantee safety.

Actions reflect detected payment, credential, or link/software requests. Sources
are not invented, and an official-sounding claim is not proof of impersonation.

These bounded English patterns can miss paraphrases, obfuscation, Roman Urdu,
and other languages, and can flag legitimate requests. Negation handling is basic;
quotes, reported speech, and complex context are not understood. Arabic-script
presence is a coverage warning, not language identification or Urdu scam analysis.
Links are assessed only through local URL heuristics; they are never visited,
resolved, or expanded by the URL checker. Detected claims are checked separately
through the existing Tavily tool.

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
Green requires no text or URL warnings, no Arabic-script coverage warning, and no Urdu request.
Duplicate reasons are removed. Suspicious links add simple actions to avoid the
link, visit the official website directly, and avoid entering credentials.

Limitations: the lists are small demo heuristics, not reputation data or a complete
official-domain registry. Subdomain counting uses a small suffix list rather than
a full public-suffix database. The checker cannot establish ownership, detect all
lookalikes, inspect destination content, follow redirects, or guarantee safety.
Legitimate sites and quoted examples can be flagged; undetected URLs can be unsafe.
The `VerifyResponse` shape, disabled follow-up, and language preservation are
unchanged. Source lists now contain trusted claim evidence when available.

## Verification agent/orchestrator

`verify_content(request: VerifyRequest) -> VerifyResponse` in
`backend/agent/verifier.py` is the central orchestration entry point. It calls the
scam checker for text, the URL checker for each distinct link, and the claim
verifier only for detected claims. Candidate detection reuses the existing
sentence helper and detector. Duplicate claims are checked once per request.

Risk combination, reason deduplication, actions, language preservation, and final
response construction live in the verifier. Existing scam/URL rules are retained
and combined with claim/media evidence. Tools remain independent collectors; no scam or
URL heuristics were moved into the agent. The `/verify` route only accepts the
validated request and returns the verifier's result. Blocking provider calls run
in a worker thread rather than blocking the async API event loop.

Tool selection and risk combination remain deterministic. Image/video extraction
uses Gemini; the existing English-pattern and URL-heuristic limitations remain.

`verify_media(data, mime, language)` selects only the matching image or video tool.
It feeds visible/spoken text to the scam checker, extracted URLs to the URL checker,
and extracted claims to the claim verifier, deduplicating against candidates in
the extracted text. It does not treat model summaries or signal names as verified
facts. Model observations are labeled as such in the reasons.

Claims supported by official snippet evidence can remain Green only if no other
risk or uncertainty applies. Reliable contradiction contributes Red; conflicting,
insufficient, missing-key, or unavailable claim evidence contributes Yellow,
never an assertion of falsehood. Confirmation cannot override scam or URL risk.
Only trusted claim evidence is mapped to public `Source(label, url)` entries,
deduplicated by URL. Failed/empty/low-confidence media or uncertain visual cues
contribute Yellow. Visual cues alone do not establish Red or prove manipulation.

JSON `POST /verify` retains its existing request and response schemas. Multipart
`POST /analyze-media` still returns extraction evidence by default. Use
`POST /analyze-media?verify=true&language=en` (or `ur`) with a single `file` field
to receive the combined `VerifyResponse`. Existing extension/MIME/signature and
size validation, temporary-file cleanup, and upload limits are reused. No new
dependencies, endpoints, storage, follow-up, or frontend functionality were added.

Tavily/Gemini keys must be in the process environment; `.env` is not automatically
loaded. Requests can now incur provider usage only when the corresponding tool is
selected. Multiple distinct claims can make multiple searches. Model extraction,
narrow claim matching, source coverage, and relative-date limitations remain;
sources support evidence, not a guarantee of authenticity.

## Claim tools

`detect_claim(content)` in `backend/tools/claim_detector.py` returns a typed
candidate (`has_claim`, nullable `claim`). It extracts the first English sentence
starting with a known organization or generic institution followed by a narrow
announcement/policy predicate. It preserves Rs. amounts and rejects questions
and instructions. This is candidate detection, not an assertion of truth.

`verify_claim(claim)` in `backend/tools/claim_verifier.py` accepts a single claim
of at most 500 characters. It makes one Tavily Search POST using standard-library
HTTP, a 15-second timeout, basic search, and at most five requested results.
Automatic parameter selection, generated answers, images, and raw content are
disabled. There are no retries or secondary searches. Basic search consumes
Tavily credits; use the free allowance and manage the account quota separately.
See the [Tavily Search API](https://docs.tavily.com/documentation/api-reference/endpoint/search).

Set `TAVILY_API_KEY` in the process environment. `.env.example` contains a
placeholder only; `.env` files are not loaded automatically. No key is hardcoded
or logged. Missing configuration, HTTP/network errors, malformed JSON/results,
and empty evidence return `insufficient_evidence` with a sanitized explanation.

Internal evidence includes title, URL, snippet, trusted flag, and source kind.
Only valid HTTP(S) result URLs and minimally relevant snippets are retained;
duplicate URLs are removed and at most five evidence items are returned. Ranking
prefers HTTPS `.gov.pk`/existing official reference domains, then the small news
list (Dawn, Reuters, BBC), then other results. Domain checks use dot boundaries
and reject user-info URLs for trust. Trust means a source preference, not a
guarantee that the page or search snippet is accurate.

Decision rules deliberately trade recall for caution:

- `confirmed`: a complete normalized statement matches an official snippet sentence.
- `contradicted`: an official sentence matches the same statement with explicit
  auxiliary negation added/removed (has/have/had/will/is/are/was/were + not).
- `conflicting`: both matching positions occur in retained official evidence.
- `insufficient_evidence`: no clear match, weak/nonofficial/irrelevant results,
  uncertain input, or search failure. This does not mean false.

Relative dates (today, next week, this month, etc.) are not resolved and cannot
produce automatic confirmation. Questions and double-quoted snippet sentences
are excluded from decisive matching. News is retained as context but does not
produce an automatic verdict on its own. Amounts and factual wording must match;
the tool does not infer equivalence or contradiction from loose keyword overlap.

Limitations include narrow English detection, no paraphrase understanding,
no full-page inspection, incomplete date/context/quotation handling, small source
lists, and dependence on search snippets that may be stale or incomplete. Even
an exact official-snippet match is not a guarantee of factual truth. Most real
claims will conservatively return insufficient evidence. No external LLM is used.

The detector and Tavily tool are connected to `verify_content` for detected claims
and reused after media extraction. Public response schemas remain unchanged;
claim uncertainty now prevents an otherwise unsupported Green result.

For manual use after setting the key, run Python from the repository root:

```python
from backend.tools.claim_detector import detect_claim
from backend.tools.claim_verifier import verify_claim

candidate = detect_claim("BISP has launched a new Rs. 25,000 payment scheme.")
if candidate.has_claim:
    print(verify_claim(candidate.claim).model_dump_json(indent=2))
```

Claim-tool tests mock Tavily and require no internet or real key. The full suite
passes 20 tests, including existing verifier regressions. No live Tavily request
was run during this milestone because `TAVILY_API_KEY` was not configured.

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
The foundation originally used manual checks; pytest now runs the backend suite below.

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

## Orchestrator validation

Three standard-library unittest tests passed, covering tool-call selection,
all distinct URLs, reason deduplication, and risk/language regressions. Run with
`.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.
Ten live responses matched the complete pre-refactor responses, including normal
text, OTP, normal/suspicious URLs, reward/shortener, Urdu coverage, multiple URLs,
and weak evidence. Nine invalid requests returned 422. Health, Swagger HTML,
the root redirect, and OpenAPI checks passed. No testing dependency was added.

## Automated backend tests

Install development dependencies and run from the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

`requirements-dev.txt` adds pytest and httpx for FastAPI's in-process TestClient.
`pytest.ini` discovers `tests/`, including the preserved unittest classes. The
suite covers health, verification, validation, Swagger/OpenAPI, CORS, scam/URL
evidence and false positives, verifier routing, claim detection, mocked Tavily
verification, and the current image/video tools and multipart upload endpoint.
Media tests use mocked extraction and container-signature fixtures; they do not
validate live Gemini accuracy or actual video decoding.

Fixtures remove real provider keys, mock provider responses, and block external
connections (loopback remains available for Windows asyncio internals). No API
credits, internet, running server, or `.env` keys are needed. Current result:
119 tests passed, 23 unittest subtests passed, zero failures. Two upstream
Starlette/AnyIO TestClient deprecation warnings remain. Routing tests cover skipped
tools, claim statuses, source trust/deduplication, media reuse, provider failures,
uncertainty, preservation of stronger scam risk, and opt-in media verdicts.
