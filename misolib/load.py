"""Load and init solvers."""
from reframed.solvers.solver import VarType


def introduce_binary_variables(community, solver, min_growth=0.01):
    """Add binary variables to the solver instance.

    Keyword arguments:
    community -- community model instance
    solver -- solver instance
    min_growth -- minimal growth rate required (default: 0.01)
    """
    for org_id in community.organisms.keys():
        solver.add_variable(f"y_{org_id}", 0, 1, vartype=VarType.BINARY, update=False)

    solver.update()

    bound = 1000

    for org_id, org_model in community.organisms.items():
        org_var = f"y_{org_id}"
        for r_id in org_model.reactions.keys():
            merged_id = community.reaction_map[(org_id, r_id)]

            if r_id == org_model.biomass_reaction:
                solver.add_constraint(
                    f"c_{merged_id}_lb",
                    {merged_id: 1, org_var: -min_growth},
                    ">",
                    0,
                    update=False,
                )
                solver.add_constraint(
                    f"c_{merged_id}_ub",
                    {merged_id: 1, org_var: -bound},
                    "<",
                    0,
                    update=False,
                )
            else:
                solver.add_constraint(
                    f"c_{merged_id}_lb",
                    {merged_id: 1, org_var: bound},
                    ">",
                    0,
                    update=False,
                )
                solver.add_constraint(
                    f"c_{merged_id}_ub",
                    {merged_id: 1, org_var: -bound},
                    "<",
                    0,
                    update=False,
                )


def setup_medium(model, solver, base_medium, carbon_sources):
    """Setup the medium for model on solver.

    Arguments:
    model -- model instance
    solver -- solver instance
    base_medium -- list with compounds
    carbon_sources -- list with carbon sources
    """
    for r_id in model.reactions.keys():
        if r_id.startswith("R_EX_") and not r_id.endswith("_INT"):
            if r_id[2:] in base_medium:
                bound = -1000
            elif r_id[2:] in carbon_sources:
                bound = -10
            else:
                bound = 0
            solver.add_constraint(
                f"c_{r_id}_lb",
                {r_id: 1},
                ">",
                bound,
            )
