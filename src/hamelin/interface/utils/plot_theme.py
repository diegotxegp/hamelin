"""Theming for pyqtgraph plots, which don't follow Qt stylesheets."""

import pyqtgraph as pg

from hamelin.interface.utils.colors import colors


def style_plot(plot_widget):
    """Apply the current theme's surface + axis colours to a PlotWidget.
    Light mode leaves the axes on pyqtgraph's own default pens, exactly as
    they were before theming existed."""
    c = colors()
    plot_widget.setBackground(c.surface)
    plot_widget.getViewBox().setBackgroundColor(c.surface)

    axis_color = c.muted if c.dark else pg.getConfigOption("foreground")
    plot_item = plot_widget.getPlotItem()
    for name in ("left", "bottom"):
        axis = plot_item.getAxis(name)
        axis.setPen(pg.mkPen(axis_color))
        axis.setTextPen(pg.mkPen(axis_color))
