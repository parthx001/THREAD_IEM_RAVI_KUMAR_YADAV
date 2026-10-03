import pandas as pd
df = pd.read_csv("student_behavior_features.csv")
df = df.sort_values(
    ["id_student", "deadline"]
).copy()

#Converting submission behaviour into risk

submission_risk = {
    "Early": 0.0,
    "Near Deadline": 0.35,
    "Last Minute": 0.75,
    "Late": 1.0
}
df["submission_risk"] = (
    df["submission_behavior"]
    .map(submission_risk)
    .fillna(0)
)
#Calculating procrastination score

df["procrastination_score"] = (
    df["submission_risk"] * 60
    +
    df["last_minute_activity"] * 40
).round(1)

#Marking each task as risky

df["risky_task"] = (
    df["procrastination_score"] >= 55
).astype(int)

#Detecting repeated pattern
df["risky_last_3"] = (
    df.groupby("id_student")["risky_task"]
    .rolling(window=3, min_periods=2)
    .sum()
    .reset_index(level=0, drop=True)
)
df["rolling_risk"] = (
    df.groupby("id_student")["procrastination_score"]
    .rolling(window=3, min_periods=2)
    .mean()
    .reset_index(level=0, drop=True)
    .round(1)
)
df["pattern_detected"] = (
    df["risky_last_3"] >= 2
).astype(int)

#Find pattern onset

df["pattern_onset"] = 0
for student_id, group in df.groupby("id_student"):
    detected = group[group["pattern_detected"] == 1]
    if len(detected) > 0:
        first_index = detected.index[0]
        df.loc[first_index, "pattern_onset"] = 1

#Creating simple explanation

def make_explanation(row):
    reasons = []
    if row["submission_behavior"] == "Late":
        reasons.append("the task was submitted after the deadline")
    elif row["submission_behavior"] == "Last Minute":
        reasons.append("the task was submitted at the last minute")
    elif row["submission_behavior"] == "Near Deadline":
        reasons.append("the task was completed close to the deadline")
    if row["last_minute_activity"] == 1:
        reasons.append(
            "academic activity increased sharply just before the deadline"
        )
    if row["risky_last_3"] >= 2:
        reasons.append(
            "similar behaviour appeared in at least 2 of the last 3 tasks"
        )
    if not reasons:
        return "No strong procrastination pattern detected."
    return "Pattern detected because " + ", and ".join(reasons) + "."
df["explanation"] = df.apply(
    make_explanation,
    axis=1
)

#Risk level

def risk_level(score):
    if score >= 75:
        return "High"
    elif score >= 45:
        return "Emerging"
    else:
        return "Normal"
df["risk_level"] = df["rolling_risk"].apply(
    lambda x: risk_level(x) if pd.notna(x) else "Normal"
)
#Save full result

df.to_csv(
    "procrastination_results.csv",
    index=False
)
#Create student summary

summaries = []
for student_id, group in df.groupby("id_student"):
    onset = group[group["pattern_onset"] == 1]
    if len(onset) > 0:
        first = onset.iloc[0]
        summaries.append({
            "id_student": student_id,
            "pattern_found": "Yes",
            "onset_assessment":
                first["id_assessment"],
            "onset_day":
                first["deadline"],
            "risk_at_onset":
                first["rolling_risk"],
            "explanation":
                first["explanation"]
        })
    else:

        summaries.append({
            "id_student": student_id,
            "pattern_found": "No",
            "onset_assessment": None,
            "onset_day": None,
            "risk_at_onset":
                group["rolling_risk"].iloc[-1],
            "explanation":
                "No repeated procrastination pattern was found."
        })
summary_df = pd.DataFrame(summaries)
summary_df.to_csv(
    "student_pattern_summary.csv",
    index=False
)
#Display results

print("\nDETECTION COMPLETE\n")
print("Total students:", df["id_student"].nunique())
print(
    "Students with detected pattern:",
    (summary_df["pattern_found"] == "Yes").sum()
)
print(
    "Students without pattern:",
    (summary_df["pattern_found"] == "No").sum()
)
print("\nSample detected students:\n")
print(
    summary_df[
        summary_df["pattern_found"] == "Yes"
    ].head(10).to_string(index=False)
)
print("\nCreated files:")
print("1. procrastination_results.csv")
print("2. student_pattern_summary.csv")