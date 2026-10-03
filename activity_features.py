import pandas as pd

#Load cleaned assessment data

assessments = pd.read_csv("clean_assessments.csv")
course_counts = (
    assessments
    .groupby(["code_module", "code_presentation"])
    .size()
    .sort_values(ascending=False)
)
module, presentation = course_counts.index[0]
print("\nSelected course:")
print(module, presentation)
course = assessments[
    (assessments["code_module"] == module) &
    (assessments["code_presentation"] == presentation)
].copy()

selected_students = (
    course["id_student"]
    .drop_duplicates()
    .head(300)
    .tolist()
)
course = course[
    course["id_student"].isin(selected_students)
].copy()
print("Students selected:", len(selected_students))
print("Assessment records:", len(course))

#Read studentVle.csv in chunks

activity_parts = []
chunk_size = 250000
print("\nReading studentVle.csv...")
for number, chunk in enumerate(
    pd.read_csv(
        "studentVle.csv",
        usecols=[
            "code_module",
            "code_presentation",
            "id_student",
            "date",
            "sum_click"
        ],
        chunksize=chunk_size
    )
):
    filtered = chunk[
        (chunk["code_module"] == module) &
        (chunk["code_presentation"] == presentation) &
        (chunk["id_student"].isin(selected_students))
    ]
    if not filtered.empty:
        activity_parts.append(filtered)
    if number % 10 == 0:
        print("Processed chunk:", number)

#Combine activity
activity = pd.concat(
    activity_parts,
    ignore_index=True
)
print("\nRelevant VLE activity rows:", len(activity))

daily_activity = (
    activity
    .groupby(["id_student", "date"], as_index=False)
    ["sum_click"]
    .sum()
)
print("Daily activity rows:", len(daily_activity))

#Calculate activity before every deadline

features = []
for _, task in course.iterrows():
    student = task["id_student"]
    deadline = task["deadline"]
    student_activity = daily_activity[
        daily_activity["id_student"] == student
    ]
    last_7 = student_activity[
        (student_activity["date"] >= deadline - 7) &
        (student_activity["date"] <= deadline)
    ]
    last_2 = student_activity[
        (student_activity["date"] >= deadline - 2) &
        (student_activity["date"] <= deadline)
    ]
    previous_5 = student_activity[
        (student_activity["date"] >= deadline - 7) &
        (student_activity["date"] <= deadline - 3)
    ]
    clicks_7d = last_7["sum_click"].sum()
    clicks_2d = last_2["sum_click"].sum()
    clicks_previous_5d = previous_5["sum_click"].sum()

    active_days_7d = last_7["date"].nunique()
    recent_daily_average = clicks_2d / 3
    previous_daily_average = clicks_previous_5d / 5
    burst_ratio = recent_daily_average / (previous_daily_average + 1)
    if burst_ratio >= 1.5 and clicks_2d >= 5:
        last_minute_activity = 1
    else:
        last_minute_activity = 0
    features.append({
        "id_student": student,
        "id_assessment": task["id_assessment"],
        "clicks_last_7d": clicks_7d,
        "clicks_last_2d": clicks_2d,
        "clicks_previous_5d": clicks_previous_5d,
        "active_days_last_7d": active_days_7d,
        "burst_ratio": round(burst_ratio, 2),
        "last_minute_activity": last_minute_activity
    })
activity_features = pd.DataFrame(features)

#Merge with assessment behaviour

final = course.merge(
    activity_features,
    on=["id_student", "id_assessment"],
    how="left"
)
final.to_csv(
    "student_behavior_features.csv",
    index=False
)
print("\nSUCCESS!")
print("Created: student_behavior_features.csv")
print("\nSample features:\n")
print(
    final[
        [
            "id_student",
            "id_assessment",
            "deadline",
            "date_submitted",
            "submission_behavior",
            "clicks_last_7d",
            "clicks_last_2d",
            "burst_ratio",
            "last_minute_activity"
        ]
    ].head(20)
)
print("\nLast-minute activity counts:")
print(
    final["last_minute_activity"]
    .value_counts()
)