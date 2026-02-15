"""
Example 1: Agent Heartbeat

The simplest SCRAWL program — an agent derives its identity baseline,
verifies the ML Identity holds, and emits a heartbeat signal.

This is the "Hello World" of SCRAWL: if this runs, your stack works.

Usage:
    python examples/heartbeat.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vm import ScrawlVM
from src.synapse import Instruction
from src.opcodes import IdentityOp, ExecutionOp
from src.identity import ml_identity, ml_identity_verify


def main():
    print("=== SCRAWL Agent Heartbeat ===\n")

    # 1. Verify the ML Identity holds (pure math — no VM needed)
    for a in [1, 5, 10, 42, 1000]:
        b, lhs = ml_identity(a)
        assert lhs == b * b, f"Identity broken at a={a}"
        print(f"  ML Identity: {a} + {a*a} + {b} = {b*b}  ✓")

    # 2. Build a SCRAWL program: derive baseline, verify, fingerprint, halt
    program = [
        Instruction(IdentityOp.I_DERIVE, [0, 0xCAFE, 16]),   # CR0 = baseline from seed 0xCAFE
        Instruction(IdentityOp.I_VERIFY, [0, 0, 1]),          # R1 = verify(CR0)
        Instruction(IdentityOp.I_FINGERPRINT, [2, 0]),         # R2 = fingerprint(CR0)
        Instruction(ExecutionOp.X_YIELD, [1]),                 # yield R1 (verification result)
        Instruction(ExecutionOp.X_HALT),                       # done
    ]

    # 3. Execute on the SCRAWL VM
    vm = ScrawlVM()
    result = vm.execute(program)

    print(f"\n  VM executed {result.instructions_executed} instructions in {result.execution_time_ms:.3f}ms")
    print(f"  Identity verified: {'YES' if vm.registers.get_reg(1) == 1 else 'NO'}")
    print(f"  Fingerprint: 0x{vm.registers.get_reg(2):016X}")
    print(f"  Yielded: {result.yielded_values}")

    # 4. Show the baseline
    baseline = vm.baselines[0]
    print(f"\n  Baseline: seed=0x{baseline.seed:04X}, depth={baseline.depth}")
    print(f"  Chain (first 5): {baseline.chain[:5]}")
    print(f"  All chain values are integers: {all(isinstance(v, int) for v in baseline.chain)}")

    print("\n=== Heartbeat OK ===")


if __name__ == "__main__":
    main()
