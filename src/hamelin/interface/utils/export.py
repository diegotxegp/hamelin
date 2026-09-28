"""Shared "Export" behavior for the single-model and comparison views.

One click saves an image of whatever chart/table is on screen (PNG or PDF -
something to paste straight into a report) and, for the data views, a CSV
with the same underlying numbers next to it. The single-model page instead
exports a self-contained report (project + model info + metrics) as CSV or
a formatted PDF.

Kept as one button per view instead of a format picker in the UI - the
format choice lives in the save dialog's filter.
"""

import csv
import html
from pathlib import Path

from PySide6.QtCore import QMarginsF, QRectF, QSize, Qt
from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter, QTextDocument
from PySide6.QtWidgets import QFileDialog, QWidget

from hamelin.interface.utils.widgets import RoundedButton, set_asset_icon, Toast


def make_export_button():
    """Return a RoundedButton styled like the rest of the app's actions
    (Dashboard/Back), ready to `.clicked.connect(...)` to an export handler."""
    btn = RoundedButton("  Export", 220, 70, 35)
    set_asset_icon(btn, "down.svg")
    btn.setIconSize(QSize(32, 32))
    return btn


# A4 at 150 DPI, minus a 10 mm margin, is the page box every PDF export
# below fits its content into - scaled down to the width and split across
# pages top-to-bottom so nothing is ever clipped off an edge.
_PDF_DPI = 150
_PDF_MARGIN_MM = 10.0


def _pixmap_to_pdf(pixmap, out_path):
    """Draw *pixmap* into a PDF at *out_path*, scaled to the page width and
    continued onto further pages when it's taller than one page. Picks
    landscape when the capture is clearly wider than it is tall so a wide
    table doesn't come out with unreadably small text."""
    landscape = pixmap.width() > pixmap.height() * 1.4
    writer = QPdfWriter(str(out_path))
    writer.setResolution(_PDF_DPI)
    writer.setPageLayout(QPageLayout(
        QPageSize(QPageSize.A4),
        QPageLayout.Landscape if landscape else QPageLayout.Portrait,
        QMarginsF(_PDF_MARGIN_MM, _PDF_MARGIN_MM, _PDF_MARGIN_MM, _PDF_MARGIN_MM),
        QPageLayout.Millimeter,
    ))

    page = writer.pageLayout().paintRectPixels(writer.resolution())
    scale = page.width() / pixmap.width()
    src_per_page = page.height() / scale  # source px that fit on one page

    painter = QPainter(writer)
    try:
        y = 0
        first = True
        while y < pixmap.height():
            if not first:
                writer.newPage()
            first = False
            h = min(src_per_page, pixmap.height() - y)
            painter.drawPixmap(
                QRectF(page.x(), page.y(), pixmap.width() * scale, h * scale),
                pixmap,
                QRectF(0, y, pixmap.width(), h),
            )
            y += h
    finally:
        painter.end()


def _render_image(image_source, out_path):
    """Write *image_source* (a QWidget, captured with .grab(), or a
    matplotlib Figure) to *out_path*, whose suffix (.png / .pdf) picks the
    format."""
    is_pdf = out_path.suffix.lower() == ".pdf"

    if not isinstance(image_source, QWidget):  # matplotlib Figure - native both
        image_source.savefig(str(out_path), dpi=_PDF_DPI, bbox_inches="tight")
        return

    pixmap = image_source.grab()
    if is_pdf:
        _pixmap_to_pdf(pixmap, out_path)
    else:
        pixmap.save(str(out_path), "PNG")


def _write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def export_chart_and_data(parent, default_filename, image_source, csv_header, csv_rows):
    """
    Prompt for a save location, then write the picture (``<name>.pdf`` or
    ``<name>.png``, per the dialog's filter) of *image_source* and, unless
    *csv_header* is None, ``<name>.csv`` (*csv_rows* under *csv_header*)
    next to it.

    Args:
        parent: Widget to anchor the file dialog and success/error toast to.
        default_filename: Suggested file name (without extension).
        image_source: Either a QWidget (captured via `.grab()`) or a
            matplotlib Figure (captured via `.savefig()`).
        csv_header: List of column names, or None to skip the CSV file.
        csv_rows: List of row tuples/lists matching csv_header.
    """
    path, selected = QFileDialog.getSaveFileName(
        parent, "Export", f"{default_filename}.pdf",
        "PDF Document (*.pdf);;PNG Image (*.png)",
    )
    if not path:
        return

    suffix = ".png" if "png" in selected.lower() else ".pdf"
    image_path = Path(path)
    if image_path.suffix.lower() not in (".pdf", ".png"):
        image_path = image_path.with_suffix(suffix)

    try:
        _render_image(image_source, image_path)

        saved = [image_path.name]
        if csv_header is not None:
            csv_path = image_path.with_suffix(".csv")
            _write_csv(csv_path, csv_header, csv_rows)
            saved.append(csv_path.name)

        Toast(parent, f"Exported {' and '.join(saved)}").show()
    except OSError as exc:
        Toast(parent, f"Export failed: {exc}", success=False).show()


def _report_pdf(out_path, title, header, rows):
    """A plain, self-contained report page: a heading and a two-or-more
    column table of *rows*. Rendered from HTML so it paginates and stays
    legible, unlike a screenshot of a widget that was never meant to be
    printed."""
    head_cells = "".join(f"<th>{html.escape(str(h))}</th>" for h in header)
    body = ""
    for row in rows:
        cells = "".join(
            f"<td>{'' if v is None else html.escape(str(v))}</td>" for v in row
        )
        body += f"<tr>{cells}</tr>"

    doc = QTextDocument()
    doc.setHtml(f"""
        <h2 style="font-family: sans-serif;">{html.escape(title or 'Report')}</h2>
        <table cellspacing="0" cellpadding="6" width="100%"
               style="font-family: sans-serif; font-size: 10pt; border-collapse: collapse;">
            <tr style="background:#eee;">{head_cells}</tr>
            {body}
        </table>
    """)

    writer = QPdfWriter(str(out_path))
    writer.setResolution(_PDF_DPI)
    writer.setPageLayout(QPageLayout(
        QPageSize(QPageSize.A4), QPageLayout.Portrait,
        QMarginsF(15, 15, 15, 15), QPageLayout.Millimeter,
    ))
    page = writer.pageLayout().paintRectPixels(writer.resolution())
    doc.setPageSize(page.size())
    doc.print_(writer)


def export_csv(parent, default_filename, csv_header, csv_rows, title=None):
    """
    Prompt for a save location, then write ``<name>.csv`` (*csv_rows* under
    *csv_header*) or, if the PDF filter is chosen, a formatted ``<name>.pdf``
    report of the same rows under *title*.

    For an export that's a report (e.g. project + model info + metrics)
    rather than a snapshot of some chart or table on screen.

    Args:
        parent: Widget to anchor the file dialog and success/error toast to.
        default_filename: Suggested file name (without extension).
        csv_header: List of column names.
        csv_rows: List of row tuples/lists matching csv_header.
        title: Heading for the PDF report (ignored for CSV).
    """
    path, selected = QFileDialog.getSaveFileName(
        parent, "Export", f"{default_filename}.pdf",
        "PDF Document (*.pdf);;CSV File (*.csv)",
    )
    if not path:
        return

    as_csv = "csv" in selected.lower()
    out_path = Path(path)
    if out_path.suffix.lower() not in (".pdf", ".csv"):
        out_path = out_path.with_suffix(".csv" if as_csv else ".pdf")

    try:
        if as_csv:
            _write_csv(out_path, csv_header, csv_rows)
        else:
            _report_pdf(out_path, title or default_filename, csv_header, csv_rows)
        Toast(parent, f"Exported {out_path.name}").show()
    except OSError as exc:
        Toast(parent, f"Export failed: {exc}", success=False).show()
