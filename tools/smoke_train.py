"""Headless training smoke test: python tools/smoke_train.py data.csv  (or: ./hamelin -c "$(cat tools/smoke_train.py)" data.csv)."""
import sys, tempfile, time, pandas as pd
from hamelin.analytics.automl.ludwig_backend import LudwigBackend
df = pd.read_csv(sys.argv[1])
out = tempfile.mkdtemp(prefix="hamelin_smoke_")
t0 = time.time()
res = LudwigBackend().run(df, df.columns[-1], time_limit_s=100, output_directory=out, test_split=0.2, random_seed=1)
print("SMOKE_OK", res.model_type, {k: round(v, 3) for k, v in res.test_metrics.items() if isinstance(v, float)}, round(time.time() - t0), "s", flush=True)
