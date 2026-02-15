# SCRAWL v1.1

**Structured Compressed Runtime for Agent-to-Agent Workload Language**

```
552 tests | 100% pass rate | zero external dependencies | Python 3.10+
```

SCRAWL is a binary instruction set and runtime for AI agent communication. Where existing protocols treat agent messages as text to be parsed, SCRAWL treats them as programs to be executed — 84 opcodes across six domains (tensor operations, attention routing, execution control, state management, consensus, and identity), transmitted in a compact binary wire format, with built-in delta compression derived from the ML Identity equation. One agent compiles intent into SCRAWL instructions; the receiving agent executes them directly on a register-based VM. No JSON parsing, no schema negotiation, no prompt engineering between agents.

## Why SCRAWL?

**The problem:** AI agents talking to each other waste most of their bandwidth on syntax. JSON-RPC messages, protocol negotiation, schema validation, text serialization — all overhead that exists because we're forcing agents to communicate the way humans read. Agents don't need readable wire formats. They need fast, compact, verifiable instruction streams.

**What SCRAWL does differently:**

- **Binary ISA, not text protocol.** 84 instructions encode in 4–12 bytes each. A complete attention-routing operation that would be 200+ bytes in JSON is 8 bytes in SCRAWL.
- **Execute, don't parse.** The receiving agent runs instructions directly on a register-based VM — no deserialization step, no schema validation, no type coercion.
- **Delta compression from first principles.** Agents establish a shared mathematical baseline (derived from the ML Identity: `a + a² + b = b²` where `b = a + 1`). Subsequent messages transmit only the XOR delta against that baseline. Identical messages compress to 3 bytes.
- **Consensus built into the ISA.** `C_PROPOSE`, `C_VOTE`, `C_COMMIT` are native opcodes, not application-layer constructs. Multi-agent agreement is a VM operation, not a protocol.
- **Zero external dependencies.** Pure Python. No numpy, no protobuf, no gRPC. The entire stack — tensor math, binary encoding, VM execution, bidirectional transpilation — runs on a bare Python install.
- **Auditable by design.** ROSETTA transpiles any SCRAWL binary to human-readable pseudocode and back. Every instruction is inspectable. Every roundtrip is deterministic.

**Compared to alternatives:**

| | SCRAWL | MCP/A2A | Protobuf | FIPA-ACL | WASM |
|---|--------|---------|----------|----------|------|
| AI-native opcodes | ✓ 84 ops | ✗ | ✗ | ✗ | ✗ |
| Built-in consensus | ✓ | ✗ | ✗ | Partial | ✗ |
| Delta compression | ✓ 70–94% | ✗ | ✗ | ✗ | ✗ |
| Zero dependencies | ✓ | ✗ | ✗ | ✗ | ✗ |
| Bidirectional transpiler | ✓ | ✗ | ✗ | ✗ | ✗ |
| Identity verification | ✓ | ✗ | ✗ | ✗ | ✗ |

## Quick Start

```bash
git clone https://github.com/mlinnovations/scrawl.git
cd scrawl
python examples/heartbeat.py
```

**5-line agent ping-pong:**

```python
from src.vm import ScrawlVM
from src.synapse import Instruction
from src.opcodes import IdentityOp, ExecutionOp

vm = ScrawlVM()
vm.execute([
    Instruction(IdentityOp.I_DERIVE, [0, 0xCAFE, 16]),  # derive identity
    Instruction(IdentityOp.I_VERIFY, [0, 0, 1]),          # verify it holds
    Instruction(ExecutionOp.X_YIELD, [1]),                 # emit result
    Instruction(ExecutionOp.X_HALT),                       # done
])
print(f"Identity verified: {vm.registers.get_reg(1) == 1}")  # True
```

**Delta-compressed state sync between two agents:**

```python
from src.identity import IdentityBaseline, DeltaCompressor

baseline = IdentityBaseline(seed=0xBEEF, depth=16)
sender = DeltaCompressor(baseline)
receiver = DeltaCompressor(baseline)

state = b"agent_position: x=100, y=200, health=95"
compressed = sender.compress(state)        # 53 bytes → ~17 bytes
recovered = receiver.decompress(compressed) # lossless roundtrip
assert recovered == state
```

## Examples

| Example | What it shows | Run it |
|---------|--------------|--------|
| [heartbeat.py](examples/heartbeat.py) | Identity derivation, VM execution, integer chains | `python examples/heartbeat.py` |
| [consensus_vote.py](examples/consensus_vote.py) | Multi-agent voting, trace hooks, quorum checks | `python examples/consensus_vote.py` |
| [delta_state_sync.py](examples/delta_state_sync.py) | Shared baselines, delta compression, handshake | `python examples/delta_state_sync.py` |
| [fused_attention.py](examples/fused_attention.py) | ROSETTA macros, tensor ops, compile→execute→decompile | `python examples/fused_attention.py` |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    ROSETTA v1.1                      │
│         Human-readable ↔ Binary transpiler           │
│         84 opcodes + macro layer                     │
├─────────────────────────────────────────────────────┤
│                   SYNAPSE v1.0                       │
│          Binary wire format + CRC-32C                │
│     Magic | Version | Flags | SeqID | Payload | CRC  │
├─────────────────────────────────────────────────────┤
│                  SCRAWL VM v1.1                      │
│     Register-based execution engine                  │
│     256 GP + 64 tensor + 16 context registers        │
│     Per-instruction timeout + trace hooks            │
├──────────┬──────────┬──────────┬────────────────────┤
│ Tensor   │ Attention│ Execution│ State | Consensus  │
│ 15 ops   │ 14 ops   │ 16 ops   │ 15+12 ops         │
├──────────┴──────────┴──────────┴────────────────────┤
│              ML Identity Foundation                  │
│    a + a² + b = b² (integer-only, cross-platform)    │
│    Baselines | Chains | Delta | Gnomon | Algebraic   │
└─────────────────────────────────────────────────────┘
```

**Six operational domains — 84 total opcodes:**

- **Tensor** (15): compose, decompose, transform, reshape, slice, reduce, quantize, broadcast, fill, copy, compare, convert, normalize, random, einsum
- **Attention** (14): route, mask, focus, scatter, gather, cross, self, multi-head, sparse, linear, flash, window, pool, topk
- **Execution** (16): nop, halt, yield, abort, branch, loop, call, return, fork, join, trap, resume, spawn, kill, sleep, wake
- **State** (15): sync, lock, unlock, delta, apply, snapshot, restore, publish, subscribe, watch, cas, load, store, evict, prefetch
- **Consensus** (12): propose, vote, commit, reject, quorum, escalate, timeout, revoke, delegate, audit, veto, ratify
- **Identity** (12): derive, verify, baseline, reconstruct, rotate, challenge, respond, bind, unbind, fingerprint, chain, split

## v1.1 Changes

All improvements are tested (76 dedicated tests) and documented:

| Change | Source | Impact |
|--------|--------|--------|
| Integer-only identity chains | ML Identity Theorem 1 + §2.3 | Cross-platform determinism guaranteed |
| Gnomon incremental squares | Theorem 4 + 5 | Multiplication → addition in chain derivation |
| Generalized ML Identity | Theorem 2 | Arbitrary-gap verification for stride operations |
| Zero-cost algebraic verification | §7.2 + 7.5 | Free corruption detection in consensus |
| Triangular-square duality | Theorem 6 | Memory allocation optimization |
| Consensus trace hooks | Peer review (Grok) | 9 event types, severity filtering, external callbacks |
| ROSETTA macro layer | Peer review (Grok) | User-defined compound operations, 3 built-ins |
| Per-instruction VM timeout | Internal analysis | Configurable wall-clock limit per instruction |
| Tensor in-place operations | Internal analysis | Zero-allocation hot path for add/sub/scale/hadamard |
| ROSETTA full compiler | Internal analysis | All 84 opcodes compile; strict mode with CompileError |
| RLE decode hardening | Internal analysis | Stream corruption detection in delta decompression |

## Tests

```
=== SCRAWL Core ===     360/360  (100%)
=== FLUX/SCRAWL ===     116/116  (100%)
=== SCRAWL v1.1 ===      76/76   (100%)
─────────────────────────────────────────
TOTAL                   552/552  (100%)
```

Run all tests:

```bash
python tests/test_scrawl.py       # Core: 360 tests
python flux_scrawl_tests.py       # FLUX 2.0: 116 tests
python tests/test_v11.py          # v1.1 features: 76 tests
```

## The ML Identity

SCRAWL's mathematical foundation is the ML Identity, discovered by M. L. McKnight in 1999 at Raymond High School, Mississippi:

```
a + a² + b = b²    where b = a + 1
```

This identity holds in any commutative ring (integers, rationals, complex numbers, finite fields). SCRAWL uses it for:

- **Shared baselines:** Two agents derive identical baselines from the same seed using integer-only chain derivation
- **Delta compression:** Messages are XOR'd against the baseline expectation; structured data compresses 70–94%
- **Algebraic verification:** `a + a² + b == b²` is a zero-cost integrity check — one addition, one comparison
- **Gnomon updates:** `(a+1)² = a² + a + (a+1)` replaces multiplication with addition in chain generation

The complete mathematical treatment is in *The ML Identity Theorem Family* paper (17 theorems, 6 engineering applications).

## Project Structure

```
scrawl/
├── src/
│   ├── opcodes.py      # 84 instructions, 6 domains (444 lines)
│   ├── registers.py    # Tensors, register file (485 lines)
│   ├── synapse.py      # Binary wire format (474 lines)
│   ├── rosetta.py      # Bidirectional transpiler + macros (942 lines)
│   ├── identity.py     # ML Identity foundation (377 lines)
│   └── vm.py           # Execution engine + trace hooks (664 lines)
├── tests/
│   ├── test_scrawl.py  # Core test suite (360 tests)
│   └── test_v11.py     # v1.1 feature tests (76 tests)
├── examples/
│   ├── heartbeat.py
│   ├── consensus_vote.py
│   ├── delta_state_sync.py
│   └── fused_attention.py
├── flux_scrawl.py      # FLUX 2.0 compression (754 lines)
├── flux_scrawl_tests.py # FLUX tests (116 tests)
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## License

Apache License 2.0 — use it, modify it, ship it. See [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues welcome. PRs for new macros and opcodes especially.

---

**ML Innovations LLC** · M. L. McKnight · Pheba, Mississippi · 2026

*Built on the ML Identity — discovered 1999, Raymond High School, Mississippi*
