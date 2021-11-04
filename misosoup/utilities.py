"""MiSoS(oup) utilities."""
import argparse
import sys
import os

from glob import glob
from random import sample

import yaml

from .library.validate import validate_solution_file


def filter_soup():
    """Main."""
    parser = argparse.ArgumentParser(
        description="Remove numerical relicts from `misosoup` solutions."
    )
    parser.add_argument("--log", default="INFO")
    parser.add_argument("input", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("--threshold", type=float, default=10e-8)

    args = parser.parse_args()

    with open(args.input) as file_descriptor:
        solution_data = yaml.safe_load(file_descriptor)

    output_dict = {
        cs: {
            org: [
                {r: v for r, v in sol.items() if abs(v) > args.threshold}
                for sol in org_sols
            ]
            for org, org_sols in cs_sols.items()
        }
        for cs, cs_sols in solution_data.items()
    }

    output = yaml.dump(output_dict)

    if args.output:
        if not os.path.exists(os.path.dirname(args.output)):
            os.makedirs(os.path.dirname(args.output))
        with open(args.output, "w") as file_descriptor:
            file_descriptor.write(output)
    else:
        print(output)


def taste_soup():
    """Verify integrity of solutions in raw misosoup output."""
    parser = argparse.ArgumentParser(
        description="Verify integrity of solutions in raw `misosoup` output."
    )
    parser.add_argument("--log", default="INFO")
    parser.add_argument("input", type=str)

    args = parser.parse_args()

    if validate_solution_file(args.input):
        print("\033[92mValid solution file.\033[0m")
    else:
        print("\033[91mInvalid solution file.\033[0m")
        sys.exit(os.EX_DATAERR)


def select_ingredients():
    """Create directory with sampled models."""
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--log", default="INFO")
    parser.add_argument("source", type=str, help="Source directory with sbml models.")
    parser.add_argument(
        "target", type=str, help="Target directory is created and contains symlinks."
    )
    parser.add_argument("-n", "--n-models", type=int, default=10)

    args = parser.parse_args()

    files = glob(os.path.join(args.source, "*.xml"))
    file_names = [os.path.basename(f) for f in files]
    source_list = args.source.split(os.sep)
    target_list = args.target.split(os.sep)

    if not source_list[-1]:
        source_list.pop()
    if not target_list[-1]:
        target_list.pop()

    # move to common node
    while target_list[0] == source_list[0]:
        target_list.pop(0)
        source_list.pop(0)

    # add relative difference
    source_list = len(target_list) * [".."] + source_list

    relative_source = os.path.join(*source_list)
    relative_files = [os.path.join(relative_source, f) for f in file_names]

    os.makedirs(args.target)

    sampled = sample(relative_files, args.n_models)
    for _sample in sampled:
        os.symlink(_sample, os.path.join(args.target, os.path.basename(_sample)))
