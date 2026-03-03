import pandas as pd
from scipy.stats import wilcoxon

df = pd.read_excel("RQ3.xlsx")
df_paired = df.copy()

df_paired["Delta_Content"] = (
    df_paired["Confidence Unit Content_Exit"]
    - df_paired["Confidence Unit Content_Entry"]
)

df_paired["Delta_Assessments"] = (
    df_paired["Confidence Assessments_Exit"] - df_paired["Confidence Assessments_Entry"]
)


# --- Function to build summary row ---
def build_summary(entry_col, exit_col, delta_col, label):
    mean_entry = df_paired[entry_col].mean()
    mean_exit = df_paired[exit_col].mean()
    mean_delta = df_paired[delta_col].mean()

    improved = (df_paired[delta_col] > 0).sum()
    unchanged = (df_paired[delta_col] == 0).sum()
    decreased = (df_paired[delta_col] < 0).sum()

    return {
        "Measure": label,
        "N": len(df_paired),
        "Mean Entry": round(mean_entry, 2),
        "Mean Exit": round(mean_exit, 2),
        "Mean Change (Δ)": round(mean_delta, 2),
        "Improved (n)": improved,
        "Unchanged (n)": unchanged,
        "Decreased (n)": decreased,
    }


row_content = build_summary(
    "Confidence Unit Content_Entry",
    "Confidence Unit Content_Exit",
    "Delta_Content",
    "Confidence in Unit Content",
)

row_assess = build_summary(
    "Confidence Assessments_Entry",
    "Confidence Assessments_Exit",
    "Delta_Assessments",
    "Confidence in Assessments",
)
summary_table = pd.DataFrame([row_content, row_assess])

summary_table


df_thoughts = df.copy()

df_thoughts["Delta_Content"] = (
    df_thoughts["Thoughts Content Covered_Exit"]
    - df_thoughts["Thoughts Content Covered_Entry"]
)

df_thoughts["Delta_Facilitator"] = (
    df_thoughts["Thoughts Facilitator_Exit"] - df_thoughts["Thoughts Facilitator_Entry"]
)

df_thoughts["Delta_Structure"] = (
    df_thoughts["Thoughts Structure of the Classes_Exit"]
    - df_thoughts["Thoughts Structure of the Classes_Entry"]
)


def build_summary(entry_col, exit_col, delta_col, label):
    return {
        "Measure": label,
        "N": len(df_thoughts),
        "Mean Entry": round(df_thoughts[entry_col].mean(), 2),
        "Mean Exit": round(df_thoughts[exit_col].mean(), 2),
        "Mean Change (Δ)": round(df_thoughts[delta_col].mean(), 2),
        "Improved (n)": (df_thoughts[delta_col] > 0).sum(),
        "Unchanged (n)": (df_thoughts[delta_col] == 0).sum(),
        "Decreased (n)": (df_thoughts[delta_col] < 0).sum(),
    }


# --- Build rows ---
rows = [
    build_summary(
        "Thoughts Content Covered_Entry",
        "Thoughts Content Covered_Exit",
        "Delta_Content",
        "Content Covered",
    ),
    build_summary(
        "Thoughts Facilitator_Entry",
        "Thoughts Facilitator_Exit",
        "Delta_Facilitator",
        "Facilitator",
    ),
    build_summary(
        "Thoughts Structure of the Classes_Entry",
        "Thoughts Structure of the Classes_Exit",
        "Delta_Structure",
        "Structure of the Classes",
    ),
]

summary_thoughts = pd.DataFrame(rows)

summary_thoughts
