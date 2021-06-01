# MiSoS(oup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

MInimal Supplying cOmmunity Search (MiSoS(oup)) is a python-based command line tool that implements a series of constraint-based metabolic methods to search for minimal microbial communities - communities in which every member is required for the community to persist. MiSoS(oup) can be used with two objectives: 1- to find minimal communities in a given medium and 2 - to find minimal supplying communities which are the minimal communities required for growth of a strain (or species) of interest, that we refer to as the focal strain.

The input to MiSoS(oup) is a set of genome-scale metabolic models, corresponding to the strains (species) that will be considered as focal strains or potential community members. To find minimal communities, MiSoS(oup) implements a series of constraint-based metabolic methods in which metabolic steady-state is assumed (as in Flux Balance Analysis). The output of MiSoS(oup) is a human readable yaml file that returns all minimal communities with a detail of the community members, their growth rate and their metabolic consumptions and secresions. 

Specifically, to find a minimal community, MiSoS(oup) first minimizes the number of community members. For this optimization step MiSoS(oup) uses the simplex method in `gurobi` (optimization solver). In a second step, MiSoS(oup) maximizes the total community biomass. As a result of these two optimization steps one gets a community which is minimal and in which the consumption/secretion pattern of each community member reflects what is required for optimal community growth. In addition, MiSoS(oup) can be set to perform a third optimization to reflect parsimoneous enzyme usage (see Lewis, et al. Mol Syst Bio doi:10.1038/msb.2010.47). When this third optimization is done, the consumption/secretion pattern of each community member in the minimal community, will be one that allows maximal (community or focal strain) growth while minimizing the total flux through the system.

## Install MiSoS(soup)

```bash
git clone git@gitlab.ethz.ch:ochsnern/misosoup.git
cd misosoup
pip install .
```

If you are unable to install `gurobipy`, it may need to be installed manually
e.g. on a hpc cluster, to make use of the local gurobi installation. In such 
a case please refer to the instructions on the cluster support page. 

For testing and developement:

```bash
git clone git@gitlab.ethz.ch:ochsnern/misosoup.git
cd misosoup
pip install -e .[dev]
```

Run tests with `tox`. You will need our test data to pass.

## Usage
After installation, you can easily use MiSoS(oup) with:
```bash
misosoup PATH_TO_MODELS/*.xml --output OUTPUT --base-medium BASE_MEDIUM --carbon-sources CARBON_SOURCES --strain STRAIN
```
PATH_TO_MODELS: indicate the path to the directory where the strains' metabolic models are found. Strains with metabolic models included in this directory will be considered as potential members in the minimal communities. The models should be in xml format and follow the same naming conventions (e.g. if glucose's id in one model is 'glc__D', the same id should be used in the  other models). 
--output OUTPUT: output file name in yaml format. If it is not given, the results will be printed to stdout.
--base-medium BASE_MEDIUM: path to the yaml file with the detailed description of the growth medium. The file requires a list with those metabolites found in the medium. These should be introduced using the ids of the exchange reactions, as they appear in the strains' metabolic models, e.g. 'R_EX_h_e'. (We suggest looking at the reaction ids of the model in a browser since tools such us cobrapy might change the naming.) All metabolites listed in BASE_MEDIUM can be consumed in unlimited amounts. 
--carbon-sources CARBON_SOURCES: list of carbon sources to include in the medium. Introduce the metabolite id, as it appears in the strains' genome-scale metabolic models (e.g. 'ac'). The community's carbon source consumption is limitted to 10 mmol gDW-1 h-1. @Nico, I think here it would be best if the user entered the exchange reaction of the carbon source.
--strain STRAIN: Focal strain model id. If no strain is provided, `misosoup` computes minimal communities.

MiSoS(oup) can be used with the additional arguments:

```bash
misosoup PATH_TO_MODELS/*.xml --output OUTPUT --base-medium BASE_MEDIUM --carbon-sources CARBON_SOURCES --strain STRAIN --parsimony --community-size COMMUNITY_SIZE --minimal-growth MINIMAL_GROWTH --exchange-format EXCHANGE_FORMAT --validate --log LOG
```
--parsimony: will return the solution that minimizes total flux. This does not affect the community members but can alter what each member consumes and secretes. 
--community-size COMMUNITY_SIZE: @Nico, is this the maximum number of strains to be part of a community or the number of alternative solutions? I thought it was the later, but the name COMMUNITY_SIZE makes me think it's about the number of strains found in each community.
--minimal-growth MINIMAL_GROWTH: minimal growth rate of strains. Every strain that makes up a community needs to satisfy this minimal growth constraint. The default growth rate used is 0.01 (1/h).

For further description:
```bash
misosoup --help
```

## Example
```
cd example
```
The following code will run `misosoup` to find minimal supplying communities for A1R12 in a medium that contains acetate as carbon source:
```bash
misosoup ./strains/*.xml --output ./OUTPUT_example.yaml --base-medium medium_MBM_no_co2_hco3.yaml --carbon-sources ac --strain A1R12 --parsimony 
```

## Output file
The .yaml output file will give the community members ```y_STRAIN-NAME: 1.0```, the growth of each community member ```Growth_STRAIN-NAME``` and the total community growth ```community_growth```. In addition, the output file will include the flux at which metabolites are taken up or secreted to the medium. This consumption/secretion pattern is given for the community as a whole (```R_EX-ID```) as well as for each community member separately (```R_EX-ID_STRAIN-NAME_i```). Negative and positive fluxes indicate consumption and secretion respectively.  

In the example, we run `misosoup`  to find minimal supplying communities that would allow growth of A1R12 in MBM with acetate (ac) as the sole source of carbon. Looking at the output of the simulation (OUTPUT_example.yaml) you'll see that `misosoup` found two alternative supplying communities - A1R12 can grow in MBM with acetate as carbon source when in the precense of I3M07 or I2R16. When looking at the community made up of A1R12 and I3M07 in more detail we can see that, for example, both strains produce carbon dioxide (see the community carbon dioxide flux `R_EX_co2_e: 1.699252325510545` and the strain specific carbon dioxide flux `R_EX_co2_e_A1R12_i: 0.7423145314936204` and `R_EX_co2_e_I3M07_i: 0.9569377940169246`). We can also see that the strains engage in cross-feeding interactions. For example, I3M07 produces arginine (`R_EX_arg__L_e_I3M07_i: 0.0028645059229462128`) that A1R12 consumes (`R_EX_arg__L_e_A1R12_i: -0.0028645059229462128`).

## Citation

If you use misosoup, please cite X.

## Workflows

`snakemake` is a useful tool to execute many experiments and gather results.
See [MiSoS(oup) Workflow Template](https://gitlab.ethz.ch/ochsnern/misosoup_workflow_template)
on how to use it.
