"""Stage 9 - statistical evidence (no ML): expected vs observed, p-values, posterior forgery probability."""
import numpy as np
from scipy.stats import binom
import config as C


def analyse(block_mismatches, L=C.BLOCK_SIZE, eps=C.EXPECTED_ERROR, q=C.FORGERY_MISMATCH):
    m = np.asarray(block_mismatches)
    worst = int(m.max())
    # p-value: chance an HONEST block would show at least this many mismatches
    p_honest = float(binom.sf(worst - 1, L, eps)) if worst > 0 else 1.0
    # posterior probability of 'forger' vs 'honest' on the worst block (equal priors, model assumptions!)
    ll_h = binom.logpmf(worst, L, eps)
    ll_f = binom.logpmf(worst, L, q)
    forgery_prob = float(1.0 / (1.0 + np.exp(np.clip(ll_h - ll_f, -50, 50))))
    return {
        "block_mismatches": [int(x) for x in m],
        "total_mismatches": int(m.sum()),
        "total_elements": int(len(m) * L),
        "observed_rate": float(m.sum() / (len(m) * L)),
        "expected_rate": eps,
        "expected_per_block": L * eps,
        "worst_block": worst,
        "p_value_honest": p_honest,
        "forgery_probability": forgery_prob,
    }
