"""
Grid router — heatmap computation and position inspection.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from fastapi import APIRouter

from api.models import (
    GridRequest, GridResponse,
    InspectRequest, InspectResponse,
)

from viable_zones import (
    sweep_grid,
    sweep_grid_gradient,
    test_viable,
    test_sufficient,
    test_sustainable,
    raw_margins,
    cost_breakdown,
    compute_cap_floor,
    compute_ops_floor,
    PASS_THRESHOLD,
)

router = APIRouter(tags=["grid"])


# LRU cache for grid computations (keyed on immutable tuples)
@lru_cache(maxsize=32)
def _cached_grids(dims_tuple: tuple[int, ...], sliders_tuple: tuple[float, ...]):
    """Compute both grids and zone metrics, cached."""
    dims = list(dims_tuple)
    sliders = list(sliders_tuple)

    grid = sweep_grid(dims, sliders)
    gradient_grid = sweep_grid_gradient(dims, sliders)

    # Zone metrics from the combined layer
    combined = grid[:, :, 3]
    zone_mask = combined >= PASS_THRESHOLD
    zone_area = float(np.mean(zone_mask) * 100.0)

    # Cap/Ops ranges where zone is viable
    cap_positions = np.any(zone_mask, axis=0)
    ops_positions = np.any(zone_mask, axis=1)

    if np.any(cap_positions):
        cap_indices = np.where(cap_positions)[0]
        cap_range = [float(cap_indices[0]) / 100.0, float(cap_indices[-1]) / 100.0]
    else:
        cap_range = [0.0, 0.0]

    if np.any(ops_positions):
        ops_indices = np.where(ops_positions)[0]
        ops_range = [float(ops_indices[0]) / 100.0, float(ops_indices[-1]) / 100.0]
    else:
        ops_range = [0.0, 0.0]

    cap_floor = compute_cap_floor(dims)
    ops_floor = compute_ops_floor(dims)

    return grid, gradient_grid, zone_area, cap_range, ops_range, cap_floor, ops_floor


@router.post("/grid", response_model=GridResponse)
async def compute_grid(req: GridRequest):
    """Compute 101x101 heatmap grids for given dimensions + sliders."""
    dims_t = tuple(req.dimensions)
    sliders_t = tuple(req.sliders)

    grid, gradient_grid, zone_area, cap_range, ops_range, cap_floor, ops_floor = (
        _cached_grids(dims_t, sliders_t)
    )

    return GridResponse(
        grid=grid.tolist(),
        gradient_grid=gradient_grid.tolist(),
        zone_area=round(zone_area, 1),
        cap_range=cap_range,
        ops_range=ops_range,
        cap_floor=round(cap_floor, 3),
        ops_floor=round(ops_floor, 3),
    )


@router.post("/grid/inspect", response_model=InspectResponse)
async def inspect_position(req: InspectRequest):
    """Inspect a single Cap/Ops position: scores + cost breakdown."""
    dims = req.dimensions
    sliders = req.sliders

    v = test_viable(req.cap, req.ops, dims, sliders)
    s = test_sufficient(req.cap, req.ops, dims, sliders)
    u = test_sustainable(req.cap, req.ops, dims, sliders)
    vm, sm, um = raw_margins(req.cap, req.ops, dims, sliders)

    scores = {
        "viable": round(v, 4),
        "sufficient": round(s, 4),
        "sustainable": round(u, 4),
        "combined": round(min(v, s, u), 4),
        "margin": round(min(vm, sm, um), 4),
    }

    bd = cost_breakdown(req.cap, req.ops, dims, sliders)
    # Round all float values for clean JSON
    bd_clean = {}
    for k, val in bd.items():
        if isinstance(val, float):
            bd_clean[k] = round(val, 4)
        else:
            bd_clean[k] = val

    return InspectResponse(scores=scores, cost_breakdown=bd_clean)
