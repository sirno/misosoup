"""Load and init solvers."""
import logging
import math

from reframed.solvers.solver import VarType


BOUND_INF = 1000


def introduce_binary_variables(community, solver, minimal_growth=0.01):
    """Add binary variables to the solver instance.

    Keyword arguments:
    community -- community model instance
    solver -- solver instance
    min_growth -- minimal growth rate required (default: 0.01)
    """
    for org_id in community.organisms.keys():
        solver.add_variable(f"y_{org_id}", 0, 1, vartype=VarType.BINARY, update=False)

    solver.update()

    for org_id, org_model in community.organisms.items():
        org_var = f"y_{org_id}"
        for r_id, reaction in org_model.reactions.items():
            if (
                not r_id.startswith("R_EX")
                and r_id != org_model.biomass_reaction
                and reaction.lb * reaction.ub <= 0
            ):
                continue

            merged_id = community.reaction_map[(org_id, r_id)]
            ubound = BOUND_INF
            lbound = -BOUND_INF

            if r_id == org_model.biomass_reaction:
                lbound = minimal_growth

            if reaction.lb * reaction.ub > 0:
                lbound = -BOUND_INF if math.isinf(reaction.lb) else reaction.lb
                ubound = BOUND_INF if math.isinf(reaction.ub) else reaction.ub
                solver.set_bounds({merged_id: (-BOUND_INF, BOUND_INF)})

            solver.add_constraint(
                f"c_{merged_id}_lb",
                {merged_id: 1, org_var: -lbound},
                ">",
                0,
                update=False,
            )
            solver.add_constraint(
                f"c_{merged_id}_ub",
                {merged_id: 1, org_var: -ubound},
                "<",
                0,
                update=False,
            )


def setup_medium(model, solver, medium):
    """Setup the medium for model on solver.

    Arguments:
    model -- model instance
    solver -- solver instance
    medium -- medium dict
    """
    missing_reactions = set(medium.keys()) - set(model.reactions.keys())
    for r_id in missing_reactions:
        logging.warning("Missing reaction %s in model %s", r_id, model.id)
    for r_id in model.reactions.keys():
        if r_id.startswith("R_EX_") and not r_id.endswith("_i"):
            bound = medium[r_id] if r_id in medium.keys() else 0
            solver.add_constraint(
                f"c_{r_id}_lb",
                {r_id: 1},
                ">",
                bound,
            )
