# Quantum-Inspired Cyber Threat Detection for Digital Signature Security (SIH 26141)

> **Academic prototype — Quantum-SIMULATED software. Not physical quantum hardware.**

A statistics-based (zero AI/ML) cybersecurity framework that simulates a Quantum Digital Signature (QDS) architecture inspired by Gottesman-Chuang, simulates sophisticated cyber attacks, and detects them using quantum measurement statistics, Bell-state entanglement verification, and binomial-derived decision thresholds.

---

## Deliverables Summary

This repository fulfills all items specified in the **Expected Deliverables Table**:

| S.No | Deliverable | Documentation & Code Reference | Status |
| :--- | :--- | :--- | :---: |
| 1 | **Mathematical Model of Teleportation-based QDS** | [DELIVERABLES.md](DELIVERABLES.md), `quantum/` (`paulis.py`, `bell.py`, `teleport.py`) | Completed |
| 2 | **Quantum-Inspired Threat Detection Framework** | [DELIVERABLES.md](DELIVERABLES.md), `detection/` (`thresholds.py`, `statistics.py`, `classifier.py`) | Completed |
| 3 | **Signature Generation & Verification Module** | [DELIVERABLES.md](DELIVERABLES.md), `qds/` (`protocol.py`, `service.py`) | Completed |
| 4 | **Attack Simulation Module** | [DELIVERABLES.md](DELIVERABLES.md), `attacks/` (`simulate.py`), `detection/replay.py` | Completed |
| 6 | **Software Framework / Prototype** | [DELIVERABLES.md](DELIVERABLES.md), `backend/main.py`, `frontend/app.py`, `tests/` | Completed |

For full formal derivations, mathematical formulas, and test metrics, see [DELIVERABLES.md](DELIVERABLES.md) and [docs/QDS_Mentor_Guide.md](docs/QDS_Mentor_Guide.md).

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation & Setup
```bash
# Clone the repository
git clone https://github.com/maliniaids-stack/quantum-threat-detector.git
cd quantum-threat-detector

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run Automated Verification Tests
```bash
python -m pytest tests/ -v
```
All 51 automated tests must pass with 0 failures.

### 4. Launch Services
**Terminal 1 — REST API Backend:**
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
API Documentation will be available at: `http://127.0.0.1:8000/docs`

**Terminal 2 — Threat Monitoring Console:**
```bash
streamlit run frontend/app.py --server.port 8501
```
Dashboard will be available at: `http://localhost:8501`

---

## Project Structure

```
quantum-threat-detector/
├── DELIVERABLES.md            # Formal mapping to SIH expected deliverables
├── README.md                  # System overview and quick-start guide
├── requirements.txt           # Pinned library dependencies
├── config.py                  # System parameters and binomial derivations
├── .gitignore                 # Git ignore rules
│
├── quantum/                   # Quantum Mechanics Core
│   ├── paulis.py              #   Pauli operators and 6 eigenstates (|0>, |1>, |+>, |->, |+i>, |-i>)
│   ├── measure.py             #   Projective measurement operators, Born rule, readout noise
│   ├── bell.py                #   Bell pairs (Phi+, Psi+), entanglement verification, QBER channel test
│   ├── teleport.py            #   Teleportation circuit with mid-circuit classical feed-forward
│   └── shor_toy.py            #   Period-finding circuit factoring N = 15 on AerSimulator
│
├── qds/                       # Quantum Digital Signature Protocol
│   ├── protocol.py            #   Key generation, distribution, signing, and verification
│   └── service.py             #   End-to-end coordinated service and Monte Carlo pipeline
│
├── attacks/                   # Cyber Threat Simulation Module
│   └── simulate.py            #   Blind forgery, informed forgery, impersonation, channel tampering
│
├── detection/                 # Threat Detection Engine (Strictly No AI/ML)
│   ├── thresholds.py          #   Binomial distribution dual-threshold decision engine
│   ├── statistics.py          #   p-values, observed error rates, Bayesian posterior
│   ├── classifier.py          #   Rule-based threat vector classification
│   ├── replay.py              #   One-time key registry and timestamp freshness guard
│   └── audit.py               #   SHA-256 hash-chained cryptographic audit ledger
│
├── backend/                   # REST API Service
│   └── main.py                #   FastAPI endpoints with CORS support
│
├── frontend/                  # Institutional Evaluation Console
│   └── app.py                 #   Streamlit application with Plotly visualizations
│
├── tests/                     # Test Suite (51 automated tests)
│   ├── conftest.py            #   Shared fixtures
│   ├── test_pipeline.py       #   39 unit/integration tests for quantum, detection, and attacks
│   └── test_api.py            #   12 comprehensive API endpoint smoke and integration tests
│
└── docs/                      # Architectural Documentation
    └── QDS_Mentor_Guide.md    #   Comprehensive 90KB guide with proofs and defense answers
```

---

## Detection Engine Architecture

The detection logic relies purely on statistical hypothesis testing over projective quantum measurements:

| Parameter | Value | Description |
| :--- | :---: | :--- |
| Block Size ($L$) | 128 | Pauli qubits per digest bit block |
| Honest Error Rate ($p_0$) | 0.02 | Expected experimental readout error |
| Forger Error Rate ($p_1$) | 0.333 / 0.50 | Theoretical mismatch rate imposed by No-Cloning theorem |
| False Alarm Rate ($\alpha$) | $10^{-6}$ | Target bound on false rejection per block |
| **Accept Threshold ($s_a$)** | **$\le 8$** | Verdict = ACCEPT if $\max_i(\text{mismatches}_i) \le s_a$ |
| **Reject Threshold ($s_v$)** | **$> 26$** | Verdict = REJECT if $\max_i(\text{mismatches}_i) > s_v$ |
| **Inconclusive Interval** | **$(8, 26]$** | Verdict = INCONCLUSIVE if marginal |

---

## Attack Coverage & Verification

| Threat Scenario | Simulated Vector | Detection Method | Test Validation |
| :--- | :--- | :--- | :---: |
| **Blind Forgery** | Random eigenstate substitution | Mismatch rate $\approx 50\% > s_v$ | Verified (10/10) |
| **Informed Forgery** | Measure-and-guess on public key copy | Mismatch rate $\approx 33.3\% > s_v$ | Verified (10/10) |
| **Replay Attack** | Reusing valid signature / expired timestamp | Freshness guard window ($\Delta t \le 60\text{s}$) | Verified (10/10) |
| **Impersonation** | Unregistered private key claim | Signer identity mismatch + quantum failure | Verified (10/10) |
| **Unauthorized Verifier**| Verification without distributed public key| Verifier registry validation check | Verified (10/10) |
| **Channel Tampering** | Intercept-resend eavesdropper (Eve) | Bell-pair QBER exceeds threshold ($> 10\%$) | Verified (10/10) |

---

## Scope Disclosures & Academic Integrity

- **Simulated States**: All quantum states are modeled as complex statevectors in NumPy / Qiskit Aer. No physical quantum processor is claimed.
- **Zero AI/ML**: Detection is based exclusively on closed-form binomial probabilities and hypothesis testing.
- **Classical Replay Guard**: Replay attacks are mitigated through cryptographic nonces and time windows; quantum mechanics alone does not prevent message replay.
- **Shor Algorithm Scope**: The Shor demo illustrates the vulnerability of classical RSA-15 to motivate quantum-safe signature research.

---

## License & Attribution

Developed for **Smart India Hackathon (SIH 26141)**.
Based on the foundations established in Gottesman & Chuang (2001), *Quantum Digital Signatures*, arXiv:quant-ph/0105032.
