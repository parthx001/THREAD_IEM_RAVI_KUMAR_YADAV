import pandas as pd
df = pd.read_csv("processed_assessments.csv")
print("Original rows:", len(df))
df = df[df["is_banked"] == 0]
df = df[df["date_submitted"] >= 0]
df = df.dropna(subset=["deadline"])
# Recalculate behaviour
df["days_from_deadline"] = (
    df["date_submitted"] - df["deadline"]
)
def classify_submission(diff):
    if diff > 0:
        return "Late"
    elif diff >= -1:
        return "Last Minute"
    elif diff >= -3:
        return "Near Deadline"
    else:
        return "Early"
df["submission_behavior"] = (
    df["days_from_deadline"]
    .apply(classify_submission)
)
df = df.sort_values(
    ["id_student", "deadline"]
)
df.to_csv(
    "clean_assessments.csv",
    index=False
)
print("Clean rows:", len(df))
print("\nBehaviour distribution:")
print(df["submission_behavior"].value_counts())
print("\nSample:")
print(
    df[
        [
            "id_student",
            "id_assessment",
            "deadline",
            "date_submitted",
            "days_from_deadline",
            "submission_behavior"
        ]
    ].head(15)
)