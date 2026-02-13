import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
from matplotlib.patches import Patch

df = pd.read_excel("EntrySurvey_JaydenUpdated.xlsx")
df.head()

df = df[df["Finished"] == True].copy()
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

rename_map = {
    "Select the unit you taking this particular REBOUND class for?": "Unit",
    "Are you a first-generation student to attend university? (First-generation student meaning you/ your siblings are the first ones to attend university)": "First Generation Student",
    "Are you a repeating student?": "Repeating Student",
    "What challenges did you face in your first attempt at the unit?\nPlease choose everything that applies. If you have other reasons not on the list, please list them in the other option.": "Challenges Faced",
    "How confident are you with the unit? - The Unit Content": "Confidence Unit Content",
    "How confident are you with the unit? - The Assessments": "Confidence Assessments",
    "What are your thoughts on the REBOUND classes so far? - The Content Covered": "Thoughts Content Covered",
    "What are your thoughts on the REBOUND classes so far? - The Facilitator": "Thoughts Facilitator",
    "What are your thoughts on the REBOUND classes so far? - Structure of the Classes": "Thoughts Structure of the Classes",
    "What are your expectations of the REBOUND classes? Why did you choose to attend them?": "Expectations of REBOUND Classes",
    "Can you give us feedback about the REBOUND classes, please? (What's working for you? How can these REBOUND classes be better? How can we improve?)": "Feedback",
    "Please enter your StudentID": "StudentID",
}

df = df.rename(columns=rename_map)

## Map Yes/No to 1/0
map = {"Yes": 1, "No": 0}
df["First Generation Student"] = df["First Generation Student"].map(map)
df["Repeating Student"] = df["Repeating Student"].map(map)

confidence = {
    "Very Confident": 4,
    "Confident": 3,
    "Somewhat Confident": 2,
    "Not Confident at all": 1,
}
df["Confidence Unit Content"] = df["Confidence Unit Content"].map(confidence)
df["Confidence Assessments"] = df["Confidence Assessments"].map(confidence)
thought = {
    "Very Helpful": 4,
    "Fairly helpful": 3,
    "Somewhat helpful": 2,
    "Not helpful at all": 1,
}
thought_cols = [
    "Thoughts Content Covered",
    "Thoughts Facilitator",
    "Thoughts Structure of the Classes",
]

for col in thought_cols:
    df[col] = df[col].map(thought)


df["Recorded Date"] = pd.to_datetime(df["Recorded Date"])
df_s1 = df[df["Recorded Date"] <= "2025-06-30"]
df_s2 = df[
    (df["Recorded Date"] >= "2025-07-01") & (df["Recorded Date"] <= "2025-11-30")
]

## For comp1350 s1 s2
df_1350 = df[df["Unit"] == "COMP1350 - Introduction to Database Design and Management"]
df_1350_s1 = df_s1[
    df_s1["Unit"] == "COMP1350 - Introduction to Database Design and Management"
]
df_1350_s2 = df_s2[
    df_s2["Unit"] == "COMP1350 - Introduction to Database Design and Management"
]

## For comp1000 s1 s2
df_1000 = df[df["Unit"] == "COMP1000- Introduction to Computer Programming"]
df_1000_s1 = df_s1[df_s1["Unit"] == "COMP1000- Introduction to Computer Programming"]
df_1000_s2 = df_s2[df_s2["Unit"] == "COMP1000- Introduction to Computer Programming"]

## Challenge faced mapping
challenge_map = {
    "The content of the unit was overwhelming": "Unit Content",
    "The assessments were too difficult to attempt": "Unit Content",
    "I wish I had more time to complete the assessments": "Unit Content",
    "I couldn't understand the lecturer": "Staff Involved in the Unit",
    "I couldn't understand the workshop instructor": "Staff Involved in the Unit",
    "The staff weren't approachable": "Staff Involved in the Unit",
    "It was my first semester, everything was overwhelming": "Other",
    "I enrolled late and couldn't catch up with the contents of the unit": "Other",
    "I didn't understand how to manage my time better": "Other",
    "I had personal issues": "Other",
}

df_challenge = df[(df["Repeating Student"] == 1)].copy()


def extract(text):
    if pd.isna(text):
        return []
    return [t.strip() for t in str(text).split(",")]


df_challenge["Challenge_List"] = df_challenge["Challenges Faced"].apply(extract)
df_challenge_final = df_challenge.explode("Challenge_List")

df_challenge_final = df_challenge_final.rename(columns={"Challenge_List": "Challenge"})
df_challenge_final["Category"] = (
    df_challenge_final["Challenge"].map(challenge_map).fillna("Other")
)


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

for i, bar in enumerate(bars_1000):
    count = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        count + 0.3,
        f"n = {count} ({pct_1000[i]:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=10,
    )

for i, bar in enumerate(bars_1350):
    count = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        count + 0.3,
        f"n = {int(count)} ({pct_1350[i]:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.xticks(x, sessions)
plt.ylabel("Number of Students")
plt.legend(title="Unit")
plt.tight_layout()
plt.show()


# First-generation stacked bar chart
def first_gen_counts(d):
    yes = int((d["First Generation Student"] == 1).sum())
    no = int((d["First Generation Student"] == 0).sum())
    total = yes + no
    return yes, no, total


yes_1000_s1, no_1000_s1, total_1000_s1 = first_gen_counts(df_1000_s1)
yes_1350_s1, no_1350_s1, total_1350_s1 = first_gen_counts(df_1350_s1)

yes_1000_s2, no_1000_s2, total_1000_s2 = first_gen_counts(df_1000_s2)
yes_1350_s2, no_1350_s2, total_1350_s2 = first_gen_counts(df_1350_s2)

total_s1 = total_1000_s1 + total_1350_s1
total_s2 = total_1000_s2 + total_1350_s2

sessions = [f"Session 1 (n = {total_s1})", f"Session 2 (n = {total_s2})"]
x = np.arange(len(sessions))
width = 0.36
gap = 0.01
offset = width / 2 + gap

comp1000_no = [no_1000_s1, no_1000_s2]
comp1000_yes = [yes_1000_s1, yes_1000_s2]
comp1000_total = [total_1000_s1, total_1000_s2]

comp1350_no = [no_1350_s1, no_1350_s2]
comp1350_yes = [yes_1350_s1, yes_1350_s2]
comp1350_total = [total_1350_s1, total_1350_s2]

plt.figure(figsize=(10, 6))
bars_1000_no = plt.bar(
    x - offset, comp1000_no, width, color="blue", edgecolor="white", label="COMP1000"
)
bars_1350_no = plt.bar(
    x + offset, comp1350_no, width, color="skyblue", edgecolor="white", label="COMP1350"
)

bars_1000_yes = plt.bar(
    x - offset,
    comp1000_yes,
    width,
    bottom=comp1000_no,
    color="blue",
    edgecolor="white",
    hatch="///",
)
bars_1350_yes = plt.bar(
    x + offset,
    comp1350_yes,
    width,
    bottom=comp1350_no,
    color="skyblue",
    edgecolor="white",
    hatch="///",
)


def annotate_inside(bars_no, bars_yes, no_counts, yes_counts):
    for i in range(len(bars_no)):
        if no_counts[i] > 0:
            y_no = bars_no[i].get_height() / 2
            plt.text(
                bars_no[i].get_x() + bars_no[i].get_width() / 2,
                y_no,
                f"No (n = {no_counts[i]})",
                ha="center",
                va="center",
                fontsize=9,
                color="black",
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.25"
                ),
            )
        if yes_counts[i] > 0:
            y_yes = bars_no[i].get_height() + bars_yes[i].get_height() / 2
            plt.text(
                bars_yes[i].get_x() + bars_yes[i].get_width() / 2,
                y_yes,
                f"Yes (n = {yes_counts[i]})",
                ha="center",
                va="center",
                fontsize=9,
                color="black",
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.25"
                ),
            )


annotate_inside(bars_1000_no, bars_1000_yes, comp1000_no, comp1000_yes)
annotate_inside(bars_1350_no, bars_1350_yes, comp1350_no, comp1350_yes)

plt.xticks(x, sessions)
plt.ylabel("Number of Students")

unit_legend = plt.legend(title="Unit", loc="upper right")
plt.gca().add_artist(unit_legend)

fg_legend = [
    Patch(facecolor="white", edgecolor="black", label="Yes", hatch="///"),
    Patch(facecolor="white", edgecolor="black", label="No"),
]
plt.legend(
    handles=fg_legend,
    title="First Generation",
    loc="upper right",
    bbox_to_anchor=(1.0, 0.78),
)

plt.tight_layout()
plt.show()


# Repeating students stacked bar chart
def first_gen_counts(d):
    yes = int((d["Repeating Student"] == 1).sum())
    no = int((d["Repeating Student"] == 0).sum())
    total = yes + no
    return yes, no, total


yes_1000_s1, no_1000_s1, total_1000_s1 = first_gen_counts(df_1000_s1)
yes_1350_s1, no_1350_s1, total_1350_s1 = first_gen_counts(df_1350_s1)

yes_1000_s2, no_1000_s2, total_1000_s2 = first_gen_counts(df_1000_s2)
yes_1350_s2, no_1350_s2, total_1350_s2 = first_gen_counts(df_1350_s2)

total_s1 = total_1000_s1 + total_1350_s1
total_s2 = total_1000_s2 + total_1350_s2

sessions = [f"Session 1 (n = {total_s1})", f"Session 2 (n = {total_s2})"]
x = np.arange(len(sessions))
width = 0.36
gap = 0.01
offset = width / 2 + gap

comp1000_no = [no_1000_s1, no_1000_s2]
comp1000_yes = [yes_1000_s1, yes_1000_s2]
comp1000_total = [total_1000_s1, total_1000_s2]

comp1350_no = [no_1350_s1, no_1350_s2]
comp1350_yes = [yes_1350_s1, yes_1350_s2]
comp1350_total = [total_1350_s1, total_1350_s2]

plt.figure(figsize=(10, 6))
bars_1000_no = plt.bar(
    x - offset, comp1000_no, width, color="blue", edgecolor="white", label="COMP1000"
)
bars_1350_no = plt.bar(
    x + offset, comp1350_no, width, color="skyblue", edgecolor="white", label="COMP1350"
)

bars_1000_yes = plt.bar(
    x - offset,
    comp1000_yes,
    width,
    bottom=comp1000_no,
    color="blue",
    edgecolor="white",
    hatch="///",
)
bars_1350_yes = plt.bar(
    x + offset,
    comp1350_yes,
    width,
    bottom=comp1350_no,
    color="skyblue",
    edgecolor="white",
    hatch="///",
)


def annotate_inside(bars_no, bars_yes, no_counts, yes_counts):
    for i in range(len(bars_no)):
        if no_counts[i] > 0:
            y_no = bars_no[i].get_height() / 2
            plt.text(
                bars_no[i].get_x() + bars_no[i].get_width() / 2,
                y_no,
                f"No (n = {no_counts[i]})",
                ha="center",
                va="center",
                fontsize=9,
                color="black",
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.25"
                ),
            )
        if yes_counts[i] > 0:
            y_yes = bars_no[i].get_height() + bars_yes[i].get_height() / 2
            plt.text(
                bars_yes[i].get_x() + bars_yes[i].get_width() / 2,
                y_yes,
                f"Yes (n = {yes_counts[i]})",
                ha="center",
                va="center",
                fontsize=9,
                color="black",
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.25"
                ),
            )


annotate_inside(bars_1000_no, bars_1000_yes, comp1000_no, comp1000_yes)
annotate_inside(bars_1350_no, bars_1350_yes, comp1350_no, comp1350_yes)

plt.xticks(x, sessions)
plt.ylabel("Number of Students")

unit_legend = plt.legend(title="Unit", loc="upper right")
plt.gca().add_artist(unit_legend)

fg_legend = [
    Patch(facecolor="white", edgecolor="black", label="Yes", hatch="///"),
    Patch(facecolor="white", edgecolor="black", label="No"),
]
plt.legend(
    handles=fg_legend,
    title="Repeating",
    loc="upper right",
    bbox_to_anchor=(1.0, 0.78),
)

plt.tight_layout()
plt.show()

## Challenge categories stacked bar chart
order = ["Unit Content", "Staff Involved in the Unit", "Other"]
colors = ["#c6dbef", "#6baed6", "#2171b5"]

u1350 = "COMP1350 - Introduction to Database Design and Management"
u1000 = "COMP1000- Introduction to Computer Programming"


def session_1(df):
    return df[df["Recorded Date"] <= "2025-06-30"]


def session_2(df):
    return df[
        (df["Recorded Date"] >= "2025-07-01") & (df["Recorded Date"] <= "2025-11-30")
    ]


def compute_counts_and_pct(sub):
    counts = sub["Category"].value_counts().reindex(order, fill_value=0)
    total = int(counts.sum())
    pct = (counts / total * 100).round(1)
    return counts, pct, total


rows = []
index_labels = [
    "Session 1 – COMP1000",
    "Session 1 – COMP1350",
    "Session 2 – COMP1000",
    "Session 2 – COMP1350",
]

subs = [
    session_1(df_challenge_final[df_challenge_final["Unit"] == u1000]),
    session_1(df_challenge_final[df_challenge_final["Unit"] == u1350]),
    session_2(df_challenge_final[df_challenge_final["Unit"] == u1000]),
    session_2(df_challenge_final[df_challenge_final["Unit"] == u1350]),
]

for sub in subs:
    counts, pct, total = compute_counts_and_pct(sub)
    row = {}
    for cat in order:
        row[f"{cat}_n"] = int(counts[cat])
        row[f"{cat}_pct"] = float(pct[cat])
    row["Total_n"] = total
    rows.append(row)

plot_df = pd.DataFrame(rows, index=index_labels)

y_labels = [f"{idx}\n(n = {int(plot_df.loc[idx, 'Total_n'])})" for idx in plot_df.index]

plt.figure(figsize=(12, 6))

left = [0] * len(plot_df)
y_pos = list(range(len(plot_df)))

for i, cat in enumerate(order):
    vals = plot_df[f"{cat}_pct"]
    bars = plt.barh(y_pos, vals, left=left, color=colors[i], label=cat)
    for j, (bar, val) in enumerate(zip(bars, vals)):
        n_val = int(plot_df.iloc[j][f"{cat}_n"])
        if n_val > 0:
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + bar.get_height() / 2,
                f"n={n_val} ({val:.1f}%)",
                ha="center",
                va="center",
                fontsize=9,
                color="black",
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.25"
                ),
            )

    left = [l + v for l, v in zip(left, vals)]

plt.xlabel("Percentage")
plt.xlim(0, 100)
plt.legend(title="Challenge Category", bbox_to_anchor=(1.05, 1), loc="upper left")

ax = plt.gca()


ax.set_yticks(y_pos)
ax.set_yticklabels(y_labels)
for label in ax.get_yticklabels():
    label.set_multialignment("center")
ax.invert_yaxis()
plt.tight_layout()
plt.show()

# Challenge table
order = ["Unit Content", "Staff Involved in the Unit", "Other"]

u1350 = "COMP1350 - Introduction to Database Design and Management"
u1000 = "COMP1000- Introduction to Computer Programming"


def session_1(d):
    return d[d["Recorded Date"] <= "2025-06-30"]


def session_2(d):
    return d[
        (d["Recorded Date"] >= "2025-07-01") & (d["Recorded Date"] <= "2025-11-30")
    ]


def compute_counts(sub):
    return sub["Category"].value_counts().reindex(order, fill_value=0)


subs = [
    (
        "Session 1",
        "COMP1000",
        session_1(df_challenge_final[df_challenge_final["Unit"] == u1000]),
    ),
    (
        "Session 1",
        "COMP1350",
        session_1(df_challenge_final[df_challenge_final["Unit"] == u1350]),
    ),
    (
        "Session 2",
        "COMP1000",
        session_2(df_challenge_final[df_challenge_final["Unit"] == u1000]),
    ),
    (
        "Session 2",
        "COMP1350",
        session_2(df_challenge_final[df_challenge_final["Unit"] == u1350]),
    ),
]

rows = []
for sess, unit, sub in subs:
    counts = compute_counts(sub)
    rows.append(
        {
            "Session": sess,
            "Unit": unit,
            "Unit Content (n)": int(counts["Unit Content"]),
            "Staff Involved (n)": int(counts["Staff Involved in the Unit"]),
            "Other (n)": int(counts["Other"]),
        }
    )

challenge_table = pd.DataFrame(rows)
challenge_table

## Build confidence table
confidence_levels = {
    1: "Not Confident (n)",
    2: "Somewhat Confident (n)",
    3: "Confident (n)",
    4: "Very Confident (n)",
}

confidence_components = {
    "Unit Content": "Confidence Unit Content",
    "Assessments": "Confidence Assessments",
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

# Perceptions table
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

## Expectations graph
df_expect = pd.read_excel("entry_survey_cleaned.xlsx", sheet_name="Expectation Theme")

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
    "Catch Up Content",
    "Extra Practice",
    "Assessments Help",
    "Unanswered",
]
theme_colors = ["#6baed6", "#9ecae1", "#74c476", "#bcbddc", "#fdd0a2"]


def normalize_theme_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


def theme_counts(sub):
    tmp = sub.copy()
    for c in theme_cols:
        if c not in tmp.columns:
            tmp[c] = pd.NA
        tmp[c] = tmp[c].map(normalize_theme_cell)

    out = []
    for t in theme_map:
        out.append(int((tmp[theme_cols] == t).sum().sum()))
    return np.array(out, dtype=int)


c_1000_s1 = theme_counts(df_1000_s1)
c_1000_s2 = theme_counts(df_1000_s2)
c_1350_s1 = theme_counts(df_1350_s1)
c_1350_s2 = theme_counts(df_1350_s2)

comp1000 = np.vstack([c_1000_s1, c_1000_s2]).T
comp1350 = np.vstack([c_1350_s1, c_1350_s2]).T

total_s1 = int(c_1000_s1.sum() + c_1350_s1.sum())
total_s2 = int(c_1000_s2.sum() + c_1350_s2.sum())

sessions = [f"Session 1 (n ={total_s1})", f"Session 2 (n ={total_s2})"]

x = np.arange(len(sessions))
width = 0.36
gap = 0.01
offset = width / 2 + gap

fig, ax = plt.subplots(figsize=(11, 6))

bottom_1000 = np.zeros(len(sessions))
bottom_1350 = np.zeros(len(sessions))

theme_handles = []

for i, (lab, col) in enumerate(zip(theme_map, theme_colors)):
    b1 = ax.bar(
        x - offset, comp1000[i], width, bottom=bottom_1000, color=col, edgecolor="white"
    )
    b2 = ax.bar(
        x + offset,
        comp1350[i],
        width,
        bottom=bottom_1350,
        color=col,
        edgecolor="white",
        hatch="///",
    )

    theme_handles.append(Patch(facecolor=col, edgecolor="white", label=lab))

    for j in range(len(sessions)):
        if comp1000[i, j] > 0:
            ax.text(
                (x - offset)[j],
                bottom_1000[j] + comp1000[i, j] / 2,
                f"n={comp1000[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )
        if comp1350[i, j] > 0:
            ax.text(
                (x + offset)[j],
                bottom_1350[j] + comp1350[i, j] / 2,
                f"n={comp1350[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )

    bottom_1000 += comp1000[i]
    bottom_1350 += comp1350[i]

ax.set_xticks(x)
ax.set_xticklabels(sessions)
ax.set_ylabel("Number of Themes")

theme_legend = ax.legend(
    handles=theme_handles,
    title="Expectation Theme",
    loc="upper right",
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)
ax.add_artist(theme_legend)

unit_handles = [
    Patch(facecolor="white", edgecolor="black", label="COMP1000"),
    Patch(facecolor="white", edgecolor="black", label="COMP1350", hatch="///"),
]
ax.legend(
    handles=unit_handles,
    title="Unit",
    loc="upper right",
    bbox_to_anchor=(0.95, 0.75),
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)

plt.tight_layout()
plt.show()

# Motivation Graph
df_motivation = pd.read_excel(
    "entry_survey_cleaned.xlsx", sheet_name="Motivation Theme"
)
df_motivation.columns = (
    df_motivation.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
)
df_motivation["Recorded Date"] = pd.to_datetime(
    df_motivation["Recorded Date"], errors="coerce"
)

df_s1 = df_motivation[
    df_motivation["Recorded Date"] <= pd.Timestamp("2025-06-30 23:59:59")
]
df_s2 = df_motivation[
    (df_motivation["Recorded Date"] >= pd.Timestamp("2025-07-01"))
    & (df_motivation["Recorded Date"] <= pd.Timestamp("2025-11-30 23:59:59"))
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
    "Unanswered",
]
theme_colors = ["#6baed6", "#9ecae1", "#74c476", "#bcbddc", "#fdd0a2"]


def normalize_theme_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


def theme_counts(sub):
    tmp = sub.copy()
    for c in theme_cols:
        if c not in tmp.columns:
            tmp[c] = pd.NA
        tmp[c] = tmp[c].map(normalize_theme_cell)

    out = []
    for t in theme_map:
        out.append(int((tmp[theme_cols] == t).sum().sum()))
    return np.array(out, dtype=int)


c_1000_s1 = theme_counts(df_1000_s1)
c_1000_s2 = theme_counts(df_1000_s2)
c_1350_s1 = theme_counts(df_1350_s1)
c_1350_s2 = theme_counts(df_1350_s2)

comp1000 = np.vstack([c_1000_s1, c_1000_s2]).T
comp1350 = np.vstack([c_1350_s1, c_1350_s2]).T

total_s1 = int(c_1000_s1.sum() + c_1350_s1.sum())
total_s2 = int(c_1000_s2.sum() + c_1350_s2.sum())

sessions = [f"Session 1 (n ={total_s1})", f"Session 2 (n ={total_s2})"]

x = np.arange(len(sessions))
width = 0.36
gap = 0.01
offset = width / 2 + gap

fig, ax = plt.subplots(figsize=(11, 6))

bottom_1000 = np.zeros(len(sessions))
bottom_1350 = np.zeros(len(sessions))

theme_handles = []

for i, (lab, col) in enumerate(zip(theme_map, theme_colors)):
    b1 = ax.bar(
        x - offset, comp1000[i], width, bottom=bottom_1000, color=col, edgecolor="white"
    )
    b2 = ax.bar(
        x + offset,
        comp1350[i],
        width,
        bottom=bottom_1350,
        color=col,
        edgecolor="white",
        hatch="///",
    )

    theme_handles.append(Patch(facecolor=col, edgecolor="white", label=lab))

    for j in range(len(sessions)):
        if comp1000[i, j] > 0:
            ax.text(
                (x - offset)[j],
                bottom_1000[j] + comp1000[i, j] / 2,
                f"n={comp1000[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )
        if comp1350[i, j] > 0:
            ax.text(
                (x + offset)[j],
                bottom_1350[j] + comp1350[i, j] / 2,
                f"n={comp1350[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )

    bottom_1000 += comp1000[i]
    bottom_1350 += comp1350[i]

ax.set_xticks(x)
ax.set_xticklabels(sessions)
ax.set_ylabel("Number of Themes")

theme_legend = ax.legend(
    handles=theme_handles,
    title="Motivation Theme",
    loc="upper right",
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)
ax.add_artist(theme_legend)

unit_handles = [
    Patch(facecolor="white", edgecolor="black", label="COMP1000"),
    Patch(facecolor="white", edgecolor="black", label="COMP1350", hatch="///"),
]
ax.legend(
    handles=unit_handles,
    title="Unit",
    loc="upper right",
    bbox_to_anchor=(0.92, 0.75),
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)

plt.tight_layout()
plt.show()

# Feedback Graph
df_feedback = pd.read_excel("entry_survey_cleaned.xlsx", sheet_name="Feedback Theme")
df_feedback.columns = (
    df_feedback.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
)
df_feedback["Recorded Date"] = pd.to_datetime(
    df_feedback["Recorded Date"], errors="coerce"
)

df_s1 = df_feedback[df_feedback["Recorded Date"] <= pd.Timestamp("2025-06-30 23:59:59")]
df_s2 = df_feedback[
    (df_feedback["Recorded Date"] >= pd.Timestamp("2025-07-01"))
    & (df_feedback["Recorded Date"] <= pd.Timestamp("2025-11-30 23:59:59"))
]

u1000 = "COMP1000- Introduction to Computer Programming"
u1350 = "COMP1350 - Introduction to Database Design and Management"

df_1000_s1 = df_s1[df_s1["Unit"] == u1000]
df_1350_s1 = df_s1[df_s1["Unit"] == u1350]
df_1000_s2 = df_s2[df_s2["Unit"] == u1000]
df_1350_s2 = df_s2[df_s2["Unit"] == u1350]

theme_cols = [
    "Feedback Theme 1",
    "Feedback Theme 2",
    "Feedback Theme 3",
    "Feedback Theme 4",
    "Feedback Theme 5",
]
theme_map = [
    "Teaching Approach",
    "Learning Environment",
    "Learning Outcomes",
    "Suggestions for Improvement",
    "Unanswered",
]
theme_colors = ["#6baed6", "#9ecae1", "#74c476", "#bcbddc", "#fdd0a2"]


def normalize_theme_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


def theme_counts(sub):
    tmp = sub.copy()
    for c in theme_cols:
        if c not in tmp.columns:
            tmp[c] = pd.NA
        tmp[c] = tmp[c].map(normalize_theme_cell)

    out = []
    for t in theme_map:
        out.append(int((tmp[theme_cols] == t).sum().sum()))
    return np.array(out, dtype=int)


c_1000_s1 = theme_counts(df_1000_s1)
c_1000_s2 = theme_counts(df_1000_s2)
c_1350_s1 = theme_counts(df_1350_s1)
c_1350_s2 = theme_counts(df_1350_s2)

comp1000 = np.vstack([c_1000_s1, c_1000_s2]).T
comp1350 = np.vstack([c_1350_s1, c_1350_s2]).T

total_s1 = int(c_1000_s1.sum() + c_1350_s1.sum())
total_s2 = int(c_1000_s2.sum() + c_1350_s2.sum())

sessions = [f"Session 1 (n ={total_s1})", f"Session 2 (n ={total_s2})"]

x = np.arange(len(sessions))
width = 0.36
gap = 0.01
offset = width / 2 + gap

fig, ax = plt.subplots(figsize=(11, 6))

bottom_1000 = np.zeros(len(sessions))
bottom_1350 = np.zeros(len(sessions))

theme_handles = []

for i, (lab, col) in enumerate(zip(theme_map, theme_colors)):
    b1 = ax.bar(
        x - offset, comp1000[i], width, bottom=bottom_1000, color=col, edgecolor="white"
    )
    b2 = ax.bar(
        x + offset,
        comp1350[i],
        width,
        bottom=bottom_1350,
        color=col,
        edgecolor="white",
        hatch="///",
    )

    theme_handles.append(Patch(facecolor=col, edgecolor="white", label=lab))

    for j in range(len(sessions)):
        if comp1000[i, j] > 0:
            ax.text(
                (x - offset)[j],
                bottom_1000[j] + comp1000[i, j] / 2,
                f"n={comp1000[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )
        if comp1350[i, j] > 0:
            ax.text(
                (x + offset)[j],
                bottom_1350[j] + comp1350[i, j] / 2,
                f"n={comp1350[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )

    bottom_1000 += comp1000[i]
    bottom_1350 += comp1350[i]

ax.set_xticks(x)
ax.set_xticklabels(sessions)
ax.set_ylabel("Number of Themes")

theme_legend = ax.legend(
    handles=theme_handles,
    title="Feedback Theme",
    loc="upper right",
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)
ax.add_artist(theme_legend)

unit_handles = [
    Patch(facecolor="white", edgecolor="black", label="COMP1000"),
    Patch(facecolor="white", edgecolor="black", label="COMP1350", hatch="///"),
]
ax.legend(
    handles=unit_handles,
    title="Unit",
    loc="upper right",
    bbox_to_anchor=(0.94, 0.75),
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)

plt.tight_layout()
plt.show()

# Suggestion Graph
df_suggestion = pd.read_excel(
    "entry_survey_cleaned.xlsx", sheet_name="Suggestion Theme"
)
df_suggestion.columns = (
    df_suggestion.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
)
df_suggestion["Recorded Date"] = pd.to_datetime(
    df_suggestion["Recorded Date"], errors="coerce"
)

df_s1 = df_suggestion[
    df_suggestion["Recorded Date"] <= pd.Timestamp("2025-06-30 23:59:59")
]
df_s2 = df_suggestion[
    (df_suggestion["Recorded Date"] >= pd.Timestamp("2025-07-01"))
    & (df_suggestion["Recorded Date"] <= pd.Timestamp("2025-11-30 23:59:59"))
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
    "Unanswered",
]
theme_colors = ["#6baed6", "#9ecae1", "#74c476", "#fdd0a2"]


def normalize_theme_cell(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s == "" or s == "0":
        return pd.NA
    return s


def theme_counts(sub):
    tmp = sub.copy()
    for c in theme_cols:
        if c not in tmp.columns:
            tmp[c] = pd.NA
        tmp[c] = tmp[c].map(normalize_theme_cell)

    out = []
    for t in theme_map:
        out.append(int((tmp[theme_cols] == t).sum().sum()))
    return np.array(out, dtype=int)


c_1000_s1 = theme_counts(df_1000_s1)
c_1000_s2 = theme_counts(df_1000_s2)
c_1350_s1 = theme_counts(df_1350_s1)
c_1350_s2 = theme_counts(df_1350_s2)

comp1000 = np.vstack([c_1000_s1, c_1000_s2]).T
comp1350 = np.vstack([c_1350_s1, c_1350_s2]).T

total_s1 = int(c_1000_s1.sum() + c_1350_s1.sum())
total_s2 = int(c_1000_s2.sum() + c_1350_s2.sum())

sessions = [f"Session 1 (n ={total_s1})", f"Session 2 (n ={total_s2})"]

x = np.arange(len(sessions))
width = 0.36
gap = 0.01
offset = width / 2 + gap

fig, ax = plt.subplots(figsize=(11, 6))

bottom_1000 = np.zeros(len(sessions))
bottom_1350 = np.zeros(len(sessions))

theme_handles = []

for i, (lab, col) in enumerate(zip(theme_map, theme_colors)):
    b1 = ax.bar(
        x - offset, comp1000[i], width, bottom=bottom_1000, color=col, edgecolor="white"
    )
    b2 = ax.bar(
        x + offset,
        comp1350[i],
        width,
        bottom=bottom_1350,
        color=col,
        edgecolor="white",
        hatch="///",
    )

    theme_handles.append(Patch(facecolor=col, edgecolor="white", label=lab))

    for j in range(len(sessions)):
        if comp1000[i, j] > 0:
            ax.text(
                (x - offset)[j],
                bottom_1000[j] + comp1000[i, j] / 2,
                f"n={comp1000[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )
        if comp1350[i, j] > 0:
            ax.text(
                (x + offset)[j],
                bottom_1350[j] + comp1350[i, j] / 2,
                f"n={comp1350[i, j]}",
                ha="center",
                va="center",
                fontsize=9,
                bbox=dict(
                    facecolor="white", edgecolor="none", boxstyle="round,pad=0.2"
                ),
            )

    bottom_1000 += comp1000[i]
    bottom_1350 += comp1350[i]

ax.set_xticks(x)
ax.set_xticklabels(sessions)
ax.set_ylabel("Number of Themes")

theme_legend = ax.legend(
    handles=theme_handles,
    title="Suggestion Theme",
    loc="upper right",
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)
ax.add_artist(theme_legend)

unit_handles = [
    Patch(facecolor="white", edgecolor="black", label="COMP1000"),
    Patch(facecolor="white", edgecolor="black", label="COMP1350", hatch="///"),
]
ax.legend(
    handles=unit_handles,
    title="Unit",
    loc="upper right",
    bbox_to_anchor=(0.96, 0.8),
    fontsize=9,
    title_fontsize=10,
    frameon=True,
    framealpha=0.9,
)

plt.tight_layout()
plt.show()

#! # Which students perceive REBOUND as helpful,
#! # and how do unit and session differences predict perceived helpfulness of each REBOUND component (content, facilitator, and class structure)?

#! RQ1.1 Do students perceive the helpfulness of REBOUND differently across sessions within the same unit? or Does perception change over time within a unit?
# Within unit 1350, across sessions comparison
results = []

for comp in components:
    x = df_1350_s1[comp].dropna()
    y = df_1350_s2[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results.append(
        {
            "Component": comp,
            "Session 1 N": len(x),
            "Session 2 N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_results_1350 = pd.DataFrame(results)
mw_results_1350


## effect_sizes optional if chaz wants
def rank(u, n1, n2):
    return 1 - (2 * u) / (n1 * n2)


effect_sizes = []

for comp in components:
    x = df_1350_s1[comp].dropna()
    y = df_1350_s2[comp].dropna()

    u_stat, _ = mannwhitneyu(x, y, alternative="two-sided")
    rbc = rank(u_stat, len(x), len(y))

    effect_sizes.append({"Component": comp, "Rank-Biserial r": rbc})

effect_sizes_1350 = pd.DataFrame(effect_sizes)
effect_sizes_1350

# Within unit 1000, across sessions comparison
results = []

for comp in components:
    x = df_1000_s1[comp].dropna()
    y = df_1000_s2[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results.append(
        {
            "Component": comp,
            "Session 1 N": len(x),
            "Session 2 N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_results_1000 = pd.DataFrame(results)
mw_results_1000


def rank(u, n1, n2):
    return 1 - (2 * u) / (n1 * n2)


effect_sizes = []

for comp in components:
    x = df_1000_s1[comp].dropna()
    y = df_1000_s2[comp].dropna()

    u_stat, _ = mannwhitneyu(x, y, alternative="two-sided")
    rbc = rank(u_stat, len(x), len(y))

    effect_sizes.append({"Component": comp, "Rank-Biserial r": rbc})

effect_sizes_1000 = pd.DataFrame(effect_sizes)
effect_sizes_1000

mw_results_comparison = pd.concat([mw_results_1350, mw_results_1000], ignore_index=True)
mw_results_comparison


effect_sizes_1350["Component"] = "COMP1350" + " - " + effect_sizes_1350["Component"]
effect_sizes_1000["Component"] = "COMP1000" + " - " + effect_sizes_1000["Component"]
effect_sizes_comparison = pd.concat(
    [effect_sizes_1350, effect_sizes_1000], ignore_index=True
)
effect_sizes_comparison

## Within sessions, across units comparison
#! RQ1.2 Do students taking different units perceive the helpfulness of REBOUND differently when attending in the same session?
# or At the same time point, does the unit itself matter?
results_s1 = []

for comp in components:
    x = df_1350_s1[comp].dropna()
    y = df_1000_s1[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results_s1.append(
        {
            "Session": "Session 1",
            "Component": comp,
            "COMP1350 N": len(x),
            "COMP1000 N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_unit_session1 = pd.DataFrame(results_s1)
mw_unit_session1


results_s2 = []

for comp in components:
    x = df_1350_s2[comp].dropna()
    y = df_1000_s2[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results_s2.append(
        {
            "Session": "Session 2",
            "Component": comp,
            "COMP1350 N": len(x),
            "COMP1000 N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_unit_session2 = pd.DataFrame(results_s2)
mw_unit_session2

mw_unit_comparison = pd.concat([mw_unit_session1, mw_unit_session2], ignore_index=True)

mw_unit_comparison


#! RQ1.3 Do students with different pre-REBOUND confidence levels perceive REBOUND differently after attending it?
# Get Confidence Unit Content first
df["Low Confidence Content"] = df["Confidence Unit Content"].isin([1, 2]).astype(int)
df["High Confidence Content"] = df["Confidence Unit Content"].isin([3, 4]).astype(int)
results_conf_content = []

low_group = df[df["Low Confidence Content"] == 1]
high_group = df[df["High Confidence Content"] == 1]

for comp in components:
    x = low_group[comp].dropna()
    y = high_group[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results_conf_content.append(
        {
            "Component": comp,
            "Low Confidence N": len(x),
            "High Confidence N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_conf_content = pd.DataFrame(results_conf_content)
mw_conf_content


# Effect sizes for confidence content
def rank(u, n1, n2):
    return 1 - (2 * u) / (n1 * n2)


effect_conf_content = []

for _, row in mw_conf_content.iterrows():
    rbc = rank(row["U statistic"], row["Low Confidence N"], row["High Confidence N"])

    effect_conf_content.append({"Component": row["Component"], "Rank-Biserial r": rbc})

effect_conf_content_df = pd.DataFrame(effect_conf_content)
effect_conf_content_df

# Get confidence Assessments next
df["Low Confidence Assess"] = df["Confidence Assessments"].isin([1, 2]).astype(int)
df["High Confidence Assess"] = df["Confidence Assessments"].isin([3, 4]).astype(int)
results_conf_assess = []

low_group = df[df["Low Confidence Assess"] == 1]
high_group = df[df["High Confidence Assess"] == 1]

for comp in components:
    x = low_group[comp]
    y = high_group[comp]

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results_conf_assess.append(
        {
            "Component": comp,
            "Low Confidence N": len(x),
            "High Confidence N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_conf_assess = pd.DataFrame(results_conf_assess)
mw_conf_assess

# Effect sizes for confidence assessments
effect_conf_assess = []

for _, row in mw_conf_assess.iterrows():
    rbc = rank(row["U statistic"], row["Low Confidence N"], row["High Confidence N"])

    effect_conf_assess.append({"Component": row["Component"], "Rank-Biserial r": rbc})

effect_conf_assess_df = pd.DataFrame(effect_conf_assess)
effect_conf_assess_df

df_1350 = df[df["Unit"] == "COMP1350 - Introduction to Database Design and Management"]

low = df_1350[df_1350["Confidence Unit Content"].isin([1, 2])]
high = df_1350[df_1350["Confidence Unit Content"].isin([3, 4])]

results_1350_content = []

for comp in components:
    x = low[comp].dropna()
    y = high[comp].dropna()

    u, p = mannwhitneyu(x, y, alternative="two-sided")

    results_1350_content.append(
        {
            "Unit": "COMP1350",
            "Confidence Type": "Unit Content",
            "Component": comp,
            "Low N": len(x),
            "High N": len(y),
            "U statistic": u,
            "p-value": p,
            "Rank-Biserial r": rank(u, len(x), len(y)),
        }
    )

pd.DataFrame(results_1350_content)

# In which unit does pre-REBOUND confidence matter more for how students perceive REBOUND after taking it?
# COMP1350 first
low = df_1350[df_1350["Confidence Assessments"].isin([1, 2])]
high = df_1350[df_1350["Confidence Assessments"].isin([3, 4])]

results_1350_assess = []

for comp in components:
    x = low[comp]
    y = high[comp]

    u, p = mannwhitneyu(x, y, alternative="two-sided")

    results_1350_assess.append(
        {
            "Unit": "COMP1350",
            "Confidence Type": "Assessments",
            "Component": comp,
            "Low N": len(x),
            "High N": len(y),
            "U statistic": u,
            "p-value": p,
            "Rank-Biserial r": rank(u, len(x), len(y)),
        }
    )

pd.DataFrame(results_1350_assess)


# Now COMP1000
df_1000 = df[df["Unit"] == "COMP1000- Introduction to Computer Programming"]

low = df_1000[df_1000["Confidence Unit Content"].isin([1, 2])]
high = df_1000[df_1000["Confidence Unit Content"].isin([3, 4])]

results_1000_content = []

for comp in components:
    x = low[comp].dropna()
    y = high[comp].dropna()

    u, p = mannwhitneyu(x, y, alternative="two-sided")

    results_1000_content.append(
        {
            "Unit": "COMP1000",
            "Confidence Type": "Unit Content",
            "Component": comp,
            "Low N": len(x),
            "High N": len(y),
            "U statistic": u,
            "p-value": p,
            "Rank-Biserial r": rank(u, len(x), len(y)),
        }
    )

pd.DataFrame(results_1000_content)


#! RQ1.3 Do repeating students perceive REBOUND as more helpful than non-repeating students?
df_repeat = df[df["Repeating Student"] == 1]
df_nonrepeat = df[df["Repeating Student"] == 0]
results_repeat = []

for comp in components:
    x = df_repeat[comp].dropna()
    y = df_nonrepeat[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results_repeat.append(
        {
            "Component": comp,
            "Repeating N": len(x),
            "Non-Repeating N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_repeat_results = pd.DataFrame(results_repeat)
mw_repeat_results


## Effect sizes for repeating vs non-repeating
def rank(u, n1, n2):
    return 1 - (2 * u) / (n1 * n2)


effect_sizes_repeat = []

for _, row in mw_repeat_results.iterrows():
    rbc = rank(row["U statistic"], row["Repeating N"], row["Non-Repeating N"])

    effect_sizes_repeat.append({"Component": row["Component"], "Rank-Biserial r": rbc})

effect_sizes_repeat_df = pd.DataFrame(effect_sizes_repeat)
effect_sizes_repeat_df


#! RQ1.4 Do first-generation students perceive REBOUND as more helpful than non–first-generation students?
df_firstgen = df[df["First Generation Student"] == 1]
df_nonfirstgen = df[df["First Generation Student"] == 0]

results_firstgen = []

for comp in components:
    x = df_firstgen[comp].dropna()
    y = df_nonfirstgen[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results_firstgen.append(
        {
            "Component": comp,
            "First-Gen N": len(x),
            "Non–First-Gen N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_firstgen_results = pd.DataFrame(results_firstgen)
mw_firstgen_results


## Effect sizes for first-generation vs non–first-generation
def rank(u, n1, n2):
    return 1 - (2 * u) / (n1 * n2)


effect_sizes_firstgen = []

for _, row in mw_firstgen_results.iterrows():
    rbc = rank(row["U statistic"], row["First-Gen N"], row["Non–First-Gen N"])

    effect_sizes_firstgen.append(
        {"Component": row["Component"], "Rank-Biserial r": rbc}
    )

effect_sizes_firstgen_df = pd.DataFrame(effect_sizes_firstgen)
effect_sizes_firstgen_df


#! RQ1.5 How do repeating students' perceptions of REBOUND compare to those of first-generation students?
#! That is, are repeating students more likely to find REBOUND helpful than first-generation students?
df_repeat_only = df[df["Repeating Student"] == 1]

df_firstgen_only = df[
    (df["First Generation Student"] == 1) & (df["Repeating Student"] == 0)
]

results_rg_fg = []

for comp in components:
    x = df_repeat_only[comp].dropna()
    y = df_firstgen_only[comp].dropna()

    u_stat, p_val = mannwhitneyu(x, y, alternative="two-sided")

    results_rg_fg.append(
        {
            "Component": comp,
            "Repeating N": len(x),
            "First-Gen Only N": len(y),
            "U statistic": u_stat,
            "p-value": p_val,
        }
    )

mw_repeat_vs_firstgen = pd.DataFrame(results_rg_fg)
mw_repeat_vs_firstgen


## Effect sizes for repeating vs first-generation only
def rank(u, n1, n2):
    return 1 - (2 * u) / (n1 * n2)


effect_sizes_rg_fg = []

for _, row in mw_repeat_vs_firstgen.iterrows():
    rbc = rank(row["U statistic"], row["Repeating N"], row["First-Gen Only N"])

    effect_sizes_rg_fg.append({"Component": row["Component"], "Rank-Biserial r": rbc})

effect_sizes_rg_fg_df = pd.DataFrame(effect_sizes_rg_fg)
effect_sizes_rg_fg_df
