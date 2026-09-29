"""Optional showcase: a TOY Shor's algorithm that factors N = 15 with a = 7 (period r = 4).
It demonstrates WHY RSA is at risk. It only works for a tiny number and is not an attack on real RSA."""
from math import gcd
from fractions import Fraction
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate
from qiskit_aer import AerSimulator
from qiskit import transpile

N, A = 15, 7


def _mod15_power(a, power):
    u = QuantumCircuit(4)
    for _ in range(power):
        if a in (7, 8):
            u.swap(1, 2); u.swap(2, 3); u.swap(0, 3)
        if a in (7, 11, 13):
            for q in range(4):
                u.x(q)
    g = u.to_gate(label=f"{a}^{power} mod 15")
    return g.control(1)


def build_circuit(n_count=4):
    qc = QuantumCircuit(n_count + 4, n_count)
    qc.x(n_count)                                   # work register starts at |1>
    for q in range(n_count):
        qc.h(q)
    for q in range(n_count):
        qc.append(_mod15_power(A, 2 ** q), [q] + [n_count + i for i in range(4)])
    qc.append(QFTGate(n_count).inverse(), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc


def run(shots=1024, n_count=4):
    sim = AerSimulator()
    counts = sim.run(transpile(build_circuit(n_count), sim), shots=shots).result().get_counts()
    factors = set()
    for bits, _ in counts.items():
        phase = int(bits, 2) / 2 ** n_count
        r = Fraction(phase).limit_denominator(N).denominator
        if r % 2 == 0 and pow(A, r // 2, N) != N - 1:
            for f in (gcd(pow(A, r // 2) - 1, N), gcd(pow(A, r // 2) + 1, N)):
                if f not in (1, N):
                    factors.add(f)
    return counts, sorted(factors)
