"""
Master of Ops — Team Execution OS  v3.0
Auto-Dial Outbound Cockpit | Industrial Premium
"""

import random
import smtplib
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import google.generativeai as genai
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Master of Ops | Execution OS",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

:root {
    --bg:#0B0F14; --surface:#131920; --panel:#1A2330; --border:#263040;
    --teal:#00A7A7; --teal-dim:#007A7A; --amber:#F0A500; --red:#E05252;
    --green:#3DBA72; --purple:#9B72CF; --text:#FFFFFF; --muted:#8899AA;
    --radius:4px;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
h1, h2, h3 {
    font-family: 'Barlow Condensed', sans-serif !important;
    letter-spacing: .05em;
    text-transform: uppercase;
}

.op-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    margin-bottom: .6rem;
}
.op-card-teal { border-left: 3px solid var(--teal); }

.kpi-strip { display: flex; gap: .6rem; margin-bottom: 1.2rem; flex-wrap: wrap; }
.kpi {
    flex: 1; min-width: 90px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-top: 2px solid var(--teal);
    padding: .6rem .9rem;
    border-radius: var(--radius);
    text-align: center;
}
.kpi.amber  { border-top-color: var(--amber); }
.kpi.red    { border-top-color: var(--red); }
.kpi.green  { border-top-color: var(--green); }
.kpi.purple { border-top-color: var(--purple); }
.kpi-val {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.8rem; font-weight: 800;
    color: var(--teal); line-height: 1;
}
.kpi.amber  .kpi-val { color: var(--amber); }
.kpi.red    .kpi-val { color: var(--red); }
.kpi.green  .kpi-val { color: var(--green); }
.kpi.purple .kpi-val { color: var(--purple); }
.kpi-label {
    font-size: .58rem; text-transform: uppercase;
    letter-spacing: .12em; color: var(--muted); margin-top: .15rem;
}
.kpi-sub { font-size: .6rem; color: var(--green); margin-top: .1rem; }

.lead-block {
    background: var(--panel);
    border: 1px solid var(--teal);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    margin-bottom: .75rem;
}
.lead-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.7rem; font-weight: 800; letter-spacing: .05em;
}
.lead-company { font-family: 'DM Mono', monospace; font-size: .88rem; color: var(--teal); }

.badge {
    display: inline-block; padding: .12rem .55rem;
    border-radius: 2px; font-size: .62rem; font-weight: 600;
    letter-spacing: .1em; text-transform: uppercase;
    font-family: 'Barlow Condensed', sans-serif;
}
.badge-cold   { background: #1E3A5F; color: #7AB8F5; }
.badge-warm   { background: #4A2E00; color: var(--amber); }
.badge-hot    { background: #4A1010; color: var(--red); }
.badge-dnc    { background: #2A2A2A; color: var(--muted); }
.ch-call      { background: #0A2A2A; color: var(--teal); }
.ch-email     { background: #2A2A00; color: var(--amber); }
.ch-li        { background: #1A0A2A; color: var(--purple); }

.intel-grid { display: flex; flex-wrap: wrap; gap: .4rem; margin: .5rem 0; }
.intel-chip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: .2rem .55rem;
    font-size: .7rem; color: #CCDDEE;
}
.intel-chip span { color: var(--muted); font-size: .62rem; margin-right: .3rem; }

.step-bar { display: flex; gap: .3rem; margin: .5rem 0; align-items: center; }
.step-dot {
    width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700; font-size: .78rem;
    border: 1px solid var(--border); color: var(--muted); background: var(--surface);
}
.step-dot.active { background: var(--teal); border-color: var(--teal); color: #000; }
.step-dot.done   { background: var(--teal-dim); border-color: var(--teal-dim); color: #000; }
.step-line { flex: 1; height: 1px; background: var(--border); }

.dial-number {
    font-family: 'DM Mono', monospace;
    font-size: 1.6rem; font-weight: 500;
    color: var(--teal); letter-spacing: .08em; margin: .4rem 0;
}

.funnel-step {
    display: flex; align-items: center; gap: .8rem;
    padding: .55rem .9rem; margin: .2rem 0;
    border-radius: var(--radius);
    background: var(--panel); border: 1px solid var(--border);
}
.funnel-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .9rem; font-weight: 700; letter-spacing: .04em; min-width: 160px;
}
.funnel-bar-wrap { flex: 1; height: 7px; background: var(--border); border-radius: 3px; }
.funnel-bar { height: 7px; border-radius: 3px; }
.funnel-pct { font-family: 'DM Mono', monospace; font-size: .72rem; color: var(--muted); min-width: 36px; text-align: right; }
.funnel-n   { font-family: 'DM Mono', monospace; font-size: .88rem; font-weight: 500; min-width: 30px; text-align: right; }

.lb-row { display: flex; align-items: center; gap: .65rem; padding: .5rem .9rem; border-bottom: 1px solid var(--border); }
.lb-row:hover { background: rgba(255,255,255,.02); }
.lb-rank { font-family: 'Barlow Condensed', sans-serif; font-size: 1.3rem; font-weight: 800; color: var(--muted); width: 26px; text-align: center; }
.lb-rank.gold   { color: #FFD700; }
.lb-rank.silver { color: #C0C0C0; }
.lb-rank.bronze { color: #CD7F32; }
.lb-name  { flex: 1; font-weight: 500; font-size: .88rem; }
.lb-bar-wrap { width: 100px; height: 5px; background: var(--border); border-radius: 3px; }
.lb-bar  { height: 5px; background: var(--teal); border-radius: 3px; }
.lb-count { font-family: 'DM Mono', monospace; font-size: .82rem; color: var(--teal); min-width: 28px; text-align: right; }

.feed-row { display: flex; gap: .65rem; padding: .4rem 0; border-bottom: 1px solid var(--border); font-size: .8rem; }

.stTextInput input, .stTextArea textarea {
    background: var(--surface) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important; border-radius: var(--radius) !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
}
.stSelectbox div[data-baseweb="select"] * { color: var(--text) !important; }
.stMultiSelect div[data-baseweb="select"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
}
.stMultiSelect div[data-baseweb="select"] * { color: var(--text) !important; }

.stButton > button {
    background: var(--teal) !important; color: #000 !important; border: none !important;
    font-family: 'Barlow Condensed', sans-serif !important; font-weight: 700 !important;
    font-size: .85rem !important; letter-spacing: .1em !important;
    text-transform: uppercase !important; border-radius: var(--radius) !important;
    padding: .4rem 1rem !important;
}
.stButton > button:hover { background: var(--teal-dim) !important; }
.stLinkButton a {
    background: var(--panel) !important; color: var(--teal) !important;
    border: 1px solid var(--teal) !important;
    font-family: 'Barlow Condensed', sans-serif !important; font-weight: 700 !important;
    font-size: .8rem !important; letter-spacing: .08em !important;
    text-transform: uppercase !important; border-radius: var(--radius) !important;
    padding: .3rem .9rem !important;
}

[data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important; gap: 0 !important;
}
[data-baseweb="tab"] {
    font-family: 'Barlow Condensed', sans-serif !important; font-size: .88rem !important;
    letter-spacing: .07em !important; text-transform: uppercase !important;
    color: var(--muted) !important; background: transparent !important;
    border-radius: 0 !important; padding: .55rem 1.1rem !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: var(--teal) !important; border-bottom: 2px solid var(--teal) !important;
}

[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--teal-dim); border-radius: 2px; }

.logo-mark {
    font-family: 'Barlow Condensed', sans-serif; font-size: 1.4rem; font-weight: 800;
    letter-spacing: .12em; text-transform: uppercase; color: var(--teal);
}
.logo-sub { font-size: .58rem; letter-spacing: .2em; color: var(--muted); text-transform: uppercase; }

.section-label {
    font-family: 'Barlow Condensed', sans-serif; font-size: .68rem;
    letter-spacing: .2em; color: var(--muted); text-transform: uppercase; margin: 1rem 0 .4rem;
}
.setup-card {
    background: linear-gradient(135deg, #0A1A2A, #0B1E1E);
    border: 1px solid var(--teal); border-radius: var(--radius); padding: 1.8rem; margin: 1rem 0;
}
.session-banner {
    background: linear-gradient(90deg, #002A2A, #0A1A2A);
    border: 1px solid var(--teal); border-radius: var(--radius);
    padding: .6rem 1.2rem; display: flex; align-items: center;
    justify-content: space-between; margin-bottom: .8rem;
}
.session-active {
    font-family: 'Barlow Condensed', sans-serif; font-size: .85rem;
    font-weight: 700; letter-spacing: .12em; color: var(--teal);
}
.session-pulse {
    display: inline-block; width: 8px; height: 8px;
    background: var(--green); border-radius: 50%; margin-right: .5rem;
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .3; } }

@media (max-width: 768px) {
    .kpi-strip { flex-wrap: wrap; }
    .kpi { min-width: 42%; }
    .lb-bar-wrap { display: none; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS & CONFIG
# ─────────────────────────────────────────────
SHEET_LEADS = "Leads"
SHEET_ACTIVITY = "ActivityLog"
SHEET_SETTINGS = "Settings"
SHEET_USERS = "Users"
CACHE_TTL_SECONDS = 45

SEQUENCE = [
    {"step": 1, "channel": "Call", "label": "Cold Call #1"},
    {"step": 2, "channel": "Email", "label": "Intro Email"},
    {"step": 3, "channel": "LinkedIn", "label": "LinkedIn Connect"},
    {"step": 4, "channel": "Call", "label": "Follow-up Call"},
    {"step": 5, "channel": "Email", "label": "Value Email"},
    {"step": 6, "channel": "LinkedIn", "label": "LinkedIn Message"},
    {"step": 7, "channel": "Call", "label": "Decision Call"},
]

CALL_OUTCOMES = [
    "Dialed – no answer",
    "Dialed – voicemail",
    "Connected – gatekeeper only",
    "Connected – decision maker",
    "Meeting set",
    "Not interested",
    "Wrong number",
]
EMAIL_OUTCOMES = ["Sent", "Replied", "Bounced"]
LI_OUTCOMES = ["Outreach done", "Response received"]
CONNECTED_OUTS = {"Connected – decision maker", "Connected – gatekeeper only", "Meeting set"}

STATUSES = ["Cold", "Warm", "Hot", "DNC"]
TEAM_USERS = ["Alex", "Jordan", "Morgan", "Taylor", "Casey", "Riley", "Drew", "Skyler", "Quinn", "Avery"]

CORE_LEAD_COLS = [
    "LeadID", "ContactName", "Company", "Title", "Phone", "Email",
    "Industry", "Revenue", "Status", "SequenceStep", "Notes",
    "LastTouched", "LastTouchedBy", "LockedBy", "LockTime",
]
ACTIVITY_COLS = [
    "ActivityID", "Timestamp", "Username", "LeadID", "ContactName",
    "Channel", "Outcome", "Action", "Notes",
]

URL_COL_HINTS = [
    "linkedin", "linkedin url", "person linkedin", "contact linkedin",
    "company linkedin", "website", "company website", "url", "profile",
]

INTEL_FIELDS = [
    ("# Employees", "Employees"),
    ("Employees", "Employees"),
    ("Annual Revenue", "Revenue"),
    ("Industry", "Industry"),
    ("City", "City"),
    ("State", "State"),
    ("Country", "Country"),
    ("Keywords", "Keywords"),
    ("Primary Intent Topic", "Intent Topic"),
    ("Intent Score", "Intent Score"),
    ("Total Funding", "Total Funding"),
    ("Latest Funding", "Latest Funding"),
]

COLUMN_MAP = {
    "full name": "ContactName",
    "name": "ContactName",
    "contact name": "ContactName",
    "company": "Company",
    "company name": "Company",
    "organization": "Company",
    "title": "Title",
    "job title": "Title",
    "position": "Title",
    "phone": "Phone",
    "phone number": "Phone",
    "mobile": "Phone",
    "email": "Email",
    "email address": "Email",
    "work email": "Email",
    "industry": "Industry",
    "revenue": "Revenue",
    "annual revenue": "Revenue",
}


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "logged_in": False,
        "username": "",
        "active_lead_id": None,
        "ai_draft": "",
        "ai_subject": "",
        "dial_session": False,
        "email_panel_open": False,
        "leads_last_good": pd.DataFrame(columns=CORE_LEAD_COLS),
        "activity_last_good": pd.DataFrame(columns=ACTIVITY_COLS),
        "settings_last_good": {},
        "skip_set": set(),
        "smtp_test_cfg": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# ─────────────────────────────────────────────
#  GOOGLE SHEETS
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)


conn = get_conn()


def ensure_columns(df, columns):
    safe_df = df.copy() if df is not None else pd.DataFrame()
    for col in columns:
        if col not in safe_df.columns:
            safe_df[col] = ""
    return safe_df


def normalize_leads_df(df):
    df = ensure_columns(df, CORE_LEAD_COLS)
    if df.empty:
        return pd.DataFrame(columns=list(df.columns))
    df["LeadID"] = df["LeadID"].astype(str)
    df["SequenceStep"] = pd.to_numeric(df["SequenceStep"], errors="coerce").fillna(1).astype(int)
    df["Status"] = df["Status"].replace("", pd.NA).fillna("Cold")
    df["LastTouched"] = pd.to_datetime(df["LastTouched"], errors="coerce", utc=True)
    df["LockTime"] = pd.to_datetime(df["LockTime"], errors="coerce", utc=True)
    for col in ["ContactName", "Company", "Title", "Phone", "Email", "Industry", "Revenue", "Notes", "LastTouchedBy", "LockedBy"]:
        df[col] = df[col].fillna("").astype(str)
    return df


def normalize_activity_df(df):
    df = ensure_columns(df, ACTIVITY_COLS)
    if df.empty:
        return pd.DataFrame(columns=list(df.columns))
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)
    for col in ["ActivityID", "Username", "LeadID", "ContactName", "Channel", "Outcome", "Action", "Notes"]:
        df[col] = df[col].fillna("").astype(str)
    return df


def dataframe_for_sheet(df, columns):
    out = ensure_columns(df, columns).copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out.fillna("")


def is_rate_limit_error(exc):
    text = str(exc)
    return "quota" in text.lower() or "429" in text or "RESOURCE_EXHAUSTED" in text


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def read_sheet_cached(worksheet_name):
    df = conn.read(worksheet=worksheet_name, ttl=CACHE_TTL_SECONDS)
    return pd.DataFrame() if df is None else pd.DataFrame(df)


def clear_sheet_caches():
    read_sheet_cached.clear()


def load_leads(show_errors=True):
    try:
        df = normalize_leads_df(read_sheet_cached(SHEET_LEADS))
        st.session_state.leads_last_good = df.copy()
        return df
    except Exception as exc:
        fallback = normalize_leads_df(st.session_state.leads_last_good)
        if show_errors:
            if is_rate_limit_error(exc):
                st.warning("Google Sheets read quota was hit. Showing the most recent cached leads while the quota cools down.")
            else:
                st.error(f"Leads load error: {exc}")
        return fallback


def load_activity(show_errors=False):
    try:
        df = normalize_activity_df(read_sheet_cached(SHEET_ACTIVITY))
        st.session_state.activity_last_good = df.copy()
        return df
    except Exception as exc:
        fallback = normalize_activity_df(st.session_state.activity_last_good)
        if show_errors:
            if is_rate_limit_error(exc):
                st.warning("Google Sheets activity quota was hit. Showing cached activity.")
            else:
                st.error(f"Activity load error: {exc}")
        return fallback


def load_settings(show_errors=False):
    try:
        df = read_sheet_cached(SHEET_SETTINGS)
        if df is None or df.empty or "key" not in df.columns:
            st.session_state.settings_last_good = {}
            return {}
        settings = dict(zip(df["key"].astype(str), df["value"].astype(str)))
        st.session_state.settings_last_good = settings
        return settings
    except Exception as exc:
        fallback = dict(st.session_state.settings_last_good)
        if show_errors:
            if is_rate_limit_error(exc):
                st.info("Refreshing cached settings. Google Sheets quota is cooling down.")
            else:
                st.error(f"Settings load error: {exc}")
        return fallback


def save_leads(df):
    try:
        normalized = normalize_leads_df(df)
        conn.update(worksheet=SHEET_LEADS, data=dataframe_for_sheet(normalized, list(normalized.columns)))
        st.session_state.leads_last_good = normalized.copy()
        clear_sheet_caches()
        return True
    except Exception as exc:
        st.error(f"Save error: {exc}")
        return False


def save_activity(df):
    try:
        normalized = normalize_activity_df(df)
        conn.update(worksheet=SHEET_ACTIVITY, data=dataframe_for_sheet(normalized, list(normalized.columns)))
        st.session_state.activity_last_good = normalized.copy()
        clear_sheet_caches()
        return True
    except Exception as exc:
        st.warning(f"Activity save error: {exc}")
        return False


def save_settings(settings_dict):
    try:
        settings_df = pd.DataFrame(list(settings_dict.items()), columns=["key", "value"])
        conn.update(worksheet=SHEET_SETTINGS, data=settings_df)
        st.session_state.settings_last_good = dict(settings_dict)
        st.session_state.smtp_test_cfg = dict(settings_dict)
        clear_sheet_caches()
        return True
    except Exception as exc:
        st.error(f"Settings save error: {exc}")
        return False


def log_activity(lead_id, contact_name, channel, outcome, action, notes=""):
    df = load_activity(show_errors=False)
    row = {
        "ActivityID": f"ACT-{int(time.time() * 1000)}",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Username": st.session_state.username,
        "LeadID": lead_id,
        "ContactName": contact_name,
        "Channel": channel,
        "Outcome": outcome,
        "Action": action,
        "Notes": notes,
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_activity(df)


def ensure_sheet(worksheet_name, columns):
    try:
        existing = conn.read(worksheet=worksheet_name, ttl=CACHE_TTL_SECONDS)
        existing = pd.DataFrame() if existing is None else pd.DataFrame(existing)
    except Exception:
        existing = pd.DataFrame()

    if existing.empty:
        conn.update(worksheet=worksheet_name, data=pd.DataFrame(columns=columns))
        return

    for col in columns:
        if col not in existing.columns:
            existing[col] = ""
    conn.update(worksheet=worksheet_name, data=existing)


def bootstrap_sheets():
    try:
        ensure_sheet(SHEET_LEADS, CORE_LEAD_COLS)
        ensure_sheet(SHEET_ACTIVITY, ACTIVITY_COLS)
        ensure_sheet(SHEET_SETTINGS, ["key", "value"])
        ensure_sheet(SHEET_USERS, ["username", "password", "role", "display"])
        clear_sheet_caches()
        return True, "Sheets initialised without overwriting existing data ✓"
    except Exception as exc:
        return False, str(exc)


def seed_demo_data():
    industries = ["Automotive", "Aerospace", "Food & Bev", "Heavy Equipment", "Plastics", "Metal Fab"]
    companies = [
        ("Apex Precision Parts", "Sarah Chen", "VP Operations", "(312) 555-0142", "s.chen@apexprecision.com"),
        ("Ironclad Fabrication", "Marcus Webb", "Plant Manager", "(415) 555-0193", "m.webb@ironclad.com"),
        ("Summit Aerospace", "Diana Patel", "Director of Procurement", "(213) 555-0167", "d.patel@summitaero.com"),
        ("CoreTech Manufacturing", "James Okafor", "COO", "(312) 555-0188", "j.okafor@coretech.com"),
        ("BlueLine Plastics", "Rachel Torres", "Supply Chain Lead", "(617) 555-0154", "r.torres@blueline.com"),
        ("Forgemaster Industries", "Tom Kramer", "CEO", "(503) 555-0171", "t.kramer@forgemaster.com"),
        ("Velocity Automotive", "Lisa Nguyen", "Operations Director", "(734) 555-0139", "l.nguyen@velocityauto.com"),
        ("Meridian Metal Works", "Evan Shaw", "Purchasing Manager", "(216) 555-0182", "e.shaw@meridianmetal.com"),
    ]
    reps = ["Alex", "Jordan", "Morgan", "Taylor"]
    statuses = ["Cold", "Warm", "Hot", "Cold", "Warm", "Hot", "Cold", "Warm"]
    steps = [1, 2, 3, 4, 1, 2, 3, 1]
    now = datetime.now(timezone.utc)
    leads, acts = [], []

    for i, ((comp, contact, title, phone, email), status, step) in enumerate(zip(companies, statuses, steps)):
        lid = f"L-DEMO-{i+1:03d}"
        lts = (now - timedelta(days=random.randint(0, 12))).strftime("%Y-%m-%dT%H:%M:%SZ")
        rep = reps[i % len(reps)]
        leads.append({
            "LeadID": lid,
            "ContactName": contact,
            "Company": comp,
            "Title": title,
            "Phone": phone,
            "Email": email,
            "Industry": industries[i % len(industries)],
            "Revenue": ["$2M-$5M", "$5M-$20M", "$20M-$50M", "$50M+"][i % 4],
            "Status": status,
            "SequenceStep": step,
            "Notes": "Showed interest in Q3 pricing. Follow up on lead time concerns." if status != "Cold" else "",
            "LastTouched": lts,
            "LastTouchedBy": rep,
            "LockedBy": "",
            "LockTime": "",
        })
        for j in range(random.randint(2, 4)):
            ch = ["Call", "Email", "LinkedIn"][j % 3]
            out = CALL_OUTCOMES[j % len(CALL_OUTCOMES)] if ch == "Call" else EMAIL_OUTCOMES[j % len(EMAIL_OUTCOMES)] if ch == "Email" else LI_OUTCOMES[j % len(LI_OUTCOMES)]
            acts.append({
                "ActivityID": f"ACT-D-{i * 10 + j}",
                "Timestamp": (now - timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Username": reps[(i + j) % len(reps)],
                "LeadID": lid,
                "ContactName": contact,
                "Channel": ch,
                "Outcome": out,
                "Action": f"Step {j+1} touch",
                "Notes": "Demo entry",
            })

    try:
        conn.update(worksheet=SHEET_LEADS, data=pd.DataFrame(leads))
        conn.update(worksheet=SHEET_ACTIVITY, data=pd.DataFrame(acts))
        st.session_state.leads_last_good = normalize_leads_df(pd.DataFrame(leads))
        st.session_state.activity_last_good = normalize_activity_df(pd.DataFrame(acts))
        clear_sheet_caches()
        return True, f"Seeded {len(leads)} leads + {len(acts)} activities ✓"
    except Exception as exc:
        return False, str(exc)


# ─────────────────────────────────────────────
#  LEAD ROUTING & LOCKS
# ─────────────────────────────────────────────
def score_lead(row):
    now = datetime.now(timezone.utc)
    if row["Status"] == "DNC":
        return -9999
    lead_id = str(row.get("LeadID", ""))
    if lead_id in st.session_state.get("skip_set", set()):
        return -9997
    locked_by = str(row.get("LockedBy", "")).strip()
    lock_time = row.get("LockTime")
    if locked_by and locked_by != st.session_state.username:
        if pd.notna(lock_time) and (now - lock_time).total_seconds() < 600:
            return -9998
    last = row["LastTouched"]
    age = (now - last).total_seconds() / 86400 if pd.notna(last) else 30
    mult = {"Hot": 3.0, "Warm": 1.5, "Cold": 1.0}.get(row["Status"], 0.5)
    step_bonus = (8 - int(row["SequenceStep"])) * 8
    return (age * 5 + step_bonus) * mult


def get_next_lead(df):
    if df.empty:
        return None
    ranked = df.copy()
    ranked["_score"] = ranked.apply(score_lead, axis=1)
    ranked = ranked[ranked["_score"] > -9000]
    return None if ranked.empty else ranked.sort_values("_score", ascending=False).iloc[0]


def lock_lead(df, lead_id):
    now_s = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    df.loc[df["LeadID"] == lead_id, "LockedBy"] = st.session_state.username
    df.loc[df["LeadID"] == lead_id, "LockTime"] = now_s
    return df


def unlock_lead(df, lead_id):
    df.loc[df["LeadID"] == lead_id, "LockedBy"] = ""
    df.loc[df["LeadID"] == lead_id, "LockTime"] = ""
    return df


def advance_lead(df, lead_id, new_status, new_notes):
    now_s = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = df[df["LeadID"] == lead_id].iloc[0]
    next_step = min(int(row["SequenceStep"]) + 1, 7)
    df.loc[df["LeadID"] == lead_id, "Status"] = new_status
    df.loc[df["LeadID"] == lead_id, "SequenceStep"] = next_step
    df.loc[df["LeadID"] == lead_id, "LastTouched"] = now_s
    df.loc[df["LeadID"] == lead_id, "LastTouchedBy"] = st.session_state.username
    if new_notes.strip():
        existing = str(row["Notes"]).strip()
        prefix = f"{existing}\n" if existing else ""
        df.loc[df["LeadID"] == lead_id, "Notes"] = f"{prefix}[{now_s[:10]}] {new_notes}"
    return unlock_lead(df, lead_id)


# ─────────────────────────────────────────────
#  EMAIL
# ─────────────────────────────────────────────
def get_smtp_settings():
    settings = load_settings()
    return {
        "from_address": settings.get("smtp_from", ""),
        "smtp_host": settings.get("smtp_host", "smtp.gmail.com"),
        "smtp_port": int(settings.get("smtp_port", "587")),
        "smtp_user": settings.get("smtp_user", ""),
        "smtp_password": settings.get("smtp_password", ""),
        "smtp_label": settings.get("smtp_label", "Email"),
    }


def send_email_smtp(cfg, to_addr, subject, body):
    if not cfg["smtp_user"] or not cfg["smtp_password"]:
        return False, "SMTP not configured. Go to Setup → Email Config."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg["from_address"] or cfg["smtp_user"]
        msg["To"] = to_addr
        msg.attach(MIMEText(body, "plain"))

        host = str(cfg["smtp_host"]).strip()
        port = int(cfg["smtp_port"])
        user = str(cfg["smtp_user"]).strip()
        password = str(cfg["smtp_password"]).strip().replace(" ", "")

        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=20) as smtp:
                smtp.login(user, password)
                smtp.sendmail(msg["From"], [to_addr], msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=20) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(user, password)
                smtp.sendmail(msg["From"], [to_addr], msg.as_string())
        return True, "Email sent ✓"
    except Exception as exc:
        return False, f"SMTP error: {exc}"


# ─────────────────────────────────────────────
#  GEMINI
# ─────────────────────────────────────────────
def generate_ai_draft(lead_row, draft_type):
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return "Subject: Quick follow-up", "No AI key configured — write your message here."

    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    contact = lead_row.get("ContactName", "there")
    company = lead_row.get("Company", "the company")
    industry = lead_row.get("Industry", "manufacturing")
    revenue = lead_row.get("Revenue", "unknown")
    notes = lead_row.get("Notes", "no prior notes")

    if draft_type == "email":
        prompt = (
            f"Write a B2B follow-up sales email.\n"
            f"Lead: {contact} at {company} | Industry: {industry} | Revenue: {revenue}\n"
            f"Prior notes: {notes}\n"
            f"Rules: Professional, operator-first, zero jargon, simple language.\n"
            f"MAX 3 sentence body. First line must be 'Subject: <subject here>'. No fluff."
        )
    else:
        prompt = (
            f"Write a LinkedIn connection message for B2B outreach.\n"
            f"Lead: {contact} at {company} | Industry: {industry} | Revenue: {revenue}\n"
            f"Prior notes: {notes}\n"
            f"Rules: Human, witty but professional. MAX 3 sentences. No 'I hope this finds you well.'"
        )

    try:
        text = model.generate_content(prompt).text.strip()
        if draft_type == "email":
            lines = text.split("\n")
            subject = lines[0].replace("Subject:", "").strip() if lines and lines[0].lower().startswith("subject:") else f"Following up — {company}"
            body = "\n".join(lines[1:]).strip()
            return subject, body
        return "", text
    except Exception as exc:
        return "Subject: Follow-up", f"Gemini error: {exc}"


# ─────────────────────────────────────────────
#  CSV / EXCEL IMPORT
# ─────────────────────────────────────────────
def detect_url_columns(df):
    url_cols = []
    for col in df.columns:
        cl = col.lower().strip()
        if any(hint in cl for hint in URL_COL_HINTS):
            url_cols.append(col)
        elif df[col].dtype == object:
            sample = df[col].dropna().head(5).astype(str)
            if sample.str.startswith("http").any():
                url_cols.append(col)
    return list(set(url_cols))


def map_import_df(raw_df):
    df = raw_df.copy()
    rename = {}
    first_name_col, last_name_col = None, None

    for col in df.columns:
        cl = col.lower().strip()
        if "first name" in cl or cl == "first":
            first_name_col = col
        elif "last name" in cl or cl == "last":
            last_name_col = col
        elif cl in COLUMN_MAP:
            rename[col] = COLUMN_MAP[cl]

    df = df.rename(columns=rename)

    if "ContactName" not in df.columns:
        if first_name_col and last_name_col:
            df["ContactName"] = (
                df[first_name_col].fillna("").astype(str).str.strip()
                + " "
                + df[last_name_col].fillna("").astype(str).str.strip()
            ).str.strip()
        elif first_name_col:
            df["ContactName"] = df[first_name_col].fillna("").astype(str).str.strip()

    for col in CORE_LEAD_COLS:
        if col not in df.columns:
            df[col] = ""

    for i, row in df.iterrows():
        val = str(row.get("LeadID", "")).strip()
        if not val or val == "nan":
            df.at[i, "LeadID"] = f"L-{int(time.time() * 1000)}-{i}"

    df["Status"] = df["Status"].replace("", pd.NA).fillna("Cold")
    df["SequenceStep"] = pd.to_numeric(df["SequenceStep"], errors="coerce").fillna(1).astype(int)
    df["Notes"] = df["Notes"].fillna("")
    df["LockedBy"] = df["LockedBy"].fillna("")
    df["LockTime"] = df["LockTime"].fillna("")
    return df


# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────
def sl(txt):
    return f'<div class="section-label">{txt}</div>'


def status_badge(status):
    cls = {"Cold": "badge-cold", "Warm": "badge-warm", "Hot": "badge-hot", "DNC": "badge-dnc"}.get(status, "badge-cold")
    return f'<span class="badge {cls}">{status}</span>'


def channel_badge(channel):
    cls = {"Call": "ch-call", "Email": "ch-email", "LinkedIn": "ch-li"}.get(channel, "ch-call")
    icons = {"Call": "📞", "Email": "✉️", "LinkedIn": "🔗"}
    return f'<span class="badge {cls}">{icons.get(channel, "")} {channel}</span>'


def step_indicator(current_step):
    parts = []
    icons = {"Call": "📞", "Email": "✉️", "LinkedIn": "🔗"}
    for step in SEQUENCE:
        number = step["step"]
        cls = "done" if number < current_step else "active" if number == current_step else ""
        parts.append(f'<div class="step-dot {cls}" title="Step {number}: {step["label"]}">{icons.get(step["channel"], "·")}</div>')
        if number < 7:
            parts.append('<div class="step-line"></div>')
    st.markdown(f'<div class="step-bar">{"".join(parts)}</div>', unsafe_allow_html=True)


def get_step_info(step_num):
    for step in SEQUENCE:
        if step["step"] == step_num:
            return step
    return {"step": step_num, "channel": "Call", "label": f"Step {step_num}"}


def render_intel_panel(row):
    chips = []
    seen = set()
    for src_col, label in INTEL_FIELDS:
        if src_col in row.index:
            val = str(row.get(src_col, "")).strip()
            if val and val not in ("nan", "", "None") and label not in seen:
                chips.append(f'<div class="intel-chip"><span>{label}</span>{val}</div>')
                seen.add(label)
    for col, label in [("Revenue", "Revenue"), ("Industry", "Industry")]:
        if label not in seen:
            val = str(row.get(col, "")).strip()
            if val and val not in ("nan", "", "None"):
                chips.append(f'<div class="intel-chip"><span>{label}</span>{val}</div>')
    if chips:
        st.markdown(sl("COMPANY INTEL"), unsafe_allow_html=True)
        st.markdown(f'<div class="intel-grid">{"".join(chips)}</div>', unsafe_allow_html=True)


def render_url_buttons(row):
    url_cols = detect_url_columns(pd.DataFrame([row]))
    if not url_cols:
        return
    links = []
    for col in url_cols:
        val = str(row.get(col, "")).strip()
        if not val or val in ("nan", "None", ""):
            continue
        if not val.startswith("http"):
            val = "https://" + val
        cl = col.lower()
        if "person" in cl or ("linkedin" in cl and "company" not in cl):
            links.append(("👤 Contact LinkedIn", val))
        elif "company" in cl and "linkedin" in cl:
            links.append(("🏢 Company LinkedIn", val))
        elif "website" in cl or "web" in cl:
            links.append(("🌐 Company Website", val))
        else:
            links.append((f"🔗 {col}", val))
    if links:
        st.markdown(sl("QUICK LINKS"), unsafe_allow_html=True)
        cols = st.columns(len(links))
        for i, (label, url) in enumerate(links):
            with cols[i]:
                st.link_button(label, url, use_container_width=True)


def kpi_tile(val, label, cls="", sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi {cls}"><div class="kpi-val">{val}</div><div class="kpi-label">{label}</div>{sub_html}</div>'


# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
def tab_setup():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">⚙️ SYSTEM SETUP — START HERE</h2>', unsafe_allow_html=True)
    settings = load_settings()

    st.markdown(sl("✉️ EMAIL CONFIGURATION"), unsafe_allow_html=True)
    st.markdown('<div class="op-card">', unsafe_allow_html=True)
    ec1, ec2 = st.columns(2)
    with ec1:
        email_type = st.selectbox("Email Provider", ["Gmail", "Custom Domain / SMTP"], key="setup_email_type")
        from_addr = st.text_input("From Address", value=settings.get("smtp_from", ""), placeholder="you@gmail.com", key="setup_from")
        smtp_label = st.text_input("Identity Label", value=settings.get("smtp_label", "Work Email"), placeholder="e.g. Gmail or Ops Email", key="setup_label")
    with ec2:
        if email_type == "Gmail":
            smtp_host = "smtp.gmail.com"
            smtp_port = 587
            st.info("Gmail requires a Google App Password. Turn on 2-Step Verification, then create an App Password and paste that here instead of your normal password.")
        else:
            smtp_host = st.text_input("SMTP Host", value=settings.get("smtp_host", "mail.yourdomain.com"), key="setup_host")
            smtp_port = st.number_input("SMTP Port", value=int(settings.get("smtp_port", 587)), key="setup_port")
        smtp_user = st.text_input("SMTP Username", value=settings.get("smtp_user", ""), key="setup_user")
        smtp_pwd = st.text_input("SMTP Password / App Password", value=settings.get("smtp_password", ""), type="password", key="setup_pwd")

    if st.button("💾 SAVE EMAIL CONFIG", use_container_width=True, key="btn_save_email"):
        new_settings = dict(settings)
        new_settings.update({
            "smtp_from": from_addr.strip(),
            "smtp_host": smtp_host if email_type != "Gmail" else "smtp.gmail.com",
            "smtp_port": str(smtp_port if email_type != "Gmail" else 587),
            "smtp_user": smtp_user.strip(),
            "smtp_password": smtp_pwd.strip().replace(" ", ""),
            "smtp_label": smtp_label.strip(),
        })
        if save_settings(new_settings):
            st.success("Email config saved ✓")

    st.markdown(sl("TEST EMAIL"), unsafe_allow_html=True)
    test_to = st.text_input("Send test to", placeholder="your@email.com", key="setup_test_to")
    if st.button("📤 SEND TEST EMAIL", use_container_width=True, key="btn_test_email"):
        cfg = st.session_state.get("smtp_test_cfg") or get_smtp_settings()
        ok, msg = send_email_smtp(cfg, test_to.strip(), "Master of Ops — Test Email", "This is a test email from your Master of Ops outbound system.")
        (st.success if ok else st.error)(msg)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="setup-card">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.55rem;font-weight:800;
                    letter-spacing:.1em;color:#00A7A7;margin-bottom:.4rem;">ZERO → LIVE IN 5 STEPS</div>
        <div style="color:#8899AA;font-size:.84rem;">Follow in order. Bootstrapper handles the sheet setup.</div>
    </div>
    """, unsafe_allow_html=True)

    steps_data = [
        ("01", "GOOGLE SHEET", "#00A7A7", 'Go to <a href="https://sheets.google.com" target="_blank" style="color:#00A7A7">sheets.google.com</a>. Create a blank spreadsheet. Add four tabs named exactly: <code>Leads</code>, <code>ActivityLog</code>, <code>Settings</code>, and <code>Users</code>.'),
        ("02", "GCP SERVICE ACCOUNT", "#F0A500", "Enable <strong>Google Sheets API</strong> and <strong>Google Drive API</strong>. IAM → Service Accounts → Create → Download JSON key."),
        ("03", "SHARE SHEET", "#3DBA72", "Open your Sheet → Share → paste the service account email → set to <strong>Editor</strong>."),
        ("04", "STREAMLIT SECRETS", "#9B72CF", """App Settings → Secrets. Paste and fill in your values:<br>
<pre style="background:#0B0F14;padding:.7rem;border-radius:4px;font-size:.68rem;color:#00A7A7;overflow-x:auto;">[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_ID/edit"
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\nKEY\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "name@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

GEMINI_API_KEY = "your-gemini-key-from-aistudio.google.com"</pre>"""),
        ("05", "BOOTSTRAP & DEPLOY", "#00A7A7", "Click Bootstrap → Seed Demo → go to the Dial Queue and start executing."),
    ]

    for num, title, color, body in steps_data:
        st.markdown(
            f'<div style="display:flex;gap:1rem;margin:.5rem 0;padding:1rem;background:var(--panel);border:1px solid var(--border);border-left:3px solid {color};border-radius:4px;">'
            f'<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.9rem;font-weight:800;color:{color};min-width:38px;line-height:1;">{num}</div>'
            f'<div><div style="font-family:\'Barlow Condensed\',sans-serif;font-size:.82rem;font-weight:700;letter-spacing:.1em;color:{color};margin-bottom:.3rem;">{title}</div>'
            f'<div style="font-size:.8rem;color:#CCDDEE;line-height:1.65;">{body}</div></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Bootstrap Sheets**")
        st.caption("Creates missing tabs and headers without wiping existing data.")
        if st.button("🚀 BOOTSTRAP", use_container_width=True):
            ok, msg = bootstrap_sheets()
            (st.success if ok else st.error)(msg)
    with c2:
        st.markdown("**Seed Demo Data**")
        st.caption("8 leads + activity records for dashboard testing.")
        if st.button("🧪 SEED DEMO", use_container_width=True):
            ok, msg = seed_demo_data()
            (st.success if ok else st.error)(msg)
    with c3:
        st.markdown("**Test Connection**")
        st.caption("Confirms read/write is working.")
        if st.button("🔌 TEST", use_container_width=True):
            df = load_leads()
            st.success(f"Connected ✓ — {len(df)} leads found.")

    st.markdown("---")
    st.markdown(sl("SEQUENCE CONFIGURATION (7 STEPS)"), unsafe_allow_html=True)
    seq_html = "".join([
        f'<div style="display:flex;gap:.75rem;padding:.4rem .75rem;border-bottom:1px solid var(--border);font-size:.8rem;align-items:center;">'
        f'<span style="font-family:\'DM Mono\',monospace;color:var(--muted);min-width:20px;">{s["step"]}</span>'
        f'{channel_badge(s["channel"])}'
        f'<span style="color:#CCDDEE;">{s["label"]}</span></div>'
        for s in SEQUENCE
    ])
    st.markdown(f'<div class="op-card" style="padding:0;">{seq_html}</div>', unsafe_allow_html=True)
    st.caption("To change the sequence, edit the SEQUENCE list at the top of app.py and redeploy.")

    st.markdown("---")
    st.markdown(
        f'<div style="font-size:.7rem;color:#4A5A6A;line-height:1.9;">'
        f'<strong style="color:#8899AA;">Leads columns:</strong> {" · ".join(CORE_LEAD_COLS)}<br>'
        f'<strong style="color:#8899AA;">ActivityLog columns:</strong> {" · ".join(ACTIVITY_COLS)}<br>'
        f'<strong style="color:#8899AA;">Extra columns</strong> from CSV/Excel import are preserved automatically.<br>'
        f'<strong style="color:#8899AA;">Sheets cache:</strong> {CACHE_TTL_SECONDS}s to avoid quota blowups.</div>',
        unsafe_allow_html=True,
    )


def tab_dial_queue():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📞 DIAL QUEUE — OUTBOUND COCKPIT</h2>', unsafe_allow_html=True)

    df = load_leads()
    if df.empty:
        st.info("No leads loaded. Go to **Setup** to bootstrap + seed, or **Manage Leads** to import.")
        return

    total = len(df)
    hot = int((df["Status"] == "Hot").sum())
    warm = int((df["Status"] == "Warm").sum())
    active = int((df["Status"] != "DNC").sum())

    st.markdown(
        f'<div class="kpi-strip">'
        f'{kpi_tile(total, "Total Leads")}'
        f'{kpi_tile(warm, "Warm", "amber")}'
        f'{kpi_tile(hot, "Hot 🔥", "red")}'
        f'{kpi_tile(active, "In Queue", "green")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(sl("QUEUE FILTERS"), unsafe_allow_html=True)
    q1, q2 = st.columns(2)
    campaign_column = "Campaign" if "Campaign" in df.columns else None
    with q1:
        if campaign_column:
            campaign_options = ["All"] + sorted(df[campaign_column].dropna().astype(str).unique().tolist())
            selected_campaign = st.selectbox("Campaign", campaign_options, key="dq_campaign")
        else:
            selected_campaign = "All"
            st.caption("Add a `Campaign` column to filter queue by campaign.")
    with q2:
        start_step = st.selectbox("Start from step", ["All", 1, 2, 3, 4, 5, 6, 7], key="dq_start_step")

    if not st.session_state.dial_session:
        if st.button("▶  START AUTO DIAL SESSION", use_container_width=True):
            st.session_state.dial_session = True
            st.session_state.active_lead_id = None
            st.session_state.ai_draft = ""
            st.session_state.ai_subject = ""
            st.session_state.email_panel_open = False
            st.session_state.skip_set = set()
            st.rerun()
        st.caption("Auto-dial loads leads one after another. After each save the next lead loads automatically.")
        return

    col_banner, col_stop = st.columns([4, 1])
    with col_banner:
        st.markdown(
            '<div class="session-banner">'
            '<span><span class="session-pulse"></span><span class="session-active">AUTO DIAL SESSION ACTIVE</span></span>'
            '<span style="font-size:.72rem;color:var(--muted);">Save each call → next lead loads automatically</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_stop:
        if st.button("■ STOP SESSION", use_container_width=True):
            if st.session_state.active_lead_id:
                df = unlock_lead(df, st.session_state.active_lead_id)
                save_leads(df)
            st.session_state.dial_session = False
            st.session_state.active_lead_id = None
            st.rerun()

    queue_df = df.copy()
    if selected_campaign != "All" and campaign_column:
        queue_df = queue_df[queue_df[campaign_column].astype(str) == selected_campaign]
    if start_step != "All":
        queue_df = queue_df[queue_df["SequenceStep"] >= int(start_step)]

    lead_options = {
        f"{row['ContactName']} — {row['Company']} ({row['LeadID']})": row["LeadID"]
        for _, row in queue_df.iterrows()
    }
    chosen_label = st.selectbox("Specific lead override", ["Auto-priority queue"] + list(lead_options.keys()), key="dq_specific_lead")

    lead = None
    if chosen_label != "Auto-priority queue":
        chosen_id = lead_options[chosen_label]
        matches = queue_df[queue_df["LeadID"] == chosen_id]
        if not matches.empty:
            lead = matches.iloc[0]
    if lead is None:
        lead = get_next_lead(queue_df)
    if lead is None:
        st.success("✅ Queue clear — no leads match the current queue filters.")
        st.session_state.dial_session = False
        return

    lead_id = lead["LeadID"]
    step_num = int(lead["SequenceStep"])
    step_info = get_step_info(step_num)
    channel = step_info["channel"]
    status = lead["Status"]

    if st.session_state.active_lead_id != lead_id:
        df = lock_lead(df, lead_id)
        save_leads(df)
        st.session_state.active_lead_id = lead_id
        st.session_state.ai_draft = ""
        st.session_state.ai_subject = ""
        st.session_state.email_panel_open = channel == "Email"

    col_main, col_intel = st.columns([3, 2])

    with col_main:
        st.markdown(
            f'<div class="lead-block">'
            f'<div class="lead-company">{lead.get("Company", "—")}</div>'
            f'<div class="lead-name">{lead.get("ContactName", "—")}</div>'
            f'<div style="color:var(--muted);font-size:.8rem;margin:.2rem 0;">{lead.get("Title", "—")}</div>'
            f'<div style="margin-top:.5rem;display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;">'
            f'{status_badge(status)}{channel_badge(channel)}'
            f'<span style="font-family:\'DM Mono\',monospace;font-size:.72rem;color:var(--muted);">Step {step_num}/7: {step_info["label"]}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        step_indicator(step_num)

        if channel == "Call":
            phone = str(lead.get("Phone", "")).strip()
            tel_raw = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            tel_url = f"tel:{tel_raw}"

            st.markdown(sl("📞 CALL PANEL"), unsafe_allow_html=True)
            st.markdown(f'<div class="op-card"><div class="dial-number">{phone or "No phone on file"}</div></div>', unsafe_allow_html=True)

            if phone:
                st.link_button(f"📲 DIAL NOW — {phone}", tel_url, use_container_width=True)
                st.caption("Opens your phone dialer with this number pre-loaded. Return here to log the outcome.")
            else:
                st.warning("No phone number for this lead.")

            st.markdown(sl("LOG CALL OUTCOME"), unsafe_allow_html=True)
            call_outcome = st.selectbox("Outcome *", ["— select —"] + CALL_OUTCOMES, key="call_out")
            call_notes = st.text_area("Call notes *", placeholder="What happened? Intel? Next steps?", height=80, key="call_notes")
            new_status = st.selectbox("Update Status", STATUSES, index=STATUSES.index(status), key="call_status")

            save_disabled = call_outcome == "— select —" or not call_notes.strip()
            if st.button("✅ SAVE CALL & NEXT LEAD", use_container_width=True, disabled=save_disabled):
                df = load_leads()
                df = advance_lead(df, lead_id, new_status, call_notes)
                if save_leads(df):
                    log_activity(lead_id, str(lead.get("ContactName", "")), "Call", call_outcome, f"Step {step_num}: {step_info['label']}", call_notes)
                    st.session_state.active_lead_id = None
                    st.session_state.email_panel_open = False
                    st.success("Logged ✓ — Loading next lead…")
                    time.sleep(0.6)
                    st.rerun()

        elif channel == "LinkedIn":
            st.markdown(sl("🔗 LINKEDIN TRACKING"), unsafe_allow_html=True)
            li_notes = st.text_input("Short note (optional)", placeholder="e.g. Sent connection request", key="li_notes")
            lc1, lc2 = st.columns(2)
            with lc1:
                if st.button("✅ OUTREACH DONE", use_container_width=True):
                    df = load_leads()
                    df = advance_lead(df, lead_id, status, li_notes or "LinkedIn outreach done")
                    if save_leads(df):
                        log_activity(lead_id, str(lead.get("ContactName", "")), "LinkedIn", "Outreach done", f"Step {step_num}: {step_info['label']}", li_notes)
                        st.session_state.active_lead_id = None
                        st.success("Logged ✓ — next lead…")
                        time.sleep(0.5)
                        st.rerun()
            with lc2:
                if st.button("💬 RESPONSE RECEIVED", use_container_width=True):
                    df = load_leads()
                    df = advance_lead(df, lead_id, "Warm", li_notes or "LinkedIn response received")
                    if save_leads(df):
                        log_activity(lead_id, str(lead.get("ContactName", "")), "LinkedIn", "Response received", f"Step {step_num}: {step_info['label']}", li_notes)
                        st.session_state.active_lead_id = None
                        st.success("Logged ✓ → Status: Warm")
                        time.sleep(0.5)
                        st.rerun()

        if channel == "Email" or st.session_state.email_panel_open:
            st.markdown(sl("✉️ EMAIL PANEL"), unsafe_allow_html=True)
            cfg = get_smtp_settings()

            if not cfg["smtp_user"]:
                st.info("Email not configured. Add SMTP details in Setup → Email Configuration. You can still log email manually below.")
            else:
                st.caption(f"Sending as: {cfg['smtp_label']} ({cfg['from_address'] or cfg['smtp_user']})")

                if not st.session_state.ai_subject or not st.session_state.ai_draft:
                    with st.spinner("Drafting email…"):
                        subj, body = generate_ai_draft(lead, "email")
                        st.session_state.ai_subject = subj
                        st.session_state.ai_draft = body

                to_addr = st.text_input("To", value=str(lead.get("Email", "")), key="email_to")
                subject = st.text_input("Subject", value=st.session_state.ai_subject, key="email_subj")
                body = st.text_area("Body", value=st.session_state.ai_draft, height=130, key="email_body")

                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("📤 SEND EMAIL", use_container_width=True):
                        if not to_addr.strip():
                            st.error("To address required.")
                        else:
                            ok, msg = send_email_smtp(cfg, to_addr, subject, body)
                            if ok:
                                df = load_leads()
                                df = advance_lead(df, lead_id, status, f"Email sent: {subject}")
                                save_leads(df)
                                log_activity(lead_id, str(lead.get("ContactName", "")), "Email", "Sent", f"Step {step_num}: {step_info['label']}", f"Subject: {subject}")
                                st.success(msg)
                                st.session_state.email_panel_open = False
                                st.session_state.active_lead_id = None
                                time.sleep(0.6)
                                st.rerun()
                            else:
                                st.error(f"Send failed: {msg}")
                                st.info("For Gmail, use the full Gmail address as username and a Google App Password, not your normal Gmail password.")
                with ec2:
                    if st.button("📝 LOG EMAIL MANUALLY", use_container_width=True):
                        df = load_leads()
                        df = advance_lead(df, lead_id, status, f"Email logged: {subject}")
                        save_leads(df)
                        log_activity(lead_id, str(lead.get("ContactName", "")), "Email", "Sent", f"Step {step_num}: {step_info['label']}", f"Subject: {subject} (manual log)")
                        st.session_state.active_lead_id = None
                        time.sleep(0.5)
                        st.rerun()

            st.markdown(sl("MARK PRIOR EMAIL"), unsafe_allow_html=True)
            rb1, rb2 = st.columns(2)
            with rb1:
                if st.button("↩ MARK REPLIED", use_container_width=True):
                    log_activity(lead_id, str(lead.get("ContactName", "")), "Email", "Replied", "Manual mark", "")
                    st.success("Replied logged.")
            with rb2:
                if st.button("⛔ MARK BOUNCED", use_container_width=True):
                    log_activity(lead_id, str(lead.get("ContactName", "")), "Email", "Bounced", "Manual mark", "")
                    st.success("Bounce logged.")

        if channel != "Email" and not st.session_state.email_panel_open:
            if st.button("✉ ADD EMAIL THIS SESSION", use_container_width=True):
                st.session_state.email_panel_open = True
                st.rerun()

        st.markdown("---")
        sk1, sk2 = st.columns(2)
        with sk1:
            if st.button("⏭ SKIP THIS LEAD", use_container_width=True):
                st.session_state.skip_set.add(lead_id)
                df = load_leads()
                df = unlock_lead(df, lead_id)
                save_leads(df)
                st.session_state.active_lead_id = None
                st.session_state.email_panel_open = False
                st.rerun()
        with sk2:
            if st.button("🚫 MARK DNC", use_container_width=True):
                df = load_leads()
                df.loc[df["LeadID"] == lead_id, "Status"] = "DNC"
                df = unlock_lead(df, lead_id)
                save_leads(df)
                log_activity(lead_id, str(lead.get("ContactName", "")), "Call", "Not interested", "DNC marked", "")
                st.session_state.active_lead_id = None
                st.rerun()

    with col_intel:
        st.markdown(sl("CONTACT INFO"), unsafe_allow_html=True)
        st.markdown(
            f'<div class="op-card" style="font-size:.82rem;line-height:1.9;">'
            f'<div style="color:var(--muted);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.3rem;">Phone</div>'
            f'<div style="font-family:\'DM Mono\',monospace;color:var(--teal);font-size:1rem;margin-bottom:.6rem;">{lead.get("Phone", "—")}</div>'
            f'<div style="color:var(--muted);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">Email</div>'
            f'<div style="font-family:\'DM Mono\',monospace;font-size:.8rem;margin-bottom:.6rem;">{lead.get("Email", "—")}</div>'
            f'<div style="color:var(--muted);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">Company</div>'
            f'<div>{lead.get("Company", "—")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        render_intel_panel(lead)
        render_url_buttons(lead)

        company_enc = urllib.parse.quote_plus(str(lead.get("Company", "")))
        news_url = f"https://www.google.com/search?q={company_enc}+news&tbm=nws"
        st.markdown(sl("RESEARCH"), unsafe_allow_html=True)
        st.link_button("📰 COMPANY NEWS", news_url, use_container_width=True)

        notes_val = str(lead.get("Notes", "")).strip()
        if notes_val and notes_val != "nan":
            st.markdown(sl("PRIOR NOTES"), unsafe_allow_html=True)
            st.markdown(f'<div class="op-card op-card-teal" style="font-size:.82rem;white-space:pre-wrap;max-height:180px;overflow-y:auto;">{notes_val}</div>', unsafe_allow_html=True)

        if channel == "LinkedIn":
            st.markdown(sl("AI LINKEDIN DRAFT"), unsafe_allow_html=True)
            if not st.session_state.ai_draft and st.button("⚡ GENERATE LI DRAFT", use_container_width=True):
                with st.spinner("Drafting…"):
                    _, body = generate_ai_draft(lead, "linkedin")
                    st.session_state.ai_draft = body
            if st.session_state.ai_draft:
                st.markdown(f'<div class="op-card" style="border-color:var(--purple);font-size:.82rem;white-space:pre-wrap;">{st.session_state.ai_draft}</div>', unsafe_allow_html=True)


def tab_analytics():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📊 OPS ANALYTICS — COMMAND VIEW</h2>', unsafe_allow_html=True)

    leads_df = load_leads()
    act_df = load_activity()
    now = datetime.now(timezone.utc)
    today = now.date()

    if leads_df.empty and act_df.empty:
        st.info("No data yet. Go to Setup → Seed Demo Data.")
        return

    cf1, _, _ = st.columns([1, 1, 3])
    with cf1:
        rng = st.selectbox("Time Range", ["Last 7 days", "Last 14 days", "Last 30 days", "All time"])
    cutoff = now - timedelta(days={"Last 7 days": 7, "Last 14 days": 14, "Last 30 days": 30, "All time": 3650}[rng])

    act = act_df.copy()
    if not act.empty and "Timestamp" in act.columns:
        act = act[act["Timestamp"] >= cutoff]

    def ch_out(channel, outcome_filter=None):
        if act.empty or "Channel" not in act.columns:
            return 0
        sub = act[act["Channel"] == channel]
        if outcome_filter:
            sub = sub[sub["Outcome"].isin(outcome_filter)]
        return len(sub)

    dials = ch_out("Call")
    contacts = ch_out("Call", CONNECTED_OUTS)
    contact_rate = round(contacts / dials * 100 if dials else 0, 1)
    meetings = ch_out("Call", {"Meeting set"})
    emails_sent = ch_out("Email", {"Sent"})
    email_reply = ch_out("Email", {"Replied"})
    email_bounce = ch_out("Email", {"Bounced"})
    bounce_rate = round(email_bounce / emails_sent * 100 if emails_sent else 0, 1)
    li_out = ch_out("LinkedIn", {"Outreach done"})
    li_resp = ch_out("LinkedIn", {"Response received"})
    li_rate = round(li_resp / li_out * 100 if li_out else 0, 1)
    total_leads = len(leads_df)
    hot_leads = int((leads_df["Status"] == "Hot").sum()) if not leads_df.empty else 0
    active_reps = act["Username"].nunique() if not act.empty else 0
    today_acts = len(act[pd.to_datetime(act["Timestamp"], utc=True).dt.date == today]) if not act.empty else 0

    st.markdown(sl("📞 CALL PERFORMANCE"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(dials, "Dials")}{kpi_tile(contacts, "Contacts", "green")}{kpi_tile(f"{contact_rate}%", "Contact Rate", "amber")}{kpi_tile(meetings, "Meetings Set", "red")}</div>', unsafe_allow_html=True)
    st.markdown(sl("✉️ EMAIL PERFORMANCE"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(emails_sent, "Emails Sent")}{kpi_tile(email_reply, "Replies", "green")}{kpi_tile(f"{bounce_rate}%", "Bounce Rate", "red")}</div>', unsafe_allow_html=True)
    st.markdown(sl("🔗 LINKEDIN PERFORMANCE"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(li_out, "LI Outreach", "purple")}{kpi_tile(li_resp, "LI Responses", "green")}{kpi_tile(f"{li_rate}%", "LI Response Rate", "amber")}</div>', unsafe_allow_html=True)
    st.markdown(sl("🔥 PIPELINE"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(total_leads, "Total Leads")}{kpi_tile(hot_leads, "Hot 🔥", "red")}{kpi_tile(active_reps, "Active Reps", "purple")}{kpi_tile(today_acts, "Today Actions", "green")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_lb, col_fn = st.columns(2)

    with col_lb:
        st.markdown(sl("🏆 REP LEADERBOARD"), unsafe_allow_html=True)
        if not act.empty:
            lb = act.groupby("Username").size().reset_index(name="touches").sort_values("touches", ascending=False)
            max_t = lb["touches"].max() or 1
            ranks = ["gold", "silver", "bronze"]
            lb_html = ""
            for rank, (_, row) in enumerate(lb.iterrows(), 1):
                rc = ranks[rank - 1] if rank <= 3 else ""
                pct = int(row["touches"] / max_t * 100)
                lb_html += f'<div class="lb-row"><div class="lb-rank {rc}">#{rank}</div><div class="lb-name">{row["Username"]}</div><div class="lb-bar-wrap"><div class="lb-bar" style="width:{pct}%"></div></div><div class="lb-count">{row["touches"]}</div></div>'
            st.markdown(f'<div class="op-card" style="padding:0;">{lb_html}</div>', unsafe_allow_html=True)

        if not act.empty and "Channel" in act.columns:
            st.markdown(sl("REP CHANNEL BREAKDOWN"), unsafe_allow_html=True)
            pivot = act.groupby(["Username", "Channel"]).size().reset_index(name="n").pivot(index="Username", columns="Channel", values="n").fillna(0).astype(int)
            st.dataframe(pivot, use_container_width=True)

    with col_fn:
        st.markdown(sl("🔽 SEQUENCE FUNNEL"), unsafe_allow_html=True)
        if not leads_df.empty:
            total_active = len(leads_df[leads_df["Status"] != "DNC"]) or 1
            colors = {"Call": "#00A7A7", "Email": "#F0A500", "LinkedIn": "#9B72CF"}
            html = ""
            for step in SEQUENCE:
                n = int((leads_df["SequenceStep"] == step["step"]).sum())
                p = round(n / total_active * 100)
                html += f'<div class="funnel-step"><div class="funnel-label">Step {step["step"]}: {step["label"]}</div><div class="funnel-bar-wrap"><div class="funnel-bar" style="width:{p}%;background:{colors[step["channel"]]}"></div></div><div class="funnel-pct">{p}%</div><div class="funnel-n">{n}</div></div>'
            for label, filt, color in [("Warm 🌡", leads_df["Status"] == "Warm", "#F0A500"), ("Hot 🔥", leads_df["Status"] == "Hot", "#E05252"), ("DNC 🚫", leads_df["Status"] == "DNC", "#4A5A6A")]:
                n = int(filt.sum())
                p = round(n / total_active * 100)
                html += f'<div class="funnel-step"><div class="funnel-label">{label}</div><div class="funnel-bar-wrap"><div class="funnel-bar" style="width:{p}%;background:{color}"></div></div><div class="funnel-pct">{p}%</div><div class="funnel-n">{n}</div></div>'
            st.markdown(html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(sl("📈 DAILY ACTIVITY VOLUME"), unsafe_allow_html=True)
    if not act.empty and "Timestamp" in act.columns:
        act["date"] = pd.to_datetime(act["Timestamp"], utc=True).dt.date
        daily = act.groupby("date").size().reset_index(name="count")
        all_days = pd.date_range(start=cutoff.date(), end=today, freq="D").date
        daily = pd.DataFrame({"date": all_days}).merge(daily, on="date", how="left").fillna(0)
        daily["count"] = daily["count"].astype(int)
        max_c = daily["count"].max() or 1
        bars = "".join([f'<div title="{r["date"]}: {r["count"]}" style="flex:1;min-width:4px;height:{max(int(r["count"]/max_c*68),2)}px;background:#00A7A7;border-radius:2px 2px 0 0;opacity:{0.3+0.7*(r["count"]/max_c):.2f}"></div>' for _, r in daily.iterrows()])
        st.markdown(f'<div class="op-card"><div style="display:flex;align-items:flex-end;gap:2px;height:72px;">{bars}</div><div style="display:flex;justify-content:space-between;margin-top:.25rem;"><span style="font-size:.62rem;color:var(--muted);">{daily["date"].iloc[0]}</span><span style="font-size:.62rem;color:var(--muted);">{daily["date"].iloc[-1]}</span></div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(sl("📋 LIVE ACTIVITY FEED"), unsafe_allow_html=True)
    if not act.empty:
        feed = act.sort_values("Timestamp", ascending=False).head(25)
        colors = {"Call": "var(--teal)", "Email": "var(--amber)", "LinkedIn": "var(--purple)"}
        feed_html = ""
        for _, row in feed.iterrows():
            ts = pd.to_datetime(row["Timestamp"], utc=True)
            minutes = int((now - ts).total_seconds() / 60)
            age = f"{minutes}m ago" if minutes < 60 else f"{minutes//60}h ago" if minutes < 1440 else f"{minutes//1440}d ago"
            channel = row.get("Channel", "")
            cc = colors.get(channel, "var(--muted)")
            feed_html += f'<div class="feed-row"><span style="color:var(--muted);font-family:\'DM Mono\',monospace;font-size:.67rem;min-width:52px;">{age}</span><span style="font-weight:600;min-width:65px;color:var(--teal)">{row.get("Username", "")}</span><span style="color:{cc};min-width:62px;font-size:.75rem;">{channel}</span><span style="color:#CCDDEE;min-width:80px;">{row.get("ContactName", "")}</span><span style="color:var(--muted);font-style:italic;font-size:.78rem;">{row.get("Outcome", "")}</span></div>'
        st.markdown(f'<div class="op-card" style="max-height:280px;overflow-y:auto;">{feed_html}</div>', unsafe_allow_html=True)


def tab_manage_leads():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📋 LEAD MANAGEMENT + IMPORT</h2>', unsafe_allow_html=True)
    df = load_leads()

    with st.expander("📥 IMPORT FROM CSV / EXCEL", expanded=False):
        uploaded = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"], key="import_file")
        if uploaded is not None:
            try:
                raw = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                st.success(f"File loaded: {len(raw)} rows, {len(raw.columns)} columns")
                st.caption(f"Columns found: {', '.join(raw.columns.tolist())}")

                mapped = map_import_df(raw)
                url_cols = detect_url_columns(raw)
                if url_cols:
                    st.info(f"URL columns detected and preserved: {', '.join(url_cols)}")

                preview_cols = [c for c in ["ContactName", "Company", "Title", "Phone", "Email", "Industry", "Status"] if c in mapped.columns]
                st.dataframe(mapped[preview_cols].head(8), use_container_width=True)

                ic1, ic2 = st.columns(2)
                with ic1:
                    append_mode = st.radio("Import mode", ["Append to existing", "Replace all leads"], index=0)
                with ic2:
                    default_step = st.selectbox("Start at sequence step", list(range(1, 8)), format_func=lambda x: f"Step {x}: {get_step_info(x)['label']}")
                    mapped["SequenceStep"] = mapped["SequenceStep"].where(mapped["SequenceStep"] > 0, default_step)

                if st.button("✅ CONFIRM IMPORT", use_container_width=True):
                    if append_mode == "Append to existing" and not df.empty:
                        all_cols = list(set(df.columns.tolist() + mapped.columns.tolist()))
                        combined = pd.concat([df.reindex(columns=all_cols), mapped.reindex(columns=all_cols)], ignore_index=True)
                        combined = combined.drop_duplicates(subset=["LeadID"], keep="last")
                    else:
                        combined = mapped
                    if save_leads(combined):
                        st.success(f"Imported {len(mapped)} leads ✓  (Total now: {len(combined)})")
                        st.rerun()
            except Exception as exc:
                st.error(f"Import error: {exc}")

    st.markdown("---")

    with st.expander("➕ ADD SINGLE LEAD", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            cn = st.text_input("Contact Name *", key="new_cn")
            comp = st.text_input("Company *", key="new_comp")
            title = st.text_input("Title", key="new_title")
        with c2:
            phone = st.text_input("Phone", key="new_phone")
            email = st.text_input("Email", key="new_email")
            industry = st.text_input("Industry", key="new_ind")
        with c3:
            revenue = st.text_input("Revenue", key="new_rev")
            status = st.selectbox("Status", STATUSES, key="new_status")
            step = st.selectbox("Start Step", list(range(1, 8)), format_func=lambda x: f"Step {x}: {get_step_info(x)['label']}", key="new_step")

        if st.button("ADD LEAD", use_container_width=True):
            if not cn.strip() or not comp.strip():
                st.error("Contact Name and Company are required.")
            else:
                new = {c: "" for c in CORE_LEAD_COLS}
                new.update({
                    "LeadID": f"L-{int(time.time() * 1000)}",
                    "ContactName": cn.strip(),
                    "Company": comp.strip(),
                    "Title": title.strip(),
                    "Phone": phone.strip(),
                    "Email": email.strip(),
                    "Industry": industry.strip(),
                    "Revenue": revenue.strip(),
                    "Status": status,
                    "SequenceStep": step,
                    "Notes": "",
                    "LockedBy": "",
                    "LockTime": "",
                })
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                if save_leads(df):
                    log_activity(new["LeadID"], cn.strip(), "", "", "Lead Created", "")
                    st.success(f"'{cn}' added ✓")
                    st.rerun()

    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1:
        selected_statuses = st.multiselect("Status", STATUSES, default=STATUSES)
    with f2:
        selected_steps = st.multiselect("Step", list(range(1, 8)), default=list(range(1, 8)), format_func=lambda x: f"S{x}: {get_step_info(x)['label'][:12]}")
    with f3:
        search = st.text_input("Search", placeholder="Name / Company…", key="search_leads")

    if not df.empty:
        view = df.copy()
        if selected_statuses:
            view = view[view["Status"].isin(selected_statuses)]
        if selected_steps:
            view = view[view["SequenceStep"].isin(selected_steps)]
        if search.strip():
            s = search.lower()
            view = view[view["ContactName"].str.lower().str.contains(s, na=False) | view["Company"].str.lower().str.contains(s, na=False)]
        display_cols = [c for c in ["LeadID", "ContactName", "Company", "Industry", "Status", "SequenceStep", "LastTouched", "LockedBy"] if c in view.columns]
        st.dataframe(view[display_cols].sort_values("SequenceStep"), use_container_width=True, height=360)
        st.caption(f"{len(view)} leads shown · {len(df.columns)} columns preserved in sheet")

    st.markdown("---")
    st.markdown("**EDIT LEAD**")
    if not df.empty:
        options = {f"{row['ContactName']} — {row['Company']} ({row['LeadID']})": row["LeadID"] for _, row in df.iterrows()}
        chosen = st.selectbox("Select Lead", ["— select —"] + list(options.keys()), key="edit_lead_sel")
        if chosen != "— select —":
            row = df[df["LeadID"] == options[chosen]].iloc[0]
            ec1, ec2 = st.columns(2)
            with ec1:
                edit_status = st.selectbox("Status", STATUSES, index=STATUSES.index(str(row.get("Status", "Cold"))), key="edit_status")
                edit_step = st.selectbox("Step", list(range(1, 8)), index=max(int(row.get("SequenceStep", 1)) - 1, 0), format_func=lambda x: f"{x}: {get_step_info(x)['label']}", key="edit_step")
            with ec2:
                edit_notes = st.text_area("Notes", value=str(row.get("Notes", "")), height=100, key="edit_notes")

            if st.button("💾 UPDATE LEAD", use_container_width=True):
                now_s = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                for col, val in [("Status", edit_status), ("SequenceStep", edit_step), ("Notes", edit_notes), ("LastTouched", now_s), ("LastTouchedBy", st.session_state.username)]:
                    df.loc[df["LeadID"] == options[chosen], col] = val
                if save_leads(df):
                    log_activity(options[chosen], str(row.get("ContactName", "")), "", "", f"Manual Update → {edit_status}", edit_notes)
                    st.success("Updated ✓")
                    st.rerun()


def tab_activity():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📋 TEAM ACTIVITY LOG</h2>', unsafe_allow_html=True)
    df = load_activity()
    if df.empty:
        st.info("No activity yet.")
        return

    now = datetime.now(timezone.utc)
    today = now.date()
    today_df = df[pd.to_datetime(df["Timestamp"], utc=True).dt.date == today]

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Actions", len(df))
    with k2:
        st.metric("Today's Actions", len(today_df))
    with k3:
        st.metric("Active Reps Today", today_df["Username"].nunique())
    with k4:
        st.metric("Dials Today", len(today_df[today_df["Channel"] == "Call"]) if "Channel" in today_df.columns else 0)
    with k5:
        st.metric("Emails Today", len(today_df[today_df["Channel"] == "Email"]) if "Channel" in today_df.columns else 0)

    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1:
        fu = st.selectbox("Operator", ["All"] + sorted(df["Username"].dropna().unique().tolist()), key="act_filter_user")
    with f2:
        fc = st.selectbox("Channel", ["All", "Call", "Email", "LinkedIn"], key="act_filter_ch")
    with f3:
        fo = st.text_input("Search outcome / notes", placeholder="e.g. voicemail", key="act_search")

    show = df.copy()
    if fu != "All":
        show = show[show["Username"] == fu]
    if fc != "All" and "Channel" in show.columns:
        show = show[show["Channel"] == fc]
    if fo.strip() and "Outcome" in show.columns:
        s = fo.lower()
        show = show[show["Outcome"].str.lower().str.contains(s, na=False) | show["Notes"].str.lower().str.contains(s, na=False)]

    show = show.sort_values("Timestamp", ascending=False).head(300)
    dcols = [c for c in ["Timestamp", "Username", "ContactName", "Channel", "Outcome", "Action", "Notes"] if c in show.columns]
    st.dataframe(show[dcols], use_container_width=True, height=500)


def tab_ai():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">🤖 AI MESSAGE WORKSHOP</h2>', unsafe_allow_html=True)
    st.caption("Draft messages for any lead — standalone, outside the live queue.")

    c1, c2 = st.columns(2)
    with c1:
        contact = st.text_input("Contact Name", key="ai_contact")
        company = st.text_input("Company", key="ai_company")
        industry = st.text_input("Industry", key="ai_industry")
    with c2:
        revenue = st.text_input("Revenue", key="ai_revenue")
        mtype = st.radio("Type", ["Follow-up Email", "LinkedIn Message"], horizontal=True, key="ai_type")
        notes = st.text_area("Context / Notes", height=80, key="ai_notes")

    if st.button("⚡ GENERATE DRAFT", use_container_width=True):
        if not contact or not company:
            st.error("Need at least a name and company.")
        else:
            row = {"ContactName": contact, "Company": company, "Industry": industry, "Revenue": revenue, "Notes": notes}
            draft_type = "email" if "Email" in mtype else "linkedin"
            with st.spinner("Generating…"):
                subj, body = generate_ai_draft(row, draft_type)
            if draft_type == "email":
                st.markdown(sl("SUBJECT"), unsafe_allow_html=True)
                st.code(subj)
            st.markdown(sl("BODY"), unsafe_allow_html=True)
            st.markdown(f'<div class="op-card" style="border-color:var(--teal);font-size:.9rem;white-space:pre-wrap;">{body}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LOGIN / SIDEBAR / MAIN
# ─────────────────────────────────────────────
def login_screen():
    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:70vh;gap:1rem;">'
        '<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:3rem;font-weight:800;letter-spacing:.15em;color:#00A7A7;text-transform:uppercase;">⚙ Master of Ops</div>'
        '<div style="font-size:.68rem;letter-spacing:.3em;color:#8899AA;text-transform:uppercase;margin-top:-.7rem;">Team Execution OS v3 — Auto-Dial Outbound Cockpit</div>'
        '<div style="height:1px;width:280px;background:#263040;margin:.5rem 0;"></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("**SELECT OPERATOR**")
        name = st.selectbox("", ["— choose —"] + TEAM_USERS, label_visibility="collapsed")
        custom = st.text_input("Or enter your name", placeholder="Your name…")
        if st.button("🔓 ENTER THE OPS FLOOR", use_container_width=True):
            chosen = custom.strip() if custom.strip() else name
            if chosen and chosen != "— choose —":
                st.session_state.username = chosen
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Pick a name to proceed.")


def render_sidebar():
    with st.sidebar:
        session_indicator = "🟢 SESSION ACTIVE" if st.session_state.dial_session else "⚫ No session"
        st.markdown(
            f'<div style="padding:1rem 0 1.3rem 0;border-bottom:1px solid var(--border);margin-bottom:.9rem;">'
            f'<div class="logo-mark">⚙ Master of Ops</div><div class="logo-sub">Execution OS v3.0</div></div>'
            f'<div style="font-size:.68rem;color:#8899AA;margin-bottom:.4rem;">Operator: <span style="color:#00A7A7;font-weight:600">{st.session_state.username}</span></div>'
            f'<div style="font-size:.68rem;color:#8899AA;margin-bottom:.8rem;">{session_indicator}</div>',
            unsafe_allow_html=True,
        )

        if st.button("⬅ Logout", use_container_width=True):
            if st.session_state.active_lead_id:
                df = load_leads()
                if not df.empty:
                    df = unlock_lead(df, st.session_state.active_lead_id)
                    save_leads(df)
            st.session_state.logged_in = False
            st.session_state.dial_session = False
            st.session_state.email_panel_open = False
            st.session_state.username = ""
            st.session_state.active_lead_id = None
            st.session_state.ai_draft = ""
            st.session_state.ai_subject = ""
            st.rerun()

        st.markdown("---")
        for line in [
            "⚙️ Setup → Go Live",
            "📞 Dial Queue → Cockpit",
            "📊 Analytics → KPIs",
            "📋 Manage → Import + Edit",
            "📋 Activity → Full Log",
            "🤖 AI Workshop",
        ]:
            st.markdown(f'<div style="font-size:.76rem;color:#8899AA;padding:.18rem 0;">{line}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div style="font-size:.58rem;color:#4A5A6A;line-height:1.7;text-align:center;">7-step sequence | Locks: 10 min<br>SMTP email | tel: dialer links<br>CSV/Excel import | URL columns<br>Cached Sheets reads</div>', unsafe_allow_html=True)


def main():
    if not st.session_state.logged_in:
        login_screen()
        return

    render_sidebar()
    tabs = st.tabs(["⚙️ SETUP", "📞 DIAL QUEUE", "📊 ANALYTICS", "📋 MANAGE LEADS", "📋 ACTIVITY LOG", "🤖 AI WORKSHOP"])
    with tabs[0]:
        tab_setup()
    with tabs[1]:
        tab_dial_queue()
    with tabs[2]:
        tab_analytics()
    with tabs[3]:
        tab_manage_leads()
    with tabs[4]:
        tab_activity()
    with tabs[5]:
        tab_ai()


if __name__ == "__main__":
    main()
