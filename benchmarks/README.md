# Benchmarks: pure Ludwig vs pure scikit-learn

Reference experiments that run each framework on its own (no Hamelin),
to compare against the results obtained through the app.

| File | What it does |
|---|---|
| `ludwig/ludwig_experiment.ipynb` | Ludwig AutoML (`auto_train`) on a list of OpenML tasks |
| `sklearn/sklearn_experiment.ipynb` | scikit-learn pipelines + `RandomizedSearchCV` on the same tasks |
| `requirements.txt` | Pinned dependency versions |
| `compare_variants.py` | Fold-by-fold comparison of the Ludwig variants against `default` and sklearn |
| `common_utils.py` | Shared helpers imported by both notebooks (OpenML split download, `save_incremental_results`, ...) |

## Reproducibility

Exact versions are pinned in `requirements.txt` (Python 3.12). Create a
clean environment and select it as the notebook kernel:

    uv venv --python 3.12 .venv-bench
    uv pip install --python .venv-bench/bin/python -r requirements.txt

`TEST_MODE` in `common_utils.py` must be `False` for the full experiment
(14 tasks, every OpenML fold); `True` runs one task and one fold as a
smoke test. Seeds are fixed in `SEEDS` (one per fold).

## Data

Datasets are downloaded from OpenML by task id (`openml.tasks.get_task`),
so there is no local `data/` folder. OpenML caches them under `~/.openml`.

## Run modes

Set in `common_utils.py` (at most one of the first two):

| Mode | What it runs | Time limit |
|---|---|---|
| `TEST_MODE = True` | `TEST_TASK_ID` (37, diabetes), fold 0 only | 300 s |
| `SINGLE_TASK_MODE = True` | same task as the smoke test (`SINGLE_TASK_ID = TEST_TASK_ID`), all 10 folds | 1000 s |
| both `False` | all 14 tasks, all folds | 1000 s |

## Ludwig variants

`LUDWIG_VARIANT` in `ludwig/ludwig_experiment.ipynb`:

- `default` – plain `auto_train` (for tabular data Ludwig 0.17.9 selects the
  `ft_transformer` combiner by itself).
- `ple` – default + piecewise-linear encoder for number features.
- `concat` – default but with the lightweight concat (MLP) combiner.

Ludwig is limited to 2 concurrent trials (`LUDWIG_MAX_CONCURRENT_TRIALS`, or
`run_screening.py --trials N`): with 3, Ray killed trials for lack of memory on an
8 GB machine. Results obtained with different trial counts are not comparable, so
keep it fixed across all variants.

## Cheap screening of the Ludwig variants

In `common_utils.py` set `TEST_MODE = False`, `SINGLE_TASK_MODE = True`,
`MAX_FOLDS = 3` and `TIME_LIMIT_OVERRIDE_S = 300`. Run `sklearn_experiment.ipynb`
once and `ludwig_experiment.ipynb` once per `LUDWIG_VARIANT`. Results go to
`.../results/single_task_3f_300s/`. Then, from `benchmarks/`:

    python compare_variants.py

It pairs the runs by fold and compares every variant against `default` and
against sklearn. With fewer than 6 folds the Wilcoxon p-value is not reported
(it cannot reach 0.05), so the screening only tells which variants are worth
a full 10-fold run (`MAX_FOLDS = None`).

## How to read the results

**Per run** (`task_<id>_<tool>_all_runs.csv`): one row per fold with the metrics
and `time_taken` (seconds, training + evaluation). For classification the metrics
are `roc_auc` and `accuracy` (for Ludwig use `accuracy_micro`, which is the plain
fraction of correct predictions; Ludwig's own `accuracy` is a different quantity).
For regression: `root_mean_squared_error`, `mean_absolute_error`, `mean_squared_error`, `r2`.
`summary_<tool>.csv` has mean and std per task.

**Comparing variants** (`python compare_variants.py`): everything is paired by fold
and measured against Ludwig `default`. Sklearn is the reference, not a candidate.

| Column | Meaning |
|---|---|
| `diff_vs_default` | Mean paired difference; **> 0 = better** than default (already sign-corrected for RMSE) |
| `folds_better` | In how many folds the variant beat default |
| `p_wilcoxon` | Empty with fewer than 6 informative folds: it cannot reach 0.05 |
| `time_vs_default` | Cost: 2.0 means twice as slow as default |
| `verdict` | Rule fixed before looking at the data, see below |

Verdict rule (decided beforehand, so it is not tuned to the results):

- **DISCARD**: worse than default by more than 10 % in *every* paired fold (at least 2).
- **PROMISING**: better than default in *every* paired fold (at least 3).
- **UNCLEAR**: anything else. It does not mean "no effect", only "not enough evidence".

**Things to keep in mind**

- Ludwig is not deterministic even with a fixed seed (it stops by time and runs
  trials in parallel). Two identical `default` runs on diabetes fold 0 gave AUC
  0.767 and 0.849. Never judge a variant on one run.
- Ludwig runs ~100 s longer than its time limit; sklearn usually ends far
  earlier because it exhausts its small search space.
- Ludwig here is limited to CPU and 3 concurrent trials (8 GB machine), which
  caps how many configurations it can try in the time limit.
- A screening with 3 folds can only find large effects. A "PROMISING" variant
  must be confirmed with all 10 folds (`MAX_FOLDS = None`) before claiming anything.

## Outputs (not versioned)

Each notebook lives in its own folder and writes next to it, one subfolder per run mode:

- `ludwig/results/<mode>/<variant>/` – per-task `task_<id>_ludwig_all_runs.csv`,
  `summary_ludwig.csv` and `ludwig_inferred_feature_types.json`
- `sklearn/results/<mode>/` – per-task `task_<id>_sklearn_all_runs.csv` and `summary_sklearn.csv`

Both are in `.gitignore`. To keep a light summary for the paper, copy it
elsewhere (e.g. `experimento/`) or un-ignore that specific file.

## Before committing

Clear notebook outputs:

    jupyter nbconvert --clear-output --inplace */*.ipynb
