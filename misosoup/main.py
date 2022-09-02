"""MiSoS(oup)"""

import argparse
import glob
import logging
import os
from collections import defaultdict

import yaml

from .library.getters import get_biomass, get_exchange_reactions
from .library.readwrite import load_models, read_compounds
from .library.validate import validate_solution_dict
from .library.minimizer import Minimizer

from .reframed.layered_community import LayeredCommunity


def main(args):
    """Main function."""
    input_paths = glob.glob(args.input[0]) if len(args.input) == 1 else args.input
    models = load_models(input_paths)

    media = read_compounds(args.media)
    base_medium = media["base_medium"] if "base_medium" in media.keys() else {}

    community = LayeredCommunity("CoI", models, copy_models=False)

    solutions = defaultdict(dict)

    if args.objective:
        objective = {reaction: 1 for reaction in args.objective}
    else:
        objective = {community.merged_model.biomass_reaction: 1}

    if args.disable_objective:
        objective = None

    for medium_id, medium_composition in media.items():
        if not medium_id == "base_medium" and (
            not args.media_select or medium_id in args.media_select
        ):
            medium = {
                **medium_composition,
                **base_medium,
            }

            minimizer = Minimizer(
                org_id=args.strain,
                medium=medium,
                community=LayeredCommunity("community", models),
                values=(
                    get_biomass(community)
                    + get_exchange_reactions(community.merged_model)
                ),
                community_size=args.community_size,
                objective=objective,
                parsimony=args.parsimony,
                minimal_growth=args.minimal_growth,
                cache_file=args.cache_file,
            )

            solution = minimizer.minimize()

            solutions[medium_id][args.strain] = solution

    output_dict = {
        k: {org: sol if sol else [{f"Growth_{org}": 0}] for org, sol in v.items()}
        for k, v in solutions.items()
    }

    if args.validate:
        validate_solution_dict(output_dict, args.exchange_format)

    output = yaml.dump(output_dict, Dumper=yaml.CSafeDumper)

    if args.output:
        if not os.path.exists(os.path.dirname(args.output)):
            os.makedirs(os.path.dirname(args.output))
        with open(args.output, "a", encoding="utf8") as file_descriptor:
            file_descriptor.write(output)
    else:
        print(output)


def entry():
    """Misosoup entry point."""
    parser = argparse.ArgumentParser(
        description="""
    Compute minimal supplying communities with MiSoS(oup).

    `misosoup` will create a large community network and evaluate which
    communities can supply growth of some strain (or each other, if no strain
    is chosen).

    It will report the results in `yaml` format, where the dictionaries contain all
    active exchange reactions and their rates, as well as the activity of strains (i.e.
    `y_strain: 1` for any active strain), the community growth rate and the individual
    growth rates of all participating strains:

        ```
        carbon_source:
            strain:
                - {}
                - {}
        ```
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input", nargs="+", type=str, help="List or wildcard for model paths."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file. Format: YAML. If not supplied, will print to stdout.",
    )
    parser.add_argument(
        "--cache-file",
        type=str,
        help="Path to cache file. If set, intermediate constraints will be stored.",
    )
    parser.add_argument(
        "--media",
        type=str,
        required=True,
        help="Path to media. Format: YAML. File needs to contain dictionary with media, see examples.",
    )
    parser.add_argument(
        "--media-select",
        type=str,
        nargs="+",
        help="List of media names to use from the media file.",
    )
    parser.add_argument(
        "--strain",
        type=str,
        default="min",
        help="Focal strain model id. If no strain is provided, we compute minimal communities.",
    )
    parser.add_argument(
        "--parsimony", action="store_true", help="Compute parsimony solution."
    )
    parser.add_argument(
        "--community-size",
        type=int,
        default=0,
        help="Maximum community size. Default: 0 (Arbitrary).",
    )
    parser.add_argument(
        "--minimal-growth",
        type=float,
        default=0.01,
        help=(
            "Minimal required growth for strain or community."
            "Each strain that is considered to grow needs to at least achieve "
            "this minimal growth rate given by this argument."
        ),
    )
    parser.add_argument(
        "--exchange-format",
        type=str,
        default="R_EX_{}_e",
        help=(
            "Regular expression to retrieve the carbon source from an exchange "
            "reaction. The group containing the carbon source, should be named "
            "`carbon_source`; as can be seen from the default. "
            "default: `R_EX_(\\w+)_e"
        ),
    )
    parser.add_argument(
        "--disable-objective",
        action="store_true",
        help="If set, no objective will be optimized.",
    )
    parser.add_argument(
        "--objective",
        type=str,
        nargs="+",
        help=(
            "List of ids that are part of the objective function. By default "
            + "the community biomass is maximized."
        ),
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help=(
            "Validate solution. Numerical consistency will be verified on the "
            "final solution."
        ),
    )
    parser.add_argument("--log", default="INFO", help="Log level. Default: INFO")

    args_parsed = parser.parse_args()

    logging.basicConfig(level=args_parsed.log, format="%(asctime)s %(message)s")

    main(args_parsed)
