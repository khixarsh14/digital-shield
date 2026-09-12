# Digital Shield — Pitch Notes

## 1. Problem

Generative AI, phishing, impersonation, and digital scams make fake or misleading content increasingly easy to create and distribute.

The people most vulnerable are often those who have the least access to technical verification tools.

Existing solutions are frequently:

- Too technical
- Full of jargon
- Separate from where misinformation spreads
- Difficult for low-literacy users

---

# 2. Solution

Digital Shield is an accessible verification assistant that investigates suspicious:

- Messages
- Links
- Screenshots/images
- Public claims

The result is simplified into:

- 🟢 Looks Safe
- 🟡 Verify First
- 🔴 High Risk

Then Digital Shield explains:

- Why
- What the user should do next

---

# 3. Agentic Differentiator

> **Digital Shield doesn't just detect suspicious content — it investigates it.**

The planned agent will:

1. Verify factual claims
2. Select the right tool based on content
3. Ask for missing information instead of guessing

Simple flow:

```text
UNDERSTAND
    ↓
INVESTIGATE
    ↓
VERIFY
    ↓
PROTECT
```

---

# 4. Browser Prototype and Future Deployment Vision

The browser application is the actual hackathon prototype. It is the only live frontend and will provide input, sources, explanations, and accessibility controls.

WhatsApp is shown only through a slide animation: a suspicious message is forwarded to Digital Shield, investigated, and answered with a risk result. This is a presentation concept, not a built integration.

Frame this line explicitly as the future deployment vision:

> **If you know how to forward a WhatsApp message, you know how to use Digital Shield.**

Then transition to:

> “For the hackathon prototype, we implemented the verification experience as a browser application.”

Use that completed-prototype wording only once the browser verification flow is actually implemented. At present, the repository contains the Vite starter and backend foundation.

The same verification engine could later connect to WhatsApp and other channels.

---

# 5. Accessibility

Accessibility is not an extra feature.

Digital Shield is designed around:

- Simple language
- English and Urdu
- Icons
- Traffic-light results
- Clear next actions
- Optional text-to-speech
- Minimal technical jargon

Future regional-language support may include:

- Punjabi
- Sindhi
- Pashto
- Saraiki

---

# 6. Feasibility

The MVP intentionally avoids unnecessary complexity.

We are using:

- One backend
- One lightweight agent
- Small verification tools
- One React + Vite browser frontend
- Free tools/resources
- No custom model training
- No real WhatsApp integration during the hackathon

This makes the prototype achievable and demo-friendly.

---

# 7. Scalability

The verification backend is channel-independent.

Future channels can include:

```text
WhatsApp
Mobile App
Browser Extension
Kiosk
```

Future capabilities may include:

- More regional languages
- Stronger reputation sources
- Audio analysis
- Video analysis
- Trusted-contact escalation
- Reporting workflows

---

# 8. Strong Lines

### Main Product Line

> **Forward → Verify → Stay Safe**

### Main Technical Line

> **Digital Shield doesn't just detect suspicious content — it investigates it.**

### Future Deployment Accessibility Line

> **If you know how to forward a WhatsApp message, you know how to use Digital Shield.**

### Future Scalability Line

> **One verification engine. Multiple accessible channels.**

### Main UX Line

> **The complexity stays behind the scenes. The user only sees the risk, the reason, and what to do next.**

---

# 9. What Not to Claim

Avoid saying:

- “100% accurate”
- “We can always detect AI-generated content”
- “Green means guaranteed safe”
- “Unverified means fake”

Prefer:

- “Looks safe based on available evidence”
- “High risk”
- “Could not verify”
- “Needs further verification”
- “Possible manipulation”
