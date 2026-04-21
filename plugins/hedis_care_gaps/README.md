# HEDIS Care Gap Flag Plugin

**Organization:** Suvida Healthcare
**Purpose:** Surface overdue quality measure alerts at the point of care

---

## What This Plugin Does (Plain English)

When a patient checks into a Suvida clinic, this plugin automatically reviews their chart and checks three important quality measures that Suvida is scored on through HEDIS (a national quality reporting program for value-based care organizations).

**For patients with diabetes:**
- Has this patient had an HbA1c blood sugar test in the past 12 months?
- Have they had a diabetic eye exam in the past 12 months?

**For patients with high blood pressure:**
- Has this patient had a blood pressure measurement recorded in the past 6 months?

The plugin then shows a small banner at the top of the patient's chart:
- 🔴 **Red** = The measure is overdue — action needed today if possible
- 🟡 **Yellow** = Coming due within 60 days — good time to schedule
- ✅ **Green** = Current — no action needed

## Why This Matters for Suvida

HEDIS scores directly affect Suvida's quality bonuses and star ratings under value-based care contracts. Missing even a small percentage of diabetic eye exams or A1c tests can cost the organization money and, more importantly, means patients are not getting preventive care they need.

This plugin gives clinicians a real-time nudge at the exact moment they're already looking at the patient's chart — when it's easiest to order the missing test or referral.

---

## Technical Details

| Field | Value |
|-------|-------|
| SDK Version | canvas 0.135.0 |
| Trigger Event | `APPOINTMENT_CHECKED_IN` |
| FHIR Resources | Condition, Observation |
| ICD-10 Codes | E10.x, E11.x (diabetes); I10 (hypertension) |
| LOINC Codes | 4548-4 (HbA1c); 55284-4 (BP); 32451-7 (eye exam) |
| Effect Type | AddBannerAlert |

---

## Files in This Plugin

| File | Purpose |
|------|---------|
| `plugin.py` | Main handler — runs when patient checks in, fetches data, builds banner |
| `hedis_rules.py` | Threshold rules — what counts as "overdue" for each measure |
| `CANVAS_MANIFEST.json` | Plugin registration file required by Canvas SDK |
| `__init__.py` | Python package marker (empty) |

---

## Extending This Plugin

To add a new HEDIS measure (e.g., colorectal cancer screening for patients 45–75):

1. Add the relevant ICD-10 or age condition to `hedis_rules.py`
2. Add the LOINC code(s) for the screening test to `hedis_rules.py`
3. Add a new threshold entry to the `THRESHOLDS` dict in `hedis_rules.py`
4. Add a new `check_overdue()` call in `plugin.py`'s `compute()` method

Then tell Claude: "Add colorectal cancer screening to the HEDIS banner for patients ages 45–75" — Claude will make these edits for you.
