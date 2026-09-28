"""Shared radar-chart geometry and drawing primitives.

Used by widgets/visualise_comparison_radar.py (the multi-model radar
comparison tool, reachable from the landing page's Comparison Tools). This
used to live in widgets/one_model.py, back when that page's own radar
compared a single model to the average of others - once that page was
simplified down to a plain "cards" view (a genuine multi-model comparison
belongs with the other comparison tools, not bolted onto a single-model
page), the drawing code moved here so the new comparison widget - and
anything else that wants a radar later - doesn't have to duplicate it.
"""

import math

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainterPath, QPen
import pyqtgraph as pg


def robust_bounds(values):
    """5th/95th percentile of values - used to normalize a metric's range
    for radar placement so a single outlier doesn't collapse every other
    point to near-zero or near-one."""
    if not values:
        return 0.0, 0.0

    sorted_vals = sorted(values)
    p5 = sorted_vals[int(0.05 * (len(sorted_vals) - 1))]
    p95 = sorted_vals[int(0.95 * (len(sorted_vals) - 1))]
    return p5, p95


def normalize(value, p5, p95):
    if p95 == p5:
        return 0.5
    return max(0.0, min(1.0, (value - p5) / (p95 - p5)))


def point_on_circle(index, count, radius, value=1.0):
    angle = (2 * math.pi * index) / count - math.pi / 2
    return radius * value * math.cos(angle), radius * value * math.sin(angle)


class RadarItem(pg.Qt.QtWidgets.QGraphicsPathItem):
    """One series' polygon on a radar chart: `values` are already
    normalized to [0, 1] (see normalize()), one per axis in `labels`'s
    order."""

    def __init__(self, values, labels, radius=160, color="#107C10", dashed=False, width=2):
        super().__init__()

        self.values = values
        self.labels = labels
        self.radius = radius

        n = len(values)
        path = QPainterPath()

        if n == 0:
            self.setPath(path)
            return

        x0, y0 = point_on_circle(0, n, radius, values[0])
        path.moveTo(x0, y0)

        for i in range(1, n):
            x, y = point_on_circle(i, n, radius, values[i])
            path.lineTo(x, y)

        path.closeSubpath()

        self.setPath(path)

        pen = QPen(QColor(color), width)
        if dashed:
            pen.setStyle(Qt.DashLine)

        self.setPen(pen)

        fill = QColor(color)
        fill.setAlpha(60)
        self.setBrush(fill)
