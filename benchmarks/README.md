# Benchmarks: Ludwig AutoML vs scikit-learn

Two notebooks that run Ludwig AutoML and scikit-learn on the same OpenML
tasks, folds and seeds, and record metrics and training time.

| File | What it does |
|---|---|
| `ludwig/ludwig_experiment.ipynb` | Ludwig AutoML (`auto_train`, default configuration) on a list of OpenML tasks |
| `sklearn/sklearn_experiment.ipynb` | scikit-learn pipelines + `RandomizedSearchCV` on the same tasks |
| `common_utils.py` | Shared helpers imported by both notebooks (OpenML split download, resume, environment info, ...) |
| `run_benchmark.sh` | Runs everything unattended (Ludwig, scikit-learn, analysis); restarts interrupted datasets |
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

### Full experiment

**In Jupyter (the main way).** Start Jupyter with the full experiment enabled and
*Run All* in `ludwig/ludwig_experiment.ipynb` (and, if wanted, `sklearn/...`):

    BENCH_TEST_MODE=0 .venv-bench/bin/jupyter lab

(or set `TEST_MODE = False` in `common_utils.py`). No cell needs to be run by
hand. The last cell runs the analysis and shows the summary table, so the
notebook alone leaves the results and the tables ready. One cell runs for hours:
keep the browser/VS Code session and the machine awake, or use the script below.

**From a terminal, unattended (for the long run).**

    nohup ./run_benchmark.sh > /dev/null 2>&1 &     # or inside tmux/screen
    tail -f results/full_all_folds_1000s/logs/launcher.log

`run_benchmark.sh` runs the same notebooks as scripts (live logs in `results/<mode>/logs/`, no
per-cell timeout), then the analysis. `./run_benchmark.sh ludwig` (or `sklearn`)
runs only one tool; `PYTHON=/path/to/python` selects the interpreter (default
`.venv-bench/bin/python`); `BENCH_TEST_MODE=1 ./run_benchmark.sh` is the smoke
test. A second pass redoes the datasets that did not finish in the first one
(`BENCH_PASSES=1` disables it).

The Ludwig experiment is 14 tasks x 10 folds x up to 1000 s (plus the ~100 s
Ludwig overshoots), at most roughly 42 h on a machine like the one in
`environment_ludwig.json`; scikit-learn usually takes far less (it stops when
its small search space is exhausted, 28 s on diabetes).

**If anything interrupts it** (Ctrl+C, reboot, crash), launch the same command
again, or *Run All* again, with the same `BENCH_*` variables. The experiment
continues dataset by dataset: a dataset with all its runs saved is skipped,
and one that was only partly done is **discarded and restarted from fold 0**,
so every dataset comes from one uninterrupted series of runs on the same
machine. The discarded CSV is kept in `results/<mode>/<tool>/discarded/` for inspection
and ignored by the analysis. The same happens inside a launch: if one run of a
dataset fails, the dataset is started over (`BENCH_DATASET_RETRIES`, default 1)
and then the experiment goes on with the next one. A dataset that keeps
failing is reported with a `[WARN]` and costs up to twice its normal time.

**To start from scratch** (re-run everything for the same mode) use
`BENCH_RESUME=0`: the previous `results/<mode>/<tool>/` folder is moved to
`results/<mode>/<tool>.old_<timestamp>` (delete it by hand when sure) and nothing is
reused. Do not start two launches at once; the script refuses.

From the command line, `jupyter nbconvert --execute` needs the cell timeout
disabled, because one cell runs for hours:

    cd ludwig && jupyter nbconvert --to notebook --execute --inplace \
        --ExecutePreprocessor.timeout=-1 ludwig_experiment.ipynb

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

Ludwig runs about 100 s longer than its time limit (or stops earlier if its
default 10 trials finish first), while scikit-learn usually ends much earlier
because it exhausts its small search space. The tables under *Outputs* and
*Analysis* describe every file.

## Outputs (not versioned)

Temporary files: Ludwig's `hyperopt/` folder (every trial's checkpoints and logs)
is deleted before and after each run, and Ray's session files in the system
temp folder when no other Ray job is running. Results are **not** deleted
before a run, so that an interrupted experiment can continue; `BENCH_RESUME=0`
moves them aside (see above).

Everything is written under `results/`, one folder per run mode (`test`,
`single_task_<folds>_<time>s`, `full_all_folds_1000s`, ...), so one experiment
is one folder you can zip and share:

    results/
    ├── datasets_summary.csv           (from `analyze_results.py --datasets`)
    └── full_all_folds_1000s/          one experiment, everything together
        ├── ludwig/                    runs, summary, environment, Ludwig diagnostics
        ├── sklearn/                   runs, summary, environment
        ├── analysis/                  tables and statistics
        └── logs/                      logs of the launches (launcher.log = whole session)

Each notebook writes to its tool's folder:

| File (in `results/<mode>/<tool>/`) | What it contains |
|---|---|
| `task_<id>_<tool>_all_runs.csv` | One row per run (fold): ids (`task_id`, `repeat`, `fold`, `seed`, `dataset_name`), the metrics and `time_taken` (s, training + evaluation). Classification: `roc_auc` (binary), `accuracy`, `balanced_accuracy`, `f1_macro`; Ludwig also `accuracy_micro` (the plain fraction of correct predictions; its own `accuracy` is a different quantity) and `loss`. Regression: `root_mean_squared_error`, `mean_absolute_error`, `mean_squared_error`, `r2`. Ludwig also `train_time_s`, `n_trials`, `n_trials_failed`; scikit-learn also `best_model`. |
| `summary_<tool>.csv` | Per task: `n_runs`, and the mean and sample standard deviation of every metric. |
| `environment_<tool>.json` | The machine: CPU model, cores and frequency, RAM, GPUs and whether they were used, CUDA build of PyTorch, library versions, git commit of the scripts, time limit, seeds. Quote it in the paper: Ludwig chooses its own concurrency and devices, so its results depend on the hardware. A resumed run keeps the original and, only if the machine or the versions differ from it, adds `environment_<tool>_resumed_<date>.json`. |
| `ludwig_inferred_feature_types.json` | Ludwig only. Per run: the type and encoder Ludwig chose for each input feature, the output type and the combiner. |
| `ludwig_run_diagnostics.json` | Ludwig only. Per run: trials launched and failed, epochs and time of the best trial, model type, combiner, trainer settings (epochs, batch size, early stopping), winning hyperparameters and the CPUs/GPUs Ray detected. |
| `discarded/` | Only after a restart: the CSVs of datasets that were discarded and redone. |

## Analysis

The last cell of each notebook runs the analysis and shows the summary table.
Edit its `ANALYSIS_OUTPUTS` list to choose which files are written (the
summary table is always shown). The same analysis runs from a terminal (from
`benchmarks/`):

    python analyze_results.py <mode>                 # e.g. full_all_folds_1000s
    python analyze_results.py <mode> --no-baseline   # skip the OpenML download
    python analyze_results.py <mode> --tool sklearn  # summary of the sklearn runs

It writes `results/<mode>/analysis/`:

| File | What it contains |
|---|---|
| `summary_table_<tool>.csv/.md` | One row per task: `mean ± sd` of the main metrics over the runs, the constant-predictor baseline next to each metric, and the mean time. Ready for the paper. |
| `baseline.csv` | The constant predictor (majority class / training mean) on the same folds. A tool at or below it is not learning. |
| `time_and_failures_<tool>.csv` | Runs completed vs expected per task, and the time used (mean, sd, min, max, % of the limit). |
| `per_task_stats.csv` | Per task and metric: mean, sd, 95% CI (t, n runs), median, min, max. |
| `ludwig_diagnostics.csv` | The diagnostics JSON flattened, one row per run. |
| `paired_tests.csv`, `across_tasks.csv` | Ludwig vs scikit-learn (needs both): Wilcoxon per task on the same folds, and across tasks, Holm-corrected. The p-values are slightly optimistic because the training sets of the folds overlap. |

`python analyze_results.py --datasets` writes `results/datasets_summary.csv` straight
from OpenML (no results needed): instances, features (target included, as in
OpenML), numeric/categorical split, missing values, classes, the columns OpenML
excludes (`excluded_columns`) and the majority-class share, which is the
accuracy of the constant predictor. Use only what the paper needs.

## Before committing

Clear notebook outputs:

    jupyter nbconvert --clear-output --inplace */*.ipynb
