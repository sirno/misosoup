# MiSoS(oup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Install MiSoS(soup)

```bash
git clone git@gitlab.ethz.ch:ochsnern/misosoup.git
cd misosoup
pip install -i https://pypi.gurobi.com gurobipy
pip install .
```

If you are unable to install `gurobipy`, you may need to have a look at the
cluster support page of the `gurobi` module.

For testing and developement:

```bash
git clone git@gitlab.ethz.ch:ochsnern/misosoup.git
cd misosoup
pip install -i https://pypi.gurobi.com gurobipy
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
