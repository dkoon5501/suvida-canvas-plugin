# suvida-canvas-plugin

Canvas Medical AI plugins for Suvida Healthcare — value-based primary care for Hispanic seniors.

## Plugins

### HEDIS Care Gap Flag (`plugins/hedis_care_gaps/`)

Displays a color-coded banner alert on a patient's chart when key HEDIS quality measures are overdue. Fires on patient check-in.

| Color | Meaning |
|-------|---------|
| 🔴 Red | Overdue — action needed today |
| 🟡 Yellow | Due within 60 days — schedule soon |
| ✅ Green | Current — no action needed |

**Measures tracked:** HbA1c (diabetes, annual), diabetic eye exam (annual), blood pressure (hypertension, every 6 months).

**Canvas SDK version:** 0.135.0 | **Trigger:** `APPOINTMENT_CHECKED_IN`

## Getting Started

See [GUIDE.md](GUIDE.md) for the full step-by-step setup guide (written for non-developers).

**Quick start for developers:**

```bash
# Install dependencies
pip install -r setup/requirements.txt

# Set up Canvas credentials
cp setup/credentials.ini.template ~/.canvas/credentials.ini
# Edit ~/.canvas/credentials.ini with your sandbox client_id and client_secret

# Verify your connection
python3 setup/verify_setup.py

# Run tests (no Canvas sandbox required)
python -m pytest tests/ -v
```

## Repository Structure

```
suvida-canvas-plugin/
├── GUIDE.md                        ← Non-developer setup guide
├── plugins/
│   └── hedis_care_gaps/
│       ├── plugin.py               ← Main handler
│       ├── hedis_rules.py          ← HEDIS threshold rules & value sets
│       ├── CANVAS_MANIFEST.json    ← Canvas SDK manifest
│       └── README.md               ← Plugin documentation
├── setup/
│   ├── requirements.txt            ← Python dependencies
│   ├── credentials.ini.template    ← OAuth credentials template
│   └── verify_setup.py             ← Connection verification script
├── tests/
│   └── test_hedis_care_gaps.py     ← Unit + integration tests
└── evaluation/
    └── suvida_memo_template.md     ← Leadership evaluation memo template
```

## Security Notes

- **Never commit** `~/.canvas/credentials.ini` — it contains your OAuth client secret
- The `credentials.ini.template` in this repo is safe to commit (contains only placeholder values)
- Plugin runs inside Canvas Medical's sandboxed environment; it does not store or transmit patient data externally
