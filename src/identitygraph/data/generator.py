"""Seeded synthetic credit-application generator. ALL DATA IS SYNTHETIC."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import load_config
from .schemas import CHANNELS, EMPLOYMENT

FIRST = ["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery", "Quinn",
         "Priya", "Wei", "Maria", "Omar", "Elena", "Kofi", "Hana", "Luca", "Nia", "Ravi"]
LAST = ["Smith", "Johnson", "Lee", "Patel", "Garcia", "Kim", "Nguyen", "Brown", "Davis", "Khan",
        "Martin", "Lopez", "Clark", "Young", "Singh", "Adams", "Baker", "Reed", "Cruz", "Wong"]
STREETS = ["Oak", "Maple", "Pine", "Cedar", "Elm", "Lake", "Hill", "River", "Park", "Main"]
REF_DATE = pd.Timestamp("2025-06-01")


class _Gen:
    def __init__(self, seed: int):
        self.rng = np.random.default_rng(seed)
        self.counter = 0

    def uid(self, prefix: str) -> str:
        self.counter += 1
        return f"{prefix}{self.counter:07d}"

    def name(self) -> str:
        return f"{self.rng.choice(FIRST)} {self.rng.choice(LAST)}"

    def dob(self, lo: int = 20, hi: int = 75) -> str:
        age = int(self.rng.integers(lo, hi))
        d = REF_DATE - pd.Timedelta(days=age * 365 + int(self.rng.integers(0, 365)))
        return d.strftime("%Y-%m-%d")

    def email(self, name: str) -> str:
        base = name.lower().replace(" ", ".")
        dom = self.rng.choice(["mail.test", "inbox.test", "post.test"])
        return f"{base}{int(self.rng.integers(1, 9999))}@{dom}"

    def phone(self) -> str:
        return f"+1-555-{int(self.rng.integers(1000000, 9999999))}"

    def address(self) -> str:
        return f"{int(self.rng.integers(1, 9999))} {self.rng.choice(STREETS)} St, Unit {int(self.rng.integers(1, 400))}"

    def device(self) -> str:
        return f"dev-{int(self.rng.integers(10**8, 10**9))}"

    def ip(self) -> str:
        r = self.rng
        return f"{int(r.integers(11, 220))}.{int(r.integers(0, 255))}.{int(r.integers(0, 255))}.{int(r.integers(1, 255))}"

    def income(self, emp: str) -> float:
        mu = {"employed": 11.0, "self_employed": 11.0, "unemployed": 9.5, "student": 9.6, "retired": 10.6}[emp]
        return float(np.exp(self.rng.normal(mu, 0.45)))


def _group_sizes(r, total: int, lo: int, hi: int) -> list[int]:
    out = []
    while total > 0:
        s = min(total, int(r.integers(lo, hi + 1)))
        out.append(s)
        total -= s
    return out


def generate(n: int | None = None, seed: int | None = None, cfg: dict | None = None) -> pd.DataFrame:
    cfg = dict(cfg or load_config("data"))
    n = n or cfg["n_records"]
    seed = cfg["seed"] if seed is None else seed
    g = _Gen(seed)
    r = g.rng
    start = pd.Timestamp(cfg["start_date"])
    span = cfg["days"] * 86400
    rows: list[dict] = []

    def rand_ts() -> pd.Timestamp:
        return start + pd.Timedelta(seconds=float(r.uniform(0, span)))

    def base_row(ts, scenario, label, name=None, **over):
        emp = str(r.choice(EMPLOYMENT, p=[0.6, 0.15, 0.08, 0.07, 0.10]))
        inc = g.income(emp)
        nm = name or g.name()
        row = dict(
            application_id="", applicant_id=g.uid("APL"), application_timestamp=ts,
            full_name=nm, date_of_birth=g.dob(), email=g.email(nm), phone=g.phone(),
            address=g.address(), device_id=g.device(), ip_address=g.ip(), employment_status=emp,
            annual_income=round(inc, 2),
            requested_credit=round(inc * float(np.clip(r.lognormal(-1.6, 0.6), 0.02, 1.0)), 2),
            application_channel=str(r.choice(CHANNELS, p=[0.45, 0.35, 0.1, 0.1])),
            fraud_label=label, fraud_scenario=scenario,
        )
        row.update(over)
        return row

    n_fraud_target = int(n * cfg["fraud_rate_target"])
    shares = {"synthetic_identity": 0.25, "device_ring": 0.2, "shared_contact": 0.15,
              "velocity_burst": 0.15, "identity_inconsistency": 0.13, "income_anomaly": 0.12}
    counts = {k: int(v * n_fraud_target) for k, v in shares.items()}

    for size in _group_sizes(r, counts["device_ring"], 3, 8):
        dev, ip = g.device(), g.ip()
        t0 = rand_ts()
        for _ in range(size):
            ts = t0 + pd.Timedelta(hours=float(r.uniform(0, 24 * 20)))
            rows.append(base_row(ts, "device_ring", 1, device_id=dev if r.random() < 0.9 else g.device(),
                                 ip_address=ip if r.random() < 0.6 else g.ip()))
    for size in _group_sizes(r, counts["shared_contact"], 2, 6):
        ph, ad = g.phone(), g.address()
        t0 = rand_ts()
        for _ in range(size):
            ts = t0 + pd.Timedelta(hours=float(r.uniform(0, 24 * 30)))
            rows.append(base_row(ts, "shared_contact", 1,
                                 phone=ph if r.random() < 0.8 else g.phone(),
                                 address=ad if r.random() < 0.7 else g.address()))
    for size in _group_sizes(r, counts["velocity_burst"], 4, 10):
        dev, ip = g.device(), g.ip()
        t0 = rand_ts()
        for _ in range(size):
            ts = t0 + pd.Timedelta(minutes=float(r.uniform(0, 90)))
            rows.append(base_row(ts, "velocity_burst", 1,
                                 device_id=dev if r.random() < 0.7 else g.device(), ip_address=ip))
    for size in _group_sizes(r, counts["synthetic_identity"], 2, 5):
        ph, ad, shared_nm = g.phone(), g.address(), g.name()
        t0 = rand_ts()
        for _ in range(size):
            ts = t0 + pd.Timedelta(days=float(r.uniform(0, 40)))
            nm = g.name()
            rows.append(base_row(ts, "synthetic_identity", 1, name=nm,
                                 phone=ph if r.random() < 0.6 else g.phone(),
                                 address=ad if r.random() < 0.5 else g.address(),
                                 email=g.email(shared_nm) if r.random() < 0.3 else g.email(nm),
                                 date_of_birth=g.dob(18, 24) if r.random() < 0.5 else g.dob(),
                                 employment_status="unemployed" if r.random() < 0.4 else "employed"))
    for _ in range(counts["identity_inconsistency"]):
        nm = g.name()
        rows.append(base_row(rand_ts(), "identity_inconsistency", 1, name=nm,
                             email=f"{g.name().lower().replace(' ', '')}{int(r.integers(1, 99))}@mail.test",
                             date_of_birth=g.dob(18, 22)))
    for _ in range(counts["income_anomaly"]):
        row = base_row(rand_ts(), "income_anomaly", 1)
        row["requested_credit"] = round(row["annual_income"] * float(r.uniform(0.8, 2.5)), 2)
        rows.append(row)

    n_legit = n - len(rows)
    households = [(g.address(), g.device(), g.ip()) for _ in range(max(1, n_legit // 40))]
    for _ in range(n_legit):
        row = base_row(rand_ts(), "legitimate", 0)
        if r.random() < 0.06:  # legitimate shared households add realistic noise
            ad, dv, ip = households[int(r.integers(0, len(households)))]
            row["address"] = ad
            if r.random() < 0.5:
                row["device_id"], row["ip_address"] = dv, ip
        if r.random() < 0.03:
            row["requested_credit"] = round(row["annual_income"] * float(r.uniform(0.5, 1.2)), 2)
        if r.random() < 0.04:
            row["email"] = f"{g.name().lower().replace(' ', '')}@mail.test"
        if r.random() < 0.05:
            row["date_of_birth"] = g.dob(18, 22)
        rows.append(row)

    df = pd.DataFrame(rows)
    df["application_timestamp"] = pd.to_datetime(df["application_timestamp"])
    df = df.sort_values("application_timestamp", kind="stable").reset_index(drop=True)
    df["application_id"] = [f"APP{i:07d}" for i in range(1, len(df) + 1)]
    return df
