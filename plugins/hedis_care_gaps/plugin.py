"""
HEDIS Care Gap Flag — Canvas Medical Plugin
Suvida Healthcare | Value-Based Primary Care

When a patient checks in or a chart is opened, this handler:
  1. Checks whether the patient has diabetes or hypertension
  2. Queries their most recent lab results and referrals
  3. Applies HEDIS thresholds (from hedis_rules.py)
  4. Displays a color-coded banner on the chart

Color codes:
  🔴 Red    = Overdue (past the HEDIS measurement window)
  🟡 Yellow = Due soon (within 60 days of becoming overdue)
  ✅ Green  = Current (result is within the required timeframe)

FHIR resources used:
  - Patient    (demographics, for chart personalization)
  - Condition  (active diagnoses — we look for diabetes / hypertension ICD-10 codes)
  - Observation (lab results — HbA1c, blood pressure via LOINC codes)
"""

from __future__ import annotations

from datetime import date

from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.effects import Effect
from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.observation import Observation

from hedis_care_gaps.hedis_rules import (
    A1C_LOINC_CODES,
    BLOOD_PRESSURE_LOINC_CODES,
    STATUS_NOT_APPLICABLE,
    check_overdue,
    format_banner_line,
    has_diabetes,
    has_hypertension,
)


class HEDISCareGapHandler(BaseHandler):
    """
    Fires on patient check-in and chart open events.
    Returns AddBannerAlert effects for any open HEDIS gaps.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.APPOINTMENT_CHECKED_IN),
    ]

    def compute(self) -> list[Effect]:
        patient_id = self.event.target.id
        if not patient_id:
            return []

        # ── 1. Fetch active condition codes ──────────────────────────────────
        active_conditions = Condition.objects.for_patient(patient_id).filter(
            clinical_status="active"
        )
        condition_codes = [
            coding.code
            for cond in active_conditions
            for coding in getattr(cond, "icd10_codings", [])
        ]

        patient_has_diabetes = has_diabetes(condition_codes)
        patient_has_hypertension = has_hypertension(condition_codes)

        # If patient has neither diabetes nor hypertension, no HEDIS gaps apply
        if not patient_has_diabetes and not patient_has_hypertension:
            return []

        # ── 2. Check HbA1c (diabetes patients only) ───────────────────────────
        a1c_status = STATUS_NOT_APPLICABLE
        a1c_last_date = None
        if patient_has_diabetes:
            a1c_obs = (
                Observation.objects.for_patient(patient_id)
                .filter(code__in=list(A1C_LOINC_CODES))
                .order_by("-effective_datetime")
                .first()
            )
            if a1c_obs and a1c_obs.effective_datetime:
                a1c_last_date = a1c_obs.effective_datetime.date()
            a1c_status = check_overdue(a1c_last_date, "a1c")

        # ── 3. Check blood pressure (hypertension patients) ───────────────────
        bp_status = STATUS_NOT_APPLICABLE
        bp_last_date = None
        if patient_has_hypertension:
            bp_obs = (
                Observation.objects.for_patient(patient_id)
                .filter(code__in=list(BLOOD_PRESSURE_LOINC_CODES))
                .order_by("-effective_datetime")
                .first()
            )
            if bp_obs and bp_obs.effective_datetime:
                bp_last_date = bp_obs.effective_datetime.date()
            bp_status = check_overdue(bp_last_date, "blood_pressure")

        # ── 4. Check diabetic eye exam (diabetes patients only) ───────────────
        # Eye exams may appear as Observations or ServiceRequests.
        # We check Observations first; missing referral data is treated as overdue.
        eye_status = STATUS_NOT_APPLICABLE
        eye_last_date = None
        if patient_has_diabetes:
            # LOINC 32451-7 = "Ophthalmologic examination and evaluation"
            eye_obs = (
                Observation.objects.for_patient(patient_id)
                .filter(code="32451-7")
                .order_by("-effective_datetime")
                .first()
            )
            if eye_obs and eye_obs.effective_datetime:
                eye_last_date = eye_obs.effective_datetime.date()
            eye_status = check_overdue(eye_last_date, "eye_exam")

        # ── 5. Build the banner ───────────────────────────────────────────────
        lines = []
        if a1c_status != STATUS_NOT_APPLICABLE:
            lines.append(format_banner_line("HbA1c", a1c_status, a1c_last_date))
        if eye_status != STATUS_NOT_APPLICABLE:
            lines.append(format_banner_line("Eye Exam", eye_status, eye_last_date))
        if bp_status != STATUS_NOT_APPLICABLE:
            lines.append(format_banner_line("Blood Pressure", bp_status, bp_last_date))

        # Only show the banner if at least one measure is overdue or due soon
        any_gap = any(
            s in ("overdue", "due_soon")
            for s in [a1c_status, eye_status, bp_status]
            if s != STATUS_NOT_APPLICABLE
        )
        if not any_gap:
            return []

        banner_text = " | ".join(lines)
        # Canvas banners have a ~200-char limit on narrative
        if len(banner_text) > 195:
            banner_text = banner_text[:192] + "..."

        effects = [
            AddBannerAlert(
                patient_id=str(patient_id),
                key="suvida_hedis_care_gaps",
                narrative=banner_text,
                placement=[AddBannerAlert.Placement.CHART],
                intent=AddBannerAlert.Intent.WARNING,
            )
        ]
        return effects
