# Changelog

All notable changes to Hamelin are listed here, newest first.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
version numbers follow [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-10-04

### Added
- **Review before training:** a window shown when you press *Start training*. It lists the
  data used (dataset, patients, outcome, predictors, selection rules) and every model
  setting, marks each one as *Default*, *Your choice* or *Detected from data*, explains it
  in one line, warns about risks (very few patients, too many predictors for the number of
  patients) and estimates the total duration.
- **Model size** (Automatic / Lightweight) and **Learning method** (Automatic / Cautious)
  in the advanced settings of the Training page. Both default to Automatic and are
  remembered per project.
- The **Prediction** and **Forecasting** pages are enabled.
- Early-stopping modes and model-architecture details (see the user manual).
- The 14 benchmark datasets as example data in `datasets/`.
- `CITATION.cff` and a DOI badge ([Zenodo](https://doi.org/10.5281/zenodo.23128034)).

### Changed
- Refreshed screenshots, user manual and README.
- The application version is now read from a single place (`src/hamelin/__init__.py`).
- Complete package metadata in `pyproject.toml` (description, authors, licence, URLs).

## [0.1.0] - 2026-10-03

First public release (Linux x86-64 standalone executable, CPU only).

### Added
- Projects, data import and cleaning, descriptive Table 1, automatic model training
  (Ludwig AutoML with Ray Tune), evaluation with 95 % bootstrap confidence intervals,
  model comparison, export of charts, tables and reports.
- English and Spanish interface, light and dark themes, built-in help.
- Per-model record of the settings, software versions, seed and dataset changes.

[0.2.0]: https://github.com/diegotxegp/hamelin/releases/tag/v0.2.0
[0.1.0]: https://github.com/diegotxegp/hamelin/releases/tag/v0.1.0
