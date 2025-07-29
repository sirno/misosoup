"""Gurobi solver instance for individual environments."""

from gurobipy import Model as GurobiModel
from reframed.solvers.gurobi_solver import GurobiSolver
from reframed.solvers.solver import Parameter, Solver

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

        for par, value in default_parameters.items():
            self.set_parameter(par, value)

        self.params = params
        if params is not None:
            for par, value in params.items():
                self.set_parameter(par, value)

        if model:
            self.build_problem(model)
