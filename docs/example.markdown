# Example

This package includes an `example` directory containing models and media
specifications, enabling users to perform a straightforward analysis using
`misosoup`. The example demonstrates how to identify minimal microbial
communities that utilize acetate as the sole carbon source. The results of this
analysis are pre-generated and available in the directory for reference.

## Running the Example

To execute the analysis, navigate to the `example` directory and use the
following command:

```bash
cd example/marine/
misosoup ./strains/*.xml --output ./output.yaml --media media.yaml --strain A1R12 --media-select ac
```

This command instructs `misosoup` to analyze the specified microbial strains
for their ability to support the growth of strain
[A1R12](https://biocyc.org/A1R12/organism-summary) in a Minimal Basal Medium
(MBM) with acetate (ac) as the exclusive carbon source.

## Analysis Results

The simulation results, detailed in `output.yaml`, reveal two potential
microbial communities capable of supporting A1R12 growth:

- **Solution 1:** Community comprising A1R12 and I2R16, indicating a symbiotic
  relationship sufficient for growth on acetate.
- **Solution 2:** Community comprising A1R12 and I3M07. Detailed analysis of
  this community shows:
  - Both strains produce carbon dioxide as a by-product, with strain-specific
    CO2 fluxes of `R_EX_co2_e_A1R12_i: 0.564` for A1R12 and
    `R_EX_co2_e_I3M07_i: 0.1312` for I3M07.
  - The total community-level carbon dioxide production is quantified by the
    flux `R_EX_co2_e: 1.695`, highlighting the combined metabolic activity.

These solutions showcase `misosoup`'s ability to predict minimal microbial
communities based on specific metabolic requirements, facilitating targeted
research and application in microbial ecology and synthetic biology.


