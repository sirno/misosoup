# MiSoS(oup)

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
