"""Stage 8 - attack simulators. Each returns a forged/attacker-made signature (or a modified channel setting)."""
import numpy as np
import config as C
from qds import protocol as P
from quantum.measure import measure


def blind_forgery(signer_id, key_id, message, nonce, timestamp, rng):
    """Attacker knows nothing: guesses a random (basis, value) for every element."""
    d = P.digest_bits(signer_id, key_id, message, nonce, timestamp)
    revealed = [np.stack([rng.integers(0, 3, C.BLOCK_SIZE), rng.integers(0, 2, C.BLOCK_SIZE)], axis=1).tolist() for _ in d]
    return {"signer_id": signer_id, "key_id": key_id, "message": message, "nonce": nonce,
            "timestamp": timestamp, "digest": d, "revealed": revealed}


def informed_forgery(attacker_copy, signer_id, key_id, message, nonce, timestamp, rng):
    """Attacker legitimately holds ONE copy of the public quantum key. He measures each state in a random
    basis and claims the result (best simple strategy; expected mismatch about 1/3)."""
    d = P.digest_bits(signer_id, key_id, message, nonce, timestamp)
    revealed = []
    for j, bit in enumerate(d):
        st = attacker_copy[j, bit]
        b = rng.integers(0, 3, size=len(st))
        v = measure(st, b, rng)
        revealed.append(np.stack([b, v], axis=1).tolist())
    return {"signer_id": signer_id, "key_id": key_id, "message": message, "nonce": nonce,
            "timestamp": timestamp, "digest": d, "revealed": revealed}


def impersonation(claimed_signer, victim_key_id, message, nonce, timestamp, rng):
    """Mallory signs with HER OWN key but claims to be the victim."""
    mallory_key = P.generate_key(claimed_signer, rng)   # her own random key, but she labels it with the victim's name
    mallory_key["key_id"] = victim_key_id
    return P.sign(mallory_key, message, nonce, timestamp)
