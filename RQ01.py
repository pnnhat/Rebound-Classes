import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
from matplotlib.patches import Patch

df = pd.read_excel("entry_with_Participant ID.xlsx")

fg = df[df["First Generation Student"] == 1]

fg_unique_sem = (
    fg.groupby("Semester")["StudentID"]
    .nunique()
    .reset_index()
    .rename(columns={"StudentID": "Unique First Generation Students (n)"})
    .sort_values("Semester")
)
fg_unique_sem

# ----- Unique totals per Semester x Course -----
total_unique = (
    df.groupby(["Semester", "C1/C2"])["StudentID"]
    .nunique()
    .reset_index()
    .rename(columns={"StudentID": "Total Unique Students (n)"})
)

# ----- Unique first-gen per Semester x Course -----
fg = df[df["First Generation Student"] == 1]
fg_unique = (
    fg.groupby(["Semester", "C1/C2"])["StudentID"]
    .nunique()
    .reset_index()
    .rename(columns={"StudentID": "Unique First Generation Students (n)"})
)

# Merge + compute %
summary = total_unique.merge(fg_unique, on=["Semester", "C1/C2"], how="left")
summary["Unique First Generation Students (n)"] = (
    summary["Unique First Generation Students (n)"].fillna(0).astype(int)
)
summary["First Generation (%)"] = (
    summary["Unique First Generation Students (n)"]
    / summary["Total Unique Students (n)"]
    * 100
)

summary = summary.sort_values(["Semester", "C1/C2"])

# ----- Clustered columns: S1 C1, S1 C2, S2 C1, S2 C2 -----
groups = [("S1", "C1"), ("S1", "C2"), ("S2", "C1"), ("S2", "C2")]

sem_map = {"S1": "Semester 1", "S2": "Semester 2"}

vals, totals, pcts, labels = [], [], [], []
for sem, unit in groups:
    row = summary[(summary["Semester"] == sem) & (summary["C1/C2"] == unit)]

    if len(row) == 0:
        vals.append(0)
        totals.append(0)
        pcts.append(0.0)
        labels.append(f"{sem_map.get(sem, sem)} {unit} (n = 0)")
    else:
        fg_n = int(row["Unique First Generation Students (n)"].iloc[0])
        tot_n = int(row["Total Unique Students (n)"].iloc[0])
        pct = float(row["First Generation (%)"].iloc[0]) if tot_n > 0 else 0.0

        vals.append(fg_n)
        totals.append(tot_n)
        pcts.append(pct)
        labels.append(f"{sem_map.get(sem, sem)} {unit} (n = {tot_n})")

x = np.arange(len(labels))

plt.figure(figsize=(11, 6), dpi=200)
bars = plt.bar(x, vals, width=0.55, color="#A7C7E7")

for i, bar in enumerate(bars):
    count = int(bar.get_height())
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        count + 0.3,
        f"n = {count} ({pcts[i]:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.xticks(x, labels)
plt.ylabel("First Generation Students")
plt.tight_layout()
plt.show()


rep = df[df["Repeating Student"] == 1]
rep_unique = (
    rep.groupby(["Semester"])["StudentID"]
    .nunique()
    .reset_index()
    .rename(columns={"StudentID": "Unique Repeating Students (n)"})
)
rep_unique = rep_unique.sort_values(["Semester"])

rep_unique


df = pd.read_excel("RQ1.xlsx")

outcomes = ["Pass", "Fail", "Withdrawn"]

colors = {"Pass": "#A7C7E7", "Fail": "#FFD6A5", "Withdrawn": "#B7E4C7"}

# counts per Semester × Unit × Grade
counts = (
    df.groupby(["Semester", "C1/C2", "Grade"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=outcomes, fill_value=0)
)

panels = [("S1", "C1"), ("S1", "C2"), ("S2", "C1"), ("S2", "C2")]
sem_map = {"S1": "Semester 1", "S2": "Semester 2"}

for sem, unit in panels:
    key = (sem, unit)

    vals = (
        counts.loc[key] if key in counts.index else pd.Series({o: 0 for o in outcomes})
    )
    total = int(vals.sum())

    fig, ax = plt.subplots(figsize=(7, 5), dpi=200)

    bars = ax.bar(
        outcomes,
        [int(vals[o]) for o in outcomes],
        color=[colors[o] for o in outcomes],
    )

    ymax = max(1, int(vals.max())) + 3
    ax.set_ylim(0, ymax)
    ax.set_ylabel("Number of Students")
    ax.set_title(f"{sem_map.get(sem, sem)} {unit} (n = {total})")

    for bar in bars:
        c = int(bar.get_height())
        pct = (c / total * 100) if total > 0 else 0.0
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"n = {c} ({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()


df = pd.read_excel("RQ1.xlsx", sheet_name="Sheet2")
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
fg = df[df["First Generation Student"] == 1]

fg_mean = (
    fg.groupby(["Semester", "C1/C2"])["Score"]
    .mean()
    .reset_index()
    .rename(columns={"Score": "Mean Score (First-Gen)"})
)

fg_mean["Mean Score (First-Gen)"] = fg_mean["Mean Score (First-Gen)"].round(1)
fg_mean


fg_perf = (
    fg.groupby(["Semester", "C1/C2", "Grade"])["StudentID"]
    .nunique()
    .unstack(fill_value=0)
    .reset_index()
)
fg_perf["Total (n)"] = fg_perf[["Pass", "Fail", "Withdrawn"]].sum(axis=1)
fg_perf

# Order groups
groups = [("S1", "C1"), ("S1", "C2"), ("S2", "C1"), ("S2", "C2")]

sem_map = {"S1": "Semester 1", "S2": "Semester 2"}

vals = []
totals = []
labels = []

for sem, unit in groups:
    row = fg_perf[(fg_perf["Semester"] == sem) & (fg_perf["C1/C2"] == unit)]

    if len(row) == 0:
        vals.append([0, 0, 0])
        totals.append(0)
        labels.append(f"{sem_map[sem]} {unit} (n = 0)")
    else:
        p = int(row["Pass"].iloc[0])
        f = int(row["Fail"].iloc[0])
        w = int(row["Withdrawn"].iloc[0])
        total = int(row["Total (n)"].iloc[0])

        vals.append([p, f, w])
        totals.append(total)
        labels.append(f"{sem_map[sem]} {unit} (n = {total})")

vals = np.array(vals)

# Light theme colours (same style as before)
colors = {"Pass": "#A7C7E7", "Fail": "#FFD6A5", "Withdrawn": "#B7E4C7"}

outcomes = ["Pass", "Fail", "Withdrawn"]

x = np.arange(len(labels))
width = 0.25

plt.figure(figsize=(12, 6), dpi=200)

bars_pass = plt.bar(x - width, vals[:, 0], width, label="Pass", color=colors["Pass"])
bars_fail = plt.bar(x, vals[:, 1], width, label="Fail", color=colors["Fail"])
bars_wdrw = plt.bar(
    x + width, vals[:, 2], width, label="Withdrawn", color=colors["Withdrawn"]
)

# Add headroom
plt.ylim(0, max(1, int(vals.max())) + 5)


# Annotate
def annotate(bars, idx):
    for i, bar in enumerate(bars):
        count = int(bar.get_height())
        total = totals[i]
        pct = (count / total * 100) if total > 0 else 0.0

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.4,
            f"n = {count} ({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )


annotate(bars_pass, 0)
annotate(bars_fail, 1)
annotate(bars_wdrw, 2)

plt.xticks(x, labels, rotation=15, ha="right")
plt.ylabel("Number of First Generation Students")
plt.legend(title="Grade")

plt.tight_layout()
plt.show()


outcomes = ["Pass", "Fail", "Withdrawn"]
groups = [("S1", "C1"), ("S1", "C2"), ("S2", "C1"), ("S2", "C2")]
sem_map = {"S1": "Semester 1", "S2": "Semester 2"}

# Outcome colors stay consistent
colors = {"Pass": "#A7C7E7", "Fail": "#FFD6A5", "Withdrawn": "#B7E4C7"}

# total counts
tot = (
    df.groupby(["Semester", "C1/C2", "Grade"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=outcomes, fill_value=0)
)

# first-gen counts
fg = df[df["First Generation Student"] == 1]
fgc = (
    fg.groupby(["Semester", "C1/C2", "Grade"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=outcomes, fill_value=0)
)

# build matrices in fixed order
tot_mat, fg_mat, labels, totals = [], [], [], []
for sem, unit in groups:
    if (sem, unit) in tot.index:
        trow = tot.loc[(sem, unit)].values.astype(int)
    else:
        trow = np.array([0, 0, 0], dtype=int)

    if (sem, unit) in fgc.index:
        frow = fgc.loc[(sem, unit)].values.astype(int)
    else:
        frow = np.array([0, 0, 0], dtype=int)

    tot_mat.append(trow)
    fg_mat.append(frow)

    n_total = int(trow.sum())
    totals.append(n_total)
    labels.append(f"{sem_map.get(sem, sem)} {unit} (n = {n_total})")

tot_mat = np.array(tot_mat)  # shape (4,3)
fg_mat = np.array(fg_mat)  # shape (4,3)
nonfg_mat = tot_mat - fg_mat  # remainder

x = np.arange(len(groups))
width = 0.25

fig, ax = plt.subplots(figsize=(12, 6), dpi=200)

# cluster positions for Pass/Fail/Withdrawn
offsets = [-width, 0.0, width]

# draw each outcome as a clustered bar, stacked FG + non-FG
for j, outcome in enumerate(outcomes):
    xpos = x + offsets[j]

    # FG segment (hatched)
    ax.bar(
        xpos,
        fg_mat[:, j],
        width,
        color=colors[outcome],
        edgecolor="black",
        hatch="///",
        linewidth=0.6,
        label=f"{outcome} (First-Gen)" if j == 0 else None,
    )

    # Non-FG segment (same color, no hatch) stacked on top
    ax.bar(
        xpos,
        nonfg_mat[:, j],
        width,
        bottom=fg_mat[:, j],
        color=colors[outcome],
        edgecolor="black",
        linewidth=0.6,
        label=f"{outcome} (Non-First-Gen)" if j == 0 else None,
    )

    # annotate TOTAL on top of each clustered bar, plus % FG in that outcome
    for i in range(len(groups)):
        total_outcome = int(tot_mat[i, j])
        fg_outcome = int(fg_mat[i, j])
        pct_fg = (fg_outcome / total_outcome * 100) if total_outcome > 0 else 0.0

        ax.text(
            xpos[i],
            total_outcome + 0.4,
            f"n={total_outcome}\n(FG {pct_fg:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=8,
        )

ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=15, ha="right")
ax.set_ylabel("Number of Students")
ax.set_ylim(0, max(1, int(tot_mat.max())) + 6)

# Two legends: outcomes (colors) + subgroup (hatch)
outcome_handles = [plt.Rectangle((0, 0), 1, 1, color=colors[o]) for o in outcomes]
leg1 = ax.legend(outcome_handles, outcomes, title="Grade", loc="upper right")
ax.add_artist(leg1)

sub_handles = [
    plt.Rectangle(
        (0, 0), 1, 1, facecolor="white", edgecolor="black", hatch="///", linewidth=0.6
    ),
    plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="black", linewidth=0.6),
]
ax.legend(
    sub_handles,
    ["First-Gen", "Non-First-Gen"],
    loc="upper right",
    bbox_to_anchor=(1, 0.7),
)

plt.tight_layout()
plt.show()
