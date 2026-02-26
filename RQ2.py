import pandas as pd
import numpy as np
from scipy.stats import spearmanr

df = pd.read_excel("RQ2.xlsx")

df_unique = df.drop_duplicates(subset=["Participant ID", "Semester"])
df = df_unique.copy()
df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
df["Confidence Combined"] = df[
    ["Confidence Unit Content", "Confidence Assessments"]
].mean(axis=1)


def build_summary(data, label):
    if len(data) < 3:
        return None

    rho_unit, p_unit = spearmanr(data["Confidence Unit Content"], data["Score"])
    rho_assess, p_assess = spearmanr(data["Confidence Assessments"], data["Score"])
    rho_combined, p_combined = spearmanr(data["Confidence Combined"], data["Score"])

    rho_content, p_content = spearmanr(
        data["Helpfulness Content Covered"], data["Score"]
    )
    rho_fac, p_fac = spearmanr(data["Helpfulness Facilitator"], data["Score"])
    rho_struct, p_struct = spearmanr(
        data["Helpfulness Structure of the Classes"], data["Score"]
    )
    rho_help_combined, p_help_combined = spearmanr(
        data[
            [
                "Helpfulness Content Covered",
                "Helpfulness Facilitator",
                "Helpfulness Structure of the Classes",
            ]
        ].mean(axis=1),
        data["Score"],
    )

    return {
        "Group": label,
        "n": len(data),
        "Mean Score": round(data["Score"].mean(), 1),
        "SD Score": round(data["Score"].std(), 1),
        "Median Score": round(data["Score"].median(), 1),
        "Spearman ρ (Confidence - Unit Content)": round(rho_unit, 3),
        "p-value (Confidence - Unit Content)": round(p_unit, 4),
        "Spearman ρ (Confidence - Assessments)": round(rho_assess, 3),
        "p-value (Confidence - Assessments)": round(p_assess, 4),
        "Spearman ρ (Confidence - Combined)": round(rho_combined, 3),
        "p-value (Confidence - Combined)": round(p_combined, 4),
        "Spearman ρ (Helpfulness - Content Covered)": round(rho_content, 3),
        "p-value (Helpfulness - Content Covered)": round(p_content, 4),
        "Spearman ρ (Helpfulness - Facilitator)": round(rho_fac, 3),
        "p-value (Helpfulness - Facilitator)": round(p_fac, 4),
        "Spearman ρ (Helpfulness - Structure of the Classes)": round(rho_struct, 3),
        "p-value (Helpfulness - Structure of the Classes)": round(p_struct, 4),
        "Spearman ρ (Helpfulness - Combined)": round(rho_help_combined, 3),
        "p-value (Helpfulness - Combined)": round(p_help_combined, 4),
    }


rows = []

rows.append(build_summary(df, "Overall"))
for unit in ["C1", "C2"]:
    subset = df[df["C1/C2"] == unit]
    rows.append(build_summary(subset, unit))

for sem in ["S1", "S2"]:
    subset = df[df["Semester"] == sem]
    rows.append(build_summary(subset, sem))
order = [
    ("C1", "S1"),
    ("C2", "S1"),
    ("C1", "S2"),
    ("C2", "S2"),
]

for unit, sem in order:
    subset = df[(df["C1/C2"] == unit) & (df["Semester"] == sem)]
    if len(subset) > 2:
        rows.append(build_summary(subset, f"{unit} {sem}"))

big_table = pd.DataFrame([r for r in rows if r is not None])
big_table

confidence_cols = [
    "Group",
    "n",
    "Mean Score",
    "SD Score",
    "Median Score",
    "Spearman ρ (Confidence - Unit Content)",
    "p-value (Confidence - Unit Content)",
    "Spearman ρ (Confidence - Assessments)",
    "p-value (Confidence - Assessments)",
    "Spearman ρ (Confidence - Combined)",
    "p-value (Confidence - Combined)",
]

confidence_table = big_table[confidence_cols]

confidence_table.to_excel("RQ2_Confidence.xlsx", index=False)

helpfulness_cols = [
    "Group",
    "n",
    "Mean Score",
    "SD Score",
    "Median Score",
    "Spearman ρ (Helpfulness - Content Covered)",
    "p-value (Helpfulness - Content Covered)",
    "Spearman ρ (Helpfulness - Facilitator)",
    "p-value (Helpfulness - Facilitator)",
    "Spearman ρ (Helpfulness - Structure of the Classes)",
    "p-value (Helpfulness - Structure of the Classes)",
    "Spearman ρ (Helpfulness - Combined)",
    "p-value (Helpfulness - Combined)",
]

helpfulness_table = big_table[helpfulness_cols]

helpfulness_table.to_excel("RQ2_Helpfulness.xlsx", index=False)
