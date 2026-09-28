"""Rule evaluator utilities
===========================

Provides simple, safe parsing of clinician-friendly rules and applies
them to pandas DataFrames without using eval().

Supported forms (examples):
  Edad >= 18
  Sexo == 'Femenino'
  Duracion_min > 180
  Diagnosticos in ['A','B']

Returns boolean masks and sample rows/counts for preview.
"""
from typing import List, Tuple, Dict, Any
import re
import pandas as pd


_OP_PATTERNS = ['==', '!=', '>=', '<=', '>', '<', ' in ', ' not in ', ' contains ']


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    # strip surrounding quotes
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        return raw[1:-1]
    # list literal like [1,2,'a']
    if raw.startswith('[') and raw.endswith(']'):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        parts = re.split(r"\s*,\s*", inner)
        return [_parse_value(p) for p in parts]
    # booleans
    if raw.lower() in ('true', 'false'):
        return raw.lower() == 'true'
    # numbers
    try:
        if '.' in raw:
            return float(raw)
        return int(raw)
    except Exception:
        pass
    return raw


def parse_rule(rule: str) -> Tuple[str, str, Any]:
    """Parse a single rule into (column, operator, value).

    Raises ValueError on unsupported format.
    """
    if not rule or not rule.strip():
        raise ValueError('Empty rule')
    r = rule.strip()
    # try to match operators by longest-first
    for op in sorted(_OP_PATTERNS, key=len, reverse=True):
        if op in r:
            parts = r.split(op)
            if len(parts) != 2:
                raise ValueError(f'Bad rule format: {rule}')
            col = parts[0].strip()
            val = parts[1].strip()
            return col, op.strip(), _parse_value(val)
    # fallback: whitespace separated (col op val)
    m = re.split(r"\s+", r, maxsplit=2)
    if len(m) == 3:
        col, op, val = m
        return col, op, _parse_value(val)
    raise ValueError(f'Unsupported rule syntax: {rule}')


def apply_rules(df: pd.DataFrame, rules: List[str], mode: str = 'include') -> Dict[str, Any]:
    """Apply a list of rules to `df`.

    mode: 'include' returns rows that match ANY inclusion rule (OR semantics)
          'exclude' returns rows that do NOT match ANY exclusion rule

    Returns dict with keys: mask (pd.Series bool), count, sample_df
    """
    if df is None or df.empty:
        return {'mask': pd.Series([False] * 0, index=df.index if df is not None else []), 'count': 0, 'sample': df.head(0)}

    masks = []
    for rule in rules:
        try:
            col, op, val = parse_rule(rule)
        except ValueError:
            # invalid rule → skip with all-False mask
            masks.append(pd.Series([False] * len(df), index=df.index))
            continue

        if col not in df.columns:
            masks.append(pd.Series([False] * len(df), index=df.index))
            continue

        series = df[col]
        # handle operators
        if op == '==':
            masks.append(series == val)
        elif op == '!=':
            masks.append(series != val)
        elif op == '>=':
            masks.append(series.astype(object) >= val)
        elif op == '<=':
            masks.append(series.astype(object) <= val)
        elif op == '>':
            masks.append(series.astype(object) > val)
        elif op == '<':
            masks.append(series.astype(object) < val)
        elif op == 'in':
            if isinstance(val, list):
                masks.append(series.isin(val))
            else:
                masks.append(series.isin([val]))
        elif op == 'not in':
            if isinstance(val, list):
                masks.append(~series.isin(val))
            else:
                masks.append(~series.isin([val]))
        elif op == 'contains':
            try:
                masks.append(series.astype(str).str.contains(str(val), na=False))
            except Exception:
                masks.append(pd.Series([False] * len(df), index=df.index))
        else:
            # unknown operator
            masks.append(pd.Series([False] * len(df), index=df.index))

    if not masks:
        # nothing to apply
        final_mask = pd.Series([True] * len(df), index=df.index) if mode == 'include' else pd.Series([False] * len(df), index=df.index)
    else:
        if mode == 'include':
            # OR semantics: any rule true → included
            final_mask = pd.concat(masks, axis=1).any(axis=1)
        else:
            # exclude: rows where any exclusion rule is true are removed
            exc_mask = pd.concat(masks, axis=1).any(axis=1)
            final_mask = ~exc_mask

    count = int(final_mask.sum())
    sample = df.loc[final_mask].head(5)
    return {'mask': final_mask, 'count': count, 'sample': sample}


if __name__ == '__main__':
    import pandas as pd
    df = pd.DataFrame({'Edad': [20, 30, 15], 'Sexo': ['Femenino', 'Masculino', 'Femenino']})
    out = apply_rules(df, ["Edad >= 18", "Sexo == 'Femenino'"], mode='include')
    print(out['count'])