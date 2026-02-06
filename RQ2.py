import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
from scipy.stats import spearmanr

df = pd.read_excel("EntrySurvey_JaydenUpdated.xlsx")
df.head()

drop = [
    "Start Date",
    "End Date",
    "Response Type",
    "IP Address",
    "Duration (in seconds)",
    "Recipient Last Name",
    "Recipient First Name",
    "Recipient Email",
    "External Data Reference",
    "Location Latitude",
    "Location Longitude",
    "Distribution Channel",
    "User Language",
    "Do you wish to be notified via email, once the results of the survey has been processed at the end of the data collection?",
]

consent_col = [
    c for c in df.columns if c.startswith("Welcome to the REBOUND research study!")
][0]

df = df[
    (df[consent_col] != "I do not consent, I do not wish to participate")
    & (~df[consent_col].isna())
]

for col in df.columns:
    if col.startswith("Welcome to the REBOUND research study!"):
        drop.append(col)
df = df.drop(columns=drop, errors="ignore")


#! Is there evidence that students who perceive REBOUND as more helpful tend to
# achieve more academic outcomes compared to those who perceive it as less helpful?
score_df = pd.read_excel("REBOUND Score.xlsx")
score_df.head()
score = "Score"

survey_cols = [
    "Response ID",
    "Unit",
    "Thoughts Content Covered",
    "Thoughts Facilitator",
    "Thoughts Structure of the Classes",
    "Confidence Unit Content",
    "Confidence Assessments",
    "Repeating Student",
]

survey_df = df[survey_cols].copy()
merged = pd.merge(
    survey_df, score_df[["Response ID", score]], on="Response ID", how="inner"
)

# Change to other components if needed (Jayden was lazy sorry)
merged["High"] = merged["Confidence Unit Content"] >= 3

merged_1000 = merged[merged["Unit"] == "COMP1000- Introduction to Computer Programming"]

merged_1350 = merged[
    merged["Unit"] == "COMP1350 - Introduction to Database Design and Management"
]


low_1000 = merged_1000.loc[~merged_1000["High"], "Score"].dropna()
high_1000 = merged_1000.loc[merged_1000["High"], "Score"].dropna()

u_1000, p_1000 = mannwhitneyu(low_1000, high_1000, alternative="two-sided")

print("COMP1000 Confidence Unit Content")
print(f"Low N = {len(low_1000)}, High N = {len(high_1000)}")
print(f"U statistic = {u_1000:.2f}, p-value = {p_1000:.4f}")

low_1350 = merged_1350.loc[~merged_1350["High"], "Score"].dropna()
high_1350 = merged_1350.loc[merged_1350["High"], "Score"].dropna()

u_1350, p_1350 = mannwhitneyu(low_1350, high_1350, alternative="two-sided")

print("COMP1350 Confidence Unit Content")
print(f"Low N = {len(low_1350)}, High N = {len(high_1350)}")
print(f"U statistic = {u_1350:.2f}, p-value = {p_1350:.4f}")


def rank(u, n1, n2):
    return 1 - (2 * u) / (n1 * n2)


r_1000 = rank(u_1000, len(low_1000), len(high_1000))
r_1350 = rank(u_1350, len(low_1350), len(high_1350))

print("Effect sizes")
print(f"COMP1000: r = {r_1000:.3f}")
print(f"COMP1350: r = {r_1350:.3f}")


data_1000 = merged[
    merged["Unit"] == "COMP1000- Introduction to Computer Programming"
].dropna(subset=["Confidence Unit Content", "Score"])
plt.figure(figsize=(6, 4))
sns.regplot(
    data=data_1000,
    x="Confidence Unit Content",
    y="Score",
    scatter_kws={"alpha": 0.6},
    line_kws={"linestyle": "--"},
)
plt.title("COMP1000: Confidence Unit Content vs Final Score")
plt.xlabel("Confidence Unit Content")
plt.ylabel("Final Score")
plt.xticks([1, 2, 3, 4])
plt.tight_layout()
plt.show()


data_1350 = merged[
    merged["Unit"] == "COMP1350 - Introduction to Database Design and Management"
].dropna(subset=["Confidence Unit Content", "Score"])

plt.figure(figsize=(6, 4))
sns.regplot(
    data=data_1350,
    x="Confidence Unit Content",
    y="Score",
    scatter_kws={"alpha": 0.6},
    line_kws={"linestyle": "--"},
    lowess=True,
)

plt.title("COMP1350: Confidence Unit Content vs Final Score")
plt.xlabel("Confidence Unit Content")
plt.ylabel("Final Score")
plt.xticks([1, 2, 3, 4])
plt.tight_layout()
plt.show()


## capture 1st gen family and repeating student
