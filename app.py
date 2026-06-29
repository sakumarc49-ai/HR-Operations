from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "hr_operations.db"

st.set_page_config(
    page_title="PeopleFlow — HR Operations",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


WORKFLOW = [
    ("01", "Manpower Requirement", "Capture and approve workforce demand", "requisitions"),
    ("02", "Recruitment", "Source, screen and interview talent", "candidates"),
    ("03", "Selection & Offer", "Close compensation and secure acceptance", "offers"),
    ("04", "Pre-Onboarding", "Verify documents and create records", "preboarding"),
    ("05", "Onboarding", "Prepare access, orientation and joining", "onboarding"),
    ("06", "Employee Lifecycle", "Attendance, leave, learning and engagement", "lifecycle"),
    ("07", "Performance", "Goals, reviews, feedback and growth", "performance"),
    ("08", "Payroll & Benefits", "Payroll, tax, insurance and benefits", "payroll"),
    ("09", "Employee Relations", "Grievances, policy and compliance", "relations"),
    ("10", "Exit Process", "Transfer knowledge and close employment", "exit"),
]

STAGE_META = {
    "requisitions": ("Manpower Requirement", "business_center"),
    "candidates": ("Recruitment", "person_search"),
    "offers": ("Selection & Offer", "handshake"),
    "preboarding": ("Pre-Onboarding", "fact_check"),
    "onboarding": ("Onboarding", "rocket_launch"),
    "lifecycle": ("Employee Lifecycle", "groups"),
    "performance": ("Performance", "monitoring"),
    "payroll": ("Payroll & Benefits", "payments"),
    "relations": ("Employee Relations", "balance"),
    "exit": ("Exit Process", "logout"),
}

TASK_TEMPLATES = {
    "requisitions": ["Validate business justification", "Confirm budget", "Approve hiring request"],
    "candidates": ["Publish job post", "Screen applications", "Schedule interviews", "Collect manager feedback"],
    "offers": ["Record selection decision", "Complete salary discussion", "Release offer letter", "Confirm acceptance"],
    "preboarding": ["Collect identity documents", "Complete background verification", "Create employee record"],
    "onboarding": ["Complete joining formalities", "Create employee ID", "Provision system access", "Run orientation"],
    "lifecycle": ["Review attendance", "Process leave requests", "Assign training", "Plan engagement activity"],
    "performance": ["Set goals", "Complete performance review", "Hold feedback session", "Process appraisal"],
    "payroll": ["Validate attendance inputs", "Process salary", "Apply tax deductions", "Update benefits"],
    "relations": ["Acknowledge grievance", "Assign case owner", "Review policy", "Record resolution"],
    "exit": ["Acknowledge resignation", "Plan knowledge transfer", "Conduct exit interview", "Process final settlement", "Issue relieving letter"],
}


@contextmanager
def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with db() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS requisitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                department TEXT NOT NULL,
                manager TEXT NOT NULL,
                openings INTEGER NOT NULL,
                priority TEXT NOT NULL,
                target_date TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                source TEXT NOT NULL,
                stage TEXT NOT NULL,
                score INTEGER NOT NULL,
                owner TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                designation TEXT NOT NULL,
                join_date TEXT NOT NULL,
                status TEXT NOT NULL,
                manager TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                stage TEXT NOT NULL,
                subject TEXT NOT NULL,
                owner TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        if con.execute("SELECT COUNT(*) FROM requisitions").fetchone()[0] == 0:
            now = datetime.now().isoformat(timespec="minutes")
            con.executemany(
                "INSERT INTO requisitions(role,department,manager,openings,priority,target_date,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
                [
                    ("Senior Data Analyst", "Analytics", "Priya Nair", 2, "High", str(date.today() + timedelta(days=22)), "Recruiting", now),
                    ("Product Designer", "Product", "Arjun Mehta", 1, "Medium", str(date.today() + timedelta(days=35)), "Approved", now),
                    ("Customer Success Lead", "Customer Success", "Neha Shah", 1, "Urgent", str(date.today() + timedelta(days=12)), "Interviewing", now),
                    ("Finance Associate", "Finance", "Rohan Iyer", 2, "Medium", str(date.today() + timedelta(days=45)), "Pending approval", now),
                ],
            )
            con.executemany(
                "INSERT INTO candidates(name,role,source,stage,score,owner,updated_at) VALUES(?,?,?,?,?,?,?)",
                [
                    ("Aarav Kapoor", "Senior Data Analyst", "LinkedIn", "Interview", 88, "Maya", now),
                    ("Diya Menon", "Senior Data Analyst", "Referral", "Screening", 82, "Maya", now),
                    ("Kabir Rao", "Product Designer", "Careers page", "Applied", 76, "Sameer", now),
                    ("Ananya Bose", "Customer Success Lead", "Referral", "Offer", 92, "Sameer", now),
                    ("Vivaan Joshi", "Customer Success Lead", "Naukri", "Interview", 85, "Maya", now),
                ],
            )
            con.executemany(
                "INSERT INTO employees(name,department,designation,join_date,status,manager) VALUES(?,?,?,?,?,?)",
                [
                    ("Ishita Verma", "Engineering", "Software Engineer", str(date.today() - timedelta(days=310)), "Active", "Karan Malhotra"),
                    ("Aditya Sen", "Marketing", "Campaign Manager", str(date.today() - timedelta(days=188)), "Active", "Naina Gupta"),
                    ("Meera Kulkarni", "Analytics", "Data Analyst", str(date.today() - timedelta(days=42)), "Probation", "Priya Nair"),
                    ("Reyansh Jain", "Operations", "Operations Executive", str(date.today() - timedelta(days=9)), "Onboarding", "Dev Patel"),
                ],
            )
            con.executemany(
                "INSERT INTO tasks(title,stage,subject,owner,due_date,priority,status) VALUES(?,?,?,?,?,?,?)",
                [
                    ("Schedule panel interview", "candidates", "Aarav Kapoor", "Maya", str(date.today() + timedelta(days=1)), "High", "Open"),
                    ("Release offer letter", "offers", "Ananya Bose", "Sameer", str(date.today()), "Urgent", "Open"),
                    ("Provision laptop access", "onboarding", "Reyansh Jain", "IT Desk", str(date.today() + timedelta(days=2)), "High", "Open"),
                    ("Complete 30-day check-in", "lifecycle", "Meera Kulkarni", "Priya Nair", str(date.today() - timedelta(days=2)), "Medium", "Open"),
                    ("Validate monthly payroll inputs", "payroll", "All employees", "Payroll", str(date.today() + timedelta(days=4)), "High", "Open"),
                    ("Update knowledge-transfer plan", "exit", "Nikhil Suri", "Dev Patel", str(date.today() + timedelta(days=3)), "Medium", "Open"),
                ],
            )
            con.executemany(
                "INSERT INTO activity(event,detail,created_at) VALUES(?,?,?)",
                [
                    ("Offer approved", "Ananya Bose · Customer Success Lead", now),
                    ("Candidate advanced", "Aarav Kapoor moved to Interview", now),
                    ("New joiner added", "Reyansh Jain · Operations", now),
                    ("Requisition created", "Finance Associate · 2 openings", now),
                ],
            )


def query(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with db() as con:
        return con.execute(sql, params).fetchall()


def execute(sql: str, params: tuple = ()) -> None:
    with db() as con:
        con.execute(sql, params)


def log_activity(event: str, detail: str) -> None:
    execute(
        "INSERT INTO activity(event,detail,created_at) VALUES(?,?,?)",
        (event, detail, datetime.now().isoformat(timespec="minutes")),
    )


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
        :root { --ink:#14231f; --forest:#173d35; --forest-2:#24594e; --sage:#7ea89b; --gold:#d2b279; --ivory:#f5f3ee; --paper:#faf9f6; --line:#e7e3da; --muted:#727b77; }
        html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
        .stApp { background:radial-gradient(circle at 85% 0%,rgba(210,178,121,.10),transparent 27%),var(--paper); color:var(--ink); }
        [data-testid="stHeader"] { background:rgba(250,249,246,.82); backdrop-filter:blur(18px); border-bottom:1px solid rgba(231,227,218,.65); }
        [data-testid="stSidebar"] { background:linear-gradient(180deg,#10231e 0%,#0d1916 100%); border-right:1px solid rgba(255,255,255,.06); }
        [data-testid="stSidebar"] * { color:#eef2ef; }
        [data-testid="stSidebar"] .stRadio > div { gap:.35rem; }
        [data-testid="stSidebar"] .stRadio label { padding:.48rem .65rem; border-radius:12px; transition:all .18s ease; }
        [data-testid="stSidebar"] .stRadio label:hover { background:rgba(255,255,255,.06); transform:translateX(2px); }
        [data-testid="stSidebar"] .stRadio [data-checked="true"] { background:linear-gradient(90deg,rgba(210,178,121,.20),rgba(255,255,255,.06)); border:1px solid rgba(210,178,121,.18); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { line-height:1.35; }
        .block-container { padding-top:4rem; padding-bottom:4rem; max-width:1460px; }
        h1,h2,h3 { font-family:'DM Sans',sans-serif !important; color:var(--ink); letter-spacing:-.035em; }
        .brand-lockup { padding:12px 4px 26px; }
        .brand-mark { width:34px; height:34px; display:inline-flex; align-items:center; justify-content:center; background:linear-gradient(145deg,#d9c08f,#a78348); color:#10231e; border-radius:11px; font-family:'Instrument Serif'; font-size:23px; margin-bottom:13px; box-shadow:0 8px 22px rgba(0,0,0,.2); }
        .brand { font-family:'Instrument Serif'; font-size:29px; line-height:1; color:#fff; letter-spacing:-.02em; }
        .brand-dot { color:var(--gold); }
        .brand-sub { color:#82968f; font-size:10px; margin-top:8px; letter-spacing:.17em; text-transform:uppercase; }
        .eyebrow { font-size:10px; text-transform:uppercase; letter-spacing:.19em; color:#8f7350; font-weight:700; margin-bottom:8px; }
        .page-title { font:400 43px/1.08 'Instrument Serif'; color:var(--ink); margin:0 0 7px; letter-spacing:-.025em; }
        .page-sub { color:var(--muted); font-size:14px; margin-bottom:26px; max-width:760px; }
        .hero { overflow:hidden; position:relative; background:radial-gradient(circle at 88% 15%,rgba(210,178,121,.24),transparent 23%),radial-gradient(circle at 72% 120%,rgba(87,148,132,.36),transparent 38%),linear-gradient(125deg,#10241f 0%,#173d35 65%,#24594e 100%); border-radius:28px; padding:35px 38px 34px; color:white; margin-bottom:22px; box-shadow:0 22px 55px rgba(18,47,40,.18); border:1px solid rgba(255,255,255,.08); }
        .hero:after { content:''; position:absolute; width:170px; height:170px; border:1px solid rgba(255,255,255,.13); border-radius:50%; right:-38px; top:-70px; box-shadow:0 0 0 28px rgba(255,255,255,.025),0 0 0 56px rgba(255,255,255,.018); }
        .hero h1 { font-family:'Instrument Serif' !important; font-weight:400; letter-spacing:-.02em; color:#fff; font-size:43px; margin:0 0 10px; }
        .hero h1 em { color:#e7d4ab; font-weight:400; }
        .hero p { color:#bed0ca; max-width:650px; margin:0; font-size:14px; line-height:1.65; }
        .hero-tag { display:inline-flex; align-items:center; gap:7px; color:#e5c98f; font-size:10px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; margin-bottom:16px; }
        .hero-tag:before { content:''; width:6px; height:6px; background:#d2b279; border-radius:50%; box-shadow:0 0 0 4px rgba(210,178,121,.12); }
        .hero-status { position:absolute; right:38px; bottom:33px; border-left:1px solid rgba(255,255,255,.16); padding-left:24px; z-index:1; }
        .hero-status-label { color:#8ca9a0; font-size:9px; letter-spacing:.14em; text-transform:uppercase; }
        .hero-status-value { color:#fff; font-size:13px; margin-top:5px; }
        .metric-card { position:relative; overflow:hidden; background:rgba(255,255,255,.88); border:1px solid var(--line); border-radius:18px; padding:19px 20px 17px; min-height:118px; box-shadow:0 8px 28px rgba(32,48,42,.055); transition:transform .18s ease,box-shadow .18s ease; }
        .metric-card:hover { transform:translateY(-2px); box-shadow:0 14px 34px rgba(32,48,42,.09); }
        .metric-card:before { content:''; position:absolute; top:0; left:20px; right:20px; height:2px; background:linear-gradient(90deg,var(--gold),transparent); }
        .metric-label { color:#818985; font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:.15em; }
        .metric-value { font:400 35px/1 'Instrument Serif'; color:var(--ink); margin:11px 0 7px; }
        .metric-note { color:#4f7d70; font-size:11px; font-weight:600; }
        .section-label { display:flex; align-items:center; gap:12px; font:600 17px 'DM Sans'; margin:28px 0 14px; color:var(--ink); letter-spacing:-.02em; }
        .section-label:after { content:''; height:1px; flex:1; background:linear-gradient(90deg,var(--line),transparent); }
        .workflow-card { background:rgba(255,255,255,.86); border:1px solid var(--line); border-radius:18px; padding:18px; height:154px; position:relative; overflow:hidden; box-shadow:0 5px 20px rgba(35,48,43,.04); transition:all .2s ease; }
        .workflow-card:hover { transform:translateY(-3px); border-color:#cfc4ad; box-shadow:0 13px 30px rgba(35,48,43,.09); }
        .workflow-card:before { content:''; position:absolute; width:52px; height:52px; border-radius:50%; background:rgba(126,168,155,.09); right:-18px; top:-18px; }
        .workflow-num { color:#94764b; font:700 9px 'DM Sans'; letter-spacing:.15em; text-transform:uppercase; }
        .workflow-name { color:var(--ink); font:600 14px/1.3 'DM Sans'; margin:19px 0 7px; letter-spacing:-.02em; }
        .workflow-desc { color:#7b827f; font-size:11px; line-height:1.45; max-width:90%; }
        .workflow-arrow { position:absolute; bottom:13px; right:16px; width:23px; height:23px; display:flex; align-items:center; justify-content:center; color:#7c9f95; background:#eef4f1; border-radius:50%; font-size:13px; }
        .panel { background:rgba(255,255,255,.9); border:1px solid var(--line); border-radius:20px; padding:22px; box-shadow:0 8px 25px rgba(35,48,43,.05); }
        .status { display:inline-block; border-radius:999px; padding:4px 9px; font-size:11px; font-weight:700; }
        .status-open { color:#9a652b; background:#fbf0dc; }
        .status-done { color:#376f61; background:#e2f2ec; }
        div[data-testid="stDataFrame"] { background:white; border-radius:17px; overflow:hidden; border:1px solid var(--line); box-shadow:0 7px 24px rgba(35,48,43,.04); }
        .stButton > button { border-radius:12px; border:1px solid #dcd7cc; font-weight:600; min-height:41px; background:#fff; color:var(--ink); transition:all .18s ease; }
        .stButton > button:hover { border-color:#8b7550; color:#173d35; transform:translateY(-1px); box-shadow:0 7px 16px rgba(35,48,43,.08); }
        .stButton > button[kind="primary"] { background:linear-gradient(135deg,#173d35,#24594e); border-color:#173d35; color:white; }
        [data-testid="stForm"] { background:rgba(255,255,255,.9); border:1px solid var(--line); padding:24px; border-radius:20px; box-shadow:0 8px 25px rgba(35,48,43,.04); }
        [data-baseweb="input"] > div,[data-baseweb="select"] > div,textarea { border-radius:11px !important; border-color:#dedad1 !important; background:#fff !important; }
        [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid var(--line); }
        [data-baseweb="tab"] { border-radius:10px 10px 0 0; padding-left:16px; padding-right:16px; }
        [aria-selected="true"][role="tab"] { color:var(--forest) !important; font-weight:700; }
        .copilot { position:relative; overflow:hidden; background:radial-gradient(circle at 90% 0%,rgba(210,178,121,.22),transparent 30%),linear-gradient(140deg,#edf3ef,#f8f3e9); border:1px solid #ddd8ca; border-radius:22px; padding:26px; }
        .copilot-title { font:400 28px 'Instrument Serif'; color:var(--forest); }
        .copilot-answer { background:rgba(255,255,255,.9); border-radius:16px; padding:18px; margin-top:14px; color:#30453f; border:1px solid #e0ded6; line-height:1.6; box-shadow:0 8px 22px rgba(35,48,43,.04); }
        hr { border-color:rgba(255,255,255,.12) !important; }
        [data-testid="stSidebar"] hr { margin:1.4rem 0; }
        @media(max-width:900px) { .hero-status { display:none; } .hero { padding:28px 25px; } .hero h1 { font-size:35px; } .page-title { font-size:37px; } }
        footer { visibility:hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="eyebrow">{kicker}</div><div class="page-title">{title}</div><div class="page-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def metric(label: str, value: str | int, note: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def dataframe(rows: list[sqlite3.Row], columns: dict[str, str]) -> None:
    if not rows:
        st.info("No records yet. Add the first one to get started.")
        return
    frame = pd.DataFrame([dict(r) for r in rows])
    frame = frame[list(columns)].rename(columns=columns)
    st.dataframe(frame, width="stretch", hide_index=True)


def dashboard() -> None:
    reqs = query("SELECT * FROM requisitions")
    candidates = query("SELECT * FROM candidates")
    employees = query("SELECT * FROM employees")
    open_tasks = query("SELECT * FROM tasks WHERE status='Open'")
    overdue = sum(date.fromisoformat(t["due_date"]) < date.today() for t in open_tasks)
    offers = sum(c["stage"] == "Offer" for c in candidates)

    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-tag">People operations command centre</div>
          <h1>People, with <em>purpose.</em></h1>
          <p>Move every people process forward—from the first hiring request to a thoughtful farewell—with clarity, care and one beautifully simple view.</p>
          <div class="hero-status"><div class="hero-status-label">Today</div><div class="hero-status-value">{date.today().strftime('%A · %d %B')}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    with cols[0]: metric("Open positions", sum(r["openings"] for r in reqs if r["status"] != "Closed"), "Across active requisitions")
    with cols[1]: metric("Active candidates", len(candidates), f"{offers} currently at offer")
    with cols[2]: metric("Employees", len(employees), f"{sum(e['status']=='Onboarding' for e in employees)} joining now")
    with cols[3]: metric("Actions due", len(open_tasks), f"{overdue} overdue — attention needed" if overdue else "Everything on track")

    st.markdown('<div class="section-label">The employee journey</div>', unsafe_allow_html=True)
    for start in (0, 5):
        cols = st.columns(5)
        for col, (num, name, desc, stage) in zip(cols, WORKFLOW[start:start + 5]):
            count = len(query("SELECT id FROM tasks WHERE stage=? AND status='Open'", (stage,)))
            with col:
                st.markdown(
                    f'<div class="workflow-card"><div class="workflow-num">STEP {num} &nbsp;·&nbsp; {count} OPEN</div><div class="workflow-name">{name}</div><div class="workflow-desc">{desc}</div><div class="workflow-arrow">→</div></div>',
                    unsafe_allow_html=True,
                )

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown('<div class="section-label">Priority queue</div>', unsafe_allow_html=True)
        dataframe(
            query("SELECT title,subject,owner,due_date,priority FROM tasks WHERE status='Open' ORDER BY due_date LIMIT 7"),
            {"title": "Action", "subject": "For", "owner": "Owner", "due_date": "Due", "priority": "Priority"},
        )
    with right:
        st.markdown('<div class="section-label">Recent movement</div>', unsafe_allow_html=True)
        for item in query("SELECT * FROM activity ORDER BY id DESC LIMIT 6"):
            timestamp = item["created_at"].replace("T", " · ")
            st.markdown(f"**{item['event']}**  \n{item['detail']} · <span style='color:#9298a8;font-size:12px'>{timestamp}</span>", unsafe_allow_html=True)
            st.markdown("---")


def requisitions_page() -> None:
    page_header("Talent planning", "Manpower requirements", "Raise, approve and track hiring demand before recruitment begins.")
    tab1, tab2 = st.tabs(["Active requests", "Raise new request"])
    with tab1:
        rows = query("SELECT * FROM requisitions ORDER BY id DESC")
        cols = st.columns(3)
        with cols[0]: metric("Requests", len(rows), "Total requisitions")
        with cols[1]: metric("Openings", sum(r["openings"] for r in rows), "Planned headcount")
        with cols[2]: metric("Awaiting approval", sum(r["status"] == "Pending approval" for r in rows), "Manager action required")
        st.markdown('<div class="section-label">Requisition register</div>', unsafe_allow_html=True)
        dataframe(rows, {"id":"ID", "role":"Role", "department":"Department", "manager":"Hiring manager", "openings":"Openings", "priority":"Priority", "target_date":"Target date", "status":"Status"})
        if rows:
            with st.expander("Update request status"):
                c1, c2, c3 = st.columns([1, 1, .45])
                selected = c1.selectbox("Requisition", [f"REQ-{r['id']:03d} · {r['role']}" for r in rows])
                new_status = c2.selectbox("New status", ["Pending approval", "Approved", "Recruiting", "Interviewing", "Offer", "Closed"])
                if c3.button("Update", type="primary", width="stretch"):
                    req_id = int(selected.split("·")[0].replace("REQ-", "").strip())
                    execute("UPDATE requisitions SET status=? WHERE id=?", (new_status, req_id))
                    log_activity("Requisition updated", f"REQ-{req_id:03d} moved to {new_status}")
                    st.success("Request updated.")
                    st.rerun()
    with tab2:
        with st.form("new_req", clear_on_submit=True):
            c1, c2 = st.columns(2)
            role = c1.text_input("Role title", placeholder="e.g. Business Analyst")
            department = c2.selectbox("Department", ["Analytics", "Customer Success", "Engineering", "Finance", "HR", "Marketing", "Operations", "Product", "Sales"])
            manager = c1.text_input("Hiring manager", placeholder="Full name")
            openings = c2.number_input("Number of openings", 1, 100, 1)
            priority = c1.selectbox("Priority", ["Medium", "High", "Urgent", "Low"])
            target = c2.date_input("Target joining date", date.today() + timedelta(days=30), min_value=date.today())
            justification = st.text_area("Business justification", placeholder="Why is this role required now?")
            submitted = st.form_submit_button("Submit hiring request", type="primary")
            if submitted:
                if not role.strip() or not manager.strip() or not justification.strip():
                    st.error("Please complete the role, manager and business justification.")
                else:
                    execute("INSERT INTO requisitions(role,department,manager,openings,priority,target_date,status,created_at) VALUES(?,?,?,?,?,?,?,?)", (role.strip(), department, manager.strip(), openings, priority, str(target), "Pending approval", datetime.now().isoformat(timespec="minutes")))
                    log_activity("Requisition created", f"{role} · {openings} opening(s)")
                    st.success("Hiring request submitted to HR.")


def recruitment_page() -> None:
    page_header("Talent acquisition", "Recruitment pipeline", "Move candidates from application through interviews and into an accepted offer.")
    candidates = query("SELECT * FROM candidates ORDER BY id DESC")
    stages = ["Applied", "Screening", "Interview", "Selected", "Offer", "Accepted", "Rejected"]
    pipeline = st.columns(6)
    for col, stage in zip(pipeline, stages[:6]):
        with col:
            count = sum(c["stage"] == stage for c in candidates)
            st.markdown(f'<div class="metric-card"><div class="metric-label">{stage}</div><div class="metric-value">{count}</div><div class="metric-note">candidates</div></div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Candidate register", "Add candidate"])
    with tab1:
        dataframe(candidates, {"id":"ID", "name":"Candidate", "role":"Role", "source":"Source", "stage":"Stage", "score":"Score", "owner":"Recruiter", "updated_at":"Last updated"})
        if candidates:
            with st.expander("Advance or update candidate", expanded=True):
                c1, c2, c3 = st.columns([1.2, .8, .45])
                selected = c1.selectbox("Candidate", [f"CAN-{c['id']:03d} · {c['name']}" for c in candidates])
                stage = c2.selectbox("Move to", stages)
                if c3.button("Move", type="primary", width="stretch"):
                    cid = int(selected.split("·")[0].replace("CAN-", "").strip())
                    person = next(c for c in candidates if c["id"] == cid)
                    execute("UPDATE candidates SET stage=?,updated_at=? WHERE id=?", (stage, datetime.now().isoformat(timespec="minutes"), cid))
                    log_activity("Candidate advanced", f"{person['name']} moved to {stage}")
                    if stage in ("Interview", "Selected", "Offer", "Accepted"):
                        task_title = {"Interview":"Schedule interview", "Selected":"Complete salary discussion", "Offer":"Confirm offer acceptance", "Accepted":"Start document collection"}[stage]
                        task_stage = {"Interview":"candidates", "Selected":"offers", "Offer":"offers", "Accepted":"preboarding"}[stage]
                        execute("INSERT INTO tasks(title,stage,subject,owner,due_date,priority,status) VALUES(?,?,?,?,?,?,?)", (task_title, task_stage, person["name"], person["owner"], str(date.today()+timedelta(days=2)), "High", "Open"))
                    st.success(f"{person['name']} moved to {stage}.")
                    st.rerun()
    with tab2:
        roles = [r["role"] for r in query("SELECT role FROM requisitions WHERE status!='Closed'")]
        with st.form("new_candidate", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Candidate name")
            role = c2.selectbox("Role", roles or ["General application"])
            source = c1.selectbox("Source", ["Careers page", "LinkedIn", "Naukri", "Referral", "Agency", "Campus"])
            owner = c2.text_input("Recruiter", value="Maya")
            score = st.slider("Initial profile score", 0, 100, 70)
            if st.form_submit_button("Add to pipeline", type="primary"):
                if not name.strip(): st.error("Candidate name is required.")
                else:
                    execute("INSERT INTO candidates(name,role,source,stage,score,owner,updated_at) VALUES(?,?,?,?,?,?,?)", (name.strip(), role, source, "Applied", score, owner.strip(), datetime.now().isoformat(timespec="minutes")))
                    log_activity("Candidate added", f"{name} · {role}")
                    st.success("Candidate added to the recruitment pipeline.")


def people_page() -> None:
    page_header("People directory", "Employee lifecycle", "A unified employee record from joining through development and ongoing engagement.")
    rows = query("SELECT * FROM employees ORDER BY id DESC")
    cols = st.columns(4)
    with cols[0]: metric("Total people", len(rows), "Current directory")
    with cols[1]: metric("Onboarding", sum(r["status"] == "Onboarding" for r in rows), "Access and induction")
    with cols[2]: metric("On probation", sum(r["status"] == "Probation" for r in rows), "Review milestones")
    with cols[3]: metric("Active", sum(r["status"] == "Active" for r in rows), "Fully onboarded")
    tab1, tab2 = st.tabs(["Employee directory", "Add employee"])
    with tab1:
        dataframe(rows, {"id":"Employee ID", "name":"Employee", "department":"Department", "designation":"Designation", "join_date":"Joined", "status":"Status", "manager":"Manager"})
    with tab2:
        with st.form("new_employee", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Employee name")
            department = c2.selectbox("Department", ["Analytics", "Customer Success", "Engineering", "Finance", "HR", "Marketing", "Operations", "Product", "Sales"])
            designation = c1.text_input("Designation")
            manager = c2.text_input("Manager")
            joining = c1.date_input("Joining date", date.today())
            status = c2.selectbox("Status", ["Onboarding", "Probation", "Active", "Notice period"])
            if st.form_submit_button("Create employee record", type="primary"):
                if not all([name.strip(), designation.strip(), manager.strip()]): st.error("Please complete all employee details.")
                else:
                    execute("INSERT INTO employees(name,department,designation,join_date,status,manager) VALUES(?,?,?,?,?,?)", (name.strip(), department, designation.strip(), str(joining), status, manager.strip()))
                    log_activity("Employee record created", f"{name} · {designation}")
                    st.success("Employee record created.")


def operations_page() -> None:
    page_header("Shared work queue", "HR operations", "Coordinate ownership and completion across every stage of the employee journey.")
    rows = query("SELECT * FROM tasks ORDER BY CASE status WHEN 'Open' THEN 0 ELSE 1 END, due_date")
    stages = [s for _, _, _, s in WORKFLOW]
    c1, c2, c3 = st.columns(3)
    with c1: metric("Open actions", sum(r["status"] == "Open" for r in rows), "Across all workflows")
    with c2: metric("Overdue", sum(r["status"] == "Open" and date.fromisoformat(r["due_date"]) < date.today() for r in rows), "Needs escalation")
    with c3: metric("Completed", sum(r["status"] == "Done" for r in rows), "Closed actions")
    tab1, tab2, tab3 = st.tabs(["Work queue", "Add action", "Workflow playbooks"])
    with tab1:
        status_filter = st.segmented_control("Show", ["Open", "Done", "All"], default="Open")
        shown = rows if status_filter == "All" else [r for r in rows if r["status"] == status_filter]
        dataframe(shown, {"id":"ID", "title":"Action", "stage":"Workflow", "subject":"Employee / candidate", "owner":"Owner", "due_date":"Due", "priority":"Priority", "status":"Status"})
        open_rows = [r for r in rows if r["status"] == "Open"]
        if open_rows:
            c1, c2 = st.columns([1.7, .5])
            selected = c1.selectbox("Complete an action", [f"TASK-{r['id']:03d} · {r['title']} · {r['subject']}" for r in open_rows])
            if c2.button("Mark complete", type="primary", width="stretch"):
                tid = int(selected.split("·")[0].replace("TASK-", "").strip())
                task = next(r for r in open_rows if r["id"] == tid)
                execute("UPDATE tasks SET status='Done' WHERE id=?", (tid,))
                log_activity("Action completed", f"{task['title']} · {task['subject']}")
                st.success("Action completed.")
                st.rerun()
    with tab2:
        with st.form("new_task", clear_on_submit=True):
            c1, c2 = st.columns(2)
            title = c1.text_input("Action")
            stage = c2.selectbox("Workflow", stages, format_func=lambda s: STAGE_META[s][0])
            subject = c1.text_input("Employee or candidate")
            owner = c2.text_input("Owner")
            due = c1.date_input("Due date", date.today() + timedelta(days=2))
            priority = c2.selectbox("Priority", ["Medium", "High", "Urgent", "Low"])
            if st.form_submit_button("Add action", type="primary"):
                if not all([title.strip(), subject.strip(), owner.strip()]): st.error("Please complete the action, subject and owner.")
                else:
                    execute("INSERT INTO tasks(title,stage,subject,owner,due_date,priority,status) VALUES(?,?,?,?,?,?,?)", (title.strip(), stage, subject.strip(), owner.strip(), str(due), priority, "Open"))
                    st.success("Action added to the queue.")
    with tab3:
        selected_stage = st.selectbox("Select a workflow", stages, format_func=lambda s: STAGE_META[s][0])
        st.markdown(f"### {STAGE_META[selected_stage][0]} checklist")
        for index, task in enumerate(TASK_TEMPLATES[selected_stage], 1):
            st.markdown(f"**{index:02d}** &nbsp; {task}", unsafe_allow_html=True)
            st.markdown("---")


def copilot_answer(prompt: str) -> str:
    p = prompt.lower()
    open_tasks = query("SELECT * FROM tasks WHERE status='Open' ORDER BY due_date")
    candidates = query("SELECT * FROM candidates")
    reqs = query("SELECT * FROM requisitions")
    employees = query("SELECT * FROM employees")
    if any(w in p for w in ["overdue", "late", "urgent", "attention"]):
        items = [t for t in open_tasks if date.fromisoformat(t["due_date"]) < date.today() or t["priority"] == "Urgent"]
        if not items: return "Nothing is overdue or marked urgent right now. The queue is in good shape."
        lines = [f"• <strong>{t['title']}</strong> for {t['subject']} — owned by {t['owner']}, due {t['due_date']}" for t in items]
        return f"I found <strong>{len(items)} item(s) needing attention</strong>:<br>" + "<br>".join(lines)
    if any(w in p for w in ["candidate", "recruit", "interview", "offer"]):
        by_stage = {s: sum(c["stage"] == s for c in candidates) for s in ["Applied", "Screening", "Interview", "Selected", "Offer", "Accepted"]}
        top = sorted(candidates, key=lambda c: c["score"], reverse=True)[:3]
        names = ", ".join(f"{c['name']} ({c['score']})" for c in top)
        return f"The pipeline has <strong>{len(candidates)} candidates</strong>: " + ", ".join(f"{v} {k.lower()}" for k, v in by_stage.items() if v) + f". Highest profile scores: <strong>{names}</strong>."
    if any(w in p for w in ["headcount", "manpower", "requisition", "opening", "hiring"]):
        openings = sum(r["openings"] for r in reqs if r["status"] != "Closed")
        pending = [r for r in reqs if r["status"] == "Pending approval"]
        return f"There are <strong>{openings} planned openings across {len(reqs)} requisitions</strong>. <strong>{len(pending)}</strong> request(s) await approval. The most time-sensitive role is <strong>{min(reqs, key=lambda r: r['target_date'])['role']}</strong>."
    if any(w in p for w in ["employee", "onboard", "probation", "people"]):
        onboarding = [e for e in employees if e["status"] == "Onboarding"]
        probation = [e for e in employees if e["status"] == "Probation"]
        return f"The directory has <strong>{len(employees)} employees</strong>. <strong>{len(onboarding)}</strong> are onboarding and <strong>{len(probation)}</strong> are on probation. " + (f"Current joiner: <strong>{onboarding[0]['name']}</strong> in {onboarding[0]['department']}." if onboarding else "No one is currently onboarding.")
    if any(w in p for w in ["today", "focus", "priority", "do"]):
        top = open_tasks[:4]
        return "Here is the recommended focus list:<br>" + "<br>".join(f"{i}. <strong>{t['title']}</strong> — {t['subject']} ({t['owner']})" for i, t in enumerate(top, 1))
    return "I can help with live summaries of <strong>hiring demand, candidates, offers, onboarding, employees, and overdue actions</strong>. Try asking “What needs attention?” or “Summarise the recruitment pipeline.”"


def copilot_page() -> None:
    page_header("HR intelligence", "PeopleFlow Copilot", "Ask operational questions and get answers grounded in your current HR records.")
    st.markdown('<div class="copilot"><div class="copilot-title">✦ What would you like to know?</div><div style="color:#68708a;margin-top:5px">Your copilot reads the live workflow data in this app.</div></div>', unsafe_allow_html=True)
    suggestions = st.columns(4)
    prompts = ["What needs attention?", "Summarise recruitment", "Show hiring demand", "Who is onboarding?"]
    for col, text in zip(suggestions, prompts):
        with col:
            if st.button(text, width="stretch"): st.session_state.copilot_prompt = text
    prompt = st.text_input("Ask PeopleFlow", value=st.session_state.get("copilot_prompt", ""), placeholder="e.g. Which HR actions are overdue?")
    if prompt:
        answer = copilot_answer(prompt)
        st.markdown(f'<div class="copilot-answer"><strong>PeopleFlow Copilot</strong><br><br>{answer}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Suggested daily brief</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel">{copilot_answer("What should we focus on today?")}</div>', unsafe_allow_html=True)


def sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="brand-lockup"><div class="brand-mark">P</div><div class="brand">PeopleFlow<span class="brand-dot">.</span></div><div class="brand-sub">People operations suite</div></div>', unsafe_allow_html=True)
        page = st.radio("Navigation", ["Overview", "Manpower", "Recruitment", "Employees", "HR Operations", "Copilot"], label_visibility="collapsed")
        st.markdown("---")
        open_count = query("SELECT COUNT(*) AS c FROM tasks WHERE status='Open'")[0]["c"]
        st.markdown(f"<div style='font-size:9px;letter-spacing:.16em;color:#7f948d'>TODAY'S QUEUE</div><div style='font:400 35px Instrument Serif;color:#e5c98f;margin:7px 0 2px'>{open_count}</div><div style='font-size:11px;color:#91a39d'>open HR actions</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.caption("PeopleFlow  ·  Local workspace")
    return page


init_db()
apply_styles()
page = sidebar()

if page == "Overview": dashboard()
elif page == "Manpower": requisitions_page()
elif page == "Recruitment": recruitment_page()
elif page == "Employees": people_page()
elif page == "HR Operations": operations_page()
elif page == "Copilot": copilot_page()
