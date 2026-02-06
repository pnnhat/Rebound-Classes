import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch

df = pd.read_excel("Project REBOUND Exit Survey_Jayden.xlsx")
df.head()

df = df[df["Finished"] == True].copy()
consent_col = [
    c for c in df.columns if c.startswith("Welcome to the REBOUND research study!")
][0]
df = df[df[consent_col] == "I consent to provide responses"].copy()
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


for col in df.columns:
    if col.startswith("Welcome to the REBOUND research study!"):
        drop.append(col)
df = df.drop(columns=drop, errors="ignore")

rename_map = {
    "Select the unit you taking this particular REBOUND class for?": "Unit",
    "How confident are you with the unit, now at the end of the semester? - The unit content": "Confidence Unit Content",
    "How confident are you with the unit, now at the end of the semester? - The assessments": "Confidence Assessments",
    "How confident are you with the unit, now at the end of the semester? - Meeting the learning outcomes & passing the unit": "Confidence Learning Outcomes",
    "What are your thoughts on the REBOUND classes at the end of the semester? - The Content Covered": "Thoughts Content Covered",
    "What are your thoughts on the REBOUND classes at the end of the semester? - The Facilitator": "Thoughts Facilitator",
    "What are your thoughts on the REBOUND classes at the end of the semester? - Structure of the Classes": "Thoughts Structure of the Classes",
    "On the scale of 1 to 5, rate your experience with the REBOUND classes - Ratiing for REBOUND Classes": "Rating REBOUND Classes",
    "How did Rebound classes help you with the unit?": "How Rebound Classes Helped",
    "What can we do to better the Rebound classes?": "Feedback",
}

df = df.rename(columns=rename_map)

confidence_map = {
    "Very Confident": 4,
    "Confident": 3,
    "Somewhat Confident": 2,
    "Not Confident at all": 1,
}

df["Confidence Unit Content"] = df["Confidence Unit Content"].map(confidence_map)
df["Confidence Assessments"] = df["Confidence Assessments"].map(confidence_map)
df["Confidence Learning Outcomes"] = df["Confidence Learning Outcomes"].map(
    confidence_map
)

thought_map = {
    "Very Confident": 4,
    "Confident": 3,
    "Somewhat Confident": 2,
    "Not Confident at all": 1,
}

thought_cols = [
    "Thoughts Content Covered",
    "Thoughts Facilitator",
    "Thoughts Structure of the Classes",
]

for col in thought_cols:
    df[col] = df[col].map(thought_map)

df["Rating REBOUND Classes"] = pd.to_numeric(
    df["Rating REBOUND Classes"], errors="coerce"
)

df["Recorded Date"] = pd.to_datetime(df["Recorded Date"])

df["Unit"] = df["Unit"].str.strip()

u1350 = "COMP1350 - Introduction to Database Design and Management"
u1000 = "COMP1000- Introduction to Computer Programming"

# COMP1000
df_1000 = df[df["Unit"] == u1000]
df_1000_s1 = df_1000[df_1000["Recorded Date"] <= "2025-06-30"]
df_1000_s2 = df_1000[
    (df_1000["Recorded Date"] >= "2025-07-01")
    & (df_1000["Recorded Date"] <= "2025-11-30")
]

# COMP1350
df_1350 = df[df["Unit"] == u1350]
df_1350_s1 = df_1350[df_1350["Recorded Date"] <= "2025-06-30"]
df_1350_s2 = df_1350[
    (df_1350["Recorded Date"] >= "2025-07-01")
    & (df_1350["Recorded Date"] <= "2025-11-30")
]

### Graph for overall
s1_comp1350 = len(df_1350_s1)
s2_comp1350 = len(df_1350_s2)

s1_comp1000 = len(df_1000_s1)
s2_comp1000 = len(df_1000_s2)

total_s1 = s1_comp1350 + s1_comp1000
total_s2 = s2_comp1350 + s2_comp1000

pct_s1_1350 = (s1_comp1350 / total_s1) * 100
pct_s1_1000 = (s1_comp1000 / total_s1) * 100

pct_s2_1350 = (s2_comp1350 / total_s2) * 100
pct_s2_1000 = (s2_comp1000 / total_s2) * 100
sessions = [f"Session 1 (n = {total_s1})", f"Session 2 (n = {total_s2})"]

comp1000_values = [s1_comp1000, s2_comp1000]
comp1350_values = [s1_comp1350, s2_comp1350]

pct_1000 = [pct_s1_1000, pct_s2_1000]
pct_1350 = [pct_s1_1350, pct_s2_1350]

x = np.arange(len(sessions))
width = 0.36

plt.figure(figsize=(10, 6))
bars_1000 = plt.bar(
    x - width / 2, comp1000_values, width, label="COMP1000", color="blue"
)
bars_1350 = plt.bar(
    x + width / 2, comp1350_values, width, label="COMP1350", color="skyblue"
)


def add_labels(bars, pcts):
    for i, bar in enumerate(bars):
        h = int(bar.get_height())
        plt.annotate(
            f"n = {h} ({pcts[i]:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            clip_on=False,
        )


add_labels(bars_1000, pct_1000)
add_labels(bars_1350, pct_1350)

plt.xticks(x, sessions)
plt.ylabel("Number of Students")
plt.legend(title="Unit")

ax = plt.gca()
ymax = max(comp1000_values + comp1350_values)
ax.set_ylim(0, ymax + 1)
ax.set_yticks(np.arange(0, ymax + 2, 1))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{int(y)}"))

plt.tight_layout()
plt.show()


## Confidence Table
confidence_levels = {
    1: "Not Confident (n)",
    2: "Somewhat Confident (n)",
    3: "Confident (n)",
    4: "Very Confident (n)",
}

confidence_components = {
    "Unit Content": "Confidence Unit Content",
    "Assessments": "Confidence Assessments",
    "Learning Outcomes": "Confidence Learning Outcomes",
}


def build_confidence_table(df):
    rows = []

    subs = [
        ("Session 1", "COMP1000", df_1000_s1),
        ("Session 1", "COMP1350", df_1350_s1),
        ("Session 2", "COMP1000", df_1000_s2),
        ("Session 2", "COMP1350", df_1350_s2),
    ]

    for session, unit, sub in subs:
        for component_name, col in confidence_components.items():
            row = {
                "Session": session,
                "Unit": unit,
                "Component": component_name,
            }

            for lvl, label in confidence_levels.items():
                row[label] = int((sub[col] == lvl).sum())

            rows.append(row)

    return pd.DataFrame(rows)


confidence_table = build_confidence_table(df)
confidence_table

## Thoughts Table
thought_levels = {
    1: "Not Helpful (n)",
    2: "Somewhat Helpful (n)",
    3: "Fairly Helpful (n)",
    4: "Very Helpful (n)",
}

thought_components = {
    "Content Covered": "Thoughts Content Covered",
    "Facilitator": "Thoughts Facilitator",
    "Structure of the Classes": "Thoughts Structure of the Classes",
}


def build_thoughts_table(df):
    rows = []

    subs = [
        ("Session 1", "COMP1000", df_1000_s1),
        ("Session 1", "COMP1350", df_1350_s1),
        ("Session 2", "COMP1000", df_1000_s2),
        ("Session 2", "COMP1350", df_1350_s2),
    ]

    for session, unit, sub in subs:
        for component_name, col in thought_components.items():
            row = {
                "Session": session,
                "Unit": unit,
                "Component": component_name,
            }

            for lvl, label in thought_levels.items():
                row[label] = int((sub[col] == lvl).sum())

            rows.append(row)

    return pd.DataFrame(rows)


thoughts_table = build_thoughts_table(df)
thoughts_table


# Rating Plot
rating_levels = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]


def build_rating_table(
    df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2, rating_col="Rating REBOUND Classes"
):
    rows = []

    subs = [
        ("Session 1", "COMP1000", df_1000_s1),
        ("Session 1", "COMP1350", df_1350_s1),
        ("Session 2", "COMP1000", df_1000_s2),
        ("Session 2", "COMP1350", df_1350_s2),
    ]

    rating_levels = [1, 2, 3, 4, 5]

    for session, unit, sub in subs:
        s = pd.to_numeric(sub[rating_col], errors="coerce").dropna()
        s = s.round().astype(int)
        s = s[s.isin(rating_levels)]

        row = {
            "Session": session,
            "Unit": unit,
        }

        for lvl in rating_levels:
            row[f"{lvl} (n)"] = int((s == lvl).sum())

        rows.append(row)

    return pd.DataFrame(rows)


rating_table = build_rating_table(df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2)
rating_table


## Expectations table
df_expect = pd.read_excel("exit_survey_cleaned.xlsx", sheet_name="Expectation Theme")

df_expect.columns = (
    df_expect.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
)
df_expect["Recorded Date"] = pd.to_datetime(df_expect["Recorded Date"], errors="coerce")

df_s1 = df_expect[df_expect["Recorded Date"] <= pd.Timestamp("2025-06-30 23:59:59")]
df_s2 = df_expect[
    (df_expect["Recorded Date"] >= pd.Timestamp("2025-07-01"))
    & (df_expect["Recorded Date"] <= pd.Timestamp("2025-11-30 23:59:59"))
]

u1000 = "COMP1000- Introduction to Computer Programming"
u1350 = "COMP1350 - Introduction to Database Design and Management"

df_1000_s1 = df_s1[df_s1["Unit"] == u1000]
df_1350_s1 = df_s1[df_s1["Unit"] == u1350]
df_1000_s2 = df_s2[df_s2["Unit"] == u1000]
df_1350_s2 = df_s2[df_s2["Unit"] == u1350]

theme_cols = [
    "Expectation Theme 1",
    "Expectation Theme 2",
    "Expectation Theme 3",
    "Expectation Theme 4",
    "Expectation Theme 5",
]
theme_map = [
    "Understand/Clarify Concepts",
    "Catch Up",
    "Practice",
    "Assessments Help",
    "No Comments",
]
theme_colors = ["#6baed6", "#9ecae1", "#74c476", "#bcbddc", "#fdd0a2"]


def normalize_theme_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


def build_expectation_table(df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2):
    rows = []
    subs = [
        ("Session 1", "COMP1000", df_1000_s1),
        ("Session 1", "COMP1350", df_1350_s1),
        ("Session 2", "COMP1000", df_1000_s2),
        ("Session 2", "COMP1350", df_1350_s2),
    ]

    for session, unit, sub in subs:
        tmp = sub.copy()
        for c in theme_cols:
            if c not in tmp.columns:
                tmp[c] = pd.NA
            tmp[c] = tmp[c].map(normalize_theme_cell)

        row = {
            "Session": session,
            "Unit": unit,
        }
        for theme_label in theme_map:
            row[f"{theme_label} (n)"] = int(
                (tmp[theme_cols] == theme_label).sum().sum()
            )

        rows.append(row)

    return pd.DataFrame(rows)


expect_table = build_expectation_table(df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2)
expect_table


## Motivation table
df_expect = pd.read_excel("exit_survey_cleaned.xlsx", sheet_name="Motivation Theme")

df_expect.columns = (
    df_expect.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
)
df_expect["Recorded Date"] = pd.to_datetime(df_expect["Recorded Date"], errors="coerce")

df_s1 = df_expect[df_expect["Recorded Date"] <= pd.Timestamp("2025-06-30 23:59:59")]
df_s2 = df_expect[
    (df_expect["Recorded Date"] >= pd.Timestamp("2025-07-01"))
    & (df_expect["Recorded Date"] <= pd.Timestamp("2025-11-30 23:59:59"))
]

u1000 = "COMP1000- Introduction to Computer Programming"
u1350 = "COMP1350 - Introduction to Database Design and Management"

df_1000_s1 = df_s1[df_s1["Unit"] == u1000]
df_1350_s1 = df_s1[df_s1["Unit"] == u1350]
df_1000_s2 = df_s2[df_s2["Unit"] == u1000]
df_1350_s2 = df_s2[df_s2["Unit"] == u1350]

theme_cols = [
    "Motivation Theme 1",
    "Motivation Theme 2",
    "Motivation Theme 3",
    "Motivation Theme 4",
    "Motivation Theme 5",
]
theme_map = [
    "Lack of Prior Background",
    "Falling Behind",
    "Confidence/Anxiety-Related Motivation",
    "Other",
    "No Comments",
]
theme_colors = ["#6baed6", "#9ecae1", "#74c476", "#bcbddc", "#fdd0a2"]


def normalize_theme_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


def build_motivation_table(df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2):
    rows = []
    subs = [
        ("Session 1", "COMP1000", df_1000_s1),
        ("Session 1", "COMP1350", df_1350_s1),
        ("Session 2", "COMP1000", df_1000_s2),
        ("Session 2", "COMP1350", df_1350_s2),
    ]

    for session, unit, sub in subs:
        tmp = sub.copy()
        for c in theme_cols:
            if c not in tmp.columns:
                tmp[c] = pd.NA
            tmp[c] = tmp[c].map(normalize_theme_cell)

        row = {
            "Session": session,
            "Unit": unit,
        }
        for theme_label in theme_map:
            row[f"{theme_label} (n)"] = int(
                (tmp[theme_cols] == theme_label).sum().sum()
            )

        rows.append(row)

    return pd.DataFrame(rows)


motivation_table = build_motivation_table(
    df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2
)
motivation_table


## Suggestion table
df_expect = pd.read_excel("exit_survey_cleaned.xlsx", sheet_name="Suggestion Theme")

df_expect.columns = (
    df_expect.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
)
df_expect["Recorded Date"] = pd.to_datetime(df_expect["Recorded Date"], errors="coerce")

df_s1 = df_expect[df_expect["Recorded Date"] <= pd.Timestamp("2025-06-30 23:59:59")]
df_s2 = df_expect[
    (df_expect["Recorded Date"] >= pd.Timestamp("2025-07-01"))
    & (df_expect["Recorded Date"] <= pd.Timestamp("2025-11-30 23:59:59"))
]

u1000 = "COMP1000- Introduction to Computer Programming"
u1350 = "COMP1350 - Introduction to Database Design and Management"

df_1000_s1 = df_s1[df_s1["Unit"] == u1000]
df_1350_s1 = df_s1[df_s1["Unit"] == u1350]
df_1000_s2 = df_s2[df_s2["Unit"] == u1000]
df_1350_s2 = df_s2[df_s2["Unit"] == u1350]

theme_cols = [
    "Suggestion Theme 1",
    "Suggestion Theme 2",
    "Suggestion Theme 3",
    "Suggestion Theme 4",
]
theme_map = [
    "More Teaching Support",
    "Pace Adjustment",
    "Session Structure",
    "No Comments",
]
theme_colors = ["#6baed6", "#9ecae1", "#74c476", "#fdd0a2"]


def normalize_theme_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


def build_suggestion_table(df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2):
    rows = []
    subs = [
        ("Session 1", "COMP1000", df_1000_s1),
        ("Session 1", "COMP1350", df_1350_s1),
        ("Session 2", "COMP1000", df_1000_s2),
        ("Session 2", "COMP1350", df_1350_s2),
    ]

    for session, unit, sub in subs:
        tmp = sub.copy()
        for c in theme_cols:
            if c not in tmp.columns:
                tmp[c] = pd.NA
            tmp[c] = tmp[c].map(normalize_theme_cell)

        row = {
            "Session": session,
            "Unit": unit,
        }
        for theme_label in theme_map:
            row[f"{theme_label} (n)"] = int(
                (tmp[theme_cols] == theme_label).sum().sum()
            )

        rows.append(row)

    return pd.DataFrame(rows)


suggestion_table = build_suggestion_table(
    df_1000_s1, df_1350_s1, df_1000_s2, df_1350_s2
)
suggestion_table
