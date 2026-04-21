"""
HEDIS threshold rules and clinical value sets for Suvida Healthcare.

Defines which ICD-10 codes indicate diabetes/hypertension and which LOINC
codes correspond to relevant lab results. Also defines how many days old a
result can be before it is considered overdue (per HEDIS measurement year rules).
"""

from datetime import date, timedelta

# ── ICD-10 Diagnosis Code Prefixes ──────────────────────────────────────────

# Type 1 diabetes (E10.x), Type 2 diabetes (E11.x), Other specified (E13.x)
DIABETES_ICD10_PREFIXES = ("E10", "E11", "E13")

# Essential hypertension
HYPERTENSION_ICD10_PREFIXES = ("I10",)

# ── LOINC Lab Codes ──────────────────────────────────────────────────────────

# HbA1c (glycated hemoglobin) — the standard diabetes control measure
A1C_LOINC_CODES = {"4548-4", "4549-2", "17856-6"}

# Blood pressure — systolic and diastolic (used to confirm BP was checked)
# Canvas typically stores BP as a panel with components; we look for the panel LOINC
BLOOD_PRESSURE_LOINC_CODES = {"55284-4", "8480-6", "8462-4"}

# Diabetic retinal eye exam CPT-equivalent LOINC (used in Observation resources)
# In practice, eye exams may appear as Referral/ServiceRequest — plugin checks both
EYE_EXAM_LOINC_CODES = {"32451-7"}

# ── HEDIS Measure Thresholds ─────────────────────────────────────────────────

# Number of days within which a measure result is considered current (not overdue)
THRESHOLDS = {
    "a1c": 365,         # HbA1c must be done at least once per year
    "eye_exam": 365,    # Diabetic eye exam must be done at least once per year
    "blood_pressure": 180,  # BP must be recorded at least once every 6 months
}

# Days before the threshold at which we show a "due soon" yellow warning
WARNING_DAYS_BEFORE = 60  # e.g., 10 months old for a 12-month threshold

# ── Status Constants ──────────────────────────────────────────────────────────

STATUS_CURRENT = "current"       # Within threshold — show green ✅
STATUS_DUE_SOON = "due_soon"     # Within warning window — show yellow 🟡
STATUS_OVERDUE = "overdue"       # Past threshold or never done — show red 🔴
STATUS_NOT_APPLICABLE = "n/a"    # Measure doesn't apply to this patient


def has_diabetes(condition_codes: list[str]) -> bool:
    """Return True if any active condition code indicates diabetes."""
    return any(
        code.upper().startswith(DIABETES_ICD10_PREFIXES)
        for code in condition_codes
    )


def has_hypertension(condition_codes: list[str]) -> bool:
    """Return True if any active condition code indicates hypertension."""
    return any(
        code.upper().startswith(HYPERTENSION_ICD10_PREFIXES)
        for code in condition_codes
    )


def check_overdue(last_result_date: date | None, measure_key: str) -> str:
    """
    Given the date of the most recent result and a measure name,
    return STATUS_CURRENT, STATUS_DUE_SOON, or STATUS_OVERDUE.

    measure_key must be one of: "a1c", "eye_exam", "blood_pressure"
    """
    if last_result_date is None:
        return STATUS_OVERDUE

    threshold_days = THRESHOLDS[measure_key]
    warning_days = threshold_days - WARNING_DAYS_BEFORE
    days_since = (date.today() - last_result_date).days

    if days_since <= warning_days:
        return STATUS_CURRENT
    elif days_since <= threshold_days:
        return STATUS_DUE_SOON
    else:
        return STATUS_OVERDUE


def format_banner_line(measure_label: str, status: str, last_date: date | None) -> str:
    """Format one line of the care gap banner for display in Canvas."""
    icons = {
        STATUS_CURRENT: "✅",
        STATUS_DUE_SOON: "🟡",
        STATUS_OVERDUE: "🔴",
        STATUS_NOT_APPLICABLE: "—",
    }
    icon = icons.get(status, "?")
    if last_date:
        date_str = last_date.strftime("%b %d, %Y")
        return f"{icon} {measure_label}: last {date_str}"
    else:
        return f"{icon} {measure_label}: no record found"
