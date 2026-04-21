# Internal Evaluation Memo
## Canvas Medical AI Plugin — Suvida Healthcare

**Date:** [FILL IN DATE]
**Prepared by:** [YOUR NAME], Operations
**Audience:** Chief Medical Officer, VP of Clinical Operations, IT Leadership
**Subject:** Canvas Medical Developer Sandbox Evaluation — HEDIS Care Gap Flag Plugin Demo

---

## Executive Summary

Suvida Healthcare conducted a hands-on technical evaluation of Canvas Medical's EMR platform, specifically testing its developer plugin framework and AI extensibility. We built and demonstrated a functioning AI-powered plugin — the **HEDIS Care Gap Flag** — that automatically alerts clinicians when a patient's chart is opened and key quality measures are overdue.

**Bottom line:** Canvas Medical's plugin SDK is functional and well-documented for a developer audience. For Suvida's use case (value-based care, Hispanic seniors, HEDIS quality reporting), it offers promising capabilities but has access restrictions and maturity considerations that require further discussion with Canvas's enterprise team before a production commitment.

---

## What We Built

**Plugin Name:** HEDIS Care Gap Flag
**Function:** When a patient checks in or a chart is opened in Canvas, the plugin automatically:

1. Checks whether the patient has diabetes (Type 1 or Type 2) or hypertension
2. Looks up their most recent HbA1c lab result, blood pressure measurement, and diabetic eye exam referral
3. Compares those dates against HEDIS measurement year thresholds
4. Displays a real-time color-coded banner at the top of the chart:
   - 🔴 **Red** = Overdue (measure has lapsed — action recommended today)
   - 🟡 **Yellow** = Due soon (within 60 days of lapsing)
   - ✅ **Green** = Current (no action needed)

**Clinical population targeted:** Patients with Type 2 diabetes or hypertension — a high-priority segment of Suvida's roster for HEDIS performance.

**Build time:** Approximately [X] hours using Claude Code as the development assistant.

---

## Demo Results

| Scenario Tested | Result |
|-----------------|--------|
| Diabetic patient, no A1c in 14 months | 🔴 Red banner appeared on chart open |
| Hypertensive patient, BP checked 5 months ago | 🟡 Yellow banner (due soon) |
| Patient with all measures current | No banner (correct — no clutter) |
| Patient with no diabetes or hypertension | No banner (correct — not applicable) |

**Demo video/screenshot:** [ATTACH OR DESCRIBE]

---

## Canvas Medical Platform Assessment

### What Canvas Can Do (Relevant to Suvida)

| Capability | Available? | Notes |
|------------|------------|-------|
| Real-time chart event hooks (note open, check-in) | ✅ Yes | Works in developer sandbox |
| FHIR R4 data access (conditions, labs, medications) | ✅ Yes | Read access via OAuth2 |
| Custom banner/alert display in chart | ✅ Yes | `AddBannerAlert` effect |
| Bilingual (Spanish/English) content display | ✅ Yes | Text can be any language |
| Protocol cards (structured quality checklists) | ✅ Yes | `ProtocolCard` effect |
| Custom note templates | ✅ Yes | Command injection into notes |
| AI/LLM integration (Claude, GPT, etc.) | ✅ Yes | Plugins can call external APIs |
| HEDIS measure tracking | Partial | Plugin layer works; HEDIS data must come from Canvas's own records |
| Population health dashboard | ❓ Unknown | Not tested in sandbox; may require enterprise tier |
| Medication reconciliation workflows | ❓ Unknown | Available via SDK but not tested |
| HL7 v2 or direct EHR data import | ❓ Unknown | Not accessible in developer sandbox |

### Key Limitations Discovered

**1. FHIR API Access Restriction (Important)**
Canvas restricts full FHIR API access to paying customers and approved trusted partners. In the developer sandbox, FHIR access may be limited or require additional approval. This means:
- You cannot query Canvas FHIR data from external systems (e.g., Power Automate, n8n) without a Canvas contract.
- Plugins running *inside* Canvas can access FHIR — but external integrations cannot.

**Implication for Suvida:** If we want to pull Canvas patient data into our existing reporting tools (Airtable, Power BI, etc.), we would need a commercial contract and a data partnership agreement with Canvas.

**2. Developer Sandbox ≠ Production Canvas**
The developer sandbox has sample/fake patients only. We cannot test against real Suvida patient data until we have a production or pilot contract. Behavioral differences between sandbox and production may exist.

**3. Plugin Deployment Requires Technical Setup**
Plugin installation currently requires command-line tools and Python. Non-technical staff cannot deploy plugins without assistance. Canvas's roadmap may include a no-code plugin marketplace — status unknown.

**4. No Native Spanish-Language EMR Interface**
Canvas Medical's core interface is English-only. While our plugin *can* display bilingual content in banners and note templates, the underlying EMR navigation and documentation workflows are in English. This is a gap for Suvida's bilingual clinical staff and patients who prefer Spanish.

**5. Limited Community/Template Library**
Canvas is a smaller EMR vendor. The plugin ecosystem is early-stage compared to Epic or Athena. Fewer pre-built templates and integrations are available.

---

## How Canvas Compares to [CURRENT EMR NAME]

| Feature | Canvas Medical | [Current EMR] |
|---------|---------------|----------------|
| Custom plugin/AI development | ✅ Strong (Python SDK, FHIR) | [FILL IN] |
| HEDIS quality reporting built-in | [FILL IN] | [FILL IN] |
| Spanish-language interface | ❌ English only | [FILL IN] |
| Value-based care dashboards | ❓ Unknown | [FILL IN] |
| Ease of use for clinical staff | ❓ Not tested with staff | [FILL IN] |
| Cost (per provider/month) | [REQUEST FROM CANVAS] | [FILL IN] |
| HIPAA BAA available | ✅ Yes (required for production) | [FILL IN] |
| Patient portal | ✅ Yes | [FILL IN] |

---

## Recommended Next Steps

**Immediate (within 30 days):**
- [ ] Schedule a Canvas Medical enterprise demo focused on Suvida's specific population (Hispanic seniors, value-based care, HEDIS)
- [ ] Request a FHIR API data access overview — specifically ask: "Can we query Canvas FHIR from external tools under a commercial agreement?"
- [ ] Ask Canvas for their Spanish-language roadmap

**If Canvas is a finalist:**
- [ ] Request a 90-day pilot with 1–2 Suvida providers and a small real patient panel
- [ ] Test the HEDIS care gap plugin with real patient data to validate accuracy
- [ ] Run a usability study with Suvida clinical staff (at least 3 providers and 2 MAs)
- [ ] Get pricing proposal and compare TCO (total cost of ownership) vs. current EMR

**Questions for Canvas Medical Account Team:**
1. What is the FHIR API access model for commercial customers — can we pull data into external reporting tools?
2. Is there a Spanish-language UI roadmap? Timeline?
3. Do you have existing customers serving similar populations (Hispanic seniors, PACE programs, community health centers)?
4. What is the migration path from [CURRENT EMR]?
5. What HEDIS measure tracking and reporting is built into the core Canvas platform vs. requiring custom plugins?

---

## Conclusion

The Canvas Medical HEDIS Care Gap Flag plugin we built demonstrates that Canvas's platform is technically capable of supporting Suvida's AI ambitions. **Building a meaningful, working plugin took [X] hours** — significantly less than a traditional EHR customization project.

However, we are evaluating Canvas as an *EMR* first, not just as a plugin platform. The FHIR access restrictions, English-only interface, and limited track record with Suvida's specific population type require further due diligence before recommending a full migration.

**Recommendation:** Proceed to enterprise discovery conversations with Canvas while maintaining [CURRENT EMR] as the status quo. Set a 60-day decision checkpoint.

---

*Prepared using Claude Code (AI development assistant) and the Canvas Medical Developer Sandbox.*
*Plugin code is stored at: github.com/dkoon5501/suvida-canvas-plugin/plugins/hedis_care_gaps*
