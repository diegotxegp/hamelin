import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path


def generate_mlp_gif():

    # ───────────────────────────────
    # DARK THEME COLORS
    # ───────────────────────────────
    BG = "#121212"
    TEXT = "white"
    GRID = "#555555"
    AXIS = "#AAAAAA"

    # ───────────────────────────────
    # XOR DATASET
    # ───────────────────────────────
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    y = np.array([[0], [1], [1], [0]], dtype=float)

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    # Network architecture
    n_features = 2
    n_hidden = 4
    n_outputs = 1

    rng = np.random.default_rng(42)

    W1 = rng.normal(0, 2, (n_features, n_hidden))
    b1 = np.zeros((1, n_hidden))

    W2 = rng.normal(0, 2, (n_hidden, n_outputs))
    b2 = np.zeros((1, n_outputs))

    lr = 0.5
    n_epochs = 150

    W1_hist, W2_hist = [], []
    A1_hist, Y_hist = [], []
    loss_hist, acc_hist = [], []

    # ───────────────────────────────
    # TRAINING
    # ───────────────────────────────
    for _ in range(n_epochs):

        z1 = X @ W1 + b1
        a1 = sigmoid(z1)

        z2 = a1 @ W2 + b2
        y_pred = sigmoid(z2)

        eps = 1e-12

        loss = -np.mean(
            y * np.log(y_pred + eps)
            + (1 - y) * np.log(1 - y_pred + eps)
        )

        acc = np.mean((y_pred > 0.5) == y)

        dz2 = y_pred - y

        dW2 = a1.T @ dz2 / len(X)
        db2 = np.mean(dz2, axis=0, keepdims=True)

        da1 = dz2 @ W2.T
        dz1 = da1 * a1 * (1 - a1)

        dW1 = X.T @ dz1 / len(X)
        db1 = np.mean(dz1, axis=0, keepdims=True)

        W1 -= lr * dW1
        W2 -= lr * dW2

        b1 -= lr * db1
        b2 -= lr * db2

        W1_hist.append(W1.copy())
        W2_hist.append(W2.copy())

        A1_hist.append(a1.copy())
        Y_hist.append(y_pred.copy())

        loss_hist.append(loss)
        acc_hist.append(acc)


    # ───────────────────────────────
    # NETWORK POSITIONS
    # ───────────────────────────────
    input_pos = [
        (0, 1),
        (0, -1)
    ]

    hidden_pos = [
        (3, 2),
        (3, 0.7),
        (3, -0.7),
        (3, -2)
    ]

    output_pos = [
        (6, 0)
    ]


    # ───────────────────────────────
    # FIGURE
    # ───────────────────────────────
    fig = plt.figure(
        figsize=(16, 8),
        facecolor=BG
    )

    ax_net = plt.subplot(1, 2, 1)
    ax_plot = plt.subplot(1, 2, 2)

    ax_net.set_facecolor(BG)
    ax_plot.set_facecolor(BG)


    fig.suptitle(
        "MLP Training on XOR Problem",
        fontsize=32,
        fontweight="bold",
        color=TEXT
    )


    ax_net.set_title(
        "Neural Network (Forward Pass)",
        color=TEXT
    )

    ax_plot.set_title(
        "Training Metrics",
        color=TEXT
    )


    # ───────────────────────────────
    # DRAW NETWORK
    # ───────────────────────────────
    def draw_network(ax, W1, W2, a1, yhat, frame):

        ax.clear()
        ax.set_facecolor(BG)

        ax.set_xlim(-1.5, 8)
        ax.set_ylim(-4, 4)
        ax.axis("off")


        ax.axvline(
            4.2,
            color=GRID,
            lw=1,
            alpha=0.5
        )


        ax.text(
            0,
            3.3,
            "INPUT",
            ha="center",
            fontweight="bold",
            fontsize=24,
            color=TEXT
        )

        ax.text(
            3,
            3.3,
            "HIDDEN",
            ha="center",
            fontweight="bold",
            fontsize=24,
            color=TEXT
        )

        ax.text(
            6,
            3.3,
            "OUTPUT",
            ha="center",
            fontweight="bold",
            fontsize=24,
            color=TEXT
        )


        max_w = max(
            np.max(np.abs(W1)),
            np.max(np.abs(W2)),
            1e-8
        )


        # Connections input -> hidden
        for i, (x1, y1) in enumerate(input_pos):

            for j, (x2, y2) in enumerate(hidden_pos):

                w = W1[i, j]

                ax.plot(
                    [x1, x2],
                    [y1, y2],
                    color="royalblue" if w > 0 else "crimson",
                    lw=0.5 + 4.5 * abs(w) / max_w,
                    alpha=0.6
                )


        # Connections hidden -> output
        for j, (x1, y1) in enumerate(hidden_pos):

            for k, (x2, y2) in enumerate(output_pos):

                w = W2[j, k]

                ax.plot(
                    [x1, x2],
                    [y1, y2],
                    color="royalblue" if w > 0 else "crimson",
                    lw=0.5 + 4.5 * abs(w) / max_w,
                    alpha=0.6
                )


        # Neurons

        for i, (x, y_) in enumerate(input_pos):

            ax.scatter(
                x,
                y_,
                s=2000,
                color="white",
                edgecolor="black"
            )

            ax.text(
                x,
                y_ + 0.2,
                f"x{i+1}",
                color=TEXT,
                ha="center"
            )


        for j, (x, y_) in enumerate(hidden_pos):

            act = a1[0, j]

            ax.scatter(
                x,
                y_,
                s=2000,
                c=[act],
                cmap="viridis",
                vmin=0,
                vmax=1,
                edgecolor="black"
            )

            ax.text(
                x,
                y_,
                f"{act:.2f}",
                ha="center",
                fontsize=8,
                color=TEXT
            )

                    # Output neuron

        out = float(yhat[0, 0])

        ax.scatter(
            output_pos[0][0],
            output_pos[0][1],
            s=2400,
            c=[out],
            cmap="viridis",
            vmin=0,
            vmax=1,
            edgecolor="black"
        )

        ax.text(
            6,
            -1.2,
            f"pred: {1 if out > 0.5 else 0}",
            ha="center",
            fontweight="bold",
            color=TEXT
        )

        ax.text(
            -1,
            -3.5,
            f"epoch {frame+1}",
            fontsize=9,
            color=TEXT
        )



    # ───────────────────────────────
    # DRAW METRICS
    # ───────────────────────────────
    def draw_metrics(ax, frame):

        ax.clear()

        ax.set_facecolor(BG)

        ax.set_title(
            "Training Progress (Loss & Accuracy)",
            color=TEXT
        )

        ax.set_xlabel(
            "Epoch",
            color=TEXT
        )

        ax.set_ylabel(
            "Value",
            color=TEXT
        )


        ax.tick_params(
            colors=TEXT
        )

        for spine in ax.spines.values():
            spine.set_color(AXIS)


        ax.grid(
            True,
            alpha=0.3,
            color=GRID
        )


        epochs = np.arange(len(loss_hist))


        ax.plot(
            epochs[:frame+1],
            loss_hist[:frame+1],
            color="red",
            label="Loss"
        )


        ax.plot(
            epochs[:frame+1],
            acc_hist[:frame+1],
            color="green",
            label="Accuracy"
        )


        legend = ax.legend()

        for text in legend.get_texts():
            text.set_color(TEXT)



    # ───────────────────────────────
    # UPDATE ANIMATION
    # ───────────────────────────────
    def update(i):

        draw_network(
            ax_net,
            W1_hist[i],
            W2_hist[i],
            A1_hist[i],
            Y_hist[i],
            i
        )


        draw_metrics(
            ax_plot,
            i
        )



    # ───────────────────────────────
    # SAVE GIF
    # ───────────────────────────────
    anim = FuncAnimation(
        fig,
        update,
        frames=n_epochs,
        interval=80
    )


    # Anchored to this file's own location, not the process's cwd - a
    # relative "generated_gifs/" path only works when this script happens
    # to be run from the project root.
    out_dir = Path(__file__).resolve().parent.parent / "generated_gifs"
    out_dir.mkdir(
        exist_ok=True
    )


    out = str(out_dir / "mlp.gif")


    anim.save(
        out,
        writer="pillow",
        fps=15
    )


    plt.close(fig)


    print("Saved:", out)

    return out



if __name__ == "__main__":
    generate_mlp_gif()  