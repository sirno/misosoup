# MiSoS(oup)


[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/misosoup.svg)](https://badge.fury.io/py/misosoup)

Minimal Supplying Community Search (`misosoup`) is a command line tool that
searches for minimal microbial communities --- where every member is required
for the community to persist in a medium. `misosoup` can be used for two major
objectives: (1) Find minimal communities in a given medium or (2) Find minimal
_supplying_ communities in a medium; where every member is required for growth
of a strain / species of interest (focal strain).

As input `misosoup` takes a set of genome-scale metabolic models; one for each
strain / species that will be considered as potential community member. The tool
will then execute a series of constraint-based optimizations to find minimal
communities. For the computation of the solutions it is assumed a metabolic steady-state 
 (as in Flux Balance Analysis) but no optimization criteria are required (although
 can be optionally applied). Once computed, community members, their
respective growth rates and there metabolic consumption and secretion will be
reported in a human-readable and parseable format.

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

`misosoup` requires a version of Python >3.7 and <3.10 (it will be compatible with 3.10 soon).

The latest stable version of `misosoup` is available through `pip` and hence it can easily installed executing:

```bash
pip install misosoup
```

### Dependencies

* `misosoup` uses the `Guroby` optimizer that is free for academic use but it
  requires a license.
* Academic licenses can be obtained on the
  [gurobi license page](https://www.gurobi.com/academia/academic-program-and-licenses/)
* To retrieve a license, the `grbgetkey` command is needed. The command is not
  provided with `gurobipy` when installed through pip. Please download the full
  gurobi version on their website and install gurobi with their installer.

### Notes

* If you are unable to install `gurobipy`, it may need to be installed manually
e.g. on a hpc cluster, to make use of the local gurobi installation. In such
a case please refer to the instructions on the cluster support page.

 * If `misosoup` requirements are not those of your local installation, you may consider installing it within a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html). Once you have `anaconda` installed in your computer you create an environment:
 
```bash
conda create --name misosoup --channel gurobi python=3.9 gurobi
```
 then you activate it:
 
```bash
conda activate misosoup
``` 

and finally you can install `misosoup` within that environment.  
 
```bash
pip install misosoup
```

By default, `pip` installation comes with a free-trial license. Once you obtain your academic license, you want to substitute the free license with the academic one. Search in the anaconda environment the license file:

```bash
find $path_misosoup_environment -iname '*gurobi.lic'
```

Which will return the $path_free_license. Now simply overwrite the free license by the academic one:

```bash
cp $path_academic_license $path_free_license
```

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
    `R_EX_ac_e: -10` provides _acetate_ to the communities). The medium with id
    `base_medium` will be added to all media.
* --strain
  * Indicates the focal STRAIN model id. If no strain is provided, `misosoup`
    computes minimal communities.

## Additional arguments

`misosoup` can be used with the additional arguments:

```bash
misosoup MODEL_PATH/*.xml --output OUTPUT_FILE --media MEDIA_FILE --strain STRAIN --parsimony --community-size COMMUNITY_SIZE --minimal-growth MINIMAL_GROWTH --exchange-format EXCHANGE_FORMAT --validate --log LOG
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
misosoup ./strains/*.xml --output ./output_example.yaml --media media_mbm_no_co2_hco3.yaml --strain A1R12 --parsimony
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

