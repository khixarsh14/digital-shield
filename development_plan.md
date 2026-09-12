# Digital Shield — Development Plan

## Goal

Build a reliable hackathon MVP with one shared backend and two separate frontends.

Development should prioritize:

1. Working end-to-end flow
2. Agentic behavior
3. Accessibility
4. Demo reliability
5. Visual polish

---

# Phase 1 — Foundation

## Milestone 1: Repository Setup

Create:

```text
whatsapp-frontend/
web-frontend/
backend/
docs/
```

Add:

- `.gitignore`
- `.env.example`
- `requirements.txt`
- `README.md`

Acceptance:

- Project structure is clean.
- Both frontend folders and backend folder exist.
- Environment secrets are not committed.

---

## Milestone 2: Backend Skeleton

Implement:

- FastAPI app
- `GET /health`
- Base request/response schemas
- Initial `POST /verify`

Acceptance:

- FastAPI starts successfully.
- Swagger loads.
- `/health` works.
- `/verify` returns a valid structured placeholder response.

---

# Phase 2 — Core Verification

## Milestone 3: Scam Checker

Implement lightweight scam-pattern analysis.

Signals may include:

- Urgency
- Money requests
- OTP/PIN requests
- Rewards/prizes
- Threats
- Impersonation

Acceptance:

- Known scam examples return meaningful reasons.
- Checker returns structured data.
- No frontend logic is added here.

---

## Milestone 4: Basic Verification Agent

Implement one agent that:

- Understands the input
- Uses scam-checker evidence
- Produces structured result
- Can return follow-up state

Acceptance:

- `/verify` returns Green/Yellow/Red-compatible structured output.
- Output contains summary, reasons, actions.

---

## Milestone 5: URL Checker

Implement deterministic URL checks.

Acceptance:

- Suspicious URLs return useful signals.
- Normal-looking URLs are not automatically marked dangerous.
- Agent can use URL checker when a URL is present.

---

# Phase 3 — Frontends

## Milestone 6: Browser Frontend Base

Build:

- Main Digital Shield layout
- Text verification input
- Result display
- API service layer

Acceptance:

- User can submit text.
- Browser frontend displays backend result.

---

## Milestone 7: WhatsApp Simulator Base

Build:

- Chat header
- Chat bubbles
- Message input
- Result message rendering

Acceptance:

- User can send text.
- Same backend response is rendered in chat style.
- No verification logic is duplicated in frontend.

---

# Phase 4 — Agentic Capabilities

## Milestone 8: Claim Verifier

Implement claim-verification tool using free resources.

Acceptance:

- Agent can identify a factual claim.
- Tool returns structured verification state.
- Sources/evidence can be attached where available.

---

## Milestone 9: Intelligent Tool Selection

Agent decides whether to use:

- Scam checker
- URL checker
- Claim verifier
- Vision tool

Acceptance:

- Different inputs trigger different tools.
- Agent does not blindly run everything.

---

## Milestone 10: Follow-Up Questions

Implement clarification flow.

Acceptance:

- Insufficient information returns `needs_followup: true`.
- Both frontends can display and continue from the follow-up question.

---

# Phase 5 — Multimodal

## Milestone 11: Vision Tool

Add screenshot/image analysis.

Acceptance:

- Image can be submitted.
- Visible text/claims/URLs can be extracted or understood.
- Agent can send extracted content to other tools.

---

# Phase 6 — Accessibility

## Milestone 12: English / Urdu

Add language-aware output.

Acceptance:

- User can select English or Urdu.
- Backend result follows selected language.
- Risk logic remains independent of translation.

---

## Milestone 13: Listen Button

Add browser text-to-speech where supported.

Acceptance:

- Result can be read aloud.
- No paid TTS service is required for MVP.

---

# Phase 7 — Demo Hardening

## Milestone 14: Test Scenarios

Lock 3–4 demo cases.

Acceptance:

- Each scenario is repeatable.
- Expected output is known.
- Both frontends behave consistently.

---

## Milestone 15: Polish

Focus on:

- Loading states
- Error handling
- Mobile responsiveness
- Urdu readability
- Visual consistency
- Clear risk hierarchy

Do not add unrelated features during final polish.

---

# Feature Prioritization

## Must Have

- Shared backend
- Browser frontend
- WhatsApp simulator
- Text analysis
- URL analysis
- Claim verification
- Agent tool selection
- Follow-up questions
- English/Urdu
- Structured risk results

## Should Have

- Screenshot/image analysis
- Text-to-speech
- Evidence/source display

## Could Have

- Extra regional languages
- More sophisticated reputation checks
- Trusted-contact sharing
- Awareness library

## Not Now

- Audio deepfake detection
- Video deepfake detection
- Real WhatsApp integration
- Authentication
- Database
- Multi-agent system
