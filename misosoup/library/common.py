"""Common functions."""
import re
import yaml

from typing import List
from collections.abc import Iterable


def get_metabolite_name(compound: str) -> str:
    """Get metabolite id from compound name."""
    return f"M_{compound}_c"


def get_reaction_name(compound: str) -> str:
    """Get reaction id from compound name."""
    return f"EX_{compound}_e"


def get_compound_name(exchange_reaction: str) -> str:
    """Get compound name from reaction id."""
    return re.search(
        "((?<=R_EX_).*(?=_e))|((?<=EX_).*(?=_e))", exchange_reaction
    ).group(0)


def merge_dicts(a: dict, b: dict, path=None):
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


def merge_yaml(file_list: List[str]):
    """Merge yaml files."""
    solutions = {}
    for path in file_list:
        with open(path, "r") as file_descriptor:
            merge_dicts(
                solutions, yaml.safe_load(file_descriptor, Loader=yaml.CSafeLoader)
            )
    return solutions


def is_exchange(variable: str) -> bool:
    """Check if variable is an exchange reaction."""
    return variable.startswith("R_EX")


def is_internal_exchange(variable: str) -> bool:
    """Check if variable is an internal exchange reaction."""
    return variable.startswith("R_EX") and variable.endswith("_i")


def is_growth(variable: str) -> bool:
    """Check if variable is a growth reaction."""
    return variable.startswith("Growth")


def is_local(variable: str, member: str) -> bool:
    """Check if variable is a local reaction of the member."""
    return member in variable


def is_in_member(variable: str, members: Iterable) -> bool:
    """Check if variable is a local reaction of any of the members"""
    return any(map(is_local, members))
