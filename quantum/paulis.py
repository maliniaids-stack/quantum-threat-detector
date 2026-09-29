"""Stage 3 - Pauli operators and their eigenstates (NumPy only, fast)."""
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

BASIS_NAMES = ["Z", "X", "Y"]          # basis index 0, 1, 2
PAULI_MATRICES = {"Z": Z, "X": X, "Y": Y}
PAULI_STACK = np.stack([X, Y, Z])      # used for random Pauli noise

_s = 1 / np.sqrt(2)
# EIGEN[basis_index, value] -> state vector.  value 0 = eigenvalue +1, value 1 = eigenvalue -1
EIGEN = np.array([
    [[1, 0], [0, 1]],                    # Z: |0>, |1>
    [[_s, _s], [_s, -_s]],               # X: |+>, |->
    [[_s, 1j * _s], [_s, -1j * _s]],     # Y: |+i>, |-i>
], dtype=complex)


def check_eigenstates() -> bool:
    """Sanity check: P|e> = (+1 or -1)|e> for all six states."""
    for b, name in enumerate(BASIS_NAMES):
        for v in (0, 1):
            e = EIGEN[b, v]
            if not np.allclose(PAULI_MATRICES[name] @ e, (1 - 2 * v) * e):
                return False
    return True
