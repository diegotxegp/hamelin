# Benchmarks: Ludwig AutoML vs scikit-learn

Two notebooks that run Ludwig AutoML and scikit-learn on the same OpenML
tasks, folds and seeds, and record metrics and training time.

| File | What it does |
|---|---|
| `ludwig/ludwig_experiment.ipynb` | Ludwig AutoML (`auto_train`, default configuration) on a list of OpenML tasks |
| `sklearn/sklearn_experiment.ipynb` | scikit-learn pipelines + `RandomizedSearchCV` on the same tasks |
| `common_utils.py` | Shared helpers imported by both notebooks (OpenML split download, resume, environment info, ...) |
| `run_benchmark.sh` | Runs everything unattended (Ludwig, scikit-learn, analysis); resumable |
| `analyze_results.py` | Statistics, paper tables and the dataset table (trains nothing) |
| `requirements.txt` | Pinned dependency versions |

## Quick start (fresh clone)

From the repository root:

    cd benchmarks
    uv venv --python 3.12 .venv-bench
    uv pip install --python .venv-bench/bin/python -r requirements.txt
    .venv-bench/bin/python -m ipykernel install --user --name ludwig-bench
    .venv-bench/bin/jupyter lab

Open each notebook and select the `ludwig-bench` kernel (the notebooks must
be run with their own folder as working directory). Exact versions are pinned in
`requirements.txt` (Python 3.12). If the default `torch` wheel does not match
the machine's GPU/CUDA, install the right build before the rest. The
notebooks fall back to CPU when the GPU is not supported by that build.

Run the smoke test first (`TEST_MODE = True`, the default): it takes about
7 minutes for both notebooks and confirms the environment works.

### Full experiment, unattended

    mkdir -p logs && nohup ./run_benchmark.sh > logs/launcher.log 2>&1 &    # or inside tmux/screen

`run_benchmark.sh` runs Ludwig, then scikit-learn, then the analysis, and writes
live logs to `logs/`. `./run_benchmark.sh ludwig` (or `sklearn`) runs only one
tool; `PYTHON=/path/to/python` selects the interpreter (default
`.venv-bench/bin/python`); `BENCH_TEST_MODE=1 ./run_benchmark.sh` is the smoke
test. A second pass retries the runs that failed in the first one
(`BENCH_PASSES=1` disables it).

The Ludwig experiment is 14 tasks x 10 folds x up to 1000 s (plus the ~100 s
Ludwig overshoots), roughly 42 h on a machine like the one in
`environment_ludwig.json`; scikit-learn usually takes far less (it stops when
its small search space is exhausted, 28 s on diabetes). If anything interrupts
it (Ctrl+C, reboot, crash), **launch the same command again**: runs already
saved in the CSVs are skipped (`BENCH_RESUME=0` starts over and overwrites
them). Do not start two launches at once; the script refuses.

Running the notebooks by hand also works: open each one and *Run All* (no cell
needs to be run by hand). From the command line, `jupyter nbconvert` needs the
cell timeout disabled, because one cell runs for hours:

    cd ludwig && jupyter nbconvert --to notebook --execute --inplace \
        --ExecutePreprocessor.timeout=-1 ludwig_experiment.ipynb

`run_benchmark.sh` avoids this by running the notebooks as scripts.

## Reproducibility

Protocol: the 10 official OpenML folds of each task, fold *i* run with seed
`SEEDS[i]`, 1000 s per run, and mean and standard deviation over the 10 runs.
Both notebooks share the task list, the folds and the seeds through
`common_utils.py`, so their results are directly comparable. The standard
deviation mixes the data-split and the seed variability (they are paired). Ludwig itself is not fully deterministic even with a
fixed seed (it stops by time and runs trials in parallel), so small
differences between repeated runs are expected.

## Data

Datasets are downloaded from OpenML by task id (`openml.tasks.get_task`),
so there is no local `data/` folder. OpenML caches them under `~/.openml`.

## Run modes

Set in `common_utils.py`; at most one of the first two can be `True`:

| Mode | What it runs | Time limit |
|---|---|---|
| `TEST_MODE = True` | `TEST_TASK_ID` (37, diabetes), fold 0 only (smoke test) | 300 s |
| `SINGLE_TASK_MODE = True` | same task, all 10 folds | 1000 s |
| both `False` | all 14 tasks, all folds (full experiment) | 1000 s |

Set `BENCH_TEST_MODE=0` (or `TEST_MODE = False`) for the full experiment.
`MAX_FOLDS` limits the folds per task and `TIME_LIMIT_OVERRIDE_S` changes the
time limit; both can also be set with the `BENCH_MAX_FOLDS` and
`BENCH_TIME_LIMIT_S` environment variables. `BENCH_TEST_TASK_ID` picks another
task for the smoke test. Very short Ludwig limits (about 60 s) fail with
`grace_period must be <= max_t`; use at least a few minutes.

Ludwig runs with its own defaults: concurrency and device use (CPUs/GPUs) are
decided automatically, nothing is limited. Each trial is a full PyTorch
process (~1-2 GB), so make sure the machine has enough memory.

## How to read the results

`task_<id>_<tool>_all_runs.csv` has one row per fold with the metrics and
`time_taken` (seconds, training + evaluation). For classification the metrics
are `roc_auc`, `accuracy`, `balanced_accuracy` and `f1_macro` (for Ludwig use
`accuracy_micro`, which is the plain fraction of correct predictions; Ludwig's
own `accuracy` is a different quantity). Balanced accuracy and macro-F1 are
computed from the predicted labels with scikit-learn for both tools, and they
matter on imbalanced tasks, where accuracy alone is misleading. For regression: `root_mean_squared_error`, `mean_absolute_error`,
`mean_squared_error` and `r2`. `summary_<tool>.csv` has the mean and standard
deviation per task.

Ludwig runs about 100 s longer than its time limit, while scikit-learn usually
ends much earlier because it exhausts its small search space.

## Outputs (not versioned)

Each notebook writes next to itself, in one subfolder per run mode:

- `ludwig/results/<mode>/`: per-task `task_<id>_ludwig_all_runs.csv`,
  `summary_ludwig.csv`, `ludwig_inferred_feature_types.json`,
  `ludwig_run_diagnostics.json` and `environment_ludwig.json`
- `sklearn/results/<mode>/`: per-task `task_<id>_sklearn_all_runs.csv`,
  `summary_sklearn.csv` and `environment_sklearn.json`

`ludwig_run_diagnostics.json` records, per run, what Ludwig did on its own:
trials launched and failed, epochs of the best trial, model type, combiner,
trainer settings (epochs, batch size, early stopping), winning hyperparameters
and the CPUs/GPUs Ray detected. The CSV also has `train_time_s`, `n_trials` and
`n_trials_failed` for Ludwig.

`environment_<tool>.json` records the machine (CPU model, cores and frequency,
RAM, GPUs and whether they were used, CUDA build of PyTorch), library versions,
the git commit of the scripts, time limit and seeds. Quote it in the paper:
Ludwig chooses its own concurrency and devices, so its results depend on the
hardware. A resumed run writes `environment_<tool>_resumed_<date>.json` and
keeps the original.

## Analysis

After the notebooks finish (from `benchmarks/`):

    python analyze_results.py <mode>           # e.g. full_all_folds_1000s
    python analyze_results.py <mode> --no-baseline   # skip the OpenML download

It writes `analysis_<mode>/` with: `summary_table.csv/.md` (one row per task,
mean ± sd, constant-predictor baseline and time, ready for the paper),
`per_task_stats.csv` (sd, 95% CI, median, min, max), `baseline.csv`,
`time_and_failures.csv` (time used vs the limit, failed runs),
`ludwig_diagnostics.csv` (one row per run, from the diagnostics JSON) and, when the
scikit-learn results exist, `paired_tests.csv` and `across_tasks.csv`
(Wilcoxon, Holm-corrected; p-values are slightly optimistic because the
training sets of the folds overlap). Use only what the paper needs.

`python analyze_results.py --datasets` writes `datasets_summary.csv` straight
from OpenML (no results needed): instances, features (target included, as in
OpenML), numeric/categorical split, missing values, classes and the
majority-class share, which is the accuracy of the constant predictor.

## Before committing

Clear notebook outputs:

    jupyter nbconvert --clear-output --inplace */*.ipynb
