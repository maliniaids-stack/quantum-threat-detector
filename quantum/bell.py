"""Stage 4 - Bell states with Qiskit, plus the fast correlation rule used for bulk channel tests."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from .paulis import EIGEN
from .measure import collapse, eve_intercept_resend, pauli_noise


def bell_circuit(kind: str = "phi+") -> QuantumCircuit:
    """Build one of the four Bell states on 2 qubits."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)                 # now |phi+> = (|00> + |11>)/sqrt2
    if kind in ("phi-", "psi-"):
        qc.z(0)
    if kind in ("psi+", "psi-"):
        qc.x(1)
    return qc


def bell_statevector(kind: str = "phi+") -> Statevector:
    return Statevector(bell_circuit(kind))


def bell_channel_test(n_pairs, rng, eve_fraction=0.0, channel_noise=0.0):
    """Simulate n Bell pairs (|phi+>). Alice and Bob measure in the same random basis (Z or X).
    Rule used (checked against Qiskit in tests): when Alice measures her half of |phi+> in basis P and
    gets outcome a, Bob's half collapses to the P-eigenstate with the same outcome a.
    Returns the quantum bit error rate (QBER) = fraction of pairs where outcomes disagree."""
    basis = rng.integers(0, 2, size=n_pairs)               # 0 = Z, 1 = X
    a, bob_state = collapse(EIGEN[basis, 0].copy(), basis, rng)   # Alice's outcome; Bob's collapsed half
    bob_state = EIGEN[basis, a].copy()
    bob_state = pauli_noise(bob_state, channel_noise, rng)
    if eve_fraction > 0:
        bob_state, _ = eve_intercept_resend(bob_state, eve_fraction, rng)
    b, _ = collapse(bob_state, basis, rng)
    errors = int((a != b).sum())
    return {"pairs": int(n_pairs), "errors": errors, "qber": errors / n_pairs}
