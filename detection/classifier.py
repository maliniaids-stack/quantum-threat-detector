"""Rule-based threat classifier (deliberately NOT machine learning). Every rule is explainable."""

BLIND_RATE_CUTOFF = 0.42   # between 1/3 (measure-and-guess) and 1/2 (pure guessing)


def classify(ctx: dict):
    """ctx keys: unauthorized, replay, impersonation, channel_flag, verdict, observed_rate.
    Returns (attack_type, reason)."""
    if ctx.get("unauthorized"):
        return "UNAUTHORIZED_VERIFICATION", "verifier is not registered / copy budget exceeded"
    if ctx.get("replay"):
        return "REPLAY_ATTACK", ctx.get("replay_reason", "replayed signature")
    verdict = ctx["verdict"]
    if verdict == "ACCEPT":
        return "NONE", "signature consistent with honest noise"
    if ctx.get("impersonation"):
        return "IMPERSONATION", "submitter identity differs from claimed signer and quantum check failed"
    if ctx.get("channel_flag"):
        return "CHANNEL_MANIPULATION", "Bell-pair test flagged this key's channel and verification failed"
    if verdict == "INCONCLUSIVE":
        return "SUSPICIOUS", "mismatches between the accept and reject thresholds (weak tampering or excess noise)"
    if ctx["observed_rate"] >= BLIND_RATE_CUTOFF:
        return "FORGERY_BLIND", "mismatch rate near 1/2: signature looks like random guessing"
    return "FORGERY_INFORMED", "mismatch rate near 1/3: signature looks like measure-and-guess forgery"
