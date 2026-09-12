# Digital Shield — System Architecture

## 1. Project Overview

**Digital Shield** is an accessible scam, misinformation, suspicious-link, and suspicious-media verification assistant designed especially for users with low digital literacy.

The hackathon prototype has one React + Vite browser frontend and one shared FastAPI backend, with one lightweight verification agent and four tools.

This document describes the target MVP. See [project context](project_context.md) for implemented capabilities; verification currently returns a placeholder.

### Core Product Message

> **Digital Shield doesn't just detect suspicious content — it investigates it.**

### Future Deployment Vision

> **If you know how to forward a WhatsApp message, you know how to use Digital Shield.**

---

# 2. MVP Scope

The target MVP supports:

- Text messages
- Suspicious links
- Screenshots/images
- English
- Urdu
- Simple traffic-light risk results
- Recommended actions
- Browser-based text-to-speech where supported

The MVP does **not** prioritize:

- Audio verification
- Video deepfake detection
- Custom model training
- Real WhatsApp Business API integration
- Multi-agent architecture
- Authentication
- Databases
- Production infrastructure
- Paid APIs

---

# 3. High-Level Architecture

```text
Browser Frontend (React + Vite)
      ↓
FastAPI Backend
      ↓
One Verification Agent
      ↓ selects relevant tools
Scam Checker | URL Checker | Claim Verifier | Vision Tool
      ↓
Evidence
      ↓
Structured Risk Result
```

Tools are selected according to the input; this is not a fixed sequence that runs every tool.

---

# 4. Repository Structure

```text
digital-shield/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── main.py
│   ├── agent/
│   │   ├── verifier.py
│   │   └── prompts.py
│   ├── tools/
│   │   ├── scam_checker.py
│   │   ├── url_checker.py
│   │   ├── claim_verifier.py
│   │   └── vision_tool.py
│   ├── models/
│   │   └── schemas.py
│   └── utils/
│       └── helpers.py
│
├── docs/
│   ├── architecture.md
│   ├── project_context.md
│   ├── development_plan.md
│   ├── demo_plan.md
│   ├── coding_agent_guide.md
│   └── pitch_notes.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 5. Browser Frontend Responsibilities

The browser application is the only frontend in the hackathon prototype. It uses a Digital Shield visual identity and simple, accessible language.

Planned features:

- Text and suspicious-link input
- Screenshot/image upload when backend support is ready
- Risk result, reasons, recommended actions, and relevant sources
- Missing-information follow-up questions
- English/Urdu selector
- Browser text-to-speech where supported
- Loading and error states

The frontend displays backend results; verification and evidence evaluation belong in the backend.

---

# 6. Shared Backend

The browser frontend calls one shared, channel-independent backend.

```text
Browser Frontend → POST /verify → FastAPI Backend
```

Keep verification logic independent of the delivery channel so future integrations can reuse the same engine. No channel-specific business logic is needed for the MVP.

---

# 7. Backend Endpoints

## Primary endpoint

```http
POST /verify
```

Target responsibilities (not yet implemented beyond text validation and a placeholder response):

- Accept text, URL, image, or screenshot
- Pass input to verification agent
- Run selected tools
- Return a standard structured response

## Supporting endpoint

```http
GET /health
```

Used for simple health checks.

Image verification should ideally remain part of `/verify` instead of creating unnecessary duplicate endpoints.

---

# 8. Standard Response Schema

The browser frontend consumes the structured backend response below. These are target result examples; the current placeholder contract is documented in [project context](project_context.md).

Example:

```json
{
  "status": "red",
  "label": "High Risk",
  "summary": "This message shows strong scam indicators.",
  "reasons": [
    "Creates urgency",
    "Contains an unverified link",
    "Requests sensitive action"
  ],
  "actions": [
    "Do not open the link",
    "Do not share OTP or PIN",
    "Verify through the official source"
  ],
  "sources": [],
  "needs_followup": false,
  "followup_question": null,
  "language": "en"
}
```

Example requiring clarification:

```json
{
  "status": "yellow",
  "label": "Need More Information",
  "summary": "There is not enough evidence yet.",
  "reasons": [],
  "actions": [],
  "sources": [],
  "needs_followup": true,
  "followup_question": "Did they ask you for an OTP, PIN, money, or a link?",
  "language": "en"
}
```

---

# 9. Verification Agent

Digital Shield uses **one lightweight verification agent**.

The agent is responsible for:

```text
UNDERSTAND
    ↓
PLAN
    ↓
SELECT TOOLS
    ↓
COLLECT EVIDENCE
    ↓
EVALUATE
    ↓
RESPOND
```

The agent should not automatically run every tool.

It should decide what investigation is needed for the current input.

---

# 10. Agentic Feature 1 — Autonomous Claim Verification

When a message contains a factual claim, the agent determines whether external verification is needed.

Example:

```text
"HEC has announced that universities will remain closed next week."
```

Flow:

```text
Extract factual claim
        ↓
Decide verification is needed
        ↓
Call Claim Verifier
        ↓
Search trusted/relevant sources
        ↓
Compare evidence
        ↓
Return:
confirmed / unconfirmed / conflicting / insufficient evidence
```

The system must not convert **unverified** into **false** without supporting evidence.

---

# 11. Agentic Feature 2 — Intelligent Tool Selection

The agent selects tools according to the content.

Examples:

```text
Suspicious URL
    ↓
URL Checker
```

```text
Public factual claim
    ↓
Claim Verifier
```

```text
Screenshot/image
    ↓
Vision Tool
```

```text
Scam-like text
    ↓
Scam Checker
```

One input may require multiple tools.

Example:

```text
Screenshot:
"Claim your BISP payment at xyz-example.com"
```

Possible flow:

```text
Vision Tool
    ↓
Extract text + URL + claim
    ↓
Claim Verifier
+
URL Checker
+
Scam Checker
    ↓
Combine evidence
    ↓
Final verdict
```

---

# 12. Agentic Feature 3 — Ask for Missing Information

The agent should ask a simple follow-up question when evidence is insufficient.

Example:

```text
User:
Someone called saying my bank account will be blocked.
Is this real?
```

Possible response:

```text
🟡 I need a little more information.

Did they ask you for:
• OTP
• PIN
• Money
• A link
• None of these
```

The next user answer is analyzed as part of the same verification flow.

This prevents the system from guessing when important context is missing.

---

# 13. Tool Responsibilities

## Scam Checker

Checks for common scam indicators:

- Urgency
- Money requests
- OTP/PIN requests
- Prize/reward language
- Threats
- Impersonation
- Suspicious calls to action

---

## URL Checker

Checks:

- URL structure
- HTTPS
- Suspicious TLD/domain
- Lookalike domain patterns
- Excessive subdomains
- IP-address-based URLs
- URL shorteners
- Suspicious keywords
- Brand/domain mismatch

It should use deterministic checks and free resources where possible.

---

## Claim Verifier

Responsibilities:

```text
Receive claim
    ↓
Find relevant trusted evidence
    ↓
Compare claim with evidence
    ↓
Return structured verification result
```

Possible statuses:

- confirmed
- unconfirmed
- conflicting
- insufficient evidence

Trusted/official sources should be preferred when relevant.

---

## Vision Tool

Responsibilities:

- Understand screenshots/images
- Read visible text
- Extract URLs
- Extract factual claims
- Identify suspicious messaging
- Return structured observations to the agent

The vision model is evidence, not absolute proof of AI generation or manipulation.

---

# 14. Risk Assessment

The user should see only simple risk categories:

```text
🟢 LOOKS SAFE
🟡 VERIFY FIRST
🔴 HIGH RISK
```

## Green

No major scam indicators were found.

This is **not a guarantee** that the content is genuine.

## Yellow

The content contains uncertain or suspicious elements, or verification is incomplete.

## Red

Strong scam indicators or dangerous requests are present.

Examples:

- OTP/PIN request
- Money request
- Suspicious login link
- Strong impersonation
- Contradiction with trusted evidence

---

# 15. Accessibility

Accessibility is a core product requirement.

The browser frontend should support:

- English
- Urdu
- Simple language
- Large, recognizable icons
- Risk colors
- Minimal reading
- Clear next actions
- Text-to-speech where supported

Regional languages such as Punjabi, Sindhi, Pashto, and Saraiki are future extensions.

The MVP should prioritize making English and Urdu work well rather than supporting many languages poorly.

---

# 16. Language Strategy

The backend response should be language-aware.

Possible field:

```json
{
  "language": "ur"
}
```

The verification logic should remain independent of the presentation language.

This means:

```text
Evidence / risk logic
        ↓
Language-aware explanation layer
        ↓
English or Urdu response
```

This separation makes future regional-language expansion easier.

---

# 17. Voice Accessibility

The browser frontend may provide:

```text
🔊 Listen
```

For the MVP, browser text-to-speech can be used where supported.

This avoids additional paid services and helps users with limited literacy.

---

# 18. Prototype vs Future Deployment

## Hackathon Prototype

The implemented frontend channel is the browser application. The repository currently has a Vite starter and a FastAPI foundation; the verification experience is still planned.

```text
Browser Application → FastAPI → Verification Agent → Selected Tools
```

## Future Deployment and Pitch Visualization

WhatsApp appears only as a presentation concept: a slide animation shows a suspicious message being forwarded to Digital Shield, investigated, and answered with a risk result. This animation is not an implemented system or a live integration.

The same channel-independent verification engine could later connect to the official WhatsApp API, a mobile app, a browser extension, or a kiosk. None of these integrations is part of the MVP.

---

# 19. MVP Development Order

1. Backend foundation
2. Scam checker
3. Verification agent
4. URL checker
5. Browser frontend
6. Frontend/backend connection
7. Claim verifier
8. Vision tool
9. Intelligent tool selection
10. Follow-up questions
11. English/Urdu
12. Browser text-to-speech
13. Demo hardening

Implementation should be done in small, testable batches.

---

# 20. Demo Scenarios

## Scenario 1 — Fake Internship Scam

Demonstrates:

- Scam analysis
- Money request
- Urgency
- Clear risk response

## Scenario 2 — Government Claim + Suspicious URL

Demonstrates:

- Claim extraction
- Claim verification
- URL checking
- Multi-tool agent behavior

## Scenario 3 — Missing Information

Demonstrates:

- Clarifying question
- Multi-turn verification
- Responsible uncertainty

## Scenario 4 — Screenshot

Demonstrates:

- Vision understanding
- Extraction of suspicious content
- Agent tool selection

---

# 21. Architecture Rules

1. One shared backend.
2. One browser frontend.
3. One structured backend API contract.
4. No duplicated verification logic in the frontend.
5. One verification agent, not multiple agents.
6. Agent selects tools instead of running everything automatically.
7. Evidence is separated from user-facing explanation.
8. Unverified does not mean false.
9. Avoid claiming perfect deepfake detection.
10. Only free tools/resources for the hackathon MVP.
11. No unnecessary infrastructure.
12. Prioritize reliable demo behavior over technical complexity.

---

# 22. Pitch Architecture

Show the browser application as the actual prototype and describe the engine:

```text
USER → UNDERSTAND → INVESTIGATE → VERIFY → PROTECT
```

> **Digital Shield doesn't just detect suspicious content — it investigates it.**

For the future deployment vision, show the WhatsApp slide animation and say:

> **If you know how to forward a WhatsApp message, you know how to use Digital Shield.**

Make clear that the animation is a presentation concept, not functionality built for this hackathon. The same engine could later serve multiple channels.

---

