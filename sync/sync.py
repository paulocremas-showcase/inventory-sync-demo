"""Diff-and-push inventory sync: only pushes SKUs whose quantity actually
changed since the last successful sync, and zeroes out (rather than
silently drops) SKUs that disappeared from the local source, so a
delisted item's stock doesn't stay stale and sellable on the vendor side.
"""
from __future__ import annotations

import asyncio


def compute_delta(local_state: dict[str, int], last_synced_state: dict[str, int]) -> dict[str, int]:
    """Returns only what needs to be pushed: changed quantities, new SKUs,
    and zeroes for SKUs present last sync but missing now."""
    delta: dict[str, int] = {}

    for sku, qty in local_state.items():
        if last_synced_state.get(sku) != qty:
            delta[sku] = qty

    for sku in last_synced_state:
        if sku not in local_state:
            delta[sku] = 0

    return delta


async def run_sync(local_state: dict[str, int], last_synced_state: dict[str, int], client) -> dict[str, int]:
    delta = compute_delta(local_state, last_synced_state)
    await asyncio.gather(*(client.push(sku, qty) for sku, qty in delta.items()))

    new_synced_state = dict(last_synced_state)
    for sku, qty in delta.items():
        if qty == 0 and sku not in local_state:
            new_synced_state.pop(sku, None)
        else:
            new_synced_state[sku] = qty

    return new_synced_state
