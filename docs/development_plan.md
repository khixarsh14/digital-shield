# Digital Shield — Development Plan

## Goal and constraints

Build a reliable hackathon MVP with one React + Vite browser frontend, one shared
FastAPI backend, one lightweight verification agent, and four focused tools.
Prioritize end-to-end flow, agentic behavior, accessibility, demo reliability, and polish.

Use free tools/resources only. No custom ML training, authentication, database
unless later required, or real WhatsApp API integration for the MVP. WhatsApp is
only a future deployment concept shown in slides; it has no frontend milestone.

## Repository alignment

Use `frontend/`, `backend/`, and `docs/`, with root `requirements.txt`,
`.env.example`, `.gitignore`, and `README.md`. The existing Vite starter has been
moved to `frontend/`; no product UI was built during alignment. Preserve unrelated
working code. Keep secrets out of version control.

## 1. Backend foundation — implemented

FastAPI, typed schemas, `GET /health`, placeholder `POST /verify`, Swagger, and a
root redirect are implemented. Live checks passed. Verification is still pending;
see `project_context.md` for the exact contract.

## 2. Scam checker

Implement signals for urgency, money requests, OTP/PIN requests, rewards, threats,
and impersonation. Known examples should return structured signals and reasons.
Keep analysis in the backend.

## 3. Verification agent

Implement one lightweight agent that understands input, uses scam-checker evidence,
and returns traffic-light status, summary, reasons, and actions. Separate evidence
from presentation. Missing evidence is not proof of falsehood.

## 4. URL checker

Implement deterministic URL checks with useful signals. Normal-looking URLs must
not automatically be marked dangerous. Use the tool when a URL warrants investigation.

## 5. Browser frontend

Build the Digital Shield interface in `frontend/`: input, results, and loading/error
states. Use an accessible visual identity. No verification logic belongs in the UI.

## 6. Frontend/backend connection

Connect input to `POST /verify` through the service layer. Verify real API responses
render correctly and validation/network failures are handled.

## 7. Claim verifier

Enable autonomous factual-claim verification using free trusted/relevant sources.
Return confirmed, unconfirmed, conflicting, or insufficient-evidence results with
sources. Do not convert unverified into false.

## 8. Vision tool

Add screenshot/image support. Extract visible content, URLs, and claims for the
agent. Observations are not absolute proof of manipulation or AI generation.

## 9. Intelligent tool selection

Route to scam checker, URL checker, claim verifier, and vision tool according to
input. Test relevant selection instead of automatically running all tools.

## 10. Follow-up questions

Ask simple missing-information questions. The browser should display and continue
the flow, with subsequent answers interpreted in context. Test follow-up state and
`needs_followup`/`followup_question` fields.

## 11. English/Urdu

Support language selection and explanations in that language. Keep risk logic
independent of translation. Currently only the language field is preserved;
placeholder copy remains English.

## 12. Browser text-to-speech

Add a listen control where browser speech is supported and handle unavailable
speech or voices. No paid TTS service is required.

## 13. Demo hardening

Rehearse repeatable browser scenarios: scam, claim plus URL, missing information,
and screenshot when ready. Check loading, errors, mobile layout, Urdu, sources,
and clear results. Follow `demo_plan.md`; label WhatsApp animation as a future
concept. Do not add unrelated features during final polish.

## Future options

Regional languages, stronger reputation sources, awareness content, and additional
channels can follow the MVP. Audio/video analysis and multi-agent systems are out
of current scope.