"""Simulation API routes for recruitment ad budget optimization."""

from __future__ import annotations
from typing import List, Dict, Any
from fastapi import APIRouter

from backend.schemas import SimulationRequest, SimulationResponse, ChannelConfig
from src.optimizer.bandit import BanditSimulator, DEFAULT_CHANNELS

router = APIRouter(prefix="/api/v1", tags=["Budget Optimizer Simulation"])


@router.get("/channels", response_model=List[ChannelConfig])
def get_channels() -> List[ChannelConfig]:
    """Retrieve available recruitment channels and simulated baseline economics."""
    return [ChannelConfig(**c) for c in DEFAULT_CHANNELS]


@router.post("/simulate", response_model=SimulationResponse)
def run_budget_simulation(req: SimulationRequest) -> SimulationResponse:
    """Run comparative budget optimization simulation (Thompson Sampling vs Equal Split vs Benchmarks)."""
    channel_dicts = [c.model_dump() for c in req.channels] if req.channels else DEFAULT_CHANNELS

    simulator = BanditSimulator(
        channels=channel_dicts,
        total_budget=req.total_budget,
        days=req.days,
        seed=req.seed or 42
    )

    results = simulator.run_simulation()
    return SimulationResponse(**results)
