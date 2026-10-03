import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG

st.set_page_config(
    page_title="ProTrack",
    page_icon="📚",
    layout="wide"
)
# LOAD DATA
@st.cache_data
def load_data():
    results = pd.read_csv("procrastination_results.csv")
    summary = pd.read_csv("student_pattern_summary.csv")
    return results, summary
results, summary = load_data()

# TITLE
st.title("📚 ProTrack")
st.subheader(
    "Explainable Procrastination Pattern Detection for Students"
)
st.caption(
    "Detecting when repeated postponement and last-minute academic behaviour begins to emerge."
)
st.divider()

# STUDENT SELECTOR

students = sorted(results["id_student"].unique())
selected_student = st.selectbox(
    "Select Student",
    students
)
student_data = results[
    results["id_student"] == selected_student
].sort_values("deadline")

student_summary = summary[
    summary["id_student"] == selected_student
].iloc[0]

# TOP METRICS

col1, col2, col3, col4 = st.columns(4)
pattern_found = student_summary["pattern_found"]
latest_risk = student_data["rolling_risk"].dropna()
if len(latest_risk) > 0:
    latest_risk = latest_risk.iloc[-1]
else:
    latest_risk = 0
with col1:
    st.metric(
        "Pattern Detected",
        pattern_found
    )
with col2:
    st.metric(
        "Current Risk",
        f"{latest_risk:.1f}%"
    )
with col3:
    if pattern_found == "Yes":
        onset = student_summary["onset_assessment"]
        st.metric(
            "Pattern Onset",
            f"Assessment {int(onset)}"
        )
    else:
        st.metric(
            "Pattern Onset",
            "Not Detected"
        )
with col4:
    risky_tasks = int(
        student_data["risky_task"].sum()
    )
    st.metric(
        "Risky Tasks",
        risky_tasks
    )
st.divider()
# RISK TREND GRAPH

st.subheader("📈 Procrastination Risk Over Time")
plot_data = student_data.copy()
plot_data["assessment_label"] = (
    "Assessment "
    + plot_data["id_assessment"].astype(str)
)
fig = px.line(
    plot_data,
    x="assessment_label",
    y="rolling_risk",
    markers=True,
    title="Behavioural Risk Progression"
)
fig.add_hline(
    y=45,
    line_dash="dash",
    annotation_text="Emerging Risk"
)
fig.add_hline(
    y=75,
    line_dash="dash",
    annotation_text="High Risk"
)
fig.update_layout(
    xaxis_title="Academic Activity Sequence",
    yaxis_title="Risk Score (%)"
)
st.plotly_chart(
    fig,
    width="stretch"
)

# PATTERN ONSET
st.subheader("🎯 Behavioural Turning Point")
onset_rows = student_data[
    student_data["pattern_onset"] == 1
]
if len(onset_rows) > 0:
    onset = onset_rows.iloc[0]
    st.error(
        f"""
        Repeated procrastination behaviour begins around
        Assessment {int(onset['id_assessment'])}.

        Rolling Risk: {onset['rolling_risk']:.1f}%
        """
    )
else:
    st.success(
        "No clear repeated procrastination pattern was detected."
    )
# EXPLANATION
st.subheader("🧠 Why was this detected?")
if len(onset_rows) > 0:
    onset = onset_rows.iloc[0]
    st.write(
        onset["explanation"]
    )
    reasons = []
    if onset["submission_behavior"] == "Late":
        reasons.append(
            "The assessment was submitted after its deadline."
        )
    elif onset["submission_behavior"] == "Last Minute":
        reasons.append(
            "The assessment was submitted extremely close to the deadline."
        )
    elif onset["submission_behavior"] == "Near Deadline":
        reasons.append(
            "The assessment was completed close to its deadline."
        )
    if onset["last_minute_activity"] == 1:
        reasons.append(
            "Student activity increased sharply during the final days before the deadline."
        )
    if onset["risky_last_3"] >= 2:
        reasons.append(
            "Similar risky behaviour occurred in at least two of the previous three assessments."
        )
    for reason in reasons:
        st.write("•", reason)
else:
    st.write(
        "The student's academic history does not show a repeated procrastination trend."
    )
st.divider()
# ACTIVITY BURST VISUALIZATION
st.subheader("⚡ Last-Minute Activity Behaviour")
activity_chart = student_data[
    [
        "id_assessment",
        "clicks_previous_5d",
        "clicks_last_2d"
    ]
].copy()
activity_chart["id_assessment"] = (
    activity_chart["id_assessment"].astype(str)
)
activity_long = activity_chart.melt(
    id_vars="id_assessment",
    value_vars=[
        "clicks_previous_5d",
        "clicks_last_2d"
    ],
    var_name="Period",
    value_name="Clicks"
)
activity_long["Period"] = activity_long["Period"].replace({
    "clicks_previous_5d": "Earlier 5 Days",
    "clicks_last_2d": "Final 2 Days"
})
fig2 = px.bar(
    activity_long,
    x="id_assessment",
    y="Clicks",
    color="Period",
    barmode="group",
    title="Academic Activity Before Deadlines"
)
fig2.update_layout(
    xaxis_title="Assessment",
    yaxis_title="Platform Activity"
)
st.plotly_chart(
    fig2,
    width="stretch"
)
# HISTORY TABLE
st.subheader("📋 Student Activity History")
display_columns = [
    "id_assessment",
    "deadline",
    "date_submitted",
    "submission_behavior",
    "clicks_last_7d",
    "clicks_last_2d",
    "burst_ratio",
    "procrastination_score",
    "rolling_risk",
    "risk_level"
]
history = student_data[
    display_columns
].copy()
history.columns = [
    "Assessment",
    "Deadline Day",
    "Submitted Day",
    "Submission Behaviour",
    "Clicks (7 Days)",
    "Clicks (Final 2 Days)",
    "Activity Burst",
    "Task Risk",
    "Rolling Risk",
    "Risk Level"
]
st.dataframe(
    history,
    width="stretch",
    hide_index=True
)
# SYSTEM EXPLANATION
with st.expander("How ProTrack works"):
    st.write(
        """
        ProTrack analyses a sequence of academic activities rather than
        judging a student from a single late submission.

        It examines:

        • submission timing relative to deadlines

        • repeated near-deadline or late submissions

        • sudden increases in learning-platform activity

        • behaviour across the previous three assessments

        The system then identifies the point where repeated risky
        behaviour begins to emerge and provides an explanation based
        on the student's activity history.
        """
    )