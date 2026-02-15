"""
Example 2: Consensus Vote

Two agents participate in a consensus round. One proposes, both vote,
and the proposal commits. Trace hooks capture the full audit trail.

Demonstrates: C_PROPOSE, C_VOTE, C_QUORUM, C_COMMIT, trace events.

Usage:
    python examples/consensus_vote.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vm import ScrawlVM, TraceSeverity
from src.synapse import Instruction
from src.opcodes import ConsensusOp, IdentityOp, ExecutionOp


def main():
    print("=== SCRAWL Consensus Vote ===\n")

    # Capture trace events for audit
    audit_log = []

    def audit_hook(event):
        severity = TraceSeverity(event.severity).name
        audit_log.append(f"  [{severity:8s}] {event.domain}.{event.event_type}: {event.message}")

    # Agent 0: Proposes and votes APPROVE
    vm = ScrawlVM()
    vm.agent_id = 0
    vm.add_trace_hook(audit_hook)

    program = [
        # Derive identity for this agent
        Instruction(IdentityOp.I_DERIVE, [0, 0xA0A0, 16]),

        # Propose: "adopt SCRAWL v1.1 as standard protocol"
        # Proposal ID=1, data from R0 (agent's identity fingerprint), agents=[0, 1]
        Instruction(IdentityOp.I_FINGERPRINT, [0, 0]),
        Instruction(ConsensusOp.C_PROPOSE, [1, 0, [0, 1]]),

        # Set quorum: 50% approval required
        Instruction(ConsensusOp.C_QUORUM, [1, 0.5]),

        # Agent 0 votes APPROVE (vote=0)
        Instruction(ConsensusOp.C_VOTE, [1, 0, 0]),

        # Simulate Agent 1 voting APPROVE
        Instruction(ConsensusOp.C_VOTE, [1, 0, 0]),

        # Commit — quorum met, proposal passes
        Instruction(ConsensusOp.C_COMMIT, [1, 1]),

        Instruction(ExecutionOp.X_HALT),
    ]

    # Switch agent_id mid-execution for the second vote
    vm.agent_id = 0
    result = vm.execute(program)

    print("Audit Trail:")
    for line in audit_log:
        print(line)

    commit_result = vm.registers.get_reg(1)
    print(f"\n  Proposal committed: {'YES' if commit_result == 1 else 'NO'}")
    print(f"  Instructions executed: {result.instructions_executed}")
    print(f"  Trace events: {len(result.trace_events)}")

    # Show what happens when a vote is REJECTED
    print("\n--- Rejection Scenario ---\n")
    audit_log.clear()
    vm2 = ScrawlVM()
    vm2.agent_id = 0
    vm2.add_trace_hook(audit_hook)

    rejection_program = [
        Instruction(ConsensusOp.C_PROPOSE, [2, 0, [0, 1, 2]]),
        Instruction(ConsensusOp.C_QUORUM, [2, 0.67]),
        Instruction(ConsensusOp.C_VOTE, [2, 0, 0]),   # Agent 0: APPROVE
        Instruction(ConsensusOp.C_VOTE, [2, 1, 0]),   # Agent 1: REJECT
        Instruction(ConsensusOp.C_COMMIT, [2, 3]),     # Quorum not met
        Instruction(ExecutionOp.X_HALT),
    ]

    vm2.execute(rejection_program)
    print("Audit Trail:")
    for line in audit_log:
        print(line)

    # Filter for warnings and errors
    warnings = vm2.get_trace_events(TraceSeverity.WARN)
    print(f"\n  Warnings/Errors: {len(warnings)}")
    for w in warnings:
        print(f"    {TraceSeverity(w.severity).name}: {w.message}")

    print("\n=== Consensus Demo Complete ===")


if __name__ == "__main__":
    main()
