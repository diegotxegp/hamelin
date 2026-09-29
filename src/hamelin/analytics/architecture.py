"""
Model architecture summary
==========================

Plain-language description of what a trained Ludwig model is made of, read
from its saved ``model_hyperparameters.json``.  Combiner descriptions are
taken from the official Ludwig documentation
(``docs/ludwig/04_configuration/configuration__combiner.md``).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# combiner type -> one-sentence description (Ludwig combiner documentation)
COMBINER_DESCRIPTIONS: dict[str, str] = {
    "concat": "Concatenates the encoded input features and passes them through optional fully connected layers.",
    "tabnet": "TabNet: sequential attention that selects which features to use at each decision step.",
    "transformer": "Stack of Transformer self-attention layers over the encoded input features.",
    "tabtransformer": "TabTransformer: Transformer layers over the categorical embeddings, combined with the numeric features.",
    "ft_transformer": (
        "FT-Transformer: every feature becomes a token, a learnable [CLS] token is added and the whole "
        "sequence goes through Transformer self-attention layers, learning cross-feature interactions."
    ),
    "cross_attention": "Pairwise multi-head cross-attention between all input features.",
    "perceiver": "Perceiver IO style: learnable latent tokens cross-attend to all encoder outputs.",
    "sequence_concat": "Concatenates sequence features along the sequence or feature dimension.",
    "sequence": "Applies a sequence encoder over the concatenated features.",
    "comparator": "Compares two entities' encodings.",
}

_ENCODER_LABELS = {"passthrough": "passed through unchanged", "dense": "dense layer", "sparse": "sparse"}


def _pick(d: dict, *keys: str) -> dict:
    return {k: d[k] for k in keys if d.get(k) is not None}


def describe_architecture(model_dir: str | Path) -> list[tuple[str, str]]:
    """Return ``[(label, value), …]`` rows for the model in *model_dir* (empty if unreadable)."""
    path = Path(model_dir)
    for cand in (path / "model_hyperparameters.json", path / "model" / "model_hyperparameters.json"):
        if cand.is_file():
            path = cand
            break
    else:
        return []
    try:
        cfg: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []

    rows: list[tuple[str, str]] = []
    comb = cfg.get("combiner") or {}
    ctype = comb.get("type")
    if ctype:
        desc = COMBINER_DESCRIPTIONS.get(ctype, "")
        rows.append(("Combiner", f"{ctype}" + (f" — {desc}" if desc else "")))
        params = _pick(comb, "num_layers", "num_heads", "hidden_size", "num_fc_layers", "output_size", "dropout")
        if params:
            rows.append(("Combiner size", ", ".join(f"{k}={round(v, 3) if isinstance(v, float) else v}"
                                                      for k, v in params.items())))
    enc = sorted({f"{f.get('type')}/{(f.get('encoder') or {}).get('type', 'default')}"
                  for f in cfg.get("input_features", [])})
    if enc:
        rows.append(("Input encoders (type/encoder)", ", ".join(enc)))
    dec = sorted({f"{f.get('type')}/{(f.get('decoder') or {}).get('type', 'default')}"
                  for f in cfg.get("output_features", [])})
    if dec:
        rows.append(("Output decoders (type/decoder)", ", ".join(dec)))
    tr = cfg.get("trainer") or {}
    opt = tr.get("optimizer") or {}
    if opt.get("type"):
        lr = tr.get("learning_rate")
        rows.append(("Optimizer", f"{opt['type']}" + (f", learning rate {lr:.2g}" if isinstance(lr, (int, float)) else "")))
    if tr.get("batch_size") is not None:
        rows.append(("Batch size", str(tr["batch_size"])))
    if tr.get("epochs") is not None:
        rows.append(("Max. epochs", str(tr["epochs"])))
    return rows
