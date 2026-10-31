# Data and dependency attribution

The compact mouse spatial perturbation inputs derive from GSE274447 and the Spatial perturb-seq study by Shen et al. (2026), DOI: 10.1038/s41467-026-69677-6. Data provenance and preparation records are in `data/` and `protocols/`. The source data retain their original rights.

The optional correlated-regression comparator calls the unmodified official `susieR` 0.14.2 package through an R subprocess. It is not a reimplementation of SuSiE. The package environment is pinned in `protocols/external/renv.lock`; `restore_R.R` installs it from its upstream sources. See Wang et al. (2020), DOI: 10.1111/rssb.12388. All dependencies retain their respective licences.

CADE source code is released under the MIT License; see `LICENSE`. Source data and third-party dependencies retain their original rights and licences.
