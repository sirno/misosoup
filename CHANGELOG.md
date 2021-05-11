# Changelog

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
