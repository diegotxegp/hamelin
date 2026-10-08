# Benchmark: Ludwig AutoML

A notebook that runs Ludwig AutoML (`auto_train`, default configuration) on the 14
datasets of the project's [`datasets/`](../datasets) folder and records the metrics and
the training time. It runs from the notebook itself: everything that can be changed is in its
**Parameters** cell.

| File | What it does |
|---|---|
| `ludwig/ludwig_experiment.ipynb` | The benchmark. Its *Parameters* cell holds every setting (run mode, time limit, split, datasets, targets, seeds) |
| `common_utils.py` | Helper functions (dataset loading, saving and resuming results, machine record, GPU/temp handling); no settings |
| `analyze_results.py` | Statistics, paper table and dataset table (trains nothing); the notebook calls it in its last cell |
| `run_benchmark.sh` | Optional: runs the notebook unattended from a terminal |
| `requirements.txt` | Pinned dependency versions |

## Quick start (fresh clone)

From the repository root:

    cd benchmarks
    uv venv --python 3.12 .venv-bench
    uv pip install --python .venv-bench/bin/python -r requirements.txt
    .venv-bench/bin/python -m ipykernel install --user --name ludwig-bench
    uv pip install --python .venv-bench/bin/python jupyterlab   # or open the notebook in VS Code
    .venv-bench/bin/jupyter lab

Open `ludwig/ludwig_experiment.ipynb`, select the `ludwig-bench` kernel, check the
**Parameters** cell and *Run All*. The notebook must run with its own folder
(`benchmarks/ludwig`) as working directory, which is what Jupyter does by default. Exact
versions are pinned in `requirements.txt` (Python 3.12). If the default `torch` wheel does not
match the machine's GPU/CUDA, install the right build before the rest. The notebook falls
back to CPU when the GPU is not supported by that build.

The Parameters cell starts in **test mode** (`TEST_MODE = True`): one dataset (diabetes), its
first seed, 300 s, about 7 minutes. It confirms the environment works. For the full
experiment set `TEST_MODE = False` (all datasets, all their seeds, 1000 s per run).

## The Parameters cell

| Parameter | Meaning |
|---|---|
| `TEST_MODE`, `TEST_DATASET` | `True`: smoke test on `TEST_DATASET`, first seed only. `False`: every dataset in `DATASETS` with all its seeds |
| `TIME_LIMIT_S` | Time budget of each run: 300 s in test mode, 1000 s otherwise |
| `TEST_FRACTION` | Share of the whole dataset used as test (0.2 by default). The rest is split internally into train and validation (0.7 / 0.1, Ludwig's defaults). The test share is part of the results folder's name |
| `DATASETS` | One row per dataset: `name: (folder in datasets/, target column, seeds)`. Add, remove or change datasets, targets and seeds here |
| `RESUME`, `DATASET_RETRIES` | What to do after an interruption or a failed run (see below) |
| `DATASETS_DIR`, `RESULTS_ROOT` | Where the CSV files are read from and the results are written to |

A dataset is run once per seed, so the number of seeds of a row is the number of runs of that
dataset: 59 runs in total (from 2 seeds for hypothyroid up to 6 for credit-g).

### Interruptions

A full run takes hours: 59 runs x up to 1000 s (plus the ~100 s Ludwig overshoots), at most
roughly 18 h on a machine like the one in `environment_ludwig.json`.
Keep the browser/VS Code session and the machine awake, or use `run_benchmark.sh`.

If anything interrupts it (Ctrl+C, reboot, crash), run the notebook again with the same
parameters. With `RESUME = True` the experiment continues dataset by dataset: a dataset with all
its runs saved is skipped, and one that was only partly done is **discarded and restarted from
its first seed**, so every dataset comes from one uninterrupted series of runs on the same
machine. The discarded CSV is kept in `results/<mode>/ludwig/discarded/` for inspection and
ignored by the analysis. The same happens inside a run: if one run of a dataset fails, the
dataset is started over (`DATASET_RETRIES`, default 1) and the experiment goes on with the next
one. To start from scratch set `RESUME = False`: the previous `results/<mode>/ludwig/` folder is
moved to `results/<mode>/ludwig.old_<timestamp>` (delete it by hand when sure).

### From a terminal

    ./run_benchmark.sh test          # smoke test, about 7 minutes
    ./run_benchmark.sh full          # the whole experiment
    tail -f results/logs/launcher.log

`run_benchmark.sh` extracts the notebook's code cells into a script and runs it, with live logs in
`results/logs/` and no per-cell timeout. `full` / `test` override `TEST_MODE` for that launch
(the notebook is not edited); without either, the notebook's value is used. It runs in the
foreground: for a long run use tmux/screen or `nohup ./run_benchmark.sh full > /dev/null 2>&1 &`
(then `tail -f results/logs/launcher.log`). The rest of the Parameters cell is used as it is.
`PYTHON=/path/to/python` selects the interpreter (default `.venv-bench/bin/python`); a second
pass redoes the datasets that did not finish in the first one (`BENCH_PASSES=1` disables it).
Do not start two launches at once; the script refuses.

## Protocol

- **Data:** the CSV files of `datasets/` (no download), listed in `DATASETS` with each one's
  folder and **target column**. The folder gives the task type (`Binary` and `Classification`
  are classification, `Regression` is regression). The target is stated because Ludwig's
  `auto_train` requires it as an argument and cannot detect it; the notebook checks that the
  column exists. Ludwig does infer the type of the target, and the notebook fails a run if it is
  not the dataset's task type.
- **One run per seed.** The seed drives Ludwig's split, its hyperparameter sampling and its
  training. The results of a dataset are the mean and standard deviation over its runs.
- **80/20 by default.** Ludwig receives the whole dataset and splits it itself into
  70% train / 10% validation / 20% test (the split type is its own choice: stratified when the
  target is an imbalanced classification target, random otherwise). Only the shares and the seed
  are given to it; everything else is Ludwig's default. The notebook fails the run if the trained
  model is not configured with the test share that was asked for.
- **Metrics.** Ludwig picks the best epoch by its validation metric, and the reported
  metrics are those of its test split at that same epoch (read from `training_stats`), so
  the test split plays no part in training or model selection. All the metrics Ludwig computes
  there are saved; those it does not compute (e.g. balanced accuracy, macro-F1) are not
  available, because Ludwig's test rows and predictions are not exposed. No cross-validation.
- **Ludwig is not fully deterministic** even with a fixed seed (it stops by time and runs
  trials in parallel), so small differences between repeated runs are expected. The standard
  deviation mixes the data-split and the seed variability.
- **Ludwig's defaults** include its concurrency and device use (CPUs/GPUs), which are decided
  automatically; each trial is a full PyTorch process (~0.5-1.5 GB), and as many trials run in parallel as
  Ludwig decides, so make sure the machine has enough free memory (several GB): if the node runs out of
  it, Ray kills trials and the run fails. Each run prints the RAM available, and between runs the
  benchmark stops Ray and frees the memory. The only exceptions are workarounds that do not change the model:
  `backend="local"` (a Ludwig 0.17.x bug with Ray) and, before each trial, a GPU memory wait
  adapted to a GPU that also drives the desktop (`init_ray_for_ludwig` in `common_utils.py`).
  Very short time limits (about 60 s) fail with `grace_period must be <= max_t`; use at least a
  few minutes. Ludwig runs about 100 s longer than its time limit (or stops earlier if its default
  10 trials finish first); with short limits some of the 10 trials never start.

## Outputs (not versioned)

Everything is written under `results/`, one folder per run mode and test share (`test_300s_test20pct`,
`full_1000s_test20pct`, ...), so one experiment is one folder you can zip and share:

    results/
    ├── logs/                          only with run_benchmark.sh (launcher.log = whole session)
    └── full_1000s_test20pct/          one experiment, everything together
        ├── ludwig/                    runs, parameters, environment, Ludwig diagnostics
        └── analysis/                  tables and statistics

Temporary files: Ludwig's `hyperopt/` folder (every trial's checkpoints and logs) is deleted
before and after each run, and Ray's session files in the system temp folder when no other Ray
job is running. Results are **not** deleted before a run, so that an interrupted experiment can
continue.

| File (in `results/<mode>/ludwig/`) | What it contains |
|---|---|
| `<dataset>_runs.csv` | One row per run (seed): `dataset`, `group`, `seed`, the metrics and `time_taken` (s, training + evaluation). Every metric Ludwig computes on its test split for the target, none filtered out: for classification typically `accuracy`, `accuracy_micro` (the plain fraction of correct predictions; Ludwig's own `accuracy` is a different quantity), `roc_auc` (binary), `loss` and whatever else it reports; for regression `root_mean_squared_error`, `mean_absolute_error`, `mean_squared_error`, `r2`, `loss`, .... Also `train_time_s`, `n_trials`, `n_trials_failed`. |
| `parameters.json` | The settings of the launch (the Parameters cell: time limit, split, datasets, targets, seeds). The analysis reads it. |
| `environment_ludwig.json` | The machine: CPU model, cores and frequency, RAM, GPUs and whether they were used, CUDA build of PyTorch, library versions, git commit of the scripts, and the parameters. Quote it in the paper: Ludwig chooses its own concurrency and devices, so its results depend on the hardware. A resumed run keeps the original and, only if the machine or the versions differ from it, adds `environment_ludwig_resumed_<date>.json`. |
| `ludwig_inferred_feature_types.json` | Per run: the type and encoder Ludwig chose for each input feature, the output type and the combiner. |
| `ludwig_run_diagnostics.json` | Per run: trials launched and failed, epochs and time of the best trial, model type, combiner, trainer settings (epochs, batch size, early stopping), winning hyperparameters and the CPUs/GPUs Ray detected. |
| `discarded/` | Only after a restart: the CSVs of datasets that were discarded and redone. |

## Analysis

The last cell of the notebook runs the analysis and shows the summary table. Edit its
`ANALYSIS_OUTPUTS` list to choose which files are written (the summary table is always
shown). The same analysis runs from a terminal (from `benchmarks/`):

    python analyze_results.py <mode>                 # e.g. full_1000s_test20pct

It writes `results/<mode>/analysis/`. The notebook also refreshes it each time a dataset finishes, so the
summary grows while the benchmark runs:

| File | What it contains |
|---|---|
| `summary_metrics.csv` | One row per dataset, every metric Ludwig reports plus times and trials: mean, std, median, worst and best run and the 95% CI of the mean (t, n runs). Also `runs_expected`, `runs_failed` and the mean time as a percentage of the limit. Best is the minimum for losses, errors, times and failed trials. |
| `datasets_summary.csv` | Per dataset: instances, features, numeric/other split (by column type), missing values, classes and the majority-class share (the accuracy of the constant predictor). Use only what the paper needs. |

## Before committing

Clear notebook outputs:

    jupyter nbconvert --clear-output --inplace */*.ipynb
