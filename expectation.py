import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
from matplotlib.patches import Patch

df = pd.read_excel("entry_expectation.xlsx")
df.columns = df.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
theme_cols = ["Theme 1", "Theme 2", "Theme 3", "Theme 4"]
themes = [
    "Understand Concepts",
    "Catch-up on Content",
    "Missed Lesson",
    "Assessments Help",
    "Extra Practice",
    "For Confidence",
    "Slow-paced Learning",
    "New to Computing",
]
for c in theme_cols:
    if c not in df.columns:
        df[c] = pd.NA


def norm_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


tmp = df.copy()
for c in theme_cols:
    tmp[c] = tmp[c].map(norm_cell)


def respondent_count(sub, theme):
    return int((sub[theme_cols] == theme).any(axis=1).sum())


denom = {
    ("Semester 1", "C1"): 28,
    ("Semester 1", "C2"): 19,
    ("Semester 2", "C1"): 16,
    ("Semester 2", "C2"): 7,
}


def cell_str(n, d):
    pct = (n / d * 100.0) if d > 0 else 0.0
    return f"{n} ({pct:.1f}%)"


groups = [
    ("Semester 1", "C1"),
    ("Semester 1", "C2"),
    ("Semester 2", "C1"),
    ("Semester 2", "C2"),
]

rows = []
for t in themes:
    row = {"Themes": t}
    for g in groups:
        sem, c = g
        sub = tmp[(tmp["Semester"] == sem) & (tmp["C1/C2"] == c)]
        n = respondent_count(sub, t)
        row[f"{sem} {c}"] = cell_str(n, denom[g])
    rows.append(row)

theme_table = pd.DataFrame(rows)[
    ["Themes", "Semester 1 C1", "Semester 1 C2", "Semester 2 C1", "Semester 2 C2"]
]

theme_table
