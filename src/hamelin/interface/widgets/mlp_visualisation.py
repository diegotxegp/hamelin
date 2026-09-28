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


# ───────────────────────────────
# DIAGRAM 1 — NETWORK ARCHITECTURE (layers of neurons)
# ───────────────────────────────
class NetworkDiagram(QWidget):
    """Schematic: input layer -> hidden layer -> output layer, fully connected."""

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

        layers = [2, 3, 2, 1]  # input, hidden, hidden, output
        labels = ["Input", "Hidden", "Hidden", "Output"]
        x_positions = [w * (i + 1) / (len(layers) + 1) for i in range(len(layers))]

        # compute node positions
        positions = []
        for count, x in zip(layers, x_positions):
            ys = [h * (i + 1) / (count + 1) for i in range(count)]
            positions.append([(x, y) for y in ys])

        # connections
        pen = QPen(QColor(colors().muted))
        pen.setWidth(1)
        p.setPen(pen)
        for layer_a, layer_b in zip(positions, positions[1:]):
            for xa, ya in layer_a:
                for xb, yb in layer_b:
                    p.drawLine(int(xa), int(ya), int(xb), int(yb))

        # nodes
        for li, layer in enumerate(positions):
            color = QColor(YELLOW) if li == len(positions) - 1 else QColor(BLUE)
            p.setPen(QPen(QColor(colors().text), 1))
            p.setBrush(QBrush(color))
            for x, y in layer:
                p.drawEllipse(QPoint(int(x), int(y)), radius, radius)

        # labels
        p.setPen(QPen(QColor(colors().muted)))
        font = QFont()
        font.setPointSize(9)
        p.setFont(font)
        for x, label in zip(x_positions, labels):
            rect = QRect(int(x) - 40, h - 18, 80, 16)
            p.drawText(rect, Qt.AlignCenter, label)

        p.end()


# ───────────────────────────────
# DIAGRAM 2 — SINGLE NEURON COMPUTATION
# ───────────────────────────────
class NeuronDiagram(QWidget):
    """Schematic: inputs -> weighted sum + bias -> activation -> output."""

    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)
        self.setFixedHeight(110)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        steps = ["Inputs", "Weights + bias", "Activation", "Output"]
        n = len(steps)
        box_w = min(140, (w - 40) // n - 10)
        box_h = 46
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

        # arrows between boxes
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


# ───────────────────────────────
# DIAGRAM 3 — TRAINING LOOP
# ───────────────────────────────
class TrainingLoopDiagram(QWidget):
    """Schematic: predict -> compare -> error -> adjust -> back to predict."""

    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)
        self.setFixedHeight(260)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2

        steps = ["Predict", "Compare", "Measure error", "Adjust weights"]
        box_w, box_h = 130, 40
        # Radius must clear half the box width/height on every axis, or the
        # four boxes (placed at 90/0/-90/180 degrees) overlap in the middle.
        r = max(box_w / 2 + 30, min(w, h) // 2 - 40)

        font = QFont()
        font.setPointSize(9)
        p.setFont(font)

        centers = []
        angles = [90, 0, -90, 180]  # top, right, bottom, left (degrees)
        import math
        for angle in angles:
            rad = math.radians(angle)
            x = cx + r * math.cos(rad)
            y = cy - r * math.sin(rad)
            centers.append((x, y))

        # circular arrows between consecutive steps
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

        # step boxes
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


class MLPVisualisationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Anchored to this file's own location, not the process's cwd -
        # see utils/widgets.py's ASSETS_DIR comment for why.
        self.gif_path = Path(__file__).resolve().parent.parent / "utils" / "generated_gifs" / "mlp.gif"
        self.movie = None

        self.stack = QStackedWidget()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        # ───────────────────────────────
        # GLOBAL CLEAN STYLE (NO CARDS)
        # ───────────────────────────────
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

        # ───────────────────────────────
        # PAGES
        # ───────────────────────────────
        self._build_pages()

        root.addWidget(self.stack, stretch=1)

        # ───────────────────────────────
        # NAVIGATION
        # ───────────────────────────────
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

    # ───────────────────────────────
    # PAGES
    # ───────────────────────────────
    def _build_pages(self):

        # ─────────────────────────────
        # PAGE 1 — WHAT IS AN MLP + HOW IT'S STRUCTURED
        # ─────────────────────────────
        p1 = QWidget()
        l1 = QVBoxLayout(p1)
        l1.setContentsMargins(10, 10, 10, 10)
        l1.setSpacing(10)

        l1.addLayout(make_header(
            "The Multi-Layer Perceptron (MLP)",
            ""
        ))

        l1.addWidget(make_section(
            "What is it?",
            "A Multi-Layer Perceptron is one of the simplest and oldest types "
            "of artificial neural networks. It learns patterns directly from "
            "data by adjusting internal parameters, and can then use what it "
            "learned to make predictions on new, unseen examples.\n\n"
            "It is widely used for classification (sorting things into "
            "categories), regression (predicting a numeric value), and other "
            "general pattern recognition tasks.",
            BLUE
        ))

        l1.addWidget(make_section(
            "How is it structured?",
            "An MLP is organised into layers of neurons, stacked one after "
            "another:\n\n"
            "• Input layer : receives the raw data (the features describing "
            "an example)\n"
            "• Hidden layer(s) : transform and combine that information, "
            "extracting increasingly abstract patterns\n"
            "• Output layer : produces the final prediction\n\n"
            "It is called fully connected because every neuron in one "
            "layer is linked to every neuron in the next ",
            GRAY
        ))

        diagram1 = NetworkDiagram()
        l1.addWidget(diagram1)

        l1.addStretch()
        self.stack.addWidget(p1)

        # ─────────────────────────────
        # PAGE 2 — HOW IT WORKS + TRAINING
        # ─────────────────────────────
        p2 = QWidget()
        l2 = QVBoxLayout(p2)
        l2.setContentsMargins(10, 10, 10, 10)
        l2.setSpacing(10)

        l2.addLayout(make_header(
            "How it works and learns",
            "From a single calculation to a trained model"
        ))

        l2.addWidget(make_section(
            "Inside a neuron",
            "Each connection between neurons carries a weight, and every "
            "neuron adds a bias. For every neuron:\n\n"
            "1. Each incoming value is multiplied by its weight\n"
            "2. All the results are summed, and a bias is added\n"
            "3. The sum passes through an activation function, which "
            "introduces non-linearity\n\n"
            "This calculation is repeated layer after layer, letting the "
            "network build increasingly complex representations of the data.",
            BLUE
        ))

        diagram2 = NeuronDiagram()
        l2.addWidget(diagram2)

        l2.addWidget(make_section(
            "Training: how it learns",
            "Training is the process of teaching the network to make better "
            "predictions:\n\n"
            "• The model makes a prediction from an example\n"
            "• That prediction is compared to the correct answer\n"
            "• The difference (the error) is measured with a loss function\n"
            "• Backpropagation uses that error to adjust every weight, "
            "moving the network's predictions closer to the truth\n\n"
            "Repeated over many examples and many passes, this process "
            "gradually improves the model's accuracy.",
            GRAY
        ))

        diagram3 = TrainingLoopDiagram()
        l2.addWidget(diagram3)

        l2.addStretch()
        self.stack.addWidget(p2)

                # ─────────────────────────────
        # PAGE 3 — APPLICATIONS, STRENGTHS & LIMITATIONS
        # ─────────────────────────────
        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        l3.setContentsMargins(10, 10, 10, 10)
        l3.setSpacing(10)

        l3.addLayout(make_header(
            "Applications, strengths and limitations",
            "Where MLPs are useful and what are their main challenges"
        ))

        l3.addWidget(make_section(
            "Applications and examples",
            "MLPs are widely used for problems where the input data can be "
            "represented as a fixed set of numerical features.\n\n"
            "• Classification: recognising categories from data, such as "
            "detecting whether an email is spam, identifying fraudulent "
            "transactions, or predicting whether a medical examination "
            "corresponds to a healthy or abnormal case.\n\n"
            "• Regression: predicting continuous values, for example "
            "estimating house prices, forecasting energy consumption, "
            "or predicting patient-related measurements from clinical data.\n\n"
            "• Pattern recognition: analysing structured information such "
            "as customer behaviour, sensor measurements, industrial data, "
            "or biological signals.",
            BLUE
        ))

        l3.addWidget(make_section(
            "Strengths",
            "MLPs are one of the most fundamental neural network architectures "
            "and remain useful because of their simplicity and flexibility.\n\n"
            "• They are easy to understand and implement, making them a common "
            "starting point when developing machine learning models.\n\n"
            "• They can approximate complex mathematical relationships thanks "
            "to their multiple layers and non-linear activation functions.\n\n"
            "• They work well on structured or tabular datasets where each "
            "input feature has a clear meaning.\n\n"
            "• They can be adapted to many different tasks by changing their "
            "architecture and output layer.",
            GRAY
        ))

        l3.addWidget(make_section(
            "Limitations",
            "Despite their usefulness, MLPs have several important limitations.\n\n"
            "• They do not naturally understand spatial relationships, making "
            "them less effective than Convolutional Neural Networks (CNNs) "
            "for image analysis.\n\n"
            "• They do not keep information from previous inputs, which makes "
            "them unsuitable for many sequential problems such as speech or "
            "time-series analysis.\n\n"
            "• Large MLPs can require many parameters, increasing training "
            "time and the risk of overfitting (which means the model performs "
            "well on training data but poorly on unseen data because it has "
            "memorized the specific examples instead of learning generalizable "
            "patterns).\n\n"
            "• Their performance depends strongly on choices such as the number "
            "of layers, learning rate, and amount of training data.",
            BLUE
        ))

        l3.addStretch()
        self.stack.addWidget(p3)

                # ─────────────────────────────
        # PAGE 4 — GIF
        # ─────────────────────────────
        p4 = QWidget()
        l4 = QVBoxLayout(p4)
        l4.setContentsMargins(10, 10, 10, 10)
        l4.setSpacing(10)

        l4.addLayout(make_header(
            "See it in action",
            "A visual walkthrough of the network learning process"
        ))

        l4.addWidget(make_section(
            "Example: learning the XOR problem",
            "This animation illustrates how an MLP learns to solve the classical "
            "XOR problem.\n\n"
            "Each epoch, the network performs a forward pass to produce a prediction, "
            "compares it with the expected output, and updates its weights using "
            "backpropagation. As training progresses, the connections evolve, the "
            "loss decreases, and the predictions become increasingly accurate.",
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

        l4.addWidget(
            self.gif_label,
            stretch=1
        )

        self.stack.addWidget(p4)

        self._load_gif()

    # ───────────────────────────────
    # GIF
    # ───────────────────────────────
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

        scale = min(w / size.width(), h / size.height())*1.6

        self.movie.setScaledSize(
            QSize(int(size.width() * scale), int(size.height() * scale))
        )

    # ───────────────────────────────
    # NAVIGATION
    # ───────────────────────────────
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

    # ───────────────────────────────
    # RESIZE
    # ───────────────────────────────
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._scale_gif()