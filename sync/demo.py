"""Runs one sync cycle against the in-memory mock vendor and prints what
was actually pushed, so the idempotency and zero-out behavior are visible
without needing a real vendor account.
"""
from __future__ import annotations

import asyncio
import json

from .sync import run_sync
from .vendor_client import MockVendorAPI


async def main() -> None:
    last_synced_state = {"sku-1": 10, "sku-2": 5, "sku-3": 20}
    local_state = {
        "sku-1": 10,  # unchanged, should not be pushed
        "sku-2": 8,  # changed, should be pushed
        # sku-3 delisted, should be zeroed
        "sku-4": 3,  # new, should be pushed
    }

    vendor = MockVendorAPI()
    new_state = await run_sync(local_state, last_synced_state, vendor)

    print(f"vendor calls made: {vendor.call_count}")
    print(f"pushed: {json.dumps(vendor.remote_state, indent=2)}")
    print(f"new synced state: {json.dumps(new_state, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
