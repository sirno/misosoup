"""Gurobi solver instance for individual environments."""

from reframed.solvers.solver import Solver, Parameter
from reframed.solvers.gurobi_solver import GurobiSolver, default_parameters
from gurobipy import Model as GurobiModel


default_parameters = {
    Parameter.OPTIMALITY_TOL: 1e-6,
    Parameter.FEASIBILITY_TOL: 1e-6,
}


class GurobiEnvSolver(GurobiSolver):
    """Gurobi interface initialized in gurobi environment."""

    def __init__(self, model=None, env=None, params=None):
        """Init GurobiEnvSolver."""
        Solver.__init__(self)
        self.problem = GurobiModel(env=env)
        self.set_parameters(default_parameters)
        self.params = params
        if params is not None:
            self.set_parameters(params)
        if model:
            self.build_problem(model)
