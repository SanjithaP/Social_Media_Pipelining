import os
import time
import json
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
API_KEY = os.getenv("PERSPECTIVE_API_KEY")
assert API_KEY, "Set PERSPECTIVE_API_KEY in .env"

DATA_DIR = Path("data")
OUT_DIR = Path("out"); OUT_DIR.mkdir(exist_ok=True)
OUT_PARQ = OUT_DIR / "posts_scored.parquet"
OUT_CSV  = OUT_DIR / "posts_scored.csv"

SAMPLE_PER_SOURCE = 10000
PER_REQUEST_SLEEP = 1.0
BATCH_SIZE = 100

COLUMN_HINTS = {
    "bluesky_posts.csv": {"text": "record", "time": "indexed_at"},
    "sp_posts.csv":      {"text": "com",    "time": "time"},
    "pol_posts.csv":     {"text": "com",    "time": "time"},
}

def guess_source(path):
    name = path.name.lower()
    if "pol" in name: return "4chan_pol"
    if "sp"  in name: return "4chan_sp"
    if any(x in name for x in ["bsky","blue","bluesky"]): return "bsky"
    return name.replace(".csv","")

def pick_time_series(df, path, hints):
    if "time" in hints and hints["time"] in df.columns:
        col = hints["time"]
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            s = pd.to_numeric(s, errors="coerce")
            unit = "ms" if s.dropna().median() > 1e12 else "s"
            dt = pd.to_datetime(s, unit=unit, utc=True, errors="coerce")
        else:
            dt = pd.to_datetime(s, utc=True, errors="coerce")
        if dt.notna().any():
            print(f"  time: using hint column '{col}'")
            return dt
    for col in ["created_at","createdAt","indexed_at","indexedAt","time","timestamp","ts","date"]:
        if col in df.columns:
            s = df[col]
            if pd.api.types.is_numeric_dtype(s):
                s = pd.to_numeric(s, errors="coerce")
                unit = "ms" if s.dropna().median() > 1e12 else "s"
                dt = pd.to_datetime(s, unit=unit, utc=True, errors="coerce")
            else:
                dt = pd.to_datetime(s, utc=True, errors="coerce")
            if dt.notna().mean() > 0.3:
                print(f"  time: picked '{col}'")
                return dt
    best = None
    best_ok = 0.0
    for col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().mean() < 0.6:
            continue
        for unit in ["s","ms"]:
            dt = pd.to_datetime(s, unit=unit, utc=True, errors="coerce")
            ok = dt.notna().mean()
            if ok > best_ok:
                best_ok = ok
                best = dt
    if best is not None and best_ok > 0.6:
        print("  time: picked a numeric column by guessing seconds/ms")
        return best
    raise ValueError(f"Could not find a usable timestamp in {path.name}. Columns: {list(df.columns)}")

def parse_record_to_text(series):
    out = []
    for v in series.astype(str):
        txt = ""
        try:
            obj = json.loads(v)
            if isinstance(obj, dict):
                txt = str(obj.get("text") or "")
            else:
                txt = ""
        except Exception:
            txt = ""
        out.append(txt)
    s = pd.Series(out, index=series.index)
    return s

def pick_text_series(df, path, hints):
    if "text" in hints and hints["text"] in df.columns:
        col = hints["text"]
        if col == "record":
            s = parse_record_to_text(df[col])
            if s.str.len().sum() > 0:
                print("  text: using 'record' (JSON → text)")
                return s.fillna("").str.strip()
        else:
            print(f"  text: using hint column '{col}'")
            return df[col].astype(str).fillna("").str.strip()
    for col in ["body","text","com","comment","content","message","full_text","body_text"]:
        if col in df.columns:
            print(f"  text: picked '{col}'")
            return df[col].astype(str).fillna("").str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            s = df[col].astype(str)
            if s.str.contains('"text"').mean() > 0.2:
                parsed = parse_record_to_text(s)
                if parsed.str.len().sum() > 0:
                    print(f"  text: parsed JSON from '{col}'")
                    return parsed.fillna("").str.strip()
    best_col = None
    best_score = -1.0
    for col in df.columns:
        if df[col].dtype == object:
            s = df[col].astype(str).fillna("")
            mean_len = s.str.len().mean()
            if mean_len < 8:
                continue
            letters = (s.str.count(r"[A-Za-z]")).sum()
            spaces  = (s.str.count(r"\s")).sum()
            total   = max(int(s.str.len().sum()), 1)
            score   = float(mean_len) * float(letters + spaces) / float(total)
            if score > best_score:
                best_score = score
                best_col = col
    if best_col is not None:
        print(f"  text: picked longest-looking column '{best_col}'")
        return df[best_col].astype(str).fillna("").str.strip()
    raise ValueError(f"Could not find a text/body column in {path.name}.")

def load_one_csv(path):
    print(f"\nLoading {path.name} ...")
    hints = COLUMN_HINTS.get(path.name, {})
    df = pd.read_csv(path, low_memory=False)
    df["source"] = guess_source(path)
    df["created_at"] = pick_time_series(df, path, hints)
    df["body"]       = pick_text_series(df, path, hints)
    if "thread_number" not in df.columns:
        for c in ["thread_id","thread","tid","root","root_id","resto"]:
            if c in df.columns:
                df = df.rename(columns={c: "thread_number"})
                break
    if "board_name" not in df.columns and "board" in df.columns:
        df = df.rename(columns={"board": "board_name"})
    if "id" not in df.columns:
        df["id"] = (
            path.name + "|" +
            df["created_at"].astype(str) + "|" +
            df["body"].astype(str).str.slice(0, 64)
        )
    need = ["id","source","board_name","thread_number","created_at","body"]
    for c in need:
        if c not in df.columns:
            df[c] = pd.NA
    print(f"  rows: {len(df)}  (source={df['source'].iloc[0]})")
    return df[need]

files = sorted(DATA_DIR.glob("*.csv"))
if not files:
    raise SystemExit("No CSVs in ./data")

frames = []
for f in files:
    try:
        frames.append(load_one_csv(f))
    except Exception as e:
        print(f"Skipping {f.name} because: {e}")

if not frames:
    raise SystemExit("No usable CSVs after parsing")

posts = pd.concat(frames, ignore_index=True)
posts = posts.dropna(subset=["created_at"]).copy()
posts = posts.drop_duplicates(subset=["id"])

for c in ["toxicity","severe_toxicity"]:
    if c not in posts.columns:
        posts[c] = np.nan

need = posts["toxicity"].isna() & posts["body"].astype(str).str.len().gt(0)

if SAMPLE_PER_SOURCE is None:
    idx_to_score = posts.index[need].tolist()
    print("Scoring ALL rows that need scores:", len(idx_to_score))
else:
    idx_to_score = []
    for src, part in posts[need].groupby("source"):
        n = min(SAMPLE_PER_SOURCE, len(part))
        if n > 0:
            pick = part.sample(n=n, random_state=42).index.tolist()
            idx_to_score.extend(pick)
            print(f"{src}: will score {n} rows")
    print("Total to score:", len(idx_to_score))

API_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
session = requests.Session()

def score_text(text):
    t = (text or "")[:2000]
    payload = {
        "comment": {"text": t},
        "languages": ["en"],
        "requestedAttributes": {
            "TOXICITY": {},
            "SEVERE_TOXICITY": {}
        }
    }
    params = {"key": API_KEY}
    for _ in range(3):
        try:
            r = session.post(API_URL, params=params, json=payload, timeout=30)
        except requests.RequestException:
            time.sleep(1)
            continue
        if r.status_code == 200:
            data = r.json()
            tox = np.nan
            sev = np.nan
            try:
                tox = data["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
            except Exception:
                pass
            try:
                sev = data["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
            except Exception:
                pass
            return tox, sev
        if r.status_code in (429, 503):
            time.sleep(2)
            continue
        return np.nan, np.nan
    return np.nan, np.nan

if idx_to_score:
    for start in tqdm(range(0, len(idx_to_score), BATCH_SIZE), desc="Scoring"):
        chunk = idx_to_score[start:start + BATCH_SIZE]
        tox_vals = []
        sev_vals = []
        for i in chunk:
            t, s = score_text(posts.at[i, "body"])
            tox_vals.append(t)
            sev_vals.append(s)
            time.sleep(PER_REQUEST_SLEEP)
        posts.loc[chunk, "toxicity"] = tox_vals
        posts.loc[chunk, "severe_toxicity"] = sev_vals
        posts.to_parquet(OUT_PARQ, index=False)

posts.to_parquet(OUT_PARQ, index=False)
posts.to_csv(OUT_CSV, index=False)
print("Wrote:", OUT_PARQ, "and", OUT_CSV)
