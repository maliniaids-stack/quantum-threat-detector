"""Stage 10 - two-threshold engine. Thresholds come from the binomial distribution, not guesses."""
from dataclasses import dataclass, asdict
from scipy.stats import binom
import config as C


@dataclass
class Thresholds:
    block_size: int
    accept_max: int      # s_a : mismatches <= s_a in every block  -> ACCEPT
    reject_min: int      # s_v : mismatches  > s_v in any block    -> REJECT
    alpha: float
    expected_error: float
    forgery_rate: float

    def as_dict(self):
        return asdict(self)


def compute_thresholds(L=C.BLOCK_SIZE, eps=C.EXPECTED_ERROR, q=C.FORGERY_MISMATCH, alpha=C.ALPHA) -> Thresholds:
    s_a = int(binom.isf(alpha, L, eps))            # P(honest block > s_a) <= alpha
    s_v = int(binom.ppf(alpha, L, q)) - 1          # P(forger block <= s_v) < alpha
    if s_a >= s_v:
        raise ValueError("Block too small: honest and forger distributions overlap. Increase BLOCK_SIZE.")
    return Thresholds(L, s_a, s_v, alpha, eps, q)


def decide(block_mismatches, th: Thresholds) -> str:
    worst = max(block_mismatches)
    if worst > th.reject_min:
        return "REJECT"
    if worst <= th.accept_max:
        return "ACCEPT"
    return "INCONCLUSIVE"


def qber_threshold(n_pairs=C.N_TEST_PAIRS, expected_qber=C.EXPECTED_ERROR, alpha=C.ALPHA) -> float:
    """Channel is flagged when the Bell-pair error rate exceeds this value."""
    return float(binom.isf(alpha, n_pairs, expected_qber)) / n_pairs
