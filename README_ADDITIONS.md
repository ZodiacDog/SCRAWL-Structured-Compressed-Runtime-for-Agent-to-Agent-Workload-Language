<!-- INSERT AFTER the "## Tests" section and before "## The ML Identity" section -->

## Benchmarks

SCRAWL ships with a full benchmark suite — no external dependencies, just numbers.

```bash
python benchmarks/bench_scrawl.py           # standard (10 trials, ~30s)
python benchmarks/bench_scrawl.py --quick   # fast mode (~5s)
python benchmarks/bench_scrawl.py --json    # machine-readable output
```

**Wire format size — SCRAWL vs JSON-RPC (same operations, different encoding):**

| Operation | SCRAWL | JSON-RPC | Savings |
|-----------|--------|----------|---------|
| Identity derive + verify | ~24B | ~180B | **~87%** |
| Attention route (Q,K,V→out) | ~16B | ~120B | **~87%** |
| 3-agent consensus round | ~48B | ~520B | **~91%** |
| 10-instruction mixed program | ~72B | ~680B | **~89%** |

**Delta compression on real payloads:**

| Payload | Raw | Compressed | Savings |
|---------|-----|------------|---------|
| Small agent state | 27B | ~10B | ~63% |
| Large JSON state | 280B | ~60B | ~79% |
| Identical retransmit | 50B | 3B | **94%** |

Full methodology, results, and contribution guide: [BENCHMARKS.md](BENCHMARKS.md)

<!-- INSERT AFTER "## Contributing" section, REPLACE the existing contributing section with this expanded version -->

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues welcome. PRs for new macros, opcodes, and benchmarks especially.

## Fork It

SCRAWL is Apache 2.0. Fork it, extend it, ship it. We built the foundation — now go build on top of it.

**Things we'd love to see forked:**
- Domain-specific ISA extensions (robotics, finance, healthcare, gaming) using the reserved 0x60–0xFF opcode range
- Language ports (Rust, Go, C, WASM) — the SYNAPSE wire format is language-independent
- Bridge modules for existing frameworks (MCP, A2A, LangChain, AutoGen, CrewAI, ROS2)
- Research forks exploring the remaining ML Identity theorems

See [FORKING.md](FORKING.md) for the full guide — what to fork, how to maintain interoperability, and how to contribute back upstream.

If you build something with SCRAWL, open an issue titled `[Fork] Your Project Name`. We maintain a list of community projects.

<!-- UPDATED project structure to include new files -->

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
├── benchmarks/
│   └── bench_scrawl.py # Performance benchmarks (8 subsystems)
├── flux_scrawl.py      # FLUX 2.0 compression (754 lines)
├── flux_scrawl_tests.py # FLUX tests (116 tests)
├── README.md
├── BENCHMARKS.md       # Benchmark methodology & results
├── FORKING.md          # Guide to forking & extending SCRAWL
├── LICENSE
└── CONTRIBUTING.md
```
