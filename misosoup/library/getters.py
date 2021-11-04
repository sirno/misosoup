"""Create lists with variables for communities and models."""
from math import copysign


def get_binary(community):
    """Binary variables for community."""
    return [f"y_{org_id}" for org_id in community.organisms.keys()]


def get_biomass(community):
    """Biomass reactions for communities."""
    return [community.merged_model.biomass_reaction] + [
        community.reaction_map[org_id, org_model.biomass_reaction]
        for org_id, org_model in community.organisms.items()
    ]


def get_exchange_reactions(model):
    """Exchange reactions for model."""
    return [r_id for r_id in model.reactions.keys() if r_id.startswith("R_EX_")]


def get_consuming_metabolite_reactions(community, organism):
    """Get consuming reactions for organism in community."""
    reactions = []
    metabolite_lookup = {}
    metabolites = organism.get_external_metabolites(from_reactions=True)
    for metabolite in metabolites:
        rxns = organism.get_metabolite_consumers(metabolite)
        reactions = reactions + [
            community.reaction_map[organism.id, rxn]
            for rxn in rxns
            if not rxn.startswith("R_EX_") and not rxn.startswith("R_sink_")
        ]
        metabolite_lookup.update(
            {
                rxn: {
                    "metabolite": metabolite,
                    "direction": copysign(
                        1,
                        community.merged_model.reactions[rxn].stoichiometry[metabolite],
                    ),
                }
                for rxn in rxns
            }
        )

    return reactions, metabolite_lookup


def get_producing_metabolite_reactions(community, organism):
    """Get producing reactions for organism in community."""
    reactions = []
    producer_lookup = {}
    metabolites = organism.get_external_metabolites(from_reactions=True)
    for metabolite in metabolites:
        rxns = organism.get_metabolite_producers(metabolite)
        reactions = reactions + [
            community.reaction_map[organism.id, rxn]
            for rxn in rxns
            if not rxn.startswith("R_EX_") and not rxn.startswith("R_sink_")
        ]
        producer_lookup.update(
            {
                rxn: {
                    "metabolite": metabolite,
                    "direction": copysign(
                        1,
                        community.merged_model.reactions[rxn].stoichiometry[metabolite],
                    ),
                }
                for rxn in rxns
            }
        )

    return reactions, producer_lookup
