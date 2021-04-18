"""Test validate."""
from misolib.validate import validate_solution

test_pattern = "R_EX_{}_e"


def test_reject_invalid_exchange():
    """Check if invalid exchange can is found."""
    assert not validate_solution(
        {
            "R_EX_meta_e_BBBB_INT": 2.3283064365386963e-10,
            "y_AAAA": 1,
        },
        test_pattern,
    )


def test_accept_valid_exchange():
    """Check if a valid exchange is accepted."""
    assert validate_solution(
        {
            "R_EX_meta_e_AAAA_INT": -10.0,
            "y_AAAA": 1,
        },
        test_pattern,
    )


def test_accept_other_reactions():
    """Check non exchange reactions are accepted."""
    assert validate_solution(
        {
            "R_any_reaction_name": 1000.0,
        },
        test_pattern,
    )


def test_ignore_inactive_reactions():
    """Check if inactive reactions have an effect on validity."""
    assert validate_solution(
        {
            "R_EX_meta_e_BBBB_INT": 0,
            "y_AAAA": 1,
        },
        test_pattern,
    )
