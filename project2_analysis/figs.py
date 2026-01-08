import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, FuncFormatter, MaxNLocator
from pathlib import Path
import re

IN  = Path("out/posts_scored.parquet")
FIG = Path("figs")
FIG.mkdir(exist_ok=True)
OUT = Path("out"); OUT.mkdir(exist_ok=True)

WIN_START = pd.Timestamp("2025-11-01", tz="UTC")
WIN_END   = pd.Timestamp("2025-11-15", tz="UTC")

posts = pd.read_parquet(IN)
posts["created_at"] = pd.to_datetime(posts["created_at"], utc=True, errors="coerce")
posts = posts.dropna(subset=["created_at"])
if "source" not in posts.columns:
    posts["source"] = "unknown"

def in_window(df):
    return df[(df["created_at"] >= WIN_START) & (df["created_at"] < WIN_END)].copy()

def set_day_ticks(ax):
    ax.set_xlim([WIN_START, WIN_END])
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.grid(True, axis="y", alpha=0.3)
    ax.grid(True, axis="x", which="major", alpha=0.15)
    ax.tick_params(axis="x", labelsize=9, rotation=0)

print("making daily plots...")

subset_daily = in_window(posts)
daily_tmp = subset_daily.copy()
daily_tmp["date"] = daily_tmp["created_at"].dt.floor("D")
daily_all = daily_tmp.groupby(["date", "source"]).size().reset_index(name="n")
pivot_daily = daily_all.pivot(index="date", columns="source", values="n").fillna(0)

fig, ax = plt.subplots(figsize=(10, 4))
for src in sorted(pivot_daily.columns):
    ax.plot(pivot_daily.index, pivot_daily[src].values, label=src)
ax.set_title("Posts per day — all sources (Nov 1–14, 2025)")
ax.set_xlabel("time (UTC)")
ax.set_ylabel("# posts")
set_day_ticks(ax)
ax.legend()
plt.tight_layout()
plt.savefig(FIG / "posts_per_day_all_nov1_14.png")
plt.close()

print("Plots created successfully!")
print(f"Check the {FIG} directory for output")
