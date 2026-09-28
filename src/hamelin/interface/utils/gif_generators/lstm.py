import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from pathlib import Path


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def generate_lstm_gif():
    # Simple simulated LSTM-like dynamics for illustration
    rng = np.random.default_rng(3)
    seq_len = 30
    # synthetic input sequence (sinus + noise)
    t = np.linspace(0, 4 * np.pi, seq_len)
    inputs = 0.6 * np.sin(t) + rng.normal(0, 0.15, seq_len)

    # fake 'weights' matrix 3x3 that will slowly update
    W = rng.normal(0, 0.8, (3, 3))

    # cell state evolving using a toy rule: c_t = tanh(W @ [x_t, c_{t-1}, 1])
    c = np.zeros(3)
    states = []
    weights_hist = []

    for epoch in range(seq_len):
        x = np.array([inputs[epoch], 0.0, 1.0])
        c = np.tanh(W @ x)
        states.append(c.copy())
        weights_hist.append(W.copy())
        # pretend training: small random update
        W += rng.normal(0, 0.05, W.shape)

    states = np.array(states)
    weights_hist = np.array(weights_hist)

    fig = plt.figure(figsize=(10, 5), facecolor="#1a1a2e")
    gs = gridspec.GridSpec(2, 3, figure=fig, left=0.06, right=0.98, top=0.95, bottom=0.12, wspace=0.35, hspace=0.35)

    ax_in = fig.add_subplot(gs[0, 0:2])
    ax_state = fig.add_subplot(gs[1, 0:2])
    ax_w = fig.add_subplot(gs[:, 2])

    def style_ax(ax, title):
        ax.set_facecolor("#0f0f1a")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("#444466")
        ax.set_title(title, color="white", fontsize=10, fontweight="bold")

    style_ax(ax_in, "Input sequence")
    style_ax(ax_state, "Cell states (3 units)")
    style_ax(ax_w, "Weights (3×3)")

    line_in, = ax_in.plot([], [], color="#e7a600", lw=2)
    ax_in.set_xlim(0, seq_len)
    ax_in.set_ylim(inputs.min() - 0.5, inputs.max() + 0.5)
    ax_in.grid(True, alpha=0.2)

    lines = [ax_state.plot([], [], lw=2)[0] for _ in range(3)]
    ax_state.set_xlim(0, seq_len)
    ax_state.set_ylim(-1.2, 1.2)
    ax_state.grid(True, alpha=0.2)

    im = ax_w.imshow(weights_hist[0], cmap="coolwarm", vmin=-2.0, vmax=2.0)
    cb = fig.colorbar(im, ax=ax_w, fraction=0.08)

    def init():
        line_in.set_data([], [])
        for ln in lines:
            ln.set_data([], [])
        im.set_data(weights_hist[0])
        return [line_in, *lines, im]

    def update(frame):
        # show up to frame for inputs and states
        x = np.arange(frame + 1)
        line_in.set_data(x, inputs[: frame + 1])
        for i in range(3):
            lines[i].set_data(x, states[: frame + 1, i])

        im.set_data(weights_hist[frame])
        # overlay numeric values on the weight map
        ax_w.clear()
        style_ax(ax_w, "Weights (3×3)")
        im2 = ax_w.imshow(weights_hist[frame], cmap="coolwarm", vmin=-2.0, vmax=2.0)
        for (i, j), val in np.ndenumerate(weights_hist[frame]):
            ax_w.text(j, i, f"{val:+.2f}", ha="center", va="center", color="white" if abs(val) > 1.0 else "black", fontweight="bold")
        return [line_in, *lines, im2]

    anim = FuncAnimation(fig, update, frames=seq_len, init_func=init, blit=False, interval=200)
    # Anchored to this file's own location, not the process's cwd - a
    # relative "generated_gifs/" path only works when this script happens
    # to be run from the project root.
    out_dir = Path(__file__).resolve().parent.parent / "generated_gifs"
    out_dir.mkdir(exist_ok=True)
    out = str(out_dir / "lstm.gif")
    anim.save(out, writer="pillow", fps=6)
    plt.close(fig)
    print(f"Saved → {out}")
    return out


if __name__ == "__main__":
    generate_lstm_gif()
