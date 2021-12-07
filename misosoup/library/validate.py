"""Validate."""
import re
import logging
import yaml


def validate_solution(solution, exchange_format, exclude_strains=None):
    """Validate solution."""
    valid = True
    if exclude_strains is None:
        exclude_strains = []
    active_strains = []
    active_exchanges = []

    for var, rate in solution.items():
        if rate:
            if var.startswith("y_"):
                active_strains.append(var[2:])
            else:
                active_exchanges.append(var)

    matchers = [
        re.compile(exchange_format.format(r"\w+") + f"_{strain}_i")
        for strain in active_strains
        if strain not in exclude_strains
    ]

    for var in active_exchanges:
        if var.endswith("_i") and not any(m.match(var) for m in matchers):
            logging.warning("Numerical inconsistency found for %s", var)
            valid = False

    return valid


def validate_solution_dict(solution_data, exchange_format):
    """Validate if a solution dictionary reports numerical inconsistency."""
    valid = True
    for carbon_source, carbon_source_solutions in solution_data.items():
        for _, org_sols in carbon_source_solutions.items():
            for _, sol in enumerate(org_sols):
                if not validate_solution(sol, exchange_format):
                    valid = False
                    print(
                        f"Inconsistency found: carbon source={carbon_source}, "
                        "organism={org}, solution={i}"
                    )
    return valid


def validate_solution_file(path, exchange_format="R_EX_{}_e"):
    """Validate if a solution file reports numerical inconsistency."""
    with open(path, encoding="utf8") as file_descriptor:
        solution_data = yaml.safe_load(file_descriptor)
    return validate_solution_dict(solution_data, exchange_format)
