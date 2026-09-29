"""Stage 5 - quantum teleportation with Pauli corrections (Qiskit).
Two versions: (A) deferred/statevector for proving fidelity ≈ 1.0,
(B) real mid-circuit measurements + classical feed-forward runnable on Aer."""
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity
from qiskit_aer import AerSimulator


def teleport_deferred(prep_gates):
    """3 qubits: q0 = state to send, q1 (Alice) & q2 (Bob) share a Bell pair.
    Corrections are written as controlled gates (equivalent to 'measure, send 2 bits, correct')."""
    qc = QuantumCircuit(3)
    prep_gates(qc)
    qc.h(1); qc.cx(1, 2)            # Bell pair
    qc.cx(0, 1); qc.h(0)            # Alice's Bell-basis measurement (basis change)
    qc.cx(1, 2)                     # Pauli-X correction if Alice's q1 = 1
    qc.cz(0, 2)                     # Pauli-Z correction if Alice's q0 = 1
    return qc


def teleport_fidelity(prep_gates) -> float:
    """Fidelity between the input state and what Bob holds after teleportation (ideal = 1.0)."""
    ref = QuantumCircuit(1); prep_gates(ref)
    target = Statevector(ref)
    bob = partial_trace(Statevector(teleport_deferred(prep_gates)), [0, 1])
    return float(state_fidelity(bob, target))


def teleport_with_measurements(prep_gates):
    """Textbook version with real mid-circuit measurements + classical feed-forward (runs on Aer)."""
    q = QuantumRegister(3, "q")
    c0, c1, out = ClassicalRegister(1, "c0"), ClassicalRegister(1, "c1"), ClassicalRegister(1, "out")
    qc = QuantumCircuit(q, c0, c1, out)
    prep_gates(qc)
    qc.h(1); qc.cx(1, 2)
    qc.cx(0, 1); qc.h(0)
    qc.measure(0, c0); qc.measure(1, c1)
    with qc.if_test((c1, 1)):
        qc.x(2)
    with qc.if_test((c0, 1)):
        qc.z(2)
    # undo the preparation on Bob's qubit so a perfect teleport always reads 0
    inv = QuantumCircuit(1); prep_gates(inv)
    qc.compose(inv.inverse(), qubits=[2], inplace=True)
    qc.measure(2, out)
    return qc


def run_teleport_on_aer(prep_gates, shots=4096):
    """Run the mid-circuit-measurement teleportation on AerSimulator.
    Returns the fraction of shots where the teleported qubit matches the original
    (i.e., Bob's qubit, after inverse-prep, reads 0).
    Perfect teleportation gives success_rate = 1.0."""
    qc = teleport_with_measurements(prep_gates)
    sim = AerSimulator()
    result = sim.run(transpile(qc, sim), shots=shots).result()
    counts = result.get_counts()
    # Registers are space-separated in MSB-first order: 'out c1 c0'
    # The 'out' register is the leftmost element
    success = sum(v for k, v in counts.items() if k.split()[0] == '0')
    return success / shots

