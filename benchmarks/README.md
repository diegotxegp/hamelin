# Benchmarks

Ludwig AutoML (`ludwig/`) and InsuML (`InsuML/`) on the 14 datasets in `datasets/`, one run per seed.

| File | |
|---|---|
| `ludwig/ludwig_experiment.ipynb` | Ludwig `auto_train` with default settings |
| `InsuML/InsuML_experiment.ipynb` | InsuML with default settings |
| `common_utils.py` | Helpers shared by the notebooks |
| `analyze_results.py` | Summary tables from the results |
| `run_benchmark.sh` | Runs a notebook unattended |
| `requirements.txt` | Pinned versions (Python 3.12) |

## Run

    cd benchmarks
    uv venv --python 3.12 .venv-bench
    uv pip install --python .venv-bench/bin/python -r requirements.txt
    .venv-bench/bin/python -m ipykernel install --user --name ludwig-bench

Open a notebook, select the `ludwig-bench` kernel, check the *Parameters* cell and *Run All*.
Test mode (`TEST_MODE = True`) runs one dataset and one seed; the full experiment sets it to `False`.
From a terminal:

    ./run_benchmark.sh test             # Ludwig, smoke test
    ./run_benchmark.sh insuml full      # InsuML, all datasets and seeds

An interrupted run continues where it stopped: finished datasets are skipped and partial ones restart.
Each trial needs about 1 GB of RAM; if memory is short, Ray kills trials and the run fails
(for InsuML, lower `PARALLEL_TRIALS`).

## Results

`<tool>/results/<run mode>/` (not versioned):

    <tool>/                    <dataset>_runs.csv, parameters.json, environment_<tool>.json, diagnostics
    analysis/                  summary_metrics.csv, datasets_summary.csv
    ../logs/                   only with run_benchmark.sh

`<dataset>_runs.csv` has one row per seed with every test metric (`accuracy_micro` is the plain
accuracy), `train_time_s` and `n_trials`. Summaries:

    python analyze_results.py <run mode> [--tool InsuML]
