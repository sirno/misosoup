"""Solver functions."""
import logging

from reframed.solvers.solution import Status

logger = logging.getLogger(__name__)


def minimal_suppliers(
    org,
    community,
    solver,
    values,
    community_size=0,
    growth=True,
    parsimony=False,
    minimal_growth=0.01,
):
    """Compute minimal suppliers with MiSoS(oup).

    Keyword Arguments:
    org -- focal strain id
    community -- community model
    solver -- solver instance
    values -- list with variables to store
    community_size -- max community size, if 0 all community sizes will be searched (default: 0)
    growth -- optimize growth (default: True)
    parsimony -- minimize flux (default: False)
    """
    solver.add_constraint(
        f"c_{org}_growth",
        {community.reaction_map[org, community.organisms[org].biomass_reaction]: 1},
        ">",
        minimal_growth,
        update=True,
    )
    solutions = _minimize(community, solver, values, community_size, growth, parsimony)
    solver.remove_constraints([f"c_{org}_growth"])
    return solutions


def minimal_communities(
    org_id,
    community,
    solver,
    values,
    community_size=0,
    growth=True,
    parsimony=False,
    minimal_growth=0.01,
):
    """Compute minimal communities with MiSoS(oup).

    Keyword Arguments:
    community -- community model
    solver -- solver instance
    values -- list with variables to store
    community_size -- max community size, if 0 all community sizes will be searched (default: 0)
    growth -- optimize growth (default: True)
    parsimony -- minimize flux (default: False)
    """
    assert org_id == "min"
    solver.add_constraint(
        "c_community_growth",
        {community.merged_model.biomass_reaction: 1},
        ">",
        minimal_growth,
        update=True,
    )
    solutions = _minimize(community, solver, values, community_size, growth, parsimony)
    solver.remove_constraints(["c_community_growth"])
    return solutions


def _minimize(community, solver, values, community_size, growth, parsimony):
    """Minimize the community size for problem as set up in solver."""
    solutions = []
    constraints = []
    temporary_constraints = []

    obj = {f"y_{org_id}": 1 for org_id in community.organisms.keys()}

    solution_length = 0
    i = 0

    while True:
        logging.info("------------")
        logging.info("Starting optimization...")
        solution = solver.solve(
            linear=obj,
            get_values=list(obj.keys()) + values,
            minimize=True,
        )

        logging.info("Solution status: %s", str(solution.status))

        if solution.status != Status.OPTIMAL:
            break

        selected = {k: 1 for k in obj.keys() if solution.values[k] > 0.5}
        not_selected = {k: 1 for k in obj.keys() if solution.values[k] < 0.5}
        logging.info("Community size: %i", len(selected))
        logging.info(
            "Community growth: %f",
            solution.values[community.merged_model.biomass_reaction],
        )

        # Fix selected community
        solver.add_constraint("c_not_selection", not_selected, "=", 0, update=True)
        solver.add_constraint("c_selection", selected, "=", len(selected), update=True)

        try:
            if growth:
                logging.info("Starting growth optimization.")
                solution = solver.solve(
                    linear={community.merged_model.biomass_reaction: 1},
                    get_values=list(obj.keys()) + values,
                    minimize=False,
                )
                if solution.status != Status.OPTIMAL:
                    logging.info(
                        "Community Inconsistent: %s", str(list(selected.keys()))
                    )
                    solver.add_constraint(
                        f"c_tmp_{len(temporary_constraints) + 1}", not_selected, ">", 1
                    )
                    temporary_constraints.append(
                        f"c_tmp_{len(temporary_constraints) + 1}"
                    )
                    continue
                solver.remove_constraints(temporary_constraints)
                temporary_constraints = []
                logging.info(
                    "Community growth: %f",
                    solution.values[community.merged_model.biomass_reaction],
                )

            if parsimony:
                logging.info("Starting parsimony optimization.")

                solver.add_constraint(
                    "c_growth",
                    {community.merged_model.biomass_reaction: 1},
                    ">",
                    solution.values[community.merged_model.biomass_reaction] - 1e-4,
                    update=True,
                )

                solution = solver.solve(
                    quadratic={
                        (rid, rid): 1
                        for rid in community.merged_model.reactions
                        if not rid.startswith("Growth")
                        and rid != community.merged_model.biomass_reaction
                    },
                    get_values=list(obj.keys()) + values,
                    minimize=True,
                )

                solver.remove_constraints(["c_growth"])

                logging.info("Parsimony solution status: %s", str(solution.status))
                if solution.status != Status.OPTIMAL:
                    break
                logging.info(
                    "Parsimony community growth: %f",
                    solution.values[community.merged_model.biomass_reaction],
                )
        finally:
            solver.remove_constraints(["c_not_selection", "c_selection"])

        solver.add_constraint(f"c_{i}", selected, "<", len(selected) - 1, update=True)
        constraints.append(f"c_{i}")

        solution_length = len(selected)
        if community_size and solution_length > community_size:
            break

        solutions.append(solution)

        i += 1

        if not community_size:
            break

    solver.remove_constraints(constraints)

    return solutions
