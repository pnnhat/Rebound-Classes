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

counts = (
    df.groupby(["Semester", "C1/C2", "Grade"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=outcomes, fill_value=0)
)

groups = [("S1", "C1"), ("S1", "C2"), ("S2", "C1"), ("S2", "C2")]

labels = [f"{s} {u}" for s, u in groups]

data = []
for key in groups:
    if key in counts.index:
        data.append(counts.loc[key].values)
    else:
        data.append([0, 0, 0])

data = np.array(data)

x = np.arange(len(labels))
width = 0.25

plt.figure(figsize=(10, 6))

plt.bar(x - width, data[:, 0], width, label="Pass")
plt.bar(x, data[:, 1], width, label="Fail")
plt.bar(x + width, data[:, 2], width, label="Withdrawn")

plt.xticks(x, labels)
plt.ylabel("Number of Students")
plt.title("Academic Outcomes by Semester and Unit")
plt.legend()

plt.tight_layout()
plt.show()
