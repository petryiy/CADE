# Frozen pilot inputs

The numerical inputs derive from the public Stereo-seq dataset GSE274447:

- Study: Shen et al. (2026), *Spatial perturb-seq: single-cell functional genomics within intact tissue architecture*, Nature Communications 17:3018. https://doi.org/10.1038/s41467-026-69677-6
- Repository: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274447
- Original analysis: https://github.com/kimberle9/spatialperturbseq

The two `.npz` files contain only the fixed pilot required for this paper. Load them with `numpy.load(..., allow_pickle=False)`.

| Array | Meaning |
|---|---|
| `Y` | Raw counts, ordered Vps35l, Dock10, Gpr37, Sparc |
| `N` | Intercept, pooled near/far exposure, density at 50/100 micrometres |
| `S` | Eight bounded source exposures |
| `counts_near`, `counts_far` | Four target-specific integer counts in (20,50] and (50,100] micrometre rings |
| `blocks`, `index` | Frozen evaluation block and receiver identifiers |
| `xy`, `component` | Receiver coordinates in micrometres and disconnected coordinate component |
| `B2`, `B3`, corresponding `_columns` | Original prepared feature tables for exact generator reconstruction |
| `permutation_counts` | 99 precomputed restricted-label source-count designs, stored losslessly as uint8 |

Source order: `clu`, `fasn`, `stk39`, `oligo2`; near then far for each target. `oligo2` preserves the author-provided barcode label. For all bounded features, the transform is `count / (1 + count)`.

Permutation IDs 1–49 are the calibration reference; 50–99 are the evaluation set. Labels were restricted within chip, connected coordinate component, 500 micrometre block and barcode-count strata. Permuted counts include the spatial exposure consequence of those frozen relabelings. The arrays are sufficient to reproduce the evaluated fits; they do not regenerate a new set of permutations from the complete original cell matrices.

`preparation_audit.json` records pilot hashes, geometry and receiver preparation. `source_preparation_manifest.json` records the original source-object hashes. Native coordinates use the recorded 0.5 micrometre pitch conversion; the source RDS object has no resolution attribute. The manuscript supplement gives the selection criteria. Inputs include public mouse data, not human clinical records. Cite the source study when using these derived inputs. Source-data rights and the code license are separate; no new license is asserted over the original data.

## Additional compact inputs

`locked/C02943C3.npz` and `locked/A03599E2.npz` contain the prespecified held-out readouts and exposure designs used by the external comparison. Their selection and preparation are recorded in `protocols/external/locked_protocol.json` and `protocols/external/native_preparation.json`.

`followup/B03018A2.npz` contains 49,243 eligible receivers from the previously unused GSE274447 specimen GSM9659883. It includes source positions and labels, the two fixed readout panels, spatial components and block identifiers. The frozen support rules and readout lists are in `protocols/followup/protocol.json`; the original input hash is in `protocols/followup/native_preparation.json`.

The bundled inputs support all native fits and restricted-label randomizations. For optional raw reconstruction, use the public GEF URL in the follow-up protocol and run `python run.py followup-prepare --input-gef /absolute/path/GSM9659883_B03018A2.adjusted.cellbin.gef`.
