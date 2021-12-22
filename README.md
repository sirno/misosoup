# MiSoS(oup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Minimal Supplying Community Search (`misosoup`) is a command line tool that
searches for minimal microbial communities. These are communities in which every
member is required for the community to persist. `misosoup` can be used for two
major objectives: (1) Find minimal communities in a given medium or (2) Find
minimal supplying communities in a medium; these are the minimal communities
required for growth of a strain (or species) of interest, that we refer to as
the focal strain.

As input `misosoup` takes a set of genome-scale metabolic models; one for each
strain (species) that will be considered as potential community members. The
tool will then execute a series of constraint-based optimizations to find
minimal communities. For the computation of the solutions metabolic steady-state
is assumed (as in Flux Balance Analysis). Once computed, community members,
their respective growth rates and there metabolic consumption and secretion will
be reported in a human-readable and parsable format.

## Details

To find minimal microbial communities `misosoup` solves a repeated sequence of
optimization problems using MILP formulations:

1. Minimize the number of community member (see Zelezniak, et al. PNAS
   doi:10.1073/pnas.1421834112)
2. Fix the active community members and optimize growth of the total community
   biomass. If this fails, exclude the community from the possible solutions and
   repeat.
3. Optionally: Execute a third optimization to reflect parsimonious enzyme usage
   (see Lewis, et al. Mol Syst Bio doi:10.1038/msb.2010.47)

## Install MiSoS(soup)

```bash
pip install misosoup
```

If you are unable to install `gurobipy`, it may need to be installed manually
e.g. on a hpc cluster, to make use of the local gurobi installation. In such
a case please refer to the instructions on the cluster support page.

## Usage

After installation, you can easily use `misosoup` with:

```bash
misosoup MODEL_PATH/*.xml --output OUTPUT_FILE --media MEDIA_FILE --strain STRAIN
```

### Arguments

* MODEL_PATH: indicates the path to the directory where the metabolic models are
  described. Strains with metabolic models included in this directory will be
  considered as potential members in the minimal communities. The models should
  be in sbml format and follow the same naming conventions (e.g. if glucose's id
  in one model is 'glc__D', the same id should be used in the other models).
* --output
  * Use OUTPUT_FILE for output in yaml format. If it is not given, the results
    will be printed to stdout.
* --media
  * Load media from MEDIA_FILE. The file should contain the description of the
    growth media that shall be tested. The file should contain a dictionary with
    all media that the community should be evaluated on. Each of the media needs
    to contain a dictionary of exchange reactions and there lower bound, (i.e.
    `R_EX_ac_e: -10` provides *acetate* to the communities). The medium with id
    `base_medium` will be added to all media.
* --strain
  * Indicates the focal STRAIN model id. If no strain is provided, `misosoup`
    computes minimal communities.

## Additional arguments

`misosoup` can be used with the additional arguments:

```bash
misosoup MODEL_PATH/*.xml --output OUTPUT_FILE --media MEDIA_FILE --strain STRAIN --parsimony --community-size COMMUNITY_SIZE --minimal-growth MINIMAL_GROWTH --exchange-format EXCHANGE_FORMAT --validate --log LOG
```

* --parsimony
  * If this flag is used the algorithm will return the solution that minimizes
    the total flux. This does not affect the community members but can alter
    what each member consumes and secretes.
* --community-size
  * Look for communities up to size COMMUNITY_SIZE, then stop.
* --minimal-growth
  * Set the MINIMAL_GROWTH rate of strains. Every strain that makes up a
    community needs to satisfy this minimal growth constraint. The default
    growth rate used is 0.01 (1/h).

For further description:

```bash
misosoup --help
```

## Output file

The .yaml output file will give:

* The community members: `y_<STRAIN_NAME>: 1.0`.
* The growth of each community member `Growth_<STRAIN_NAME>`.
* The total community growth `community_growth`.
* The flux at which metabolites are taken up or secreted to the medium. Negative
  and positive fluxes indicate consumption and secretion, respectively. This
  consumption/secretion pattern is given for:
  * The community as a whole: (`R_EX_<ID>_e`)
  * Each community member separately (`R_EX_<ID>_<STRAIN_NAME>_i`).  

## Example

```bash
cd example
```

The following code will run `misosoup` to find minimal supplying communities for
A1R12 in a medium that contains acetate as carbon source:

```bash
misosoup ./strains/*.xml --output ./example_output.yaml --media medium_MBM_no_co2_hco3.yaml --strain A1R12 --parsimony 
```

In the example, we run `misosoup` to find minimal supplying communities that
would allow growth of A1R12 in MBM with acetate (ac) as the sole source of
carbon. Looking at the output of the simulation (example_output.yaml) you'll see
that `misosoup` found two alternative supplying communities:

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

Add here some information for developers on how the repo is structured or a basic description of the main scripts.
