# MiSoS(oup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

```bash
misosoup --help
```

## Workflows

`snakemake` is a useful tool to execute many experiments and gather results.
See [MiSoS(oup) Workflow Template](https://gitlab.ethz.ch/ochsnern/misosoup_workflow_template)
on how to use it.
