# CADE

**Coupled Adaptive Double-branch Estimation of correlated neighborhood effects**

Ruiqi Zhang · UNSW Sydney

CADE estimates the contribution of nearby perturbation sources to sparse expression readouts. It fits detection and positive-expression branches, projects out measured background features, and averages sparse source supports using a coupled Gaussian score likelihood. The two branches are combined on the expression scale.

## Quick start

The reference environment is Python 3.13. The implementation runs on CPU.

```bash
git clone https://github.com/petryiy/CADE.git
cd CADE
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py demo
python run.py check
```

The demo trains on the bundled C02943C3 pilot and predicts the A03599E2 pilot. Tests check frozen score examples, direct coefficient-to-prediction replay, input constraints and native spatial feature reconstruction.

All scientific definitions live in **[CADE.ipynb](CADE.ipynb)**. The notebook has no saved outputs. Open it in Jupyter or a notebook editor and run the definition cells; the fitting example is opt-in. `run.py` loads these same definitions.

## Python interface

```python
from run import load_core

cade = load_core()
chips, outcomes = cade['load_pilot']('.')
d = cade['make_design'](chips['C02943C3'], chips['A03599E2'])
fit = cade['fit_cade'](
    d['Z'][:, :5], d['Z'][:, 5:], outcomes['C02943C3'], d['blocks'],
    predict_N=d['T'][:, :5], predict_S=d['T'][:, 5:],
)
prediction = fit['observed_prediction']
source_contrast = prediction - fit['observed_zero_prediction']
```

- `N`: five background columns, including an intercept.
- `S`: eight identity-specific neighborhood exposures bounded in `[0, 1]`.
- `Y`: four nonnegative expression readouts.
- `blocks`: spatial block identifiers used for weighting.

The source contrast sets `S` to zero while holding `N` fixed. `screen=True` enables the optional branch-level evidence screen. The evaluated implementation uses eight source columns; exact support enumeration costs exponentially more as the source panel grows.

## Reproduce experiments

The compact public-data inputs and predefined protocols are bundled. Full runs can take hours; their outputs are ignored by Git.

```bash
python run.py normal
python run.py spatial
python run.py permutations
```

For a short execution check, use `python run.py normal --replicates 1` or `python run.py spatial --replicates 1 --limit 1`. These reduced runs do not reproduce the full benchmark. Pilot runs save results under `reruns/`.

The official SuSiE comparator requires R and `susieR` 0.14.2:

```bash
Rscript restore_R.R
python run.py external-normal
python run.py external-spatial
python run.py external-native
python run.py followup-normal
python run.py followup-spatial
python run.py followup-native
python run.py followup-randomization
python run.py followup-components
```

The external and follow-up runs save results under `results/external/` and `results/followup/`. They resume completed case keys. Run `followup-native` before `followup-randomization`. Normal and spatial tasks support `--shard i --shards n`; keep `n` fixed within a run. Use `CADE_R_LIBRARY` to select an existing R library.

## Repository contents

| Path | Purpose |
|---|---|
| `CADE.ipynb` | Estimator, controls, spatial generators and evaluation routines |
| `run.py` | Command-line entry point |
| `data/` | Compact pilot, locked readout and held-out specimen inputs |
| `protocols/` | Fixed experiment settings, preparation records and R environment |
| `tests/` | Numerical checks and a small frozen reference |

The repository contains the executable research implementation. Paper drafts, old versions, HTML reports and large prediction caches are kept outside this source release. The model definitions match the retained research implementation.

## Data and citation

Inputs derive from the public mouse Spatial perturb-seq dataset [GSE274447](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274447). See [data/README.md](data/README.md) for array definitions and provenance. Source-data rights and dependency licences remain separate from the software.

- Shen et al. (2026). *Spatial perturb-seq: single-cell functional genomics within intact tissue architecture*. [DOI: 10.1038/s41467-026-69677-6](https://doi.org/10.1038/s41467-026-69677-6).
- Wang et al. (2020). *A simple new approach to variable selection in regression, with application to genetic fine mapping*. [DOI: 10.1111/rssb.12388](https://doi.org/10.1111/rssb.12388).

Software citation metadata are in [CITATION.cff](CITATION.cff). Dependency attribution and the current licensing status are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

CADE source code is available under the [MIT License](LICENSE). Copyright (c) 2026 Ruiqi Zhang. Public source data and third-party dependencies retain their original rights and licences.
