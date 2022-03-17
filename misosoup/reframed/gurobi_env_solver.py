"""Gurobi solver instance for individual environments."""

from reframed.solvers.solver import Solver
from reframed.solvers.gurobi_solver import GurobiSolver, default_parameters
from gurobipy import Model as GurobiModel


class GurobiEnvSolver(GurobiSolver):
    """Gurobi interface initialized in gurobi environment."""

    def __init__(self, model=None, env=None):
        """Init GurobiEnvSolver."""
        Solver.__init__(self)
        if env:
            self.problem = GurobiModel(env=env)
        else:
            self.problem = GurobiModel()
        self.set_parameters(default_parameters)
        if model:
            self.build_problem(model)
