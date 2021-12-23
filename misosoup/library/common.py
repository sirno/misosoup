"""Common functions."""
import re
import yaml


def get_metabolite_name(compound):
    """Get metabolite id from compound name."""
    return f"M_{compound}_c"


def get_reaction_name(compound):
    """Get reaction id from compound name."""
    return f"EX_{compound}_e"


def get_compound_name(exchange_reaction):
    """Get compound name from reaction id."""
    return re.search(
        "((?<=R_EX_).*(?=_e))|((?<=EX_).*(?=_e))", exchange_reaction
    ).group(0)


def merge_dicts(a, b, path=None):
    """Merge b into a."""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def merge_yaml(file_list):
    """Merge yaml files."""
    solutions = {}
    for path in file_list:
        with open(path, "r") as file_descriptor:
            merge_dicts(solutions, yaml.safe_load(file_descriptor))
    return solutions
