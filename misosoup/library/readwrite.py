import yaml

import pandas as pd

from reframed.io.sbml import load_cbmodel

from .common import get_reaction_name


def load_models(paths):
    return [load_cbmodel(path, flavor="fbc2") for path in paths]


def read_medium(path, medium_name):
    with open(path, "r") as fd:
        medium_data = yaml.safe_load(fd)
    return {
        key: [get_reaction_name(compound) for compound in compounds]
        for key, compounds in medium_data[medium_name].items()
    }


def read_compounds(path):
    with open(path, "r") as fd:
        compounds = yaml.safe_load(fd)
    return compounds


def read_supplements(path):
    with open(path, "r") as fd:
        supplement_sources = yaml.safe_load(fd)
    return [get_reaction_name(source) for source in supplement_sources.carbon_sources]


def write_minimal_suppliers(solutions, path=None):
    processed = {
        org: [
            {
                "biomass": sol.values["community_growth"],
                "community": [
                    k for k, v in sol.values.items() if v == 1 and k.startswith("y_")
                ],
            }
            for sol in sols
        ]
        for org, sols in solutions.items()
    }
    if path:
        with open(path, "w") as f:
            f.write(yaml.dump(processed))
    else:
        print(yaml.dump(processed))


def read_solutions_yaml(file_path):
    with open(file_path, "r") as fd:
        solutions = yaml.safe_load(fd)

    carbon_source_solutions_type = list(solutions.values())[0]
    strain_solutions_type = list(carbon_source_solutions_type.values())[0]
    data_dict = (
        {
            (carbon_source, strain, idx): {**strain_solution}
            for carbon_source, carbon_source_solutions in solutions.items()
            for strain, strain_solutions in carbon_source_solutions.items()
            for idx, strain_solution in enumerate(strain_solutions)
        }
        if isinstance(strain_solutions_type, list)
        else {
            (carbon_source, strain, 0): {**strain_solutions}
            for carbon_source, carbon_source_solutions in solutions.items()
            for strain, strain_solutions in carbon_source_solutions.items()
        }
    )

    df = pd.DataFrame.from_dict(
        data_dict,
        orient="index",
    ).sort_index(level=0)
    df.index.names = ["carbon_source", "strain", "solution_idx"]
    df["growth_rate"] = df.community_growth

    return df


def read_isolates_yaml(file_path):
    with open(file_path, "r") as fd:
        solutions = yaml.safe_load(fd)

    # carbon_sources = list(solutions.keys())
    # strains = list(solutions[carbon_sources[0]].keys())

    isolates_df = pd.DataFrame.from_dict(
        {
            (carbon_source, strain): {
                "biomass": strain_solution["biomass"],
                **strain_solution["exchange"],
            }
            for carbon_source, carbon_source_solutions in solutions.items()
            for strain, strain_solution in carbon_source_solutions.items()
        },
        orient="index",
    )
    isolates_df.index.names = ["carbon_source", "strain"]
    isolates_df["growth_rate"] = isolates_df.biomass

    return isolates_df
