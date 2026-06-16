---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

# misosoup

[![Github repo](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/sirno/misosoup)
[![PyPI version](https://badge.fury.io/py/misosoup.svg)](https://badge.fury.io/py/misosoup)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Minimal Supplying Community Search (`misosoup`) is a command line tool
designed to search for minimal microbial communities, wherein every member is
essential for the community's persistence within a given medium. Its primary
functions include:

- Identifying minimal communities within a specified medium.
- Identifying minimal "supplying" communities within a medium, where each
  member is necessary for the growth of a focal strain or species of interest.

To utilize `misosoup`, users provide a set of genome-scale metabolic models,
each representing a potential member of the community. The program then employs
constraint-based optimizations to determine minimal communities. These
optimizations assume a metabolic steady-state, akin to Flux Balance Analysis.

Once computations are complete, `misosoup` outputs information about community
members, their respective growth rates, as well as their metabolic consumptions
and secretions, presented in a format both readable by humans and parseable by
software.

## Details

To find minimal microbial communities `misosoup` solves a repeated sequence of
optimization problems using MILP formulations:

1. Minimize the number of community member (see Zelezniak, et al. PNAS
   doi:10.1073/pnas.1421834112).
2. Fix the active community members and check the feasibility of the entire community.
3. Optionally: Maximize community biomass (sum of individual growth rates).
4. Optionally: Perform an optimization to reflect parsimonious enzyme usage
   (see Lewis, et al. Mol Syst Bio doi:10.1038/msb.2010.47).

## Citation

If you use misosoup, please cite our paper.

## Development

Any contributions are welcome.

