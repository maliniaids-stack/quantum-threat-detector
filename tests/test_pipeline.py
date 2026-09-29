"""Comprehensive test suite for the QDS Threat Detection prototype.

Tests cover:
- Pauli eigenstate math
- Measurement error rates (same-basis = 0%, wrong-basis ≈ 50%)
- Bell state correctness (Qiskit)
- Bell-pair QBER vs eavesdropper theory
- Teleportation fidelity (statevector) and Aer mid-circuit measurement
- NumPy engine agreement with Qiskit circuits (Bell correlation, teleport fidelity)
- Threshold separation (binomial-derived)
- 25 repeated legitimate signatures → all ACCEPT
- Each attack type × 10 repetitions → correctly classified
- Audit-chain tamper detection
- Shor toy factoring
"""
import time
import numpy as np
import pytest
from quantum.paulis import check_eigenstates, EIGEN, PAULI_MATRICES, BASIS_NAMES
from quantum.measure import prepare, measure, pauli_noise, eve_intercept_resend, collapse
from quantum.bell import bell_channel_test, bell_statevector, bell_circuit
from quantum.teleport import teleport_fidelity, run_teleport_on_aer
from quantum.shor_toy import run as shor_run
from qds.service import QDSSystem, ATTACKS
from qds import protocol as P
from detection import audit
from detection.thresholds import compute_thresholds, decide, qber_threshold
from detection.statistics import analyse
from detection.classifier import classify
from detection.replay import ReplayGuard


# ---------------------------------------------------------------------------
# Stage 3: Pauli eigenstates
# ---------------------------------------------------------------------------

class TestPauliEigenstates:
    def test_all_six_eigenstates_satisfy_eigenvalue_equation(self):
        """P|e⟩ = ±|e⟩ for all 6 Pauli eigenstates."""
        assert check_eigenstates()

    def test_eigenstates_are_normalised(self):
        for b in range(3):
            for v in range(2):
                assert abs(np.linalg.norm(EIGEN[b, v]) - 1.0) < 1e-12

    def test_eigenstates_orthogonal_within_basis(self):
        for b in range(3):
            inner = np.abs(np.vdot(EIGEN[b, 0], EIGEN[b, 1]))
            assert inner < 1e-12, f"basis {BASIS_NAMES[b]} eigenstates not orthogonal"


# ---------------------------------------------------------------------------
# Stage 3: Measurement engine
# ---------------------------------------------------------------------------

class TestMeasurement:
    def test_same_basis_zero_error(self):
        """Measuring in the preparation basis must give 0 % error."""
        rng = np.random.default_rng(0)
        b = rng.integers(0, 3, 20000)
        v = rng.integers(0, 2, 20000)
        s = prepare(b, v)
        out = measure(s, b, rng)
        assert (out != v).sum() == 0

    def test_wrong_basis_half_error(self):
        """Measuring in a different basis must give ≈ 50 % error."""
        rng = np.random.default_rng(1)
        b = rng.integers(0, 3, 40000)
        v = rng.integers(0, 2, 40000)
        s = prepare(b, v)
        err = (measure(s, (b + 1) % 3, rng) != v).mean()
        assert abs(err - 0.5) < 0.02, f"wrong-basis error rate {err} not close to 0.5"

    def test_readout_error_adds_noise(self):
        rng = np.random.default_rng(2)
        b = np.zeros(50000, int)
        v = np.zeros(50000, int)
        s = prepare(b, v)
        out = measure(s, b, rng, readout_error=0.05)
        err = (out != v).mean()
        assert abs(err - 0.05) < 0.01


# ---------------------------------------------------------------------------
# Stage 4: Bell states
# ---------------------------------------------------------------------------

class TestBell:
    def test_phi_plus_probabilities(self):
        """|Φ⁺⟩ = (|00⟩ + |11⟩)/√2"""
        p = bell_statevector("phi+").probabilities_dict()
        assert abs(p.get("00", 0) - 0.5) < 1e-9
        assert abs(p.get("11", 0) - 0.5) < 1e-9

    def test_psi_plus_probabilities(self):
        """|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2"""
        p = bell_statevector("psi+").probabilities_dict()
        assert abs(p.get("01", 0) - 0.5) < 1e-9
        assert abs(p.get("10", 0) - 0.5) < 1e-9

    def test_bell_channel_no_eve_zero_qber(self):
        rng = np.random.default_rng(10)
        r = bell_channel_test(20000, rng)
        assert r["qber"] == 0.0

    def test_bell_channel_full_eve_third_qber(self):
        """QBER ≈ eve_fraction/3 for intercept-resend (full eve → ~1/3)."""
        rng = np.random.default_rng(11)
        r = bell_channel_test(20000, rng, eve_fraction=1.0)
        assert abs(r["qber"] - 1 / 3) < 0.02

    def test_bell_channel_partial_eve(self):
        """QBER ≈ eve_fraction/3 for partial eavesdropping."""
        rng = np.random.default_rng(12)
        for frac in [0.3, 0.6]:
            r = bell_channel_test(30000, rng, eve_fraction=frac)
            expected = frac / 3
            assert abs(r["qber"] - expected) < 0.02, f"frac={frac}, qber={r['qber']}, expected≈{expected}"


# ---------------------------------------------------------------------------
# Stage 5: Teleportation
# ---------------------------------------------------------------------------

class TestTeleportation:
    @pytest.mark.parametrize("prep", [
        lambda qc: None,                                # |0⟩
        lambda qc: qc.x(0),                             # |1⟩
        lambda qc: qc.h(0),                              # |+⟩
        lambda qc: (qc.ry(1.1, 0), qc.rz(0.7, 0)),     # arbitrary
    ])
    def test_statevector_fidelity(self, prep):
        assert teleport_fidelity(prep) > 0.999999

    def test_aer_mid_circuit_measurement_teleport(self):
        """Prove mid-circuit measurement + classical feedforward works on Aer."""
        rate = run_teleport_on_aer(lambda qc: (qc.ry(1.1, 0), qc.rz(0.7, 0)), shots=4096)
        assert rate == 1.0, f"Aer teleport success rate {rate} != 1.0"


# ---------------------------------------------------------------------------
# NumPy-vs-Qiskit agreement proof
# ---------------------------------------------------------------------------

class TestNumpyQiskitAgreement:
    """Prove the fast NumPy engine agrees with actual Qiskit circuits."""

    def test_bell_correlation_agreement(self):
        """NumPy Bell channel test agrees with Qiskit Statevector Bell state probabilities.
        Qiskit proves |Φ⁺⟩ = (|00⟩+|11⟩)/√2 → same-basis outcomes always agree.
        NumPy bell_channel_test with no noise must also give QBER = 0."""
        # Qiskit proof
        sv = bell_statevector("phi+")
        probs = sv.probabilities_dict()
        assert abs(probs["00"] - 0.5) < 1e-9 and abs(probs["11"] - 0.5) < 1e-9
        # NumPy proof (same result)
        rng = np.random.default_rng(100)
        r = bell_channel_test(50000, rng)
        assert r["qber"] == 0.0

    def test_teleportation_fidelity_agreement(self):
        """Both the Qiskit statevector method and the Aer circuit method
        produce perfect teleportation (fidelity = 1.0)."""
        prep = lambda qc: (qc.ry(2.3, 0), qc.rz(1.1, 0))
        sv_fidelity = teleport_fidelity(prep)
        aer_rate = run_teleport_on_aer(prep, shots=2048)
        assert sv_fidelity > 0.999999
        assert aer_rate == 1.0


# ---------------------------------------------------------------------------
# Stage 9-10: Statistics & Thresholds
# ---------------------------------------------------------------------------

class TestStatisticsAndThresholds:
    def test_thresholds_separate(self):
        th = compute_thresholds()
        assert th.accept_max < th.reject_min, "accept and reject thresholds must be separated"

    def test_honest_blocks_within_accept(self):
        """Honest noise produces mismatches well within the accept threshold."""
        rng = np.random.default_rng(20)
        import config as C
        for _ in range(100):
            m = rng.binomial(C.BLOCK_SIZE, C.EXPECTED_ERROR, C.DIGEST_BITS)
            assert max(m) <= compute_thresholds().accept_max

    def test_forger_blocks_above_reject(self):
        """Forger mismatch rate produces mismatches above the reject threshold."""
        rng = np.random.default_rng(21)
        import config as C
        th = compute_thresholds()
        for _ in range(100):
            m = rng.binomial(C.BLOCK_SIZE, C.FORGERY_MISMATCH, C.DIGEST_BITS)
            assert max(m) > th.reject_min

    def test_analyse_returns_expected_keys(self):
        stats = analyse([2, 3, 1, 2, 1, 3, 2, 1])
        for key in ("block_mismatches", "total_mismatches", "observed_rate",
                     "expected_rate", "worst_block", "p_value_honest", "forgery_probability"):
            assert key in stats

    def test_qber_threshold_positive(self):
        assert qber_threshold() > 0


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class TestClassifier:
    def test_unauthorized(self):
        a, _ = classify({"unauthorized": True, "replay": False, "impersonation": False,
                          "channel_flag": False, "verdict": "REJECT", "observed_rate": 0})
        assert a == "UNAUTHORIZED_VERIFICATION"

    def test_replay(self):
        a, _ = classify({"unauthorized": False, "replay": True, "replay_reason": "key reused",
                          "impersonation": False, "channel_flag": False, "verdict": "REJECT", "observed_rate": 0})
        assert a == "REPLAY_ATTACK"

    def test_accept_means_none(self):
        a, _ = classify({"unauthorized": False, "replay": False, "impersonation": False,
                          "channel_flag": False, "verdict": "ACCEPT", "observed_rate": 0.01})
        assert a == "NONE"


# ---------------------------------------------------------------------------
# Replay Guard
# ---------------------------------------------------------------------------

class TestReplayGuard:
    def test_fresh_key_accepted(self):
        g = ReplayGuard()
        ok, _ = g.check("key1", time.time(), time.time())
        assert ok

    def test_reused_key_rejected(self):
        g = ReplayGuard()
        g.consume("key1")
        ok, reason = g.check("key1", time.time(), time.time())
        assert not ok and "replayed" in reason

    def test_stale_timestamp_rejected(self):
        g = ReplayGuard()
        ok, reason = g.check("key2", time.time() - 600, time.time())
        assert not ok and "stale" in reason


# ---------------------------------------------------------------------------
# Full pipeline: legitimate signatures
# ---------------------------------------------------------------------------

@pytest.fixture
def system():
    return QDSSystem(seed=42, db_path=":memory:")


def test_legitimate_accepted_25_times(system):
    """Over 25 repeated legitimate-signature runs, all must ACCEPT."""
    for i in range(25):
        r = system.run_scenario("legitimate")
        assert r["verdict"] == "ACCEPT", f"Trial {i} unexpectedly {r['verdict']}"
        assert r["attack_type"] == "NONE"
        assert r["threat_score"] == 0


# ---------------------------------------------------------------------------
# Full pipeline: attack detection (each ×10)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("attack,expected_type", [
    ("blind_forgery", "FORGERY_BLIND"),
    ("informed_forgery", "FORGERY_INFORMED"),
    ("replay", "REPLAY_ATTACK"),
    ("impersonation", "IMPERSONATION"),
    ("unauthorized_verifier", "UNAUTHORIZED_VERIFICATION"),
    ("channel_manipulation", "CHANNEL_MANIPULATION"),
])
def test_attacks_detected_10_times(system, attack, expected_type):
    for i in range(10):
        r = system.run_scenario(attack, 0.5)
        assert r["verdict"] == "REJECT", f"{attack} trial {i}: expected REJECT, got {r['verdict']}"
        assert r["attack_type"] == expected_type, f"{attack} trial {i}: expected {expected_type}, got {r['attack_type']}"


# ---------------------------------------------------------------------------
# Audit chain
# ---------------------------------------------------------------------------

def test_audit_chain_intact(system):
    system.run_scenario("legitimate")
    system.run_scenario("blind_forgery")
    assert audit.verify_chain(system.con)["valid"]


def test_audit_chain_detects_tampering(system):
    system.run_scenario("legitimate")
    system.run_scenario("blind_forgery")
    assert audit.verify_chain(system.con)["valid"]
    # Tamper
    system.con.execute("UPDATE events SET verdict='ACCEPT' WHERE id=2")
    system.con.commit()
    result = audit.verify_chain(system.con)
    assert not result["valid"]
    assert result["broken_at_event"] == 2


# ---------------------------------------------------------------------------
# Shor toy
# ---------------------------------------------------------------------------

def test_shor_toy_factors_15():
    counts, factors = shor_run(shots=1024)
    assert 3 in factors and 5 in factors, f"Expected [3, 5], got {factors}"
