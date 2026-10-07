# Example datasets

The 14 public datasets used in the benchmarks (`benchmarks/`), downloaded from
[OpenML](https://www.openml.org) and saved as CSV. Import any of them from the
**Data** page to try Hamelin without your own data.

| Folder | Datasets |
|---|---|
| `Binary/` | blood-transfusion-service-center, breast-w, credit-g, diabetes, qsar-biodeg |
| `Classification/` (multiclass) | analcatdata_dmft, cmc, hypothyroid, mfeat-morphological, vehicle |
| `Regression/` | cholesterol, cloud, liver-disorders, plasma_retinol |

The benchmarks read these files directly, so the folder layout matters: the subfolder
(`Binary`, `Classification`, `Regression`) says whether a dataset is a classification or a
regression task, and each dataset's target column is listed in the `DATASETS` table of the
notebook's Parameters cell (`benchmarks/ludwig/ludwig_experiment.ipynb`); it is the last column of every file.

Each dataset keeps the licence of its OpenML entry.
