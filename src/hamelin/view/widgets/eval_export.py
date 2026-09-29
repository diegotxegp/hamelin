"""
Evaluation export
~~~~~~~~~~~~~~~~~

Save dialogs for the Evaluation page: a chart or table as PNG/PDF (plus a CSV
of the numbers behind it) and a model report as CSV or PDF. Dialogs open in
the active project's results/reports/ folder (see hamelin.utils.export_paths).
"""

from __future__ import annotations

import csv
import html
from pathlib import Path

from PySide6.QtCore import QMarginsF, QRectF
from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter, QTextDocument
from PySide6.QtWidgets import QFileDialog, QWidget
from qfluentwidgets import InfoBar, InfoBarPosition
from PySide6.QtCore import Qt

from hamelin.utils.export_paths import default_export_path
from hamelin.utils.logger import log

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


def _notify(parent, ok: bool, text: str) -> None:
    (InfoBar.success if ok else InfoBar.error)(
        title="Exported" if ok else "Export failed", content=text,
        orient=Qt.Horizontal, isClosable=True,
        position=InfoBarPosition.TOP, duration=3500, parent=parent,
    )


def export_chart_and_data(parent, project_dir, default_name, image_source, header, rows) -> None:
    """Ask where to save, then write ``<name>.pdf|png`` of *image_source*
    (a QWidget or a matplotlib Figure) and ``<name>.csv`` with *rows*."""
    path, selected = QFileDialog.getSaveFileName(
        parent.window(), "Export", default_export_path(project_dir, "reports", f"{default_name}.png"),
        "PNG Image (*.png);;PDF Document (*.pdf)",
    )
    if not path:
        return
    image_path = Path(path)
    if image_path.suffix.lower() not in (".pdf", ".png"):
        image_path = image_path.with_suffix(".pdf" if "pdf" in selected.lower() else ".png")
    try:
        _render_image(image_source, image_path)
        saved = [image_path.name]
        if header is not None:
            csv_path = image_path.with_suffix(".csv")
            _write_csv(csv_path, header, rows)
            saved.append(csv_path.name)
        _notify(parent, True, " and ".join(saved))
    except OSError as exc:
        log.error(f"Export failed: {exc}")
        _notify(parent, False, str(exc))


def export_report(parent, project_dir, default_name, header, rows, title=None) -> None:
    """Ask where to save, then write *rows* as CSV or a formatted PDF."""
    path, selected = QFileDialog.getSaveFileName(
        parent.window(), "Export", default_export_path(project_dir, "reports", f"{default_name}.csv"),
        "CSV File (*.csv);;PDF Document (*.pdf)",
    )
    if not path:
        return
    as_pdf = "pdf" in selected.lower()
    out = Path(path)
    if out.suffix.lower() not in (".pdf", ".csv"):
        out = out.with_suffix(".pdf" if as_pdf else ".csv")
    try:
        if out.suffix.lower() == ".pdf":
            _report_pdf(out, title or default_name, header, rows)
        else:
            _write_csv(out, header, rows)
        _notify(parent, True, out.name)
    except OSError as exc:
        log.error(f"Export failed: {exc}")
        _notify(parent, False, str(exc))
