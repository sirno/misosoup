"""Layered community class implementation."""

import logging
import math

from gurobipy import Env
from reframed import (
    CBModel,
    CBReaction,
    Community,
    Compartment,
    Gene,
    GPRAssociation,
    Metabolite,
    Protein,
    ReactionType,
)
from reframed.solvers.solver import VarType

from ..reframed.gurobi_env_solver import GurobiEnvSolver

BOUND_INF = 1000


class LayeredCommunity(Community):
    """Community model with additional layer of exchange reactions for each member."""

    default_environment = Env(params={"LogToConsole": 0, "Method": 1})

    def __init__(
        self,
        community_id: str,
        models: list,
        env: Env = None,
        copy_models=False,
        suffix="_i",
        params=None,
    ):
        super().__init__(
            community_id=community_id,
            models=models,
            copy_models=copy_models,
        )

        if env is None:
            env = self.default_environment

        self.suffix = suffix
        self.solver = GurobiEnvSolver(model=self.merged_model, env=env, params=params)
        self.has_binary_variables = False

    def merge_models(self):
        comm_model = CBModel(self.id)
        old_ext_comps = []
        ext_mets = []
        self.reaction_map = {}
        self.metabolite_map = {}

        # default IDs
        ext_comp_id = "ext"
        biomass_id = "community_biomass"
        comm_growth = "community_growth"

        # create external compartment

        comp = Compartment(ext_comp_id, "extracellular environment", external=True)
        comm_model.add_compartment(comp)

        # community biomass

        met = Metabolite(biomass_id, "Total community biomass", ext_comp_id)
        comm_model.add_metabolite(met)

        rxn = CBReaction(
            comm_growth,
            name="Community growth rate",
            reversible=False,
            stoichiometry={biomass_id: -1},
            lb=0,
            ub=math.inf,
            objective=1,
        )

        comm_model.add_reaction(rxn)

        # add each organism
        for org_id, model in self.organisms.items():

            def rename(old_id):
                return f"{old_id}_{org_id}"

            # add internal compartments
            for c_id, comp in model.compartments.items():
                if comp.external:
                    old_ext_comps.append(c_id)
                new_comp = Compartment(rename(c_id), comp.name)
                comm_model.add_compartment(new_comp)

            # add metabolites
            for m_id, met in model.metabolites.items():
                # always create a local metabolite
                new_id = rename(m_id)
                new_met = Metabolite(new_id, met.name, rename(met.compartment))
                new_met.metadata = met.metadata.copy()
                comm_model.add_metabolite(new_met)
                self.metabolite_map[(org_id, m_id)] = new_id

                # if the metabolite is external and not yet added to the
                # community model, add it
                if (
                    met.compartment in old_ext_comps
                    and m_id not in comm_model.metabolites
                ):
                    new_met = Metabolite(m_id, met.name, ext_comp_id)
                    new_met.metadata = met.metadata.copy()
                    comm_model.add_metabolite(new_met)
                    ext_mets.append(new_met.id)

            # add genes
            for g_id, gene in model.genes.items():
                new_id = rename(g_id)
                new_gene = Gene(new_id, gene.name)
                new_gene.metadata = gene.metadata.copy()
                comm_model.add_gene(new_gene)

            # add internal reactions
            for r_id, rxn in model.reactions.items():
                new_id = rename(r_id)

                if rxn.reaction_type == ReactionType.EXCHANGE and r_id.startswith(
                    "R_EX"
                ):
                    new_id = new_id + self.suffix

                    m_id = list(rxn.stoichiometry.keys())[0]
                    ext_m_id = biomass_id if r_id == model.biomass_reaction else m_id
                    int_m_id = rename(m_id)

                    new_stoichiometry = {
                        ext_m_id: 1,
                        int_m_id: -1,
                    }
                    new_rxn = CBReaction(
                        new_id,
                        reversible=True,
                        stoichiometry=new_stoichiometry,
                        reaction_type=ReactionType.EXCHANGE,
                    )
                else:
                    new_stoichiometry = {
                        rename(m_id): coeff for m_id, coeff in rxn.stoichiometry.items()
                    }

                    if r_id == model.biomass_reaction:
                        new_stoichiometry[biomass_id] = 1

                    if rxn.gpr is None:
                        new_gpr = None
                    else:
                        new_gpr = GPRAssociation()
                        new_gpr.metadata = rxn.gpr.metadata.copy()

                        for protein in rxn.gpr.proteins:
                            new_protein = Protein()
                            new_protein.genes = [rename(g_id) for g_id in protein.genes]
                            new_protein.metadata = protein.metadata.copy()
                            new_gpr.proteins.append(new_protein)

                    new_rxn = CBReaction(
                        new_id,
                        name=rxn.name,
                        reversible=rxn.reversible,
                        stoichiometry=new_stoichiometry,
                        reaction_type=rxn.reaction_type,
                        lb=rxn.lb,
                        ub=rxn.ub,
                        gpr_association=new_gpr,
                    )

                comm_model.add_reaction(new_rxn)
                new_rxn.metadata = rxn.metadata.copy()
                self.reaction_map[(org_id, r_id)] = new_id

        # Add exchange reactions

        for m_id in ext_mets:
            r_id = f"R_EX_{m_id[2:]}" if m_id.startswith("M_") else f"R_EX_{m_id}"
            rxn = CBReaction(
                r_id,
                reversible=True,
                stoichiometry={m_id: -1},
                reaction_type=ReactionType.EXCHANGE,
            )
            comm_model.add_reaction(rxn)

        return comm_model

    def setup_binary_variables(self, minimal_growth):
        """Setup binary variables for each organism."""
        for org_id in self.organisms.keys():
            self.solver.add_variable(
                f"y_{org_id}",
                0,
                1,
                vartype=VarType.BINARY,
                update=False,
            )

        self.solver.update()

        for org_id, org_model in self.organisms.items():
            org_var = f"y_{org_id}"
            for r_id, reaction in org_model.reactions.items():
                if (
                    not r_id.startswith("R_EX")
                    and r_id != org_model.biomass_reaction
                    and reaction.lb * reaction.ub <= 0
                ):
                    continue

                merged_id = self.reaction_map[(org_id, r_id)]
                ubound = BOUND_INF
                lbound = -BOUND_INF

                if r_id == org_model.biomass_reaction:
                    lbound = minimal_growth

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

        self.solver.update()
        self.has_binary_variables = True

    def setup_growth_requirement(self, minimal_growth):
        for org_id, org_model in self.organisms.items():
            merged_id = self.reaction_map[(org_id, org_model.biomass_reaction)]
            self.solver.add_constraint(
                f"c_{merged_id}_lb",
                {merged_id: 1},
                ">",
                minimal_growth,
                update=False,
            )
        self.solver.update()

    def setup_medium(self, medium):
        """Setup the medium for model on solver."""
        missing_reactions = set(medium.keys()) - set(self.merged_model.reactions.keys())
        for r_id in sorted(missing_reactions):
            logging.warning(
                "Missing reaction %s in model %s", r_id, self.merged_model.id
            )
        for r_id in self.merged_model.reactions.keys():
            if r_id.startswith("R_EX_") and not r_id.endswith("_i"):
                bound = medium[r_id] if r_id in medium.keys() else 0
                self.solver.add_constraint(
                    f"c_{r_id}_lb",
                    {r_id: 1},
                    ">",
                    bound,
                )

    def setup_parsimony(self):
        # add absolute variables for each reaction
        for rid in self.merged_model.reactions:
            self.solver.add_variable(f"abs_{rid}_pos", 0, 1000, update=False)
            self.solver.add_variable(f"abs_{rid}_neg", 0, 1000, update=False)

        self.solver.update()

        # add absolute constraints for each reaction
        for rid in self.merged_model.reactions:
            self.solver.add_constraint(
                f"c_{rid}_abs",
                {f"abs_{rid}_pos": 1, f"abs_{rid}_neg": -1, rid: -1},
                "=",
                0,
            )

    def check_feasibility(self, values: list):
        existing_values = set(values) & set(self.merged_model.reactions.keys())
        logging.debug("Gathering variables: %s", existing_values)
        return self.solver.solve(get_values=existing_values)

    def objective_optimization(self, objective: dict, values: list):
        existing_values = set(values) & set(self.merged_model.reactions.keys())
        return self.solver.solve(
            linear=objective,
            get_values=existing_values,
            minimize=False,
        )

    def parsimony_optimization(self, objective: dict, value: float, values: list):
        if value > 0:
            self.solver.add_constraint(
                "c_growth",
                objective,
                ">",
                value,
                update=True,
            )

        existing_values = set(values) & set(self.merged_model.reactions.keys())
        parsimony_solution = self.solver.solve(
            linear={
                f"abs_{rid}_{sense}": 1
                for rid in self.merged_model.reactions
                for sense in ["pos", "neg"]
            },
            get_values=existing_values,
            minimize=True,
        )

        self.solver.remove_constraints(["c_growth"])

        return parsimony_solution
