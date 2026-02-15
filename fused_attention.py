"""
Example 4: Fused Attention Macro

Demonstrates the ROSETTA macro layer: user-defined compound operations
that expand to native SCRAWL instructions. Shows the full pipeline:

    ROSETTA pseudocode → Compile → SYNAPSE binary → Execute on VM → Decompile

Also shows tensor in-place operations and attention routing.

Usage:
    python examples/fused_attention.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vm import ScrawlVM
from src.registers import Tensor
from src.synapse import Instruction, SynapseEncoder, SynapseDecoder
from src.rosetta import (
    decompile, compile_program, expand_macro_full, get_macros,
    register_macro, RosettaMacro
)
from src.opcodes import (
    TensorOp, AttentionOp, ExecutionOp, IdentityOp, ComposeMode
)


def main():
    print("=== SCRAWL Fused Attention Macro Demo ===\n")

    # ── 1. Show registered macros ──
    print("1. Registered Macros:")
    for name, macro in get_macros().items():
        print(f"   {name}({', '.join(macro.params)}) → {macro.description}")

    # ── 2. Expand a macro to see what it produces ──
    print("\n2. Macro Expansion:")
    instructions = expand_macro_full("fused_attention(TR0, TR1, TR2, TR3)")
    for i, inst in enumerate(instructions):
        print(f"   [{i}] {inst.mnemonic} {inst.operands}")
    print(f"   → {len(instructions)} native instructions")

    # ── 3. Register a custom macro ──
    print("\n3. Custom Macro: strided_compose")

    def _strided_compose(src1, src2, dst):
        """Compose two tensors with intermediate normalization."""
        return [
            Instruction(TensorOp.T_NORM, [src1, src1, 1]),      # L2 normalize src1
            Instruction(TensorOp.T_NORM, [src2, src2, 1]),      # L2 normalize src2
            Instruction(TensorOp.T_COMPOSE, [dst, src1, src2, ComposeMode.DOT]),  # dot product
        ]

    register_macro(RosettaMacro(
        "strided_compose", ["src1", "src2", "dst"],
        _strided_compose,
        "Normalized dot product: norm(a) · norm(b)"))

    expanded = expand_macro_full("strided_compose(TR0, TR1, TR2)")
    print(f"   Expanded to {len(expanded)} instructions:")
    for inst in expanded:
        print(f"     {inst.mnemonic}")

    # ── 4. Full ROSETTA roundtrip ──
    print("\n4. ROSETTA Compile → Execute → Decompile Roundtrip:")

    source = """
# Derive identity baseline
CR0 = identity.derive(seed=0xF00D, depth=8)
R1 = identity.verify(CR0, R0)

# Attention routing
TR3 = attention.self(TR0)

# Halt
halt
"""
    print("   Source (ROSETTA pseudocode):")
    for line in source.strip().split("\n"):
        if line.strip():
            print(f"     {line.strip()}")

    compiled = compile_program(source, strict=True)
    print(f"\n   Compiled: {len(compiled)} instructions")

    # Encode to SYNAPSE binary
    encoder = SynapseEncoder()
    frame = encoder.encode_frame(compiled)
    print(f"   SYNAPSE frame: {len(frame)} bytes")

    # Decode back
    decoder = SynapseDecoder()
    decoded, metadata = decoder.decode_frame(frame)
    print(f"   Decoded: {len(decoded)} instructions")

    # Decompile to readable form
    readable = decompile(decoded, include_hex=True)
    print(f"\n   Decompiled (with hex annotations):")
    for line in readable.split("\n"):
        if line.strip() and not line.startswith("# ROSETTA") and not line.startswith("# Instructions"):
            print(f"     {line}")

    # ── 5. Execute attention on actual tensors ──
    print("\n5. Attention Execution with SCRAWL Tensors:")

    # Create Q, K, V matrices (2x3 for simplicity)
    Q = Tensor([1.0, 0.0, 1.0,
                0.0, 1.0, 0.0], (2, 3))
    K = Tensor([1.0, 0.0, 1.0,
                0.0, 1.0, 0.0], (2, 3))
    V = Tensor([10.0, 20.0, 30.0,
                40.0, 50.0, 60.0], (2, 3))

    vm = ScrawlVM()
    vm.registers.set_treg(0, Q)
    vm.registers.set_treg(1, K)
    vm.registers.set_treg(2, V)

    attn_program = [
        Instruction(AttentionOp.A_ROUTE, [0, 1, 2, 3]),
        Instruction(ExecutionOp.X_HALT),
    ]

    result = vm.execute(attn_program)
    output = vm.registers.get_treg(3)
    print(f"   Q shape: {Q.shape}")
    print(f"   K shape: {K.shape}")
    print(f"   V shape: {V.shape}")
    print(f"   Output shape: {output.shape}")
    print(f"   Output values: [{', '.join(f'{v:.2f}' for v in output.data)}]")
    print(f"   Execution: {result.execution_time_ms:.3f}ms")

    # ── 6. Tensor in-place operations ──
    print("\n6. Tensor In-Place Operations (zero-allocation):")

    t = Tensor([1.0, 2.0, 3.0, 4.0], (4,))
    bias = Tensor([0.1, 0.2, 0.3, 0.4], (4,))

    obj_id = id(t)
    t.add_inplace(bias).scale_inplace(2.0)

    print(f"   Original tensor mutated in-place: {id(t) == obj_id}")
    print(f"   Result: [{', '.join(f'{v:.1f}' for v in t.data)}]")
    print(f"   (1+0.1)*2=2.2, (2+0.2)*2=4.4, (3+0.3)*2=6.6, (4+0.4)*2=8.8")

    print("\n=== Fused Attention Demo Complete ===")


if __name__ == "__main__":
    main()
