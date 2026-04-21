# Suvida Healthcare — Canvas Medical AI Plugin Guide
## HEDIS Care Gap Flag: Step-by-Step Build Guide

> **Who this is for:** Healthcare operations professionals with no command-line experience.
> **How to use this guide:** Work through each checkbox in order. When a step says "Tell Claude," type that exact message in this chat. When a step says "Open in Safari/browser," do that on your iPhone.

---

## Glossary of Terms (defined once here, used throughout)

| Term | Plain-English Definition |
|------|--------------------------|
| **Plugin** | A small add-on that runs inside Canvas Medical and reacts to what a clinician is doing — like a sticky note that appears automatically when a chart is opened. |
| **Sandbox** | A safe practice version of Canvas Medical with no real patients. Perfect for building and testing without risk. |
| **OAuth** | A secure handshake that lets our plugin log into Canvas without storing a username and password in plain text. |
| **Client ID / Client Secret** | The username and password equivalent for OAuth — two codes Canvas gives you when you register your plugin. Keep these private. |
| **FHIR** | (pronounced "fire") The standard file format Canvas uses to store patient data — conditions, medications, lab results, etc. Think of it as the universal language EMRs speak. |
| **FHIR Resource** | One record in the FHIR format. Examples: a `Patient` resource (demographics), an `Observation` resource (lab result), a `Condition` resource (diagnosis). |
| **HEDIS** | A set of quality measures that value-based care organizations like Suvida are scored on. Example: "What % of our diabetic patients had an HbA1c test this year?" |
| **HbA1c** | A blood test that measures average blood sugar over 3 months — the key diabetes management measure. HEDIS requires it annually. |
| **Canvas SDK** | A set of Python tools (SDK = Software Development Kit) that lets developers write plugins for Canvas Medical. Claude Code uses it on your behalf. |
| **Python** | A programming language. The Canvas SDK is written in Python. Claude Code runs Python commands on the server — you don't need to type them yourself. |
| **Terminal / Command Line** | A text-based interface for computers. You do NOT need to use this — Claude Code handles all terminal commands for you. |
| **CPA** | Canvas Plugin Assistant — a Claude Code tool that helps scaffold (create the skeleton of) Canvas plugins. |

---

## Progress Tracker

Use this to track where you are across sessions:

- [ ] **Phase 1** — Account & Environment Setup
- [ ] **Phase 2** — Understand What Was Built for You
- [ ] **Phase 3** — Connect to Your Canvas Sandbox
- [ ] **Phase 4** — Deploy & Test the Plugin
- [ ] **Phase 5** — Iterate & Harden
- [ ] **Phase 6** — Evaluate for Suvida Leadership

---

# PHASE 1 — Account & Environment Setup

**Goal:** Get a Canvas Medical developer sandbox account so you have a practice environment with fake patients.

**Why:** Canvas restricts FHIR API access to paying customers and trusted development partners. The Developer Sandbox gives you a free practice instance where you can build and test plugins safely, with no risk to real patient data.

---

### Step 1.1 — Sign Up for the Canvas Developer Sandbox

- [ ] **Open Safari (or Chrome) on your iPhone.**
- [ ] **Go to:** `canvasmedical.com`
- [ ] **Look for "Developer" or "Sandbox" in the navigation menu.** It may be under "Developers" or "Try Canvas."
- [ ] **Click "Request a Developer Sandbox"** (or similar — the button text may vary).
- [ ] **Fill in the form** with your name, email, and organization (Suvida Healthcare).
- [ ] **Submit the form.**
- [ ] **Check your email** — Canvas will send a confirmation and sandbox access link, typically within 1 business day.

> **What success looks like:** You receive an email from Canvas Medical with a link to your sandbox instance. The URL will look something like `https://your-instance.canvasmedical.com`.

> **If you hit a snag:** The Developer Sandbox signup page URL may change. If you can't find it, tell Claude: "I can't find the Canvas Developer Sandbox signup page — can you help me locate it?" and paste any error text you see.

---

### Step 1.2 — Log Into Your Sandbox

- [ ] **Click the link in your Canvas welcome email.**
- [ ] **Set your password** when prompted.
- [ ] **Log in** and confirm you see the Canvas Medical interface with sample/test patients.

> **What success looks like:** You see the Canvas Medical EMR interface with a list of sample patients (names like "Test Patient" or fictional names). There are no real patients in this sandbox.

---

### Step 1.3 — Create OAuth Application Credentials

> **Why:** Our plugin needs to securely identify itself to Canvas to fetch patient data. OAuth credentials are like a badge — Canvas won't share data without them.

- [ ] **While logged into your Canvas sandbox**, look for a **Settings** or **Admin** area (usually a gear icon ⚙️ or your name/avatar in the top corner).
- [ ] **Find "API" or "OAuth Applications"** in the settings menu.
- [ ] **Click "Create Application"** (or "New OAuth App").
- [ ] **Fill in the form:**
  - **Name:** `Suvida HEDIS Plugin` (or any name you'll recognize)
  - **Grant Type:** Select `Client Credentials` (this is the machine-to-machine option — no user login needed)
  - **Client Type:** Select `Confidential`
  - **Redirect URI:** Leave blank or enter `http://localhost` (not needed for client credentials)
- [ ] **Save / Create** the application.
- [ ] **Copy the following values** that Canvas displays (save them somewhere safe — you'll paste them here shortly):
  - `client_id` — looks like a long string of letters and numbers
  - `client_secret` — looks similar; treat this like a password, don't share it

- [ ] **Also note your instance name** — this is the part of your sandbox URL before `.canvasmedical.com`. For example, if your URL is `https://suvida-dev.canvasmedical.com`, your instance name is `suvida-dev`.

> **What success looks like:** You have three values written down or copied: `client_id`, `client_secret`, and `instance_name`.

---

### Step 1.4 — Share Credentials with Claude (Securely)

- [ ] **Tell Claude exactly this** (replace the placeholders with your real values):

```
My Canvas credentials are:
client_id: [paste your client_id here]
client_secret: [paste your client_secret here]
instance_name: [paste your instance name here]
```

> **Note on security:** These credentials only work on your sandbox (no real patients). Claude Code will store them in a local file called `~/.canvas/credentials.ini` on this server — not in the chat history.

Claude will then:
- Save your credentials to `~/.canvas/credentials.ini`
- Run the verification script to confirm everything connects properly
- Show you a green ✓ confirmation or explain any errors

> **What success looks like:** Claude reports "✓ Connected to [your-instance] successfully. Found X patients in your sandbox."

---

### Phase 1 Complete ✓

When the verification passes, check the Phase 1 box at the top and move to Phase 2.

---

# PHASE 2 — What Was Already Built for You

**Goal:** Understand the structure of the HEDIS Care Gap Flag plugin before you deploy it.

**Why:** You don't need to write code, but understanding what the plugin does helps you describe it confidently to Suvida's CMO and clinical staff.

---

### What the HEDIS Care Gap Flag Plugin Does

When a clinician opens a patient's chart in Canvas Medical, this plugin automatically:

1. **Checks if the patient has diabetes** (looks for diagnosis codes starting with E11 in their record)
2. **Queries their last lab results** for:
   - HbA1c (blood sugar control test) — HEDIS requires this annually for diabetic patients
   - Blood pressure reading — HEDIS requires this every 6 months
3. **Checks for diabetic eye exam referrals** — HEDIS requires this annually for diabetic patients
4. **Displays a color-coded banner** at the top of the chart:
   - 🔴 **Red** = Overdue (more than 12 months since last result, or never done)
   - 🟡 **Yellow** = Due soon (result is 10–12 months old)
   - ✅ **Green** = Current (result is within the required timeframe)

### File Structure

```
suvida-canvas-plugin/
├── GUIDE.md                     ← This file (your coaching guide)
├── setup/
│   ├── requirements.txt         ← List of software the plugin needs
│   ├── credentials.ini.template ← Template for your Canvas login credentials
│   └── verify_setup.py          ← Script that tests your connection to Canvas
├── plugins/
│   └── hedis_care_gaps/
│       ├── plugin.py            ← The main plugin brain (what runs when a chart opens)
│       ├── hedis_rules.py       ← The rules: what counts as "overdue" for each measure
│       ├── CANVAS_MANIFEST.json ← Plugin registration file required by Canvas SDK
│       └── README.md            ← Plugin description
├── tests/
│   └── test_hedis_care_gaps.py  ← Automated checks that the plugin behaves correctly
└── evaluation/
    └── suvida_memo_template.md  ← Pre-filled memo for your CMO and ops leadership
```

### Phase 2 Complete ✓

Move to Phase 3 when you're ready to connect to your sandbox.

---

# PHASE 3 — Connect & Deploy the Plugin

**Goal:** Connect the plugin code to your Canvas sandbox and install it.

**Prerequisite:** Phase 1 must be complete (credentials verified).

---

### Step 3.1 — Deploy the Plugin

- [ ] **Tell Claude:** `"Deploy the HEDIS care gap plugin to my Canvas sandbox."`

Claude will:
- Package the plugin using the Canvas SDK
- Upload it to your sandbox instance
- Confirm the deployment succeeded

> **What success looks like:** Claude reports "Plugin deployed successfully. Plugin ID: [id]. Status: Active."

---

### Step 3.2 — Add a Test Patient (if needed)

Your Canvas sandbox comes with sample patients. If you need a patient with a diabetes diagnosis for testing:

- [ ] **Tell Claude:** `"Create a test patient in my Canvas sandbox with a Type 2 diabetes diagnosis (E11.9) and no HbA1c result in the past 14 months."`

Claude will create a test FHIR Patient and Condition record via the Canvas API.

> **What success looks like:** Claude reports the test patient's name and ID.

---

### Step 3.3 — Test the Plugin in the Canvas Interface

- [ ] **On your iPhone, open your Canvas sandbox** (`https://[your-instance].canvasmedical.com`).
- [ ] **Find the test patient** in the patient list (search by the name Claude gave you).
- [ ] **Open the patient's chart.**
- [ ] **Look for the HEDIS care gap banner** at the top of the chart — it should appear within a few seconds.

> **What success looks like:** You see a banner with colored indicators for HbA1c, blood pressure, and eye exam — at least one should be red (overdue) for the test patient.

> **If the banner doesn't appear:** Tell Claude: "The HEDIS banner didn't show up when I opened the test patient's chart. Here's what I see: [describe what you see or paste any error]."

### Phase 3 Complete ✓

---

# PHASE 4 — Iterate with AI (Plain-English Changes)

**Goal:** Learn how to modify the plugin by describing changes in plain English — no coding required.

**Why:** The power of working with Claude Code is that you can iterate on functionality just by describing what you want, as if talking to a developer.

---

### Example Iteration Requests

You can tell Claude any of the following (or make up your own):

**Add a new measure:**
> "Add a cholesterol check (LDL-C) to the HEDIS banner for patients over 65. Flag it red if no result in the past 12 months."

**Change the display:**
> "Make the banner show the actual date of the last HbA1c result, not just 'overdue.' Show it in Spanish as well as English."

**Add a new patient type:**
> "Right now the plugin only flags care gaps for diabetic patients. Can you also flag annual wellness visits for patients over 65 who haven't had one in 12 months?"

**Adjust a threshold:**
> "Change the 'yellow warning' threshold for blood pressure from 5-6 months to 4-5 months."

---

### Hardening the Plugin Before Your Demo

Before presenting to Suvida leadership, run these three reviews by telling Claude:

- [ ] **Tell Claude:** `"Run /cpa:coverage on the HEDIS plugin"` — checks that all code paths are tested
- [ ] **Tell Claude:** `"Run /cpa:security-review on the HEDIS plugin"` — checks for any security issues (e.g., credentials exposed, data leakage)
- [ ] **Tell Claude:** `"Run /cpa:database-performance-review on the HEDIS plugin"` — checks that FHIR queries are efficient

For each review, Claude will report findings and offer to fix any issues it finds.

### Phase 4 Complete ✓

---

# PHASE 5 — Evaluate for Suvida Leadership

**Goal:** Prepare a 1-page memo summarizing what you built and whether Canvas Medical is a fit for Suvida.

- [ ] **Open the memo template:** `evaluation/suvida_memo_template.md`
- [ ] **Tell Claude:** `"Fill in the evaluation memo based on what we built and tested."`

Claude will complete the memo with:
- What the plugin does and its demo results
- Canvas SDK capabilities and limitations
- FHIR API access restrictions (important for Suvida to know)
- Recommended next steps for the CMO and ops leadership

- [ ] **Review the memo** and ask Claude to adjust any section.
- [ ] **Export or copy the memo text** to share with your team.

### Phase 5 Complete ✓

---

# Troubleshooting Reference

| Error Message | What It Means | What to Do |
|---------------|---------------|------------|
| `401 Unauthorized` | Your credentials are wrong or expired | Re-check your client_id and client_secret from Canvas settings |
| `404 Not Found` | The patient or resource doesn't exist in your sandbox | Tell Claude the error — it will create a test patient |
| `Connection refused` | The Canvas sandbox URL is wrong | Confirm your instance name from the Canvas welcome email |
| `Plugin not found` | Plugin wasn't deployed | Tell Claude: "Re-deploy the HEDIS plugin" |
| `No FHIR resources returned` | Patient has no matching records | Normal for a fresh test patient — Claude can add test data |
| Any other error | Paste the full error text to Claude | Claude will diagnose it in plain English |

---

# Quick Reference: What to Say to Claude

| What You Want | Tell Claude |
|---------------|-------------|
| Connect to sandbox | "My Canvas credentials are: client_id: X, client_secret: Y, instance_name: Z" |
| Deploy plugin | "Deploy the HEDIS care gap plugin to my Canvas sandbox" |
| Create test patient | "Create a test patient with Type 2 diabetes and overdue HbA1c" |
| Make a change | Describe it in plain English — Claude will figure out the code |
| Run security review | "Run /cpa:security-review on the HEDIS plugin" |
| Write the eval memo | "Fill in the evaluation memo based on what we built" |
| Fix an error | Paste the error text directly into the chat |

---

*Guide version 1.0 — Built with Claude Code for Suvida Healthcare*
*Plugin: HEDIS Care Gap Flag | Repo: github.com/dkoon5501/suvida-canvas-plugin*
