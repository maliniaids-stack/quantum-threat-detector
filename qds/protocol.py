"""Stages 6-7 - a simplified QDS: key generation, distribution, signing, verification.
Educational model inspired by Gottesman-Chuang QDS. NOT a production or physically secure implementation."""
import hashlib, uuid
import numpy as np
import config as C
from quantum.measure import prepare, measure, pauli_noise, eve_intercept_resend
from quantum.bell import bell_channel_test
from detection.thresholds import qber_threshold


def generate_key(signer_id, rng, k=C.DIGEST_BITS, L=C.BLOCK_SIZE):
    """Private key: for each digest position j and bit value v, L secret (basis, value) pairs."""
    bases = rng.integers(0, 3, size=(k, 2, L))
    values = rng.integers(0, 2, size=(k, 2, L))
    return {"signer_id": signer_id, "key_id": uuid.uuid4().hex[:12], "bases": bases, "values": values}


def public_states(key):
    """Quantum public key: one Pauli-eigenstate per private-key element. Shape (k, 2, L, 2)."""
    return prepare(key["bases"], key["values"])


def distribute(states, rng, channel_noise=C.CHANNEL_NOISE, eve_fraction=0.0):
    """Send the public-key states to a verifier.
    Teleportation of each state is modelled as ideal teleportation + Pauli noise from the imperfect Bell pair
    (Qiskit circuit in quantum/teleport.py proves the ideal case). Attacker Eve may intercept-resend.
    A separate batch of Bell pairs measures the channel health (QBER)."""
    flat = states.reshape(-1, 2)
    flat = pauli_noise(flat, channel_noise, rng)
    if eve_fraction > 0:
        flat, _ = eve_intercept_resend(flat, eve_fraction, rng)
    report = bell_channel_test(C.N_TEST_PAIRS, rng, eve_fraction=eve_fraction, channel_noise=channel_noise)
    thr = qber_threshold()
    report.update({"qber_threshold": thr, "healthy": report["qber"] <= thr})
    return flat.reshape(states.shape), report


def digest_bits(signer_id, key_id, message, nonce, timestamp, k=C.DIGEST_BITS):
    h = hashlib.sha256(f"{signer_id}|{key_id}|{nonce}|{timestamp}|{message}".encode()).digest()
    return [(h[0] >> (7 - i)) & 1 for i in range(k)]


def sign(key, message, nonce, timestamp):
    """Signature = classical description of the private-key blocks selected by the message digest."""
    d = digest_bits(key["signer_id"], key["key_id"], message, nonce, timestamp)
    revealed = [np.stack([key["bases"][j, d[j]], key["values"][j, d[j]]], axis=1).tolist() for j in range(len(d))]
    return {"signer_id": key["signer_id"], "key_id": key["key_id"], "message": message,
            "nonce": nonce, "timestamp": timestamp, "digest": d, "revealed": revealed}


def verify_quantum(stored_states, signature, rng, readout_error=C.READOUT_ERROR):
    """Measure the stored quantum states in the bases claimed by the signature; count mismatches per block."""
    # never trust the digest inside the signature: recompute it from the message the verifier actually received
    digest = digest_bits(signature["signer_id"], signature["key_id"], signature["message"],
                         signature["nonce"], signature["timestamp"])
    mism = []
    for j, bit in enumerate(digest):
        claim = np.array(signature["revealed"][j])            # (L, 2): basis, value
        st = stored_states[j, bit]                            # (L, 2)
        out = measure(st, claim[:, 0], rng, readout_error)
        mism.append(int((out != claim[:, 1]).sum()))
    return mism
