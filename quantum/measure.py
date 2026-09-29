"""Stage 2/3 - state preparation, projective measurement, noise (vectorised)."""
import numpy as np
from .paulis import EIGEN, PAULI_STACK


def prepare(bases, values):
    """Return an (N,2) array of Pauli-eigenstates."""
    return EIGEN[np.asarray(bases), np.asarray(values)].copy()


def measure(states, bases, rng, readout_error=0.0):
    """Projective measurement of each state in its own Pauli basis.
    Returns array of 0/1 outcomes (0 <-> eigenvalue +1)."""
    e_plus = EIGEN[np.asarray(bases), 0]
    p0 = np.abs(np.einsum("ni,ni->n", e_plus.conj(), states)) ** 2   # Born rule
    outcome = (rng.random(len(states)) > p0).astype(int)
    if readout_error > 0:
        outcome ^= (rng.random(len(states)) < readout_error).astype(int)
    return outcome


def collapse(states, bases, rng):
    """Measure, then return the post-measurement states (the state 'remembers' the outcome)."""
    out = measure(states, bases, rng)
    return out, EIGEN[np.asarray(bases), out].copy()


def pauli_noise(states, p, rng):
    """Depolarising-style channel: with probability p apply a random X, Y or Z."""
    states = states.copy()
    hit = rng.random(len(states)) < p
    n = int(hit.sum())
    if n:
        which = rng.integers(0, 3, size=n)
        states[hit] = np.einsum("nij,nj->ni", PAULI_STACK[which], states[hit])
    return states


def eve_intercept_resend(states, fraction, rng):
    """Attacker measures a fraction of qubits in a random Pauli basis and resends the result."""
    states = states.copy()
    hit = rng.random(len(states)) < fraction
    n = int(hit.sum())
    if n:
        guess_basis = rng.integers(0, 3, size=n)
        _, new = collapse(states[hit], guess_basis, rng)
        states[hit] = new
    return states, hit
