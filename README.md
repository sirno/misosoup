# MiSoS(oup)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Install MiSoS(soup)

```bash
git clone git@github.com:sirno/misosoup.git
cd misosoup
git submodule init
git submodule update
pip install libs/reframed
pip install -i https://pypi.gurobi.com gurobipy
pip install .
```

If you are unable to install `gurobipy`, you may need to have a look at the
cluster support page of the `gurobi` module.

For testing and developement:

```bash
git clone git@github.com:sirno/misosoup.git
cd misosoup
git submodule init
git submodule update
pip install libs/reframed
pip install -i https://pypi.gurobi.com gurobipy
pip install -e .[dev]
```

Make sure you have `docker` installed and run tests with `pytest tests`.

## Usage

```bash
misosoup --help
```

## Workflows

`snakemake` is a useful tool to execute many experiments and gather results. In
`./workflows` you can find a workflow to execute `misosoup`. It can be
configured in `workflows/config.yaml`. With our test data (not part of this
repository), the workflow can be used as followed:

```bash
cd workflows
snakemake -j1 gather
```

For cluster execution refer to [https://snakemake.readthedocs.io/en/stable/executing/cluster.html](https://snakemake.readthedocs.io/en/stable/executing/cluster.html)
and consider installing a profile, e.g. for LSF [https://github.com/Snakemake-Profiles/lsf](https://github.com/Snakemake-Profiles/lsf)
