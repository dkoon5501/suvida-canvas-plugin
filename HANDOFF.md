# Suvida Canvas Plugin — Session Handoff

## What Was Built

**Canvas Medical HEDIS Care Gap Flag plugin** — fully migrated from `glow-skincare-app` into its own dedicated repo.

When a patient checks in, the plugin reads their active conditions and recent labs via FHIR and shows a color-coded banner in Canvas:
- 🔴 Red = overdue (HbA1c > 12 mo, eye exam > 12 mo, BP > 6 mo)
- 🟡 Yellow = due within 60 days
- ✅ Green = current / no action needed

---

## Repo

**GitHub:** `github.com/dkoon5501/suvida-canvas-plugin`
**Active branch:** `claude/migrate-canvas-plugin-sa5IN`

```
suvida-canvas-plugin/
├── .devcontainer/devcontainer.json   ← Codespace config (Python 3.11, auto-installs deps)
├── GUIDE.md                          ← Non-developer step-by-step guide (Phases 1–5)
├── README.md                         ← Repo overview + developer quickstart
├── plugins/hedis_care_gaps/
│   ├── plugin.py                     ← Main handler (fires on APPOINTMENT_CHECKED_IN)
│   ├── hedis_rules.py                ← ICD-10/LOINC value sets, HEDIS thresholds
│   ├── CANVAS_MANIFEST.json          ← Canvas SDK manifest (sdk_version 0.135.0)
│   └── README.md
├── setup/
│   ├── requirements.txt              ← canvas==0.135.0, requests, configparser
│   ├── credentials.ini.template      ← Copy to ~/.canvas/credentials.ini
│   └── verify_setup.py               ← OAuth + FHIR connection checker
├── tests/
│   └── test_hedis_care_gaps.py       ← 17 unit + integration tests (no sandbox needed)
└── evaluation/
    └── suvida_memo_template.md       ← CMO/leadership memo template
```

---

## Codespace Status

- Codespace created and building ✓
- Python 3.11, `canvas==0.135.0`, `pytest` auto-installed on container create
- `PYTHONPATH` set to `plugins/` so imports resolve correctly
- VS Code test discovery pointed at `tests/`

**First thing to run in the Codespace terminal:**
```bash
python -m pytest tests/ -v
```
All 17 tests should pass with no Canvas sandbox needed.

---

## Where Things Were Left

Everything is working locally. The plugin has **not yet been deployed** to a Canvas sandbox — that's the next step.

---

## Next Steps (in order)

### 1 — Get Canvas Sandbox Credentials (Phase 1 of GUIDE.md)
- Sign up at `canvasmedical.com` → Developer Sandbox (if not done)
- Canvas sandbox → Settings → OAuth Applications → Create App
  - Grant Type: `Client Credentials`
  - Client Type: `Confidential`
- Copy: `client_id`, `client_secret`, `instance_name` (subdomain of your sandbox URL)

### 2 — Set Up Credentials in the Codespace
```bash
cp setup/credentials.ini.template ~/.canvas/credentials.ini
# Edit the file — replace YOUR-SANDBOX-NAME, client_id, client_secret
nano ~/.canvas/credentials.ini
```

### 3 — Verify the Connection
```bash
python3 setup/verify_setup.py
```
Should print `✓ All checks passed!`

### 4 — Deploy the Plugin
```bash
canvas install --instance YOUR-SANDBOX-NAME plugins/hedis_care_gaps
```

### 5 — Test in Canvas UI
- Open your sandbox in a browser
- Find a test patient with an E11.x (diabetes) or I10 (hypertension) diagnosis
- Open their chart → the HEDIS banner should appear

### 6 — Fill in the Evaluation Memo
- Open `evaluation/suvida_memo_template.md`
- Fill in demo results, build time, and comparison columns
- Share with CMO / ops leadership

---

## Key Technical Details

| Item | Value |
|------|-------|
| Canvas SDK version | `canvas==0.135.0` |
| Trigger event | `APPOINTMENT_CHECKED_IN` |
| FHIR resources | `Condition`, `Observation` |
| ICD-10 (diabetes) | E10.x, E11.x, E13.x |
| ICD-10 (hypertension) | I10 |
| LOINC (HbA1c) | 4548-4, 4549-2, 17856-6 |
| LOINC (BP) | 55284-4, 8480-6, 8462-4 |
| LOINC (eye exam) | 32451-7 |
| Banner effect | `AddBannerAlert` |

---

## What to Tell the Next Claude Session

> "I'm continuing work on the Suvida Canvas Medical plugin. The repo is `github.com/dkoon5501/suvida-canvas-plugin`, branch `claude/migrate-canvas-plugin-sa5IN`. The plugin code is complete and tests pass. I need help deploying it to my Canvas sandbox — I have my `client_id`, `client_secret`, and `instance_name` ready."
