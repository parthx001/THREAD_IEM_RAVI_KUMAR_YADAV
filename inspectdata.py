import pandas as pd

assessments = pd.read_csv("assessments.csv")
student_assessment = pd.read_csv("studentAssessment.csv")
student_vle = pd.read_csv("studentVle.csv", nrows=10)

print("\n--- assessments.csv ---")
print(assessments.head())
print("\nColumns:", assessments.columns.tolist())

print("\n--- studentAssessment.csv ---")
print(student_assessment.head())
print("\nColumns:", student_assessment.columns.tolist())

print("\n--- studentVle.csv sample ---")
print(student_vle.head())
print("\nColumns:", student_vle.columns.tolist())