"""Independent, checkpoint-key-compatible CompNet + PalmBridge implementation.

Architecture reference: PalmBridge (arXiv:2601.20351) and the public X-Palm
benchmark description. No provider source, data, pretrained tensors or assets
are included. This module creates randomly initialized trainable weights.
"""
from __future__ import annotations

import math
from contextlib import contextmanager

import torch
from torch import nn
from torch.nn import functional as F

EMBED_DIM = 512
DICTIONARY_ROWS = 512
FILTER_COUNT = 32
FILTER_SIDE = 15
ROI_SIDE = 128


def normalize_gray(gray: torch.Tensor) -> torch.Tensor:
    """Normalize only positive pixels in each native uint8 gray-128 image."""
    if (
        gray.dtype != torch.uint8
        or gray.ndim != 3
        or gray.shape[0] == 0
        or gray.shape[1:] != (ROI_SIDE, ROI_SIDE)
    ):
        raise ValueError("expected nonempty uint8 (N, 128, 128) grayscale input")
    x = gray[:, None].to(torch.float32) / 255
    positive = x.ne(0)
    dims = (2, 3)
    count = positive.sum(dim=dims, keepdim=True)
    center = x.sum(dim=dims, keepdim=True) / count.clamp(min=1)
    diff = (x - center).masked_fill(~positive, 0)
    variance = diff.square().sum(dim=dims, keepdim=True) / (count - 1).clamp(min=1)
    return torch.where(count > 1, diff / (variance.sqrt() + 1e-6), x)


class OrientedKernelBank(nn.Module):
    """Learn one orientation, scale, period, anisotropy and phase per filter."""

    def __init__(self):
        super().__init__()
        self.theta = nn.Parameter(torch.linspace(0, math.pi, FILTER_COUNT + 1)[:-1])
        self.sigma = nn.Parameter(torch.ones(FILTER_COUNT) * 3)
        self.lambd = nn.Parameter(torch.ones(FILTER_COUNT) * 6)
        self.psi = nn.Parameter(torch.zeros(FILTER_COUNT))
        self.gamma = nn.Parameter(torch.ones(FILTER_COUNT) / 2)
        half = FILTER_SIDE // 2
        line = torch.arange(-half, half + 1, dtype=torch.float32)
        # Materialized grids also round-trip through safetensors for strict loading.
        self.register_buffer("xx", line[None].repeat(FILTER_SIDE, 1))
        self.register_buffer("yy", line[:, None].repeat(1, FILTER_SIDE))

    def kernels(self) -> torch.Tensor:
        angle = self.theta[:, None, None]
        major = torch.cos(angle) * self.xx + torch.sin(angle) * self.yy
        minor = torch.cos(angle) * self.yy - torch.sin(angle) * self.xx
        sigma = self.sigma.abs().clamp_min(0.5)[:, None, None]
        aspect = self.gamma.abs().clamp_min(0.1)[:, None, None]
        period = self.lambd.abs().clamp_min(1.0)[:, None, None]
        phase = self.psi[:, None, None]
        envelope = torch.exp(-(major.square() + aspect.square() * minor.square()) / (2 * sigma.square()))
        values = envelope * torch.cos(2 * math.pi * major / period + phase)
        return (values - values.mean(dim=(-2, -1), keepdim=True)).unsqueeze(1).contiguous()

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        return F.conv2d(image, self.kernels(), padding=FILTER_SIDE // 2)


class CollapsingResponse(nn.Module):
    def forward(self, responses: torch.Tensor) -> torch.Tensor:
        # max (not amax) has the historical first-winner gradient on exact ties.
        return responses.abs().max(dim=1, keepdim=True).values


class RegularBinMean(nn.Module):
    """Deterministic equivalent of adaptive mean pooling 16×16 to 4×4."""

    def forward(self, feature: torch.Tensor) -> torch.Tensor:
        if feature.ndim != 4 or feature.shape[-2:] != (16, 16):
            raise ValueError("the native CompNet pooling grid is 16×16")
        n, c = feature.shape[:2]
        return feature.reshape(n, c, 4, 4, 4, 4).mean(dim=(3, 5))


def _conv_stage(in_channels: int, out_channels: int) -> nn.Sequential:
    layers = []
    for incoming in (in_channels, out_channels):
        layers += [
            nn.Conv2d(incoming, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        ]
    return nn.Sequential(*layers)


class TextureEncoder(nn.Module):
    """Direction competition followed by four pyramidal convolution stages."""

    def __init__(self):
        super().__init__()
        self.gabor = OrientedKernelBank()
        self.compete = CollapsingResponse()
        self.gbn = nn.BatchNorm2d(1)
        widths = (1, 32, 64, 128, 256)
        for i, (incoming, outgoing) in enumerate(zip(widths, widths[1:]), 1):
            setattr(self, f"block{i}", _conv_stage(incoming, outgoing))
            if i < len(widths) - 1:
                setattr(self, f"pool{i}", nn.MaxPool2d(2, 2))
        self.gap = RegularBinMean()
        self.embed = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, EMBED_DIM, bias=False),
            nn.BatchNorm1d(EMBED_DIM),
        )
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode="fan_out")
            elif isinstance(module, nn.Linear):
                nn.init.xavier_normal_(module.weight)
            elif isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d)):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, pixels: torch.Tensor) -> torch.Tensor:
        features = self.gbn(self.compete(self.gabor(pixels).relu()))
        for stage in range(1, 5):
            features = getattr(self, f"block{stage}")(features)
            pooling = self.gap if stage == 4 else getattr(self, f"pool{stage}")
            features = pooling(features)
        return F.normalize(self.embed(features), dim=-1)


class CodewordBridge(nn.Module):
    """Nearest Euclidean codeword and fixed residual mixing (0.7 / 0.3)."""

    def __init__(self):
        super().__init__()
        self.P = nn.Parameter(F.normalize(torch.randn(DICTIONARY_ROWS, EMBED_DIM), dim=-1))

    def forward(self, z: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        powers = z.square().sum(dim=1, keepdim=True) + self.P.square().sum(dim=1)[None]
        nearest = (powers - 2 * torch.mm(z, self.P.T)).argmin(dim=-1)
        codeword = self.P.index_select(0, nearest)
        return z.mul(0.7).add(codeword.mul(0.3)), codeword, nearest

    def penalties(self, z: torch.Tensor, codeword: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        fit_codeword = (codeword - z.detach()).square().sum(dim=-1).mean()
        fit_embedding = (z - codeword.detach()).square().sum(dim=-1).mean()
        basis = F.normalize(self.P, dim=-1)
        correlation = basis.mm(basis.T)
        eye = torch.eye(DICTIONARY_ROWS, device=correlation.device, dtype=correlation.dtype)
        return fit_codeword + 0.25 * fit_embedding, (correlation - eye).square().mean()


@contextmanager
def _singleton_embedding_batchnorm(layer: nn.BatchNorm1d, batch: int):
    saved_mode = layer.training
    if batch == 1:
        # Do not fabricate a second example or suspend spatial BatchNorm.
        layer.eval()
    try:
        yield
    finally:
        layer.train(saved_mode)


class PalmBridgeE10(nn.Module):
    """Trainable reader. `forward` returns *unnormalized* bridged 512D features."""

    def __init__(self):
        super().__init__()
        self.trunk = TextureEncoder()
        self.bridge = CodewordBridge()

    def components(self, normalized: torch.Tensor):
        if normalized.ndim != 4 or normalized.shape[0] == 0 or normalized.shape[1:] != (1, ROI_SIDE, ROI_SIDE):
            raise ValueError("expected nonempty (N, 1, 128, 128) normalized images")
        with _singleton_embedding_batchnorm(self.trunk.embed[-1], normalized.shape[0]):
            z = self.trunk(normalized)
        bridged, codeword, nearest = self.bridge(z)
        return z, bridged, codeword, nearest

    def forward(self, normalized: torch.Tensor) -> torch.Tensor:
        return self.components(normalized)[1]

    def encode(self, gray: torch.Tensor) -> torch.Tensor:
        return self(normalize_gray(gray))

    def early_modules(self):
        return self.trunk.gabor, self.trunk.gbn, self.trunk.block1, self.trunk.block2

    def parameter_groups(self) -> dict[str, list[nn.Parameter]]:
        by_stage = {
            "early": self.early_modules(),
            "late": (self.trunk.block3, self.trunk.block4),
            "global": (self.trunk.embed,),
            "local": (self.bridge,),
        }
        return {key: [p for mod in modules for p in mod.parameters()] for key, modules in by_stage.items()}


def slot_dot(query: torch.Tensor, gallery: torch.Tensor) -> torch.Tensor:
    """Compare each probe to each registration slot using native float32 dots."""
    if (
        query.ndim != 2
        or gallery.ndim != 2
        or query.shape[1] != EMBED_DIM
        or gallery.shape[1] != EMBED_DIM
        or query.dtype != torch.float32
        or gallery.dtype != torch.float32
        or query.device != gallery.device
    ):
        raise ValueError("expected compatible float32 (N,512) slot arrays")
    return query.mm(gallery.T)
