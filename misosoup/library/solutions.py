from collections.abc import Callable, Iterable
from collections import defaultdict
from typing import Any

SolutionsDict = dict[str, dict[str, list[dict[str, Any]]]]


def map_solutions(
    func: Callable[[dict[str, float]], Any],
    solutions: SolutionsDict,
) -> SolutionsDict:
    """Map function over solutions and return a new solutions dict."""
    return {
        carbon_source: {
            strain: [func(solution) for solution in strain_solutions]
            for strain, strain_solutions in carbon_source_solutions.items()
        }
        for carbon_source, carbon_source_solutions in solutions.items()
    }


def filter_solutions(
    func: Callable[[dict[str, float]], bool],
    solutions: SolutionsDict,
) -> SolutionsDict:
    """Filter solutions and return a new solutions dict."""
    new = defaultdict(lambda: defaultdict(list))
    for carbon_source, carbon_source_solutions in solutions.items():
        for strain, strain_solutions in carbon_source_solutions.items():
            for solution in strain_solutions:
                if func(solution):
                    new[carbon_source][strain].append(solution)
