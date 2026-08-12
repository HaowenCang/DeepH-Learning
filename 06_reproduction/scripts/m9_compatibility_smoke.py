#!/usr/bin/env python3
"""Deterministic CPU/CUDA compatibility smoke test for frozen DeepH v0.2.2.

This test deliberately exercises CUDA kernels from PyTorch, torch-scatter via
PyG, and e3nn.  It does not download data, train a model, or write artifacts.
"""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import json
import math
import platform

import numpy as np
import scipy
import torch
import torch_geometric
from e3nn import o3
from torch_geometric.nn import MessagePassing

import deeph
from deeph import get_config


SEED = 20260811


class SumMessages(MessagePassing):
    """Minimal PyG aggregation that exercises the torch-scatter CUDA path."""

    def __init__(self) -> None:
        super().__init__(aggr="add")

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        return self.propagate(edge_index, x=x)

    def message(self, x_j: torch.Tensor) -> torch.Tensor:
        return x_j


def finite(name: str, value: torch.Tensor) -> None:
    if not bool(torch.isfinite(value).all().item()):
        raise RuntimeError(f"{name} contains NaN or Inf")


def rounded(value: float) -> float:
    if not math.isfinite(value):
        raise RuntimeError("summary contains NaN or Inf")
    return float(f"{value:.10g}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if not torch.cuda.is_available():
        raise RuntimeError("torch.cuda.is_available() is false")
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cuda.matmul.allow_tf32 = False
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.allow_tf32 = False
    if hasattr(torch, "use_deterministic_algorithms"):
        torch.use_deterministic_algorithms(True)

    cpu_x = torch.arange(1, 13, dtype=torch.float64).reshape(3, 4)
    cpu_x.requires_grad_(True)
    cpu_w = torch.arange(1, 9, dtype=torch.float64).reshape(4, 2) / 10.0
    cpu_loss = torch.tanh(cpu_x @ cpu_w).square().sum()
    cpu_loss.backward()
    finite("cpu_loss", cpu_loss)
    finite("cpu_grad", cpu_x.grad)

    device = torch.device("cuda:0")
    cuda_x = torch.arange(1, 13, device=device, dtype=torch.float32).reshape(3, 4)
    cuda_x.requires_grad_(True)
    cuda_w = torch.arange(1, 9, device=device, dtype=torch.float32).reshape(4, 2) / 10.0
    cuda_loss = torch.tanh(cuda_x @ cuda_w).square().sum()
    cuda_loss.backward()
    torch.cuda.synchronize(device)
    finite("cuda_loss", cuda_loss)
    finite("cuda_grad", cuda_x.grad)

    # torch-scatter 2.0.9 does not declare scatter_add_cuda deterministic.
    # The values below are exactly representable integers, so this particular
    # finite sum is order-independent even though the legacy kernel itself is
    # outside PyTorch's global deterministic-algorithm allowlist.
    if hasattr(torch, "use_deterministic_algorithms"):
        torch.use_deterministic_algorithms(False)
    edge_index = torch.tensor(
        [[0, 1, 2, 0, 2], [1, 2, 0, 2, 1]], device=device, dtype=torch.long
    )
    node_x = torch.tensor(
        [[1.0, 2.0], [3.0, 5.0], [7.0, 11.0]], device=device, requires_grad=True
    )
    pyg_out = SumMessages().to(device)(node_x, edge_index)
    pyg_loss = pyg_out.square().sum()
    pyg_loss.backward()
    torch.cuda.synchronize(device)
    finite("pyg_out", pyg_out)
    finite("pyg_grad", node_x.grad)
    if hasattr(torch, "use_deterministic_algorithms"):
        torch.use_deterministic_algorithms(True)

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    irreps = o3.Irreps("1x0e + 1x1o")
    tensor_product = o3.FullyConnectedTensorProduct(irreps, irreps, irreps).to(device)
    left = torch.tensor(
        [[0.25, 0.5, -0.75, 1.0], [1.25, -1.5, 1.75, -2.0]],
        device=device,
        requires_grad=True,
    )
    right = torch.tensor(
        [[-0.5, 0.75, 1.0, -1.25], [1.5, -1.75, 2.0, 0.25]],
        device=device,
        requires_grad=True,
    )
    e3nn_out = tensor_product(left, right)
    e3nn_loss = e3nn_out.square().sum()
    e3nn_loss.backward()
    torch.cuda.synchronize(device)
    finite("e3nn_out", e3nn_out)
    finite("e3nn_left_grad", left.grad)
    finite("e3nn_right_grad", right.grad)

    config = get_config([args.config])
    if config.get("basic", "dataset_name") != "graphene":
        raise RuntimeError("official graphene config did not parse as graphene")
    if config.get("basic", "interface") != "npz":
        raise RuntimeError("official graphene config interface is not npz")
    ratios = [config.getfloat("train", key) for key in ("train_ratio", "val_ratio", "test_ratio")]
    if ratios != [0.6, 0.2, 0.2]:
        raise RuntimeError(f"unexpected official split ratios: {ratios}")

    capability = torch.cuda.get_device_capability(0)
    summary = {
        "compiled_cuda": torch.version.cuda,
        "cpu_grad_sum": rounded(cpu_x.grad.sum().item()),
        "cpu_loss": rounded(cpu_loss.item()),
        "cuda_capability": list(capability),
        "cuda_device": torch.cuda.get_device_name(0),
        "cuda_grad_sum": rounded(cuda_x.grad.sum().item()),
        "cuda_loss": rounded(cuda_loss.item()),
        "deeph": deeph.__version__,
        "e3nn": metadata.version("e3nn"),
        "e3nn_grad_sum": rounded(left.grad.sum().item() + right.grad.sum().item()),
        "e3nn_loss": rounded(e3nn_loss.item()),
        "numpy": np.__version__,
        "official_split": ratios,
        "platform": platform.machine(),
        "pyg": torch_geometric.__version__,
        "pyg_grad_sum": rounded(node_x.grad.sum().item()),
        "pyg_loss": rounded(pyg_loss.item()),
        "python": platform.python_version(),
        "scipy": scipy.__version__,
        "seed": SEED,
        "torch": torch.__version__,
    }
    if capability != (8, 9):
        raise RuntimeError(f"expected compute capability (8, 9), got {capability}")
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
