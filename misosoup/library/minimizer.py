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

        self._setup_binary_variables()
        self.community.setup_medium(self.medium)

        if not org_id or org_id == "min":
            self.community.solver.add_constraint(
                "c_community_growth",
                {community.merged_model.biomass_reaction: 1},
                ">",
                minimal_growth,
                update=True,
            )
        else:
            self.community.solver.add_constraint(
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

            # get community members
            selected_names = [
                k[2:]
                for k in self._community_objective.keys()
                if solution.values[k] > 0.5
            ]
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

            # build community model
            selected_models = [
                model
                for org_id, model in self.community.organisms.items()
                if org_id in selected_names
            ]
            community = LayeredCommunity(f"{selected_names}", selected_models)

            community.setup_growth_requirement(self.minimal_growth)
            community.setup_medium(self.medium)

            if self.parsimony:
                community.setup_parsimony()

            objective_value = 0

            if not self.objective and not self.parsimony:
                solution = community.check_feasibility(values=self._get_values)
                if not self._check_solution(solution):
                    logging.info("Community Inconsistent: %s", str(selected_names))
                    self._add_knowledge_constraint(not_selected)
                    continue

            if self.objective:
                logging.info("Starting objective optimization.")
                objective_solution = community.objective_optimization(
                    self.objective,
                    self._get_values,
                )

                # check objective solution
                if not self._check_solution(objective_solution):
                    logging.warning("Unable to optimize objective.")
                    self._add_knowledge_constraint(not_selected)
                    continue

                # compute objective value
                for k, v in self.objective.items():
                    if k in objective_solution.values:
                        objective_value += v * objective_solution.values[k]

                # retain solution
                solution = objective_solution

            if self.parsimony:
                logging.info("Starting parsimony optimization.")
                parsimony_solution = community.parsimony_optimization(
                    self.objective,
                    objective_value,
                    self._get_values,
                )

                # check parsimony solution
                if not self._check_solution(parsimony_solution):
                    logging.warning("Unable to minimize fluxes.")
                    self._add_knowledge_constraint(not_selected)
                    continue

                # retain solution
                solution = parsimony_solution

            self.community.solver.add_constraint(
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

        self.community.solver.remove_constraints(self.knowledge_constraints.keys())
        self.community.solver.remove_constraints(self.community_constraints.keys())

        return self.solutions

    @property
    def _get_values(self):
        return list(self._community_objective.keys()) + self.values

    def _minimize_community(self):
        return self.community.solver.solve(
            linear=self._community_objective,
            get_values=self._get_values,
            minimize=True,
        )

    def _check_solution(self, solution):
        if solution.status != Status.OPTIMAL:
            logging.info("Solution status: %s", str(solution.status))
            return False
        logging.info(
            "Community growth: %f",
            solution.values[self.community.merged_model.biomass_reaction],
        )
        return True

    def _add_knowledge_constraint(self, not_selected: dict):
        constraint_name = f"c_tmp_{len(self.knowledge_constraints) + 1}"
        self.community.solver.add_constraint(constraint_name, not_selected, ">", 1)
        self.knowledge_constraints[constraint_name] = not_selected

    def _load_constraints_from_cache(self, cache: dict):
        for name, selected in cache["community_constraints"].items():
            self.community.solver.add_constraint(name, selected, "<", len(selected) - 1)
            self.community_constraints[name] = selected

        for name, not_selected in cache["knowledge_constraints"].items():
            self.community.solver.add_constraint(name, not_selected, ">", 1)
            self.knowledge_constraints[name] = not_selected

        self.solutions = cache["solutions"]

        self.community.solver.update()

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
            self.community.solver.add_variable(
                f"y_{org_id}",
                0,
                1,
                vartype=VarType.BINARY,
                update=False,
            )

        self.community.solver.update()

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
                    self.community.solver.set_bounds(
                        {merged_id: (-BOUND_INF, BOUND_INF)}
                    )

                self.community.solver.add_constraint(
                    f"c_{merged_id}_lb",
                    {merged_id: 1, org_var: -lbound},
                    ">",
                    0,
                    update=False,
                )
                self.community.solver.add_constraint(
                    f"c_{merged_id}_ub",
                    {merged_id: 1, org_var: -ubound},
                    "<",
                    0,
                    update=False,
                )
