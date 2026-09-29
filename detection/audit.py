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
