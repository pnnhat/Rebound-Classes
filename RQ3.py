import pandas as pd
from scipy.stats import wilcoxon

df = pd.read_excel("RQ3.xlsx")
df_paired = df.copy()

# --- Compute change scores ---
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


# --- Build rows ---
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

# --- Combine into one table ---
summary_table = pd.DataFrame([row_content, row_assess])

summary_table
