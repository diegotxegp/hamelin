from pathlib import Path

from PySide6.QtCore import Qt, QSize, QRect, QPoint
from PySide6.QtGui import QMovie, QPainter, QColor, QPen, QBrush, QFont, QPolygon
from PySide6.QtWidgets import (
    QWidget, QPushButton, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QLabel
)

from hamelin.interface.utils.colors import BLUE, YELLOW, WHITE, BLACK, GRAY, colors, themed
from hamelin.interface.utils.explanation_widgets import make_section, make_header
from hamelin.interface.utils.theme_state import theme_state


class LstmNetworkDiagram(QWidget):
    """Schematic: stacked recurrent layers with arrows looping between timesteps."""

    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)
        self.setFixedHeight(150)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        radius = 12

        layers = [3, 3, 2]  # input, recurrent, output
        labels = ["Input", "Recurrent layer", "Output"]
        x_positions = [w * (i + 1) / (len(layers) + 1) for i in range(len(layers))]

        positions = []
        for count, x in zip(layers, x_positions):
            ys = [h * (i + 1) / (count + 1) for i in range(count)]
            positions.append([(x, y) for y in ys])

        pen = QPen(QColor(colors().muted))
        pen.setWidth(1)
        p.setPen(pen)
        # forward connections
        for layer_a, layer_b in zip(positions, positions[1:]):
            for xa, ya in layer_a:
                for xb, yb in layer_b:
                    p.drawLine(int(xa), int(ya), int(xb), int(yb))

        # recurrent loop arrows inside the recurrent layer
        rlayer = positions[1]
        for x, y in rlayer:
            p.drawArc(int(x - 28), int(y - 28), 56, 56, 30 * 16, 120 * 16)

        for li, layer in enumerate(positions):
            color = QColor(YELLOW) if li == len(positions) - 1 else QColor(BLUE)
            p.setPen(QPen(QColor(colors().text), 1))
            p.setBrush(QBrush(color))
            for x, y in layer:
                p.drawEllipse(QPoint(int(x), int(y)), radius, radius)

        p.setPen(QPen(QColor(colors().muted)))
        font = QFont()
        font.setPointSize(9)
        p.setFont(font)
        for x, label in zip(x_positions, labels):
            rect = QRect(int(x) - 60, h - 18, 120, 16)
            p.drawText(rect, Qt.AlignCenter, label)

        p.end()


class LstmCellDiagram(QWidget):
    """Schematic of an LSTM cell showing gates: forget, input, output."""

    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)
        self.setFixedHeight(140)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        steps = ["Forget gate", "Input gate", "Candidate", "Output gate"]
        n = len(steps)
        box_w = min(130, (w - 40) // n - 10)
        box_h = 48
        gap = (w - box_w * n) / (n + 1)
        y = (h - box_h) // 2 - 6

        font = QFont()
        font.setPointSize(9)
        p.setFont(font)

        centers = []
        for i, label in enumerate(steps):
            x = int(gap + i * (box_w + gap))
            rect = QRect(x, y, int(box_w), box_h)

            fill = QColor(BLUE) if i in (0, 3) else QColor(YELLOW)
            p.setPen(QPen(QColor(colors().text), 1))
            p.setBrush(QBrush(fill))
            p.drawRoundedRect(rect, 8, 8)

            text_color = QColor(WHITE) if i in (0, 3) else QColor(BLACK)
            p.setPen(QPen(text_color))
            p.drawText(rect, Qt.AlignCenter, label)

            centers.append((x + box_w, y + box_h // 2))

        p.setPen(QPen(QColor(colors().muted), 2))
        p.setBrush(QBrush(QColor(colors().muted)))
        for i in range(len(centers) - 1):
            x1, cy = centers[i]
            x2 = x1 + int(gap)
            p.drawLine(x1, cy, x2 - 6, cy)
            arrow = QPolygon([
                QPoint(x2 - 6, cy - 4),
                QPoint(x2 + 2, cy),
                QPoint(x2 - 6, cy + 4),
            ])
            p.drawPolygon(arrow)

        p.end()


class TrainingLoopDiagram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)
        self.setFixedHeight(150)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 40

        steps = ["Forward (sequence)", "Compare", "Backprop through time", "Update weights"]
        box_w, box_h = 138, 40

        font = QFont()
        font.setPointSize(9)
        p.setFont(font)

        centers = []
        angles = [90, 0, -90, 180]
        import math
        for angle in angles:
            rad = math.radians(angle)
            x = cx + r * math.cos(rad)
            y = cy - r * math.sin(rad)
            centers.append((x, y))

        pen = QPen(QColor(colors().muted), 2)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        for i in range(len(centers)):
            x1, y1 = centers[i]
            x2, y2 = centers[(i + 1) % len(centers)]
            p.drawLine(int(x1), int(y1), int(x2), int(y2))
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            length = max((dx ** 2 + dy ** 2) ** 0.5, 1)
            dx, dy = dx / length, dy / length
            arrow = QPolygon([
                QPoint(int(mx - dy * 5 + dx * 5), int(my + dx * 5 + dy * 5)),
                QPoint(int(mx + dy * 5 + dx * 5), int(my - dx * 5 + dy * 5)),
                QPoint(int(mx - dx * 5), int(my - dy * 5)),
            ])
            p.setBrush(QBrush(QColor(colors().muted)))
            p.drawPolygon(arrow)
            p.setBrush(Qt.NoBrush)

        for i, (x, y) in enumerate(centers):
            rect = QRect(int(x - box_w / 2), int(y - box_h / 2), box_w, box_h)
            fill = QColor(BLUE) if i % 2 == 0 else QColor(YELLOW)
            text_color = QColor(WHITE) if i % 2 == 0 else QColor(BLACK)

            p.setPen(QPen(QColor(colors().text), 1))
            p.setBrush(QBrush(fill))
            p.drawRoundedRect(rect, 8, 8)

            p.setPen(QPen(text_color))
            p.drawText(rect, Qt.AlignCenter, steps[i])

        p.end()


class LSTMVisualisationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Anchored to this file's own location, not the process's cwd -
        # see utils/widgets.py's ASSETS_DIR comment for why.
        self.gif_path = Path(__file__).resolve().parent.parent / "utils" / "generated_gifs" / "lstm.gif"
        self.movie = None

        self.stack = QStackedWidget()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        themed(self, lambda c: f"""
            QWidget {{
                background: transparent;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {c.text};
            }}
        """)

        self._build_pages()
        root.addWidget(self.stack, stretch=1)

        bottom = QHBoxLayout()
        self.left_btn = QPushButton("←")
        self.right_btn = QPushButton("→")

        for b in (self.left_btn, self.right_btn):
            b.setFixedSize(44, 44)
            themed(b, lambda c: f"""
                QPushButton {{
                    background: {c.surface};
                    border-radius: 22px;
                    font-size: 18px;
                    font-weight: bold;
                    color: {c.text};
                    border: 1px solid {c.muted};
                }}
                QPushButton:hover {{
                    background: {c.line};
                    color: {WHITE};
                }}
                QPushButton:disabled {{
                    color: {c.muted};
                    background: {c.surface};
                }}
            """)

        bottom.addStretch()
        bottom.addWidget(self.left_btn)
        bottom.addWidget(self.right_btn)
        bottom.addStretch()

        root.addLayout(bottom)

        self.left_btn.clicked.connect(self.prev_page)
        self.right_btn.clicked.connect(self.next_page)

        self._update_buttons()

    def _build_pages(self):
        p1 = QWidget()
        l1 = QVBoxLayout(p1)
        l1.setContentsMargins(10, 10, 10, 10)
        # Wider than the original 10 - with the sections themselves grown
        # (see explanation_widgets.make_section), this is enough on its own
        # to spread the page out, so the addStretch(1) calls that used to
        # do that job between every element (leaving a big dead gap at the
        # bottom instead of actually using the space) are gone.
        l1.setSpacing(28)

        l1.addLayout(make_header(
            "The LSTM (Long Short-Term Memory)",
            "A recurrent cell designed to remember information over time"
        ))

        l1.addWidget(make_section(
            "What is an LSTM?",
            "An LSTM (Long Short-Term Memory) is a type of Recurrent Neural Network "
            "(RNN) designed to analyse sequential data. Unlike a traditional neural "
            "network, an LSTM can remember information from previous inputs while "
            "processing new ones. This allows it to understand how information evolves "
            "over time instead of analysing each observation independently.",
            BLUE
        ))

        l1.addWidget(make_section(
            "Why is it useful?",
            "Many real-world problems involve sequences rather than isolated values. "
            "Examples include ECG recordings, EEG signals, speech, written text, "
            "financial data, or patient monitoring. In these situations, previous "
            "observations often influence the interpretation of the current one. "
            "LSTMs are specifically designed to capture these temporal relationships.",
            GRAY
        ))

        l1.addWidget(make_section(
            "Key idea",
            "Instead of forgetting everything after each prediction, an LSTM keeps an "
            "internal memory. At every new timestep, it decides what information should "
            "be remembered, what should be discarded, and what should be passed to the "
            "next timestep.",
            BLUE
        ))

        l1.addWidget(LstmNetworkDiagram())
        l1.addStretch(1)
        self.stack.addWidget(p1)

        p2 = QWidget()
        l2 = QVBoxLayout(p2)
        l2.setContentsMargins(10, 10, 10, 10)
        l2.setSpacing(10)

        l2.addLayout(make_header(
            "How the LSTM cell works",
            "Gates control what is kept, written, and exposed at each step"
        ))

        l2.addStretch(1)

        l2.addWidget(make_section(
            "The memory of the LSTM",
            "The central component of an LSTM is its Cell State, which acts as a "
            "long-term memory. This memory travels through the entire sequence. "
            "At each timestep, the network updates this memory using three specialised "
            "gates that decide which information should be removed, stored, or exposed.",
            BLUE
        ))

        l2.addStretch(1)

        l2.addWidget(LstmCellDiagram())

        l2.addStretch(1)

        l2.addWidget(make_section(
            "The three gates",
            "• Forget Gate: removes information that is no longer useful.\n\n"
            "• Input Gate: decides which new information should be written into memory.\n\n"
            "• Output Gate: determines which information will be used to make the current prediction and passed to the next timestep.",
            GRAY
        ))

        l2.addStretch(1)

        l2.addWidget(make_section(
            "How the memory evolves",
            "Each new observation updates the memory. Useful information can remain "
            "stored for many timesteps, while irrelevant information is progressively "
            "forgotten. This ability allows LSTMs to model long-term dependencies "
            "within sequential data.",
            BLUE
        ))

        l2.addStretch(1)
        self.stack.addWidget(p2)



        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        l3.setContentsMargins(10, 10, 10, 10)
        l3.setSpacing(10)

        l3.addLayout(make_header(
            "Strengths, limitations and use cases",
            "Where LSTMs excel, and where they fall short"
        ))

        l3.addStretch(1)

        l3.addWidget(make_section(
            "Advantages",
            "• Learns relationships across time.\n"
            "• Can remember information over long sequences.\n"
            "• Handles variable-length inputs.\n"
            "• More resistant to vanishing gradients than standard RNNs.\n"
            "• Well suited for physiological signals such as ECGs or EEGs.",
            BLUE
        ))

        l3.addStretch(1)

        l3.addWidget(make_section(
            "Limitations",
            "• Training is computationally expensive.\n"
            "• Requires large labelled datasets.\n"
            "• Contains many parameters to optimise.\n"
            "• Modern Transformer architectures often achieve better performance on "
            "very large sequence modelling tasks.",
            GRAY
        ))

        l3.addStretch(1)

        l3.addWidget(make_section(
                "Examples of utilisation",
            "LSTMs are widely used whenever information is organised as a sequence. "
            "In healthcare, they can analyse ECG and EEG recordings, monitor vital "
            "signs in intensive care, predict blood glucose levels, or detect "
            "abnormal heart rhythms. Outside medicine, they are commonly used for "
            "speech recognition, language translation, handwriting recognition, "
            "financial time-series forecasting, and weather prediction. Their ability "
            "to remember previous observations makes them particularly effective for "
            "problems where the order of the data is important.",
            BLUE
        ))

        l3.addStretch(1)
        self.stack.addWidget(p3)




        p4 = QWidget()
        l4 = QVBoxLayout(p4)
        l4.setContentsMargins(10, 10, 10, 10)
        l4.setSpacing(10)

        l4.addLayout(make_header(
            "See it in action",
            "A visual walkthrough of the LSTM processing a sequence"
        ))

        l4.addWidget(make_section(
            "Example: learning from a sequence",
            "This animation shows an LSTM processing a sequence step by step. "
            "At each timestep, the gates update the cell state, deciding what "
            "to keep, what to discard, and what to expose as output. As "
            "training progresses, the network gradually adjusts its weights "
            "and the loss decreases.",
            BLUE
        ))

        self.gif_label = QLabel("Loading GIF...")
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setMinimumHeight(500)
        themed(self.gif_label, lambda c: f"""
            QLabel {{
                background: transparent;
                border: none;
                color: {c.muted};
            }}
        """)
        l4.addWidget(self.gif_label, stretch=1)
        self._load_gif()
        self.stack.addWidget(p4)

    def _load_gif(self):
        if not self.gif_path.exists():
            self.gif_label.setText("GIF not found")
            return

        self.movie = QMovie(str(self.gif_path))
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        self._scale_gif()

    def _scale_gif(self):
        if not self.movie:
            return

        probe = QMovie(str(self.gif_path))
        probe.jumpToFrame(0)
        size = probe.currentImage().size()

        if size.isEmpty():
            return

        w = max(1, self.gif_label.width() - 20)
        h = max(1, self.gif_label.height() - 20)

        scale = min(w / size.width(), h / size.height())

        self.movie.setScaledSize(
            QSize(int(size.width() * scale), int(size.height() * scale))
        )

    def prev_page(self):
        i = self.stack.currentIndex()
        self.stack.setCurrentIndex(max(0, i - 1))
        self._update_buttons()

    def next_page(self):
        i = self.stack.currentIndex()
        self.stack.setCurrentIndex(min(self.stack.count() - 1, i + 1))
        self._update_buttons()

    def _update_buttons(self):
        i = self.stack.currentIndex()
        self.left_btn.setEnabled(i > 0)
        self.right_btn.setEnabled(i < self.stack.count() - 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._scale_gif()
