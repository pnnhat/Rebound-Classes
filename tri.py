import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu
from matplotlib.patches import Patch


df_entry = pd.read_excel("EntrySurvey_JaydenUpdated.xlsx")

df_entry = df_entry[df_entry["Finished"] == True].copy()
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
    c
    for c in df_entry.columns
    if c.startswith("Welcome to the REBOUND research study!")
][0]

df_entry = df_entry[
    (df_entry[consent_col] != "I do not consent, I do not wish to participate")
    & (~df_entry[consent_col].isna())
]

for col in df_entry.columns:
    if col.startswith("Welcome to the REBOUND research study!"):
        drop.append(col)
df_entry = df_entry.drop(columns=drop, errors="ignore")

rename_map = {
    "Select the unit you taking this particular REBOUND class for?": "Unit_Entry",
    "Are you a first-generation student to attend university? (First-generation student meaning you/ your siblings are the first ones to attend university)": "First Generation Student",
    "Are you a repeating student?": "Repeating Student",
    "What challenges did you face in your first attempt at the unit?\nPlease choose everything that applies. If you have other reasons not on the list, please list them in the other option.": "Challenges Faced",
    "How confident are you with the unit? - The Unit Content": "Confidence Unit Content_Entry",
    "How confident are you with the unit? - The Assessments": "Confidence Assessments_Entry",
    "What are your thoughts on the REBOUND classes so far? - The Content Covered": "Thoughts Content Covered_Entry",
    "What are your thoughts on the REBOUND classes so far? - The Facilitator": "Thoughts Facilitator_Entry",
    "What are your thoughts on the REBOUND classes so far? - Structure of the Classes": "Thoughts Structure of the Classes_Entry",
    "What are your expectations of the REBOUND classes? Why did you choose to attend them?": "Expectations of REBOUND Classes_Entry",
    "Can you give us feedback about the REBOUND classes, please? (What's working for you? How can these REBOUND classes be better? How can we improve?)": "Feedback_Entry",
    "Please enter your StudentID": "StudentID",
}

df_entry = df_entry.rename(columns=rename_map)

## Map Yes/No to 1/0
map = {"Yes": 1, "No": 0}
df_entry["First Generation Student"] = df_entry["First Generation Student"].map(map)
df_entry["Repeating Student"] = df_entry["Repeating Student"].map(map)

confidence = {
    "Very Confident": 4,
    "Confident": 3,
    "Somewhat Confident": 2,
    "Not Confident at all": 1,
}
df_entry["Confidence Unit Content_Entry"] = df_entry[
    "Confidence Unit Content_Entry"
].map(confidence)
df_entry["Confidence Assessments_Entry"] = df_entry["Confidence Assessments_Entry"].map(
    confidence
)
thought = {
    "Very Helpful": 4,
    "Fairly helpful": 3,
    "Somewhat helpful": 2,
    "Not helpful at all": 1,
}
thought_cols = [
    "Thoughts Content Covered_Entry",
    "Thoughts Facilitator_Entry",
    "Thoughts Structure of the Classes_Entry",
]

for col in thought_cols:
    df_entry[col] = df_entry[col].map(thought)


df_entry["Recorded Date"] = pd.to_datetime(df_entry["Recorded Date"])
df_s1 = df_entry[df_entry["Recorded Date"] <= "2025-06-30"]
df_s2 = df_entry[
    (df_entry["Recorded Date"] >= "2025-07-01")
    & (df_entry["Recorded Date"] <= "2025-11-30")
]

## For comp1350 s1 s2
df_1350 = df_entry[
    df_entry["Unit_Entry"]
    == "COMP1350 - Introduction to Database Design and Management"
]
df_1350_s1 = df_s1[
    df_s1["Unit_Entry"] == "COMP1350 - Introduction to Database Design and Management"
]
df_1350_s2 = df_s2[
    df_s2["Unit_Entry"] == "COMP1350 - Introduction to Database Design and Management"
]

## For comp1000 s1 s2
df_1000 = df_entry[
    df_entry["Unit_Entry"] == "COMP1000- Introduction to Computer Programming"
]
df_1000_s1 = df_s1[
    df_s1["Unit_Entry"] == "COMP1000- Introduction to Computer Programming"
]
df_1000_s2 = df_s2[
    df_s2["Unit_Entry"] == "COMP1000- Introduction to Computer Programming"
]


# Exit Survey
df_exit = pd.read_excel("Project REBOUND Exit Survey_Jayden.xlsx")
df_exit = df_exit[df_exit["Finished"] == True].copy()
consent_col = [
    c for c in df_exit.columns if c.startswith("Welcome to the REBOUND research study!")
][0]
df_exit = df_exit[df_exit[consent_col] == "I consent to provide responses"].copy()
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


for col in df_exit.columns:
    if col.startswith("Welcome to the REBOUND research study!"):
        drop.append(col)
df_exit = df_exit.drop(columns=drop, errors="ignore")

rename_map = {
    "Select the unit you taking this particular REBOUND class for?": "Unit_Exit",
    "How confident are you with the unit, now at the end of the semester? - The unit content": "Confidence Unit Content_Exit",
    "How confident are you with the unit, now at the end of the semester? - The assessments": "Confidence Assessments_Exit",
    "How confident are you with the unit, now at the end of the semester? - Meeting the learning outcomes & passing the unit": "Confidence Learning Outcomes_Exit",
    "What are your thoughts on the REBOUND classes at the end of the semester? - The Content Covered": "Thoughts Content Covered_Exit",
    "What are your thoughts on the REBOUND classes at the end of the semester? - The Facilitator": "Thoughts Facilitator_Exit",
    "What are your thoughts on the REBOUND classes at the end of the semester? - Structure of the Classes": "Thoughts Structure of the Classes_Exit",
    "On the scale of 1 to 5, rate your experience with the REBOUND classes - Ratiing for REBOUND Classes": "Rating REBOUND Classes_Exit",
    "How did Rebound classes help you with the unit?": "How Rebound Classes Helped_Exit",
    "What can we do to better the Rebound classes?": "Feedback_Exit",
    "Please enter your StudentID": "StudentID",
}

df_exit = df_exit.rename(columns=rename_map)

confidence_map = {
    "Very Confident": 4,
    "Confident": 3,
    "Somewhat Confident": 2,
    "Not Confident at all": 1,
}

df_exit["Confidence Unit Content_Exit"] = df_exit["Confidence Unit Content_Exit"].map(
    confidence_map
)
df_exit["Confidence Assessments_Exit"] = df_exit["Confidence Assessments_Exit"].map(
    confidence_map
)
df_exit["Confidence Learning Outcomes_Exit"] = df_exit[
    "Confidence Learning Outcomes_Exit"
].map(confidence_map)

thought_map = {
    "Very Confident": 4,
    "Confident": 3,
    "Somewhat Confident": 2,
    "Not Confident at all": 1,
}

thought_cols = [
    "Thoughts Content Covered_Exit",
    "Thoughts Facilitator_Exit",
    "Thoughts Structure of the Classes_Exit",
]

for col in thought_cols:
    df_exit[col] = df_exit[col].map(thought_map)

df_exit["Rating REBOUND Classes_Exit"] = pd.to_numeric(
    df_exit["Rating REBOUND Classes_Exit"], errors="coerce"
)

df_exit["Recorded Date"] = pd.to_datetime(df_exit["Recorded Date"])

df_exit["Unit_Exit"] = df_exit["Unit_Exit"].str.strip()

u1350 = "COMP1350 - Introduction to Database Design and Management"
u1000 = "COMP1000- Introduction to Computer Programming"

# COMP1000
df_1000 = df_exit[df_exit["Unit_Exit"] == u1000]
df_1000_s1 = df_1000[df_1000["Recorded Date"] <= "2025-06-30"]
df_1000_s2 = df_1000[
    (df_1000["Recorded Date"] >= "2025-07-01")
    & (df_1000["Recorded Date"] <= "2025-11-30")
]

# COMP1350
df_1350 = df_exit[df_exit["Unit_Exit"] == u1350]
df_1350_s1 = df_1350[df_1350["Recorded Date"] <= "2025-06-30"]
df_1350_s2 = df_1350[
    (df_1350["Recorded Date"] >= "2025-07-01")
    & (df_1350["Recorded Date"] <= "2025-11-30")
]

df_entry.head()
df_exit.head()
df_tri = pd.merge(
    df_exit, df_entry, on="StudentID", how="inner", suffixes=("_Exit", "_Entry")
)
print("Matched responses:", len(df_tri))

df_tri.head()


def assign_session(date):
    if date <= pd.Timestamp("2025-06-30"):
        return "Session 1"
    elif date <= pd.Timestamp("2025-11-30"):
        return "Session 2"
    else:
        return np.nan


df_tri["Session"] = df_tri["Recorded Date_Exit"].apply(assign_session)


triangulated = df_tri[
    [
        "StudentID",
        "Session",
        "Unit_Exit",
        # Demographics
        "First Generation Student",
        "Repeating Student",
        # Entry Confidence
        "Confidence Unit Content_Entry",
        "Confidence Assessments_Entry",
        # Exit Confidence
        "Confidence Unit Content_Exit",
        "Confidence Assessments_Exit",
        "Confidence Learning Outcomes_Exit",
        # Entry Thoughts
        "Thoughts Content Covered_Entry",
        "Thoughts Facilitator_Entry",
        "Thoughts Structure of the Classes_Entry",
        # Exit Thoughts
        "Thoughts Content Covered_Exit",
        "Thoughts Facilitator_Exit",
        "Thoughts Structure of the Classes_Exit",
        # Entry Comments
        "Expectations of REBOUND Classes_Entry",
        "Feedback_Entry",
        # Exit Comments
        "How Rebound Classes Helped_Exit",
        "Feedback_Exit",
    ]
]

conf_cols = [
    "Confidence Unit Content_Entry",
    "Confidence Assessments_Entry",
    "Confidence Unit Content_Exit",
    "Confidence Assessments_Exit",
    "Confidence Learning Outcomes_Exit",
]

for c in conf_cols:
    if c in df_tri.columns:
        df_tri[c] = df_tri[c].replace(
            {
                4: "Very Confident",
                3: "Confident",
                2: "Somewhat Confident",
                1: "Not Confident at all",
            }
        )
thought_entry_cols = [
    "Thoughts Content Covered_Entry",
    "Thoughts Facilitator_Entry",
    "Thoughts Structure of the Classes_Entry",
]

for c in thought_entry_cols:
    if c in df_tri.columns:
        df_tri[c] = df_tri[c].replace(
            {
                4: "Very Helpful",
                3: "Fairly helpful",
                2: "Somewhat helpful",
                1: "Not helpful at all",
            }
        )
thought_exit_cols = [
    "Thoughts Content Covered_Exit",
    "Thoughts Facilitator_Exit",
    "Thoughts Structure of the Classes_Exit",
]

for c in thought_exit_cols:
    if c in df_tri.columns:
        df_tri[c] = df_tri[c].replace(
            {
                4: "Very Helpful",
                3: "Fairly helpful",
                2: "Somewhat helpful",
                1: "Not helpful at all",
            }
        )
triangulated.to_excel("linked_data.xlsx", index=False)
