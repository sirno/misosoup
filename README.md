# MiSoS(oup)

## Install MiSoS(soup)

```bash
git clone git@github.com:sirno/misosoup.git
cd misosoup
git submodule init
pip install libs/reframed
pip install gurobipy
pip install .
```

If you are unable to install `gurobipy`, you may need to have a look at the
cluster support page of the `gurobi` module.

## Usage

```bash
misosoup --help
```
