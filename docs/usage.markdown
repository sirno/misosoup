# Usage

After installation, detailed usage instructions can be found with:

```bash
misosoup -h
```

To use `misosoup` with its default settings, you can use the following command:

```bash
misosoup MODEL_PATH/*.xml --output OUTPUT_FILE --media MEDIA_FILE --strain STRAIN
```

## Arguments

* `MODEL_PATH`: indicates the path to the directory where the metabolic models are
  described. Strains with metabolic models included in this directory will be
  considered as potential members in the minimal communities. The models should
  be in sbml format and follow the same naming conventions (e.g. if glucose's id
  in one model is 'glc__D', the same id should be used in the other models).
* `--output`
  * Use OUTPUT_FILE for output in yaml format. If it is not given, the results
    will be printed to stdout.
* `--media`
  * Load media from MEDIA_FILE. An example file with a correct format to
    introduce a media composition can be found in `examples/`.
* `--strain`
  * Indicates the focal STRAIN model id. If no strain is provided, `misosoup`
    computes minimal communities.

## Additional arguments

`misosoup` can be used with additional arguments.

```bash
misosoup MODEL_PATH/*.xml --output OUTPUT_FILE --media MEDIA_FILE --strain STRAIN --parsimony --community-size COMMUNITY_SIZE --minimal-growth MINIMAL_GROWTH
```

* `--parsimony`
  * If this flag is used the algorithm will return the solution that minimizes
    the total flux. This does not affect the community members but can alter
    what each member consumes and secretes.
* `--community-size`
  * Instead of looking for all communities, find all communities up to size
    COMMUNITY_SIZE
* `--minimal-growth`
  * Set the MINIMAL_GROWTH rate of strains. Every strain that makes up a
    community needs to satisfy this minimal growth constraint. The default
    growth rate is 0.01 (1/h).

## Output file

As output `misosoup` will generate a yaml file with the following general
structure:

```yaml
medium:
  strain|min:
    - <Solution1>
    - <Solution2>
```

The solutions indicated above contain two entries, the first is a dictionary
with the community composition, and the second is a dictionary with the growth
rates and fluxes through exchange reactions of the respective optimized
solution. An example of an output file can be found in `examples/`.

## Example

This package includes an `example` directory containing models and media
specifications, enabling users to perform a straightforward analysis using
`misosoup`. The example demonstrates how to identify minimal microbial
communities that utilize acetate as the sole carbon source. The results of this
analysis are pre-generated and available in the directory for reference.

### Running the Example

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

### Analysis Results

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

## Workflows

`snakemake` is a useful tool to execute many experiments and gather results.
See [`misosoup` Workflow Template](https://gitlab.ethz.ch/ochsnern/misosoup_workflow_template)
on how to use it.

