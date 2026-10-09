import streamlit as st
import pandas as pd
import sqlite3
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "poshansetu_demo.db"

st.set_page_config(
    page_title="PoshanSetu | Follow-through Network",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Theme and language --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --green:#17694a; --green2:#23845d; --orange:#f28a43; --ink:#172b24; --muted:#64756d; --line:#e0e9e3; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding-top: 1.1rem; padding-bottom: 2.4rem; max-width: 1450px; }
[data-testid="stSidebar"] { background: #f3f8f4; border-right: 1px solid #e0e9e3; }
.hero { background: linear-gradient(115deg,#e6f4e9 0%,#f5fbf6 55%,#fff2e8 100%);
        border:1px solid #d9e9dc; border-radius:22px; padding:1.35rem 1.6rem; margin-bottom:1rem; }
.hero h1 { color:#145b40; font-family:'Manrope',sans-serif; font-size:2.4rem; font-weight:800; margin:0; letter-spacing:-1.2px; }
.hero p { color:#3e5c4d; margin:.35rem 0 0 0; font-size:1.02rem; }
.eyebrow { color:#d36e2d; font-weight:800; font-size:.72rem; letter-spacing:1.5px; text-transform:uppercase; }
.section-title { font-family:'Manrope',sans-serif; font-size:1.25rem; font-weight:800; color:#173c2c; margin:.2rem 0 .7rem; }
.kicker { color:#64756d; font-size:.88rem; }
.pill { display:inline-block; border-radius:999px; padding:4px 10px; font-size:.78rem; font-weight:700; background:#edf5ef; color:#17694a; border:1px solid #d5e8d9; }
.case-card { background:white; border:1px solid #e1e9e3; border-radius:15px; padding:14px 16px; margin-bottom:9px; }
div[data-testid="stMetric"] { background:white; border:1px solid #e0e9e3; border-radius:15px; padding:12px 14px; }
div[data-testid="stMetricLabel"] { color:#64756d; }
.stButton button, .stDownloadButton button { border-radius:10px; font-weight:700; }
div[data-testid="stDataFrame"] { border:1px solid #e0e9e3; border-radius:12px; overflow:hidden; }
hr { border-color:#e0e9e3; }
@media (max-width: 700px) {
 .hero { padding:1rem; border-radius:16px; }
 .hero h1 { font-size:1.8rem; }
 .block-container { padding-left: .8rem; padding-right: .8rem; }
}
</style>
""", unsafe_allow_html=True)

LANG = "मराठी" if "मराठी" in st.session_state.get("language", "English") else "English"
TRANSLATIONS = {
    "English": {
        "dashboard":"Dashboard", "register":"Follow-up register", "new":"New follow-up",
        "journey":"Referral journey", "supervisor":"Supervisor desk", "reports":"Impact & reports",
        "guide":"Pilot & safety", "total":"Total cases", "open":"Open cases", "due":"Due today",
        "overdue":"Overdue", "create":"Create follow-up", "save":"Save follow-up",
        "caseid":"Case ID", "code":"Fictional beneficiary code", "group":"Beneficiary group",
        "category":"Follow-up category", "action":"Next action", "worker":"Assigned worker",
        "due_date":"Due date", "priority":"Priority", "language":"Preferred language",
        "status":"Status", "outcome":"Referral outcome", "barrier":"Access barrier",
        "notes":"Operational note (no medical details)", "search":"Search case / worker / action",
        "all":"All", "complete":"Completed", "sync":"Sync queued changes", "offline":"Simulate offline mode",
        "offline_help":"Offline simulation: changes are queued locally in this session until you sync.",
        "queued":"Queued changes", "online":"Online / synced", "hero":"Bridging the gap to a healthier generation.",
        "subtitle":"A follow-through workspace for nutrition-related services — identify the next step, assign an owner, and track resolution.",
        "safety":"Demonstration only · synthetic records · not a diagnostic or treatment tool",
    },
    "मराठी": {
        "dashboard":"डॅशबोर्ड", "register":"फॉलो-अप नोंदवही", "new":"नवीन फॉलो-अप",
        "journey":"रेफरल प्रवास", "supervisor":"पर्यवेक्षक कक्ष", "reports":"परिणाम व अहवाल",
        "guide":"पायलट व सुरक्षितता", "total":"एकूण प्रकरणे", "open":"प्रलंबित प्रकरणे",
        "due":"आज देय", "overdue":"मुदत संपलेली", "create":"फॉलो-अप तयार करा",
        "save":"फॉलो-अप जतन करा", "caseid":"प्रकरण क्रमांक", "code":"काल्पनिक लाभार्थी कोड",
        "group":"लाभार्थी गट", "category":"फॉलो-अप प्रकार", "action":"पुढील कृती",
        "worker":"जबाबदार कार्यकर्ता", "due_date":"देय तारीख", "priority":"प्राधान्य",
        "language":"पसंतीची भाषा", "status":"स्थिती", "outcome":"रेफरलचा परिणाम",
        "barrier":"सेवा मिळविण्यातील अडथळा", "notes":"कामकाजाची नोंद (वैद्यकीय तपशील नको)",
        "search":"प्रकरण / कार्यकर्ता / कृती शोधा", "all":"सर्व", "complete":"पूर्ण",
        "sync":"प्रलंबित बदल समक्रमित करा", "offline":"ऑफलाइन मोडचे अनुकरण",
        "offline_help":"ऑफलाइन अनुकरण: समक्रमित करेपर्यंत बदल या सत्रात स्थानिकरित्या रांगेत राहतील.",
        "queued":"रांगेतील बदल", "online":"ऑनलाइन / समक्रमित",
        "hero":"निरोगी पिढीसाठी जोडणारा पूल.",
        "subtitle":"पोषण सेवांसाठी फॉलो-अप कार्यक्षेत्र — पुढील कृती ठरवा, जबाबदार व्यक्ती नेमा आणि पूर्तता नोंदवा.",
        "safety":"फक्त प्रात्यक्षिक · काल्पनिक नोंदी · निदान किंवा उपचार साधन नाही",
    }
}
T = TRANSLATIONS[LANG]

# -------------------- Data layer --------------------
STATUSES = ["Open", "Scheduled", "In progress", "Completed", "Escalated"]
PRIORITIES = ["Routine", "Priority", "Urgent"]
GROUPS = ["Pregnant woman", "Lactating woman", "Child caregiver", "Other"]
CATEGORIES = [
    "Maternal nutrition follow-up", "Anaemia-related referral",
    "Child growth monitoring", "Nutrition counselling", "Postpartum follow-up", "Other"
]
OUTCOMES = ["Awaiting confirmation", "Visit planned", "Completed", "Missed", "Rescheduled", "Unresolved", "Not applicable"]
BARRIERS = ["None reported", "Transport difficulty", "Could not attend during service hours",
            "Service unavailable", "Could not contact family", "Language/accessibility", "Other"]

def connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY, beneficiary_code TEXT NOT NULL, beneficiary_type TEXT NOT NULL,
            category TEXT NOT NULL, next_action TEXT NOT NULL, assigned_worker TEXT NOT NULL,
            due_date TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL, language TEXT NOT NULL,
            referral_outcome TEXT NOT NULL, barrier TEXT NOT NULL, notes TEXT NOT NULL,
            created_date TEXT NOT NULL, updated_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT, event_time TEXT NOT NULL, case_id TEXT NOT NULL,
            action TEXT NOT NULL, actor TEXT NOT NULL)""")
        count = con.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        if count == 0:
            today = date.today()
            sample = [
                ("PS-1001","DEMO-M-001","Pregnant woman","Anaemia-related referral",
                 "Confirm attendance for recommended clinical assessment","Worker A",today-timedelta(days=1),
                 "Urgent","Open","Marathi","Awaiting confirmation","Transport difficulty",
                 "Synthetic demo record",today-timedelta(days=5)),
                ("PS-1002","DEMO-C-002","Child caregiver","Child growth monitoring",
                 "Follow up on scheduled growth-monitoring visit","Worker B",today,
                 "Priority","Scheduled","Marathi","Not applicable","None reported",
                 "Synthetic demo record",today-timedelta(days=2)),
                ("PS-1003","DEMO-M-003","Lactating woman","Postpartum follow-up",
                 "Confirm completion of recommended postpartum visit","Worker A",today+timedelta(days=2),
                 "Routine","In progress","Hindi","Visit planned","None reported",
                 "Synthetic demo record",today-timedelta(days=1)),
                ("PS-1004","DEMO-C-004","Child caregiver","Nutrition counselling",
                 "Offer approved age-appropriate nutrition counselling","Worker C",today-timedelta(days=3),
                 "Priority","Escalated","Marathi","Unresolved","Could not attend during service hours",
                 "Synthetic demo record",today-timedelta(days=7)),
                ("PS-1005","DEMO-M-005","Pregnant woman","Maternal nutrition follow-up",
                 "Check whether planned nutrition counselling was received","Worker B",today-timedelta(days=1),
                 "Routine","Completed","English","Completed","None reported",
                 "Synthetic demo record",today-timedelta(days=4)),
            ]
            for row in sample:
                con.execute("""INSERT INTO cases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (*[str(x) if isinstance(x, date) else x for x in row], datetime.now().isoformat(timespec="seconds")))
            con.execute("INSERT INTO activity(event_time,case_id,action,actor) VALUES (?,?,?,?)",
                        (datetime.now().isoformat(timespec="seconds"), "PS-1005", "Demo seed case marked completed", "Demo seed"))
        con.commit()

def get_cases():
    with connect() as con:
        df = pd.read_sql_query("SELECT * FROM cases ORDER BY due_date ASC", con)
    if not df.empty:
        for col in ["due_date", "created_date"]:
            df[col] = pd.to_datetime(df[col]).dt.date
    return df

def get_activity(limit=100):
    with connect() as con:
        return pd.read_sql_query("SELECT event_time, case_id, action, actor FROM activity ORDER BY id DESC LIMIT ?", con, params=(limit,))

def log_event(case_id, action, actor="Demo user"):
    with connect() as con:
        con.execute("INSERT INTO activity(event_time,case_id,action,actor) VALUES (?,?,?,?)",
                    (datetime.now().isoformat(timespec="seconds"), case_id, action, actor))
        con.commit()

def save_case(row):
    with connect() as con:
        con.execute("""INSERT INTO cases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(case_id) DO UPDATE SET
        beneficiary_code=excluded.beneficiary_code, beneficiary_type=excluded.beneficiary_type,
        category=excluded.category, next_action=excluded.next_action, assigned_worker=excluded.assigned_worker,
        due_date=excluded.due_date, priority=excluded.priority, status=excluded.status,
        language=excluded.language, referral_outcome=excluded.referral_outcome, barrier=excluded.barrier,
        notes=excluded.notes, updated_at=excluded.updated_at""",
        (row["case_id"], row["beneficiary_code"], row["beneficiary_type"], row["category"],
         row["next_action"], row["assigned_worker"], str(row["due_date"]), row["priority"],
         row["status"], row["language"], row["referral_outcome"], row["barrier"],
         row["notes"], str(row["created_date"]), datetime.now().isoformat(timespec="seconds")))
        con.commit()

def overdue(row):
    return row["status"] != "Completed" and row["due_date"] < date.today()

def record_change(case_id, description):
    if st.session_state.get("offline_mode", False):
        st.session_state.setdefault("offline_queue", []).append({
            "case_id": case_id, "description": description, "timestamp": datetime.now().isoformat(timespec="seconds")
        })
        return False
    log_event(case_id, description)
    return True

init_db()
if "offline_queue" not in st.session_state:
    st.session_state.offline_queue = []
if "language" not in st.session_state:
    st.session_state.language = "English"
if "offline_mode" not in st.session_state:
    st.session_state.offline_mode = False

# -------------------- Navigation --------------------
with st.sidebar:
    st.markdown("## 🌱 PoshanSetu")
    st.caption("Nutrition Follow-through Network")
    lang_choice = st.radio("भाषा / Language", ["English", "मराठी"],
                            index=0 if st.session_state.language == "English" else 1, horizontal=True)
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        st.rerun()
    page_options = [T["dashboard"], T["register"], T["new"], T["journey"], T["supervisor"], T["reports"], T["guide"]]
    page = st.radio("Workspace", page_options, label_visibility="collapsed")
    st.divider()
    st.session_state.offline_mode = st.toggle(T["offline"], value=st.session_state.offline_mode)
    st.caption(T["offline_help"])
    q_count = len(st.session_state.offline_queue)
    if q_count:
        st.warning(f"{T['queued']}: {q_count}")
        if st.button(T["sync"], use_container_width=True, type="primary"):
            for item in st.session_state.offline_queue:
                log_event(item["case_id"], "SYNCED: " + item["description"])
            st.session_state.offline_queue = []
            st.session_state.offline_mode = False
            st.success("Changes synced to local demo database.")
            st.rerun()
    else:
        st.success(T["online"] if not st.session_state.offline_mode else "Offline simulation active")

st.markdown(f"""
<div class="hero">
 <div class="eyebrow">Seva First Innovation Challenge 2026 · Maharashtra Zone</div>
 <h1>🌱 PoshanSetu</h1>
 <p><b>{T['hero']}</b></p>
 <p>{T['subtitle']}</p>
</div>
""", unsafe_allow_html=True)
st.caption(T["safety"])

df = get_cases()
open_df = df[df.status != "Completed"]
overdue_df = open_df[open_df.apply(overdue, axis=1)]
today_df = open_df[open_df.due_date == date.today()]
completed_df = df[df.status == "Completed"]

# -------------------- Dashboard --------------------
if page == T["dashboard"]:
    st.markdown(f'<div class="section-title">{T["dashboard"]}</div>', unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric(T["total"], len(df))
    m2.metric(T["open"], len(open_df))
    m3.metric(T["due"], len(today_df))
    m4.metric(T["overdue"], len(overdue_df), delta="Needs attention" if len(overdue_df) else "On track", delta_color="inverse")
    st.write("")
    left, right = st.columns([1.25, .9], gap="large")
    with left:
        st.markdown('<div class="section-title">🔔 Priority follow-ups</div>', unsafe_allow_html=True)
        priority_rank = {"Urgent":0, "Priority":1, "Routine":2}
        priority_df = open_df.copy()
        priority_df["is_overdue"] = priority_df.apply(overdue, axis=1)
        priority_df["rank"] = priority_df["priority"].map(priority_rank)
        priority_df = priority_df.sort_values(["is_overdue","rank","due_date"], ascending=[False,True,True])
        if priority_df.empty:
            st.success("No open cases.")
        for _, r in priority_df.head(5).iterrows():
            tag = "🔴 OVERDUE" if overdue(r) else ("🟠 DUE TODAY" if r.due_date == date.today() else "📌 UPCOMING")
            with st.container(border=True):
                x,y = st.columns([4,1])
                x.markdown(f"**{r.case_id} · {r.category}**")
                y.markdown(f"**{r.priority}**")
                st.write(r.next_action)
                st.caption(f"{tag} · Due {r.due_date.strftime('%d %b %Y')} · {r.assigned_worker}")
                st.progress(1.0 if r.status == "Escalated" else (0.65 if overdue(r) else 0.3),
                            text=f"Workflow status: {r.status}")
    with right:
        st.markdown('<div class="section-title">📊 Workflow snapshot</div>', unsafe_allow_html=True)
        status_counts = df.status.value_counts().reindex(STATUSES, fill_value=0)
        st.bar_chart(status_counts)
        closure = round(len(completed_df)/len(df)*100) if len(df) else 0
        st.metric("Demo case closure rate", f"{closure}%")
        st.caption("This is calculated from synthetic demo records, not real programme performance.")
        st.markdown('<div class="section-title">🧭 The PoshanSetu promise</div>', unsafe_allow_html=True)
        st.write("Every identified need should have a next action, a responsible owner, a due date, and a documented outcome.")
        st.info("PoshanSetu coordinates follow-up; it does not diagnose or prescribe treatment.")

# -------------------- Register --------------------
elif page == T["register"]:
    st.markdown(f'<div class="section-title">{T["register"]}</div>', unsafe_allow_html=True)
    a,b,c = st.columns([1,1,1.4])
    with a: status_filter = st.multiselect(T["status"], STATUSES, default=STATUSES)
    with b: cat_filter = st.multiselect(T["category"], CATEGORIES, default=CATEGORIES)
    with c: query = st.text_input(T["search"])
    view = df[df.status.isin(status_filter) & df.category.isin(cat_filter)].copy()
    if query:
        mask = view.apply(lambda r: query.lower() in " ".join(str(r[x]) for x in
            ["case_id","beneficiary_code","assigned_worker","next_action","category"]).lower(), axis=1)
        view = view[mask]
    view["Overdue"] = view.apply(lambda r: "Yes" if overdue(r) else "No", axis=1)
    st.dataframe(view[["case_id","beneficiary_code","beneficiary_type","category","next_action","assigned_worker",
                       "due_date","priority","status","Overdue","referral_outcome","barrier"]],
                 use_container_width=True, hide_index=True)
    st.markdown("#### Update a follow-up")
    if not df.empty:
        selected = st.selectbox("Choose case", df.case_id.tolist())
        row = df[df.case_id == selected].iloc[0]
        with st.form("edit_case"):
            l,r = st.columns(2)
            with l:
                new_status = st.selectbox(T["status"], STATUSES, index=STATUSES.index(row.status))
                new_worker = st.text_input(T["worker"], value=row.assigned_worker)
                new_due = st.date_input(T["due_date"], value=row.due_date)
                new_priority = st.selectbox(T["priority"], PRIORITIES, index=PRIORITIES.index(row.priority))
            with r:
                new_outcome = st.selectbox(T["outcome"], OUTCOMES, index=OUTCOMES.index(row.referral_outcome))
                new_barrier = st.selectbox(T["barrier"], BARRIERS,
                    index=BARRIERS.index(row.barrier) if row.barrier in BARRIERS else len(BARRIERS)-1)
                new_action = st.text_area(T["action"], value=row.next_action)
                new_notes = st.text_input(T["notes"], value=row.notes)
            submit = st.form_submit_button("Save update", type="primary")
        if submit:
            if not new_worker.strip() or not new_action.strip():
                st.error("Assigned worker and next action are required.")
            else:
                updated = row.to_dict()
                updated.update({"status":new_status,"assigned_worker":new_worker.strip(),"due_date":new_due,
                    "priority":new_priority,"referral_outcome":new_outcome,"barrier":new_barrier,
                    "next_action":new_action.strip(),"notes":new_notes.strip()})
                save_case(updated)
                synced = record_change(selected, f"Updated case: status={new_status}; outcome={new_outcome}; barrier={new_barrier}")
                st.success("Case saved. " + ("Activity logged." if synced else "Update is queued for sync in offline simulation."))
                st.rerun()

# -------------------- Create --------------------
elif page == T["new"]:
    st.markdown(f'<div class="section-title">{T["create"]}</div>', unsafe_allow_html=True)
    st.write("Create a fictional follow-up. The record must represent an action, not a diagnosis.")
    with st.form("new_case", clear_on_submit=True):
        c1,c2 = st.columns(2)
        with c1:
            code = st.text_input(T["code"], placeholder="DEMO-M-006")
            group = st.selectbox(T["group"], GROUPS)
            category = st.selectbox(T["category"], CATEGORIES)
            language = st.selectbox(T["language"], ["Marathi","Hindi","English"])
        with c2:
            action = st.text_area(T["action"], placeholder="e.g. Confirm attendance for recommended appointment")
            worker = st.text_input(T["worker"], placeholder="Worker A")
            due = st.date_input(T["due_date"], value=date.today()+timedelta(days=2))
            priority = st.selectbox(T["priority"], PRIORITIES)
        notes = st.text_input(T["notes"], value="Created in demo")
        confirm = st.checkbox("I confirm this is fictional data and contains no real personal or health information.")
        submit = st.form_submit_button(T["save"], type="primary")
    if submit:
        if not code.strip() or not action.strip() or not worker.strip():
            st.error("Please fill in the fictional code, next action, and assigned worker.")
        elif not confirm:
            st.error("Please confirm the record is fictional.")
        else:
            existing = df.beneficiary_code.astype(str).str.upper().tolist()
            if code.strip().upper() in existing:
                st.error("That demo code already exists. Use a unique fictional code.")
            else:
                nums = [int(x.split("-")[1]) for x in df.case_id if x.startswith("PS-") and x.split("-")[1].isdigit()]
                new_id = f"PS-{max(nums+[1000])+1}"
                new_row = {"case_id":new_id,"beneficiary_code":code.strip().upper(),"beneficiary_type":group,
                    "category":category,"next_action":action.strip(),"assigned_worker":worker.strip(),
                    "due_date":due,"priority":priority,"status":"Open","language":language,
                    "referral_outcome":"Awaiting confirmation","barrier":"None reported",
                    "notes":notes.strip(),"created_date":date.today()}
                save_case(new_row)
                synced = record_change(new_id, "Follow-up case created")
                st.success(f"Created {new_id}. " + ("Saved to local demo database." if synced else "Change queued in offline simulation."))
                st.rerun()

# -------------------- Referral journey --------------------
elif page == T["journey"]:
    st.markdown(f'<div class="section-title">{T["journey"]}</div>', unsafe_allow_html=True)
    st.write("A visual hand-off from identified need to a documented outcome. The steps are operational, not clinical.")
    steps = [
        ("1", "Need recorded", "Authorised worker records a concern or an already recommended referral."),
        ("2", "Next action assigned", "A responsible worker and due date are recorded."),
        ("3", "Visit / service planned", "The beneficiary is informed through an appropriate, consent-based channel."),
        ("4", "Outcome checked", "Attendance or service outcome is confirmed where feasible."),
        ("5", "Resolve or escalate", "Close only when the defined follow-up criteria are met; otherwise assign the next action."),
    ]
    cols = st.columns(5)
    for col, (num,title,desc) in zip(cols, steps):
        with col:
            st.markdown(f"""<div style="border:1px solid #dce8df;border-radius:15px;padding:14px 12px;min-height:205px;background:#fff">
            <div style="width:34px;height:34px;border-radius:50%;background:#17694a;color:white;font-weight:800;display:flex;align-items:center;justify-content:center;margin-bottom:12px">{num}</div>
            <div style="font-weight:800;color:#174b35;margin-bottom:8px">{title}</div>
            <div style="font-size:.86rem;color:#53675b;line-height:1.45">{desc}</div></div>""", unsafe_allow_html=True)
    st.write("")
    st.markdown("#### Select a case to inspect its journey")
    if not df.empty:
        selected = st.selectbox("Case", df.case_id.tolist(), key="journey_case")
        r = df[df.case_id == selected].iloc[0]
        stages = ["Need recorded", "Next action assigned", "Visit / service planned", "Outcome checked", "Resolve or escalate"]
        stage_index = 0
        if r.status in ["Scheduled","In progress"]: stage_index = 2
        if r.referral_outcome in ["Completed","Missed","Rescheduled"]: stage_index = 3
        if r.status == "Completed": stage_index = 4
        if r.status == "Escalated" or r.referral_outcome == "Unresolved": stage_index = 4
        st.markdown(f"**{r.case_id} — {r.category}**")
        st.progress((stage_index+1)/len(stages), text=f"Illustrative workflow stage: {stages[stage_index]}")
        st.write(f"**Next action:** {r.next_action}")
        st.write(f"**Owner:** {r.assigned_worker} · **Due:** {r.due_date} · **Outcome:** {r.referral_outcome}")
        if r.status == "Escalated" or r.referral_outcome == "Unresolved":
            st.error("This case is unresolved/escalated. A responsible person should review the barrier and record a next step.")
        elif r.status == "Completed":
            st.success("The demo case is marked completed. In a real workflow, closure criteria must be defined and verified.")
        else:
            st.info("This case remains in progress until its outcome is documented or it is appropriately escalated.")

# -------------------- Supervisor desk --------------------
elif page == T["supervisor"]:
    st.markdown(f'<div class="section-title">{T["supervisor"]}</div>', unsafe_allow_html=True)
    st.write("A supervisor's operational queue for cases that need attention.")
    escalated = df[(df.status == "Escalated") | (df.referral_outcome == "Unresolved")]
    overdue = df[df.apply(overdue, axis=1)]
    c1,c2,c3 = st.columns(3)
    c1.metric("Escalated / unresolved", len(escalated))
    c2.metric("Overdue open cases", len(overdue))
    c3.metric("Workers represented", df.assigned_worker.nunique())
    todo = pd.concat([escalated, overdue]).drop_duplicates(subset=["case_id"])
    if todo.empty:
        st.success("No cases currently require supervisor attention in this demo.")
    else:
        st.markdown("#### Review queue")
        for _, r in todo.iterrows():
            with st.container(border=True):
                a,b = st.columns([3,1])
                a.markdown(f"**{r.case_id} · {r.category}**")
                b.markdown(f"**{r.priority}**")
                st.write(r.next_action)
                st.caption(f"Owner: {r.assigned_worker} · Due: {r.due_date} · Status: {r.status} · Barrier: {r.barrier}")
                with st.expander(f"Supervisor action for {r.case_id}"):
                    action_options = ["Reassign owner", "Set new due date", "Record barrier reviewed", "Escalate to programme lead"]
                    choice = st.selectbox("Action", action_options, key=f"sup_action_{r.case_id}")
                    with st.form(f"sup_form_{r.case_id}"):
                        if choice == "Reassign owner":
                            new_owner = st.text_input("New owner", value=r.assigned_worker, key=f"owner_{r.case_id}")
                            new_date = r.due_date
                        elif choice == "Set new due date":
                            new_owner = r.assigned_worker
                            new_date = st.date_input("New due date", value=max(r.due_date, date.today()), key=f"date_{r.case_id}")
                        else:
                            new_owner = r.assigned_worker
                            new_date = r.due_date
                        supervisor_note = st.text_input("Supervisor note (operational only)", key=f"note_{r.case_id}")
                        go = st.form_submit_button("Apply supervisor action")
                    if go:
                        updated = r.to_dict()
                        updated["assigned_worker"] = new_owner.strip() or r.assigned_worker
                        updated["due_date"] = new_date
                        if choice == "Escalate to programme lead":
                            updated["status"] = "Escalated"
                        elif choice == "Record barrier reviewed" and updated["status"] == "Escalated":
                            updated["status"] = "In progress"
                        save_case(updated)
                        synced = record_change(r.case_id, f"Supervisor action: {choice}; note={supervisor_note or '—'}")
                        st.success("Supervisor action saved." + (" Activity logged." if synced else " Activity queued for sync."))
                        st.rerun()
    st.markdown("#### Recent activity")
    activity = get_activity(15)
    if not activity.empty:
        st.dataframe(activity, use_container_width=True, hide_index=True)

# -------------------- Reports --------------------
elif page == T["reports"]:
    st.markdown(f'<div class="section-title">{T["reports"]}</div>', unsafe_allow_html=True)
    st.caption("Metrics here are computed from synthetic records. Do not present them as pilot outcomes.")
    n = len(df)
    closure = len(completed_df)/n*100 if n else 0
    visible = len(df[df.referral_outcome.isin(["Completed","Missed","Rescheduled","Unresolved","Visit planned"])])
    visibility = visible/n*100 if n else 0
    m1,m2,m3 = st.columns(3)
    m1.metric("Completed demo cases", len(completed_df))
    m2.metric("Demo closure rate", f"{closure:.0f}%")
    m3.metric("Outcome recorded", f"{visibility:.0f}%")
    st.markdown("#### Recommended pilot scorecard")
    scorecard = pd.DataFrame([
        ["On-time follow-up completion","Due actions completed by the agreed due date ÷ all actions due","Set baseline before pilot"],
        ["Overdue action coverage","Overdue cases reviewed with a documented next step ÷ all overdue cases","Proposed planning target: 90%"],
        ["Referral outcome visibility","Referrals with a documented outcome ÷ all referrals recorded","Proposed planning target: 90%"],
        ["Worker usability","Average response on a short usability questionnaire","Proposed planning target: 4/5"],
        ["Administrative burden","Extra minutes required per worker per day","Measure; redesign if burden rises"],
        ["Access equity","Follow-up completion by language and relevant service-access barriers","Review privacy-safe aggregates only"],
    ], columns=["Indicator","Calculation","Planning note"])
    st.dataframe(scorecard, use_container_width=True, hide_index=True)
    out = df.copy()
    for col in ["due_date","created_date"]:
        out[col] = out[col].astype(str)
    st.download_button("⬇ Download case register CSV", out.to_csv(index=False).encode("utf-8"),
                       "poshansetu_demo_cases.csv", "text/csv")
    st.markdown("#### Activity log")
    act = get_activity(100)
    st.dataframe(act, use_container_width=True, hide_index=True)

# -------------------- Pilot and safety --------------------
elif page == T["guide"]:
    st.markdown(f'<div class="section-title">{T["guide"]}</div>', unsafe_allow_html=True)
    st.markdown("### Proposed 8-week pilot")
    pilot = [
        ("Week 1","Discovery","Map current follow-up and referral workflows with frontline workers; identify duplication risks."),
        ("Weeks 2–3","Build","Configure forms, task queue, status flow, and dashboard using synthetic data."),
        ("Week 4","Usability & safety","Test language, accessibility, consent flow, access controls, and escalation rules."),
        ("Weeks 5–7","Evaluate","Run a simulated workflow test or an approved limited pilot with appropriate supervision."),
        ("Week 8","Learn","Compare with baseline, assess administrative burden, document costs, and decide whether to iterate."),
    ]
    for week,title,desc in pilot:
        with st.container(border=True):
            st.markdown(f"**{week} · {title}**")
            st.write(desc)
    st.markdown("### Before any real-world deployment")
    st.warning("""
- Obtain relevant organisational, programme, ethics, and deployment approvals.
- Use consent and data-minimisation procedures appropriate to the setting.
- Define retention, deletion, access control, audit, backup, and incident response.
- Have all health content and referral rules reviewed by qualified professionals.
- Do not make diagnosis, medication, or treatment decisions through this app.
- Assess compatibility with POSHAN Tracker and existing registers before adding workload.
- Keep access to services independent of smartphone ownership, language, or app use.
""")
    st.markdown("### Prototype limitations")
    st.write("""
This version demonstrates persistent local demo storage using SQLite, referral stages, supervisor actions, English/Marathi labels, and an offline-mode simulation that queues activity-log events until sync. It is not a fully offline mobile app/PWA: case edits are saved to the local demo database even while offline simulation is toggled, while their activity log is queued. The database is stored beside the app and is intended only for local demonstration. There is no production authentication, encryption/key management, multi-user hosting, government integration, SMS, or clinical decision support.
""")
    st.markdown("### Suggested field interview questions")
    for q in [
        "What happens after a woman is identified as needing further anaemia evaluation?",
        "How are missed appointments and pending referrals followed up today?",
        "Which current tools already capture this information?",
        "What would make another app useful rather than duplicate work?",
        "What barriers prevent families from completing recommended next steps?",
    ]:
        st.write("• " + q)

st.divider()
left,right = st.columns([3,1])
left.caption("PoshanSetu · Prototype v0.2 · Local demonstration · Synthetic data only")
right.caption("Not for clinical use")
