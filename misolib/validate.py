"""Validate."""
import re
import logging


def validate_solution(solution, pattern):
    """Validate solution."""
    valid = True
    active_strains = []
    active_exchanges = []

    for var, rate in solution.items():
        if rate:
            if var.startswith("y_"):
                active_strains.append(var[2:])
            else:
                active_exchanges.append(var)

    matchers = [
        re.compile(pattern.format("\w+") + f"_{strain}_INT")
        for strain in active_strains
    ]
    print(matchers)
    for var in active_exchanges:
        if var.endswith("_INT") and not any(m.match(var) for m in matchers):
            logging.warning("Numerical inconsistency found for %s", var)
            valid = False

    return valid
