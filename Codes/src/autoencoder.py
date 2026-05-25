"""PyTorch models for reconstruction-based time-series anomaly detection."""

from __future__ import annotations

import torch
from torch import nn


class Conv1dAutoencoder(nn.Module):
    """Small convolutional autoencoder for fixed-length multichannel windows."""

    def __init__(self, channels: int = 3, latent_channels: int = 16) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(channels, 16, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(16, latent_channels, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(latent_channels, 16, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose1d(16, channels, kernel_size=2, stride=2),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        encoded = self.encode(inputs)
        return self.decode(encoded)

    def encode(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.encoder(inputs)

    def decode(self, encoded: torch.Tensor) -> torch.Tensor:
        return self.decoder(encoded)
