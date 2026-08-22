# 1. Delisted SKUs sync as an explicit zero, not a deletion

Date: 2026-08-22

## Status

Accepted

## Context

`compute_delta` diffs local inventory state against what was last pushed to
the vendor, and pushes only what changed. A SKU can disappear from local
state entirely, for example a product gets discontinued and stops being
tracked. The simplest implementation would be to just stop mentioning that
SKU in the push: no local record, no delta entry, nothing sent.

That's wrong. If the vendor's last known quantity for that SKU was
non-zero, silently not mentioning it again leaves that last known quantity
live and sellable on the vendor's side indefinitely, even though the
product no longer exists locally at all.

## Decision

A SKU present in `last_synced_state` but missing from `local_state`
produces an explicit delta entry of `0`, not an omission. Dropping a SKU
locally has to actively zero it out on the vendor side, not just stop
mentioning it.

## Consequences

- `compute_delta`'s output size is not simply "what changed" in the
  colloquial sense; a delisted SKU counts as a change even though its
  local value didn't move, it vanished.
- Every push cycle needs both `local_state` and `last_synced_state` to
  detect a disappearance; a diff that only looks at `local_state` cannot
  produce this behavior by construction.
- The Rules section of this repo's README encodes the same constraint as a
  standing rule: "A SKU missing from local state must produce an explicit
  zero, never a silent no-op," so a future change to `compute_delta` fails
  its test rather than reintroducing the original bug quietly.
