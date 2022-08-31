"""Minimizer module."""

import logging
import math
import os
import yaml

from reframed.solvers import GurobiSolver
from reframed.solvers.solver import VarType
from reframed.solvers.solution import Status

from ..reframed.layered_community import LayeredCommunity

BOUND_INF = 1000


class Minimizer:
    """Minimizer class."""

    def __init__(
        self,
        org_id: str,
        medium: dict,
        community: LayeredCommunity,
        values: list,
        community_size: int,
        objective: dict,
        parsimony: bool,
        minimal_growth: float,
        cache_file: str = None,
    ):
        """Initialize `Minimize`."""
        self.community = community
        self.medium = medium
        self.minimal_growth = minimal_growth
        self.values = values
        self.community_size = community_size
        self.objective = objective
        self.parsimony = parsimony

        self.solver = GurobiSolver(community.merged_model)

        self._setup_binary_variables()
        self._setup_medium()

        if not org_id or org_id == "min":
            self.solver.add_constraint(
                "c_community_growth",
                {community.merged_model.biomass_reaction: 1},
                ">",
                minimal_growth,
                update=True,
            )
        else:
            self.solver.add_constraint(
                f"c_{org_id}_focal",
                {f"y_{org_id}": 1},
                ">",
                1,
                update=True,
            )

        self._community_objective = {
            f"y_{org_id}": 1 for org_id in self.community.organisms.keys()
        }

        self.solutions = []
        self.community_constraints = {}
        self.knowledge_constraints = {}

        self.cache_file = cache_file
        if cache_file and os.path.exists(cache_file):
            with open(cache_file, encoding="utf8") as cache_fd:
                cache = yaml.load(cache_fd, Loader=yaml.CSafeLoader)
            self._load_constraints_from_cache(cache)

    def minimize(self):
        """Minimize community."""
        i = len(self.community_constraints)
        while True:
            if self.cache_file:
                self._dump_constraints_to_cache()

            logging.info("------------")
            logging.info("Starting optimization...")

            solution = self._minimize_community()

            if solution.status != Status.OPTIMAL:
                logging.info("Solution status: %s", str(solution.status))
                break

            selected = {
                k: 1
                for k in self._community_objective.keys()
                if solution.values[k] > 0.5
            }
            not_selected = {
                k: 1
                for k in self._community_objective.keys()
                if solution.values[k] < 0.5
            }

            logging.info("Community size: %i", len(selected))
            logging.info(
                "Community growth: %f",
                solution.values[self.community.merged_model.biomass_reaction],
            )

            # Fix selected community
            self.solver.add_constraint(
                "c_not_selection", not_selected, "=", 0, update=True
            )
            self.solver.add_constraint(
                "c_selection", selected, "=", len(selected), update=True
            )

            try:
                growth = 0
                if self.objective:
                    solution = self._objective_optimization()
                    if not self._check_solution(solution, selected, not_selected):
                        continue
                    growth = (
                        solution.values[self.community.merged_model.biomass_reaction]
                        - 1e-4
                    )

                if self.parsimony:
                    solution = self._parsimony_optimization(growth)
                    if not self._check_solution(solution, selected, not_selected):
                        continue

                if not (self.objective or self.parsimony):
                    solution = self._no_objective_optimization()
                    if not self._check_solution(solution, selected, not_selected):
                        continue

            finally:
                self.solver.remove_constraints(["c_not_selection", "c_selection"])

            self.solver.add_constraint(
                f"c_{i}", selected, "<", len(selected) - 1, update=True
            )
            self.community_constraints[f"c_{i}"] = selected

            if self.community_size and len(selected) > self.community_size:
                break

            self.solutions.append(
                {var: rate for var, rate in solution.values.items() if rate}
            )

            i += 1

        if self.cache_file:
            self._dump_constraints_to_cache()

        return self.solutions

    @property
    def _get_values(self):
        return list(self._community_objective.keys()) + self.values

    def _minimize_community(self):
        return self.solver.solve(
            linear=self._community_objective,
            get_values=self._get_values,
            minimize=True,
        )

    def _objective_optimization(self):
        logging.info("Starting growth optimization.")
        return self.solver.solve(
            linear=self.objective,
            get_values=self._get_values,
            minimize=False,
        )

    def _no_objective_optimization(self):
        logging.info("Starting no optimization.")
        return self.solver.solve(
            get_values=self._get_values,
        )

    def _parsimony_optimization(self, growth: float = 0):
        logging.info("Starting parsimony optimization.")
        if growth > 0:
            self.solver.add_constraint(
                "c_growth",
                self.objective,
                ">",
                growth,
                update=True,
            )

        solution = self.solver.solve(
            quadratic={
                (rid, rid): 1
                for rid in self.community.merged_model.reactions
                if not rid.startswith("Growth")
                and rid != self.community.merged_model.biomass_reaction
            },
            get_values=self._get_values,
            minimize=True,
        )

        self.solver.remove_constraints(["c_growth"])

        return solution

    def _check_solution(self, solution, selected, not_selected):
        logging.debug("Solution status: %s", str(solution.status))
        if solution.status != Status.OPTIMAL:
            logging.info("Community Inconsistent: %s", str(list(selected.keys())))
            self._add_knowledge_constraint(not_selected)
            return False
        logging.info(
            "Community growth: %f",
            solution.values[self.community.merged_model.biomass_reaction],
        )
        return True

    def _add_knowledge_constraint(self, not_selected: dict):
        constraint_name = f"c_tmp_{len(self.knowledge_constraints) + 1}"
        self.solver.add_constraint(constraint_name, not_selected, ">", 1)
        self.knowledge_constraints[constraint_name] = not_selected

    def _load_constraints_from_cache(self, cache: dict):
        for name, selected in cache["community_constraints"].items():
            self.solver.add_constraint(name, selected, "<", len(selected) - 1)
            self.community_constraints[name] = selected

        for name, not_selected in cache["knowledge_constraints"].items():
            self.solver.add_constraint(name, not_selected, ">", 1)
            self.knowledge_constraints[name] = not_selected

        self.solutions = cache["solutions"]

        self.solver.update()

    def _dump_constraints_to_cache(self):
        with open(self.cache_file, "w", encoding="utf8") as cache_fd:
            yaml.dump(
                {
                    "community_constraints": self.community_constraints,
                    "knowledge_constraints": self.knowledge_constraints,
                    "solutions": self.solutions,
                },
                cache_fd,
                Dumper=yaml.CSafeDumper,
            )

    def _setup_binary_variables(self):
        """Add binary variables to the solver instance."""
        for org_id in self.community.organisms.keys():
            self.solver.add_variable(
                f"y_{org_id}", 0, 1, vartype=VarType.BINARY, update=False
            )

        self.solver.update()

        for org_id, org_model in self.community.organisms.items():
            org_var = f"y_{org_id}"
            for r_id, reaction in org_model.reactions.items():
                if (
                    not r_id.startswith("R_EX")
                    and r_id != org_model.biomass_reaction
                    and reaction.lb * reaction.ub <= 0
                ):
                    continue

                merged_id = self.community.reaction_map[(org_id, r_id)]
                ubound = BOUND_INF
                lbound = -BOUND_INF

                if r_id == org_model.biomass_reaction:
                    lbound = self.minimal_growth

                if reaction.lb * reaction.ub > 0:
                    lbound = -BOUND_INF if math.isinf(reaction.lb) else reaction.lb
                    ubound = BOUND_INF if math.isinf(reaction.ub) else reaction.ub
                    self.solver.set_bounds({merged_id: (-BOUND_INF, BOUND_INF)})

                self.solver.add_constraint(
                    f"c_{merged_id}_lb",
                    {merged_id: 1, org_var: -lbound},
                    ">",
                    0,
                    update=False,
                )
                self.solver.add_constraint(
                    f"c_{merged_id}_ub",
                    {merged_id: 1, org_var: -ubound},
                    "<",
                    0,
                    update=False,
                )

    def _setup_medium(self):
        """Setup the medium for model on solver."""
        missing_reactions = set(self.medium.keys()) - set(
            self.community.merged_model.reactions.keys()
        )
        for r_id in missing_reactions:
            logging.warning(
                "Missing reaction %s in model %s", r_id, self.community.merged_model.id
            )
        for r_id in self.community.merged_model.reactions.keys():
            if r_id.startswith("R_EX_") and not r_id.endswith("_i"):
                bound = self.medium[r_id] if r_id in self.medium.keys() else 0
                self.solver.add_constraint(
                    f"c_{r_id}_lb",
                    {r_id: 1},
                    ">",
                    bound,
                )
