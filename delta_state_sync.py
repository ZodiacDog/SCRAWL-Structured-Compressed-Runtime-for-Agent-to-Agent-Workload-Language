"""
Example 3: Delta State Sync

Two agents establish a shared ML Identity baseline, then exchange
state updates as compressed deltas. Only the difference is transmitted.

Demonstrates: IdentityBaseline, DeltaCompressor, IdentityHandshake,
              integer chains, gnomon updates.

Usage:
    python examples/delta_state_sync.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.identity import (
    IdentityBaseline, IdentityHandshake, DeltaCompressor,
    ml_identity, ml_gnomon_update, ml_algebraic_verify
)


def main():
    print("=== SCRAWL Delta State Sync ===\n")

    # ── Step 1: Identity Handshake ──
    print("Step 1: Identity Handshake")
    seed, depth = 0xBEEF, 16

    # Agent A initiates
    baseline_a, fingerprint_a = IdentityHandshake.initiate(seed, depth)
    print(f"  Agent A: baseline derived (seed=0x{seed:04X}, depth={depth})")
    print(f"  Agent A: fingerprint = {fingerprint_a.hex()}")

    # Agent B responds — verifies fingerprint matches
    baseline_b, match = IdentityHandshake.respond(seed, depth, fingerprint_a)
    print(f"  Agent B: fingerprint match = {match}")
    print(f"  Chain values are integers: {all(isinstance(v, int) for v in baseline_a.chain)}")

    # ── Step 2: Derive shared key ──
    print("\nStep 2: Shared Key Derivation")
    shared_key = IdentityHandshake.derive_shared_key(baseline_a, agent_a_id=0, agent_b_id=1)
    print(f"  Shared key: {shared_key[:16].hex()}... ({len(shared_key)} bytes)")

    # ── Step 3: Delta compression ──
    print("\nStep 3: Delta State Sync")

    comp_a = DeltaCompressor(baseline_a)
    comp_b = DeltaCompressor(baseline_b)

    # Simulate 5 state updates
    states = [
        b"agent_state: position=(100, 200), health=95, ammo=30",
        b"agent_state: position=(102, 201), health=95, ammo=29",
        b"agent_state: position=(105, 203), health=90, ammo=27",
        b"agent_state: position=(105, 203), health=90, ammo=27",  # identical to previous
        b"agent_state: position=(110, 210), health=85, ammo=25",
    ]

    total_raw = 0
    total_compressed = 0

    for i, state in enumerate(states):
        # Agent A compresses
        compressed = comp_a.compress(state)
        total_raw += len(state)
        total_compressed += len(compressed)

        # Agent B decompresses
        recovered = comp_b.decompress(compressed)
        match = recovered == state

        ratio = (1.0 - len(compressed) / len(state)) * 100
        print(f"  Update {i+1}: {len(state)}B → {len(compressed)}B "
              f"({ratio:+.1f}%) {'✓' if match else '✗ CORRUPT'}")

    savings = (1.0 - total_compressed / total_raw) * 100
    print(f"\n  Total: {total_raw}B raw → {total_compressed}B compressed ({savings:.1f}% saved)")

    # ── Step 4: Gnomon verification ──
    print("\nStep 4: Gnomon Incremental Verification")
    a_sq = 0
    for a in range(10):
        a_sq = ml_gnomon_update(a_sq, a)
        b = a + 1
        b_sq = a_sq
        verified = ml_algebraic_verify(a, a * a, b, b_sq)
        if a < 5 or a == 9:
            print(f"  ({a}+1)² = {b_sq} via gnomon, algebraic check: {'✓' if verified else '✗'}")
        elif a == 5:
            print(f"  ...")

    print("\n=== Delta State Sync Complete ===")


if __name__ == "__main__":
    main()
