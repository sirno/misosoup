"""Validate."""
import re
import yaml
import logging


def validate_solution(solution, exchange_format, exclude_strains=[]):
    """Validate solution."""
    valid = True
    active_strains = exclude_strains
    active_exchanges = []

    for var, rate in solution.items():
        if rate:
            if var.startswith("y_"):
                active_strains.append(var[2:])
            else:
                active_exchanges.append(var)

    matchers = [
        re.compile(exchange_format.format("\w+") + f"_{strain}_INT")
        for strain in active_strains
    ]

    for var in active_exchanges:
        if var.endswith("_INT") and not any(m.match(var) for m in matchers):
            logging.warning("Numerical inconsistency found for %s", var)
            valid = False

    return valid


def validate_solution_dict(solution_data, exchange_format):
    """Validate if a solution dictionary reports numerical inconsistency."""
    valid = True
    for cs, cs_sols in solution_data.items():
        for org, org_sols in cs_sols.items():
            for i, sol in enumerate(org_sols):
                if not validate_solution(sol, exchange_format, exclude_strains=[org]):
                    valid = False
                    print(
                        f"Inconsistency found: carbon source={cs}, organism={org}, solution={i}"
                    )
    return valid


def validate_solution_file(path, exchange_format="R_EX_{}_e"):
    """Validate if a solution file reports numerical inconsistency."""
    with open(path) as fd:
        solution_data = yaml.safe_load(fd)
    return validate_solution_dict(solution_data, exchange_format)