"""Train a first convolutional autoencoder on prepared DHC windows."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Codes.src.autoencoder import Conv1dAutoencoder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--windows",
        type=Path,
        default=ROOT
        / "Results"
        / "processed_data"
        / "autoencoder_windows_cons_hostatgeria_underfloor_hea.npz",
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--train-fraction", type=float, default=0.8)
    parser.add_argument("--models-dir", type=Path, default=ROOT / "Results" / "models")
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def reconstruction_errors(model: nn.Module, windows: torch.Tensor, batch_size: int) -> np.ndarray:
    loader = DataLoader(TensorDataset(windows), batch_size=batch_size, shuffle=False)
    errors: list[np.ndarray] = []
    model.eval()
    with torch.no_grad():
        for (batch,) in loader:
            reconstructed = model(batch)
            batch_error = ((reconstructed - batch) ** 2).mean(dim=(1, 2))
            errors.append(batch_error.cpu().numpy())
    return np.concatenate(errors)


def main() -> None:
    args = parse_args()
    data = np.load(args.windows, allow_pickle=True)
    windows_np = data["windows"].astype(np.float32)
    starts = pd.to_datetime(data["window_start"])
    feature_names = [str(value) for value in data["feature_names"]]

    split_index = max(1, int(len(windows_np) * args.train_fraction))
    train_np = windows_np[:split_index]
    all_windows = torch.from_numpy(windows_np)
    train_windows = torch.from_numpy(train_np)

    torch.manual_seed(42)
    model = Conv1dAutoencoder(channels=windows_np.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    loss_fn = nn.MSELoss()
    loader = DataLoader(TensorDataset(train_windows), batch_size=args.batch_size, shuffle=True)

    history: list[dict[str, float | int]] = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        losses: list[float] = []
        for (batch,) in loader:
            optimizer.zero_grad()
            reconstructed = model(batch)
            loss = loss_fn(reconstructed, batch)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
        history.append({"epoch": epoch, "train_loss": float(np.mean(losses))})
        print(f"epoch={epoch} train_loss={history[-1]['train_loss']:.6f}")

    errors = reconstruction_errors(model, all_windows, args.batch_size)
    threshold = float(np.quantile(errors[:split_index], 0.99))
    anomaly_flags = errors > threshold

    args.models_dir.mkdir(parents=True, exist_ok=True)
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    stem = args.windows.stem.replace("autoencoder_windows_", "")
    model_path = args.models_dir / f"autoencoder_{stem}.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "feature_names": feature_names,
            "means": data["means"],
            "stds": data["stds"],
            "threshold_train_p99": threshold,
            "windows_path": str(args.windows),
        },
        model_path,
    )

    scores = pd.DataFrame(
        {
            "window_start": starts,
            "reconstruction_mse": errors,
            "is_reconstruction_anomaly": anomaly_flags,
            "split": np.where(np.arange(len(errors)) < split_index, "train", "test"),
        }
    )
    scores_path = args.tables_dir / f"autoencoder_scores_{stem}.csv"
    history_path = args.tables_dir / f"autoencoder_training_history_{stem}.csv"
    summary_path = args.tables_dir / f"autoencoder_summary_{stem}.csv"
    figure_path = args.figures_dir / f"autoencoder_reconstruction_error_{stem}.png"
    scores.to_csv(scores_path, index=False)
    pd.DataFrame(history).to_csv(history_path, index=False)
    pd.DataFrame(
        [
            {
                "windows": len(windows_np),
                "train_windows": split_index,
                "test_windows": len(windows_np) - split_index,
                "features": ", ".join(feature_names),
                "threshold_train_p99": threshold,
                "flagged_windows": int(anomaly_flags.sum()),
                "model_path": model_path,
                "scores_path": scores_path,
                "figure_path": figure_path,
            }
        ]
    ).to_csv(summary_path, index=False)

    fig, axis = plt.subplots(figsize=(12, 5))
    axis.plot(scores["window_start"], scores["reconstruction_mse"], linewidth=0.8, label="Reconstruction MSE")
    flagged = scores[scores["is_reconstruction_anomaly"]]
    axis.scatter(
        flagged["window_start"],
        flagged["reconstruction_mse"],
        s=18,
        color="tab:red",
        label="Flagged window",
    )
    axis.axhline(threshold, color="tab:orange", linestyle="--", linewidth=1.0, label="Train p99 threshold")
    axis.set_title(f"Autoencoder reconstruction error: {stem}")
    axis.set_xlabel("Window start")
    axis.set_ylabel("MSE on normalized channels")
    axis.legend(loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)

    print(f"\nWrote model: {model_path}")
    print(f"Wrote scores: {scores_path}")
    print(f"Wrote summary: {summary_path}")
    print(f"Wrote figure: {figure_path}")


if __name__ == "__main__":
    main()
