# Changelog

## 2.3.1 --- Minority Complex (Jul 02, 2025)

- Restructure example description and organization
- Add auxotroph example
- Fix issue with output in same directory

## 2.3.0 --- Multiplexing Catharsis (Feb 07, 2024)

- Fix selected community not being reported
- REVERT: `check_feasibility` is no longer used to assess feasibility
- REVERT: Execution and reporting of multiple optimization targets
- Only one optimization target will be assessed and reported
- Upgrade `reframed`

## 2.2.0 --- Consistency Crisis (Feb 21, 2023)

- Use a separate environment for the MILP and the LPs
- Fix incorrect addition of knowledge constraints when optimizations fail

## 2.1.3 --- Reporting Madness (Feb 3, 2023)

- Log community members when community solution is stored
- Missing reaction warnings will be sorted
- Setup custom environment for solver

## 2.1.0 --- Transparency Dilemma (Sep 6, 2022)

- Report feasible communities if optimization fails
- Report which optimizations succeeded
- Report if parsimony variables are set
- Fix missing `check_feasibility` method.

## 2.0.0 --- Numerical Exercise (Sep 2, 2022)

- Build new community models candidate solutions for verification

## 1.3.1 --- Speedup Inclination (Sep 1, 2022)

- Use yaml C loader and dumper

## 1.3.0 --- Linearization Effort (Aug 18, 2022)

- Linear parsimony optimization

## 1.2.1 --- Reporting Bias (NONE)

- Report feasible communities, even if optimization fails
- Add function to get `supplier` and `community` frozensets.
- Update crossfeed to report as frozensets.
- Add functions to gather statistics.

## 1.2.0 --- Caching Interference (Mar 1, 2022)

- Add argument `--media-select` to choose subset of media
- Add argument `--cache-file` to cache intermediate constraints
- Add module `misosoup.library.minimizer`.
- Changed minimization to use state-aware minimizer class
- Removed module `misosoup.library.solve`
- Removed module `misosoup.library.load`

## 1.1.0 --- Optimization Indifference (Feb 3, 2022)

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
