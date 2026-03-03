import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

df = pd.read_excel("RQ4.xlsx")

df["Score"] = pd.to_numeric(df["Score"], errors="coerce")

df["Reason for Attendance"] = df["Reason for Attendance"].fillna("")


themes = [
    "Understand Concepts",
    "Catch-up on Content",
    "Extra Practice",
    "Assessments Help",
    "Missed Lesson",
    "For Confidence",
    "Slow-paced Learning",
    "New to Computing",
]

for theme in themes:
    df[theme] = df["Reason for Attendance"].str.contains(theme, case=False).astype(int)


def run_ttests(data, label="Overall"):
    results = []

    for theme in themes:
        group1 = data[data[theme] == 1]["Score"]
        group0 = data[data[theme] == 0]["Score"]

        if len(group1) > 1 and len(group0) > 1:
            t_stat, p_val = ttest_ind(group1, group0, equal_var=False)

            results.append(
                {
                    "Theme": theme,
                    "Mean (Selected)": round(group1.mean(), 1),
                    "Mean (Not Selected)": round(group0.mean(), 1),
                    "n Selected": len(group1),
                    "n Not Selected": len(group0),
                    "t-stat": round(t_stat, 3),
                    "p-value": round(p_val, 4),
                }
            )

    return pd.DataFrame(results)


overall_results = run_ttests(df, "Overall")
overall_results


unit_results = []

for unit in df["C1/C2"].unique():
    subset = df[df["C1/C2"] == unit]
    unit_results.append(run_ttests(subset, unit))

unit_results = pd.concat(unit_results, ignore_index=True)
unit_results


semester_results = []

for sem in df["Semester"].unique():
    subset = df[df["Semester"] == sem]
    semester_results.append(run_ttests(subset, sem))

semester_results = pd.concat(semester_results, ignore_index=True)
semester_results


unit_sem_results = []

for unit in df["C1/C2"].unique():
    for sem in df["Semester"].unique():
        subset = df[(df["C1/C2"] == unit) & (df["Semester"] == sem)]

        if len(subset) > 3:
            label = f"{unit} - {sem}"
            unit_sem_results.append(run_ttests(subset, label))

unit_sem_results = pd.concat(unit_sem_results, ignore_index=True)
unit_sem_results

df["C1/C2"] = df["C1/C2"].astype("category")
df["Semester"] = df["Semester"].astype("category")

formula = """
Score ~ Q("Understand Concepts") 
       + Q("Catch-up on Content") 
       + Q("Extra Practice")
       + Q("Assessments Help")
       + Q("Missed Lesson")
       + Q("For Confidence")
       + Q("Slow-paced Learning")
       + Q("New to Computing")
       + C(Q("C1/C2"))
       + C(Q("Semester"))
"""

model = smf.ols(formula=formula, data=df).fit()
print("OLS with Controls")
print(model.summary())


formula_simple = """
Score ~ Q("Understand Concepts") 
       + Q("Catch-up on Content") 
       + Q("Extra Practice")
       + Q("Assessments Help")
       + Q("Missed Lesson")
       + Q("For Confidence")
       + Q("Slow-paced Learning")
       + Q("New to Computing")
"""

model_simple = smf.ols(formula=formula_simple, data=df).fit()
print("\nOLS without Controls")
print(model_simple.summary())
# Compare the two models


print("\nPartial F-test comparing models with and without controls:")
anova_results = anova_lm(model_simple, model)
print(anova_results)
