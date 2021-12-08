# MiSoS(oup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

MInimal Supplying cOmmunity Search (MiSoS(oup)) is a command line tool that
searches for minimal microbial communities. In such communities every member
is required for the community to persist.

MiSoS(oup) can be used for two objectives: (1) Find minimal communities in a
given medium or (2) Find minimal supplying communities which are the minimal
communities required for growth of a strain (or species) of interest, that we
refer to as the focal strain.

As input MiSoS(oup) takes a set of genome-scale metabolic models, one for each
strain (species) that will be considered as potential community members. The
tool will then execute a series of constraint-based optimizations to find
minimal communities. For the computation of the solutions metabolic steady-state
is assumed (as in Flux Balance Analysis). Once computed, by default community
members, their respective growth rates and there metabolic consumption and
secretion will be reported in a human-readable and parsable format.

## Details

To obtain minimal microbial communities MiSoS(oup) solves multiple optimization
problems. All optimizations problems are solved with gurobi.

1. Minimize the number of community member.
2. Fix the active community members and optimize growth of the total community
   biomass. If this fails, exclude the community from the possible solutions and
   repeat.
3. Optionally: Execute a third optimization to reflect parsimonious enzyme usage
   (see Lewis, et al. Mol Syst Bio doi:10.1038/msb.2010.47)

## Install MiSoS(soup)

```bash
git clone git@gitlab.ethz.ch:ochsnern/misosoup.git
cd misosoup
pip install .
```

If you are unable to install `gurobipy`, it may need to be installed manually
e.g. on a hpc cluster, to make use of the local gurobi installation. In such
a case please refer to the instructions on the cluster support page.

For testing and development:

```bash
git clone https://gitlab.ethz.ch/ochsnern/misosoup.git
cd misosoup
pip install -e .[dev]
```

Run tests with `tox`. You will need our test data to pass.

## Usage
After installation, you can easily use MiSoS(oup) with:

```bash
misosoup PATH_TO_MODELS/*.xml --output OUTPUT --base-medium PATH_BASE_MEDIUM --carbon-sources CARBON_SOURCES --strain STRAIN
```

## Arguments

* PATH_TO_MODELS: indicates the path to the directory where the strains' metabolic models are found. Strains with metabolic models included in this directory will be considered as potential members in the minimal communities. The models should be in xml format and follow the same naming conventions (e.g. if glucose's id in one model is 'glc__D', the same id should be used in the other models). 
* --output
    * Use OUTPUT file name in yaml format. If it is not given, the results will be printed to stdout.
* --base-medium
    * Use the path PATH_BASE_MEDIUM to the yaml file with the detailed description of the growth medium. The file requires a list with those metabolites found in the medium. These should be introduced using the ids of the exchange reactions, as they appear in the strains' metabolic models, e.g. 'R_EX_h_e'. (We suggest looking at the reaction ids of the model in a browser since tools such as cobrapy might change the naming.) All metabolites listed in PATH_BASE_MEDIUM can be consumed in unlimited amounts (see below for an example of the format).
* --carbon-sources 
    * Use the list of CARBON_SOURCES to include in the medium. Introduce the metabolite id, as it appears in the strains' genome-scale metabolic models (e.g. 'ac'). The community's carbon source consumption is limited to 10 mmol gDW-1 h-1.
* --strain 
     * Indicates the focal STRAIN model id. If no strain is provided, `misosoup` computes minimal communities.

## Additional arguments

MiSoS(oup) can be used with the additional arguments:

```bash
misosoup PATH_TO_MODELS/*.xml --output OUTPUT --base-medium PATH_BASE_MEDIUM --carbon-sources CARBON_SOURCES --strain STRAIN --parsimony --community-size COMMUNITY_SIZE --minimal-growth MINIMAL_GROWTH --exchange-format EXCHANGE_FORMAT --validate --log LOG
```
* --parsimony
    * If this flag is used the algorithm will return the solution that minimizes the total flux. This does not affect the community members but can alter what each member consumes and secretes. 
* --community-size 
    * COMMUNITY_SIZE [Description needed]
* --minimal-growth 
    * Set the MINIMAL_GROWTH rate of strains. Every strain that makes up a community needs to satisfy this minimal growth constraint. The default growth rate used is 0.01 (1/h).

For further description:
```bash
misosoup --help
```
## Output file
The .yaml output file will give:

* The community members: ```y_STRAIN-NAME: 1.0```. 
* The growth of each community member ```Growth_STRAIN-NAME```. 
* The total community growth ```community_growth```. 
* The flux at which metabolites are taken up or secreted to the medium. Negative and positive fluxes indicate consumption and secretion, respectively. This consumption/secretion pattern is given for:
     * The community as a whole: (```EX-ID```) 
     * Each community member separately (```EX-ID_STRAIN-NAME_i```).  

## Example

```
cd example
```
The following code will run `misosoup` to find minimal supplying communities for A1R12 in a medium that contains acetate as carbon source:

```bash
misosoup ./strains/*.xml --output ./OUTPUT_example.yaml --base-medium medium_MBM_no_co2_hco3.yaml --carbon-sources ac --strain A1R12 --parsimony 
```

In the example, we run `misosoup`  to find minimal supplying communities that would allow growth of A1R12 in MBM with acetate (ac) as the sole source of carbon. Looking at the output of the simulation (OUTPUT_example.yaml) you'll see that `misosoup` found two alternative supplying communities: 

 * Solution 1: A1R12 can grow when in the presence of I3M07. If we inspect this solution in more detail we can see (for example): 
    * Each strain produces carbon dioxide. We note this by looking at the strain-specific carbon dioxide fluxes: `R_EX_co2_e_A1R12_i: 0.742` and `R_EX_co2_e_I3M07_i: 0.957`.
    * The community as a whole also produces carbon dioxide, which can be seen looking at the community-level carbon dioxide flux `R_EX_co2_e: 1.699`.
 * Solution 2:  A1R12 can grow when in the presence of I2R16. A similar analysis to the one conducted for solution 1 could be followed.


## Citation

If you use misosoup, please cite X.

## Workflows

`snakemake` is a useful tool to execute many experiments and gather results.
See [MiSoS(oup) Workflow Template](https://gitlab.ethz.ch/ochsnern/misosoup_workflow_template)
on how to use it.

## Development

Add here some information for developers on how the repo is structured or a basic description of the main scripts.
