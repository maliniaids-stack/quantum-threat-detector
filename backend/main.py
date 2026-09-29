"""Stage 11 — FastAPI backend. Run:  uvicorn backend.main:app --reload"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from qds.service import QDSSystem, ATTACKS
from detection import audit
from detection.thresholds import compute_thresholds, qber_threshold
from quantum.shor_toy import run as shor_run
import config as C

app = FastAPI(
    title="Quantum-Inspired QDS Threat Detection (academic prototype)",
    description="SIH 26141 — quantum-SIMULATED, statistics-only (no AI/ML) detection framework",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
system = QDSSystem()


@app.get("/health")
def health():
    return {"status": "ok", "project": "SIH 26141 — QDS Threat Detection (academic prototype)"}


@app.get("/attacks")
def attacks():
    return ATTACKS


@app.post("/simulate/{attack}")
def simulate(attack: str, strength: float = 0.5):
    if attack not in ATTACKS:
        raise HTTPException(404, f"unknown attack. choose from {ATTACKS}")
    if not 0.0 <= strength <= 1.0:
        raise HTTPException(422, "strength must be between 0 and 1")
    return system.run_scenario(attack, strength)


@app.get("/history")
def history(limit: int = 100):
    return audit.history(system.con, limit)


@app.get("/thresholds")
def thresholds():
    th = compute_thresholds()
    return {
        **th.as_dict(),
        "qber_threshold": qber_threshold(),
        "test_pairs": C.N_TEST_PAIRS,
        "derivation": {
            "method": "Binomial inverse survival / quantile function",
            "accept_rule": f"P(honest block > s_a | Binom(L={th.block_size}, p={th.expected_error})) <= alpha={th.alpha}",
            "reject_rule": f"P(forger block <= s_v | Binom(L={th.block_size}, p={th.forgery_rate})) < alpha={th.alpha}",
            "false_alarm_per_block": th.alpha,
            "false_alarm_system": 1 - (1 - th.alpha) ** C.DIGEST_BITS,
        },
    }


@app.get("/audit/verify")
def audit_verify():
    return audit.verify_chain(system.con)


@app.get("/detection-curve")
def detection_curve(trials: int = 40):
    return system.detection_curve(trials=min(trials, 200))


@app.get("/shor-toy")
def shor_toy():
    counts, factors = shor_run()
    return {
        "N": 15,
        "a": 7,
        "counts": counts,
        "factors_found": factors,
        "note": "Toy demo on the simulator. Shows why RSA is at risk; it does not attack real RSA.",
    }


@app.get("/reality-check")
def reality_check():
    return {
        "real": [
            "Mathematics of qubits, Pauli operators, Born rule for measurement probabilities",
            "Bell states (|Φ⁺⟩ etc.), entanglement correlations, teleportation protocol with X/Z corrections",
            "Binomial hypothesis testing: thresholds derived analytically from scipy.stats.binom",
            "No-cloning theorem implies a forger who measures disturbs the state → detectable mismatch rate",
            "QBER ≈ ε_eve/3 for intercept-resend on Bell pairs (proven in tests)",
            "Shor's algorithm circuit for period-finding (textbook, verified on Aer simulator)",
        ],
        "simulated": [
            "All qubits are NumPy state vectors (2-element complex arrays), not physical quantum states",
            "Measurement is via Born-rule inner products, not physical photon detectors",
            "Teleportation in bulk is modelled as ideal + Pauli noise (Qiskit circuit proves the ideal case)",
            "Eavesdropper is a software model that measures and resends, not a physical wiretap",
            "Bell-pair channel test uses the NumPy engine (agreement with Qiskit statevector verified in tests)",
            "Classical authenticated channels and identity management are assumed, not cryptographically implemented",
        ],
        "not_claimed": [
            "Physical quantum security — no real quantum hardware is used anywhere",
            "A production-ready QDS — this is an educational prototype",
            "That simulated attacks prove real-world security — they validate detection logic only",
            "Resistance to all quantum attacks — we model specific, well-known attack strategies",
            "Scalability to real key sizes — the demo uses 8-bit digests and 128-qubit blocks",
            "Any use of AI or ML — detection uses ONLY measurement statistics and mathematical thresholds",
        ],
    }


@app.get("/config")
def get_config():
    return {
        "DIGEST_BITS": C.DIGEST_BITS,
        "BLOCK_SIZE": C.BLOCK_SIZE,
        "READOUT_ERROR": C.READOUT_ERROR,
        "CHANNEL_NOISE": C.CHANNEL_NOISE,
        "EXPECTED_ERROR": C.EXPECTED_ERROR,
        "FORGERY_MISMATCH": C.FORGERY_MISMATCH,
        "ALPHA": C.ALPHA,
        "N_TEST_PAIRS": C.N_TEST_PAIRS,
        "FRESHNESS_SECONDS": C.FRESHNESS_SECONDS,
        "MAX_COPIES": C.MAX_COPIES,
    }
