# ADR 0009 — Persistent Trigger Causal Provenance

**Status:** Accepted for P0

## Decision

TRIGGER effects remain persistent direct support committed through `WorldPatch`.
They carry structured runtime provenance: trigger rule ID and the ordered IDs of
the snapshot supports that matched its premises. They are not DERIVE support.

When several matches produce one identical persistent output, P0 retains the
lexicographically smallest premise-ID path. This is deterministic but does not
preserve every duplicate trigger causal path.

## Consequence

Historical trigger provenance survives later retraction of its premises and a
world-aware why query can resolve the first revision that committed a support.
