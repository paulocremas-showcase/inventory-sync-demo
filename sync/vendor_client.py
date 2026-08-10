"""Client for pushing inventory updates to a vendor's API.

`MockVendorAPI` stands in for the real thing during the demo: it's just a
dict that records what was pushed, so tests can assert on exactly what went
out. `VendorAPIClient` is the real HTTP version, rate-limited via a
semaphore the same way the read-side clients in the sibling repos are.
"""
from __future__ import annotations

import asyncio

import httpx


class MockVendorAPI:
    """In-memory stand-in for a real vendor endpoint. Records every push so
    tests can assert on exactly what was sent, and how many calls it took."""

    def __init__(self):
        self.remote_state: dict[str, int] = {}
        self.call_count = 0

    async def push(self, sku: str, quantity: int) -> None:
        self.call_count += 1
        self.remote_state[sku] = quantity


class VendorAPIClient:
    """Real HTTP client. Requires a live vendor endpoint, not exercised by
    the demo path."""

    def __init__(self, base_url: str, max_concurrent: int = 5, timeout: float = 30):
        self.base_url = base_url
        self._client = httpx.AsyncClient(timeout=timeout)
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def push(self, sku: str, quantity: int) -> None:
        async with self._semaphore:
            resp = await self._client.put(f"{self.base_url}/inventory/{sku}", json={"quantity": quantity})
            resp.raise_for_status()

    async def aclose(self) -> None:
        await self._client.aclose()
