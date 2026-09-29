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
