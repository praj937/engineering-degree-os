"""
My Engineering Degree OS
A self-managed 1st-to-8th semester engineering degree command center.
Architected for enterprise-grade student UX with Supabase cloud database,
Google Gemini AI grounding, and full 8-semester academic tracking.
"""

import os
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# ---------------------------------------------------------
# SENIOR-LEVEL DESIGN SYSTEM & CSS TOKENS
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Top Hero Command Header */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15), 0 8px 10px -6px rgba(15, 23, 42, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-top: 6px;
        margin-bottom: 14px;
        font-weight: 500;
    }
    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #f1f5f9;
        backdrop-filter: blur(4px);
    }

    /* Executive KPI Card */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }
    .kpi-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
        color: #64748b;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Badges & Pills */
    .badge-success {
        color: #065f46;
        background-color: #d1fae5;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
    }
    .badge-progress {
        color: #9a3412;
        background-color: #ffedd5;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
    }
    .badge-neutral {
        color: #475569;
        background-color: #f1f5f9;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
    }
    .badge-holiday {
        color: #92400e;
        background-color: #fef3c7;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
    }
    .badge-assessment {
        color: #991b1b;
        background-color: #fee2e2;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-block;
    }

    /* Section Titles */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 18px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Semester Card Design */
    .sem-card {
        border-radius: 12px;
        padding: 16px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .sem-card-active {
        border: 2px solid #2563eb;
        background: linear-gradient(180deg, #f8fafc 0%, #eff6ff 100%);
    }

    /* Chat bubble enhancements */
    .chat-source-badge {
        font-size: 0.75rem;
        color: #2563eb;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 6px;
        padding: 2px 8px;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PATH & DATA HANDLING
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

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
# SUPABASE CREDENTIALS & CLIENT (CLOUD POSTGRESQL)
# ---------------------------------------------------------
def get_supabase_credentials():
    """Retrieves Supabase URL and Key from .env files, Streamlit secrets, or OS environment."""
    url = None
    key = None

    # 1. Local .env files
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

    # 2. Streamlit Cloud Secrets (safe exception handling)
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

    # 3. OS environment variables
    if not url:
        url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

    # 4. Streamlit session state (manual override in UI)
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
            logger.warning(f"Failed to create Supabase client: {e}")
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
    if supabase_client and table_name:
        try:
            res = supabase_client.table(table_name).select("*").execute()
            if res.data and len(res.data) > 0:
                df = pd.DataFrame(res.data)
                if "id" in df.columns and "id" not in DEFAULT_COLUMNS.get(filename, []):
                    df = df.drop(columns=["id"])
                cols = DEFAULT_COLUMNS.get(filename, [])
                avail_cols = [c for c in cols if c in df.columns]
                return df[avail_cols]
        except Exception:
            pass

    file_path = DATA_DIR / filename
    if not file_path.exists():
        cols = DEFAULT_COLUMNS.get(filename, [])
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        cols = DEFAULT_COLUMNS.get(filename, [])
        return pd.DataFrame(columns=cols)

def save_data(filename: str, df: pd.DataFrame) -> bool:
    """
    Saves DataFrame to local CSV and synchronizes with Supabase if connected.
    """
    success = True
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
        logger.error(f"Failed to save local {filename}: {e}")
        success = False

    table_name = CSV_TO_TABLE.get(filename)
    if supabase_client and table_name:
        try:
            records = df.to_dict(orient="records")
            supabase_client.table(table_name).upsert(records).execute()
        except Exception as e:
            logger.warning(f"Saved to local CSV, but Supabase sync encountered: {e}")

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
# SIDEBAR NAVIGATION & PROFILE
# ---------------------------------------------------------
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <span style="font-size: 2rem;">🎓</span>
    <div>
        <h2 style="font-size: 1.25rem; font-weight: 800; margin: 0; color: #0f172a;">Degree OS</h2>
        <p style="font-size: 0.75rem; color: #64748b; margin: 0;">Command Center v2.5</p>
    </div>
</div>
""", unsafe_allow_html=True)

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
    st.sidebar.markdown("""
    <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 10px; font-size: 0.8rem; color: #065f46;">
        <strong>🟢 Live Cloud Storage:</strong><br>Connected to Supabase PostgreSQL
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; font-size: 0.8rem; color: #475569;">
        <strong>📁 Local Storage:</strong><br>Running in local CSV mode
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="background: #f1f5f9; border-radius: 10px; padding: 12px; margin-top: 14px; font-size: 0.8rem; color: #334155;">
    <strong>👤 Student:</strong> Prajwal S Hiremath<br>
    <strong>📘 Program:</strong> B.Tech in CSE<br>
    <strong>📌 Stage:</strong> Semester 3 (Active)<br>
    <strong>📅 Ref Date:</strong> 16 Nov 2026
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GLOBAL HERO BANNER
# ---------------------------------------------------------
total_degree_credits = semesters_df["total_credits"].sum() if not semesters_df.empty else 175
completed_degree_credits = semesters_df["completed_credits"].sum() if not semesters_df.empty else 57
degree_completion_pct = (completed_degree_credits / total_degree_credits * 100) if total_degree_credits > 0 else 0

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">
        <span>🎓</span> My Engineering Degree OS
    </div>
    <div class="hero-subtitle">
        Self-Managed 1st-to-8th Semester Academic Operating System & Intelligence Center
    </div>
    <div class="hero-pills">
        <span class="hero-pill">⚡ Semester 3 in Progress</span>
        <span class="hero-pill">🎯 {degree_completion_pct:.1f}% Degree Complete ({completed_degree_credits}/{total_degree_credits} Credits)</span>
        <span class="hero-pill">🏛️ CBCS Regulation 2024–2028</span>
        <span class="hero-pill">{'🟢 Supabase Cloud Active' if supabase_client else '📁 Local CSV Mode'}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 1: DASHBOARD
# ---------------------------------------------------------
if selected_page == "Dashboard":
    # Calculate next assessment
    next_assessment_str = "None scheduled"
    next_ass_days = None
    if not assessments_df.empty and "date" in assessments_df.columns:
        ass_df_copy = assessments_df.copy()
        ass_df_copy["parsed_date"] = pd.to_datetime(ass_df_copy["date"], errors="coerce").dt.date
        upcoming_ass = ass_df_copy[ass_df_copy["parsed_date"] >= TODAY].sort_values("parsed_date")
        if not upcoming_ass.empty:
            first_ass = upcoming_ass.iloc[0]
            days_diff = (first_ass["parsed_date"] - TODAY).days
            next_ass_days = f"In {days_diff} days" if days_diff > 0 else "Today"
            next_assessment_str = f"{first_ass['course_code']} {first_ass['assessment_type']}"

    # Calculate next holiday
    next_holiday_str = "None upcoming"
    next_hol_days = None
    if not calendar_df.empty and "date" in calendar_df.columns and "event_type" in calendar_df.columns:
        cal_copy = calendar_df.copy()
        cal_copy["parsed_date"] = pd.to_datetime(cal_copy["date"], errors="coerce").dt.date
        upcoming_holidays = cal_copy[(cal_copy["event_type"].str.lower() == "holiday") & (cal_copy["parsed_date"] >= TODAY)].sort_values("parsed_date")
        if not upcoming_holidays.empty:
            first_hol = upcoming_holidays.iloc[0]
            h_days = (first_hol["parsed_date"] - TODAY).days
            next_hol_days = f"In {h_days} days" if h_days > 0 else "Today"
            next_holiday_str = str(first_hol["title"])

    # Current score summary
    prototype_pct = 0.0
    if not scores_df.empty:
        total_score = scores_df["score"].sum()
        total_max = scores_df["max_marks"].sum()
        if total_max > 0:
            prototype_pct = (total_score / total_max) * 100

    # 5 KPI Cards Row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Current Stage</div>
            <div class="kpi-value">Sem 3</div>
            <div class="kpi-subtext"><span class="badge-progress">In Progress</span></div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Degree Progress</div>
            <div class="kpi-value">{degree_completion_pct:.1f}%</div>
            <div class="kpi-subtext">{completed_degree_credits} of {total_degree_credits} Credits</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Next Assessment</div>
            <div class="kpi-value" style="font-size: 1.25rem;">{next_assessment_str}</div>
            <div class="kpi-subtext"><span class="badge-assessment">{next_ass_days or 'Scheduled'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Next Holiday</div>
            <div class="kpi-value" style="font-size: 1.15rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{next_holiday_str}">{next_holiday_str[:18]}...</div>
            <div class="kpi-subtext"><span class="badge-holiday">{next_hol_days or 'Upcoming'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Prototype Score</div>
            <div class="kpi-value">{prototype_pct:.1f}%</div>
            <div class="kpi-subtext"><span class="badge-success">Avg across tests</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Semester-by-Semester Credit Architecture</div>', unsafe_allow_html=True)
    if not semesters_df.empty:
        chart_data = semesters_df.copy()
        chart_data["Semester"] = "Sem " + chart_data["semester"].astype(str)
        chart_display = chart_data.set_index("Semester")[["completed_credits", "total_credits"]]
        chart_display.columns = ["Completed Credits", "Total Required Credits"]
        st.bar_chart(chart_display, color=["#2563eb", "#94a3b8"])

    # Two column overview
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('<div class="section-title">⚡ Action Radar (Due in Next 7 Days)</div>', unsafe_allow_html=True)
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
                    st.markdown(f"""
                    <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #92400e;">📌 {row['item']}</strong><br>
                        <span style="font-size: 0.8rem; color: #78350f;">Target: {row['target_date']} • <em>{row['category']}</em></span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No urgent tasks due in the next 7 days.")
        else:
            st.info("No checklist items recorded.")

    with right_col:
        st.markdown('<div class="section-title">📅 Academic & Examination Milestones</div>', unsafe_allow_html=True)
        if not calendar_df.empty:
            cal_copy = calendar_df.copy()
            cal_copy["parsed_date"] = pd.to_datetime(cal_copy["date"], errors="coerce").dt.date
            upcoming_events = cal_copy[cal_copy["parsed_date"] >= TODAY].sort_values("parsed_date").head(4)
            if not upcoming_events.empty:
                for _, row in upcoming_events.iterrows():
                    badge_cls = "badge-holiday" if row["event_type"] == "Holiday" else ("badge-assessment" if row["event_type"] == "Assessment" else "badge-neutral")
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px 14px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #0f172a;">{row['title']}</strong><br>
                            <span style="font-size: 0.8rem; color: #64748b;">Date: {row['date']} • Semester {row['semester']}</span>
                        </div>
                        <span class="{badge_cls}">{row['event_type']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No upcoming calendar events recorded.")

# ---------------------------------------------------------
# TAB 2: SEMESTERS 1-8
# ---------------------------------------------------------
elif selected_page == "Semesters 1-8":
    st.markdown('<div class="section-title">Semesters 1 to 8 Academic Journey</div>', unsafe_allow_html=True)
    st.caption("Eight-semester full curriculum load, status tracking, and credit milestones.")

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

        is_active = (i == 3)
        badge_html = '<span class="badge-success">Completed</span>' if status == "Completed" else ('<span class="badge-progress">In Progress</span>' if status == "In Progress" else '<span class="badge-neutral">Not Started</span>')

        with col:
            st.markdown(f"""
            <div class="sem-card {'sem-card-active' if is_active else ''}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #0f172a;">Semester {i}</h3>
                    {badge_html}
                </div>
                <div style="font-size: 0.85rem; color: #475569; margin-bottom: 8px;">
                    <strong>Courses:</strong> {c_count} Courses<br>
                    <strong>Credits:</strong> {done_cr} / {total_cr} Credits
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(progress_val)

    st.markdown("---")
    st.subheader("🔍 Inspect Semester Details")
    chosen_sem = st.selectbox("Select Semester to Inspect", options=list(range(1, 9)), index=2)

    sub_courses = courses_df[courses_df["semester"] == chosen_sem] if not courses_df.empty else pd.DataFrame()
    if not sub_courses.empty:
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
    st.markdown('<div class="section-title">Courses & Syllabus Directory</div>', unsafe_allow_html=True)
    st.caption("Comprehensive registry of course codes, credits, faculty, syllabus modules, and progress.")

    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
        sem_choice = st.selectbox("Filter by Semester", options=["All Semesters"] + [f"Semester {i}" for i in range(1, 9)], index=3)
    with filter_col2:
        search_query = st.text_input("🔍 Search Course Code, Title, Faculty, or Topic", placeholder="e.g. CS301, Data Structures, Trees...")

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
        
        st.markdown('<div class="section-title">📖 Module Syllabus Breakdowns</div>', unsafe_allow_html=True)
        for _, c_row in filtered_courses.iterrows():
            with st.expander(f"📘 {c_row['course_code']} — {c_row['course_name']} ({c_row['credits']} Credits | Sem {c_row['semester']})"):
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
    st.markdown('<div class="section-title">University Programme Specification</div>', unsafe_allow_html=True)
    st.caption("Official programme curriculum architecture, credit scheme, and academic regulations.")

    with st.container(border=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""
            **Programme Title:**  
            B.Tech in Computer Science & Engineering  
            **Awarding Body:**  
            Department of CSE & Examination Cell
            """)
        with col_b:
            st.markdown("""
            **Curriculum Framework:**  
            CBCS (Choice Based Credit System) 2024–2028  
            **Total Duration:**  
            4 Academic Years (8 Semesters)
            """)
        with col_c:
            st.markdown("""
            **Degree Credit Requirement:**  
            175 Credits  
            **Minimum Course Passing Benchmark:**  
            40% per theory & laboratory course
            """)

    st.markdown("#### 🔗 Official Syllabus Repository Link")
    st.text_input(
        "Syllabus Source / Reference URL",
        value="https://university.ac.in/syllabi/btech-cse-curriculum-2024.pdf",
        help="Official department syllabus portal"
    )

    st.markdown('<div class="section-title">🏛️ 4-Year Academic Progression Model</div>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <strong style="color: #1e3a8a;">Year 1 (Semesters 1 & 2): Foundation Stage</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">
            Engineering Mathematics, Physics, Chemistry, Basic Electrical, and C Programming fundamentals.
            </span>
        </div>
        <div class="kpi-card">
            <strong style="color: #1e3a8a;">Year 2 (Semesters 3 & 4): Core Computing Stage</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">
            Data Structures, Computer Architecture, Discrete Math, Database Systems, Operating Systems, Algorithms.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        st.markdown("""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <strong style="color: #1e3a8a;">Year 3 (Semesters 5 & 6): Advanced & Applied Systems</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">
            Computer Networks, Software Engineering, AI, Compiler Design, Web Tech, Machine Learning.
            </span>
        </div>
        <div class="kpi-card">
            <strong style="color: #1e3a8a;">Year 4 (Semesters 7 & 8): Specialization & Industry Capstone</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">
            Cyber Security, Big Data, Deep Learning Electives, Major Capstone Project, 16-Week Industry Internship.
            </span>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 5: ACADEMIC / LEAVE CALENDAR
# ---------------------------------------------------------
elif selected_page == "Academic / Leave Calendar":
    st.markdown('<div class="section-title">Academic & Institutional Leave Calendar</div>', unsafe_allow_html=True)
    st.caption("Co-listing academic dates, tests, and college holidays with timeline distance countdowns.")

    col1, col2, col3 = st.columns(3)
    with col1:
        years = ["All"] + sorted(list(calendar_df["academic_year"].dropna().unique())) if not calendar_df.empty else ["All"]
        selected_year = st.selectbox("Academic Year", years, index=0)
    with col2:
        sems = ["All"] + [f"Sem {s}" for s in sorted(list(calendar_df["semester"].dropna().unique()))] if not calendar_df.empty else ["All"]
        selected_sem = st.selectbox("Semester", sems, index=0)
    with col3:
        event_types = ["All"] + list(calendar_df["event_type"].dropna().unique()) if not calendar_df.empty else ["All"]
        selected_type = st.selectbox("Event Category", event_types, index=0)

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
    st.markdown('<div class="section-title">Internal Assessments & Examination Schedule</div>', unsafe_allow_html=True)
    st.caption("IA1, IA2, laboratory evaluations, assignments, project vivas, and end-term exams.")

    ass_col1, ass_col2 = st.columns(2)
    with ass_col1:
        sem_filter = st.selectbox("Filter by Semester", ["All"] + [f"Sem {s}" for s in range(1, 9)], index=3)
    with ass_col2:
        type_filter = st.selectbox("Filter by Assessment Type", ["All", "IA1", "IA2", "Assignment", "Lab Evaluation", "Project Review", "End Semester"])

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
    st.markdown('<div class="section-title">Degree Course Status Tracker</div>', unsafe_allow_html=True)
    st.caption("Live completion tracking across courses and semesters.")

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
    st.write(f"**Semester {track_sem} Completion Benchmark:** {completion_rate * 100:.1f}%")
    st.progress(completion_rate)

    st.markdown(f"#### Detailed Course Status for Semester {track_sem}")
    if not sem_c.empty:
        st.dataframe(
            sem_c[["course_code", "course_name", "credits", "faculty", "status"]],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    st.markdown('<div class="section-title">📊 8-Semester Status Matrix</div>', unsafe_allow_html=True)
    if not courses_df.empty:
        overall_summary = courses_df.groupby(["semester", "status"]).size().unstack(fill_value=0)
        st.dataframe(overall_summary, use_container_width=True)

# ---------------------------------------------------------
# TAB 8: SCORECARD
# ---------------------------------------------------------
elif selected_page == "Scorecard":
    st.markdown('<div class="section-title">Student Academic Scorecard</div>', unsafe_allow_html=True)
    st.caption("Verified assessment scores, letter grades, and prototype performance average.")

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
            st.metric("Cumulative Prototype Score", f"{proto_pct:.2f}%", "Overall recorded average")
        with col2:
            st.metric("Total Marks Scored", f"{tot_score:.0f} / {tot_max:.0f}")
        with col3:
            st.metric("Assessments Evaluated", len(scores_df))

        st.markdown("#### 📋 Assessment Score Records")
        st.dataframe(
            scores_df[["semester", "course_code", "assessment_type", "score", "max_marks", "grade"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### 📈 Semester-Wise Breakdown")
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
    st.markdown('<div class="section-title">Degree Execution Checklist & Control Panel</div>', unsafe_allow_html=True)
    st.caption("Strategic execution roadmap for exams, projects, document vault, and placement readiness.")

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

        # Summary KPI Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Action Items", total_items)
        with m2:
            st.metric("Completed (Done)", done_items)
        with m3:
            st.metric("Due Soon (Next 7 Days)", due_soon_items)
        with m4:
            st.metric("Overdue Items", overdue_items)

        st.markdown("---")
        
        # 1. This Week Section
        st.markdown('<div class="section-title">⚡ This Week (Next 7 Days)</div>', unsafe_allow_html=True)
        this_week = chk_calc[(chk_calc["Health"] == "Due Soon") | ((chk_calc["parsed_target"] >= TODAY) & (chk_calc["parsed_target"] <= TODAY + timedelta(days=7)))]
        if not this_week.empty:
            for _, r in this_week.iterrows():
                badge = "✅" if r["status"] == "Done" else "⏳"
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px 14px; border-radius: 8px; margin-bottom: 8px;">
                    {badge} <strong>{r['item']}</strong> — Target: <code>{r['target_date']}</code> | <em>{r['category']}</em> | Note: {r['notes']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tasks due in the next 7 days.")

        # 2. Semester Milestones Section
        st.markdown('<div class="section-title">🎯 Semester Milestones</div>', unsafe_allow_html=True)
        sem_milestones = chk_calc[chk_calc["category"].isin(["Semester Preparation", "Assessments", "Labs", "Projects"])]
        if not sem_milestones.empty:
            st.dataframe(
                sem_milestones[["category", "item", "target_date", "status", "Health", "notes"]],
                use_container_width=True,
                hide_index=True
            )

        # 3. Degree Milestones Section
        st.markdown('<div class="section-title">🏆 Long-Range Degree Milestones & Placement Readiness</div>', unsafe_allow_html=True)
        deg_milestones = chk_calc[chk_calc["category"].isin(["Placement", "Internship/Placement", "Skills", "Documents", "Degree Milestones"])]
        if not deg_milestones.empty:
            st.dataframe(
                deg_milestones[["category", "item", "target_date", "status", "Health", "notes"]],
                use_container_width=True,
                hide_index=True
            )

        st.markdown("---")
        st.markdown('<div class="section-title">✏️ Live Checklist Editor</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="section-title">Ask Degree AI Assistant</div>', unsafe_allow_html=True)
    st.caption("AI-grounded assistant with strict zero-hallucination guardrails and dataset citations.")

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

    with st.expander("⚙️ AI Configuration & Grounding Safeguards", expanded=False):
        st.write("**Grounded Context Source:** Loaded 8-Semester Degree Data")
        if api_key:
            st.success("🟢 Google Gemini API connected & operational (Model: gemini-2.5-flash).")
        else:
            st.info("ℹ️ Running in **Deterministic Local Grounding Mode**. Safe-AI rule active.")
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
                st.markdown(f'<span class="chat-source-badge">📍 Data Area: {msg["area"]}</span>', unsafe_allow_html=True)

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

    st.write("##### 💡 Try quick verification prompts:")
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
    st.markdown('<div class="section-title">Data Administration & Cloud Sync</div>', unsafe_allow_html=True)
    st.caption("Maintain degree records and synchronize with your live Supabase cloud database.")

    with st.container(border=True):
        st.subheader("⚡ Cloud Database Integration (Supabase)")
        c1, c2 = st.columns([2, 1])
        with c1:
            if supabase_client:
                st.success("🟢 **Supabase Connected & Active:** Changes automatically synchronize with your cloud PostgreSQL database.")
            else:
                if not SUPABASE_SDK_AVAILABLE:
                    st.warning("⚠️ `supabase` library not detected. Install via `pip install supabase`.")
                else:
                    st.info("ℹ️ Running in **Local CSV Mode**. Add your Supabase credentials in secrets to connect cloud storage.")

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
    st.markdown('<div class="section-title">Student Feedback (Supabase Auth & RLS)</div>', unsafe_allow_html=True)
    st.caption("Authenticated, secure feedback storage with PostgreSQL Row Level Security (RLS).")

    sup_url, sup_key = get_supabase_credentials()

    if not sup_url or not sup_key:
        st.error("Please configure SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in secrets or .env.")
        st.stop()

    if not SUPABASE_SDK_AVAILABLE:
        st.error("supabase Python library is not installed. Run `pip install supabase`.")
        st.stop()

    try:
        if "_supabase_auth_client" not in st.session_state:
            st.session_state["_supabase_auth_client"] = create_client(sup_url, sup_key)
        auth_db = st.session_state["_supabase_auth_client"]
        current_session = auth_db.auth.get_session()
    except Exception as e:
        st.error(f"Could not connect to Supabase: {e}")
        st.stop()

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
