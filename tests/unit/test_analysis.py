"""Test analysis."""
import pandas as pd

from misolib.analysis import _find_cross_feed


def test_find_valid_crossfeed():
    """Check if crossfeed detection finds a crossfed compound."""
    assert "met" in _find_cross_feed(
        pd.Series(
            {
                "R_EX_met_e_AAAA_INT": 2,
                "R_EX_met_e_BBBB_INT": -2,
            }
        )
    )


def test_miss_consumed_metabolites():
    """Check if crossfeed detection does not report consumed compounds."""
    assert "met" not in _find_cross_feed(
        pd.Series(
            {
                "R_EX_met_e_AAAA_INT": -2,
                "R_EX_met_e_BBBB_INT": -2,
            }
        )
    )


def test_miss_produced_metabolites():
    """Check if crossfeed detection does not report produced compounds."""
    assert "met" not in _find_cross_feed(
        pd.Series(
            {
                "R_EX_met_e_AAAA_INT": 2,
                "R_EX_met_e_BBBB_INT": 2,
            }
        )
    )
