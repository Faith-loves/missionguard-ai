import copy

import pytest

from services import ai_explainer


@pytest.fixture
def assessment():
    return {
        "mission": {"risk_score": 62, "mission_readiness": 38,
                    "risk_level": "HIGH", "recommendation": "DELAY"},
        "risk_factors": {"geomagnetic": 10, "solar_flare": 18, "cme": 27, "storm": 7},
        "space_weather": {
            "solar_activity": {"strongest_flare": "X1.0", "total_flares": 1},
            "cme_activity": {"earth_directed_cmes": 3, "fastest_speed_km_s": 1500},
            "geomagnetic_activity": {"latest_kp": 4, "storm_count": 2},
        },
    }


@pytest.mark.parametrize("claim", [
    "Kp contributes 18 points; solar flare contributes 10 points.",
    "Risk score is 20.", "Risk score is **20**.",
    "Readiness is 90%.", "Risk level is LOW.", "Recommendation is GO.",
    "The recorded Kp index is 4.", "The observed Kp index is 4.",
    "The measured Kp index is 4.", "A flare was detected.",
    "NASA recommends DELAY.", "NOAA has approved this mission.",
    "Proceed with the launch.", "Particle flux increases the risk.",
])
def test_unsupported_claims_rejected(assessment, claim):
    assert not ai_explainer.explanation_is_grounded(
        "This hypothetical scenario: " + claim, "simulation", assessment)


def test_valid_factors_accepted(assessment):
    assert ai_explainer.explanation_is_grounded(
        "This hypothetical scenario has a risk score of 62 and readiness of 38%. "
        "Risk level is HIGH. Recommendation is DELAY. "
        "Kp contributes 10 points; solar flare contributes 18 points; "
        "CME contributes 27 points; storm contributes 7 points.",
        "simulation", assessment)


def test_rejection_falls_back_without_mutating_decision(monkeypatch, assessment):
    before = copy.deepcopy(assessment)
    monkeypatch.setattr(ai_explainer, "watsonx_configured", lambda: True)
    monkeypatch.setattr(ai_explainer, "generate_granite_explanation",
                        lambda *args: "This hypothetical scenario has a risk score of 1.")
    result = ai_explainer.explain_assessment(assessment, "simulation")
    assert not result["ai_generated"]
    assert "62/100" in result["explanation"]
    assert "hypothetical" in result["explanation"]
    assert assessment == before


def test_empty_model_output_rejected(assessment):
    assert not ai_explainer.explanation_is_grounded("", "live", assessment)
