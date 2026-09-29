"""Central settings — change here, everything else follows.

THRESHOLD DERIVATION (binomial model)
─────────────────────────────────────
Each digest block contains L = BLOCK_SIZE qubits.

Honest verifier sees mismatches ~ Binomial(L, ε) where ε = EXPECTED_ERROR.
  → Accept threshold s_a = ISF(α, L, ε): P(honest block > s_a) ≤ α.
  → With L=128, ε=0.02, α=1e-6: s_a ≈ 8.

Measure-and-guess forger sees mismatches ~ Binomial(L, q) where q = 1/3.
  → Reject threshold s_v = PPF(α, L, q) - 1: P(forger block ≤ s_v) < α.
  → With L=128, q=1/3, α=1e-6: s_v ≈ 26.

Since s_a (≈8) < s_v (≈26), the INCONCLUSIVE zone [s_a+1, s_v] separates them.
False-alarm probability per block ≈ α = 1e-6.
For k=8 blocks, system false-alarm rate ≈ 1 - (1 - α)^k ≈ 8 × 1e-6 ≈ 8e-6.
"""
DIGEST_BITS = 8          # k: we sign an 8-bit demo digest (real systems need far more; see limitations)
BLOCK_SIZE = 128         # L: quantum states per (bit position, bit value) block
READOUT_ERROR = 0.01     # detector error probability
CHANNEL_NOISE = 0.015    # probability a random Pauli hits a qubit in transit
EXPECTED_ERROR = 0.02    # honest mismatch rate we design thresholds around (about readout + 2/3*channel)
FORGERY_MISMATCH = 1 / 3 # theoretical mismatch rate of the 'measure-and-guess' forger
ALPHA = 1e-6             # target false-alarm / miss probability used to derive thresholds
N_TEST_PAIRS = 400       # Bell pairs sacrificed to test the quantum channel
FRESHNESS_SECONDS = 300  # signatures older than this are rejected as stale
MAX_COPIES = 3           # how many verifier copies of one public key may exist
DB_PATH = "data/events.db"
