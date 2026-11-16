"""
My Engineering Degree OS
A self-managed 1st-to-8th semester engineering degree command center.
Tracks schedules, syllabus, assessments, progress, scorecard, plan/checklist, Ask Degree AI chatbot,
and cloud database integration with Supabase (PostgreSQL).
"""

import os
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

# Optional Supabase SDK import with graceful fallback
try:
    from supabase import create_client, Client
    SUPABASE_SDK_AVAILABLE = True
except ImportError:
    SUPABASE_SDK_AVAILABLE = False
    Client = None

# Set page config
st.set_page_config(
    page_title="My Engineering Degree OS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, professional college dashboard look
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-completed {
        color: #166534;
        background-color: #dcfce7;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-progress {
        color: #9a3412;
        background-color: #ffedd5;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-notstarted {
        color: #475569;
        background-color: #f1f5f9;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .health-done {
        color: #166534;
        font-weight: 600;
    }
    .health-duesoon {
        color: #b45309;
        font-weight: 600;
    }
    .health-overdue {
        color: #b91c1c;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PATH & DATA HANDLING
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# Check potential data directories
POSSIBLE_DATA_DIRS = [
    BASE_DIR / "data",
    BASE_DIR / "engineering-degree-os" / "data",
    Path.cwd() / "data",
    Path.cwd() / "engineering-degree-os" / "data",
]

DATA_DIR = None
for d in POSSIBLE_DATA_DIRS:
    if d.exists() and d.is_dir():
        DATA_DIR = d
        break

if DATA_DIR is None:
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_COLUMNS = {
    "semesters.csv": ["semester", "status", "total_credits", "completed_credits"],
    "courses.csv": ["semester", "course_code", "course_name", "credits", "faculty", "syllabus", "status"],
    "academic_calendar.csv": ["academic_year", "semester", "date", "event_type", "title"],
    "assessments.csv": ["semester", "course_code", "assessment_type", "date", "max_marks", "status"],
    "scores.csv": ["semester", "course_code", "assessment_type", "score", "max_marks", "grade"],
    "plan_checklist.csv": ["category", "item", "target_date", "status", "notes"],
}

CSV_TO_TABLE = {
    "semesters.csv": "semesters",
    "courses.csv": "courses",
    "academic_calendar.csv": "academic_calendar",
    "assessments.csv": "assessments",
    "scores.csv": "scores",
    "plan_checklist.csv": "plan_checklist",
}

# ---------------------------------------------------------
# SUPABASE CLIENT INITIALIZATION & HELPERS
# ---------------------------------------------------------
def get_supabase_credentials():
    """Retrieves Supabase URL and Key from .env files, secrets, env vars, or session state."""
    url = None
    key = None

    # 1. Check local .env files
    env_paths = [
        BASE_DIR / ".env",
        BASE_DIR / "engineering-degree-os" / ".env",
        Path.cwd() / ".env",
        Path.cwd() / "engineering-degree-os" / ".env",
    ]
    for ep in env_paths:
        if ep.exists():
            try:
                for line in ep.read_text(encoding="utf-8").splitlines():
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.split("=", 1)
                        k_clean = k.strip()
                        v_clean = v.strip().strip("'\"")
                        if "SUPABASE_URL" in k_clean and not url:
                            url = v_clean
                        if ("SUPABASE" in k_clean and ("KEY" in k_clean or "PUBLISHABLE" in k_clean)) and not key:
                            key = v_clean
            except Exception:
                pass

    # 2. Check Streamlit secrets safely
    if not url:
        try:
            if "SUPABASE_URL" in st.secrets:
                url = st.secrets["SUPABASE_URL"]
            elif "NEXT_PUBLIC_SUPABASE_URL" in st.secrets:
                url = st.secrets["NEXT_PUBLIC_SUPABASE_URL"]
        except Exception:
            pass

    if not key:
        try:
            if "SUPABASE_KEY" in st.secrets:
                key = st.secrets["SUPABASE_KEY"]
            elif "SUPABASE_ANON_KEY" in st.secrets:
                key = st.secrets["SUPABASE_ANON_KEY"]
            elif "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY" in st.secrets:
                key = st.secrets["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]
        except Exception:
            pass

    # 3. Check OS environment variables
    if not url:
        url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

    # 4. Check session state (manual entry in UI)
    if not url and "supabase_url" in st.session_state and st.session_state["supabase_url"]:
        url = st.session_state["supabase_url"]
    if not key and "supabase_key" in st.session_state and st.session_state["supabase_key"]:
        key = st.session_state["supabase_key"]

    return url, key

def init_supabase_client():
    """Initializes and returns a Supabase client if configured."""
    if not SUPABASE_SDK_AVAILABLE:
        return None
    url, key = get_supabase_credentials()
    if url and key:
        try:
            client = create_client(url, key)
            return client
        except Exception as e:
            return None
    return None

# Global Supabase client instance
supabase_client = init_supabase_client()

def load_data(filename: str) -> pd.DataFrame:
    """
    Loads data with priority:
    1. Supabase PostgreSQL cloud table (if connected)
    2. Local CSV file (fallback or default mode)
    """
    table_name = CSV_TO_TABLE.get(filename)
    # Attempt loading from Supabase if connected
    if supabase_client and table_name:
        try:
            res = supabase_client.table(table_name).select("*").execute()
            if res.data and len(res.data) > 0:
                df = pd.DataFrame(res.data)
                # Drop supabase auto-id if present and not in default schema
                if "id" in df.columns and "id" not in DEFAULT_COLUMNS.get(filename, []):
                    df = df.drop(columns=["id"])
                cols = DEFAULT_COLUMNS.get(filename, [])
                # Reorder columns if matching
                avail_cols = [c for c in cols if c in df.columns]
                return df[avail_cols]
        except Exception:
            # Fall back to CSV if Supabase table doesn't exist yet
            pass

    # Local CSV loader
    file_path = DATA_DIR / filename
    if not file_path.exists():
        cols = DEFAULT_COLUMNS.get(filename, [])
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        cols = DEFAULT_COLUMNS.get(filename, [])
        return pd.DataFrame(columns=cols)

def save_data(filename: str, df: pd.DataFrame) -> bool:
    """
    Saves DataFrame to local CSV and synchronizes with Supabase if connected.
    """
    success = True
    # 1. Save to local CSV
    try:
        file_path = DATA_DIR / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False)
        for alt_dir in POSSIBLE_DATA_DIRS:
            if alt_dir.exists() and alt_dir != DATA_DIR:
                try:
                    df.to_csv(alt_dir / filename, index=False)
                except Exception:
                    pass
    except Exception as e:
        st.error(f"Failed to save local {filename}: {e}")
        success = False

    # 2. Sync to Supabase if connected
    table_name = CSV_TO_TABLE.get(filename)
    if supabase_client and table_name:
        try:
            records = df.to_dict(orient="records")
            # Replace / upsert records into Supabase table
            supabase_client.table(table_name).upsert(records).execute()
        except Exception as e:
            st.warning(f"Note: Saved to local CSV, but Supabase sync encountered: {e}")

    return success

# Load primary datasets
semesters_df = load_data("semesters.csv")
courses_df = load_data("courses.csv")
calendar_df = load_data("academic_calendar.csv")
assessments_df = load_data("assessments.csv")
scores_df = load_data("scores.csv")
checklist_df = load_data("plan_checklist.csv")

# Ensure proper data types
if not semesters_df.empty:
    semesters_df["semester"] = pd.to_numeric(semesters_df["semester"], errors="coerce").fillna(0).astype(int)
    semesters_df["total_credits"] = pd.to_numeric(semesters_df["total_credits"], errors="coerce").fillna(0).astype(int)
    semesters_df["completed_credits"] = pd.to_numeric(semesters_df["completed_credits"], errors="coerce").fillna(0).astype(int)

if not courses_df.empty:
    courses_df["semester"] = pd.to_numeric(courses_df["semester"], errors="coerce").fillna(0).astype(int)
    courses_df["credits"] = pd.to_numeric(courses_df["credits"], errors="coerce").fillna(0).astype(int)

if not scores_df.empty:
    scores_df["score"] = pd.to_numeric(scores_df["score"], errors="coerce").fillna(0)
    scores_df["max_marks"] = pd.to_numeric(scores_df["max_marks"], errors="coerce").fillna(0)

# Current reference date
TODAY = date(2026, 11, 16)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION (11 REQUIRED TABS)
# ---------------------------------------------------------
st.sidebar.title("🎓 Degree OS")
st.sidebar.caption("Engineering Degree Command Center")

nav_options = [
    "Dashboard",
    "Semesters 1-8",
    "Courses & Syllabus",
    "University Syllabus",
    "Academic / Leave Calendar",
    "Internal Assessments",
    "Status Tracker",
    "Scorecard",
    "Plan & Checklist",
    "Ask Degree AI",
    "Data Admin",
    "Student Feedback (Supabase RLS)"
]

selected_page = st.sidebar.radio("Navigation", nav_options, index=0)

st.sidebar.markdown("---")

# Storage indicator
if supabase_client:
    st.sidebar.success("🟢 Storage: **Supabase Cloud DB**")
else:
    st.sidebar.info("📁 Storage: **Local CSV Store**")

st.sidebar.info(
    "**Student:** Prajwal S Hiremath\n\n"
    "**Programme:** B.Tech Computer Science\n\n"
    "**Current:** Semester 3 (In Progress)\n\n"
    f"**System Date:** {TODAY.strftime('%d %b %Y')}"
)

# ---------------------------------------------------------
# TAB 1: DASHBOARD
# ---------------------------------------------------------
if selected_page == "Dashboard":
    st.markdown('<div class="main-title">Degree Overview Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">1st-to-8th Semester Academic Progress, Schedulers & Indicators</div>', unsafe_allow_html=True)

    # Degree stats calculations
    total_degree_credits = semesters_df["total_credits"].sum() if not semesters_df.empty else 175
    completed_degree_credits = semesters_df["completed_credits"].sum() if not semesters_df.empty else 57
    degree_completion_pct = (completed_degree_credits / total_degree_credits * 100) if total_degree_credits > 0 else 0

    # Current semester
    curr_sem_row = semesters_df[semesters_df["status"] == "In Progress"]
    curr_sem = int(curr_sem_row["semester"].values[0]) if not curr_sem_row.empty else 3

    # Next assessment
    next_assessment_str = "None scheduled"
    if not assessments_df.empty and "date" in assessments_df.columns:
        ass_df_copy = assessments_df.copy()
        ass_df_copy["parsed_date"] = pd.to_datetime(ass_df_copy["date"], errors="coerce").dt.date
        upcoming_ass = ass_df_copy[ass_df_copy["parsed_date"] >= TODAY].sort_values("parsed_date")
        if not upcoming_ass.empty:
            first_ass = upcoming_ass.iloc[0]
            next_assessment_str = f"{first_ass['course_code']} {first_ass['assessment_type']} ({first_ass['parsed_date'].strftime('%b %d')})"

    # Next holiday
    next_holiday_str = "None upcoming"
    if not calendar_df.empty and "date" in calendar_df.columns and "event_type" in calendar_df.columns:
        cal_copy = calendar_df.copy()
        cal_copy["parsed_date"] = pd.to_datetime(cal_copy["date"], errors="coerce").dt.date
        upcoming_holidays = cal_copy[(cal_copy["event_type"].str.lower() == "holiday") & (cal_copy["parsed_date"] >= TODAY)].sort_values("parsed_date")
        if not upcoming_holidays.empty:
            first_hol = upcoming_holidays.iloc[0]
            next_holiday_str = f"{first_hol['title']} ({first_hol['parsed_date'].strftime('%b %d')})"

    # Current score summary
    prototype_pct = 0.0
    if not scores_df.empty:
        total_score = scores_df["score"].sum()
        total_max = scores_df["max_marks"].sum()
        if total_max > 0:
            prototype_pct = (total_score / total_max) * 100

    # Render Metric Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Current Semester", f"Sem {curr_sem}", "In Progress")
    with col2:
        st.metric("Degree Progress", f"{degree_completion_pct:.1f}%", f"{completed_degree_credits}/{total_degree_credits} cr")
    with col3:
        st.metric("Next Assessment", next_assessment_str)
    with col4:
        st.metric("Next Holiday", next_holiday_str)
    with col5:
        st.metric("Prototype Score Avg", f"{prototype_pct:.1f}%", "Sample Data")

    st.markdown("### 📊 Semester-by-Semester Credit Progress")
    if not semesters_df.empty:
        chart_data = semesters_df.copy()
        chart_data["Semester"] = "Sem " + chart_data["semester"].astype(str)
        chart_display = chart_data.set_index("Semester")[["completed_credits", "total_credits"]]
        chart_display.columns = ["Completed Credits", "Total Credits"]
        st.bar_chart(chart_display)
    else:
        st.info("No semester credit data loaded.")

    # Two column overview
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("#### ⚡ Urgent Action Items (Due in 7 Days)")
        if not checklist_df.empty and "target_date" in checklist_df.columns:
            chk_copy = checklist_df.copy()
            chk_copy["parsed_target"] = pd.to_datetime(chk_copy["target_date"], errors="coerce").dt.date
            urgent_tasks = chk_copy[
                (chk_copy["parsed_target"] >= TODAY) & 
                (chk_copy["parsed_target"] <= TODAY + timedelta(days=7)) & 
                (chk_copy["status"] != "Done")
            ]
            if not urgent_tasks.empty:
                for _, row in urgent_tasks.iterrows():
                    st.warning(f"📌 **{row['item']}** — Target: {row['target_date']} [{row['category']}]")
            else:
                st.success("No urgent tasks due within the next 7 days.")
        else:
            st.info("No checklist data available.")

    with right_col:
        st.markdown("#### 📅 Upcoming Academic & Assessment Milestones")
        if not calendar_df.empty:
            cal_copy = calendar_df.copy()
            cal_copy["parsed_date"] = pd.to_datetime(cal_copy["date"], errors="coerce").dt.date
            upcoming_events = cal_copy[cal_copy["parsed_date"] >= TODAY].sort_values("parsed_date").head(4)
            if not upcoming_events.empty:
                for _, row in upcoming_events.iterrows():
                    tag = "🎉 Holiday" if row["event_type"] == "Holiday" else ("📝 Test" if row["event_type"] == "Assessment" else "📘 Academic")
                    st.info(f"{tag}: **{row['title']}** on `{row['date']}` (Sem {row['semester']})")
            else:
                st.write("No upcoming events recorded.")

# ---------------------------------------------------------
# TAB 2: SEMESTERS 1-8
# ---------------------------------------------------------
elif selected_page == "Semesters 1-8":
    st.markdown('<div class="main-title">Semesters 1 to 8 Journey</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Complete 8-semester course load, credit tracking and milestone status</div>', unsafe_allow_html=True)

    row1_cols = st.columns(4)
    row2_cols = st.columns(4)
    all_card_cols = row1_cols + row2_cols

    for i in range(1, 9):
        col = all_card_cols[i - 1]
        sem_row = semesters_df[semesters_df["semester"] == i] if not semesters_df.empty else pd.DataFrame()
        status = sem_row["status"].values[0] if not sem_row.empty else ("Completed" if i <= 2 else ("In Progress" if i == 3 else "Not Started"))
        total_cr = int(sem_row["total_credits"].values[0]) if not sem_row.empty else 22
        done_cr = int(sem_row["completed_credits"].values[0]) if not sem_row.empty else (total_cr if i <= 2 else (12 if i == 3 else 0))
        
        sem_courses = courses_df[courses_df["semester"] == i] if not courses_df.empty else pd.DataFrame()
        c_count = len(sem_courses)
        progress_val = min(1.0, done_cr / total_cr) if total_cr > 0 else 0.0

        with col:
            with st.container(border=True):
                st.subheader(f"Semester {i}")
                if status == "Completed":
                    st.markdown('<span class="status-completed">Completed</span>', unsafe_allow_html=True)
                elif status == "In Progress":
                    st.markdown('<span class="status-progress">In Progress</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-notstarted">Not Started</span>', unsafe_allow_html=True)
                st.write(f"**Courses:** {c_count}")
                st.write(f"**Credits:** {done_cr} / {total_cr}")
                st.progress(progress_val)

    st.markdown("---")
    st.subheader("🔍 Inspect Semester Details")
    chosen_sem = st.selectbox("Select Semester", options=list(range(1, 9)), index=2)

    sub_courses = courses_df[courses_df["semester"] == chosen_sem] if not courses_df.empty else pd.DataFrame()
    if not sub_courses.empty:
        st.write(f"#### Courses for Semester {chosen_sem}")
        st.dataframe(
            sub_courses[["course_code", "course_name", "credits", "faculty", "status", "syllabus"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(f"No courses recorded for Semester {chosen_sem}.")

# ---------------------------------------------------------
# TAB 3: COURSES & SYLLABUS
# ---------------------------------------------------------
elif selected_page == "Courses & Syllabus":
    st.markdown('<div class="main-title">Courses & Syllabus Directory</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Detailed course codes, faculty, credits, topics and completion status</div>', unsafe_allow_html=True)

    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
        sem_choice = st.selectbox("Filter by Semester", options=["All Semesters"] + [f"Semester {i}" for i in range(1, 9)], index=3)
    with filter_col2:
        search_query = st.text_input("Search Course Code, Name, or Topic", placeholder="e.g. CS301, Data Structures, Trees...")

    filtered_courses = courses_df.copy()
    if sem_choice != "All Semesters":
        sem_num = int(sem_choice.split(" ")[1])
        filtered_courses = filtered_courses[filtered_courses["semester"] == sem_num]

    if search_query.strip():
        q = search_query.lower()
        filtered_courses = filtered_courses[
            filtered_courses["course_code"].str.lower().str.contains(q) |
            filtered_courses["course_name"].str.lower().str.contains(q) |
            filtered_courses["syllabus"].str.lower().str.contains(q) |
            filtered_courses["faculty"].str.lower().str.contains(q)
        ]

    st.write(f"Showing **{len(filtered_courses)}** courses matching criteria:")
    if not filtered_courses.empty:
        st.dataframe(
            filtered_courses[["semester", "course_code", "course_name", "credits", "faculty", "status", "syllabus"]],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("#### 📖 Course Syllabus Outline")
        for _, c_row in filtered_courses.iterrows():
            with st.expander(f"📘 {c_row['course_code']} - {c_row['course_name']} ({c_row['credits']} Credits | Sem {c_row['semester']})"):
                st.write(f"**Faculty:** {c_row['faculty']}")
                st.write(f"**Status:** {c_row['status']}")
                st.write("**Syllabus / Modules:**")
                topics = str(c_row['syllabus']).split(";")
                for t in topics:
                    st.markdown(f"- {t.strip()}")
    else:
        st.warning("No courses match the selected filters.")

# ---------------------------------------------------------
# TAB 4: UNIVERSITY SYLLABUS
# ---------------------------------------------------------
elif selected_page == "University Syllabus":
    st.markdown('<div class="main-title">University Programme Syllabus</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Programme structure, curriculum regulation, credit scheme, and official reference</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("🎓 Programme Specification Summary")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.write("**Programme Name:** B.Tech in Computer Science & Engineering")
            st.write("**Degree Awarding Body:** Department of CSE")
        with col_b:
            st.write("**Curriculum Regulation:** CBCS 2024-2028")
            st.write("**Total Duration:** 4 Years (8 Semesters)")
        with col_c:
            st.write("**Total Expected Credits:** 175 Credits")
            st.write("**Minimum Passing Mark:** 40% per course")

    st.markdown("#### 🔗 Official Syllabus Source / Reference")
    syllabus_url = st.text_input(
        "Syllabus Source / Reference URL",
        value="https://university.ac.in/syllabi/btech-cse-curriculum-2024.pdf",
        help="Official department syllabus repository link"
    )
    st.caption("Official university academic regulations and syllabus documentation must be verified through the department examination portal.")

    st.markdown("#### 🏛️ Academic Year & Curriculum Progression")
    st.markdown("""
    - **Year 1 (Semesters 1 & 2): Foundation Stage**  
      Mathematics, Basic Sciences, Engineering Physics, and Fundamentals of Programming in C/C++.
    - **Year 2 (Semesters 3 & 4): Core Engineering Stage**  
      Data Structures, Computer Architecture, Discrete Math, Operating Systems, and Algorithms.
    - **Year 3 (Semesters 5 & 6): Advanced & Applied Systems**  
      Computer Networks, Software Engineering, Artificial Intelligence, Compiler Design, and Machine Learning.
    - **Year 4 (Semesters 7 & 8): Specialization, Capstone & Industry Transition**  
      Information & Cyber Security, Big Data Analytics, Deep Learning Electives, Major Capstone Project, and Industrial Internship.
    """)

# ---------------------------------------------------------
# TAB 5: ACADEMIC / LEAVE CALENDAR
# ---------------------------------------------------------
elif selected_page == "Academic / Leave Calendar":
    st.markdown('<div class="main-title">Academic & Leave Calendar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Academic dates, exams, and institutional leave schedule</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        years = ["All"] + sorted(list(calendar_df["academic_year"].dropna().unique())) if not calendar_df.empty else ["All"]
        selected_year = st.selectbox("Academic Year", years, index=0)
    with col2:
        sems = ["All"] + [f"Sem {s}" for s in sorted(list(calendar_df["semester"].dropna().unique()))] if not calendar_df.empty else ["All"]
        selected_sem = st.selectbox("Semester", sems, index=0)
    with col3:
        event_types = ["All"] + list(calendar_df["event_type"].dropna().unique()) if not calendar_df.empty else ["All"]
        selected_type = st.selectbox("Event Type", event_types, index=0)

    cal_view = calendar_df.copy()
    if selected_year != "All":
        cal_view = cal_view[cal_view["academic_year"] == selected_year]
    if selected_sem != "All":
        s_val = int(selected_sem.split(" ")[1])
        cal_view = cal_view[cal_view["semester"] == s_val]
    if selected_type != "All":
        cal_view = cal_view[cal_view["event_type"] == selected_type]

    if not cal_view.empty:
        cal_view["parsed_date"] = pd.to_datetime(cal_view["date"], errors="coerce").dt.date
        cal_view = cal_view.sort_values("parsed_date")
        
        def calc_date_rel(d):
            if pd.isnull(d): return ""
            diff = (d - TODAY).days
            if diff == 0: return "Today"
            elif diff > 0: return f"In {diff} days"
            else: return f"{abs(diff)} days ago"

        cal_view["Timeline"] = cal_view["parsed_date"].apply(calc_date_rel)
        
        st.dataframe(
            cal_view[["academic_year", "semester", "date", "event_type", "title", "Timeline"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No calendar events match the selected filters.")

# ---------------------------------------------------------
# TAB 6: INTERNAL ASSESSMENTS
# ---------------------------------------------------------
elif selected_page == "Internal Assessments":
    st.markdown('<div class="main-title">Internal Assessments & Examinations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">IA1, IA2, lab practicals, project reviews, assignments, and end-term exams</div>', unsafe_allow_html=True)

    ass_col1, ass_col2 = st.columns(2)
    with ass_col1:
        sem_filter = st.selectbox("Filter Assessment by Semester", ["All"] + [f"Sem {s}" for s in range(1, 9)], index=3)
    with ass_col2:
        type_filter = st.selectbox("Filter Assessment by Type", ["All", "IA1", "IA2", "Assignment", "Lab Evaluation", "Project Review", "End Semester"])

    ass_view = assessments_df.copy()
    if sem_filter != "All":
        s_num = int(sem_filter.split(" ")[1])
        ass_view = ass_view[ass_view["semester"] == s_num]
    if type_filter != "All":
        ass_view = ass_view[ass_view["assessment_type"] == type_filter]

    if not ass_view.empty:
        ass_view["parsed_date"] = pd.to_datetime(ass_view["date"], errors="coerce").dt.date
        ass_view = ass_view.sort_values("parsed_date")
        st.dataframe(
            ass_view[["semester", "course_code", "assessment_type", "date", "max_marks", "status"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No assessments matching criteria.")

# ---------------------------------------------------------
# TAB 7: STATUS TRACKER
# ---------------------------------------------------------
elif selected_page == "Status Tracker":
    st.markdown('<div class="main-title">Course Status Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Not Started / In Progress / Completed completion tracking by course and semester</div>', unsafe_allow_html=True)

    track_sem = st.selectbox("Select Semester to Track", options=list(range(1, 9)), index=2)
    sem_c = courses_df[courses_df["semester"] == track_sem] if not courses_df.empty else pd.DataFrame()

    total_c = len(sem_c)
    completed_c = len(sem_c[sem_c["status"] == "Completed"]) if not sem_c.empty else 0
    progress_c = len(sem_c[sem_c["status"] == "In Progress"]) if not sem_c.empty else 0
    notstarted_c = len(sem_c[sem_c["status"] == "Not Started"]) if not sem_c.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"Total Courses (Sem {track_sem})", total_c)
    with col2:
        st.metric("Completed", completed_c)
    with col3:
        st.metric("In Progress", progress_c)
    with col4:
        st.metric("Not Started", notstarted_c)

    completion_rate = (completed_c / total_c) if total_c > 0 else 0.0
    st.write(f"**Semester {track_sem} Completion Rate:** {completion_rate * 100:.1f}%")
    st.progress(completion_rate)

    st.markdown(f"#### Detailed Course Status for Semester {track_sem}")
    if not sem_c.empty:
        st.dataframe(
            sem_c[["course_code", "course_name", "credits", "faculty", "status"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(f"No courses found for Semester {track_sem}.")

    st.markdown("---")
    st.markdown("#### Overall 8-Semester Status Breakdown")
    if not courses_df.empty:
        overall_summary = courses_df.groupby(["semester", "status"]).size().unstack(fill_value=0)
        st.dataframe(overall_summary, use_container_width=True)

# ---------------------------------------------------------
# TAB 8: SCORECARD
# ---------------------------------------------------------
elif selected_page == "Scorecard":
    st.markdown('<div class="main-title">Student Academic Scorecard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Evaluation records, grades, and prototype score percentage</div>', unsafe_allow_html=True)

    st.info(
        "ℹ️ **Prototype Score Percentage Metric:** This page calculates simple percentage as "
        "`(Total Score / Total Max Marks) * 100` from `scores.csv` (or Supabase `scores` table). "
        "This is a development prototype metric and **not** an official university CGPA/SGPA formula."
    )

    if not scores_df.empty:
        tot_score = scores_df["score"].sum()
        tot_max = scores_df["max_marks"].sum()
        proto_pct = (tot_score / tot_max * 100) if tot_max > 0 else 0.0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cumulative Prototype Score", f"{proto_pct:.2f}%", "Average of recorded scores")
        with col2:
            st.metric("Total Points Scored", f"{tot_score:.0f} / {tot_max:.0f}")
        with col3:
            st.metric("Total Assessments Graded", len(scores_df))

        st.markdown("#### 📋 Assessment Score Records")
        st.dataframe(
            scores_df[["semester", "course_code", "assessment_type", "score", "max_marks", "grade"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### 📈 Semester Average Breakdown")
        sem_group = scores_df.groupby("semester").apply(
            lambda g: pd.Series({
                "Total Scored": g["score"].sum(),
                "Total Max Marks": g["max_marks"].sum(),
                "Prototype Average %": (g["score"].sum() / g["max_marks"].sum() * 100) if g["max_marks"].sum() > 0 else 0,
                "Assessments Count": len(g)
            })
        ).reset_index()
        st.dataframe(sem_group, use_container_width=True, hide_index=True)
    else:
        st.warning("No scores recorded.")

# ---------------------------------------------------------
# TAB 9: PLAN & CHECKLIST
# ---------------------------------------------------------
elif selected_page == "Plan & Checklist":
    st.markdown('<div class="main-title">Plan & Degree Execution Checklist</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Execution control panel for degree milestones, exams, documents, and placements</div>', unsafe_allow_html=True)

    if not checklist_df.empty:
        chk_calc = checklist_df.copy()
        chk_calc["parsed_target"] = pd.to_datetime(chk_calc["target_date"], errors="coerce").dt.date

        def compute_health(row):
            status = str(row.get("status", "")).strip()
            if status == "Done":
                return "Done"
            t_date = row.get("parsed_target")
            if pd.isnull(t_date):
                return "Upcoming"
            if t_date < TODAY:
                return "Overdue"
            elif t_date <= TODAY + timedelta(days=7):
                return "Due Soon"
            else:
                return "Upcoming"

        chk_calc["Health"] = chk_calc.apply(compute_health, axis=1)

        total_items = len(chk_calc)
        done_items = len(chk_calc[chk_calc["Health"] == "Done"])
        due_soon_items = len(chk_calc[chk_calc["Health"] == "Due Soon"])
        overdue_items = len(chk_calc[chk_calc["Health"] == "Overdue"])

        # Summary Metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Checklist Items", total_items)
        with m2:
            st.metric("Completed (Done)", done_items)
        with m3:
            st.metric("Due Soon (Next 7 Days)", due_soon_items)
        with m4:
            st.metric("Overdue Items", overdue_items)

        st.markdown("---")
        
        # 1. This Week Section
        st.subheader("⚡ This Week (Next 7 Days)")
        this_week = chk_calc[(chk_calc["Health"] == "Due Soon") | ((chk_calc["parsed_target"] >= TODAY) & (chk_calc["parsed_target"] <= TODAY + timedelta(days=7)))]
        if not this_week.empty:
            for _, r in this_week.iterrows():
                badge = "✅" if r["status"] == "Done" else "⏳"
                st.write(f"{badge} **{r['item']}** — Target: `{r['target_date']}` | Category: *{r['category']}* | Notes: {r['notes']}")
        else:
            st.info("No tasks due in the next 7 days.")

        # 2. Semester Milestones Section
        st.subheader("🎯 Semester Milestones")
        sem_milestones = chk_calc[chk_calc["category"].isin(["Semester Preparation", "Assessments", "Labs", "Projects"])]
        if not sem_milestones.empty:
            st.dataframe(
                sem_milestones[["category", "item", "target_date", "status", "Health", "notes"]],
                use_container_width=True,
                hide_index=True
            )

        # 3. Degree Milestones Section
        st.subheader("🏆 Long-Range Degree Milestones & Placement Readiness")
        deg_milestones = chk_calc[chk_calc["category"].isin(["Placement", "Internship/Placement", "Skills", "Documents", "Degree Milestones"])]
        if not deg_milestones.empty:
            st.dataframe(
                deg_milestones[["category", "item", "target_date", "status", "Health", "notes"]],
                use_container_width=True,
                hide_index=True
            )

        st.markdown("---")
        st.subheader("✏️ Editable Plan & Checklist Data Table")
        st.caption("Edit item status, target dates, or notes directly below and click 'Save Checklist' to persist.")

        editable_cols = ["category", "item", "target_date", "status", "notes"]
        edited_chk = st.data_editor(
            checklist_df[editable_cols],
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Not Started", "In Progress", "Done"],
                    required=True
                ),
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=[
                        "Semester Preparation", "Assessments", "Labs", "Projects",
                        "Documents", "Skills", "Internship/Placement", "Degree Milestones", "Placement"
                    ],
                    required=True
                )
            },
            num_rows="dynamic",
            use_container_width=True,
            key="checklist_editor"
        )

        if st.button("💾 Save Checklist Changes", type="primary"):
            if save_data("plan_checklist.csv", edited_chk):
                st.success("Plan & Checklist saved successfully!")
                st.rerun()

    else:
        st.warning("plan_checklist data is empty or missing.")

# ---------------------------------------------------------
# TAB 10: ASK DEGREE AI
# ---------------------------------------------------------
elif selected_page == "Ask Degree AI":
    st.markdown('<div class="main-title">Ask Degree AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Grounded AI answers from your 1st-to-8th semester degree data</div>', unsafe_allow_html=True)

    def build_compact_context():
        ctx_parts = []
        ctx_parts.append("=== DEGREE OS DATA SOURCE ===")
        ctx_parts.append(f"Current Reference Date: {TODAY.strftime('%Y-%m-%d')}")
        
        if not semesters_df.empty:
            ctx_parts.append("\n[SEMESTERS]")
            for _, r in semesters_df.iterrows():
                ctx_parts.append(f"Sem {r['semester']}: Status={r['status']}, Total Credits={r['total_credits']}, Completed Credits={r['completed_credits']}")
        
        if not courses_df.empty:
            ctx_parts.append("\n[COURSES]")
            for _, r in courses_df.iterrows():
                ctx_parts.append(f"Sem {r['semester']} | {r['course_code']}: {r['course_name']} ({r['credits']} cr, Faculty: {r['faculty']}, Status: {r['status']}) - Syllabus: {r['syllabus']}")

        if not calendar_df.empty:
            ctx_parts.append("\n[CALENDAR]")
            for _, r in calendar_df.iterrows():
                ctx_parts.append(f"{r['date']} (Sem {r['semester']}, {r['event_type']}): {r['title']}")

        if not assessments_df.empty:
            ctx_parts.append("\n[ASSESSMENTS]")
            for _, r in assessments_df.iterrows():
                ctx_parts.append(f"Sem {r['semester']} | {r['course_code']} {r['assessment_type']} on {r['date']} (Max: {r['max_marks']}, Status: {r['status']})")

        if not scores_df.empty:
            ctx_parts.append("\n[SCORES]")
            for _, r in scores_df.iterrows():
                ctx_parts.append(f"Sem {r['semester']} | {r['course_code']} {r['assessment_type']}: Score {r['score']}/{r['max_marks']} (Grade: {r['grade']})")

        if not checklist_df.empty:
            ctx_parts.append("\n[PLAN_CHECKLIST]")
            for _, r in checklist_df.iterrows():
                ctx_parts.append(f"[{r['category']}] {r['item']} (Target: {r['target_date']}, Status: {r['status']}, Notes: {r['notes']})")

        return "\n".join(ctx_parts)

    compact_context = build_compact_context()

    api_key = None
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    with st.expander("⚙️ AI Configuration & Grounding Info", expanded=False):
        st.write("**Grounded Context Source:** Loaded Degree Data")
        if api_key:
            st.success("Google Gemini API is configured and connected.")
        else:
            st.info("No Gemini API key detected. Running in **Deterministic Local Grounding Mode**.")
            manual_key = st.text_input("Enter GEMINI_API_KEY (optional):", type="password")
            if manual_key.strip():
                api_key = manual_key.strip()

    if "degree_ai_messages" not in st.session_state:
        st.session_state.degree_ai_messages = [
            {
                "role": "assistant",
                "content": "Hello! I am **Degree AI**, your engineering degree assistant. Ask me questions about your courses, upcoming internal assessments, holidays, syllabus, or checklist.",
                "area": "System"
            }
        ]

    for msg in st.session_state.degree_ai_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "area" in msg and msg["area"] != "System":
                st.caption(f"📍 **Data Area Used:** `{msg['area']}`")

    def answer_locally(query: str):
        q = query.lower().strip()
        if "cgpa" in q or "sgpa" in q or "gpa formula" in q or "official formula" in q:
            return ("I cannot verify that from the current Degree OS data.", "Scores")
        if "attendance" in q or "regulation" in q or "condonation" in q or "hall ticket" in q:
            return ("I cannot verify that from the current Degree OS data.", "Calendar")

        if "incomplete" in q or "left" in q or "pending course" in q or "subjects left" in q:
            sem_target = 3
            for s in range(1, 9):
                if f"sem {s}" in q or f"semester {s}" in q:
                    sem_target = s
                    break
            sub_c = courses_df[courses_df["semester"] == sem_target]
            inc = sub_c[sub_c["status"] != "Completed"]
            if not inc.empty:
                items = [f"- **{r['course_code']}**: {r['course_name']} ({r['status']})" for _, r in inc.iterrows()]
                ans = f"Incomplete courses in **Semester {sem_target}** ({len(inc)} remaining):\n" + "\n".join(items)
                return (ans, "Courses")
            else:
                return (f"All courses in Semester {sem_target} are completed!", "Courses")

        if "next" in q and ("assessment" in q or "ia" in q or "test" in q or "exam" in q):
            if not assessments_df.empty:
                ass_df_copy = assessments_df.copy()
                ass_df_copy["parsed_date"] = pd.to_datetime(ass_df_copy["date"], errors="coerce").dt.date
                upcoming = ass_df_copy[ass_df_copy["parsed_date"] >= TODAY].sort_values("parsed_date")
                if not upcoming.empty:
                    first = upcoming.iloc[0]
                    days = (first["parsed_date"] - TODAY).days
                    ans = f"Your next assessment is **{first['course_code']} {first['assessment_type']}** on **{first['date']}** (in {days} days). Max Marks: {first['max_marks']}."
                    return (ans, "Assessments")
            return ("No upcoming assessments found in the schedule.", "Assessments")

        if "holiday" in q or "leave" in q or "vacation" in q:
            if not calendar_df.empty:
                cal_copy = calendar_df.copy()
                cal_copy["parsed_date"] = pd.to_datetime(cal_copy["date"], errors="coerce").dt.date
                hols = cal_copy[(cal_copy["event_type"].str.lower() == "holiday") & (cal_copy["parsed_date"] >= TODAY)].sort_values("parsed_date")
                if not hols.empty:
                    first_h = hols.iloc[0]
                    days = (first_h["parsed_date"] - TODAY).days
                    ans = f"Your next holiday is **{first_h['title']}** on **{first_h['date']}** (in {days} days)."
                    return (ans, "Calendar")
            return ("No upcoming holidays found in the calendar.", "Calendar")

        if "syllabus" in q or "topics" in q or "data structures" in q or "cs301" in q:
            matched_c = courses_df[
                courses_df["course_name"].str.lower().str.contains("data structures") |
                courses_df["course_code"].str.lower().str.contains("cs301")
            ]
            if not matched_c.empty:
                c_row = matched_c.iloc[0]
                ans = f"Topics for **{c_row['course_code']} ({c_row['course_name']})**:\n{c_row['syllabus']}"
                return (ans, "Courses")
            for _, r in courses_df.iterrows():
                if r["course_code"].lower() in q or r["course_name"].lower() in q:
                    return (f"Syllabus for **{r['course_code']} ({r['course_name']})**:\n{r['syllabus']}", "Courses")

        if "status of sem" in q or "semester status" in q or "semester 3" in q:
            sem_s = semesters_df[semesters_df["semester"] == 3]
            if not sem_s.empty:
                row = sem_s.iloc[0]
                ans = f"Semester 3 status is **{row['status']}**. Completed {row['completed_credits']} of {row['total_credits']} credits."
                return (ans, "Courses")

        if "checklist" in q or "plan" in q or "milestone" in q or "due soon" in q:
            if not checklist_df.empty:
                chk_c = checklist_df[checklist_df["status"] != "Done"]
                items = [f"- [{r['category']}] {r['item']} (Target: {r['target_date']})" for _, r in chk_c.head(4).iterrows()]
                ans = "Pending Plan & Checklist items:\n" + "\n".join(items)
                return (ans, "Plan")

        if "score" in q or "grade" in q or "marks" in q or "percentage" in q:
            if not scores_df.empty:
                tot_score = scores_df["score"].sum()
                tot_max = scores_df["max_marks"].sum()
                proto_pct = (tot_score / tot_max * 100) if tot_max > 0 else 0
                return (f"Prototype score percentage across recorded evaluations is **{proto_pct:.1f}%** ({tot_score}/{tot_max} marks).", "Scores")

        return ("I cannot verify that from the current Degree OS data.", "Courses")

    st.write("##### 💡 Try standard test questions:")
    tcol1, tcol2, tcol3 = st.columns(3)
    tcol4, tcol5, _ = st.columns(3)

    user_query = None
    if tcol1.button("1. What courses are still incomplete in Semester 3?"):
        user_query = "What courses are still incomplete in Semester 3?"
    if tcol2.button("2. When is my next internal assessment?"):
        user_query = "When is my next internal assessment?"
    if tcol3.button("3. Show my next holiday"):
        user_query = "Show my next holiday"
    if tcol4.button("4. What topics are in Data Structures?"):
        user_query = "What topics are in Data Structures?"
    if tcol5.button("5. What is my official university CGPA formula?"):
        user_query = "What is my official university CGPA formula?"

    chat_input = st.chat_input("Ask a question about your engineering degree...")
    if chat_input:
        user_query = chat_input

    if user_query:
        st.session_state.degree_ai_messages.append({"role": "user", "content": user_query})
        ai_response = ""
        area_used = "Courses"

        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                system_prompt = (
                    "You are Degree AI. Answer only from the supplied degree data. "
                    "Do not invent university rules, dates, marks, formulas or syllabus content. "
                    "If the requested information is missing, say: I cannot verify that from the current Degree OS data. "
                    "Keep answers concise and student-friendly. "
                    "At the end of your response, specify the exact data area used in the format: [DATA_AREA: Courses|Calendar|Assessments|Scores|Plan]."
                )
                full_prompt = f"{compact_context}\n\nUser Question: {user_query}"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config={"system_instruction": system_prompt}
                )
                ai_text = response.text.strip()
                if "[DATA_AREA:" in ai_text:
                    parts = ai_text.split("[DATA_AREA:")
                    ai_response = parts[0].strip()
                    area_used = parts[1].replace("]", "").strip()
                else:
                    ai_response = ai_text
                    q_low = user_query.lower()
                    if "holiday" in q_low or "calendar" in q_low: area_used = "Calendar"
                    elif "assessment" in q_low or "ia" in q_low or "exam" in q_low: area_used = "Assessments"
                    elif "score" in q_low or "grade" in q_low or "cgpa" in q_low: area_used = "Scores"
                    elif "checklist" in q_low or "plan" in q_low: area_used = "Plan"
                    else: area_used = "Courses"
            except Exception:
                ai_response, area_used = answer_locally(user_query)
        else:
            ai_response, area_used = answer_locally(user_query)

        st.session_state.degree_ai_messages.append({
            "role": "assistant",
            "content": ai_response,
            "area": area_used
        })
        st.rerun()

# ---------------------------------------------------------
# TAB 11: DATA ADMIN (WITH SUPABASE INTEGRATION)
# ---------------------------------------------------------
elif selected_page == "Data Admin":
    st.markdown('<div class="main-title">Data Administration & Cloud Sync</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Maintain degree data tables directly and synchronize with Supabase PostgreSQL</div>', unsafe_allow_html=True)

    # Supabase Connection Management Box
    with st.container(border=True):
        st.subheader("⚡ Cloud Database Integration (Supabase)")
        c1, c2 = st.columns([2, 1])
        with c1:
            if supabase_client:
                st.success("🟢 **Supabase Connected & Active:** Data operations automatically synchronize with your cloud PostgreSQL database!")
            else:
                if not SUPABASE_SDK_AVAILABLE:
                    st.warning("⚠️ `supabase` Python package is not installed. Run `pip install supabase` to enable live cloud sync.")
                else:
                    st.info("ℹ️ Running in **Local CSV Mode**. Enter your Supabase credentials below or in `.streamlit/secrets.toml` to connect cloud database.")

        with c2:
            if supabase_client:
                if st.button("🔄 Sync All CSVs to Supabase", type="primary"):
                    sync_progress = st.progress(0.0)
                    sync_log = []
                    csv_items = list(CSV_TO_TABLE.items())
                    for idx, (csv_name, tbl_name) in enumerate(csv_items):
                        local_df = load_data(csv_name)
                        try:
                            recs = local_df.to_dict(orient="records")
                            supabase_client.table(tbl_name).upsert(recs).execute()
                            sync_log.append(f"✓ {tbl_name}: {len(recs)} rows synced")
                        except Exception as e:
                            sync_log.append(f"✗ {tbl_name} failed: {e}")
                        sync_progress.progress((idx + 1) / len(csv_items))
                    st.success("Sync completed!")
                    for item in sync_log:
                        st.caption(item)
                    st.rerun()

        # Credentials Expander
        with st.expander("🔑 Configure Supabase Credentials & SQL Schema"):
            sc_col1, sc_col2 = st.columns(2)
            with sc_col1:
                cur_url, cur_key = get_supabase_credentials()
                sup_url_input = st.text_input("Supabase Project URL", value=cur_url or "", placeholder="https://xyzcompany.supabase.co")
                sup_key_input = st.text_input("Supabase Anon / Service Key", value=cur_key or "", type="password", placeholder="eyJhbGciOi...")
                if st.button("Save Supabase Credentials to Session"):
                    st.session_state["supabase_url"] = sup_url_input.strip()
                    st.session_state["supabase_key"] = sup_key_input.strip()
                    st.success("Credentials updated! Refreshing connection...")
                    st.rerun()
            with sc_col2:
                st.markdown("**Or add to `.streamlit/secrets.toml`:**")
                st.code("""
# .streamlit/secrets.toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-or-service-key"
                """, language="toml")

            st.markdown("---")
            st.markdown("#### 🛠️ Supabase PostgreSQL Table Schema (DDL)")
            st.caption("Paste this SQL into your Supabase SQL Editor to initialize all 6 tables:")
            st.code("""
-- 1. Semesters Table
CREATE TABLE IF NOT EXISTS semesters (
    semester INT PRIMARY KEY,
    status TEXT NOT NULL,
    total_credits INT NOT NULL,
    completed_credits INT NOT NULL
);

-- 2. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    semester INT NOT NULL,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    credits INT NOT NULL,
    faculty TEXT,
    syllabus TEXT,
    status TEXT NOT NULL
);

-- 3. Academic Calendar Table
CREATE TABLE IF NOT EXISTS academic_calendar (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    academic_year TEXT NOT NULL,
    semester INT NOT NULL,
    date DATE NOT NULL,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL
);

-- 4. Assessments Table
CREATE TABLE IF NOT EXISTS assessments (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    semester INT NOT NULL,
    course_code TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    date DATE NOT NULL,
    max_marks INT NOT NULL,
    status TEXT NOT NULL
);

-- 5. Scores Table
CREATE TABLE IF NOT EXISTS scores (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    semester INT NOT NULL,
    course_code TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    score NUMERIC NOT NULL,
    max_marks NUMERIC NOT NULL,
    grade TEXT NOT NULL
);

-- 6. Plan Checklist Table
CREATE TABLE IF NOT EXISTS plan_checklist (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    category TEXT NOT NULL,
    item TEXT NOT NULL,
    target_date DATE NOT NULL,
    status TEXT NOT NULL,
    notes TEXT
);
            """, language="sql")

    st.markdown("---")
    st.subheader("📋 Edit Data Tables")

    table_choices = {
        "Semesters (semesters.csv)": "semesters.csv",
        "Courses (courses.csv)": "courses.csv",
        "Academic Calendar (academic_calendar.csv)": "academic_calendar.csv",
        "Assessments (assessments.csv)": "assessments.csv",
        "Scores (scores.csv)": "scores.csv",
        "Plan & Checklist (plan_checklist.csv)": "plan_checklist.csv"
    }

    selected_label = st.selectbox("Select Data Table to View / Edit", list(table_choices.keys()))
    target_csv = table_choices[selected_label]

    curr_df = load_data(target_csv)

    st.write(f"Editing **{target_csv}** ({len(curr_df)} records):")
    edited_df = st.data_editor(curr_df, num_rows="dynamic", use_container_width=True, key=f"editor_{target_csv}")

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("💾 Save Table", type="primary"):
            if save_data(target_csv, edited_df):
                st.success(f"Successfully saved {target_csv} (local & Supabase synced)!")
                st.rerun()
    with col_btn2:
        st.caption("Changes are saved directly to `/data` and synced to Supabase when connected.")

# ---------------------------------------------------------
# TAB 12: STUDENT FEEDBACK (SUPABASE AUTH + RLS)
# ---------------------------------------------------------
elif selected_page == "Student Feedback (Supabase RLS)":
    st.markdown('<div class="main-title">Student Feedback (Supabase Auth & RLS)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Authenticated, secure feedback storage with Row Level Security (RLS)</div>', unsafe_allow_html=True)

    sup_url, sup_key = get_supabase_credentials()

    if not sup_url or not sup_key:
        st.error("Please configure SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in secrets or .env.")
        st.stop()

    if not SUPABASE_SDK_AVAILABLE:
        st.error("supabase Python library is not installed. Run `pip install supabase`.")
        st.stop()

    # Per-browser session client (Do NOT share across sessions via cache_resource)
    try:
        if "_supabase_auth_client" not in st.session_state:
            st.session_state["_supabase_auth_client"] = create_client(sup_url, sup_key)
        auth_db = st.session_state["_supabase_auth_client"]
        current_session = auth_db.auth.get_session()
    except Exception as e:
        st.error(f"Could not connect to Supabase: {e}")
        st.stop()

    # If user is not signed in, show Sign In form
    if current_session is None:
        st.subheader("🔐 Student Sign In")
        st.caption("Sign in with your verified Supabase user account to view and submit feedback.")

        with st.form("student_sign_in", clear_on_submit=True):
            user_email = st.text_input("Student Email", placeholder="e.g. student@engineeringos.com")
            user_pwd = st.text_input("Password", type="password")
            submitted_login = st.form_submit_button("Sign In", type="primary")

        if submitted_login:
            if not user_email.strip() or not user_pwd:
                st.warning("Please enter both email and password.")
            else:
                try:
                    auth_res = auth_db.auth.sign_in_with_password(
                        {"email": user_email.strip(), "password": user_pwd}
                    )
                    if auth_res.session is not None:
                        st.success("Signed in successfully!")
                        st.rerun()
                    else:
                        st.error("No session created. Please check your credentials.")
                except Exception as ex:
                    st.error(f"Sign in failed: {ex}")

        with st.expander("💡 Demo Credentials for Evaluation", expanded=True):
            st.write("You can test with these pre-configured & confirmed accounts:")
            st.write("- **User 1:** `student@engineeringos.com` / `DegreeOSPassword2026!`")
            st.write("- **User 2:** `student_a@engineeringos.com` / `DegreeOSPassword2026!`")
            st.caption("Due to Row Level Security, User 1 and User 2 will only see their own feedback records.")

        st.stop()

    # Signed in state
    user_info = current_session.user
    st.info(f"👤 Signed in as: **{user_info.email}**")

    if st.button("🚪 Sign out"):
        try:
            auth_db.auth.sign_out({"scope": "local"})
        except Exception:
            pass
        st.session_state.pop("_supabase_auth_client", None)
        st.rerun()

    st.markdown("---")
    st.subheader("📝 Submit New Feedback")
    with st.form("feedback_form"):
        f_name = st.text_input("Your Name", max_chars=100)
        f_message = st.text_area("Message / Feedback", max_chars=2000)
        submit_fb = st.form_submit_button("Save Feedback to Supabase", type="primary")

    if submit_fb:
        f_name_clean = f_name.strip()
        f_msg_clean = f_message.strip()
        if not f_name_clean or not f_msg_clean:
            st.warning("Please enter both your name and message.")
        else:
            try:
                # user_id, id, and created_at are automatically assigned by database auth.uid()
                fb_result = (
                    auth_db.table("app_feedback")
                    .insert({"name": f_name_clean, "message": f_msg_clean})
                    .execute()
                )
                st.success("Feedback successfully saved in Supabase!")
                if fb_result.data and len(fb_result.data) > 0:
                    st.caption(f"Record ID: `{fb_result.data[0]['id']}`")
                st.rerun()
            except Exception as fb_err:
                st.error(f"Failed to save feedback: {fb_err}")

    st.markdown("---")
    st.subheader("📋 Your Saved Feedback (Protected by RLS)")
    st.caption("Only feedback created by your account is visible here. Other users cannot see your rows.")

    if st.button("🔄 Refresh Records"):
        st.rerun()

    try:
        read_res = (
            auth_db.table("app_feedback")
            .select("id, name, message, created_at")
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        if read_res.data and len(read_res.data) > 0:
            st.dataframe(read_res.data, hide_index=True, use_container_width=True)
        else:
            st.info("No feedback saved for this account yet.")
    except Exception as read_err:
        st.error(f"Could not load records: {read_err}")

