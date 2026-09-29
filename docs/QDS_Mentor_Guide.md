# Quantum-Inspired QDS Threat Detection — The Complete Mentor Guide
### SIH 26141 · Parts 2 to 11 in one document · Written for a complete beginner

> **Honesty statement (read first).** This is an **academic, quantum-simulated software prototype**. Everything runs on a normal
> computer. It is **not** a real quantum computer, **not** physically secure quantum cryptography, and **not** a production QDS.
> Simulated attacks do **not** prove real-world security. Every slide, demo and answer you give should say this clearly.

**How to use this guide.** Read Part 2 first (concepts), then Parts 3–4 (design and maths), then build Part 5 stage by stage.
The code in Part 5 is the **real, tested project** (14 automated tests pass; the API and the dashboard were smoke-tested).
Parts 6–11 cover structure, dashboard, honesty rules, and your SIH presentation.

**Contents**
1. Part 2 — Concepts from zero (20 ideas)
2. Part 3 — Design: protocol, architecture, the five attack workflows
3. Part 4 — The minimum mathematics
4. Part 5 — Build it: Stages 1–14
5. Part 6 — Project structure · Part 7 — Dashboard
6. Part 8 — No fake claims · Part 9 — Limitations and future scope
7. Part 10 — SIH presentation kit · Part 11 — Judge Q&A

---

# PART 2 — Concepts from zero

Each concept has four parts: **Simple** (plain meaning), **Analogy**, **Tiny example**, **Why we need it**.
Maths is kept for Part 4.

### 2.1 Cryptography
- **Simple:** Using math to keep information secret or trustworthy.
- **Analogy:** A padlock: anyone can see it, only the key-holder opens it.
- **Tiny example:** Turning "HELLO" into "KHOOR" by shifting each letter by 3 (the old Caesar cipher).
- **Why here:** Our whole project protects the *trustworthiness* of signed messages.

### 2.2 Digital signature
- **Simple:** A code that proves **who** sent a message and that it was **not changed**.
- **Analogy:** A wax seal that is different for every letter and only you can make.
- **Tiny example:** `sign("Pay 500 INR", private key)` gives a signature. Anyone can `verify(...)`. Change "500" to "5000" and verification fails.
- **Why here:** QDS is a digital signature built on quantum states instead of a hard math problem.

### 2.3 Why RSA and ECC are used
- **Simple:** Their security rests on problems that are easy one way and extremely hard to reverse.
- **Analogy:** Mixing two paint colours is easy; separating them again is nearly impossible.
- **Tiny example:** 7 × 13 = 91 is instant. Given a 600-digit number, finding its two prime factors is infeasible for ordinary computers (RSA). ECC uses a similar one-way problem on curves.
- **Why here:** These are exactly what a quantum computer threatens, which is why QDS exists.

### 2.4 Why quantum computers threaten RSA/ECC
- **Simple:** Shor's algorithm (1994) solves factoring and the curve problem fast on a large, reliable quantum computer.
- **Analogy:** Everyone else tries keys one by one; a quantum computer finds the lock's hidden rhythm.
- **Tiny example:** In our project we run a **toy** Shor on the simulator to factor 15 = 3 × 5.
- **Why here:** This is the "why quantum" story for judges. Honest note: no machine today can break RSA-2048; the risk is about the future and about data that must stay trustworthy for decades.

### 2.5 Bit vs qubit
- **Simple:** A bit is 0 or 1. A qubit is described by two numbers, α and β, that decide the *probabilities* of getting 0 or 1 when you look.
- **Analogy:** A spinning coin: while spinning it is "both", when it lands (you measure) you see heads or tails. (The analogy is imperfect: a qubit is not just a coin we don't know the result of.)
- **Tiny example:** The state `|+⟩` gives 0 or 1 with 50% each. The state `|0⟩` always gives 0.
- **Why here:** Our public key is a list of qubits.

### 2.6 Quantum state
- **Simple:** The complete description of a qubit right now, written as `|ψ⟩ = α|0⟩ + β|1⟩`.
- **Analogy:** The exact angle of a spinning arrow; you never see the angle directly, only the result of a question you ask it.
- **Tiny example:** `|0⟩ = (1, 0)`, `|1⟩ = (0, 1)`, `|+⟩ = (1/√2, 1/√2)`.
- **Why here:** The signer's secret is *which* states were prepared.

### 2.7 Measurement
- **Simple:** Asking a qubit a question. You get one random answer (0 or 1), and the qubit **collapses** to match it.
- **Analogy:** Opening a scratch card: one look, and you can never restore it.
- **Tiny example:** Measure `|+⟩` in the 0/1 way: you get 0 or 1 (50/50); measure again immediately and you get the same answer.
- **Why here:** Measuring disturbs states. This disturbance is how eavesdroppers and forgers get caught.

### 2.7b No-cloning (the key physical rule)
- **Simple:** You cannot make a perfect copy of an unknown quantum state.
- **Analogy:** A one-of-a-kind painting that cannot be photocopied without damaging it.
- **Tiny example:** If you knew the state was `|0⟩` or `|+⟩` but not which, no machine can copy it perfectly.
- **Why here:** It is why a public key made of quantum states cannot simply be duplicated and forged.

### 2.8 Pauli X, Y and Z
- **Simple:** Three basic operations and also three *questions* you can ask a qubit. **Z** asks "0 or 1?", **X** asks "+ or −?", **Y** asks "+i or −i?".
- **Analogy:** Three different filters. Once you ask one question, the answers to the other two become random.
- **Tiny example:** The X operator flips `|0⟩` to `|1⟩`.
- **Why here:** Our key elements are randomly prepared in one of these three "question bases".

### 2.9 Eigenstates
- **Simple:** For each Pauli question, two special states give a **certain** answer. These are its eigenstates.
- **Analogy:** A question with two "sure answers"; asking a different question about the same state gives a coin flip.
- **Tiny example:** `|0⟩,|1⟩` for Z; `|+⟩,|−⟩` for X; `|+i⟩,|−i⟩` for Y. Six states in total; they are the "alphabet" of our public key.
- **Why here:** The problem statement says "Pauli eigenstates": this is exactly what we use.

### 2.10 Projective measurement
- **Simple:** Measuring by comparing the state with the eigenstates; each outcome has probability `|⟨e|ψ⟩|²`.
- **Analogy:** A sorting machine that forces every item into exactly one of two bins.
- **Tiny example:** Measure `|0⟩` in the X question: probability 50% for + and 50% for −.
- **Why here:** It is the core operation of verification and of eavesdropping.

### 2.11 Entanglement
- **Simple:** Two qubits share one joint state; their answers are linked even though each alone looks random.
- **Analogy:** Two magic coins that always land the same way, no matter how far apart (no message travels between them).
- **Tiny example:** A Bell pair measured in the same basis always gives matching answers.
- **Why here:** It lets us test the channel and teleport states.

### 2.12 Bell states
- **Simple:** The four standard maximally entangled two-qubit states. Example: `|Φ+⟩ = (|00⟩ + |11⟩)/√2`.
- **Analogy:** The "official" magic-coin pairs.
- **Tiny example:** Circuit: Hadamard on qubit 0, then CNOT from 0 to 1.
- **Why here:** (1) Channel health test: an eavesdropper breaks the matching. (2) The resource for teleportation.

### 2.13 Quantum teleportation
- **Simple:** Moving an unknown quantum state from Alice to Bob using a shared Bell pair and **two classical bits**. The original is destroyed.
- **Analogy:** Faxing a document while shredding the original; Bob needs a phone call (2 bits) to decode the fax.
- **Tiny example:** Alice teleports `|ψ⟩`; her measurement gives bits (m0, m1); Bob applies X if m1 = 1 and Z if m0 = 1.
- **Why here:** It is how the signer's public-key states travel to the verifier. Nothing travels faster than light.

### 2.14 Pauli correction
- **Simple:** The small X and/or Z fix-up Bob applies after teleportation, chosen by Alice's two bits.
- **Analogy:** The decoder key for the fax.
- **Tiny example:** bits `01` gives X, `10` gives Z, `11` gives both, `00` gives nothing.
- **Why here:** Without it Bob's state is scrambled; our tests prove fidelity 1.0 after correction.

### 2.15 Quantum Digital Signature (QDS)
- **Simple:** A signature scheme where the public key is a set of quantum states, so security comes from physics (no-cloning, measurement disturbance).
- **Analogy:** A sealed, self-damaging sample of your handwriting that verifiers can test but nobody can duplicate.
- **Tiny example:** Gottesman and Chuang proposed the first QDS in 2001.
- **Why here:** It is the system we simulate and defend.

### 2.16 How our QDS works (simplified)
1. **Key generation.** The signer makes secret (basis, value) pairs for each digest position and bit value.
2. **Distribution.** Public-key states (Pauli eigenstates) travel to the verifier; a Bell-pair test checks the channel.
3. **Signing.** The message + nonce + timestamp is hashed to a digest; the signer reveals the private-key blocks chosen by the digest bits.
4. **Verification.** The verifier measures its stored states in the claimed bases and counts mismatches per block.
5. **Decision.** Few mismatches: ACCEPT. Many: REJECT. In between: INCONCLUSIVE.

- **Why one-time keys?** Revealing a private-key block uses it up; every signature gets a fresh key. This is also the replay defence.

### 2.17 Forgery, impersonation, replay
- **Forgery:** creating a signature for a message the signer never signed. *Analogy:* faking a cheque.
- **Impersonation:** pretending to *be* the signer. *Analogy:* wearing someone's uniform.
- **Replay:** re-sending a genuine old signature. *Analogy:* photocopying a real cheque and cashing it again.
- **Why here:** These are the threats the problem statement wants detected.

### 2.18 Quantum-channel manipulation
- **Simple:** An attacker tampers with the qubits in transit (intercept, measure, resend).
- **Analogy:** Someone steams open sealed letters and reseals them clumsily.
- **Tiny example:** Eve measures a qubit in a random basis; two times out of three she picks the wrong basis and disturbs it.
- **Why here:** The disturbance shows up as extra errors in the Bell-pair test and in later verification.

### 2.19 Detecting attacks with measurement statistics
- **Simple:** Honest noise produces a small, predictable error rate; attacks produce a much larger one.
- **Analogy:** A smoke alarm: a little steam is normal; thick smoke means fire.
- **Tiny example:** Honest: about 2% mismatches. Measure-and-guess forger: about 33%. Blind guesser: about 50%.
- **Why here:** This is the "no AI/ML" detection method: pure counting and probability.

### 2.20 Threshold
- **Simple:** A line on the mismatch count that turns a number into a decision.
- **Analogy:** A pass mark in an exam.
- **Tiny example:** Our system has **two** lines: at most 13 mismatches in every block is ACCEPT; more than 18 in any block is REJECT; in between is INCONCLUSIVE.
- **Why here:** We derive the lines from probability so we can state exactly how rare false alarms are.

---
# PART 3 — Design: protocol, architecture, workflows

## 3.1 What we choose to build and why (the "better approach")

The problem statement mixes several quantum ideas. A *technically honest* design puts each idea where it genuinely fits:

| Idea from the problem statement | Where we use it | Honest note |
|---|---|---|
| Pauli eigenstates | The quantum public key (six-state alphabet) | Core of QDS |
| Projective measurement | Verification and eavesdropping | Core |
| Statistical analysis + thresholds | The detection engine | Core, no ML |
| Bell-state entanglement | **Channel health test** (QBER) | Entanglement-based checking is standard in quantum key distribution |
| Teleportation + Pauli correction | **Transporting key states** to the verifier | Not part of the simplest QDS; a legitimate transport layer |
| Replay detection | **Classical** layer: one-time key IDs, nonce, timestamp | Quantum physics alone cannot stop replay |
| Unauthorized verification | Verifier registry + copy budget | Real QDS limits copies; we simulate the counter |

**Upgrades over a naive design:** two thresholds (three verdicts), thresholds computed from binomial probability, per-block checks,
a noise model, Monte-Carlo detection curves, a hash-chained audit log, a toy Shor demo, and a Reality Check panel.

## 3.2 Corrected architecture

```
                 ┌───────────────────────────────────────────┐
                 │      ATTACK SIMULATOR (plug-in points)    │
                 │ blind/informed forgery · impersonation    │
                 │ replay · unauthorized verifier · Eve      │
                 └───────┬───────────────┬──────────────┬────┘
                         │               │              │
SETUP        Signer ─► Key generation ─► Quantum public key (Pauli eigenstates)
                                             │
QUANTUM      Bell-pair link ─► Channel test (QBER vs threshold)
CHANNEL      Teleport key states ─► Pauli correction ─► Verifier's stored copy
                                             │
SIGNING      Message + nonce + timestamp ─► SHA-256 digest ─► reveal key blocks
                                             │
CLASSICAL    Registry check ─► Replay/freshness check
GATE                                         │
VERIFY       Projective measurement of stored states ─► mismatches per block
                                             │
ANALYSIS     Observed vs expected ─► p-value ─► forgery probability
                                             │
DECISION     Two-threshold engine ─► ACCEPT / INCONCLUSIVE / REJECT
                                             │
CLASSIFY     Rule-based classifier (no ML) ─► attack type + threat score
                                             │
RECORD       SQLite + hash-chained audit log
                                             │
SERVE        FastAPI ─► Streamlit dashboard (+ Reality Check)
```

**Components in one line each**

| Component | Job |
|---|---|
| `quantum/paulis.py` | Pauli matrices and the six eigenstates |
| `quantum/measure.py` | Prepare states, measure, add noise, model an intercepting attacker |
| `quantum/bell.py` | Bell-state circuits (Qiskit) and the channel-health (QBER) test |
| `quantum/teleport.py` | Teleportation circuits with Pauli correction (Qiskit + Aer) |
| `qds/protocol.py` | Key generation, distribution, signing, quantum verification |
| `qds/service.py` | The pipeline: gates, verification, statistics, decision, logging |
| `attacks/simulate.py` | Forgery and impersonation simulators |
| `detection/statistics.py` | Observed vs expected, p-value, forgery probability |
| `detection/thresholds.py` | Two thresholds derived from binomial probability |
| `detection/classifier.py` | Explainable rules that name the attack |
| `detection/replay.py` | One-time key IDs and freshness window |
| `detection/audit.py` | Tamper-evident event log |
| `backend/main.py` | REST API |
| `frontend/app.py` | Dashboard |

**Why Qiskit *and* NumPy?** Qiskit builds and checks the real circuits (Bell, teleportation, toy Shor). Verifying thousands of qubits
one Qiskit circuit at a time would be slow, so the bulk statistics use a small vectorised NumPy engine. A test checks the two
agree (Bell rule and teleportation fidelity). This split is honest and is a good answer to a judge.

## 3.3 Workflows: what happens in each case

Numbers below come from real runs of the prototype (one run each; they vary slightly with the random seed).
Design values: block size L = 128 qubits, 8 digest blocks, honest error ≈ 2%.
Thresholds: **ACCEPT if every block has ≤ 13 mismatches; REJECT if any block has > 18.**

### Case A — Legitimate signature
1. Signer creates a fresh key; states are distributed; Bell test says the channel is healthy (QBER ≈ 1% vs limit 6%).
2. Signer signs "Transfer 500 INR to Bob" with a nonce and timestamp.
3. Verifier passes the registry check and the replay/freshness check.
4. Verifier measures stored states in the claimed bases. Typical result: about 2.2% mismatches, worst block 5 (≤ 13).
5. **ACCEPT**, threat score 0, key marked used. Over 400 legitimate runs, none was wrongly flagged.

### Case B — Forged signature
Two attacker types are simulated:
- **Blind forger** guesses every basis and value. The verifier measures the real state in the guessed basis: if the basis is right (1/3) it matches only when the value is right (1/2), otherwise (2/3) it is a coin flip. Overall mismatch is **1/2**. Observed ≈ 49%, worst block ≈ 67. **REJECT**, classified `FORGERY_BLIND`.
- **Informed forger** holds one legitimate copy of the public key and measures it in a random basis, then claims the result. Right basis (1/3): perfect. Wrong basis (2/3): claim is random, so mismatch 1/2. Overall mismatch **1/3**. Observed ≈ 35%, worst block ≈ 52. **REJECT**, classified `FORGERY_INFORMED`.

**Honest limits:** 1/3 is the result for *this simple attack*. Cleverer attacks (optimal state discrimination) can do somewhat better. Real QDS security needs formal proofs; our simulation demonstrates the *mechanism*, not a proof.

### Case C — Replay attack
1. A genuine signature is verified and ACCEPTed; its one-time key ID is recorded as used.
2. Mallory re-sends the captured signature.
3. The **classical replay guard** sees a used key ID (or a stale timestamp) and rejects it before any quantum measurement.
4. **REJECT**, `REPLAY_ATTACK`, score 100.

**Honest limit:** the quantum part does not detect replay. Replay protection is classical (nonce, timestamp, one-time keys) and we label it that way. In real QDS, key elements are consumed, which supports the same idea.

### Case D — Impersonation
1. Mallory signs with her own random key but claims to be Alice.
2. Quantum check: her revealed bases and values do not match Alice's states, so about 50% mismatch. **REJECT**.
3. Classification: the *submitter identity* (from an authenticated classical channel) differs from the *claimed signer*, so the type is `IMPERSONATION`.

**Honest limit:** statistically, an impersonator and a blind forger look the same. What separates them is identity metadata from an authenticated classical channel, which QDS protocols assume and which we simulate by a field, not implement.

### Case E — Quantum-channel manipulation
1. Eve intercepts a fraction f of qubits in transit (measure and resend).
2. **Bell test:** the channel error rate rises to about f/3 above the 1% baseline. It is flagged when it exceeds 6%.
3. **Verification:** even a *genuine* signature now shows extra mismatches (about f/3).
4. The classifier sees "verification failed + channel flagged" and reports `CHANNEL_MANIPULATION`.

Measured detection (200 trials per row, simulated):

| Eve intercepts | Genuine signature ACCEPTed | INCONCLUSIVE | REJECTed | Channel flagged |
|---|---|---|---|---|
| 0% | 100% | 0% | 0% | 0% |
| 10% | 95% | 5% | 0% | 6% |
| 20% | 18% | 74% | 7% | 81% |
| 30% | 0% | 26% | 74% | 100% |
| 40%+ | 0% | 0% | 100% | 100% |

**Honest limit:** an attacker touching under about 10% of qubits stays inside the noise and is *not reliably detected*. This is the sensitivity limit of our parameters; larger blocks or more test pairs improve it.

### What our simulation cannot truly do (say this out loud)
- It cannot provide physical security: qubits, detectors and attackers are software models.
- Teleportation of the bulk key is modelled as ideal teleportation plus Pauli noise; the exact circuit is demonstrated separately.
- Authenticated classical channels are assumed, not built.
- The 8-bit digest is a teaching simplification; real systems need long digests and proofs.

---

# PART 4 — The minimum mathematics

**States.** A qubit: `|ψ⟩ = α|0⟩ + β|1⟩`, with `|α|² + |β|² = 1`.
`|0⟩ = (1,0)`, `|1⟩ = (0,1)`, `|±⟩ = (|0⟩ ± |1⟩)/√2`, `|±i⟩ = (|0⟩ ± i|1⟩)/√2`.

**Pauli matrices.**
```
X = [[0,1],[1,0]]     Y = [[0,-i],[i,0]]     Z = [[1,0],[0,-1]]
```
Eigenvalue +1 (value 0) and −1 (value 1): Z: `|0⟩,|1⟩` · X: `|+⟩,|−⟩` · Y: `|+i⟩,|−i⟩`.
Check: `Y|+i⟩ = |+i⟩`. The code has a function that verifies all six.

**Measurement probability (Born rule).** Measuring `|ψ⟩` in the basis with eigenstates `|e0⟩,|e1⟩`:
`P(outcome k) = |⟨e_k|ψ⟩|²`, and the state collapses to `|e_k⟩`.
Same basis as preparation: outcome certain (0% error). Different basis: `|⟨e|ψ⟩|² = 1/2` (50% error).

**Bell states.** `|Φ+⟩ = (|00⟩ + |11⟩)/√2` (H then CNOT). Measuring both qubits in the same Z or X basis always agrees. With an interceptor who touches a fraction f and guesses among three bases:
`QBER ≈ baseline + f · (2/3) · (1/2) = baseline + f/3`.
Baseline from noise: a random Pauli flips a Z or X outcome with probability 2/3, so `baseline = (2/3)·p = 1%` for p = 1.5%.

**Teleportation.** Send `|ψ⟩ = α|0⟩ + β|1⟩` using a Bell pair. After Alice's basis change, the three-qubit state is
`½ Σ |m0 m1⟩ ⊗ X^{m1} Z^{m0} |ψ⟩`. Alice measures (m0, m1) and sends the two bits; Bob applies `X^{m1}` then `Z^{m0}`, and holds `|ψ⟩` exactly (fidelity 1).

**Mismatch (forgery) probabilities per key element.**
- Honest: `ε ≈ 0.02` (detector + channel noise).
- Blind guess: right basis (1/3) matches only if the value is also right (1/2) so mismatch 1/2; wrong basis (2/3) is a coin flip, mismatch 1/2. Overall **1/2**.
- Measure-and-guess: correct basis (1/3) gives 0; wrong basis (2/3) gives 1/2, so `q = 1/3`.
- Interceptor fraction f on the channel: extra mismatch `f/3` on genuine signatures.

**Block statistics.** In a block of L = 128 elements the number of mismatches is Binomial(L, rate).
- Honest: mean `Lε = 2.6`, standard deviation about 1.6.
- Measure-and-guess: mean `Lq ≈ 42.7`, standard deviation about 5.3.
These distributions barely overlap, which is why counting works.

**Thresholds (derived, not guessed).** With target error α = 10⁻⁶:
- `s_a` = smallest k with `P(Bin(L, ε) > k) ≤ α`  →  **13**
- `s_v` = the k just below where `P(Bin(L, q) ≤ k)` reaches α  →  **18**

**Decision rule.**
```
if any block has mismatches > s_v :  REJECT
elif every block has mismatches <= s_a : ACCEPT
else : INCONCLUSIVE
```
Probability a genuine signature is wrongly REJECTed: at most `α` per block, so at most `8α ≈ 8·10⁻⁶` per signature.

**Forgery probability (reported on the dashboard).** For the worst block with m mismatches, with equal priors:
`P(forger | m) = L_f / (L_h + L_f)`, where `L_h = Bin(m; L, ε)` and `L_f = Bin(m; L, q)`.
It is a *model-based* posterior, not a proof.

**p-value.** `p = P(Bin(L, ε) ≥ m)`: the chance an honest block would look this bad. Tiny p means suspicious.

---
# PART 5 — Build it, stage by stage

Work inside one folder called `quantum-threat-detection/`. Create the folders from Part 6 first. Every code block below is a
file in the tested project. **Rule:** finish a stage, run its test, then move on.

> "Line-by-line" note: each stage lists the **key lines** and what they do, so you understand every idea without reading noise.

---

## Stage 1 — Environment setup
**Objective:** a working Python environment with Qiskit, running locally. No IBM account, no paid service, no quantum hardware.

**Files:** `requirements.txt`, `config.py`

**Commands**
```bash
python --version                       # use Python 3.10 or newer
mkdir quantum-threat-detection && cd quantum-threat-detection
python -m venv .venv
source .venv/bin/activate              # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
**Code — `requirements.txt`**
```text
qiskit>=2.0
qiskit-aer>=0.17
numpy>=1.26
scipy>=1.11
fastapi>=0.110
uvicorn>=0.29
streamlit>=1.35
plotly>=5.20
pandas>=2.0
requests>=2.31
pytest>=8.0
httpx>=0.27
```

**Code — `config.py`** (every tunable number lives here)
```python
# config.py
"""Central settings. Change here, everything else follows."""
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
```

**Explanation**
- `DIGEST_BITS = 8` and `BLOCK_SIZE = 128`: the signature covers 8 digest bits; each bit position has 128 quantum elements. Total 2048 qubits per key.
- `EXPECTED_ERROR`: the honest error we design thresholds around. `ALPHA`: how rare a wrong decision must be.
- `N_TEST_PAIRS`: Bell pairs sacrificed to test the channel.

**Expected output**
```bash
python -c "import qiskit, qiskit_aer, numpy, scipy; print(qiskit.__version__, qiskit_aer.__version__)"
# prints two version numbers, e.g.  2.x.x  0.17.x
```
**How to test:** the command above must print versions with no error. Qiskit changes between releases; if a later stage breaks, run `pip freeze > requirements-lock.txt` on a working machine and share that file with your team.

**Common errors**
- `No module named qiskit`: the virtual environment is not activated.
- PowerShell refuses to activate: run `Set-ExecutionPolicy -Scope Process RemoteSigned`.
- Slow or failing install: upgrade pip (`python -m pip install -U pip`); use Python 3.10–3.12.
- Do **not** install `qiskit-ibm-runtime` yet; you don't need IBM Quantum.

---

## Stage 2 — Basic qubit simulation
**Objective:** see a qubit, measure it, and watch probabilities appear.

**Files:** `quantum/measure.py` (created fully in Stage 3 together with the Paulis). First a playground in Qiskit:
```python
from qiskit.quantum_info import Statevector
psi = Statevector.from_label("+")      # the state |+>
print(psi.probabilities())             # [0.5 0.5]
print(psi.sample_counts(1000))         # roughly 500 zeros, 500 ones
print(Statevector.from_label("r").data)  # |+i> = [0.707+0j, 0+0.707j]
```
**Expected output:** `[0.5 0.5]`, counts near 500/500, and the `|+i⟩` vector.

**Explanation**
- `from_label("+")` builds a named state. `probabilities()` applies the Born rule. `sample_counts(1000)` measures 1000 identical copies.
- Real experiments measure *copies*, because measuring destroys the original.

**How to test:** run it three times. The counts change slightly each time (randomness); the probabilities never change.

**Common errors:** `ImportError: cannot import Statevector`: an old Qiskit; upgrade with `pip install -U qiskit`.

---

## Stage 3 — Pauli operations
**Objective:** build X, Y, Z, their six eigenstates, and fast measurement.

**Files:** `quantum/paulis.py`, `quantum/measure.py`

**Code — `quantum/paulis.py`**
```python
# quantum/paulis.py
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
```

**Code — `quantum/measure.py`**
```python
# quantum/measure.py
"""Stage 2/3 - state preparation, projective measurement, noise (vectorised)."""
import numpy as np
from .paulis import EIGEN, PAULI_STACK


def prepare(bases, values):
    """Return an (N,2) array of Pauli-eigenstates."""
    return EIGEN[np.asarray(bases), np.asarray(values)].copy()


def measure(states, bases, rng, readout_error=0.0):
    """Projective measurement of each state in its own Pauli basis.
    Returns array of 0/1 outcomes (0 <-> eigenvalue +1)."""
    e_plus = EIGEN[np.asarray(bases), 0]
    p0 = np.abs(np.einsum("ni,ni->n", e_plus.conj(), states)) ** 2   # Born rule
    outcome = (rng.random(len(states)) > p0).astype(int)
    if readout_error > 0:
        outcome ^= (rng.random(len(states)) < readout_error).astype(int)
    return outcome


def collapse(states, bases, rng):
    """Measure, then return the post-measurement states (the state 'remembers' the outcome)."""
    out = measure(states, bases, rng)
    return out, EIGEN[np.asarray(bases), out].copy()


def pauli_noise(states, p, rng):
    """Depolarising-style channel: with probability p apply a random X, Y or Z."""
    states = states.copy()
    hit = rng.random(len(states)) < p
    n = int(hit.sum())
    if n:
        which = rng.integers(0, 3, size=n)
        states[hit] = np.einsum("nij,nj->ni", PAULI_STACK[which], states[hit])
    return states


def eve_intercept_resend(states, fraction, rng):
    """Attacker measures a fraction of qubits in a random Pauli basis and resends the result."""
    states = states.copy()
    hit = rng.random(len(states)) < fraction
    n = int(hit.sum())
    if n:
        guess_basis = rng.integers(0, 3, size=n)
        _, new = collapse(states[hit], guess_basis, rng)
        states[hit] = new
    return states, hit
```

**Key lines explained**
- `EIGEN[basis, value]`: a lookup table of the six states. Basis 0/1/2 = Z/X/Y; value 0 = eigenvalue +1, value 1 = −1.
- `check_eigenstates()`: multiplies each Pauli by its eigenstate and confirms you get ±1 times the same state.
- `measure(...)`: `p0 = |⟨e+|ψ⟩|²` is the Born rule; a random number decides the outcome; `readout_error` flips it sometimes (detector noise).
- `collapse(...)`: measures and returns the *post-measurement* state. This is the "measurement disturbs" rule.
- `pauli_noise(...)`: a noisy channel: with probability p a random X, Y or Z hits the qubit.
- `eve_intercept_resend(...)`: the attacker's simplest strategy.

**Expected output**
```python
import numpy as np
from quantum.paulis import check_eigenstates
from quantum.measure import prepare, measure
print(check_eigenstates())                       # True
rng = np.random.default_rng(1)
b = rng.integers(0,3,100000); v = rng.integers(0,2,100000)
s = prepare(b, v)
print((measure(s, b, rng) != v).mean())          # 0.0   (same basis: no errors)
print((measure(s, (b+1)%3, rng) != v).mean())    # about 0.50 (wrong basis: coin flip)
```
**How to test:** the three printed values above. This is the physical heart of the whole project: right basis gives certainty, wrong basis gives 50% errors.

**Common errors:** dtype errors mean the arrays were not `complex`; forgetting `.conj()` gives wrong probabilities for the Y states.

---

## Stage 4 — Bell-state generation
**Objective:** create entangled pairs and use them to test a channel.

**Files:** `quantum/bell.py`

**Code**
```python
# quantum/bell.py
"""Stage 4 - Bell states with Qiskit, plus the fast correlation rule used for bulk channel tests."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from .paulis import EIGEN
from .measure import collapse, eve_intercept_resend, pauli_noise


def bell_circuit(kind: str = "phi+") -> QuantumCircuit:
    """Build one of the four Bell states on 2 qubits."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)                 # now |phi+> = (|00> + |11>)/sqrt2
    if kind in ("phi-", "psi-"):
        qc.z(0)
    if kind in ("psi+", "psi-"):
        qc.x(1)
    return qc


def bell_statevector(kind: str = "phi+") -> Statevector:
    return Statevector(bell_circuit(kind))


def bell_channel_test(n_pairs, rng, eve_fraction=0.0, channel_noise=0.0):
    """Simulate n Bell pairs (|phi+>). Alice and Bob measure in the same random basis (Z or X).
    Rule used (checked against Qiskit in tests): when Alice measures her half of |phi+> in basis P and
    gets outcome a, Bob's half collapses to the P-eigenstate with the same outcome a.
    Returns the quantum bit error rate (QBER) = fraction of pairs where outcomes disagree."""
    basis = rng.integers(0, 2, size=n_pairs)               # 0 = Z, 1 = X
    a, bob_state = collapse(EIGEN[basis, 0].copy(), basis, rng)   # Alice's outcome; Bob's collapsed half
    bob_state = EIGEN[basis, a].copy()
    bob_state = pauli_noise(bob_state, channel_noise, rng)
    if eve_fraction > 0:
        bob_state, _ = eve_intercept_resend(bob_state, eve_fraction, rng)
    b, _ = collapse(bob_state, basis, rng)
    errors = int((a != b).sum())
    return {"pairs": int(n_pairs), "errors": errors, "qber": errors / n_pairs}
```

**Key lines explained**
- `qc.h(0); qc.cx(0,1)`: Hadamard puts qubit 0 in superposition; CNOT copies that "choice" onto qubit 1 as entanglement.
- Other Bell states come from an extra Z and/or X.
- `bell_channel_test`: Alice and Bob measure in the same random basis; **QBER** = fraction of pairs that disagree.
- `eve_fraction`: Eve intercepts that fraction of Bob's qubits.

**Expected output**
```python
from quantum.bell import *
import numpy as np
print(bell_statevector("phi+").probabilities_dict())   # 00: 0.5 and 11: 0.5
rng = np.random.default_rng(3)
print(bell_channel_test(20000, rng))                          # qber 0.0
print(bell_channel_test(20000, rng, eve_fraction=1.0))        # qber about 0.33
print(bell_channel_test(20000, rng, eve_fraction=0.3))        # qber about 0.10
```
**How to test:** also run the circuit on Aer and look for only `00` and `11` (never `01` or `10`):
```python
from qiskit import transpile
from qiskit_aer import AerSimulator
qc = bell_circuit(); qc.measure_all()
sim = AerSimulator()
print(sim.run(transpile(qc, sim), shots=2000).result().get_counts())   # {'00': ~1000, '11': ~1000}
```
**Common errors:** Qiskit prints bits in **reverse order** (qubit 0 on the right); forgetting `measure_all()` gives empty counts.

---

## Stage 5 — Quantum teleportation
**Objective:** teleport a state with Pauli corrections and prove it worked.

**Files:** `quantum/teleport.py`

**Code**
```python
# quantum/teleport.py
"""Stage 5 - quantum teleportation with Pauli corrections (Qiskit)."""
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector, partial_trace, state_fidelity


def teleport_deferred(prep_gates):
    """3 qubits: q0 = state to send, q1 (Alice) & q2 (Bob) share a Bell pair.
    Corrections are written as controlled gates (equivalent to 'measure, send 2 bits, correct')."""
    qc = QuantumCircuit(3)
    prep_gates(qc)
    qc.h(1); qc.cx(1, 2)            # Bell pair
    qc.cx(0, 1); qc.h(0)            # Alice's Bell-basis measurement (basis change)
    qc.cx(1, 2)                     # Pauli-X correction if Alice's q1 = 1
    qc.cz(0, 2)                     # Pauli-Z correction if Alice's q0 = 1
    return qc


def teleport_fidelity(prep_gates) -> float:
    """Fidelity between the input state and what Bob holds after teleportation (ideal = 1.0)."""
    ref = QuantumCircuit(1); prep_gates(ref)
    target = Statevector(ref)
    bob = partial_trace(Statevector(teleport_deferred(prep_gates)), [0, 1])
    return float(state_fidelity(bob, target))


def teleport_with_measurements(prep_gates):
    """Textbook version with real mid-circuit measurements + classical feed-forward (runs on Aer)."""
    q = QuantumRegister(3, "q")
    c0, c1, out = ClassicalRegister(1, "c0"), ClassicalRegister(1, "c1"), ClassicalRegister(1, "out")
    qc = QuantumCircuit(q, c0, c1, out)
    prep_gates(qc)
    qc.h(1); qc.cx(1, 2)
    qc.cx(0, 1); qc.h(0)
    qc.measure(0, c0); qc.measure(1, c1)
    with qc.if_test((c1, 1)):
        qc.x(2)
    with qc.if_test((c0, 1)):
        qc.z(2)
    # undo the preparation on Bob's qubit so a perfect teleport always reads 0
    inv = QuantumCircuit(1); prep_gates(inv)
    qc.compose(inv.inverse(), qubits=[2], inplace=True)
    qc.measure(2, out)
    return qc
```

**Key lines explained**
- Qubit 0 holds the state to send; qubits 1 and 2 are the Bell pair (1 = Alice's half, 2 = Bob's half).
- `cx(0,1); h(0)`: Alice's Bell-measurement basis change.
- `cx(1,2)` and `cz(0,2)`: the **Pauli corrections** (X and Z on Bob's qubit). In the first version they are controlled gates, which is mathematically the same as "measure, send two bits, correct".
- The second version uses real measurements and `if_test` (classical feed-forward) on Aer. It applies the *inverse* of the preparation to Bob's qubit so a perfect teleport always reads `0`.

**Expected output**
```python
from quantum.teleport import *
prep = lambda qc: (qc.ry(1.1, 0), qc.rz(0.7, 0))
print(teleport_fidelity(prep))            # 1.0 (up to rounding)

from qiskit import transpile
from qiskit_aer import AerSimulator
sim = AerSimulator()
counts = sim.run(transpile(teleport_with_measurements(prep), sim), shots=2000).result().get_counts()
print(counts)   # every key starts with '0' (the 'out' bit is always 0)
```
**How to test:** fidelity must be ≈ 1. In `counts`, the leftmost bit is Bob's check bit, and it must be `0` in **every** entry.

**Common errors:**
- Old tutorials use `c_if`, which was removed in Qiskit 2.x; use `if_test` as shown.
- If fidelity is below 1, a correction gate is on the wrong qubit.

---

## Stage 6 — Signature simulation
**Objective:** generate one-time keys, distribute quantum public keys, and sign.

**Files:** `qds/protocol.py`

**Code** (Stages 6 and 7 share this file)
```python
# qds/protocol.py
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
```

**Key lines explained**
- `generate_key`: for each digest position `j` and bit value `v` (0 or 1), 128 secret (basis, value) pairs.
- `public_states`: turns those secrets into six-state qubits (the quantum public key).
- `distribute`: applies transport noise (modelling teleportation with an imperfect Bell pair), optionally an intercepting Eve, and runs the Bell-pair channel test.
- `digest_bits`: SHA-256 of signer, key ID, nonce, timestamp and message; the first 8 bits choose which private-key blocks are revealed.
- `sign`: the signature is the classical description of the selected blocks. Because it reveals those blocks, **each key is used once**.

**Expected output**
```python
import numpy as np
from qds import protocol as P
rng = np.random.default_rng(1)
key = P.generate_key("alice", rng)
sig = P.sign(key, "Pay 500 INR", "n1", 1000.0)
print(sig["digest"])                       # e.g. [1, 1, 1, 0, 0, 1, 0, 0]
stored, report = P.distribute(P.public_states(key), rng)
print(report)                              # qber near 0.01, qber_threshold 0.06, healthy True
```
**How to test:** the digest has 8 bits; `healthy` is `True` when no attacker is present.

**Common errors:** `KeyError` on `revealed` means you edited a signature dict; shape mismatches mean `BLOCK_SIZE` changed in one place only.

---

## Stage 7 — Verification
**Objective:** verify a signature by measuring the stored quantum states, inside a pipeline with security gates.

**Files:** `qds/protocol.py` (`verify_quantum`, above) and `qds/service.py`

**Code — `qds/service.py`**
```python
# qds/service.py
"""Stage 7/10/11 glue: the whole pipeline in one class (used by the API and by tests)."""
import time, uuid
import numpy as np
import config as C
from qds import protocol as P
from attacks import simulate as A
from detection import audit
from detection.replay import ReplayGuard
from detection.statistics import analyse
from detection.thresholds import compute_thresholds, decide
from detection.classifier import classify

ATTACKS = ["legitimate", "blind_forgery", "informed_forgery", "replay", "impersonation",
           "unauthorized_verifier", "channel_manipulation"]


class QDSSystem:
    def __init__(self, seed=None, db_path=None):
        self.rng = np.random.default_rng(seed)
        self.con = audit.connect(db_path)
        self.th = compute_thresholds()
        self.guard = ReplayGuard()
        self.registered_verifiers = {"bob"}
        self.stores = {}          # (verifier_id, key_id) -> {"states":..., "channel":...}
        self.copies = {}          # key_id -> number of copies handed out

    # ---------- setup ----------
    def new_key(self, signer_id="alice", verifier_id="bob", eve_fraction=0.0, channel_noise=C.CHANNEL_NOISE):
        key = P.generate_key(signer_id, self.rng)
        states = P.public_states(key)
        self.copies[key["key_id"]] = 0
        stored, report = self._give_copy(key["key_id"], verifier_id, states, eve_fraction, channel_noise)
        return key, states, report

    def _give_copy(self, key_id, verifier_id, states, eve_fraction=0.0, channel_noise=C.CHANNEL_NOISE):
        if verifier_id not in self.registered_verifiers or self.copies[key_id] >= C.MAX_COPIES:
            return None, None
        stored, report = P.distribute(states, self.rng, channel_noise, eve_fraction)
        self.stores[(verifier_id, key_id)] = {"states": stored, "channel": report}
        self.copies[key_id] += 1
        return stored, report

    # ---------- verification pipeline ----------
    def verify(self, signature, verifier_id="bob", submitter_id=None, now=None):
        now = time.time() if now is None else now
        submitter_id = submitter_id or signature["signer_id"]
        ctx = {"unauthorized": False, "replay": False, "impersonation": False, "channel_flag": False}
        stats, verdict = None, "REJECT"
        store = self.stores.get((verifier_id, signature["key_id"]))

        if verifier_id not in self.registered_verifiers or store is None:
            ctx["unauthorized"] = True
        else:
            ok, why = self.guard.check(signature["key_id"], signature["timestamp"], now)
            if not ok:
                ctx["replay"], ctx["replay_reason"] = True, why
            else:
                mism = P.verify_quantum(store["states"], signature, self.rng)
                stats = analyse(mism)
                verdict = decide(mism, self.th)
                ctx["channel_flag"] = not store["channel"]["healthy"]
                ctx["impersonation"] = submitter_id != signature["signer_id"]
                if verdict != "REJECT":
                    self.guard.consume(signature["key_id"])
        ctx["verdict"] = verdict
        ctx["observed_rate"] = stats["observed_rate"] if stats else 0.0
        attack, reason = classify(ctx)
        if ctx["unauthorized"] or ctx["replay"]:
            verdict, score, fprob = "REJECT", 100, 1.0
        else:
            fprob = stats["forgery_probability"]
            score = int(round(100 * fprob))
            if ctx["channel_flag"] and verdict != "ACCEPT":
                score = max(score, 90)
        result = {
            "signature_id": signature["key_id"] + "-" + str(signature["nonce"])[:6],
            "signer": signature["signer_id"], "verifier": verifier_id, "submitter": submitter_id,
            "verdict": verdict, "attack_type": attack, "reason": reason, "threat_score": score,
            "forgery_probability": fprob, "stats": stats, "thresholds": self.th.as_dict(),
            "channel": store["channel"] if store else None, "timestamp": now,
        }
        audit.append(self.con, {"ts": now, "signature_id": result["signature_id"], "signer": result["signer"],
                                "verifier": verifier_id, "verdict": verdict, "attack_type": attack,
                                "observed_rate": ctx["observed_rate"], "forgery_prob": fprob,
                                "threat_score": score, "payload": {"stats": stats, "channel": result["channel"],
                                                                   "reason": reason}})
        return result

    # ---------- attack lab ----------
    def run_scenario(self, attack: str, strength: float = 0.5, message: str = "Transfer 500 INR to Bob"):
        now = time.time()
        nonce = uuid.uuid4().hex[:10]
        eve = strength if attack == "channel_manipulation" else 0.0
        key, states, _ = self.new_key(eve_fraction=eve)
        kid = key["key_id"]
        if attack in ("legitimate", "channel_manipulation"):
            sig = P.sign(key, message, nonce, now)
            return self.verify(sig, "bob", "alice", now)
        if attack == "replay":
            sig = P.sign(key, message, nonce, now)
            self.verify(sig, "bob", "alice", now)             # first, legitimate use
            return self.verify(sig, "bob", "mallory", now + 5)  # attacker re-sends captured packet
        if attack == "blind_forgery":
            sig = A.blind_forgery("alice", kid, "Transfer 50000 INR to Mallory", nonce, now, self.rng)
            return self.verify(sig, "bob", "alice", now)
        if attack == "informed_forgery":
            copy, _ = P.distribute(states, self.rng)          # attacker's own legitimate copy
            sig = A.informed_forgery(copy, "alice", kid, "Transfer 50000 INR to Mallory", nonce, now, self.rng)
            return self.verify(sig, "bob", "alice", now)
        if attack == "impersonation":
            sig = A.impersonation("alice", kid, "Transfer 50000 INR to Mallory", nonce, now, self.rng)
            return self.verify(sig, "bob", "mallory", now)
        if attack == "unauthorized_verifier":
            sig = P.sign(key, message, nonce, now)
            return self.verify(sig, "eve-node", "eve-node", now)
        raise ValueError(f"unknown attack {attack}")

    # ---------- detection-vs-strength curve (Monte Carlo) ----------
    def detection_curve(self, fractions=None, trials=60):
        fractions = fractions if fractions is not None else [0, .1, .2, .3, .4, .5, .7, 1.0]
        out = []
        for f in fractions:
            v = {"ACCEPT": 0, "INCONCLUSIVE": 0, "REJECT": 0}
            chan = 0
            for _ in range(trials):
                key, states, rep = self.new_key(eve_fraction=f)
                sig = P.sign(key, "m", uuid.uuid4().hex[:8], time.time())
                store = self.stores[("bob", key["key_id"])]
                m = P.verify_quantum(store["states"], sig, self.rng)
                v[decide(m, self.th)] += 1
                chan += (not rep["healthy"])
            out.append({"eve_fraction": f, "accept": v["ACCEPT"] / trials, "inconclusive": v["INCONCLUSIVE"] / trials,
                        "reject": v["REJECT"] / trials, "channel_flagged": chan / trials})
        return out
```

**Key lines explained**
- `verify_quantum` **recomputes the digest** from the message the verifier actually received. It never trusts a digest sent by the sender.
- `verify()` runs gates in order: registry check, replay/freshness check, quantum measurement, statistics, decision, classification, audit log.
- The key is consumed (`guard.consume`) only when the result is not REJECT.
- `run_scenario` builds every attack scenario end-to-end (Stage 8 uses it).
- `detection_curve` runs Monte-Carlo trials for the dashboard chart.

**Expected output**
```python
from qds.service import QDSSystem
s = QDSSystem(seed=7, db_path=":memory:")
r = s.run_scenario("legitimate")
print(r["verdict"], r["attack_type"], r["stats"]["block_mismatches"])   # ACCEPT NONE [ ... small numbers ... ]
```
**How to test:** run it 25 times; every verdict must be ACCEPT.

**Common errors:** using the same signature twice gives `REPLAY_ATTACK` (that is correct behaviour, not a bug).

---

## Stage 8 — Attack simulation
**Objective:** simulate forgery and impersonation; replay, unauthorized verification and channel manipulation are built into `run_scenario`.

**Files:** `attacks/simulate.py`

**Code**
```python
# attacks/simulate.py
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
```

**Key lines explained**
- `blind_forgery`: random guesses, expected mismatch 1/2.
- `informed_forgery`: measures a legitimately held copy in random bases, expected mismatch 1/3.
- `impersonation`: signs with her *own* key while claiming Alice's identity and key ID.

**Expected output**
```python
from qds.service import QDSSystem, ATTACKS
s = QDSSystem(seed=7, db_path=":memory:")
for a in ATTACKS:
    r = s.run_scenario(a)
    print(a, r["verdict"], r["attack_type"], r["threat_score"])
```
```
legitimate            ACCEPT  NONE                      0
blind_forgery         REJECT  FORGERY_BLIND             100
informed_forgery      REJECT  FORGERY_INFORMED          100
replay                REJECT  REPLAY_ATTACK             100
impersonation         REJECT  IMPERSONATION             100
unauthorized_verifier REJECT  UNAUTHORIZED_VERIFICATION 100
channel_manipulation  REJECT  CHANNEL_MANIPULATION      100
```
**How to test:** all seven lines must match. Also print `r["stats"]["observed_rate"]`: ≈0.02 legitimate, ≈0.35 informed forgery, ≈0.5 blind forgery.

**Common errors:** if the forgery types come out swapped, the rate cutoff in the classifier (0.42) or the block size was changed.

---

## Stage 9 — Statistical threat detection
**Objective:** turn raw mismatch counts into evidence.

**Files:** `detection/statistics.py`

**Code**
```python
# detection/statistics.py
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
```

**Key lines explained**
- `binom.sf(worst - 1, L, eps)`: probability an *honest* block shows at least this many mismatches (the p-value).
- `ll_h`, `ll_f`: log-likelihood of the observation under "honest" and under "forger".
- The forgery probability is the normalised likelihood: a model-based posterior with equal priors.
- The result also carries expected vs observed values for the dashboard.

**Expected output:** for a legitimate signature `forgery_probability` ≈ 0 and `p_value_honest` is large; for a forgery `p_value_honest` is astronomically small and `forgery_probability` is ≈ 1.

**How to test**
```python
from detection.statistics import analyse
print(analyse([2,3,1,0,2,4,3,1])["forgery_probability"])     # ~0
print(analyse([40,45,38,44,41,46,39,43])["forgery_probability"])   # ~1
```
**Common errors:** `p_value_honest = 1.0` when the worst block is 0 is intentional (nothing suspicious).

---

## Stage 10 — Threshold engine (plus classifier, replay guard, audit log)
**Objective:** derive thresholds mathematically, decide, name the attack, block replays, and keep a tamper-evident log.

**Files:** `detection/thresholds.py`, `detection/classifier.py`, `detection/replay.py`, `detection/audit.py`

**Code — `detection/thresholds.py`**
```python
# detection/thresholds.py
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
```

**Code — `detection/classifier.py`**
```python
# detection/classifier.py
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
```

**Code — `detection/replay.py`**
```python
# detection/replay.py
"""Classical layer: replay protection (one-time key ids + freshness window). Quantum physics alone does NOT stop replay."""
import config as C


class ReplayGuard:
    def __init__(self):
        self.used_keys = set()

    def check(self, key_id: str, timestamp: float, now: float):
        if key_id in self.used_keys:
            return False, "key already used (one-time key replayed)"
        if abs(now - timestamp) > C.FRESHNESS_SECONDS:
            return False, "timestamp outside freshness window (stale signature)"
        return True, "fresh"

    def consume(self, key_id: str):
        self.used_keys.add(key_id)
```

**Code — `detection/audit.py`**
```python
# detection/audit.py
"""Tamper-evident audit log: each event stores the hash of the previous one (a tiny blockchain-style chain)."""
import hashlib, json, sqlite3, os, time
import config as C

SCHEMA = """CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, signature_id TEXT, signer TEXT, verifier TEXT,
  verdict TEXT, attack_type TEXT, observed_rate REAL, forgery_prob REAL, threat_score INTEGER,
  payload TEXT, prev_hash TEXT, hash TEXT)"""


def connect(path=None):
    path = path or C.DB_PATH
    if path != ":memory:":
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute(SCHEMA)
    return con


def _digest(prev_hash, record):
    return hashlib.sha256((prev_hash + json.dumps(record, sort_keys=True)).encode()).hexdigest()


def append(con, e: dict):
    row = con.execute("SELECT hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
    prev = row["hash"] if row else "GENESIS"
    record = {k: e[k] for k in ("ts", "signature_id", "signer", "verifier", "verdict", "attack_type",
                                 "observed_rate", "forgery_prob", "threat_score")}
    record["payload"] = json.dumps(e["payload"], sort_keys=True)
    h = _digest(prev, record)
    con.execute("INSERT INTO events (ts,signature_id,signer,verifier,verdict,attack_type,observed_rate,forgery_prob,"
                "threat_score,payload,prev_hash,hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (record["ts"], record["signature_id"], record["signer"], record["verifier"], record["verdict"],
                 record["attack_type"], record["observed_rate"], record["forgery_prob"], record["threat_score"],
                 record["payload"], prev, h))
    con.commit()
    return h


def verify_chain(con):
    prev = "GENESIS"
    for r in con.execute("SELECT * FROM events ORDER BY id"):
        record = {k: r[k] for k in ("ts", "signature_id", "signer", "verifier", "verdict", "attack_type",
                                     "observed_rate", "forgery_prob", "threat_score", "payload")}
        if r["prev_hash"] != prev or _digest(prev, record) != r["hash"]:
            return {"valid": False, "broken_at_event": r["id"]}
        prev = r["hash"]
    return {"valid": True, "broken_at_event": None}


def history(con, limit=100):
    return [dict(r) for r in con.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))]
```

**Key lines explained**
- `binom.isf(alpha, L, eps)`: the count that an honest block exceeds with probability at most `alpha` (gives 13).
- `binom.ppf(alpha, L, q) - 1`: the count a forger falls at or below with probability under `alpha` (gives 18).
- `ValueError`: if the two distributions overlap, the code refuses to run and tells you to enlarge the block.
- The classifier is a plain `if` chain: every decision is explainable.
- The audit hash chain links each event to the previous one. Editing any old event breaks every later hash.

**Expected output**
```python
from detection.thresholds import compute_thresholds, decide
th = compute_thresholds(); print(th)   # accept_max=13, reject_min=18
print(decide([2,3,1,0,2,4,3,1], th))       # ACCEPT
print(decide([2,3,1,0,15,4,3,1], th))      # INCONCLUSIVE
print(decide([2,3,1,0,60,4,3,1], th))      # REJECT
```
**How to test:** the three decisions above. Then change `BLOCK_SIZE` to 32 and watch the `ValueError` appear (thresholds cannot be separated).

**Common errors:** thresholds recomputed with a different `ALPHA` in different files; keep all parameters in `config.py`.

---

## Stage 11 — Backend API
**Objective:** expose everything through FastAPI so the dashboard (or any client) can use it.

**Files:** `backend/main.py`

**Code**
```python
# backend/main.py
"""Stage 11 - FastAPI backend.  Run:  uvicorn backend.main:app --reload"""
from fastapi import FastAPI, HTTPException
from qds.service import QDSSystem, ATTACKS
from detection import audit
from detection.thresholds import qber_threshold
from quantum.shor_toy import run as shor_run
import config as C

app = FastAPI(title="Quantum-Inspired QDS Threat Detection (academic prototype)")
system = QDSSystem()


@app.get("/health")
def health():
    return {"status": "ok"}


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
    return {**system.th.as_dict(), "qber_threshold": qber_threshold(), "test_pairs": C.N_TEST_PAIRS}


@app.get("/audit/verify")
def audit_verify():
    return audit.verify_chain(system.con)


@app.get("/detection-curve")
def detection_curve(trials: int = 40):
    return system.detection_curve(trials=min(trials, 200))


@app.get("/shor-toy")
def shor_toy():
    counts, factors = shor_run()
    return {"N": 15, "a": 7, "counts": counts, "factors_found": factors,
            "note": "Toy demo on the simulator. Shows why RSA is at risk; it does not attack real RSA."}


@app.get("/reality-check")
def reality_check():
    return {
        "real": ["Mathematics of qubits, Pauli measurements, Bell states and teleportation",
                 "Binomial hypothesis testing and threshold design",
                 "No-cloning / measurement-disturbance as the reason for the detection rates"],
        "simulated": ["All qubits, channels, detectors and attackers are software models on a classical computer",
                      "Teleportation in bulk is modelled as ideal teleportation plus Pauli noise",
                      "Classical authenticated channel and identities are assumed, not implemented"],
        "not_claimed": ["Physical quantum security", "A production-ready QDS", "That simulated attacks prove real-world security"],
    }
```

**Endpoints**

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/attacks` | List scenarios |
| POST | `/simulate/{attack}?strength=0.5` | Run a scenario end to end |
| GET | `/history` | Verification history |
| GET | `/thresholds` | Current thresholds |
| GET | `/audit/verify` | Check the audit chain |
| GET | `/detection-curve` | Monte-Carlo detection curve |
| GET | `/shor-toy` | Toy Shor demo (factor 15) |
| GET | `/reality-check` | Real vs simulated statement |

**Run and test**
```bash
uvicorn backend.main:app --reload
curl -X POST "http://127.0.0.1:8000/simulate/blind_forgery"
curl http://127.0.0.1:8000/audit/verify
# interactive docs: http://127.0.0.1:8000/docs
```
**Expected output:** JSON with `verdict`, `attack_type`, `threat_score`, `stats`, `thresholds`, `channel`. `/audit/verify` returns `{"valid": true, ...}`.

**Common errors**
- `ModuleNotFoundError: qds` means you ran uvicorn from the wrong folder; run it from the project root.
- Port already in use: `--port 8001` (and set `QDS_API` for the dashboard).
- Events persist in `data/events.db`; delete it to reset the history.

---

## Stage 12 — Dashboard
**Objective:** a professional monitoring screen with attack simulation controls.

**Files:** `frontend/app.py`

**Code**
```python
# frontend/app.py
"""Stage 12 - Streamlit dashboard.  Run:  streamlit run frontend/app.py   (backend must be running)"""
import os, datetime, json
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API = os.getenv("QDS_API", "http://127.0.0.1:8000")
LABELS = {"legitimate": "Legitimate signature", "blind_forgery": "Forgery (blind guess)",
          "informed_forgery": "Forgery (measure-and-guess)", "replay": "Replay attack",
          "impersonation": "Impersonation", "unauthorized_verifier": "Unauthorized verification",
          "channel_manipulation": "Quantum-channel manipulation"}
COLORS = {"ACCEPT": "#1a9850", "INCONCLUSIVE": "#f39c12", "REJECT": "#d73027"}

st.set_page_config(page_title="QDS Threat Monitor", page_icon="🛡️", layout="wide")
st.title("🛡️ Quantum-Inspired QDS Threat Detection")
st.caption("Academic prototype: quantum-SIMULATED software. Not real quantum security. See the Reality Check tab.")


def call(method, path, **kw):
    try:
        r = requests.request(method, API + path, timeout=60, **kw)
        r.raise_for_status()
        return r.json()
    except Exception as e:                                 # show a friendly error instead of a crash
        st.error(f"Backend not reachable ({e}). Start it with: uvicorn backend.main:app --reload")
        st.stop()


tab_lab, tab_hist, tab_curve, tab_more, tab_real = st.tabs(
    ["Attack Lab", "History & Audit", "Detection curve", "Why quantum? (Shor toy)", "Reality Check"])

with tab_lab:
    c1, c2 = st.columns([1, 3])
    with c1:
        attack = st.selectbox("Scenario", list(LABELS), format_func=LABELS.get)
        strength = st.slider("Attacker strength (channel scenario)", 0.0, 1.0, 0.5, 0.05,
                             disabled=attack != "channel_manipulation")
        if st.button("Run scenario", type="primary"):
            st.session_state["last"] = call("POST", f"/simulate/{attack}", params={"strength": strength})
    res = st.session_state.get("last")
    with c2:
        if not res:
            st.info("Pick a scenario and press Run.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Verdict", res["verdict"])
            m2.metric("Attack type", res["attack_type"])
            m3.metric("Threat score", f"{res['threat_score']}/100")
            m4.metric("Forgery probability", f"{res['forgery_probability']:.4f}")
            st.write(f"**Signature ID:** `{res['signature_id']}`  |  **Signer:** {res['signer']}  |  "
                     f"**Submitted by:** {res['submitter']}  |  **Verifier:** {res['verifier']}  |  "
                     f"**Time:** {datetime.datetime.fromtimestamp(res['timestamp']):%Y-%m-%d %H:%M:%S}")
            st.write(f"**Why:** {res['reason']}")
            if res["stats"]:
                th, s = res["thresholds"], res["stats"]
                fig = go.Figure()
                fig.add_bar(x=list(range(1, len(s["block_mismatches"]) + 1)), y=s["block_mismatches"],
                            name="Observed mismatches", marker_color=COLORS[res["verdict"]])
                fig.add_hline(y=s["expected_per_block"], line_dash="dot", annotation_text="Expected (honest noise)")
                fig.add_hline(y=th["accept_max"], line_color="green", annotation_text="Accept threshold")
                fig.add_hline(y=th["reject_min"], line_color="red", annotation_text="Reject threshold")
                fig.update_layout(title="Expected vs observed mismatches per digest block",
                                  xaxis_title="Digest block", yaxis_title="Mismatches (of 128)", height=380)
                st.plotly_chart(fig, width="stretch")
                st.caption(f"Observed rate {s['observed_rate']:.3%} vs expected {s['expected_rate']:.1%} | "
                           f"p-value under 'honest' hypothesis: {s['p_value_honest']:.2e}")
            if res["channel"]:
                ch = res["channel"]
                st.write(f"**Channel health (Bell-pair test):** QBER {ch['qber']:.3%} vs limit "
                         f"{ch['qber_threshold']:.3%} → {'✅ healthy' if ch['healthy'] else '🚨 flagged'}")

with tab_hist:
    hist = call("GET", "/history")
    a = call("GET", "/audit/verify")
    st.success("Audit chain intact ✅") if a["valid"] else st.error(f"Audit chain BROKEN at event {a['broken_at_event']} 🚨")
    if hist:
        df = pd.DataFrame(hist)[["id", "ts", "signature_id", "signer", "verifier", "verdict", "attack_type",
                                 "observed_rate", "forgery_prob", "threat_score"]]
        df["ts"] = pd.to_datetime(df["ts"], unit="s")
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("Download history (JSON)", json.dumps(hist, indent=2), "qds_history.json")
    else:
        st.info("No events yet.")

with tab_curve:
    st.write("How often is an interceptor caught, as the interceptor gets stronger? (Monte Carlo, simulated)")
    trials = st.slider("Trials per point", 10, 100, 30)
    if st.button("Compute curve"):
        d = pd.DataFrame(call("GET", "/detection-curve", params={"trials": trials}))
        fig = go.Figure()
        for col, color in [("accept", "#1a9850"), ("inconclusive", "#f39c12"), ("reject", "#d73027"),
                           ("channel_flagged", "#4575b4")]:
            fig.add_scatter(x=d["eve_fraction"], y=d[col], name=col, line_color=color, mode="lines+markers")
        fig.update_layout(xaxis_title="Fraction of qubits intercepted", yaxis_title="Probability", height=420)
        st.plotly_chart(fig, width="stretch")

with tab_more:
    st.write("A toy Shor's algorithm factors 15 on the simulator. It shows *why* RSA is at risk; it is not an attack on real RSA.")
    if st.button("Run toy Shor"):
        r = call("GET", "/shor-toy")
        st.success(f"Factors of {r['N']} found: {r['factors_found']}")
        st.bar_chart(pd.Series(r["counts"]))

with tab_real:
    rc = call("GET", "/reality-check")
    for title, key in [("✅ Real (the science)", "real"), ("🧪 Simulated", "simulated"), ("🚫 Not claimed", "not_claimed")]:
        st.subheader(title)
        for line in rc[key]:
            st.write("- " + line)
```

**What it shows** (mapped to your list)

| Requirement | Where |
|---|---|
| Signature ID, signer, verifier, timestamp | Info line under the metrics |
| Verification status | "Verdict" metric (colour-coded bars) |
| Measurement results | Per-block mismatch bar chart |
| Expected vs observed | Bars vs the dotted expected line, plus observed/expected rates |
| Forgery probability, threat score, attack type | Metrics row |
| Threshold | Green (accept) and red (reject) lines on the chart |
| Verification history | "History & Audit" tab with audit-chain status |
| Attack simulation controls | Scenario dropdown, strength slider, Run button |
| Extras | Detection curve, toy Shor, Reality Check tab |

**Run and test**
```bash
streamlit run frontend/app.py          # backend must already be running
```
**Expected output:** open `http://localhost:8501`, pick "Forgery (blind guess)", press Run: REJECT, score 100, the bars far above the red line.

**Common errors:** "Backend not reachable": start uvicorn first, or set `QDS_API`. If you use an older Streamlit and see `width="stretch"` errors, replace it with `use_container_width=True`.

---

## Stage 13 — Testing
**Objective:** prove the system behaves, automatically.

**Files:** `tests/test_pipeline.py`, `tests/test_api.py`

**Code — `tests/test_pipeline.py`**
```python
# tests/test_pipeline.py
import numpy as np, pytest
from quantum.paulis import check_eigenstates
from quantum.measure import prepare, measure
from quantum.bell import bell_channel_test, bell_statevector
from quantum.teleport import teleport_fidelity
from qds.service import QDSSystem, ATTACKS
from detection import audit
from detection.thresholds import compute_thresholds


def test_eigenstates():
    assert check_eigenstates()


def test_measure_same_and_other_basis():
    rng = np.random.default_rng(0)
    b, v = rng.integers(0, 3, 20000), rng.integers(0, 2, 20000)
    s = prepare(b, v)
    assert (measure(s, b, rng) != v).mean() == 0
    assert abs((measure(s, (b + 1) % 3, rng) != v).mean() - 0.5) < 0.02


def test_bell_and_teleport():
    p = bell_statevector("phi+").probabilities_dict()
    assert abs(p["00"] - 0.5) < 1e-9 and abs(p["11"] - 0.5) < 1e-9
    assert teleport_fidelity(lambda qc: (qc.ry(1.1, 0), qc.rz(0.7, 0))) > 0.999999


def test_bell_rule_matches_eve_theory():
    rng = np.random.default_rng(1)
    assert bell_channel_test(20000, rng)["qber"] == 0
    assert abs(bell_channel_test(20000, rng, eve_fraction=1.0)["qber"] - 1 / 3) < 0.02


def test_thresholds_separate():
    th = compute_thresholds()
    assert th.accept_max < th.reject_min


@pytest.fixture
def system():
    return QDSSystem(seed=42, db_path=":memory:")


def test_legitimate_accepted_many_times(system):
    for _ in range(25):
        assert system.run_scenario("legitimate")["verdict"] == "ACCEPT"


@pytest.mark.parametrize("attack,expected", [
    ("blind_forgery", "FORGERY_BLIND"), ("informed_forgery", "FORGERY_INFORMED"), ("replay", "REPLAY_ATTACK"),
    ("impersonation", "IMPERSONATION"), ("unauthorized_verifier", "UNAUTHORIZED_VERIFICATION"),
    ("channel_manipulation", "CHANNEL_MANIPULATION")])
def test_attacks_detected(system, attack, expected):
    for _ in range(10):
        r = system.run_scenario(attack, 0.5)
        assert r["verdict"] == "REJECT" and r["attack_type"] == expected


def test_audit_chain_detects_tampering(system):
    system.run_scenario("legitimate"); system.run_scenario("blind_forgery")
    assert audit.verify_chain(system.con)["valid"]
    system.con.execute("UPDATE events SET verdict='ACCEPT' WHERE id=2"); system.con.commit()
    assert not audit.verify_chain(system.con)["valid"]
```

**Code — `tests/test_api.py`**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from backend.main import app

c = TestClient(app)


def test_api_flow():
    assert c.get("/health").json()["status"] == "ok"
    assert c.post("/simulate/legitimate").json()["verdict"] == "ACCEPT"
    assert c.post("/simulate/replay").json()["attack_type"] == "REPLAY_ATTACK"
    assert c.post("/simulate/nope").status_code == 404
    assert len(c.get("/history").json()) >= 2
    assert c.get("/audit/verify").json()["valid"]
    assert c.get("/thresholds").json()["accept_max"] < c.get("/thresholds").json()["reject_min"]
    assert c.get("/shor-toy").json()["factors_found"] == [3, 5]
```

**Run**
```bash
pytest -q
```
**Expected output:** `14 passed` (a deprecation warning about `httpx` is harmless).

**What is tested:** eigenstates, right/wrong-basis measurement, Bell states, teleportation fidelity, the interceptor's theoretical QBER, threshold separation, 25 legitimate signatures all ACCEPTed, six attack types each detected 10 times with the correct label, audit-chain tamper detection, and the API flow.

**Common errors:** a random test failing occasionally means a threshold is too tight; increase `BLOCK_SIZE` rather than loosening the assertion. Tests use a fixed seed so runs are repeatable.

---

## Stage 14 — Final demo
**Objective:** an 8-minute story that lands with judges.

**Setup (once):** delete `data/events.db`, start uvicorn and streamlit, open the dashboard.

**Demo script**
1. **The problem (1 min).** RSA and ECC and Shor. Show the "Why quantum?" tab: toy Shor factors 15.
2. **Legitimate signature (1 min).** Run it. Point at the bars below the green line and the ~2% observed rate.
3. **Blind and informed forgery (1.5 min).** Verdict REJECT; bars far above red; observed rate ≈ 50% vs ≈ 33%.
4. **Replay (1 min).** Run it: rejected before any quantum measurement; say clearly this is a classical defence.
5. **Impersonation and unauthorized verifier (1 min).**
6. **Channel manipulation (1 min).** Set strength 0.5, run; show the QBER flag. Then open the **Detection curve** tab and mention the sensitivity limit.
7. **Audit chain and Reality Check (30 sec).** Show "Audit chain intact"; read the Reality Check panel aloud.

**Backup plan:** keep a screen recording, and note that `python -m pytest -q` proves the behaviour offline.

---
# PART 6 — Project structure

```
quantum-threat-detection/
├── config.py                  # every tunable parameter
├── requirements.txt
├── README.md
├── quantum/                   # the physics layer
│   ├── paulis.py              # X, Y, Z and the six eigenstates
│   ├── measure.py             # prepare, measure, noise, intercept-resend
│   ├── bell.py                # Bell states + channel-health (QBER) test
│   ├── teleport.py            # teleportation with Pauli corrections
│   └── shor_toy.py            # optional toy Shor demo (factor 15)
├── qds/                       # the signature system
│   ├── protocol.py            # keys, distribution, sign, quantum verify
│   └── service.py             # full pipeline + attack scenarios
├── attacks/
│   └── simulate.py            # forgery and impersonation simulators
├── detection/                 # the "no ML" detection engine
│   ├── statistics.py          # expected vs observed, p-value, forgery probability
│   ├── thresholds.py          # derived two-threshold rule
│   ├── classifier.py          # explainable rules
│   ├── replay.py              # classical replay guard
│   └── audit.py               # hash-chained event log (SQLite)
├── backend/main.py            # FastAPI
├── frontend/app.py            # Streamlit dashboard
├── tests/                     # pytest
├── data/                      # SQLite database (created automatically)
└── docs/                      # this guide, diagrams, slides
```
Folders map one-to-one to the architecture layers, which makes the project easy to explain and to divide among teammates.

---

# PART 7 — Dashboard

**Recommendation: Streamlit + Plotly.** It is pure Python, so the team spends time on the science, not on frontend plumbing. Charts, tabs, metrics and a download button
come built in, and it still looks professional. **React** would look more custom but costs weeks and gives judges nothing extra to see. If you have spare time
later, wrap the same FastAPI backend in a React front end.

**Polish tips (cheap, high impact)**
- Add `.streamlit/config.toml` with a dark theme and one accent colour.
- Keep colours meaningful: green = ACCEPT, amber = INCONCLUSIVE, red = REJECT.
- Put the Reality Check tab in the demo on purpose; honesty is a strength.
- Pre-run one scenario of each type before judges arrive so the history looks alive.

**Extra features to highlight you (all included or one step away)**
1. Two-threshold verdicts (ACCEPT / INCONCLUSIVE / REJECT).
2. Thresholds derived from probability with a stated false-alarm rate.
3. Attack strength slider and a Monte-Carlo detection curve.
4. Live channel-health gauge from Bell pairs (QBER).
5. Noise model so honest signatures are realistically imperfect.
6. "Why was this decided?" evidence: expected vs observed, p-value, reason text.
7. Hash-chained tamper-evident audit log with an integrity check.
8. Toy Shor demo explaining the quantum threat.
9. Reality Check panel.
10. One-time keys and a replay ledger (classical layer).
Stretch ideas if time remains: a PDF/JSON incident report button, a parameter sweep page (block size vs detection power), and a side-by-side "RSA vs QDS" explainer.

---

# PART 8 — No fake claims

Use this table to keep your wording correct in the report, slides and demo.

| Real quantum cryptography | Our prototype |
|---|---|
| Photons or matter qubits on real hardware | NumPy and Qiskit simulations on a laptop |
| Security from physical laws under real conditions | Security *behaviour* illustrated in a model |
| Quantum memory, detectors, authenticated channels | Modelled by noise parameters and fields |
| Formal proofs against all attacks | Simulated tests against two simple attacks |

**Say:** "quantum-simulated, quantum-inspired prototype", "demonstrates the detection mechanism", "educational model inspired by Gottesman-Chuang QDS".

**Never say:** "our classical computer is a quantum computer", "unbreakable", "provides physical quantum security", "production-ready", "simulated attacks prove security".

---

# PART 9 — Limitations and future scope

**Limitations**
- Simulation only; no physical layer, no real noise or loss beyond simple models.
- 8-bit demo digest; real systems need long digests and formal security proofs.
- Only two forger strategies are simulated; stronger attackers exist.
- Authenticated classical channel and identities are assumed.
- Replay defence is classical.
- Small interceptors (under about 10% of qubits) are inside the noise and are not reliably detected.
- Bulk teleportation is modelled as ideal teleportation plus noise.

**Future scope**
- Run the small circuits on real IBM Quantum hardware (needs an account) for the Bell and teleportation demos.
- Add a realistic photon-loss and detector model.
- Multi-verifier transferability tests (the reason real QDS uses two thresholds).
- Compare against post-quantum signatures such as ML-DSA in a hybrid design.
- Optimal-attack analysis and formal security bounds.

---

# PART 10 — SIH presentation kit

**Slide flow (one idea per slide)**
1. **Problem.** RSA and ECC and Shor's algorithm; long-lived signatures are at risk.
2. **Idea.** QDS: public key made of quantum states; security from physics.
3. **Our solution.** A quantum-simulated threat-detection framework for QDS (no AI/ML).
4. **Architecture.** The corrected diagram from Part 3.
5. **How it works.** Six-state keys, Bell-pair channel test, teleportation transport, statistical verification.
6. **Detection.** Five attacks and how each is caught (table).
7. **Statistics.** Two thresholds from binomial probability; expected vs observed chart.
8. **Demo.** Screenshots of the dashboard.
9. **Innovation and feasibility.** Runs on a laptop, free tools, 14 passing tests.
10. **Limitations and future scope.** Honest and confident.

**Short answers to the standard "why" questions**
- **Why quantum?** Shor's algorithm threatens RSA/ECC; QDS bases security on physics instead of unproven hard problems.
- **Why QDS?** It offers signatures whose security does not depend on factoring or discrete logs.
- **Why not RSA/ECC?** They fall to a large quantum computer; we study what replaces them and how to monitor it.
- **Why no AI/ML?** The problem requires explainable, threshold-based detection; counting statistics is transparent and provable.
- **Why Qiskit?** Free, local, widely used, good noise tools; its circuits give us Bell states and teleportation. PennyLane is ML-oriented; Cirq has fewer beginner resources.
- **How are Bell states used?** Entangled pairs test the channel: measurement agreement drops when someone intercepts.
- **How is teleportation used?** It moves public-key states to the verifier; the two classical bits drive Pauli corrections.
- **How are attacks simulated?** Software models: random guessing, measure-and-guess, replay of a captured packet, wrong identity, unregistered verifier, and an intercept-resend eavesdropper.
- **How does statistical detection work?** Honest noise gives about 2% mismatches per block; forgers give 33–50%. Two thresholds derived from binomial probabilities separate them.

---

# PART 11 — Likely judge questions and simple answers

1. **Is this real quantum cryptography?** No. It is a quantum-simulated educational prototype. It demonstrates the detection logic that a real system would use.
2. **Can a normal computer run quantum things?** A classical computer can *simulate* a few qubits exactly. That is fine for learning and testing, but it gives no physical security.
3. **Do you need an IBM account?** No. Everything runs locally on Qiskit Aer.
4. **Why not use post-quantum cryptography (like ML-DSA)?** PQC is a strong practical option and runs on normal computers. We study the quantum-physics route and its threat monitoring. A real deployment could combine both.
5. **What makes QDS secure in principle?** No-cloning and measurement disturbance: an attacker cannot copy the key states, and probing them creates detectable errors.
6. **How do you pick thresholds?** From the binomial distribution: `s_a` so honest blocks exceed it with probability at most 10⁻⁶, `s_v` so forgers fall below it with probability under 10⁻⁶.
7. **Why two thresholds?** The gap gives an INCONCLUSIVE zone for weak tampering or unusual noise; real QDS uses this idea so different verifiers stay consistent.
8. **What is the false alarm rate?** By design at most about 8·10⁻⁶ per signature under the assumed noise; in 400 test runs none was wrongly flagged.
9. **What if real noise is higher than assumed?** Recalibrate `EXPECTED_ERROR` and increase block size; the code refuses to run if thresholds cannot be separated.
10. **How is replay detected?** By a classical layer: one-time key IDs, nonce, timestamp window. Quantum physics alone does not stop replay, and we say so.
11. **How do you tell impersonation from forgery?** The quantum statistics look alike; the difference is the authenticated identity of the submitter, which is assumed by QDS protocols.
12. **What if an attacker intercepts only a few qubits?** Below about 10% it hides in the noise. The detection-curve tab shows this limit honestly.
13. **Why use Bell states at all?** They give an independent channel-health measurement, so we can tell "channel attacked" from "signature forged".
14. **Is teleportation really simulated?** The exact circuit runs on Qiskit with fidelity 1. In bulk it is modelled as ideal teleportation plus Pauli noise for speed; a test checks the ideal case.
15. **Why an 8-bit digest?** A teaching simplification that keeps quantum data small. Production needs longer digests plus security proofs.
16. **How is this different from a normal signature checker?** Verification here is a *measurement* with probabilistic outcomes, so decisions are statistical, and attacks show up as measurable disturbance.
17. **Can attackers forge by measuring their copy?** In our model yes, but they fail with about 33% mismatch per element and are caught with overwhelming probability.
18. **Does AI or ML appear anywhere?** No. Only counting, probability and rules.
19. **Is the audit log a blockchain?** It is a simple hash chain: each entry hashes the previous one, so editing history is detectable. No mining or network.
20. **What is your innovation?** A complete, explainable, testable detection framework: derived two-threshold decisions, per-block checks, channel monitoring with Bell pairs, attack lab with detection curves, tamper-evident logging, and an honesty panel.
21. **What would you do with real hardware?** Run the Bell and teleportation circuits on IBM Quantum devices, measure real error rates, and recalibrate the thresholds.
22. **What is the main limitation?** It is a simulation with simple attackers; formal proofs and real hardware are future work.

---

*End of guide.*
