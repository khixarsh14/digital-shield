# Digital Shield — System Architecture

## 1. Project Overview

**Digital Shield** is an accessible scam, misinformation, suspicious-link, and suspicious-media verification assistant designed especially for users with low digital literacy.

The system uses one shared verification backend and exposes it through two different frontend experiences:

1. **WhatsApp Simulator Frontend** — demonstrates the intended future WhatsApp experience.
2. **Browser Frontend** — provides a richer Digital Shield web experience.

Both frontends use the **same backend, verification agent, tools, and response schema**.

### Core Product Message

> **Digital Shield doesn't just detect suspicious content — it investigates it.**

### Accessibility Message

> **If you know how to forward a WhatsApp message, you know how to use Digital Shield.**

---

# 2. MVP Scope

The MVP supports:

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
                       DIGITAL SHIELD
                             │
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
┌────────────────────────┐       ┌────────────────────────┐
│ WhatsApp Simulator     │       │ Browser Frontend       │
│ React + Vite           │       │ React + Vite           │
│                        │       │                        │
│ Familiar chat UX       │       │ Rich web experience    │
│ Forward-style flow     │       │ Cards / upload / info  │
└────────────┬───────────┘       └────────────┬───────────┘
             │                                │
             └──────────────┬─────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ FastAPI       │
                    │ Shared API    │
                    └───────┬───────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Verification Agent   │
                 │ Understand           │
                 │ Plan                 │
                 │ Select Tools         │
                 │ Evaluate Evidence    │
                 │ Respond              │
                 └─────────┬────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────────┐
│ Scam Checker   │ │ URL Checker    │ │ Claim Verifier   │
└────────────────┘ └────────────────┘ └──────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Vision Tool      │
                  │ Screenshot/Image │
                  └──────────────────┘
                           │
                           ▼
                    Evidence Set
                           │
                           ▼
                 Final Decision Engine
                           │
                           ▼
                 Structured JSON Response
```

---

# 4. Repository Structure

```text
digital-shield/
│
├── whatsapp-frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── web-frontend/
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
│   ├── test_cases.md
│   ├── coding_agent_guide.md
│   └── pitch_notes.md
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 5. Frontend Responsibilities

## 5.1 WhatsApp Simulator Frontend

Purpose:

Demonstrate how Digital Shield could work when eventually connected to WhatsApp.

The interface should feel familiar to users who already use WhatsApp.

### Main features

- Chat-style conversation
- Forwarded-message appearance
- Text input
- Screenshot/image upload
- Suspicious-link input
- Agent status messages
- Risk result in chat format
- Follow-up questions
- English/Urdu
- Listen button

### Example

```text
User:
[Forwarded image]

Digital Shield:
🛡 Checking...

✓ Message understood
✓ Link checked
✓ Claim verified

🔴 HIGH RISK

This message may be a scam.

Why?
💰 It asks for money
🔗 The link looks suspicious

What should you do?
❌ Do not send money
✅ Verify using the official source

🔊 Listen
```

The simulator should never be presented as a real WhatsApp integration.

---

## 5.2 Browser Frontend

Purpose:

Provide a richer Digital Shield experience for users who access the service through the web.

This frontend should have its own visual identity rather than copying WhatsApp.

### Possible sections

- Hero / product introduction
- Verify a message
- Check a link
- Upload screenshot
- Analysis result
- Evidence / sources where relevant
- Recommended actions
- English/Urdu selector
- Accessibility controls
- How Digital Shield works
- Scam-awareness information

### Design principle

The browser frontend can expose more information than the WhatsApp simulator, but it must still avoid technical jargon.

---

# 6. Shared Backend

Both frontends call the same backend.

The backend must remain **channel-independent**.

It should not contain WhatsApp-specific or website-specific business logic.

```text
WhatsApp Simulator ─┐
                    ├── POST /verify ──> Shared Backend
Browser Frontend ───┘
```

This allows future channels to reuse the same verification engine.

Possible future channels:

- Official WhatsApp Business API
- Mobile app
- Browser extension
- Kiosk
- Other messaging platforms

---

# 7. Backend Endpoints

## Primary endpoint

```http
POST /verify
```

Responsibilities:

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

Both frontends must receive the same response format.

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

Both frontends should support:

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

Both frontends may provide:

```text
🔊 Listen
```

For the MVP, browser text-to-speech can be used where supported.

This avoids additional paid services and helps users with limited literacy.

---

# 18. Prototype vs Production

## Hackathon Prototype

```text
WhatsApp Simulator
          │
          ├──────────┐
          │          │
Browser Web App      │
          │          │
          └────┬─────┘
               ↓
          FastAPI Backend
               ↓
       Verification Agent
               ↓
         Lightweight Tools
```

## Future Production

```text
Official WhatsApp
Website
Mobile App
Browser Extension
Other Channels
        │
        └────> Same Verification Backend
```

The shared backend is therefore the core product, while frontends are delivery channels.

---

# 19. MVP Development Order

Recommended sequence:

```text
1. FastAPI skeleton + schemas
2. Scam checker
3. Basic verification agent
4. POST /verify
5. Swagger/manual backend testing
6. URL checker
7. Browser frontend base UI
8. WhatsApp simulator base UI
9. Connect both frontends to same API
10. Claim verifier
11. Vision tool
12. Agent tool selection
13. Follow-up question flow
14. English/Urdu
15. Text-to-speech
16. Demo polishing
```

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
2. Two independent frontend designs.
3. Same API contract for both frontends.
4. No duplicated verification logic in frontends.
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

For judges, explain the system simply:

```text
USER
 ↓
Digital Shield
 ↓
UNDERSTAND
 ↓
INVESTIGATE
 ↓
VERIFY
 ↓
PROTECT
```

Then explain that the same verification engine powers:

```text
WhatsApp Experience
        +
Browser Experience
```

Strong architecture line:

> **One verification engine. Multiple accessible channels.**

Strong technical line:

> **Digital Shield doesn't just detect suspicious content — it investigates it.**

Strong accessibility line:

> **If you know how to forward a WhatsApp message, you know how to use Digital Shield.**
