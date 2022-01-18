# Changelog

## 1.1.0 --- Optimization Indifference (WIP)

- Enable gurobi logging to file
- Community feasibility test without optimization

## 1.0.0 --- Standalone Practice (Dec 23, 2021)

- Create `LayeredCommunity` subclass for `reframed.Community`
- Create `GurobiEnvSolver` subclass of `reframed.solvers.GurobiSolver`
- Remove loading bars
- Remove `tqdm` dependency
- Provide package on pypi

## 0.6.0 --- Interface Recalibration (Dec 20, 2021)

- Pass media as dictionaries
- Rework how we screen multiple carbon sources
- Command line argument `--media` added
- Command line argument `--carbon-sources` removed
- Command line argument `--base-medium` removed
- Maintenance requirements in the model are now supported

## 0.5.0 --- Operating Generalization (Dec 9, 2021)

- RESTRUCTURED PROJECT to support Windows
- Added argument to adjust objective
- Focal strain is now constraint by its binary variable

## 0.4.0 --- Documentation Expansion (May 11, 2021)

- Reaction Ids in medium need to exactly match the Ids in the models now
- Add warning if reactions Ids are not contained in the model
- Support expansion in code for large input expansion
- Minimal growth CLI argument now controls any minimal growth setting
- Always choose dual simplex method
- Add a brief description of the content of output to the `argparse` description.

## 0.3.0 --- Gut Conformity (April 29, 2021)

- Add support for biomass exchange reactions
- Add script that selects strains and populates the current directory with symbolic links
- Change the naming convention for species specific exchange reactions to `_i`
- Fix issue where target could not be an arbitrary relative path
- Fix issue with internal metabolites not being separated in some cases

## 0.2.0 --- Selective Procedures (April 19, 2021)

- Add simple solution validation `taste_soup`
- Add simple solution filter `filter_soup`
- Add unit and integration tests for new scripts.

## 0.1.0 --- Community Emergence (April 17, 2021)

- Initial version of MiSoS(oup)
