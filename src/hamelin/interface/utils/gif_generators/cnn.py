import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# DATASET  –  two 8×8 checkerboard variants
#   Class 0 : standard checkerboard  (top-left cell = black)
#   Class 1 : inverted checkerboard  (top-left cell = white)
# ─────────────────────────────────────────────────────────────────────────────
def make_checkerboard(size=8, inverted=False):
    board = np.zeros((size, size), dtype=float)
    for r in range(size):
        for c in range(size):
            if (r + c) % 2 == 0:
                board[r, c] = 1.0
    return 1.0 - board if inverted else board


def make_dataset(n_per_class=8):
    rng = np.random.default_rng(0)
    images, labels = [], []
    for _ in range(n_per_class):
        noise = rng.normal(0, 0.35, (8, 8))
        images.append(np.clip(make_checkerboard(inverted=False) + noise, 0, 1))
        labels.append(0)
    for _ in range(n_per_class):
        noise = rng.normal(0, 0.35, (8, 8))
        images.append(np.clip(make_checkerboard(inverted=True) + noise, 0, 1))
        labels.append(1)
    idx = rng.permutation(len(images))
    X = np.array(images)[idx]        
    y = np.array(labels)[idx]          
    return X, y


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def relu(x):
    return np.maximum(0, x)


def relu_grad(x):
    return (x > 0).astype(float)


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -50, 50)))


def conv2d(image, kernel, stride=1):
    kh, kw   = kernel.shape
    ih, iw   = image.shape
    oh = (ih - kh) // stride + 1
    ow = (iw - kw) // stride + 1
    out = np.zeros((oh, ow))
    for r in range(oh):
        for c in range(ow):
            patch     = image[r*stride:r*stride+kh, c*stride:c*stride+kw]
            out[r, c] = np.sum(patch * kernel)
    return out


def max_pool2d(feature_map, size=2):
    h, w   = feature_map.shape
    oh, ow = h // size, w // size
    out    = np.zeros((oh, ow))
    for r in range(oh):
        for c in range(ow):
            out[r, c] = np.max(feature_map[r*size:(r+1)*size, c*size:(c+1)*size])
    return out


# ─────────────────────────────────────────────────────────────────────────────
# FORWARD PASS 
# ─────────────────────────────────────────────────────────────────────────────
def forward(image, kernel, W_fc, b_fc):
    conv_raw = conv2d(image, kernel)                
    conv_act = relu(conv_raw)                        

    pooled   = max_pool2d(conv_act)             

    flat     = pooled.flatten()                    

    logit    = float(W_fc @ flat + b_fc)
    prob     = sigmoid(logit)
    return conv_raw, conv_act, pooled, flat, logit, prob


# ───────────────────────────────────────────────────────────────────────
# BACKWARD PASS
# ───────────────────────────────────────────────────────────────────────
def backward(image, kernel, W_fc, b_fc, label, lr=0.05):
    conv_raw, conv_act, pooled, flat, logit, prob = forward(image, kernel, W_fc, b_fc)

    d_logit = prob - label                        

    d_W_fc  = d_logit * flat                        
    d_b_fc  = d_logit                               
    d_flat  = d_logit * W_fc                         

    d_pooled = d_flat.reshape(pooled.shape)         

    pool_size  = 2
    kh, kw     = kernel.shape
    ih, iw     = image.shape
    oh_c, ow_c = ih - kh + 1, iw - kw + 1           
    d_conv_act = np.zeros((oh_c, ow_c))
    conv_act_  = relu(conv2d(image, kernel))
    for r in range(pooled.shape[0]):
        for c in range(pooled.shape[1]):
            block = conv_act_[r*pool_size:(r+1)*pool_size,
                              c*pool_size:(c+1)*pool_size]
            mr, mc = np.unravel_index(np.argmax(block), block.shape)
            d_conv_act[r*pool_size + mr, c*pool_size + mc] = d_pooled[r, c]

    d_conv_raw = d_conv_act * relu_grad(conv2d(image, kernel))

    d_kernel = np.zeros_like(kernel)
    for r in range(oh_c):
        for c in range(ow_c):
            patch        = image[r:r+kh, c:c+kw]
            d_kernel    += d_conv_raw[r, c] * patch

    kernel_new = kernel - lr * d_kernel
    W_fc_new   = W_fc   - lr * d_W_fc
    b_fc_new   = b_fc   - lr * d_b_fc

    loss = -( label * np.log(prob + 1e-12) + (1 - label) * np.log(1 - prob + 1e-12) )
    pred = int(prob > 0.5)
    return kernel_new, W_fc_new, b_fc_new, loss, pred


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING LOOP 
# ─────────────────────────────────────────────────────────────────────────────
def train(X, y, n_epochs=60, lr=0.05):
    rng    = np.random.default_rng(7)

    kernel = rng.normal(0, 0.5, (3, 3))
    W_fc   = rng.normal(0, 0.3, (9,))
    b_fc   = 0.0

    history = []   

    for epoch in range(n_epochs):
        epoch_loss, epoch_correct = 0.0, 0
        for img, lbl in zip(X, y):
            kernel, W_fc, b_fc, loss, pred = backward(img, kernel, W_fc, b_fc, lbl, lr)
            epoch_loss    += loss
            epoch_correct += int(pred == lbl)

        # Pick the first training image for the visualisation snapshot
        conv_raw, conv_act, pooled, flat, logit, prob = forward(X[0], kernel, W_fc, b_fc)

        history.append({
            "epoch"    : epoch,
            "kernel"   : kernel.copy(),
            "conv_raw" : conv_raw.copy(),
            "conv_act" : conv_act.copy(),
            "pooled"   : pooled.copy(),
            "loss"     : epoch_loss / len(X),
            "accuracy" : epoch_correct / len(X),
            "prob"     : prob,
        })

    return history


# ──────────────────────────────────────────────────────────
# PHASE 1
# ────────────────────────────────────────────────────────────────────
def make_sliding_frames(image, kernel):
    kh, kw   = kernel.shape
    ih, iw   = image.shape
    oh, ow   = ih - kh + 1, iw - kw + 1
    frames   = []
    conv_so_far = np.full((oh, ow), np.nan)
    for r in range(oh):
        for c in range(ow):
            patch              = image[r:r+kh, c:c+kw]
            val                = float(np.sum(patch * kernel))
            conv_so_far[r, c]  = val
            frames.append((r, c, conv_so_far.copy()))
    return frames



CMAP_IMG    = "gray"
CMAP_FEAT   = "RdYlGn"   
CMAP_KERNEL = "coolwarm"

def add_grid(ax, nrows, ncols, color="white", lw=0.5):
    for r in range(nrows + 1):
        ax.axhline(r, color=color, lw=lw)
    for c in range(ncols + 1):
        ax.axvline(c, color=color, lw=lw)


# ──────────────────────────────────────────────────────────
# SLIDING FRAMES
# ────────────────────────────────────────────────────────────────────
def make_sliding_frames(image, kernel):
    """Generate frames showing the kernel sliding over the image."""
    kh, kw   = kernel.shape
    ih, iw   = image.shape
    oh, ow   = ih - kh + 1, iw - kw + 1
    frames   = []
    for r in range(oh):
        for c in range(ow):
            frames.append((r, c))
    return frames


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def generate_cnn_gif():
    X, y     = make_dataset(n_per_class=8)
    history  = train(X, y, n_epochs=40, lr=0.05)
    demo_img = X[0]

    init_kernel    = history[0]["kernel"]
    sliding_frames = make_sliding_frames(demo_img, init_kernel)
    n_slide        = min(12, len(sliding_frames))  # Just show first 12 positions
    n_train        = len(history)

    total_frames = n_slide + n_train

    # ── Simple layout: left = image/kernel, right = loss
    fig = plt.figure(figsize=(12, 5), facecolor="#1a1a2e")
    gs = gridspec.GridSpec(2, 2, figure=fig, left=0.08, right=0.95, top=0.90, bottom=0.12, wspace=0.3, hspace=0.35)

    ax_img   = fig.add_subplot(gs[0, 0])
    ax_kern  = fig.add_subplot(gs[1, 0])
    ax_loss  = fig.add_subplot(gs[:, 1])

    def style_ax(ax, title):
        ax.set_facecolor("#0f0f1a")
        ax.tick_params(colors="white", labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor("#444466")
        ax.set_title(title, color="white", fontsize=10, fontweight="bold")

    fig_title = fig.text(0.5, 0.96, "", ha="center", fontsize=13, fontweight="bold", color="white")

    def draw_frame(frame_idx):
        if frame_idx < n_slide:
            # Phase 1: sliding
            fig_title.set_text("CNN: Kernel sliding across the image")
            r_pos, c_pos = sliding_frames[frame_idx]

            ax_img.clear()
            ax_img.imshow(demo_img, cmap=CMAP_IMG, vmin=0, vmax=1, origin="upper", aspect="equal")
            ax_img.set_xlim(0, 8)
            ax_img.set_ylim(8, 0)
            add_grid(ax_img, 8, 8, lw=0.4)
            rect = Rectangle((c_pos, r_pos), 3, 3, linewidth=2, edgecolor="#ffdd57", facecolor="none", zorder=5)
            ax_img.add_patch(rect)
            style_ax(ax_img, "Input (8×8)")
            ax_img.set_xticks([])
            ax_img.set_yticks([])

            ax_kern.clear()
            km = init_kernel
            ax_kern.imshow(km, cmap=CMAP_KERNEL, vmin=-np.abs(km).max(), vmax=np.abs(km).max(), origin="upper", aspect="equal")

            vext_slide = max(np.abs(km).max(), 1e-6)
            for rr in range(km.shape[0]):
                for cc in range(km.shape[1]):
                    val = km[rr, cc]
                    txt_color = "white" if abs(val) > (vext_slide * 0.5) else "black"
                    ax_kern.text(cc + 0.5, rr + 0.5, f"{val:+.2f}", ha="center", va="center", color=txt_color, fontsize=9, fontweight="bold")
            ax_kern.set_xlim(0, 3)
            ax_kern.set_ylim(3, 0)
            add_grid(ax_kern, 3, 3, lw=0.4)
            style_ax(ax_kern, "Filter (3×3)")
            ax_kern.set_xticks([])
            ax_kern.set_yticks([])

            ax_loss.clear()
            ax_loss.set_facecolor("#0f0f1a")
            ax_loss.text(0.5, 0.5, "Training not started", transform=ax_loss.transAxes, ha="center", va="center", color="#555577", fontsize=11)
            ax_loss.axis("off")

        else:
            # Phase 2: training
            h_idx = frame_idx - n_slide
            snap = history[h_idx]
            
            fig_title.set_text(f"CNN: Training progress (epoch {h_idx+1}/{n_train})")

            ax_img.clear()
            ax_img.imshow(demo_img, cmap=CMAP_IMG, vmin=0, vmax=1, origin="upper", aspect="equal")
            ax_img.set_xlim(0, 8)
            ax_img.set_ylim(8, 0)
            add_grid(ax_img, 8, 8, lw=0.4)
            style_ax(ax_img, "Input (8×8)")
            ax_img.set_xticks([])
            ax_img.set_yticks([])

            ax_kern.clear()
            km = snap["kernel"]
            vext = max(np.abs(km).max(), 1e-3)
            ax_kern.imshow(km, cmap=CMAP_KERNEL, vmin=-vext, vmax=vext, origin="upper", aspect="equal")
            ax_kern.set_xlim(0, 3)
            ax_kern.set_ylim(3, 0)
            add_grid(ax_kern, 3, 3, lw=0.4)
            style_ax(ax_kern, "Learned Filter")
            ax_kern.set_xticks([])
            ax_kern.set_yticks([])
            # Overlay raw kernel values so changes are visible numerically
            for rr in range(km.shape[0]):
                for cc in range(km.shape[1]):
                    val = km[rr, cc]
                    txt_color = "white" if abs(val) > (vext * 0.5) else "black"
                    ax_kern.text(cc + 0.5, rr + 0.5, f"{val:+.2f}", ha="center", va="center", color=txt_color, fontsize=9, fontweight="bold")

            ax_loss.clear()
            losses = [h["loss"] for h in history[:h_idx+1]]
            accs = [h["accuracy"] * 100 for h in history[:h_idx+1]]
            
            ax_loss.plot(range(len(losses)), losses, color="#e74c3c", lw=2.5, label="Loss")
            ax_loss2 = ax_loss.twinx()
            ax_loss2.plot(range(len(accs)), accs, color="#2ecc71", lw=2.5, label="Accuracy")
            
            ax_loss.set_facecolor("#0f0f1a")
            ax_loss2.set_facecolor("#0f0f1a")
            ax_loss.tick_params(colors="white", labelsize=8)
            ax_loss2.tick_params(colors="white", labelsize=8)
            ax_loss.set_xlabel("Epoch", color="white", fontsize=9)
            ax_loss.set_ylabel("Loss", color="#e74c3c", fontsize=9)
            ax_loss2.set_ylabel("Accuracy %", color="#2ecc71", fontsize=9)
            
            for spine in ax_loss.spines.values():
                spine.set_edgecolor("#444466")
            for spine in ax_loss2.spines.values():
                spine.set_edgecolor("#444466")
            
            ax_loss.set_ylim(0, max(losses) * 1.2)
            ax_loss2.set_ylim(0, 110)
            ax_loss.grid(True, alpha=0.2, color="white")

    anim = FuncAnimation(fig, draw_frame, frames=total_frames, interval=250)
    # Anchored to this file's own location, not the process's cwd - a
    # relative "generated_gifs/" path only works when this script happens
    # to be run from the project root.
    out_dir = Path(__file__).resolve().parent.parent / "generated_gifs"
    out_dir.mkdir(exist_ok=True)
    output = str(out_dir / "cnn.gif")
    anim.save(output, writer="pillow", fps=4)
    plt.close(fig)
    print(f"Saved → {output}")
    return output


if __name__ == "__main__":
    generate_cnn_gif()