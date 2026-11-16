"""
My Engineering Degree OS - Ultra Interactive Senior Developer Edition
A self-managed 1st-to-8th semester engineering degree command center.
Architected for high interactivity, live Plotly visualizations, dynamic GPA simulation,
interactive checklists, Google Gemini AI grounding, and Supabase PostgreSQL cloud sync.
"""

import os
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

# Interactive Plotly imports
import plotly.express as px
import plotly.graph_objects as go

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
# INTERACTIVE THEME ACCENT SYSTEM & DYNAMIC CSS
# ---------------------------------------------------------
# Sidebar Theme Selector for Personalized Interactive UX
if "ui_theme" not in st.session_state:
    st.session_state["ui_theme"] = "Modern Indigo"

THEMES = {
    "Modern Indigo": {
        "primary": "#2563eb",
        "primary_dark": "#1d4ed8",
        "gradient": "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%)",
        "card_border": "#e2e8f0",
        "accent": "#38bdf8",
        "hero_pill": "rgba(59, 130, 246, 0.2)"
    },
    "Cyber Emerald": {
        "primary": "#059669",
        "primary_dark": "#047857",
        "gradient": "linear-gradient(135deg, #022c22 0%, #064e3b 50%, #065f46 100%)",
        "card_border": "#a7f3d0",
        "accent": "#34d399",
        "hero_pill": "rgba(16, 185, 129, 0.2)"
    },
    "Royal Violet": {
        "primary": "#7c3aed",
        "primary_dark": "#6d28d9",
        "gradient": "linear-gradient(135deg, #1e1b4b 0%, #31104b 50%, #4c1d95 100%)",
        "card_border": "#ddd6fe",
        "accent": "#c084fc",
        "hero_pill": "rgba(139, 92, 246, 0.2)"
    },
    "Midnight Azure": {
        "primary": "#0284c7",
        "primary_dark": "#0369a1",
        "gradient": "linear-gradient(135deg, #030712 0%, #0c4a6e 50%, #075985 100%)",
        "card_border": "#bae6fd",
        "accent": "#38bdf8",
        "hero_pill": "rgba(14, 165, 233, 0.2)"
    }
}

active_theme_name = st.session_state.get("ui_theme", "Modern Indigo")
curr_theme = THEMES.get(active_theme_name, THEMES["Modern Indigo"])

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Hero Header */
    .hero-container {{
        background: {curr_theme['gradient']};
        border-radius: 18px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -6px rgba(15, 23, 42, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.12);
        animation: fadeIn 0.4s ease-in-out;
    }}
    .hero-title {{
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .hero-subtitle {{
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-top: 6px;
        margin-bottom: 14px;
        font-weight: 500;
    }}
    .hero-pills {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }}
    .hero-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
        backdrop-filter: blur(8px);
    }}

    /* Interactive KPI Cards */
    .kpi-card {{
        background: #ffffff;
        border: 1px solid {curr_theme['card_border']};
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08);
        border-color: {curr_theme['primary']};
    }}
    .kpi-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
        color: #64748b;
        margin-bottom: 6px;
    }}
    .kpi-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }}
    .kpi-subtext {{
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 6px;
        font-weight: 500;
    }}

    /* Badges & Pills */
    .badge-success {{
        color: #065f46;
        background-color: #d1fae5;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #a7f3d0;
        display: inline-block;
    }}
    .badge-progress {{
        color: #1e40af;
        background-color: #dbeafe;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #bfdbfe;
        display: inline-block;
    }}
    .badge-neutral {{
        color: #475569;
        background-color: #f1f5f9;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #e2e8f0;
        display: inline-block;
    }}
    .badge-holiday {{
        color: #854d0e;
        background-color: #fef9c3;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #fef08a;
        display: inline-block;
    }}
    .badge-assessment {{
        color: #991b1b;
        background-color: #fee2e2;
        padding: 3px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.75rem;
        border: 1px solid #fecaca;
        display: inline-block;
    }}

    /* Interactive Action Pills */
    .quick-pill {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #1e293b;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
    }}
    .quick-pill:hover {{
        background: #f1f5f9;
        border-color: {curr_theme['primary']};
        color: {curr_theme['primary']};
    }}

    /* Section & Cards */
    .section-title {{
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 24px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .interactive-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }}
    .interactive-card:hover {{
        border-color: {curr_theme['primary']};
        box-shadow: 0 6px 14px -2px rgba(0,0,0,0.06);
    }}

    .stButton>button {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }}
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

    if not url:
        url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

    if not url and "supabase_url" in st.session_state and st.session_state["supabase_url"]:
        url = st.session_state["supabase_url"]
    if not key and "supabase_key" in st.session_state and st.session_state["supabase_key"]:
        key = st.session_state["supabase_key"]

    return url, key

def init_supabase_client():
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

supabase_client = init_supabase_client()

def load_data(filename: str) -> pd.DataFrame:
    """Loads dataset from Supabase PostgreSQL first, falling back to local CSV."""
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
    """Saves DataFrame to local CSV and synchronizes with Supabase PostgreSQL."""
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

# Load primary datasets into session state or local variables
semesters_df = load_data("semesters.csv")
courses_df = load_data("courses.csv")
calendar_df = load_data("academic_calendar.csv")
assessments_df = load_data("assessments.csv")
scores_df = load_data("scores.csv")
checklist_df = load_data("plan_checklist.csv")

# Ensure proper types
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

# Reference anchor date
TODAY = date(2026, 11, 16)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION & INTERACTIVE THEME CONTROLS
# ---------------------------------------------------------
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <span style="font-size: 2.2rem;">🎓</span>
    <div>
        <h2 style="font-size: 1.25rem; font-weight: 800; margin: 0; color: #0f172a;">Degree OS</h2>
        <p style="font-size: 0.75rem; color: #64748b; margin: 0;">Interactive Intelligence Hub v3.0</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Theme Selector Widget
new_theme = st.sidebar.selectbox(
    "🎨 UI Accent Theme",
    options=["Modern Indigo", "Cyber Emerald", "Royal Violet", "Midnight Azure"],
    index=list(THEMES.keys()).index(active_theme_name),
    help="Changes primary accent colors and visual charts dynamically."
)
if new_theme != active_theme_name:
    st.session_state["ui_theme"] = new_theme
    st.rerun()

nav_options = [
    "Dashboard",
    "Semesters 1-8",
    "Courses & Syllabus",
    "University Syllabus",
    "Academic / Leave Calendar",
    "Internal Assessments",
    "Status Tracker",
    "Scorecard & GPA Simulator",
    "Plan & Checklist",
    "Ask Degree AI",
    "Data Admin",
    "Student Feedback (Supabase RLS)"
]

selected_page = st.sidebar.radio("Navigation", nav_options, index=0)

st.sidebar.markdown("---")

# Storage indicator widget
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
    <strong>📘 Program:</strong> B.Tech in CSE (Honours)<br>
    <strong>📌 Stage:</strong> Semester 3 (Active Term)<br>
    <strong>📅 Ref Date:</strong> 16 Nov 2026
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GLOBAL HERO BANNER WITH INTERACTIVE ACTIONS
# ---------------------------------------------------------
total_degree_credits = int(semesters_df["total_credits"].sum()) if not semesters_df.empty else 175
completed_degree_credits = int(semesters_df["completed_credits"].sum()) if not semesters_df.empty else 57
in_progress_credits = 24  # Semester 3 enrolled credits
remaining_credits = max(0, total_degree_credits - completed_degree_credits)
degree_completion_pct = (completed_degree_credits / total_degree_credits * 100) if total_degree_credits > 0 else 0

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">
        <span>🎓</span> My Engineering Degree OS
    </div>
    <div class="hero-subtitle">
        Self-Managed 1st-to-8th Semester Academic Operating System & Intelligence Command Center
    </div>
    <div class="hero-pills">
        <span class="hero-pill">⚡ Semester 3 Active Term</span>
        <span class="hero-pill">🎯 {degree_completion_pct:.1f}% Complete ({completed_degree_credits}/{total_degree_credits} Credits)</span>
        <span class="hero-pill">🏛️ CBCS Regulation 2024–2028</span>
        <span class="hero-pill">{'🟢 Cloud Database (Supabase)' if supabase_client else '📁 Local CSV Architecture'}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 1: INTERACTIVE EXECUTIVE DASHBOARD
# ---------------------------------------------------------
if selected_page == "Dashboard":
    # Calculate next upcoming assessment
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

    # Calculate next upcoming holiday
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

    # Prototype Score Percentage
    prototype_pct = 0.0
    if not scores_df.empty:
        total_score = scores_df["score"].sum()
        total_max = scores_df["max_marks"].sum()
        if total_max > 0:
            prototype_pct = (total_score / total_max) * 100

    # 5 KPI Cards Row
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Current Stage</div>
            <div class="kpi-value">Sem 3</div>
            <div class="kpi-subtext"><span class="badge-progress">Enrolled / Active</span></div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Credits Earned</div>
            <div class="kpi-value">{completed_degree_credits} <span style="font-size: 1rem; color: #64748b;">/ {total_degree_credits}</span></div>
            <div class="kpi-subtext"><span class="badge-success">{degree_completion_pct:.1f}% Completed</span></div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Next Assessment</div>
            <div class="kpi-value" style="font-size: 1.25rem;">{next_assessment_str}</div>
            <div class="kpi-subtext"><span class="badge-assessment">{next_ass_days or 'Scheduled'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Next Holiday</div>
            <div class="kpi-value" style="font-size: 1.15rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{next_holiday_str}">{next_holiday_str[:16]}...</div>
            <div class="kpi-subtext"><span class="badge-holiday">{next_hol_days or 'Upcoming'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with kpi5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Prototype Average</div>
            <div class="kpi-value">{prototype_pct:.1f}%</div>
            <div class="kpi-subtext"><span class="badge-success">8.82 Cumulative CGPA</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Interactive Visual Charts Row (Plotly)
    col_chart_left, col_chart_right = st.columns([1, 1])

    with col_chart_left:
        st.markdown('<div class="section-title">📊 Degree Credits Completion Ring</div>', unsafe_allow_html=True)
        # Plotly Donut Chart
        ring_labels = ["Completed Credits", "Enrolled (Sem 3)", "Remaining Credits"]
        ring_values = [completed_degree_credits, in_progress_credits, max(0, total_degree_credits - completed_degree_credits - in_progress_credits)]
        ring_colors = [curr_theme["primary"], "#f59e0b", "#e2e8f0"]
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=ring_labels,
            values=ring_values,
            hole=0.68,
            marker=dict(colors=ring_colors),
            textinfo="percent+label",
            hoverinfo="label+value+percent"
        )])
        fig_donut.update_layout(
            showlegend=True,
            margin=dict(t=20, b=20, l=10, r=10),
            height=280,
            annotations=[dict(text=f"<b>{degree_completion_pct:.1f}%</b><br>Done", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart_right:
        st.markdown('<div class="section-title">🎯 CGPA Performance Target Gauge</div>', unsafe_allow_html=True)
        # Plotly Indicator Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=8.82,
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': 8.5, 'position': "top", 'increasing': {'color': "#059669"}, 'suffix': " vs 8.5 Target"},
            title={'text': "Current CGPA Standing", 'font': {'size': 16, 'color': "#0f172a"}},
            gauge={
                'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#64748b"},
                'bar': {'color': curr_theme["primary"]},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#cbd5e1",
                'steps': [
                    {'range': [0, 6.0], 'color': '#fee2e2'},
                    {'range': [6.0, 7.5], 'color': '#fef3c7'},
                    {'range': [7.5, 8.5], 'color': '#dbeafe'},
                    {'range': [8.5, 10.0], 'color': '#d1fae5'}
                ],
                'threshold': {
                    'line': {'color': "#dc2626", 'width': 4},
                    'thickness': 0.75,
                    'value': 9.0
                }
            }
        ))
        fig_gauge.update_layout(margin=dict(t=30, b=20, l=20, r=20), height=280)
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Semester Credit Architecture (Interactive Stacked Bar)
    st.markdown('<div class="section-title">🏛️ 8-Semester Credit Progression Architecture</div>', unsafe_allow_html=True)
    if not semesters_df.empty:
        sem_chart_df = semesters_df.copy()
        sem_chart_df["Semester"] = "Sem " + sem_chart_df["semester"].astype(str)
        sem_chart_df["Pending Credits"] = sem_chart_df["total_credits"] - sem_chart_df["completed_credits"]
        
        fig_bar = px.bar(
            sem_chart_df,
            x="Semester",
            y=["completed_credits", "Pending Credits"],
            title="Completed vs Pending Credits across all 8 Semesters",
            color_discrete_map={"completed_credits": curr_theme["primary"], "Pending Credits": "#cbd5e1"},
            labels={"value": "Credits", "variable": "Credit Type"}
        )
        fig_bar.update_layout(barmode="stack", height=320, margin=dict(t=40, b=20, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    # Two column overview: Action items & Academic milestones
    act_col, mile_col = st.columns(2)
    with act_col:
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
                st.success("✅ All actions for the next 7 days are clear or completed!")
        else:
            st.info("No checklist items recorded.")

    with mile_col:
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
# TAB 2: SEMESTERS 1-8 ACADEMIC JOURNEY
# ---------------------------------------------------------
elif selected_page == "Semesters 1-8":
    st.markdown('<div class="section-title">🏛️ 8-Semester Curriculum Architecture</div>', unsafe_allow_html=True)
    st.caption("Eight-semester full curriculum load, status tracking, and credit milestones.")

    # Top Interactive Semester Selector Pills
    col_sem_pills = st.columns(8)
    for i in range(1, 9):
        with col_sem_pills[i-1]:
            if st.button(f"Sem {i}", key=f"sem_quick_{i}", use_container_width=True):
                st.session_state["chosen_sem_inspect"] = i

    chosen_sem = st.session_state.get("chosen_sem_inspect", 3)

    # Grid of Semester Cards
    row1 = st.columns(4)
    row2 = st.columns(4)
    all_cols = row1 + row2

    for i in range(1, 9):
        col = all_cols[i - 1]
        sem_row = semesters_df[semesters_df["semester"] == i] if not semesters_df.empty else pd.DataFrame()
        status = sem_row["status"].values[0] if not sem_row.empty else ("Completed" if i <= 2 else ("In Progress" if i == 3 else "Not Started"))
        total_cr = int(sem_row["total_credits"].values[0]) if not sem_row.empty else 22
        done_cr = int(sem_row["completed_credits"].values[0]) if not sem_row.empty else (total_cr if i <= 2 else (12 if i == 3 else 0))
        
        sem_courses = courses_df[courses_df["semester"] == i] if not courses_df.empty else pd.DataFrame()
        c_count = len(sem_courses)
        progress_val = min(1.0, done_cr / total_cr) if total_cr > 0 else 0.0

        is_selected = (i == chosen_sem)
        card_border_style = f"border: 2px solid {curr_theme['primary']}; background: #eff6ff;" if is_selected else "border: 1px solid #e2e8f0; background: #ffffff;"
        badge_html = '<span class="badge-success">Completed</span>' if status == "Completed" else ('<span class="badge-progress">In Progress</span>' if status == "In Progress" else '<span class="badge-neutral">Not Started</span>')

        with col:
            st.markdown(f"""
            <div class="kpi-card" style="{card_border_style} margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #0f172a;">Semester {i}</h3>
                    {badge_html}
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 6px;">
                    <strong>{c_count} Courses</strong> • <strong>{done_cr}/{total_cr} Credits</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(progress_val)

    st.markdown("---")
    st.subheader(f"🔍 Inspecting Semester {chosen_sem} Details")

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
# TAB 3: INTERACTIVE COURSES & SYLLABUS DIRECTORY
# ---------------------------------------------------------
elif selected_page == "Courses & Syllabus":
    st.markdown('<div class="section-title">📚 Interactive Course & Syllabus Directory</div>', unsafe_allow_html=True)
    st.caption("Search, filter, and inspect curriculum modules with interactive self-paced study tracking.")

    # Search and Filter Toolbar
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        sem_filter = st.selectbox("Filter Semester", options=["All Semesters"] + [f"Semester {i}" for i in range(1, 9)], index=3)
    with f2:
        status_filter = st.selectbox("Course Status", options=["All Statuses", "Completed", "Enrolled", "Upcoming"], index=0)
    with f3:
        search_kw = st.text_input("🔍 Live Search (Code, Name, Faculty, Topic)", placeholder="e.g. CS301, Data Structures, Trees, Gupta...")

    filtered = courses_df.copy()
    if sem_filter != "All Semesters":
        sem_num = int(sem_filter.split(" ")[1])
        filtered = filtered[filtered["semester"] == sem_num]

    if status_filter != "All Statuses":
        filtered = filtered[filtered["status"].str.lower() == status_filter.lower()]

    if search_kw.strip():
        q = search_kw.lower()
        filtered = filtered[
            filtered["course_code"].str.lower().str.contains(q) |
            filtered["course_name"].str.lower().str.contains(q) |
            filtered["syllabus"].str.lower().str.contains(q) |
            filtered["faculty"].str.lower().str.contains(q)
        ]

    st.markdown(f"**Found {len(filtered)} matching course(s):**")
    
    if not filtered.empty:
        st.dataframe(
            filtered[["semester", "course_code", "course_name", "credits", "faculty", "status", "syllabus"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown('<div class="section-title">📖 Interactive Unit Modules & Self-Paced Study Tracker</div>', unsafe_allow_html=True)
        st.caption("Check off completed syllabus modules to track your study progress dynamically:")

        for _, c_row in filtered.iterrows():
            c_code = c_row['course_code']
            c_name = c_row['course_name']
            c_cr = c_row['credits']
            c_fac = c_row['faculty']
            c_stat = c_row['status']
            topics = [t.strip() for t in str(c_row['syllabus']).split(";") if t.strip()]

            with st.expander(f"📘 {c_code}: {c_name} ({c_cr} Credits | Semester {c_row['semester']})"):
                st.write(f"**Faculty:** {c_fac} | **Status:** {c_stat}")
                st.markdown("##### 📝 Module Units")
                
                checked_count = 0
                for idx, top in enumerate(topics):
                    unit_key = f"chk_{c_code}_{idx}"
                    # Session state tracking for self-paced audit
                    if unit_key not in st.session_state:
                        st.session_state[unit_key] = (c_stat == "Completed")
                    
                    is_done = st.checkbox(f"Unit {idx+1}: {top}", value=st.session_state[unit_key], key=unit_key)
                    if is_done:
                        checked_count += 1
                
                progress_pct = (checked_count / len(topics)) if len(topics) > 0 else 0
                st.progress(progress_pct, text=f"Study Progress: {checked_count}/{len(topics)} Units Mastered ({progress_pct*100:.0f}%)")
    else:
        st.warning("No courses match your active search filters.")

# ---------------------------------------------------------
# TAB 4: UNIVERSITY SYLLABUS
# ---------------------------------------------------------
elif selected_page == "University Syllabus":
    st.markdown('<div class="section-title">📖 University Degree Syllabus Specification</div>', unsafe_allow_html=True)
    st.caption("Official CBCS Engineering Curriculum (Computer Science & Engineering).")

    branch = st.selectbox("Department & Branch", ["Computer Science & Engineering", "Data Science & AI", "Electronics & Communication"])
    target_sem = st.slider("Select Semester Syllabus to View", min_value=1, max_value=8, value=3)

    st.markdown(f"### Syllabus Matrix for Semester {target_sem} ({branch})")

    sem_courses = courses_df[courses_df["semester"] == target_sem] if not courses_df.empty else pd.DataFrame()
    if not sem_courses.empty:
        for _, r in sem_courses.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="interactive-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #0f172a;">{r['course_code']} — {r['course_name']}</h4>
                        <span class="badge-success">{r['credits']} Credits</span>
                    </div>
                    <p style="margin: 4px 0; color: #64748b; font-size: 0.85rem;">Faculty: <strong>{r['faculty']}</strong></p>
                    <div style="background: #f8fafc; border-left: 3px solid {curr_theme['primary']}; padding: 8px 12px; margin-top: 8px; border-radius: 4px; font-size: 0.85rem;">
                        <strong>Curriculum Modules:</strong> {r['syllabus']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No courses found for this semester.")

# ---------------------------------------------------------
# TAB 5: ACADEMIC & LEAVE CALENDAR (INTERACTIVE TIMELINE & .ICS)
# ---------------------------------------------------------
elif selected_page == "Academic / Leave Calendar":
    st.markdown('<div class="section-title">🗓️ Academic & Leave Calendar</div>', unsafe_allow_html=True)
    st.caption("Interactive chronological timeline of assessments, college milestones, and declared holidays.")

    # Event Filter Pills
    filter_type = st.radio("Filter Events", ["All Events", "Exams & Assessments", "Holidays & Breaks", "Academic Milestones"], horizontal=True)

    cal_df = calendar_df.copy()
    if not cal_df.empty:
        cal_df["parsed_date"] = pd.to_datetime(cal_df["date"], errors="coerce")
        cal_df = cal_df.sort_values("parsed_date")

        if filter_type == "Exams & Assessments":
            cal_df = cal_df[cal_df["event_type"].str.lower() == "assessment"]
        elif filter_type == "Holidays & Breaks":
            cal_df = cal_df[cal_df["event_type"].str.lower() == "holiday"]
        elif filter_type == "Academic Milestones":
            cal_df = cal_df[cal_df["event_type"].str.lower() == "academic"]

        # Interactive Plotly Timeline / Scatter Chart
        st.markdown("#### 📈 Interactive Event Schedule Timeline")
        fig_cal = px.scatter(
            cal_df,
            x="parsed_date",
            y="event_type",
            color="event_type",
            hover_name="title",
            text="title",
            size_max=15,
            color_discrete_map={"Holiday": "#eab308", "Assessment": "#ef4444", "Academic": "#3b82f6"},
            title="Academic Term Timeline (Nov 2026 - May 2027)"
        )
        fig_cal.update_traces(textposition='top center')
        fig_cal.update_layout(height=260, margin=dict(t=30, b=20, l=10, r=10), showlegend=False)
        st.plotly_chart(fig_cal, use_container_width=True)

        # Download .ICS iCalendar Export
        def generate_ics(events):
            ics_lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Engineering Degree OS//Calendar v1.0//EN"
            ]
            for _, ev in events.iterrows():
                dt_str = pd.to_datetime(ev["date"]).strftime("%Y%m%d")
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"SUMMARY:{ev['title']} ({ev['event_type']})",
                    f"DTSTART;VALUE=DATE:{dt_str}",
                    f"DTEND;VALUE=DATE:{dt_str}",
                    f"DESCRIPTION:Semester {ev['semester']} {ev['event_type']} - My Engineering Degree OS",
                    "END:VEVENT"
                ])
            ics_lines.append("END:VCALENDAR")
            return "\n".join(ics_lines)

        ics_data = generate_ics(cal_df)
        st.download_button(
            label="📅 Export Events to iCalendar (.ics for Google / Apple Calendar)",
            data=ics_data,
            file_name="engineering_degree_calendar.ics",
            mime="text/calendar"
        )

        st.markdown("---")
        st.markdown("#### 📋 Detailed Chronological Schedule")
        for _, ev in cal_df.iterrows():
            ev_date = ev["parsed_date"].date() if pd.notnull(ev["parsed_date"]) else TODAY
            diff_days = (ev_date - TODAY).days
            
            if diff_days < 0:
                badge = f'<span class="badge-neutral">{abs(diff_days)} days ago</span>'
            elif diff_days == 0:
                badge = '<span class="badge-assessment">TODAY!</span>'
            else:
                badge = f'<span class="badge-progress">In {diff_days} days</span>'

            color_strip = "#ef4444" if ev["event_type"] == "Assessment" else ("#eab308" if ev["event_type"] == "Holiday" else curr_theme["primary"])

            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid {color_strip}; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #0f172a; font-size: 1rem;">{ev['title']}</strong><br>
                    <span style="font-size: 0.8rem; color: #64748b;">📅 {ev['date']} • Semester {ev['semester']} • <em>{ev['event_type']}</em></span>
                </div>
                {badge}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No calendar events recorded.")

# ---------------------------------------------------------
# TAB 6: INTERNAL ASSESSMENTS TRACKER
# ---------------------------------------------------------
elif selected_page == "Internal Assessments":
    st.markdown('<div class="section-title">📝 Internal Assessments Tracker</div>', unsafe_allow_html=True)
    st.caption("Evaluation schedules, maximum marks, and completion status across courses.")

    if not assessments_df.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            ass_sem = st.selectbox("Filter Semester", ["All"] + list(range(1, 9)), index=3)
        with col_f2:
            ass_type = st.selectbox("Assessment Type", ["All"] + list(assessments_df["assessment_type"].unique()), index=0)

        ass_view = assessments_df.copy()
        if ass_sem != "All":
            ass_view = ass_view[ass_view["semester"] == int(ass_sem)]
        if ass_type != "All":
            ass_view = ass_view[ass_view["assessment_type"] == ass_type]

        st.dataframe(ass_view, use_container_width=True, hide_index=True)

        # Plotly Assessment Distribution Bar Chart
        st.markdown("#### 📊 Assessment Weightage & Max Marks")
        fig_ass = px.bar(
            ass_view,
            x="course_code",
            y="max_marks",
            color="assessment_type",
            barmode="group",
            title="Max Marks by Course and Assessment Type"
        )
        fig_ass.update_layout(height=300, margin=dict(t=30, b=20, l=10, r=10))
        st.plotly_chart(fig_ass, use_container_width=True)
    else:
        st.info("No assessments recorded.")

# ---------------------------------------------------------
# TAB 7: STATUS TRACKER
# ---------------------------------------------------------
elif selected_page == "Status Tracker":
    st.markdown('<div class="section-title">📈 Degree Academic Status Matrix</div>', unsafe_allow_html=True)
    st.caption("Holistic view of all courses, completion ratios, and academic milestones.")

    if not courses_df.empty:
        stat_counts = courses_df["status"].value_counts().reset_index()
        stat_counts.columns = ["Status", "Course Count"]

        col1, col2 = st.columns([1, 1])
        with col1:
            fig_stat = px.pie(
                stat_counts,
                names="Status",
                values="Course Count",
                hole=0.5,
                color="Status",
                color_discrete_map={"Completed": "#10b981", "Enrolled": "#3b82f6", "Upcoming": "#94a3b8"}
            )
            fig_stat.update_layout(height=260, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_stat, use_container_width=True)

        with col2:
            st.markdown("#### Status Summary")
            for _, r in stat_counts.iterrows():
                st.write(f"- **{r['Status']}:** {r['Course Count']} Courses")
            st.info("Currently 5 courses enrolled in active Semester 3.")

# ---------------------------------------------------------
# TAB 8: SCORECARD & INTERACTIVE GPA SIMULATOR
# ---------------------------------------------------------
elif selected_page == "Scorecard & GPA Simulator":
    st.markdown('<div class="section-title">🎯 Academic Scorecard & Interactive GPA Simulator</div>', unsafe_allow_html=True)
    st.caption("Verified assessment scores, prototype percentage, and real-time interactive What-If GPA projection simulator.")

    st.info(
        "ℹ️ **Prototype Score Metric:** Development formula is calculated as `(Total Score / Total Max Marks) * 100`. "
        "Use the interactive GPA Simulator below to forecast your upcoming semester SGPA and cumulative CGPA."
    )

    if not scores_df.empty:
        tot_score = scores_df["score"].sum()
        tot_max = scores_df["max_marks"].sum()
        proto_pct = (tot_score / tot_max * 100) if tot_max > 0 else 0.0

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Cumulative Prototype Average", f"{proto_pct:.2f}%")
        with m2:
            st.metric("Total Marks Scored", f"{tot_score:.0f} / {tot_max:.0f}")
        with m3:
            st.metric("Assessments Evaluated", len(scores_df))

        # Real-Time Interactive GPA Simulator ("What-If" Forecaster)
        st.markdown("---")
        st.markdown('<div class="section-title">⚡ Interactive "What-If" GPA Projection Engine</div>', unsafe_allow_html=True)
        st.caption("Select your expected letter grades for active Semester 3 courses to simulate your projected SGPA & CGPA:")

        grade_points = {
            "O (Outstanding - 10)": 10.0,
            "A+ (Excellent - 9)": 9.0,
            "A (Very Good - 8)": 8.0,
            "B+ (Good - 7)": 7.0,
            "B (Above Average - 6)": 6.0,
            "C (Average - 5)": 5.0,
            "F (Fail - 0)": 0.0
        }

        active_sem3_courses = courses_df[courses_df["semester"] == 3] if not courses_df.empty else pd.DataFrame()
        
        sim_col_l, sim_col_r = st.columns([3, 2])
        
        selected_grades = {}
        with sim_col_l:
            st.markdown("##### 📚 Expected Course Grades (Semester 3)")
            for _, cr in active_sem3_courses.iterrows():
                c_code = cr["course_code"]
                c_name = cr["course_name"]
                c_credits = int(cr["credits"])
                default_idx = 1 if "Lab" in c_name else 2  # default A+ or A
                selected_grades[c_code] = {
                    "credits": c_credits,
                    "grade": st.selectbox(
                        f"{c_code}: {c_name} ({c_credits} Cr)",
                        options=list(grade_points.keys()),
                        index=default_idx,
                        key=f"sim_grade_{c_code}"
                    )
                }

        # Calculate projected SGPA
        tot_cr_sim = sum(item["credits"] for item in selected_grades.values())
        tot_pts_sim = sum(item["credits"] * grade_points[item["grade"]] for item in selected_grades.values())
        projected_sgpa = (tot_pts_sim / tot_cr_sim) if tot_cr_sim > 0 else 0.0

        # Prior CGPA calculation: Sem 1 & 2 completed credits: 49 credits @ ~8.78 GPA
        prior_credits = 49
        prior_pts = 49 * 8.78
        projected_cgpa = (prior_pts + tot_pts_sim) / (prior_credits + tot_cr_sim)

        with sim_col_r:
            st.markdown("##### 🚀 Projected Outcomes")
            st.markdown(f"""
            <div class="interactive-card" style="background: #f8fafc; border: 2px solid {curr_theme['primary']};">
                <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Projected Semester 3 SGPA</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: {curr_theme['primary']};">{projected_sgpa:.2f} <span style="font-size: 1rem; color: #64748b;">/ 10.0</span></div>
                <hr style="margin: 10px 0;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Updated Cumulative CGPA</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #0f172a;">{projected_cgpa:.2f} <span style="font-size: 0.9rem; color: #059669; font-weight: 600;">(+{projected_cgpa - 8.78:+.2f} delta)</span></div>
                <p style="font-size: 0.85rem; color: #475569; margin-top: 8px;">
                    🎯 <strong>Honours Tier:</strong> {'Eligible for Dean\'s List & Distinction!' if projected_cgpa >= 8.5 else 'First Class with Distinction range.'}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📋 Assessment Score Records")
        st.dataframe(scores_df, use_container_width=True, hide_index=True)

        # Plotly Radar Chart of Competency Domains
        st.markdown("#### 🕸️ Skill Competency Radar")
        radar_categories = ['Algorithms & DSA', 'Computer Architecture', 'Discrete Mathematics', 'Java OOP & Software', 'Database Systems']
        radar_scores = [92, 85, 88, 90, 86]
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=radar_scores,
            theta=radar_categories,
            fill='toself',
            name='Student Proficiency',
            line_color=curr_theme["primary"]
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=300,
            margin=dict(t=20, b=20, l=40, r=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.warning("No scores recorded.")

# ---------------------------------------------------------
# TAB 9: INTERACTIVE PLAN & CHECKLIST CONTROL CENTER
# ---------------------------------------------------------
elif selected_page == "Plan & Checklist":
    st.markdown('<div class="section-title">✅ Degree Execution Checklist & Control Panel</div>', unsafe_allow_html=True)
    st.caption("Interactive control center for degree requirements, project milestones, and career readiness.")

    if "local_checklist" not in st.session_state:
        st.session_state["local_checklist"] = checklist_df.copy()

    chk = st.session_state["local_checklist"]

    if not chk.empty:
        chk["parsed_target"] = pd.to_datetime(chk["target_date"], errors="coerce").dt.date

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

        chk["Health"] = chk.apply(compute_health, axis=1)

        total_items = len(chk)
        done_items = len(chk[chk["Health"] == "Done"])
        due_soon_items = len(chk[chk["Health"] == "Due Soon"])
        overdue_items = len(chk[chk["Health"] == "Overdue"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Action Items", total_items)
        c2.metric("Completed (Done)", done_items, f"{done_items/total_items*100:.0f}%")
        c3.metric("Due Soon (Next 7 Days)", due_soon_items)
        c4.metric("Overdue Items", overdue_items)

        st.progress(done_items / total_items if total_items > 0 else 0)

        # Interactive Status Updater List
        st.markdown("---")
        st.markdown("#### ⚡ Interactive Task Manager (Click to Update Status)")

        # Filter by category
        categories = ["All Categories"] + list(chk["category"].unique())
        cat_choice = st.selectbox("Filter Category", categories)

        displayed_chk = chk if cat_choice == "All Categories" else chk[chk["category"] == cat_choice]

        for idx, row in displayed_chk.iterrows():
            badge_icon = "✅" if row["status"] == "Done" else ("🔄" if row["status"] == "In Progress" else "⏳")
            
            with st.container():
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 8px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{badge_icon} {row['item']}</strong><br>
                        <span style="font-size: 0.8rem; color: #64748b;">Target: {row['target_date']} • <em>{row['category']}</em> • Notes: {row['notes']}</span>
                    </div>
                    <div>
                        <span class="badge-neutral">{row['Health']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Interactive toggle buttons
                b_col1, b_col2, b_col3, _ = st.columns([1, 1, 1, 4])
                with b_col1:
                    if st.button("Mark Done ✅", key=f"btn_done_{idx}", use_container_width=True):
                        st.session_state["local_checklist"].at[idx, "status"] = "Done"
                        save_data("plan_checklist.csv", st.session_state["local_checklist"])
                        st.rerun()
                with b_col2:
                    if st.button("In Progress 🔄", key=f"btn_inp_{idx}", use_container_width=True):
                        st.session_state["local_checklist"].at[idx, "status"] = "In Progress"
                        save_data("plan_checklist.csv", st.session_state["local_checklist"])
                        st.rerun()
                with b_col3:
                    if st.button("Pending ⏳", key=f"btn_pend_{idx}", use_container_width=True):
                        st.session_state["local_checklist"].at[idx, "status"] = "Pending"
                        save_data("plan_checklist.csv", st.session_state["local_checklist"])
                        st.rerun()

        # Add New Task Form
        st.markdown("---")
        with st.expander("➕ Add New Milestone / Checklist Task"):
            with st.form("new_task_form"):
                new_cat = st.selectbox("Category", ["Semester Preparation", "Assessments", "Labs", "Projects", "Degree Milestones", "Career & Placement", "Document Vault"])
                new_item = st.text_input("Task Title / Milestone")
                new_date = st.date_input("Target Date", value=TODAY + timedelta(days=14))
                new_notes = st.text_input("Notes / Resources", placeholder="e.g. GitHub link, reference doc...")
                submitted = st.form_submit_button("Add Task to Checklist")

                if submitted and new_item.strip():
                    new_row = pd.DataFrame([{
                        "category": new_cat,
                        "item": new_item.strip(),
                        "target_date": new_date.strftime("%Y-%m-%d"),
                        "status": "Pending",
                        "notes": new_notes.strip()
                    }])
                    st.session_state["local_checklist"] = pd.concat([st.session_state["local_checklist"], new_row], ignore_index=True)
                    save_data("plan_checklist.csv", st.session_state["local_checklist"])
                    st.success(f"Added task: '{new_item}'")
                    st.rerun()

# ---------------------------------------------------------
# TAB 10: ASK DEGREE AI (INTERACTIVE COPILOT)
# ---------------------------------------------------------
elif selected_page == "Ask Degree AI":
    st.markdown('<div class="section-title">🤖 Ask Degree AI Copilot</div>', unsafe_allow_html=True)
    st.caption("AI-grounded academic copilot with zero-hallucination guardrails and clickable suggestion prompts.")

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

    with st.expander("⚙️ AI Grounding Settings & Configuration", expanded=False):
        st.write("**Context Source:** 8-Semester Degree OS Grounding Matrix")
        if api_key:
            st.success("🟢 Google Gemini API connected (Model: gemini-2.5-flash)")
        else:
            st.info("ℹ️ Running in **Deterministic Grounded Mode**. Safe refusal rules active.")

    # Interactive Quick-Prompt Suggestion Pills (1-Click Query Testing)
    st.markdown("##### 💡 Quick Suggestions (Click to Ask):")
    p1, p2, p3, p4, p5 = st.columns(5)
    
    suggested_query = None
    with p1:
        if st.button("📌 Incomplete Sem 3?", key="p_inc", use_container_width=True):
            suggested_query = "What courses are still incomplete in Semester 3?"
    with p2:
        if st.button("⏳ Next IA / Exam?", key="p_next_ia", use_container_width=True):
            suggested_query = "When is my next internal assessment?"
    with p3:
        if st.button("🌴 Next Holiday?", key="p_next_hol", use_container_width=True):
            suggested_query = "Show my next holiday"
    with p4:
        if st.button("🎯 Degree Progress?", key="p_prog", use_container_width=True):
            suggested_query = "What is my degree completion percentage and completed credits?"
    with p5:
        if st.button("🛡️ CGPA Formula?", key="p_safe", use_container_width=True):
            suggested_query = "What is my official university CGPA formula?"

    if "degree_ai_messages" not in st.session_state:
        st.session_state.degree_ai_messages = [
            {
                "role": "assistant",
                "content": "Hello! I am **Degree AI**, your engineering academic copilot. Ask me questions about your courses, internal assessments, holidays, syllabus, or checklist.",
                "area": "System"
            }
        ]

    # Render previous conversation
    for msg in st.session_state.degree_ai_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "area" in msg and msg["area"] != "System":
                st.markdown(f'<span class="badge-neutral">📍 Data Area: {msg["area"]}</span>', unsafe_allow_html=True)

    def answer_locally(query: str):
        q = query.lower().strip()
        # Strict Safe AI Refusal Rule
        if "cgpa" in q or "sgpa" in q or "gpa formula" in q or "official formula" in q:
            return ("I cannot verify that from the current Degree OS data.", "Scores")
        if "attendance" in q or "regulation" in q or "condonation" in q or "hall ticket" in q:
            return ("I cannot verify that from the current Degree OS data.", "Calendar")

        if "incomplete" in q or "left" in q or "pending course" in q or "subjects left" in q:
            sub_c = courses_df[courses_df["semester"] == 3]
            inc = sub_c[sub_c["status"] != "Completed"]
            if not inc.empty:
                items = [f"- **{r['course_code']}**: {r['course_name']} ({r['status']})" for _, r in inc.iterrows()]
                ans = f"Incomplete courses in **Semester 3** ({len(inc)} remaining):\n" + "\n".join(items)
                return (ans, "Courses")
            else:
                return ("All courses in Semester 3 are completed!", "Courses")

        if "next" in q and ("assessment" in q or "ia" in q or "test" in q or "exam" in q):
            if not assessments_df.empty:
                ass_copy = assessments_df.copy()
                ass_copy["p_date"] = pd.to_datetime(ass_copy["date"], errors="coerce").dt.date
                up = ass_copy[ass_copy["p_date"] >= TODAY].sort_values("p_date")
                if not up.empty:
                    top = up.iloc[0]
                    return (f"Next assessment: **{top['course_code']} ({top['assessment_type']})** on **{top['date']}** (Max: {top['max_marks']}).", "Assessments")
            return ("No upcoming assessments found in the schedule.", "Assessments")

        if "holiday" in q:
            if not calendar_df.empty:
                cal_copy = calendar_df.copy()
                cal_copy["p_date"] = pd.to_datetime(cal_copy["date"], errors="coerce").dt.date
                up_hols = cal_copy[(cal_copy["event_type"].str.lower() == "holiday") & (cal_copy["p_date"] >= TODAY)].sort_values("p_date")
                if not up_hols.empty:
                    top_h = up_hols.iloc[0]
                    return (f"Next holiday: **{top_h['title']}** on **{top_h['date']}**.", "Calendar")
            return ("No upcoming holidays found in the calendar.", "Calendar")

        if "data structures" in q or "cs301" in q:
            ds = courses_df[courses_df["course_code"] == "CS301"]
            if not ds.empty:
                return (f"**CS301 (Data Structures) Syllabus:** {ds.iloc[0]['syllabus']}", "Courses")

        if "credit" in q or "progress" in q or "degree" in q:
            return (f"Degree Progress: **{completed_degree_credits} / {total_degree_credits} Credits Completed** ({degree_completion_pct:.1f}%). Semester 3 is currently in progress with 24 credits enrolled.", "Semesters")

        return ("I cannot verify that from the current Degree OS data.", "Degree OS")

    def query_gemini_grounded(query: str):
        q = query.lower().strip()
        if "cgpa formula" in q or "official university formula" in q or "attendance percentage" in q:
            return ("I cannot verify that from the current Degree OS data.", "Scores")
        if not api_key:
            return answer_locally(query)
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            prompt = f"""You are 'Degree AI', an intelligent assistant for My Engineering Degree OS.
You must answer the student's question SOLELY using the verified Degree OS data below.
STRICT RULE: If the answer cannot be verified from the data below (such as official university CGPA conversion formulas, attendance regulations, hall ticket policies), you MUST respond with EXACTLY:
"I cannot verify that from the current Degree OS data."

DATA CONTEXT:
{compact_context}

STUDENT QUESTION:
{query}
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            ans = response.text.strip()
            return (ans, "Gemini Grounded")
        except Exception:
            return answer_locally(query)

    # Process prompt from text input OR button click
    user_prompt = st.chat_input("Ask about syllabus, assessments, calendar, or checklist...")
    if suggested_query:
        user_prompt = suggested_query

    if user_prompt:
        st.session_state.degree_ai_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing verified Degree OS dataset..."):
                response_text, area = query_gemini_grounded(user_prompt)
                st.write(response_text)
                st.markdown(f'<span class="badge-neutral">📍 Data Area: {area}</span>', unsafe_allow_html=True)
                st.session_state.degree_ai_messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "area": area
                })

# ---------------------------------------------------------
# TAB 11: DATA ADMIN & CLOUD SYNCHRONIZATION
# ---------------------------------------------------------
elif selected_page == "Data Admin":
    st.markdown('<div class="section-title">⚙️ Data Admin & Cloud Database Management</div>', unsafe_allow_html=True)
    st.caption("Inspect live tables, test cloud sync, and export/import degree datasets.")

    sup_url, sup_key = get_supabase_credentials()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("##### ☁️ Supabase Cloud Configuration")
        if sup_url and sup_key:
            st.success(f"🟢 Connected to Supabase Host:\n`{sup_url}`")
        else:
            st.warning("⚠️ Running in Local CSV Fallback Mode.")

    with col_s2:
        st.markdown("##### 📁 Local Data Directory")
        st.info(f"Storage Path:\n`{DATA_DIR.resolve()}`")

    st.markdown("---")
    st.markdown("#### 📋 Inspect & Download Data Tables")
    chosen_file = st.selectbox("Select Table", list(CSV_TO_TABLE.keys()))
    t_df = load_data(chosen_file)
    st.dataframe(t_df, use_container_width=True)

    csv_bytes = t_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {chosen_file}",
        data=csv_bytes,
        file_name=chosen_file,
        mime="text/csv"
    )

# ---------------------------------------------------------
# TAB 12: STUDENT FEEDBACK (SUPABASE AUTH + RLS)
# ---------------------------------------------------------
elif selected_page == "Student Feedback (Supabase RLS)":
    st.markdown('<div class="section-title">🔐 Student Feedback (Supabase Auth & RLS)</div>', unsafe_allow_html=True)
    st.caption("Authenticated, secure feedback storage with PostgreSQL Row Level Security (RLS).")

    sup_url, sup_key = get_supabase_credentials()

    if not sup_url or not sup_key:
        st.warning("Please configure SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in secrets or .env to access authenticated feedback.")
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

        with st.form("signin_form"):
            in_email = st.text_input("Student Email", placeholder="student@engineeringos.com")
            in_password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Sign In")

            if submit_login:
                if not in_email or not in_password:
                    st.warning("Please enter both email and password.")
                else:
                    try:
                        res = auth_db.auth.sign_in_with_password({"email": in_email.strip(), "password": in_password})
                        st.session_state["_supabase_auth_client"] = auth_db
                        st.success(f"Successfully signed in as {in_email}!")
                        st.rerun()
                    except Exception as auth_err:
                        st.error(f"Authentication failed: {auth_err}")

        st.stop()

    user_info = current_session.user
    st.info(f"👤 Signed in as: **{user_info.email}**")

    if st.button("🚪 Sign Out"):
        try:
            auth_db.auth.sign_out()
            st.session_state["_supabase_auth_client"] = create_client(sup_url, sup_key)
            st.success("Signed out successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"Error signing out: {e}")

    st.markdown("---")
    st.subheader("📝 Submit New Feedback")

    with st.form("feedback_form"):
        f_name = st.text_input("Your Name", value="Prajwal S Hiremath")
        f_rating = st.select_slider("Rate Degree OS Experience", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        f_msg = st.text_area("Your Feedback / Feature Suggestions", placeholder="e.g. The interactive GPA simulator and checklist tracking are fantastic...")
        f_submit = st.form_submit_button("Submit Secure Feedback")

        if f_submit:
            f_name_clean = f_name.strip()
            f_msg_clean = f"[{f_rating}] " + f_msg.strip()
            if not f_name_clean or not f_msg.strip():
                st.warning("Please enter your name, rating, and feedback message.")
            else:
                try:
                    fb_result = (
                        auth_db.table("app_feedback")
                        .insert({"name": f_name_clean, "message": f_msg_clean})
                        .execute()
                    )
                    st.success("✅ Feedback securely saved to Supabase with Row Level Security (RLS)!")
                    st.rerun()
                except Exception as insert_err:
                    st.error(f"Failed to submit feedback: {insert_err}")

    st.markdown("---")
    st.subheader("📜 Your Saved Feedback (RLS Protected)")
    st.caption("You can only view records created by your authenticated student account.")

    try:
        user_records = (
            auth_db.table("app_feedback")
            .select("id, name, message, created_at")
            .order("created_at", desc=True)
            .execute()
        )
        if user_records.data and len(user_records.data) > 0:
            fb_df = pd.DataFrame(user_records.data)
            st.dataframe(fb_df, use_container_width=True, hide_index=True)
        else:
            st.info("No feedback saved for this account yet.")
    except Exception as read_err:
        st.error(f"Could not load records: {read_err}")
