from pathlib import Path

from PySide6.QtCore import Qt, QSize, QRect, QPoint
from PySide6.QtGui import QMovie, QPainter, QColor, QPen, QBrush, QFont, QPolygon
from PySide6.QtWidgets import (
    QWidget, QPushButton, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
)

from hamelin.interface.utils.colors import BLUE, YELLOW, WHITE, BLACK, GRAY, colors, themed
from hamelin.interface.utils.explanation_widgets import make_section, make_header
from hamelin.interface.utils.theme_state import theme_state


class ConvolutionDiagram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        font = QFont()
        font.setPointSize(9)
        p.setFont(font)

        cell = max(16, min(22, (w - 320) // 18, (h - 90) // 6))
        rows, cols = 6, 6
        image_w, image_h = cols * cell, rows * cell

        feature_box = cell + 2
        feature_cluster_w = feature_box * 3 + (cell + 14) * 2
        kernel_box_w = 54
        total_w = image_w + 40 + kernel_box_w + 60 + feature_cluster_w

        grid_x = max(18, (w - total_w) // 2)
        grid_y = max(34, (h - image_h) // 2 - 16)

        p.setPen(QPen(QColor(colors().text), 1))
        for r in range(rows):
            for c in range(cols):
                shade = 40 + (r + c) * 3 if colors().dark else 245 - (r + c) * 3
                p.setBrush(QBrush(QColor(shade, shade, shade)))
                p.drawRect(grid_x + c * cell, grid_y + r * cell, cell, cell)

        p.setBrush(QBrush(QColor(YELLOW)))
        p.setPen(QPen(QColor(colors().text), 1))
        p.drawRect(grid_x + cell * 2, grid_y + cell, cell * 3, cell * 3)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(colors().muted), 2))
        p.drawRect(grid_x - 2, grid_y - 2, image_w + 4, image_h + 4)

        p.setPen(QPen(QColor(colors().text)))
        p.drawText(QRect(grid_x - 8, grid_y + image_h + 8, image_w + 16, 16), Qt.AlignCenter, "Input image")

        kernel_x = grid_x + image_w + 40
        kernel_box = QRect(kernel_x, grid_y + image_h // 2 - 27, kernel_box_w, kernel_box_w)
        p.setPen(QPen(QColor(colors().text), 1))
        p.setBrush(QBrush(QColor(BLUE)))
        p.drawRoundedRect(kernel_box, 8, 8)
        p.setPen(QPen(QColor(WHITE)))
        p.drawText(kernel_box, Qt.AlignCenter, "3×3\nfilter")

        p.setPen(QPen(QColor(colors().muted), 2))
        p.drawLine(grid_x + image_w + 18, grid_y + image_h // 2, kernel_box.left() - 10, kernel_box.center().y())
        arrow = QPolygon([
            QPoint(kernel_box.left() - 10, kernel_box.center().y() - 4),
            QPoint(kernel_box.left() - 2, kernel_box.center().y()),
            QPoint(kernel_box.left() - 10, kernel_box.center().y() + 4),
        ])
        p.setBrush(QBrush(QColor(colors().muted)))
        p.drawPolygon(arrow)
        p.setBrush(Qt.NoBrush)

        p.setPen(QPen(QColor(colors().text)))
        out_x = kernel_box.right() + 60
        p.drawText(QRect(out_x - 6, 20, 170, 18), Qt.AlignCenter, "Feature maps")
        for i in range(3):
            ox = out_x + i * (cell + 14)
            oy = grid_y + 8 + i * 7
            p.setBrush(QBrush(QColor(YELLOW if i == 1 else BLUE)))
            p.setPen(QPen(QColor(colors().text), 1))
            p.drawRect(ox, oy, cell + 2, cell + 2)
            p.setPen(QPen(QColor(WHITE if i != 1 else BLACK)))
            p.drawText(QRect(ox, oy, cell + 2, cell + 2), Qt.AlignCenter, str(i + 1))

        p.setPen(QPen(QColor(colors().muted), 2))
        p.drawLine(kernel_box.right() + 12, kernel_box.center().y(), out_x - 12, kernel_box.center().y())
        arrow2 = QPolygon([
            QPoint(out_x - 12, kernel_box.center().y() - 4),
            QPoint(out_x - 4, kernel_box.center().y()),
            QPoint(out_x - 12, kernel_box.center().y() + 4),
        ])
        p.setBrush(QBrush(QColor(colors().muted)))
        p.drawPolygon(arrow2)

        p.end()


class PipelineDiagram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        theme_state.themeChanged.connect(self.update)
        self.setFixedHeight(120)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        steps = ["Image", "Convolution", "ReLU", "Pooling", "Classifier"]
        n = len(steps)
        box_w = min(120, (w - 40) // n - 10)
        box_h = 42
        gap = (w - box_w * n) / (n + 1)
        y = (h - box_h) // 2 - 4

        font = QFont()
        font.setPointSize(9)
        p.setFont(font)

        centers = []
        for i, label in enumerate(steps):
            x = int(gap + i * (box_w + gap))
            rect = QRect(x, y, int(box_w), box_h)

            fill = QColor(BLUE) if i in (0, 4) else QColor(YELLOW)
            text_color = QColor(WHITE) if i in (0, 4) else QColor(BLACK)

            p.setPen(QPen(QColor(colors().text), 1))
            p.setBrush(QBrush(fill))
            p.drawRoundedRect(rect, 8, 8)

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
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        r = max(72, min((w - 170) // 2, (h - 70) // 2))

        steps = ["Predict", "Compare", "Measure loss", "Update filters"]
        box_w, box_h = 134, 46

        font = QFont()
        font.setPointSize(9)
        p.setFont(font)

        centers = []
        import math
        for angle in [90, 0, -90, 180]:
            rad = math.radians(angle)
            x = cx + r * math.cos(rad)
            y = cy - r * math.sin(rad)
            centers.append((x, y))

        p.setPen(QPen(QColor(colors().muted), 2))
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


class CNNVisualisationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Anchored to this file's own location, not the process's cwd -
        # see utils/widgets.py's ASSETS_DIR comment for why.
        self.gif_path = Path(__file__).resolve().parent.parent / "utils" / "generated_gifs" / "cnn.gif"
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
        # to spread the page out, so the three separate addStretch(1) calls
        # that used to do that job (splitting the leftover space into two
        # big dead gaps instead of using it) are gone.
        l1.setSpacing(28)

        l1.addLayout(make_header(
            "The Convolutional Neural Network (CNN)",
            "A neural network designed for images and spatial patterns"
        ))

        l1.addWidget(make_section(
            "What is it?",
            "A Convolutional Neural Network, often called a CNN, is a type of neural network "
            "made for understanding images and other data that has a spatial layout. In simple "
            "terms, it learns how to look at a picture, spot useful patterns inside it, and then "
            "use those patterns to make a prediction. For example, it can learn to recognise cats, "
            "dogs, handwritten digits, road signs, or any other object that appears in an image.",
            BLUE
        ))

        l1.addWidget(make_section(
            "How is it structured?",
            "A CNN is usually built in layers. The first layers look for very simple patterns, "
            "such as edges and corners. Later layers combine those simple patterns into more "
            "complex shapes, such as eyes, wheels, or letters. At the end, the network uses the "
            "patterns it has learned to decide what the image most likely contains. This layered "
            "design helps the model go from raw pixels to a useful answer.",
            GRAY
        ))

        l1.addWidget(make_section(
            "Why use a CNN?",
            "Images are not just a list of numbers. Nearby pixels often belong to the same object, "
            "and the position of a pattern matters. A CNN takes advantage of that structure by using "
            "small pattern detectors that slide across the image. Because the same detector is reused "
            "everywhere, the network stays much smaller than a model that connects everything to everything, "
            "and it is often better at learning visual patterns.",
            YELLOW
        ))

        # No alignment=Qt.AlignHCenter here - ConvolutionDiagram has no
        # sizeHint() override, so centering it would size it to (0, 220)
        # instead of stretching it to the row's width, making it
        # effectively invisible (its paintEvent draws centered within
        # whatever width it's actually given, so it's fine to let it fill
        # the row instead of forcing a specific width and centering that).
        l1.addWidget(ConvolutionDiagram())
        l1.addStretch(1)
        self.stack.addWidget(p1)

        p2 = QWidget()
        l2 = QVBoxLayout(p2)
        l2.setContentsMargins(10, 10, 10, 10)
        l2.setSpacing(10)

        l2.addLayout(make_header(
            "How it works and learns",
            "From convolution to classification"
        ))

        l2.addWidget(make_section(
            "Convolution",
            "The first important step is convolution. A small grid of numbers, called a filter or "
            "kernel, slides over the image little by little. At each position, it compares itself "
            "with the pixels underneath it and produces a value that shows how strongly a certain "
            "pattern is present. Different filters learn different patterns, so one filter may react "
            "to edges while another reacts to textures or simple shapes.",
            BLUE
        ))

        l2.addWidget(make_section(
            "Activation and pooling",
            "After convolution, the network usually applies an activation function. This is a simple "
            "mathematical rule that changes the output so the model can learn more complicated ideas. "
            "A very common activation is ReLU, short for Rectified Linear Unit. ReLU keeps positive values "
            "and turns negative values into zero, which helps the network keep useful information and "
            "discard weaker signals. After that, pooling reduces the size of the feature maps by keeping "
            "the strongest values in a small region. This makes the model lighter and helps it stay useful "
            "even if an object moves a little inside the image.",
            GRAY
        ))

        l2.addWidget(PipelineDiagram())

        l2.addWidget(make_section(
            "Training",
            "Training is the learning phase. The CNN makes a prediction, compares it with the correct "
            "answer, and measures how wrong it was. That mistake is called the loss. Then a method called "
            "backpropagation helps the network adjust its internal numbers so that the next prediction is "
            "a little better. This process is repeated many times with many examples, and the network slowly "
            "improves just like a student who keeps practising with feedback.",
            BLUE
        ))

        l2.addWidget(TrainingLoopDiagram())
        l2.addStretch()
        self.stack.addWidget(p2)

        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        l3.setContentsMargins(10, 10, 10, 10)
        l3.setSpacing(10)

        l3.addLayout(make_header(
            "Strengths and limitations",
            "Where CNNs shine, and where they are less suitable"
        ))

        l3.addStretch(1)

        l3.addWidget(make_section(
            "Strengths",
            "CNNs are especially strong when the data has a visual structure. They can learn directly "
            "from raw pixels without needing hand-made rules, and they reuse the same filters across the "
            "whole image, which makes them efficient. They also learn in stages: first small details, then "
            "larger shapes, and finally complete objects. This makes them very effective for tasks where the "
            "same object might appear in different positions.",
            BLUE
        ))

        l3.addStretch(1)

        l3.addWidget(make_section(
            "Limitations",
            "CNNs are not perfect for every problem. They often need many examples to learn well, and they "
            "can take more computer power than simpler models. Their performance also depends on design choices "
            "such as filter size, number of layers, and pooling strategy. For plain tables of numbers, where "
            "there is no image-like structure, other models are usually a better fit.",
            GRAY
        ))

        l3.addStretch(1)

        l3.addWidget(make_section(
            "Typical use cases",
            "CNNs are widely used for image classification, object detection, face recognition, medical image "
            "analysis, handwriting recognition, and other problems where nearby values form meaningful patterns.",
            YELLOW
        ))

        l3.addStretch(1)

        l3.addWidget(make_section(
            "A very short summary",
            "A CNN looks at small parts of an image, learns simple patterns first, combines those patterns "
            "into larger and more meaningful shapes, and then uses them to make a prediction. That is why it "
            "is one of the most useful models in computer vision.",
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
            "A complete example showing how a CNN sees an image"
        ))

        l4.addWidget(make_section(
            "What this example shows",
            "The animation uses a very small toy image so the idea is easy to follow. The image contains a "
            "simple shape, and the CNN uses a filter to scan it one small area at a time. When the filter "
            "finds the pattern it is looking for, it creates a strong response in the feature map. The example "
            "then shows how that information is reduced by pooling and how the loss becomes smaller as the model "
            "learns from repeated training steps.",
            GRAY
        ))

        l4.addWidget(make_section(
            "How to read it",
            "First, look at the input image and notice the filter sliding across it. Then watch the feature map "
            "to see where the pattern is strongest. Finally, look at the loss indicator: when training improves, "
            "the loss goes down, which means the model is making fewer mistakes.",
            BLUE
        ))

        self.gif_label = QLabel("Loading GIF...")
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gif_label.setMinimumHeight(650)
        themed(self.gif_label, lambda c: f"""
            QLabel {{
                background: {c.surface};
                border: 1px solid {c.muted};
                border-radius: 12px;
                color: {c.muted};
                font-size: 16px;
            }}
        """)

        l4.addWidget(self.gif_label, stretch=2)
        self.stack.addWidget(p4)

        self._load_gif()

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

        self.movie.setScaledSize(QSize(int(size.width() * scale), int(size.height() * scale)))

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