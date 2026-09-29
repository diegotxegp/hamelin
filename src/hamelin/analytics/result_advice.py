"""
Result advice
~~~~~~~~~~~~~

Plain-language reading of a trained model's test results: is it good or
weak and why, how reliable the estimate is, how it could be improved, and
what to keep in mind before relying on it.

Rule-based (no generative model): every sentence is produced from the
numbers by an explicit rule, so it is reproducible and can be audited. The
rules are rules of thumb for clinical prediction models, and the text says
so. English text lives in hamelin.i18n.strings under "advice.*".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hamelin.i18n import t

# Rules of thumb (documented in the manual):
AUC_BANDS = ((0.90, "excellent"), (0.80, "good"), (0.70, "moderate"))
R2_BANDS = ((0.90, "excellent"), (0.70, "good"), (0.50, "moderate"))
SMALL_TEST_SET = 100
MODEST_TEST_SET = 300
OVERFIT_GAP = 0.10
IMBALANCED_BELOW = 0.25
TRADEOFF_GAP = 0.20
TOO_GOOD = 0.95
WIDE_CI = 0.15


@dataclass
class Advice:
    task: str = "unknown"            # binary | multiclass | regression | unknown
    level: str = "unknown"           # good | moderate | weak | unknown
    verdict: str = ""
    sections: list[tuple[str, list[str]]] = field(default_factory=list)   # (title, lines)


def _get(metrics: dict | None, *names: str):
    for n in names:
        v = (metrics or {}).get(n)
        if isinstance(v, (int, float)):
            return float(v)
    return None


def _band(value: float, bands) -> str:
    for threshold, name in bands:
        if value >= threshold:
            return name
    return "weak"


def _class_shares(pred_df):
    """(value_counts share Series of y_true as str) or None."""
    if pred_df is None or "y_true" not in pred_df.columns or len(pred_df) == 0:
        return None
    return pred_df["y_true"].astype(str).value_counts(normalize=True)


def detect_task(test_metrics: dict, pred_df=None) -> str:
    if _get(test_metrics, "roc_auc", "auc", "roc_auc_score") is not None:
        return "binary"
    if _get(test_metrics, "r2", "root_mean_squared_error", "rmse", "mean_absolute_error", "mae") is not None:
        return "regression"
    if _get(test_metrics, "accuracy", "accuracy_score") is not None:
        shares = _class_shares(pred_df)
        return "binary" if shares is not None and len(shares) == 2 else "multiclass"
    return "unknown"


def build_advice(test_metrics: dict, train_metrics: dict | None = None, pred_df=None,
                 n_test: int | None = None) -> Advice:
    """Interpret *test_metrics* (and, when available, the saved test
    predictions *pred_df* and the *train_metrics*)."""
    tm = test_metrics or {}
    adv = Advice(task=detect_task(tm, pred_df))
    if adv.task == "unknown":
        adv.verdict = t("advice.verdict.unknown")
        return adv

    n = n_test if n_test is not None else (len(pred_df) if pred_df is not None else None)
    shares = _class_shares(pred_df)
    why: list[str] = []
    rel: list[str] = []
    imp: list[str] = [t("advice.imp.predictors")]
    headline_name, headline_value, headline_train = "", None, None
    tradeoff = overfit = too_good = weak_or_fair = False

    if adv.task == "binary":
        auc = _get(tm, "roc_auc", "auc", "roc_auc_score")
        acc = _get(tm, "accuracy", "accuracy_score")
        sens = _get(tm, "recall", "sensitivity", "true_positive_rate")
        spec = _get(tm, "specificity", "true_negative_rate", "tnr")
        prec = _get(tm, "precision", "positive_predictive_value")
        headline_name, headline_value = "AUC", auc
        headline_train = _get(train_metrics, "roc_auc", "auc", "roc_auc_score")
        if auc is not None:
            band = _band(auc, AUC_BANDS)
            adv.level = {"excellent": "good", "good": "good", "moderate": "moderate"}.get(band, "weak")
            adv.verdict = t(f"advice.verdict.binary.{band}").format(auc)
            why.append(t("advice.why.auc").format(auc))
            too_good = auc >= TOO_GOOD
            weak_or_fair = band in ("moderate", "weak")
        if acc is not None and shares is not None:
            base = float(shares.iloc[0])
            if acc - base >= 0.01:
                why.append(t("advice.why.acc_vs_base").format(acc, shares.index[0], base, acc - base))
            else:
                why.append(t("advice.why.acc_no_gain").format(acc, shares.index[0], base))
        if sens is not None and spec is not None:
            why.append(t("advice.why.sens_spec").format(sens, spec))
            if abs(sens - spec) > TRADEOFF_GAP:
                tradeoff = True
                favours = t("advice.favours.sens") if sens > spec else t("advice.favours.spec")
                why.append(t("advice.why.tradeoff").format(favours))
                imp.append(t("advice.imp.threshold"))
        if prec is not None:
            why.append(t("advice.why.precision").format(prec))
        if shares is not None and len(shares) == 2:
            minority = float(shares.iloc[-1])
            if minority < IMBALANCED_BELOW:
                imp.append(t("advice.imp.imbalance").format(minority))
    elif adv.task == "multiclass":
        acc = _get(tm, "accuracy", "accuracy_score")
        headline_name, headline_value = "accuracy", acc
        headline_train = _get(train_metrics, "accuracy", "accuracy_score")
        if acc is not None and shares is not None:
            base = float(shares.iloc[0])
            gain = acc - base
            band = "good" if gain >= 0.15 else "moderate" if gain >= 0.05 else "weak"
            adv.level = band
            adv.verdict = t(f"advice.verdict.multi.{band}").format(acc, base)
            why.append(t("advice.why.acc_vs_base").format(acc, shares.index[0], base, gain))
            weak_or_fair = band != "good"
            too_good = acc >= TOO_GOOD
        elif acc is not None:
            adv.verdict = t("advice.verdict.multi.nobase").format(acc)
        why.append(t("advice.why.multi_confusion"))
        if shares is not None and len(shares) > 2 and float(shares.iloc[-1]) < 0.05:
            imp.append(t("advice.imp.rare_classes"))
    else:  # regression
        r2 = _get(tm, "r2")
        rmse = _get(tm, "root_mean_squared_error", "rmse")
        mae = _get(tm, "mean_absolute_error", "mae")
        headline_name, headline_value = "R²", r2
        headline_train = _get(train_metrics, "r2")
        if r2 is not None:
            if r2 < 0:
                adv.level, adv.verdict = "weak", t("advice.verdict.reg.negative").format(r2)
                weak_or_fair = True
            else:
                band = _band(r2, R2_BANDS)
                adv.level = {"excellent": "good", "good": "good", "moderate": "moderate"}.get(band, "weak")
                adv.verdict = t(f"advice.verdict.reg.{band}").format(r2)
                weak_or_fair = band in ("moderate", "weak")
            why.append(t("advice.why.r2").format(r2, max(r2, 0.0)))
            too_good = r2 >= TOO_GOOD
        if rmse is not None or mae is not None:
            unit_line = t("advice.why.errors").format(
                "n/a" if rmse is None else f"{rmse:.3g}", "n/a" if mae is None else f"{mae:.3g}")
            if rmse is not None and pred_df is not None and "y_true" in pred_df.columns:
                try:
                    sd = float(pred_df["y_true"].astype(float).std())
                    if sd > 0:
                        unit_line += " " + t("advice.why.errors_vs_sd").format(sd, rmse / sd)
                except (TypeError, ValueError):
                    pass
            why.append(unit_line)
        imp.append(t("advice.imp.reg_outcome"))

    # ── reliability ───────────────────────────────────────────────────
    if n is not None:
        if n < SMALL_TEST_SET:
            rel.append(t("advice.rel.size_small").format(n))
            weak_or_fair = True
        else:
            rel.append(t("advice.rel.size_ok").format(n))
    if pred_df is not None and headline_value is not None:
        try:
            from hamelin.analytics.eval_data import bootstrap_auc_ci, bootstrap_ci_fast

            key = {"accuracy": "accuracy", "R²": "r2"}.get(headline_name)
            lo = hi = None
            if headline_name == "AUC":
                _, lo, hi = bootstrap_auc_ci(pred_df)
            elif key:
                _, lo, hi = bootstrap_ci_fast(pred_df, key)
            if lo is not None:
                line = t("advice.rel.ci").format(headline_name, lo, hi)
                if hi - lo > WIDE_CI:
                    line += " " + t("advice.rel.ci_wide")
                rel.append(line)
        except Exception:  # noqa: BLE001 - advice must never break the results view
            pass
    if headline_value is not None and headline_train is not None and headline_train - headline_value > OVERFIT_GAP:
        overfit = True
        rel.append(t("advice.rel.gap").format(headline_name, headline_train, headline_value))
    if too_good:
        rel.append(t("advice.rel.too_good"))

    # ── improvements ──────────────────────────────────────────────────
    if weak_or_fair or (n is not None and n < MODEST_TEST_SET):
        imp.append(t("advice.imp.more_data"))
    imp.append(t("advice.imp.missing"))
    imp.append(t("advice.imp.search"))
    if overfit:
        imp.append(t("advice.imp.overfit"))
    imp.append(t("advice.imp.compare"))

    cav = [t("advice.cav.internal"), t("advice.cav.subgroups"), t("advice.cav.support")]
    if adv.task == "binary":
        cav.insert(1, t("advice.cav.calibration"))

    adv.sections = [
        (t("advice.why.title"), why),
        (t("advice.rel.title"), rel),
        (t("advice.imp.title"), imp),
        (t("advice.cav.title"), cav),
    ]
    adv.sections = [(title, lines) for title, lines in adv.sections if lines]
    if not adv.verdict:
        adv.verdict = t("advice.verdict.unknown")
    return adv


def advice_html(adv: Advice, dark: bool = False) -> str:
    """Rich text for a QLabel: colour-tagged verdict, then the sections."""
    import html

    colours = {"good": "#2E9E5B", "moderate": "#D98A00", "weak": "#D13438", "unknown": "#808080"}
    parts = [f'<p><b style="color:{colours.get(adv.level, "#808080")}">{html.escape(adv.verdict)}</b></p>']
    for title, lines in adv.sections:
        parts.append(f"<p><b>{html.escape(title)}</b></p><ul style='margin-top:0'>")
        parts += [f"<li>{html.escape(line)}</li>" for line in lines]
        parts.append("</ul>")
    parts.append(f"<p style='color:gray'><i>{html.escape(t('advice.footer'))}</i></p>")
    return "".join(parts)
