"""
Unit tests for the HEDIS Care Gap Flag plugin.
Tests the rule logic in hedis_rules.py without requiring a live Canvas sandbox.

Run with: python -m pytest tests/test_hedis_care_gaps.py -v
"""

import sys
import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

# Make the plugin importable without a full canvas-sdk install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins", "hedis_care_gaps"))

import pytest

# ── Test the rules module directly (no Canvas SDK dependency) ─────────────────

from hedis_care_gaps.hedis_rules import (
    check_overdue,
    has_diabetes,
    has_hypertension,
    format_banner_line,
    STATUS_CURRENT,
    STATUS_DUE_SOON,
    STATUS_OVERDUE,
)


class TestHasCondition:
    def test_type2_diabetes_detected(self):
        assert has_diabetes(["E11.9"]) is True

    def test_type1_diabetes_detected(self):
        assert has_diabetes(["E10.65"]) is True

    def test_other_diabetes_detected(self):
        assert has_diabetes(["E13.40"]) is True

    def test_hypertension_not_diabetes(self):
        assert has_diabetes(["I10"]) is False

    def test_empty_conditions(self):
        assert has_diabetes([]) is False

    def test_multiple_codes_one_diabetes(self):
        assert has_diabetes(["Z23", "E11.9", "I10"]) is True

    def test_hypertension_detected(self):
        assert has_hypertension(["I10"]) is True

    def test_diabetes_not_hypertension(self):
        assert has_hypertension(["E11.9"]) is False

    def test_case_insensitive(self):
        assert has_diabetes(["e11.9"]) is True


class TestCheckOverdue:
    def test_no_result_is_overdue(self):
        assert check_overdue(None, "a1c") == STATUS_OVERDUE

    def test_result_yesterday_is_current(self):
        yesterday = date.today() - timedelta(days=1)
        assert check_overdue(yesterday, "a1c") == STATUS_CURRENT

    def test_result_11_months_ago_is_current(self):
        eleven_months = date.today() - timedelta(days=300)
        assert check_overdue(eleven_months, "a1c") == STATUS_CURRENT

    def test_result_10_months_ago_is_due_soon(self):
        # Threshold=365 days, warning window starts at 305 days (365-60)
        ten_months = date.today() - timedelta(days=310)
        assert check_overdue(ten_months, "a1c") == STATUS_DUE_SOON

    def test_result_13_months_ago_is_overdue(self):
        thirteen_months = date.today() - timedelta(days=396)
        assert check_overdue(thirteen_months, "a1c") == STATUS_OVERDUE

    def test_blood_pressure_7_months_overdue(self):
        seven_months = date.today() - timedelta(days=210)
        assert check_overdue(seven_months, "blood_pressure") == STATUS_OVERDUE

    def test_blood_pressure_4_months_current(self):
        four_months = date.today() - timedelta(days=120)
        assert check_overdue(four_months, "blood_pressure") == STATUS_CURRENT

    def test_blood_pressure_5_months_due_soon(self):
        # BP threshold=180 days, warning starts at 120 days (180-60)
        five_months = date.today() - timedelta(days=150)
        assert check_overdue(five_months, "blood_pressure") == STATUS_DUE_SOON


class TestFormatBannerLine:
    def test_overdue_no_date_shows_no_record(self):
        result = format_banner_line("HbA1c", STATUS_OVERDUE, None)
        assert "🔴" in result
        assert "no record found" in result

    def test_current_with_date_shows_date(self):
        last = date(2025, 3, 15)
        result = format_banner_line("HbA1c", STATUS_CURRENT, last)
        assert "✅" in result
        assert "Mar 15, 2025" in result

    def test_due_soon_shows_yellow(self):
        result = format_banner_line("Eye Exam", STATUS_DUE_SOON, date.today())
        assert "🟡" in result
        assert "Eye Exam" in result


class TestPluginIntegration:
    """
    Integration-level tests for plugin.py using mocked Canvas SDK objects.
    These tests verify the full compute() flow without a live Canvas instance.
    """

    def _make_mock_event(self, patient_id="test-patient-001"):
        event = MagicMock()
        event.target.id = patient_id
        return event

    def _make_mock_condition(self, icd10_code: str):
        cond = MagicMock()
        coding = MagicMock()
        coding.code = icd10_code
        cond.icd10_codings = [coding]
        return cond

    def _make_mock_observation(self, days_ago: int):
        obs = MagicMock()
        obs.effective_datetime = MagicMock()
        obs.effective_datetime.date.return_value = date.today() - timedelta(days=days_ago)
        return obs

    @patch("hedis_care_gaps.plugin.Condition")
    @patch("hedis_care_gaps.plugin.Observation")
    def test_no_relevant_conditions_returns_empty(self, mock_obs, mock_cond):
        """Patient with no diabetes or hypertension → no banner."""
        mock_cond.objects.for_patient.return_value.filter.return_value = []
        from hedis_care_gaps.plugin import HEDISCareGapHandler
        handler = HEDISCareGapHandler(event=self._make_mock_event())
        effects = handler.compute()
        assert effects == []

    @patch("hedis_care_gaps.plugin.Condition")
    @patch("hedis_care_gaps.plugin.Observation")
    def test_diabetic_patient_overdue_a1c_returns_banner(self, mock_obs, mock_cond):
        """Diabetic patient with no A1c in 14 months → banner with red HbA1c."""
        # Setup: patient has E11.9 (Type 2 diabetes)
        mock_cond.objects.for_patient.return_value.filter.return_value = [
            self._make_mock_condition("E11.9")
        ]
        # A1c: last result was 14 months ago (overdue)
        obs_qs = MagicMock()
        obs_qs.filter.return_value.order_by.return_value.first.return_value = (
            self._make_mock_observation(days_ago=425)
        )
        mock_obs.objects.for_patient.return_value = obs_qs

        from hedis_care_gaps.plugin import HEDISCareGapHandler
        handler = HEDISCareGapHandler(event=self._make_mock_event())
        effects = handler.compute()

        assert len(effects) == 1
        banner = effects[0]
        assert "HbA1c" in banner.narrative
        assert "🔴" in banner.narrative

    @patch("hedis_care_gaps.plugin.Condition")
    @patch("hedis_care_gaps.plugin.Observation")
    def test_all_measures_current_returns_empty(self, mock_obs, mock_cond):
        """Diabetic patient with all measures current → no banner."""
        mock_cond.objects.for_patient.return_value.filter.return_value = [
            self._make_mock_condition("E11.9")
        ]
        # All observations recent (within 6 months)
        obs_qs = MagicMock()
        obs_qs.filter.return_value.order_by.return_value.first.return_value = (
            self._make_mock_observation(days_ago=90)
        )
        mock_obs.objects.for_patient.return_value = obs_qs

        from hedis_care_gaps.plugin import HEDISCareGapHandler
        handler = HEDISCareGapHandler(event=self._make_mock_event())
        effects = handler.compute()
        assert effects == []
