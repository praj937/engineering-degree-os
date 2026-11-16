# 🎓 My Engineering Degree OS

> A self-managed 1st-to-8th semester engineering degree command center with schedules, syllabus, assessments, progress, scorecard, plan/checklist, and an AI chatbot.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Mission
To provide an engineering student with a single unified dashboard to track their complete 8-semester academic journey, know what is coming next, record academic progress, edit data without touching code, and ask questions through an AI chatbot that grounds its answers in verified degree data.

---

## 🚀 Key Features (11 Core Modules)

| # | Tab / Module | Description | Pass Condition |
|---|---|---|---|
| 1 | **Dashboard** | Degree overview, current semester (Sem 3), degree completion %, next assessment countdown, next holiday, prototype score summary, and semester-by-semester credit bar chart. | ✅ Complete & Usable |
| 2 | **Semesters 1-8** | 8 individual semester cards with course count, total vs completed credits, status badges (`Completed`, `In Progress`, `Not Started`), and progress bars, plus filterable semester details. | ✅ Complete & Usable |
| 3 | **Courses & Syllabus** | Filterable course directory across all 8 semesters with course code, name, credits, faculty, completion status, and expandable module topic outlines. Includes live search. | ✅ Complete & Usable |
| 4 | **University Syllabus** | Programme specification summary (B.Tech CSE, CBCS regulations, 175 credits, 8 semesters), curriculum progression by year, and configurable official syllabus URL reference. | ✅ Complete & Usable |
| 5 | **Academic / Leave Calendar** | Institutional calendar co-listing academic events, holidays, and examination schedules with date relative countdowns, filterable by academic year, semester, and event type. | ✅ Complete & Usable |
| 6 | **Internal Assessments** | Tracking scheduled IA1, IA2, assignments, lab evaluations, project reviews, and end-semester exams with dates, maximum marks, and status. | ✅ Complete & Usable |
| 7 | **Status Tracker** | Course progress monitor showing count of Not Started, In Progress, and Completed courses with a dynamic progress bar for any selected semester, plus an 8-semester breakdown matrix. | ✅ Complete & Usable |
| 8 | **Scorecard** | Calculates prototype score percentage as `(Total Score / Total Max Marks) * 100` from loaded evaluation records with grades and semester averages. Explicitly disclaims prototype metric vs official CGPA. | ✅ Complete & Usable |
| 9 | **Plan & Checklist** | Execution control panel with summary metrics (Total, Done, Due Soon, Overdue), **This Week** (next 7 days), **Semester Milestones**, and **Degree Milestones**, editable directly in the app. | ✅ Complete & Usable |
| 10 | **Ask Degree AI** | Grounded chatbot answering student questions using degree data context. Uses Gemini API (via `google-genai`) when available, with a built-in deterministic local fallback engine and strict Safe-AI refusal rules. | ✅ Complete & Usable |
| 11 | **Data Admin** | Interactive `st.data_editor` to view, modify, and save any of the 6 degree CSV tables directly to disk without code changes. | ✅ Complete & Usable |

---

## 🛠️ Free Tool Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/)
- **Data Storage & Manipulation:** CSV files + [Pandas](https://pandas.pydata.org/)
- **AI & LLM Grounding:** [Google AI Studio](https://aistudio.google.com/) + Gemini API (`google-genai` SDK)
- **Version Control & Hosting:** [GitHub](https://github.com/) + [Streamlit Community Cloud](https://share.streamlit.io/)

---

## 📁 Repository Structure

```text
engineering-degree-os/
│
├── app.py                      # Main single-file Streamlit application
├── requirements.txt            # App dependencies (streamlit, pandas, google-genai)
├── README.md                   # Project documentation & execution guide
├── .gitignore                  # Git ignore rules for cache and secrets
│
└── data/                       # Maintainable CSV data store
    ├── semesters.csv           # Semesters 1-8 status and credits
    ├── courses.csv             # 24+ courses across all 8 semesters with syllabus
    ├── academic_calendar.csv   # Holidays, academic milestones, and exams
    ├── assessments.csv         # IA1, IA2, assignments, lab evaluations, exams
    ├── scores.csv              # Student marks, max marks, and letter grades
    └── plan_checklist.csv      # Degree milestones, tasks, target dates, and status
```

---

## 🏃 Local Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/praj937/engineering-degree-os.git
cd engineering-degree-os
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API Key
To enable Gemini natural-language answers, either set an environment variable or create `.streamlit/secrets.toml`:
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your-api-key-here"
```
*(If no API key is provided, the app automatically runs in **Deterministic Local Grounding Mode**, supporting all standard queries without errors).*

### 4. Run the Streamlit app
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🤖 Ask Degree AI & Safe-AI Grounding

Degree AI is strictly constrained to prevent hallucination:
- **System Instruction:** *"You are Degree AI. Answer only from the supplied degree data. Do not invent university rules, dates, marks, formulas or syllabus content. If the requested information is missing, say: I cannot verify that from the current Degree OS data."*
- **Source Attribution:** Every response displays which data area was queried (`Courses`, `Calendar`, `Assessments`, `Scores`, or `Plan`).
- **Grounded Verification Examples:**
  - *"What courses are still incomplete in Semester 3?"* ➔ Cites incomplete courses from `courses.csv`.
  - *"When is my next internal assessment?"* ➔ Cites next upcoming test from `assessments.csv`.
  - *"Show my next holiday"* ➔ Cites next holiday from `academic_calendar.csv`.
  - *"What topics are in Data Structures?"* ➔ Fetches syllabus modules for CS301.
  - *"What is my official university CGPA formula?"* ➔ Safely responds: `"I cannot verify that from the current Degree OS data."`

---

## 🧪 Acceptance Test Results

- [x] **All 11 required navigation items are visible** (Dashboard, Semesters 1-8, Courses & Syllabus, University Syllabus, Academic Calendar, Internal Assessments, Status Tracker, Scorecard, Plan & Checklist, Ask Degree AI, Data Admin).
- [x] **Semester 1 to Semester 8 can all be selected** and display consistent cards and metrics.
- [x] **Course data changes when the semester filter changes.**
- [x] **Calendar distinguishes academic events and leave/holidays.**
- [x] **Assessment dates and score data are visible and calculated.**
- [x] **Plan & Checklist can be edited without touching code** via `st.data_editor` and saved to CSV.
- [x] **Chatbot gives grounded answers and a safe "cannot verify" response** when asked ungrounded policy questions.

---

## 🌐 Deployment to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **New app** and select:
   - **Repository:** `praj937/engineering-degree-os`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. In **Advanced settings / Secrets**, add `GEMINI_API_KEY = "..."` (optional).
5. Click **Deploy!**

---

## 📋 Assignment Submission Form

- **Team / Student:** Prajwal S Hiremath
- **GitHub Repository URL:** [https://github.com/praj937/engineering-degree-os](https://github.com/praj937/engineering-degree-os)
- **Live Streamlit App URL:** [https://engineering-degree-os-czzwagvsqtnehhclnfndhd.streamlit.app/](https://engineering-degree-os-czzwagvsqtnehhclnfndhd.streamlit.app/)
- **One failure/safety example:** Question: *"What is my official university CGPA formula?"* ➔ Response: *"I cannot verify that from the current Degree OS data."* (Safe-AI rule strictly enforced).
- **One improvement for next version:** Add PDF syllabus parsing with automatic course extraction and attendance percentage tracking with condonation alerts.
