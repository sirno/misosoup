# MiSoS(oup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/misosoup.svg)](https://badge.fury.io/py/misosoup)

Minimal Supplying Community Search (`misosoup`) is a command line utility
designed to search for minimal microbial communities, wherein every member is
essential for the community's persistence within a given medium. Its primary
functions include:

- Identifying minimal communities within a specified medium.
- Identifying minimal "supplying" communities within a medium, where each
  member is crucial for the growth of a focal strain or species of interest.

To utilize "misosoup," users provide a set of genome-scale metabolic models,
each representing a potential member of the community. The program then employs
constraint-based optimizations to determine minimal communities. These
optimizations assume a metabolic steady-state, akin to Flux Balance Analysis,
without necessitating specific optimization criteria (though they can be
optionally applied).

Once computations are complete, "misosoup" outputs information about community
members, their respective growth rates, as well as their metabolic consumption
and secretion, presented in a format both readable by humans and parseable by
software.

## Details

To find minimal microbial communities `misosoup` solves a repeated sequence of
optimization problems using MILP formulations:

1. Minimize the number of community member (see Zelezniak, et al. PNAS
   doi:10.1073/pnas.1421834112)
2. Fix the active community members and check the feasibility of the entire community.
3. Optionally: Optimize growth of the total community biomass.
4. Optionally: Perform an optimization to reflect parsimonious enzyme usage
   (see Lewis, et al. Mol Syst Bio doi:10.1038/msb.2010.47)

## Install MiSoS(soup)

`misosoup` requires a version of Python >3.7 and <3.11.

The latest stable version of `misosoup` is available through `pip` and hence it can easily installed executing:

```bash
pip install misosoup
```

### Dependencies

* `misosoup` uses the `Guroby` optimizer that is free for academic use but it
  requires a license.
* Academic licenses can be obtained on the
  [gurobi license page](https://www.gurobi.com/academia/academic-program-and-licenses/)
* Precise instructions on how to obtain and setup the gurobi licenses can be found on
  the [gurobi website](https://www.gurobi.com).

## Usage

After installation, you can easily use `misosoup` with:

```bash
misosoup MODEL_PATH/*.xml --output OUTPUT_FILE --media MEDIA_FILE --strain STRAIN
```

### Arguments

* `MODEL_PATH`: indicates the path to the directory where the metabolic models are
  described. Strains with metabolic models included in this directory will be
  considered as potential members in the minimal communities. The models should
  be in sbml format and follow the same naming conventions (e.g. if glucose's id
  in one model is 'glc__D', the same id should be used in the other models).
* `--output`
  * Use OUTPUT_FILE for output in yaml format. If it is not given, the results
    will be printed to stdout.
* `--media`
  * Load media from MEDIA_FILE. The file should contain the description of the
    growth media that shall be tested. The file should contain a dictionary with
    all media that the community should be evaluated on. Each of the media needs
    to contain a dictionary of exchange reactions and there lower bound, (i.e.
    `R_EX_ac_e: -10` provides _acetate_ to the communities). The medium with id
    `base_medium` will be added to all media.
* `--strain`
  * Indicates the focal STRAIN model id. If no strain is provided, `misosoup`
    computes minimal communities.

## Additional arguments

`misosoup` can be used with additional arguments.

```bash
misosoup MODEL_PATH/*.xml --output OUTPUT_FILE --media MEDIA_FILE --strain STRAIN --parsimony --community-size COMMUNITY_SIZE --minimal-growth MINIMAL_GROWTH
```

* `--parsimony`
    * If this flag is used the algorithm will return the solution that minimizes
    the total flux. This does not affect the community members but can alter
    what each member consumes and secretes.
* `--community-size`
    * Instead of looking for all communities, find all communities up to size
    COMMUNITY_SIZE
* `--minimal-growth`
    * Set the MINIMAL_GROWTH rate of strains. Every strain that makes up a
    community needs to satisfy this minimal growth constraint. The default
    growth rate used is 0.01 (1/h).

All available options can be obtained with:

```bash
misosoup --help
```

## Output file

As output `misosoup` will generate a yaml file with the following general
structure:

```yaml
carbon_source:
    focal_strain:
      - <Solution1>
      - <Solution2>
```

The solutions indicated above contain multiple entries that depend on the
specific settings misosoup has been run with. Within the solutions there are
several entries that indicate if the different optimization / verification
methods that `misosoup` used to verify the integrity of the solution failed or
succeded.

## Example

```bash
cd example
```

The following code will run `misosoup` to find minimal supplying communities for
A1R12 in a medium that contains acetate as carbon source:

```bash
misosoup ./strains/*.xml --output ./output_example.yaml --media media.yaml --strain A1R12 --media-select ac
```

In the example, we run `misosoup` to find minimal supplying communities that
would allow growth of the strain
[A1R12](https://biocyc.org/A1R12/organism-summary) in MBM with acetate (ac) as
the sole source of carbon. Looking at the output of the simulation
example_output.yaml) you'll see that `misosoup` found two alternative supplying
communities:

* Solution 1: A1R12 can grow when in the presence of I3M07. If we inspect this
  solution in more detail we can see (for example):
  * Each strain produces carbon dioxide. We note this by looking at the
    strain-specific carbon dioxide fluxes: `R_EX_co2_e_A1R12_i: 0.742` and
    `R_EX_co2_e_I3M07_i: 0.957`.
  * The community as a whole also produces carbon dioxide, which can be seen
    looking at the community-level carbon dioxide flux `R_EX_co2_e: 1.699`.
* Solution 2: A1R12 can grow when in the presence of I2R16. A similar analysis
  to the one conducted for solution 1 could be followed.

## Citation

If you use misosoup, please cite X.

## Workflows

`snakemake` is a useful tool to execute many experiments and gather results.
See [`misosoup` Workflow Template](https://gitlab.ethz.ch/ochsnern/misosoup_workflow_template)
on how to use it.

## Development

Any contributions are welcome.

