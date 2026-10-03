import pandas as pd
assessments = pd.read_csv("assessments.csv")
student_assessment = pd.read_csv("studentAssessment.csv")
df = student_assessment.merge(
    assessments[
        [
            "id_assessment",
            "code_module",
            "code_presentation",
            "assessment_type",
            "date",
            "weight"
        ]
    ],
    on="id_assessment",
    how="left"
)

df = df.rename(columns={"date": "deadline"})
df["deadline"] = pd.to_numeric(df["deadline"], errors="coerce")
df["date_submitted"] = pd.to_numeric(
    df["date_submitted"],
    errors="coerce"
)
df["days_from_deadline"] = (
    df["date_submitted"] - df["deadline"]
)
def classify_submission(row):
    difference = row["days_from_deadline"]

    if pd.isna(difference):
        return "Unknown"

    if difference > 0:
        return "Late"

    elif difference >= -1:
        return "Last Minute"

    elif difference >= -3:
        return "Near Deadline"

    else:
        return "Early"
df["submission_behavior"] = df.apply(
    classify_submission,
    axis=1
)
df = df.sort_values(
    ["id_student", "date_submitted"]
)
df.to_csv(
    "processed_assessments.csv",
    index=False
)
print("\nProcessed dataset created successfully!\n")
print(
    df[
        [
            "id_student",
            "id_assessment",
            "assessment_type",
            "deadline",
            "date_submitted",
            "days_from_deadline",
            "submission_behavior"
        ]
    ].head(20)
)
print("\nSubmission behaviour counts:\n")
print(df["submission_behavior"].value_counts()) 