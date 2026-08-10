"""Smoke tests, not a full suite. Run directly: python tests/test_sync.py"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sync.sync import compute_delta, run_sync
from sync.vendor_client import MockVendorAPI


def test_unchanged_items_are_not_pushed():
    local = {"sku-1": 10, "sku-2": 5}
    last_synced = {"sku-1": 10, "sku-2": 5}
    assert compute_delta(local, last_synced) == {}


def test_changed_and_new_items_are_pushed():
    local = {"sku-1": 12, "sku-2": 5, "sku-3": 7}
    last_synced = {"sku-1": 10, "sku-2": 5}
    delta = compute_delta(local, last_synced)
    assert delta == {"sku-1": 12, "sku-3": 7}


def test_delisted_items_are_zeroed_not_dropped():
    local = {"sku-1": 10}
    last_synced = {"sku-1": 10, "sku-2": 5}
    delta = compute_delta(local, last_synced)
    assert delta == {"sku-2": 0}


def test_run_sync_only_calls_vendor_for_the_delta():
    local = {"sku-1": 10, "sku-2": 5, "sku-3": 7}
    last_synced = {"sku-1": 10, "sku-2": 5}
    vendor = MockVendorAPI()

    new_state = asyncio.run(run_sync(local, last_synced, vendor))

    assert vendor.call_count == 1  # only sku-3 is new, sku-1/sku-2 are unchanged
    assert vendor.remote_state == {"sku-3": 7}
    assert new_state == {"sku-1": 10, "sku-2": 5, "sku-3": 7}


if __name__ == "__main__":
    test_unchanged_items_are_not_pushed()
    test_changed_and_new_items_are_pushed()
    test_delisted_items_are_zeroed_not_dropped()
    test_run_sync_only_calls_vendor_for_the_delta()
    print("all tests passed")
