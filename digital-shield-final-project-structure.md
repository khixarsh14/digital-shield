# Digital Shield — Final Project Structure

## 1. Project Proposition

**Digital Shield** is a WhatsApp-style verification assistant designed for people with low digital literacy.

The user forwards suspicious content, and the system investigates it using a lightweight verification agent and specialized tools.

### Core Flow

```text
Forward suspicious content
        ↓
Agent understands it
        ↓
Agent decides what needs investigation
        ↓
Uses the right verification tool
        ↓
Evaluates evidence
        ↓
Returns simple result

🟢 Looks Safe
🟡 Verify First
🔴 High Risk
```

### Core Differentiator

> **Digital Shield doesn't just detect suspicious content. It investigates it.**

---

## 2. MVP Scope

The hackathon MVP will support:

- Text messages
- Suspicious links
- Screenshots/images

The first version will **not** focus on audio or video.

The verification agent can perform:

- Scam-pattern analysis
- URL checking
- Claim verification
- Screenshot/image understanding
- Follow-up questioning when information is insufficient

---

## 3. Final Architecture

```text
                 FRONTEND
           React + Vite Web App
        WhatsApp-style interface

                    │
                    ▼

              POST /verify

                    │
                    ▼

            VERIFICATION AGENT
     Understand + Plan + Select Tools

       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
 Scam Checker   URL Checker   Claim Verifier
                                   │
                              Web/Search
       │
       └────────────┐
                    │
             Vision Tool
        Screenshot/Image analysis

                    ↓

              EVIDENCE SET

                    ↓

          FINAL DECISION ENGINE

                    ↓

       Structured JSON Response

                    ↓

      🟢 / 🟡 / 🔴 + explanation
            + recommended action
```

---

## 4. Final Repository Structure

```text
digital-shield/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatHeader.jsx
│   │   │   ├── ChatBubble.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   ├── TrustSignalCard.jsx
│   │   │   ├── ReasonList.jsx
│   │   │   └── AudioButton.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   │
│   ├── main.py
│   │
│   ├── agent/
│   │   ├── verifier.py
│   │   └── prompts.py
│   │
│   ├── tools/
│   │   ├── scam_checker.py
│   │   ├── url_checker.py
│   │   ├── claim_verifier.py
│   │   └── vision_tool.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── utils/
│       └── helpers.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 5. Backend Endpoints

### Primary Endpoint

```http
POST /verify
```

This endpoint receives content from the frontend and sends it to the verification agent.

### Optional Endpoints

```http
GET /health
POST /verify-image
```

Ideally, image verification can later be handled through the same `/verify` endpoint.

---

## 6. Standard Backend Response Format

Every investigation should return the same structured response.

### Example: High Risk

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
  "needs_followup": false,
  "followup_question": null
}
```

### Example: More Information Needed

```json
{
  "status": "yellow",
  "label": "Need More Information",
  "summary": "There is not enough evidence yet.",
  "reasons": [],
  "actions": [],
  "needs_followup": true,
  "followup_question": "Did they ask you for an OTP, PIN, money, or a link?"
}
```

---

## 7. Tool Responsibilities

### `scam_checker.py`

Checks for common scam patterns such as:

- Urgency
- Money requests
- OTP/PIN requests
- Reward or prize language
- Threats
- Impersonation patterns

---

### `url_checker.py`

Checks:

- URL format
- HTTPS usage
- Suspicious TLD/domain
- Lookalike domains
- Potential reputation signals

---

### `claim_verifier.py`

Responsible for:

```text
Extract factual claim
        ↓
Search trusted sources
        ↓
Compare evidence
        ↓
Return:
confirmed / unconfirmed / conflicting
```

---

### `vision_tool.py`

Responsible for:

```text
Screenshot / image
        ↓
Extract and understand visible content
        ↓
Identify text, links, claims, and suspicious elements
        ↓
Return structured information to verification agent
```

---

## 8. Verification Agent Responsibility

The agent does **not** perform every verification by itself.

Its role is:

```text
Understand
    ↓
Plan
    ↓
Choose tools
    ↓
Collect evidence
    ↓
Reason over evidence
    ↓
Produce verdict
```

### Simple Explanation

```text
Agent = Investigator
Tools = Evidence Collectors
```

This is the main agentic architecture of Digital Shield.

---

## 9. LLM Responsibilities

The LLM can be used for:

- Understanding user content
- Extracting claims
- Identifying what needs investigation
- Selecting tools
- Combining evidence
- Asking follow-up questions
- Explaining results in simple English/Urdu

The LLM should **not** be the only source of truth for factual verification.

For example:

- URL reputation should come from the URL tool
- Public claims should be checked against trusted sources
- Image content should be analyzed by the vision tool

The LLM reasons over the evidence collected by these tools.

---

## 10. What We Are Not Building for the MVP

To keep the project feasible during the hackathon, the MVP will not include:

- Custom ML model training
- Multi-agent architecture
- PostgreSQL/database
- User authentication
- Real WhatsApp Business API integration
- Real family-contact notification system
- Video deepfake detection
- Complex dashboard
- Blockchain

These can be presented as future extensions where relevant.

---

## 11. Pitch Architecture vs Prototype

### What We Pitch

```text
WhatsApp
    ↓
Digital Shield Agent
    ↓
Verification Tools
    ↓
Evidence
    ↓
Simple Safety Response
```

### What We Actually Build

```text
React WhatsApp Simulator
        ↓
FastAPI Backend
        ↓
One Verification Agent
        ↓
3–4 Lightweight Tools
        ↓
Structured Verdict
```

The browser prototype demonstrates the intended WhatsApp experience while keeping the hackathon implementation practical.

---

## 12. User Experience Philosophy

The complicated investigation happens behind the scenes.

The user should not see technical outputs such as:

```text
87% phishing probability
Domain reputation score
Synthetic media classifier score
```

Instead, the user receives:

```text
🔴 HIGH RISK

Why?
• Creates urgency
• Contains an unverified link
• Requests sensitive information

What should you do?
• Do not open the link
• Do not share OTP/PIN
• Verify through the official source
```

Optional accessibility features:

- Simple English/Urdu
- Large icons
- Clear risk colors
- Browser-based text-to-speech
- Minimal reading required

---

## 13. Final Product Positioning

### Main Pitch Line

> **If you know how to forward a WhatsApp message, you know how to use Digital Shield.**

### Product Philosophy

> **Forward → Verify → Stay Safe**

### Main Technical Differentiator

> **Digital Shield doesn't just detect suspicious content — it investigates it.**

---

## 14. Backend Implementation Order

The backend should be built in this order:

```text
1. FastAPI skeleton
2. models/schemas.py
3. tools/scam_checker.py
4. agent/verifier.py
5. POST /verify
6. Test with Swagger
7. Add url_checker.py
8. Add claim_verifier.py
9. Add vision_tool.py
10. Connect frontend
```

This gives the team a working end-to-end verification flow quickly before adding more advanced capabilities.
