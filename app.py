"""
Master of Ops — Team Execution OS  v4.0
Auto-Dial Outbound Cockpit | All bugs fixed
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timezone, timedelta
import time, urllib.parse, random, smtplib, hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
:root{--bg:#0B0F14;--surface:#131920;--panel:#1A2330;--border:#263040;--teal:#00A7A7;--teal-dim:#007A7A;--amber:#F0A500;--red:#E05252;--green:#3DBA72;--purple:#9B72CF;--text:#FFFFFF;--muted:#8899AA;--radius:4px;}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:'IBM Plex Sans',sans-serif;}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}[data-testid="stToolbar"]{display:none;}
h1,h2,h3{font-family:'Barlow Condensed',sans-serif!important;letter-spacing:.05em;text-transform:uppercase;}
.op-card{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.3rem;margin-bottom:.5rem;}
.op-card-teal{border-left:3px solid var(--teal);}
.kpi-strip{display:flex;gap:.5rem;margin-bottom:1rem;flex-wrap:wrap;}
.kpi{flex:1;min-width:80px;background:var(--panel);border:1px solid var(--border);border-top:2px solid var(--teal);padding:.5rem .8rem;border-radius:var(--radius);text-align:center;}
.kpi.amber{border-top-color:var(--amber);}.kpi.red{border-top-color:var(--red);}.kpi.green{border-top-color:var(--green);}.kpi.purple{border-top-color:var(--purple);}
.kpi-val{font-family:'Barlow Condensed',sans-serif;font-size:1.6rem;font-weight:800;color:var(--teal);line-height:1;}
.kpi.amber .kpi-val{color:var(--amber);}.kpi.red .kpi-val{color:var(--red);}.kpi.green .kpi-val{color:var(--green);}.kpi.purple .kpi-val{color:var(--purple);}
.kpi-label{font-size:.55rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-top:.1rem;}
.lead-block{background:var(--panel);border:1px solid var(--teal);border-radius:var(--radius);padding:1rem 1.3rem;margin-bottom:.6rem;}
.lead-name{font-family:'Barlow Condensed',sans-serif;font-size:1.6rem;font-weight:800;letter-spacing:.05em;}
.lead-company{font-family:'DM Mono',monospace;font-size:.85rem;color:var(--teal);}
.badge{display:inline-block;padding:.1rem .5rem;border-radius:2px;font-size:.6rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-family:'Barlow Condensed',sans-serif;}
.badge-cold{background:#1E3A5F;color:#7AB8F5;}.badge-warm{background:#4A2E00;color:var(--amber);}.badge-hot{background:#4A1010;color:var(--red);}.badge-dnc{background:#2A2A2A;color:var(--muted);}
.ch-call{background:#0A2A2A;color:var(--teal);}.ch-email{background:#2A2A00;color:var(--amber);}.ch-li{background:#1A0A2A;color:var(--purple);}
.intel-grid{display:flex;flex-wrap:wrap;gap:.35rem;margin:.4rem 0;}
.intel-chip{background:var(--surface);border:1px solid var(--border);border-radius:3px;padding:.18rem .5rem;font-size:.68rem;color:#CCDDEE;}
.intel-chip span{color:var(--muted);font-size:.6rem;margin-right:.25rem;}
.step-bar{display:flex;gap:.25rem;margin:.4rem 0;align-items:center;}
.step-dot{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:.72rem;border:1px solid var(--border);color:var(--muted);background:var(--surface);}
.step-dot.active{background:var(--teal);border-color:var(--teal);color:#000;}.step-dot.done{background:var(--teal-dim);border-color:var(--teal-dim);color:#000;}
.step-line{flex:1;height:1px;background:var(--border);}
.dial-number{font-family:'DM Mono',monospace;font-size:1.5rem;font-weight:500;color:var(--teal);letter-spacing:.08em;margin:.3rem 0;}
.funnel-step{display:flex;align-items:center;gap:.7rem;padding:.5rem .8rem;margin:.15rem 0;border-radius:var(--radius);background:var(--panel);border:1px solid var(--border);}
.funnel-label{font-family:'Barlow Condensed',sans-serif;font-size:.85rem;font-weight:700;letter-spacing:.03em;min-width:155px;}
.funnel-bar-wrap{flex:1;height:6px;background:var(--border);border-radius:3px;}
.funnel-bar{height:6px;border-radius:3px;}
.funnel-pct{font-family:'DM Mono',monospace;font-size:.68rem;color:var(--muted);min-width:34px;text-align:right;}
.funnel-n{font-family:'DM Mono',monospace;font-size:.85rem;font-weight:500;min-width:28px;text-align:right;}
.lb-row{display:flex;align-items:center;gap:.6rem;padding:.45rem .8rem;border-bottom:1px solid var(--border);}
.lb-rank{font-family:'Barlow Condensed',sans-serif;font-size:1.2rem;font-weight:800;color:var(--muted);width:24px;text-align:center;}
.lb-rank.gold{color:#FFD700;}.lb-rank.silver{color:#C0C0C0;}.lb-rank.bronze{color:#CD7F32;}
.lb-name{flex:1;font-weight:500;font-size:.85rem;}
.lb-bar-wrap{width:90px;height:5px;background:var(--border);border-radius:3px;}
.lb-bar{height:5px;background:var(--teal);border-radius:3px;}
.lb-count{font-family:'DM Mono',monospace;font-size:.8rem;color:var(--teal);min-width:26px;text-align:right;}
.feed-row{display:flex;gap:.6rem;padding:.35rem 0;border-bottom:1px solid var(--border);font-size:.78rem;}
.session-banner{background:linear-gradient(90deg,#002A2A,#0A1A2A);border:1px solid var(--teal);border-radius:var(--radius);padding:.5rem 1rem;display:flex;align-items:center;justify-content:space-between;margin-bottom:.6rem;}
.session-active{font-family:'Barlow Condensed',sans-serif;font-size:.82rem;font-weight:700;letter-spacing:.12em;color:var(--teal);}
.session-pulse{display:inline-block;width:7px;height:7px;background:var(--green);border-radius:50%;margin-right:.4rem;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.3;}}
.setup-card{background:linear-gradient(135deg,#0A1A2A,#0B1E1E);border:1px solid var(--teal);border-radius:var(--radius);padding:1.5rem;margin:.8rem 0;}
.section-label{font-family:'Barlow Condensed',sans-serif;font-size:.65rem;letter-spacing:.2em;color:var(--muted);text-transform:uppercase;margin:.8rem 0 .3rem;}
.logo-mark{font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--teal);}
.logo-sub{font-size:.55rem;letter-spacing:.2em;color:var(--muted);text-transform:uppercase;}
.stTextInput input,.stTextArea textarea{background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;}
.stSelectbox div[data-baseweb="select"],.stMultiSelect div[data-baseweb="select"]{background:var(--surface)!important;border:1px solid var(--border)!important;}
.stSelectbox div[data-baseweb="select"] *,.stMultiSelect div[data-baseweb="select"] *{color:var(--text)!important;}
.stButton>button{background:var(--teal)!important;color:#000!important;border:none!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.82rem!important;letter-spacing:.08em!important;text-transform:uppercase!important;border-radius:var(--radius)!important;padding:.35rem .9rem!important;}
.stButton>button:hover{background:var(--teal-dim)!important;}
.stButton>button:disabled{background:var(--border)!important;color:var(--muted)!important;}
.stLinkButton a{background:var(--panel)!important;color:var(--teal)!important;border:1px solid var(--teal)!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.78rem!important;letter-spacing:.07em!important;text-transform:uppercase!important;border-radius:var(--radius)!important;padding:.28rem .85rem!important;}
[data-baseweb="tab-list"]{background:var(--surface)!important;border-bottom:1px solid var(--border)!important;gap:0!important;}
[data-baseweb="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-size:.85rem!important;letter-spacing:.06em!important;text-transform:uppercase!important;color:var(--muted)!important;background:transparent!important;border-radius:0!important;padding:.5rem 1rem!important;}
[aria-selected="true"][data-baseweb="tab"]{color:var(--teal)!important;border-bottom:2px solid var(--teal)!important;}
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:var(--radius)!important;}
hr{border-color:var(--border)!important;}
::-webkit-scrollbar{width:4px;height:4px;}::-webkit-scrollbar-track{background:var(--surface);}::-webkit-scrollbar-thumb{background:var(--teal-dim);border-radius:2px;}
@media(max-width:768px){.kpi-strip{flex-wrap:wrap;}.kpi{min-width:40%;}.lb-bar-wrap{display:none;}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SHEET_LEADS    = "Leads"
SHEET_ACTIVITY = "ActivityLog"
SHEET_USERS    = "Users"
SHEET_SETTINGS = "Settings"

SEQUENCE = [
    {"step":1,"channel":"Call",     "label":"Cold Call #1"},
    {"step":2,"channel":"Email",    "label":"Intro Email"},
    {"step":3,"channel":"LinkedIn", "label":"LinkedIn Connect"},
    {"step":4,"channel":"Call",     "label":"Follow-up Call"},
    {"step":5,"channel":"Email",    "label":"Value Email"},
    {"step":6,"channel":"LinkedIn", "label":"LinkedIn Message"},
    {"step":7,"channel":"Call",     "label":"Decision Call"},
]
CALL_OUTCOMES = ["Dialed – no answer","Dialed – voicemail","Connected – gatekeeper only","Connected – decision maker","Meeting set","Not interested","Wrong number"]
EMAIL_OUTCOMES = ["Sent","Replied","Bounced"]
LI_OUTCOMES    = ["Outreach done","Response received"]
CONNECTED_OUTS = {"Connected – decision maker","Connected – gatekeeper only","Meeting set"}
STATUSES       = ["Cold","Warm","Hot","DNC"]

# Default users — admin sees all, reps see own data
DEFAULT_USERS = [
    {"username":"admin",  "password":"ops2024!",  "role":"admin",  "display":"Ops Manager"},
    {"username":"rep1",   "password":"rep1pass",   "role":"rep",    "display":"Rep 1"},
    {"username":"rep2",   "password":"rep2pass",   "role":"rep",    "display":"Rep 2"},
    {"username":"rep3",   "password":"rep3pass",   "role":"rep",    "display":"Rep 3"},
    {"username":"rep4",   "password":"rep4pass",   "role":"rep",    "display":"Rep 4"},
]

CORE_LEAD_COLS = ["LeadID","ContactName","Company","Title","Phone","Email","Industry","Revenue","Status","SequenceStep","Notes","LastTouched","LastTouchedBy","LockedBy","LockTime"]
ACTIVITY_COLS  = ["ActivityID","Timestamp","Username","LeadID","ContactName","Channel","Outcome","Action","Notes"]

URL_COL_HINTS = ["linkedin","linkedin url","person linkedin","contact linkedin","company linkedin","website","company website","url","profile","li url","li profile"]

# All fields we try to surface as intel chips
INTEL_FIELD_MAP = [
    ("# Employees","Employees"),("Employees","Employees"),("Employee Count","Employees"),
    ("Annual Revenue","Revenue"),("Revenue","Revenue"),
    ("Industry","Industry"),
    ("City","City"),("State","State"),("Country","Country"),("Location","Location"),
    ("Keywords","Keywords"),("Tags","Tags"),
    ("Primary Intent Topic","Intent Topic"),("Intent Score","Intent Score"),
    ("Total Funding","Total Funding"),("Latest Funding","Latest Funding"),
    ("Founded Year","Founded"),("Company Type","Co. Type"),
    ("SIC Code","SIC"),("NAICS Code","NAICS"),
    ("Description","About"),("Short Description","About"),
]

COLUMN_MAP = {
    "full name":"ContactName","name":"ContactName","contact name":"ContactName","contact":"ContactName",
    "company":"Company","company name":"Company","organization":"Company","account name":"Company",
    "title":"Title","job title":"Title","position":"Title","role":"Title",
    "phone":"Phone","phone number":"Phone","mobile":"Phone","direct phone":"Phone","work phone":"Phone","phone 1":"Phone",
    "email":"Email","email address":"Email","work email":"Email","business email":"Email",
    "industry":"Industry","vertical":"Industry","sector":"Industry",
    "revenue":"Revenue","annual revenue":"Revenue","revenues":"Revenue",
}

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    for k,v in {
        "logged_in":False,"username":"","user_role":"rep","user_display":"",
        "active_lead_id":None,"ai_draft":"","ai_subject":"",
        "dial_session":False,"email_panel_open":False,
        "leads_cache":None,"leads_cache_ts":0,
        "skip_set":set(),
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
#  GOOGLE SHEETS — with aggressive caching to prevent quota exhaustion
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_conn()

# Cache leads in session to avoid repeated API calls
LEADS_CACHE_TTL = 8  # seconds between refreshes

def load_leads(force=False):
    now = time.time()
    if (not force
            and st.session_state.leads_cache is not None
            and (now - st.session_state.leads_cache_ts) < LEADS_CACHE_TTL):
        return st.session_state.leads_cache.copy()
    try:
        df = conn.read(worksheet=SHEET_LEADS, ttl=0)
        if df is None or df.empty or "LeadID" not in df.columns:
            df = pd.DataFrame(columns=CORE_LEAD_COLS)
        else:
            df["LeadID"]       = df["LeadID"].astype(str)
            df["SequenceStep"] = pd.to_numeric(df.get("SequenceStep",1), errors="coerce").fillna(1).astype(int)
            df["Status"]       = df["Status"].fillna("Cold")
            df["LastTouched"]  = pd.to_datetime(df["LastTouched"],  errors="coerce", utc=True)
            df["LockTime"]     = pd.to_datetime(df["LockTime"],     errors="coerce", utc=True)
            df["LockedBy"]     = df["LockedBy"].fillna("")
            df["Notes"]        = df["Notes"].fillna("")
        st.session_state.leads_cache    = df
        st.session_state.leads_cache_ts = now
        return df.copy()
    except Exception as e:
        st.error(f"Leads load error: {e}")
        return pd.DataFrame(columns=CORE_LEAD_COLS)

def invalidate_leads_cache():
    st.session_state.leads_cache    = None
    st.session_state.leads_cache_ts = 0

def load_activity():
    try:
        df = conn.read(worksheet=SHEET_ACTIVITY, ttl=30)
        if df is None or df.empty or "ActivityID" not in df.columns:
            return pd.DataFrame(columns=ACTIVITY_COLS)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", utc=True)
        return df
    except Exception:
        return pd.DataFrame(columns=ACTIVITY_COLS)

def save_leads(df):
    try:
        conn.update(worksheet=SHEET_LEADS, data=df)
        st.session_state.leads_cache    = df.copy()
        st.session_state.leads_cache_ts = time.time()
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

def log_activity(lead_id, contact_name, channel, outcome, action, notes=""):
    try:
        df = load_activity()
        row = {
            "ActivityID":  f"ACT-{int(time.time()*1000)}",
            "Timestamp":   datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Username":    st.session_state.username,
            "LeadID":      lead_id,
            "ContactName": contact_name,
            "Channel":     channel,
            "Outcome":     outcome,
            "Action":      action,
            "Notes":       notes,
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        conn.update(worksheet=SHEET_ACTIVITY, data=df)
    except Exception as e:
        st.warning(f"Log error: {e}")

def load_settings():
    """Load key-value settings from Settings sheet."""
    try:
        df = conn.read(worksheet=SHEET_SETTINGS, ttl=60)
        if df is None or df.empty or "key" not in df.columns:
            return {}
        return dict(zip(df["key"].astype(str), df["value"].astype(str)))
    except Exception:
        return {}

def save_settings(settings_dict):
    """Save settings dict to Settings sheet."""
    try:
        df = pd.DataFrame(list(settings_dict.items()), columns=["key","value"])
        conn.update(worksheet=SHEET_SETTINGS, data=df)
        return True
    except Exception as e:
        st.error(f"Settings save error: {e}")
        return False

def bootstrap_sheets():
    try:
        conn.update(worksheet=SHEET_LEADS,    data=pd.DataFrame(columns=CORE_LEAD_COLS))
        conn.update(worksheet=SHEET_ACTIVITY, data=pd.DataFrame(columns=ACTIVITY_COLS))
        conn.update(worksheet=SHEET_SETTINGS, data=pd.DataFrame(columns=["key","value"]))
        invalidate_leads_cache()
        return True, "Sheets initialised ✓"
    except Exception as e:
        return False, str(e)

def clear_demo_leads():
    """Remove any L-DEMO-* leads."""
    df = load_leads(force=True)
    if df.empty:
        return
    df = df[~df["LeadID"].str.startswith("L-DEMO-", na=False)]
    save_leads(df)

def seed_demo_data():
    companies = [
        ("Apex Precision Parts","Sarah Chen","VP Operations","(312) 555-0142","s.chen@apexprecision.com","Automotive","$5M-$20M"),
        ("Ironclad Fabrication","Marcus Webb","Plant Manager","(415) 555-0193","m.webb@ironclad.com","Metal Fab","$2M-$5M"),
        ("Summit Aerospace","Diana Patel","Dir of Procurement","(213) 555-0167","d.patel@summitaero.com","Aerospace","$20M-$50M"),
        ("CoreTech Manufacturing","James Okafor","COO","(312) 555-0188","j.okafor@coretech.com","Heavy Equipment","$50M+"),
        ("BlueLine Plastics","Rachel Torres","Supply Chain Lead","(617) 555-0154","r.torres@blueline.com","Plastics","$5M-$20M"),
        ("Forgemaster Industries","Tom Kramer","CEO","(503) 555-0171","t.kramer@forgemaster.com","Metal Fab","$20M-$50M"),
    ]
    reps     = ["rep1","rep2","rep3"]
    statuses = ["Cold","Warm","Hot","Cold","Warm","Cold"]
    steps    = [1,2,3,1,2,1]
    now      = datetime.now(timezone.utc)
    leads,acts = [],[]
    for i,((comp,contact,title,phone,email,ind,rev),status,step) in enumerate(zip(companies,statuses,steps)):
        lid = f"L-DEMO-{i+1:03d}"
        lts = (now-timedelta(days=random.randint(0,10))).strftime("%Y-%m-%dT%H:%M:%SZ")
        rep = reps[i%len(reps)]
        leads.append({"LeadID":lid,"ContactName":contact,"Company":comp,"Title":title,"Phone":phone,"Email":email,"Industry":ind,"Revenue":rev,"Status":status,"SequenceStep":step,"Notes":"Showed interest in Q3." if status!="Cold" else "","LastTouched":lts,"LastTouchedBy":rep,"LockedBy":"","LockTime":""})
        for j in range(random.randint(1,3)):
            ch=["Call","Email","LinkedIn"][j%3]
            out=CALL_OUTCOMES[j%len(CALL_OUTCOMES)] if ch=="Call" else (EMAIL_OUTCOMES[j%len(EMAIL_OUTCOMES)] if ch=="Email" else LI_OUTCOMES[j%len(LI_OUTCOMES)])
            acts.append({"ActivityID":f"ACT-D-{i*10+j}","Timestamp":(now-timedelta(days=random.randint(1,12))).strftime("%Y-%m-%dT%H:%M:%SZ"),"Username":reps[(i+j)%len(reps)],"LeadID":lid,"ContactName":contact,"Channel":ch,"Outcome":out,"Action":f"Step {j+1}","Notes":"Demo"})
    try:
        # Append to existing real leads
        existing = load_leads(force=True)
        if not existing.empty:
            combined = pd.concat([existing, pd.DataFrame(leads)], ignore_index=True)
            combined = combined.drop_duplicates(subset=["LeadID"], keep="last")
        else:
            combined = pd.DataFrame(leads)
        conn.update(worksheet=SHEET_LEADS,    data=combined)
        conn.update(worksheet=SHEET_ACTIVITY, data=pd.DataFrame(acts))
        invalidate_leads_cache()
        return True, f"Seeded {len(leads)} demo leads ✓"
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
def check_login(username, password):
    for u in DEFAULT_USERS:
        if u["username"].lower() == username.lower() and u["password"] == password:
            return u
    return None

# ─────────────────────────────────────────────
#  LEAD ROUTING & LOCKS
# ─────────────────────────────────────────────
def score_lead(row):
    now = datetime.now(timezone.utc)
    if row["Status"] == "DNC":
        return -9999
    lid = str(row.get("LeadID",""))
    if lid in st.session_state.get("skip_set", set()):
        return -9997
    lb = str(row.get("LockedBy","")).strip()
    lt = row.get("LockTime")
    if lb and lb != st.session_state.username:
        if pd.notna(lt) and (now-lt).total_seconds() < 600:
            return -9998
    last = row["LastTouched"]
    age  = (now-last).total_seconds()/86400 if pd.notna(last) else 30
    mult = {"Hot":3.0,"Warm":1.5,"Cold":1.0}.get(row["Status"],0.5)
    return (age*5 + (8-int(row["SequenceStep"]))*8) * mult

def get_next_lead(df):
    if df.empty: return None
    df = df.copy()
    df["_score"] = df.apply(score_lead, axis=1)
    df = df[df["_score"] > -9000]
    if df.empty: return None
    return df.sort_values("_score", ascending=False).iloc[0]

def lock_lead(df, lid):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    df.loc[df["LeadID"]==lid,"LockedBy"] = st.session_state.username
    df.loc[df["LeadID"]==lid,"LockTime"]  = now
    return df

def unlock_lead(df, lid):
    df.loc[df["LeadID"]==lid,"LockedBy"] = ""
    df.loc[df["LeadID"]==lid,"LockTime"]  = ""
    return df

def advance_lead(df, lid, new_status, new_notes, advance_step=True):
    now_s = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row   = df[df["LeadID"]==lid].iloc[0]
    if advance_step:
        nxt = min(int(row["SequenceStep"])+1, 7)
        df.loc[df["LeadID"]==lid,"SequenceStep"] = nxt
    df.loc[df["LeadID"]==lid,"Status"]        = new_status
    df.loc[df["LeadID"]==lid,"LastTouched"]   = now_s
    df.loc[df["LeadID"]==lid,"LastTouchedBy"] = st.session_state.username
    if new_notes.strip():
        existing = str(row.get("Notes","")).strip()
        if existing and existing != "nan":
            df.loc[df["LeadID"]==lid,"Notes"] = f"{existing}\n[{now_s[:10]}] {new_notes}".strip()
        else:
            df.loc[df["LeadID"]==lid,"Notes"] = f"[{now_s[:10]}] {new_notes}"
    df = unlock_lead(df, lid)
    return df

def do_next_lead():
    """Clear active lead so cockpit loads the next one."""
    st.session_state.active_lead_id   = None
    st.session_state.ai_draft         = ""
    st.session_state.ai_subject       = ""
    st.session_state.email_panel_open = False

# ─────────────────────────────────────────────
#  EMAIL
# ─────────────────────────────────────────────
def get_smtp_settings():
    """Read SMTP config from Settings sheet."""
    s = load_settings()
    return {
        "from_address": s.get("smtp_from",""),
        "smtp_host":    s.get("smtp_host","smtp.gmail.com"),
        "smtp_port":    int(s.get("smtp_port","587")),
        "smtp_user":    s.get("smtp_user",""),
        "smtp_password":s.get("smtp_password",""),
        "smtp_label":   s.get("smtp_label","Email"),
    }

def send_email_smtp(cfg, to_addr, subject, body):
    if not cfg["smtp_user"] or not cfg["smtp_password"]:
        return False, "SMTP not configured. Go to Setup → Email Config."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = cfg["from_address"] or cfg["smtp_user"]
        msg["To"]      = to_addr
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=15) as s:
            s.starttls()
            s.login(cfg["smtp_user"], cfg["smtp_password"])
            s.sendmail(msg["From"], [to_addr], msg.as_string())
        return True, "Email sent ✓"
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
#  GEMINI
# ─────────────────────────────────────────────
def generate_ai_draft(lead_row, draft_type):
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return "Subject: Quick follow-up", "Configure GEMINI_API_KEY in Streamlit secrets to enable AI drafts."
    try:
        genai.configure(api_key=key)
        model   = genai.GenerativeModel("gemini-1.5-flash")
        contact = lead_row.get("ContactName","there")
        company = lead_row.get("Company","the company")
        ind     = lead_row.get("Industry","manufacturing")
        rev     = lead_row.get("Revenue","unknown")
        notes   = str(lead_row.get("Notes","")).strip() or "no prior notes"
        if draft_type == "email":
            prompt = (f"Write a B2B follow-up sales email.\nLead: {contact} at {company} | Industry: {ind} | Revenue: {rev}\nPrior notes: {notes}\nRules: Professional, operator-first, zero jargon. MAX 3 sentence body. First line must be 'Subject: <subject>'. No fluff.")
        else:
            prompt = (f"Write a LinkedIn connection message for B2B outreach.\nLead: {contact} at {company} | Industry: {ind} | Revenue: {rev}\nPrior notes: {notes}\nRules: Human, witty but professional. MAX 3 sentences. No 'I hope this finds you well.'")
        text  = model.generate_content(prompt).text.strip()
        if draft_type == "email":
            lines = text.split("\n")
            subj  = lines[0].replace("Subject:","").strip() if lines[0].lower().startswith("subject:") else f"Following up — {company}"
            body  = "\n".join(lines[1:]).strip()
            return subj, body
        return "", text
    except Exception as e:
        return "Subject: Follow-up", f"AI error: {e}"

# ─────────────────────────────────────────────
#  CSV / EXCEL IMPORT HELPERS
# ─────────────────────────────────────────────
def detect_url_columns(df):
    url_cols = []
    for col in df.columns:
        cl = col.lower().strip()
        if any(h in cl for h in URL_COL_HINTS):
            url_cols.append(col)
        elif df[col].dtype == object:
            sample = df[col].dropna().head(10).astype(str)
            if sample.str.startswith("http").any():
                url_cols.append(col)
    return list(set(url_cols))

def map_import_df(raw_df):
    df = raw_df.copy()
    # Normalise column names for matching
    rename = {}
    first_col, last_col = None, None
    for col in df.columns:
        cl = col.lower().strip()
        if "first name" in cl or cl in ("first","firstname"):
            first_col = col
        elif "last name" in cl or cl in ("last","lastname"):
            last_col = col
        elif cl in COLUMN_MAP:
            rename[col] = COLUMN_MAP[cl]
    df = df.rename(columns=rename)
    # Handle first+last → ContactName
    if "ContactName" not in df.columns:
        if first_col and last_col:
            df["ContactName"] = (df[first_col].fillna("").astype(str).str.strip() + " " + df[last_col].fillna("").astype(str).str.strip()).str.strip()
        elif first_col:
            df["ContactName"] = df[first_col].fillna("").astype(str).str.strip()
        elif last_col:
            df["ContactName"] = df[last_col].fillna("").astype(str).str.strip()
    # Ensure all core columns exist
    for col in CORE_LEAD_COLS:
        if col not in df.columns:
            df[col] = ""
    # Generate missing LeadIDs
    for i,row in df.iterrows():
        val = str(row.get("LeadID","")).strip()
        if not val or val == "nan":
            df.at[i,"LeadID"] = f"L-{int(time.time()*1000)}-{i}"
    df["Status"]       = df["Status"].replace("", pd.NA).fillna("Cold")
    df["SequenceStep"] = pd.to_numeric(df["SequenceStep"], errors="coerce").fillna(1).astype(int)
    df["Notes"]        = df["Notes"].fillna("")
    df["LockedBy"]     = df["LockedBy"].fillna("")
    df["LockTime"]     = df["LockTime"].fillna("")
    return df

# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────
def sl(txt):
    return f'<div class="section-label">{txt}</div>'

def status_badge(s):
    cls = {"Cold":"badge-cold","Warm":"badge-warm","Hot":"badge-hot","DNC":"badge-dnc"}.get(s,"badge-cold")
    return f'<span class="badge {cls}">{s}</span>'

def channel_badge(ch):
    cls   = {"Call":"ch-call","Email":"ch-email","LinkedIn":"ch-li"}.get(ch,"ch-call")
    icons = {"Call":"📞","Email":"✉️","LinkedIn":"🔗"}
    return f'<span class="badge {cls}">{icons.get(ch,"")} {ch}</span>'

def step_indicator(current_step):
    icons = {"Call":"📞","Email":"✉️","LinkedIn":"🔗"}
    parts = []
    for s in SEQUENCE:
        n   = s["step"]
        cls = "done" if n<current_step else ("active" if n==current_step else "")
        parts.append(f'<div class="step-dot {cls}" title="Step {n}: {s["label"]}">{icons.get(s["channel"],"·")}</div>')
        if n < 7: parts.append('<div class="step-line"></div>')
    st.markdown(f'<div class="step-bar">{"".join(parts)}</div>', unsafe_allow_html=True)

def get_step_info(n):
    for s in SEQUENCE:
        if s["step"] == n: return s
    return {"step":n,"channel":"Call","label":f"Step {n}"}

def kpi_tile(val, label, cls=""):
    return f'<div class="kpi {cls}"><div class="kpi-val">{val}</div><div class="kpi-label">{label}</div></div>'

def render_intel_panel(row):
    chips, seen = [], set()
    for src, label in INTEL_FIELD_MAP:
        if src in row.index:
            val = str(row.get(src,"")).strip()
            if val and val not in ("nan","","None") and label not in seen:
                chips.append(f'<div class="intel-chip"><span>{label}</span>{val[:80]}</div>')
                seen.add(label)
    if not chips: return
    st.markdown(sl("COMPANY INTEL"), unsafe_allow_html=True)
    st.markdown(f'<div class="intel-grid">{"".join(chips)}</div>', unsafe_allow_html=True)

def render_url_buttons(row):
    url_cols = detect_url_columns(pd.DataFrame([row]))
    links = []
    for col in url_cols:
        val = str(row.get(col,"")).strip()
        if not val or val in ("nan","None",""): continue
        if not val.startswith("http"): val = "https://"+val
        cl = col.lower()
        if "person" in cl or ("linkedin" in cl and "company" not in cl):
            links.append(("👤 Contact LinkedIn", val))
        elif "company" in cl and "linkedin" in cl:
            links.append(("🏢 Company LinkedIn", val))
        elif "website" in cl or "web" in cl:
            links.append(("🌐 Website", val))
        else:
            links.append((f"🔗 {col[:20]}", val))
    if not links: return
    st.markdown(sl("QUICK LINKS"), unsafe_allow_html=True)
    cols = st.columns(min(len(links),3))
    for i,(label,url) in enumerate(links[:3]):
        with cols[i]:
            st.link_button(label, url, use_container_width=True)

# ─────────────────────────────────────────────
#  LOGIN SCREEN
# ─────────────────────────────────────────────
def login_screen():
    st.markdown('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:70vh;gap:1rem;"><div style="font-family:\'Barlow Condensed\',sans-serif;font-size:3rem;font-weight:800;letter-spacing:.15em;color:#00A7A7;text-transform:uppercase;">⚙ Master of Ops</div><div style="font-size:.65rem;letter-spacing:.3em;color:#8899AA;text-transform:uppercase;margin-top:-.6rem;">Outbound Sales OS — v4.0</div><div style="height:1px;width:260px;background:#263040;margin:.5rem 0;"></div></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        st.markdown("**USERNAME**")
        uname = st.text_input("", placeholder="username", label_visibility="collapsed", key="login_user")
        st.markdown("**PASSWORD**")
        pwd   = st.text_input("", placeholder="password", type="password", label_visibility="collapsed", key="login_pwd")
        if st.button("🔓 ENTER", use_container_width=True, key="btn_login"):
            user = check_login(uname, pwd)
            if user:
                st.session_state.logged_in    = True
                st.session_state.username     = user["username"]
                st.session_state.user_role    = user["role"]
                st.session_state.user_display = user["display"]
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.markdown('<div style="font-size:.65rem;color:#4A5A6A;margin-top:.5rem;">Default: admin / ops2024! &nbsp;|&nbsp; rep1–rep4 / rep1pass–rep4pass</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        sess = "🟢 SESSION" if st.session_state.dial_session else "⚫ Idle"
        role_badge = "👑 Admin" if st.session_state.user_role == "admin" else "🎯 Rep"
        st.markdown(f'<div style="padding:.8rem 0 1.1rem 0;border-bottom:1px solid var(--border);margin-bottom:.8rem;"><div class="logo-mark">⚙ Master of Ops</div><div class="logo-sub">Execution OS v4.0</div></div><div style="font-size:.65rem;color:#8899AA;margin-bottom:.3rem;">{role_badge} — <span style="color:#00A7A7;font-weight:600">{st.session_state.user_display}</span></div><div style="font-size:.62rem;color:#4A5A6A;margin-bottom:.7rem;">{sess}</div>', unsafe_allow_html=True)
        if st.button("⬅ Logout", use_container_width=True, key="btn_logout"):
            if st.session_state.active_lead_id:
                df = load_leads()
                if not df.empty:
                    df = unlock_lead(df, st.session_state.active_lead_id)
                    save_leads(df)
            for k in ["logged_in","dial_session","email_panel_open"]:
                st.session_state[k] = False
            for k in ["username","user_role","user_display","active_lead_id","ai_draft","ai_subject"]:
                st.session_state[k] = "" if k != "active_lead_id" else None
            st.session_state.skip_set = set()
            st.rerun()
        st.markdown("---")
        for line in ["⚙️ Setup","📞 Dial Queue","📊 Analytics","📋 Manage Leads","📋 Activity Log","🤖 AI Workshop"]:
            st.markdown(f'<div style="font-size:.73rem;color:#8899AA;padding:.15rem 0;">{line}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div style="font-size:.55rem;color:#4A5A6A;text-align:center;line-height:1.6;">7-step sequence | 10min locks<br>SMTP email | tel: dialer | CSV import</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TAB: SETUP
# ─────────────────────────────────────────────
def tab_setup():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.3rem;">⚙️ SYSTEM SETUP</h2>', unsafe_allow_html=True)

    # ── EMAIL CONFIGURATION ───────────────────────────────────
    st.markdown(sl("✉️ EMAIL CONFIGURATION"), unsafe_allow_html=True)
    st.markdown('<div class="op-card">', unsafe_allow_html=True)
    settings = load_settings()

    ec1, ec2 = st.columns(2)
    with ec1:
        email_type = st.selectbox("Email Provider", ["Gmail","Custom Domain / SMTP"], key="setup_email_type")
        from_addr  = st.text_input("From Address", value=settings.get("smtp_from",""), placeholder="you@gmail.com", key="setup_from")
        smtp_label = st.text_input("Identity Label", value=settings.get("smtp_label","Work Email"), placeholder="e.g. Gmail or Ops Email", key="setup_label")
    with ec2:
        if email_type == "Gmail":
            smtp_host = "smtp.gmail.com"
            smtp_port = 587
            st.info("Gmail: use an **App Password** (not your login password). Enable 2FA → Google Account → Security → App Passwords.")
        else:
            smtp_host = st.text_input("SMTP Host", value=settings.get("smtp_host","mail.yourdomain.com"), key="setup_host")
            smtp_port = st.number_input("SMTP Port", value=int(settings.get("smtp_port",587)), key="setup_port")
        smtp_user = st.text_input("SMTP Username", value=settings.get("smtp_user",""), key="setup_user")
        smtp_pwd  = st.text_input("SMTP Password / App Password", value=settings.get("smtp_password",""), type="password", key="setup_pwd")

    if st.button("💾 SAVE EMAIL CONFIG", use_container_width=True, key="btn_save_email"):
        new_settings = dict(settings)
        new_settings.update({
            "smtp_from":     from_addr,
            "smtp_host":     smtp_host if email_type != "Gmail" else "smtp.gmail.com",
            "smtp_port":     str(smtp_port if email_type != "Gmail" else 587),
            "smtp_user":     smtp_user,
            "smtp_password": smtp_pwd,
            "smtp_label":    smtp_label,
        })
        if save_settings(new_settings):
            st.success("Email config saved ✓")

    # Test send
    st.markdown(sl("TEST EMAIL"), unsafe_allow_html=True)
    test_to = st.text_input("Send test to", placeholder="your@email.com", key="setup_test_to")
    if st.button("📤 SEND TEST EMAIL", use_container_width=True, key="btn_test_email"):
        cfg = get_smtp_settings()
        ok, msg = send_email_smtp(cfg, test_to, "Master of Ops — Test Email", "This is a test email from your Master of Ops outbound system.")
        (st.success if ok else st.error)(msg)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── SHEET SETUP ────────────────────────────────────────────
    st.markdown(sl("GOOGLE SHEETS SETUP"), unsafe_allow_html=True)
    steps_data = [
        ("01","GOOGLE SHEET","#00A7A7",'Create a blank Google Sheet. Add four tabs named exactly: <code>Leads</code>, <code>ActivityLog</code>, <code>Settings</code>, <code>Users</code>.'),
        ("02","GCP SERVICE ACCOUNT","#F0A500","Enable Sheets API + Drive API. IAM → Service Accounts → Create → Download JSON key."),
        ("03","SHARE SHEET","#3DBA72","Share your Sheet with the service account email as <strong>Editor</strong>."),
        ("04","STREAMLIT SECRETS","#9B72CF","""Paste into App Settings → Secrets:<pre style="background:#0B0F14;padding:.6rem;border-radius:4px;font-size:.65rem;color:#00A7A7;overflow-x:auto;">[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_ID/edit"
type = "service_account"
project_id = "..."   private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\nKEY\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "name@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
GEMINI_API_KEY = "your-key-from-aistudio.google.com"</pre>"""),
    ]
    for num,title,color,body in steps_data:
        st.markdown(f'<div style="display:flex;gap:.8rem;margin:.4rem 0;padding:.8rem;background:var(--panel);border:1px solid var(--border);border-left:3px solid {color};border-radius:4px;"><div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.7rem;font-weight:800;color:{color};min-width:34px;line-height:1;">{num}</div><div><div style="font-family:\'Barlow Condensed\',sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.09em;color:{color};margin-bottom:.25rem;">{title}</div><div style="font-size:.76rem;color:#CCDDEE;line-height:1.6;">{body}</div></div></div>', unsafe_allow_html=True)

    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown("**Bootstrap**"); st.caption("Init all 4 sheets.")
        if st.button("🚀 BOOTSTRAP", use_container_width=True, key="btn_bootstrap"):
            ok,msg = bootstrap_sheets()
            (st.success if ok else st.error)(msg)
    with c2:
        st.markdown("**Seed Demo**"); st.caption("Add 6 demo leads.")
        if st.button("🧪 SEED DEMO", use_container_width=True, key="btn_seed"):
            ok,msg = seed_demo_data()
            (st.success if ok else st.error)(msg)
    with c3:
        st.markdown("**Clear Demo**"); st.caption("Remove demo leads.")
        if st.button("🗑 CLEAR DEMO", use_container_width=True, key="btn_clear_demo"):
            clear_demo_leads()
            st.success("Demo leads removed ✓")
    with c4:
        st.markdown("**Test Connection**"); st.caption("Verify sheet access.")
        if st.button("🔌 TEST", use_container_width=True, key="btn_test_conn"):
            df = load_leads(force=True)
            st.success(f"Connected ✓ — {len(df)} leads found.")

    st.markdown("---")
    st.markdown(sl("7-STEP SEQUENCE"), unsafe_allow_html=True)
    seq_html = "".join([f'<div style="display:flex;gap:.6rem;padding:.35rem .7rem;border-bottom:1px solid var(--border);font-size:.78rem;align-items:center;"><span style="font-family:\'DM Mono\',monospace;color:var(--muted);min-width:18px;">{s["step"]}</span>{channel_badge(s["channel"])}<span style="color:#CCDDEE;">{s["label"]}</span></div>' for s in SEQUENCE])
    st.markdown(f'<div class="op-card" style="padding:0;">{seq_html}</div>', unsafe_allow_html=True)
    st.caption("Edit the SEQUENCE list at the top of app.py to customise steps.")

    # User reference
    st.markdown("---")
    st.markdown(sl("DEFAULT USER ACCOUNTS"), unsafe_allow_html=True)
    rows = "".join([f'<div style="display:flex;gap:1rem;padding:.3rem .7rem;border-bottom:1px solid var(--border);font-size:.75rem;"><span style="color:#00A7A7;min-width:80px;">{u["username"]}</span><span style="color:var(--muted);min-width:90px;">{u["password"]}</span><span style="color:#CCDDEE;min-width:70px;">{u["role"].upper()}</span><span style="color:#8899AA;">{u["display"]}</span></div>' for u in DEFAULT_USERS])
    st.markdown(f'<div class="op-card" style="padding:0;">{rows}</div>', unsafe_allow_html=True)
    st.caption("Change passwords by editing DEFAULT_USERS at the top of app.py and redeploying.")

# ─────────────────────────────────────────────
#  TAB: DIAL QUEUE (COCKPIT)
# ─────────────────────────────────────────────
def tab_dial_queue():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.3rem;">📞 DIAL QUEUE — OUTBOUND COCKPIT</h2>', unsafe_allow_html=True)

    df = load_leads()

    # Filter to real leads only (exclude pure-demo if desired, but show all real)
    real_df = df[~df["LeadID"].str.startswith("L-DEMO-", na=False)] if not df.empty else df

    total  = len(df)
    hot    = int((df["Status"]=="Hot").sum())   if not df.empty else 0
    warm   = int((df["Status"]=="Warm").sum())  if not df.empty else 0
    active = int((df["Status"]!="DNC").sum())   if not df.empty else 0

    st.markdown(f'<div class="kpi-strip">{kpi_tile(total,"Total Leads")}{kpi_tile(warm,"Warm","amber")}{kpi_tile(hot,"Hot 🔥","red")}{kpi_tile(active,"In Queue","green")}</div>', unsafe_allow_html=True)

    if df.empty:
        st.info("No leads. Import leads in **Manage Leads** or seed demo data from **Setup**.")
        return

    # ── Session gate ──────────────────────────────────────────
    if not st.session_state.dial_session:
        if st.button("▶  START AUTO DIAL SESSION", use_container_width=True, key="btn_start"):
            st.session_state.dial_session     = True
            st.session_state.active_lead_id   = None
            st.session_state.ai_draft         = ""
            st.session_state.ai_subject       = ""
            st.session_state.email_panel_open = False
            st.session_state.skip_set         = set()
            invalidate_leads_cache()
            st.rerun()
        st.caption("Loads leads one by one. Save each call → next lead appears automatically.")
        return

    # ── Banner ────────────────────────────────────────────────
    cb, cs = st.columns([4,1])
    with cb:
        st.markdown('<div class="session-banner"><span><span class="session-pulse"></span><span class="session-active">AUTO DIAL SESSION ACTIVE</span></span><span style="font-size:.68rem;color:var(--muted);">Save or skip each lead → next loads automatically</span></div>', unsafe_allow_html=True)
    with cs:
        if st.button("■ STOP", use_container_width=True, key="btn_stop"):
            if st.session_state.active_lead_id:
                df2 = load_leads(force=True)
                if not df2.empty:
                    df2 = unlock_lead(df2, st.session_state.active_lead_id)
                    save_leads(df2)
            st.session_state.dial_session = False
            do_next_lead()
            st.rerun()

    # ── Get next lead ─────────────────────────────────────────
    fresh_df = load_leads()
    lead = None
    if st.session_state.active_lead_id:
        matches = fresh_df[fresh_df["LeadID"]==st.session_state.active_lead_id]
        if not matches.empty:
            lead = matches.iloc[0]
    if lead is None:
        lead = get_next_lead(fresh_df)
        if lead is None:
            st.success("✅ Queue clear — all leads actioned or skipped this session.")
            st.session_state.dial_session = False
            return
        # Lock new lead
        fresh_df = lock_lead(fresh_df, lead["LeadID"])
        save_leads(fresh_df)
        st.session_state.active_lead_id   = lead["LeadID"]
        st.session_state.ai_draft         = ""
        st.session_state.ai_subject       = ""
        step_ch = get_step_info(int(lead["SequenceStep"]))["channel"]
        st.session_state.email_panel_open = (step_ch == "Email")
        lead = fresh_df[fresh_df["LeadID"]==lead["LeadID"]].iloc[0]

    lead_id  = lead["LeadID"]
    step_num = int(lead["SequenceStep"])
    step_info= get_step_info(step_num)
    channel  = step_info["channel"]
    status   = lead["Status"]

    # ── COCKPIT LAYOUT ────────────────────────────────────────
    col_main, col_intel = st.columns([3, 2])

    with col_main:
        # Lead header
        st.markdown(f'<div class="lead-block"><div class="lead-company">{lead.get("Company","—")}</div><div class="lead-name">{lead.get("ContactName","—")}</div><div style="color:var(--muted);font-size:.78rem;margin:.15rem 0;">{lead.get("Title","—")}</div><div style="margin-top:.4rem;display:flex;gap:.4rem;flex-wrap:wrap;align-items:center;">{status_badge(status)}{channel_badge(channel)}<span style="font-family:\'DM Mono\',monospace;font-size:.68rem;color:var(--muted);">Step {step_num}/7: {step_info["label"]}</span></div></div>', unsafe_allow_html=True)
        step_indicator(step_num)

        # ── CALL PANEL ────────────────────────────────────────
        if channel == "Call":
            phone   = str(lead.get("Phone","")).strip()
            tel_raw = "".join(c for c in phone if c.isdigit() or c=="+")
            tel_url = f"tel:{tel_raw}" if tel_raw else "#"

            st.markdown(sl("📞 DIAL"), unsafe_allow_html=True)
            st.markdown(f'<div class="op-card"><div class="dial-number">{phone or "No phone on file"}</div><div style="font-size:.68rem;color:var(--muted);">Tap Dial Now → your phone app opens with this number pre-loaded. Make the call, return here, log the outcome.</div></div>', unsafe_allow_html=True)

            if phone:
                st.link_button(f"📲 DIAL NOW — {phone}", tel_url, use_container_width=True)
            else:
                st.warning("No phone number. Update in Manage Leads.")

            st.markdown(sl("LOG OUTCOME"), unsafe_allow_html=True)
            call_out   = st.selectbox("Outcome *", ["— select outcome —"]+CALL_OUTCOMES, key=f"call_out_{lead_id}")
            call_notes = st.text_area("Notes *", placeholder="What happened? Objections? Intel? Even 'No answer' is valid.", height=75, key=f"call_notes_{lead_id}")
            new_status = st.selectbox("Update Status", STATUSES, index=STATUSES.index(status), key=f"call_status_{lead_id}")

            can_save = (call_out != "— select outcome —" and call_notes.strip())
            if st.button("✅ SAVE CALL & NEXT LEAD", use_container_width=True, key=f"btn_save_call_{lead_id}"):
                if not can_save:
                    st.warning("Select an outcome and add a note first.")
                else:
                    df2 = load_leads(force=True)
                    df2 = advance_lead(df2, lead_id, new_status, call_notes)
                    if save_leads(df2):
                        log_activity(lead_id, str(lead.get("ContactName","")), "Call", call_out, f"Step {step_num}: {step_info['label']}", call_notes)
                        do_next_lead()
                        st.success("✓ Logged — loading next lead…")
                        time.sleep(0.4)
                        st.rerun()

        # ── LINKEDIN PANEL ────────────────────────────────────
        elif channel == "LinkedIn":
            st.markdown(sl("🔗 LINKEDIN"), unsafe_allow_html=True)
            li_notes = st.text_input("Note (optional)", placeholder="e.g. Sent connection request", key=f"li_notes_{lead_id}")
            lc1, lc2 = st.columns(2)
            with lc1:
                if st.button("✅ OUTREACH DONE", use_container_width=True, key=f"btn_li_done_{lead_id}"):
                    df2 = load_leads(force=True)
                    df2 = advance_lead(df2, lead_id, status, li_notes or "LinkedIn outreach done")
                    if save_leads(df2):
                        log_activity(lead_id, str(lead.get("ContactName","")), "LinkedIn","Outreach done",f"Step {step_num}: {step_info['label']}",li_notes)
                        do_next_lead(); st.success("✓"); time.sleep(0.4); st.rerun()
            with lc2:
                if st.button("💬 RESPONSE RECEIVED", use_container_width=True, key=f"btn_li_resp_{lead_id}"):
                    df2 = load_leads(force=True)
                    df2 = advance_lead(df2, lead_id, "Warm", li_notes or "LinkedIn response received")
                    if save_leads(df2):
                        log_activity(lead_id, str(lead.get("ContactName","")), "LinkedIn","Response received",f"Step {step_num}: {step_info['label']}",li_notes)
                        do_next_lead(); st.success("✓ → Warm"); time.sleep(0.4); st.rerun()

        # ── EMAIL PANEL ───────────────────────────────────────
        if channel == "Email" or st.session_state.email_panel_open:
            st.markdown(sl("✉️ EMAIL"), unsafe_allow_html=True)
            cfg = get_smtp_settings()

            if not cfg["smtp_user"]:
                st.warning("Email not configured. Go to **Setup → Email Config** to add SMTP credentials. You can still log email manually below.")
            else:
                if not st.session_state.ai_subject:
                    with st.spinner("Drafting…"):
                        subj, body = generate_ai_draft(lead, "email")
                        st.session_state.ai_subject = subj
                        st.session_state.ai_draft   = body

                to_addr = st.text_input("To",      value=str(lead.get("Email","")), key=f"email_to_{lead_id}")
                subject = st.text_input("Subject", value=st.session_state.ai_subject, key=f"email_subj_{lead_id}")
                body_in = st.text_area("Body",     value=st.session_state.ai_draft, height=120, key=f"email_body_{lead_id}")

                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("📤 SEND EMAIL", use_container_width=True, key=f"btn_send_{lead_id}"):
                        if not to_addr.strip():
                            st.error("Email address required.")
                        else:
                            ok, msg = send_email_smtp(cfg, to_addr, subject, body_in)
                            if ok:
                                df2 = load_leads(force=True)
                                df2 = advance_lead(df2, lead_id, status, f"Email sent: {subject}")
                                save_leads(df2)
                                log_activity(lead_id, str(lead.get("ContactName","")), "Email","Sent",f"Step {step_num}: {step_info['label']}",f"Subject: {subject}")
                                st.success(msg)
                                do_next_lead(); time.sleep(0.4); st.rerun()
                            else:
                                st.error(f"Send failed: {msg}")
                                st.info("💡 Check your SMTP credentials in Setup. For Gmail, use an App Password (not your login password).")
                with ec2:
                    if st.button("📝 LOG SENT (MANUAL)", use_container_width=True, key=f"btn_log_email_{lead_id}"):
                        df2 = load_leads(force=True)
                        df2 = advance_lead(df2, lead_id, status, f"Email sent: {st.session_state.ai_subject or 'manual log'}")
                        save_leads(df2)
                        log_activity(lead_id, str(lead.get("ContactName","")), "Email","Sent",f"Step {step_num}: {step_info['label']}","Manual log")
                        do_next_lead(); st.success("✓ Logged"); time.sleep(0.4); st.rerun()

            # Quick mark buttons — always visible
            st.markdown(sl("MARK PRIOR EMAIL"), unsafe_allow_html=True)
            rb1, rb2 = st.columns(2)
            with rb1:
                if st.button("↩ MARK REPLIED", use_container_width=True, key=f"btn_replied_{lead_id}"):
                    log_activity(lead_id, str(lead.get("ContactName","")), "Email","Replied","Manual mark","")
                    do_next_lead(); st.success("Replied logged."); time.sleep(0.4); st.rerun()
            with rb2:
                if st.button("⛔ MARK BOUNCED", use_container_width=True, key=f"btn_bounced_{lead_id}"):
                    log_activity(lead_id, str(lead.get("ContactName","")), "Email","Bounced","Manual mark","")
                    st.success("Bounce logged.")

        # ── Email toggle (for non-email steps) ────────────────
        if channel != "Email" and not st.session_state.email_panel_open:
            if st.button("✉ ALSO SEND EMAIL", use_container_width=True, key=f"btn_toggle_email_{lead_id}"):
                st.session_state.email_panel_open = True
                st.rerun()

        # ── Skip / DNC ────────────────────────────────────────
        st.markdown("---")
        sk1, sk2 = st.columns(2)
        with sk1:
            if st.button("⏭ SKIP THIS LEAD", use_container_width=True, key=f"btn_skip_{lead_id}"):
                st.session_state.skip_set.add(lead_id)
                df2 = load_leads(force=True)
                df2 = unlock_lead(df2, lead_id)
                save_leads(df2)
                do_next_lead()
                st.rerun()
        with sk2:
            if st.button("🚫 MARK DNC", use_container_width=True, key=f"btn_dnc_{lead_id}"):
                df2 = load_leads(force=True)
                df2.loc[df2["LeadID"]==lead_id,"Status"] = "DNC"
                df2 = unlock_lead(df2, lead_id)
                save_leads(df2)
                log_activity(lead_id, str(lead.get("ContactName","")), "Call","Not interested","DNC marked","")
                do_next_lead(); st.rerun()

    # ── RIGHT: Intel column ───────────────────────────────────
    with col_intel:
        st.markdown(sl("CONTACT"), unsafe_allow_html=True)
        phone_val = str(lead.get("Phone","—"))
        email_val = str(lead.get("Email","—"))
        comp_val  = str(lead.get("Company","—"))
        st.markdown(f'<div class="op-card" style="font-size:.8rem;line-height:1.85;"><div style="color:var(--muted);font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;">Phone</div><div style="font-family:\'DM Mono\',monospace;color:var(--teal);font-size:.95rem;margin-bottom:.5rem;">{phone_val}</div><div style="color:var(--muted);font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;">Email</div><div style="font-family:\'DM Mono\',monospace;font-size:.75rem;margin-bottom:.5rem;">{email_val}</div><div style="color:var(--muted);font-size:.6rem;text-transform:uppercase;letter-spacing:.1em;">Company</div><div style="font-size:.82rem;">{comp_val}</div></div>', unsafe_allow_html=True)

        render_intel_panel(lead)
        render_url_buttons(lead)

        # Company news
        company_enc = urllib.parse.quote_plus(str(lead.get("Company","")))
        st.link_button("📰 COMPANY NEWS", f"https://www.google.com/search?q={company_enc}+news&tbm=nws", use_container_width=True)

        # Prior notes
        notes_val = str(lead.get("Notes","")).strip()
        if notes_val and notes_val != "nan":
            st.markdown(sl("PRIOR NOTES"), unsafe_allow_html=True)
            st.markdown(f'<div class="op-card op-card-teal" style="font-size:.78rem;white-space:pre-wrap;max-height:160px;overflow-y:auto;">{notes_val}</div>', unsafe_allow_html=True)

        # LinkedIn AI draft
        if channel == "LinkedIn":
            st.markdown(sl("AI DRAFT"), unsafe_allow_html=True)
            if not st.session_state.ai_draft:
                if st.button("⚡ GENERATE DRAFT", use_container_width=True, key=f"btn_li_draft_{lead_id}"):
                    with st.spinner("Drafting…"):
                        _, body = generate_ai_draft(lead, "linkedin")
                        st.session_state.ai_draft = body
            if st.session_state.ai_draft:
                st.markdown(f'<div class="op-card" style="border-color:var(--purple);font-size:.78rem;white-space:pre-wrap;">{st.session_state.ai_draft}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TAB: ANALYTICS
# ─────────────────────────────────────────────
def tab_analytics():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.3rem;">📊 OPS ANALYTICS</h2>', unsafe_allow_html=True)

    leads_df = load_leads()
    act_df   = load_activity()
    now      = datetime.now(timezone.utc)
    today    = now.date()

    # Admin sees all, rep sees own
    is_admin = (st.session_state.user_role == "admin")

    if not act_df.empty:
        if not is_admin:
            act_df = act_df[act_df["Username"] == st.session_state.username]

    if leads_df.empty and act_df.empty:
        st.info("No data yet. Go to Setup → Seed Demo, or import leads.")
        return

    cf1, cf2, _ = st.columns([1,1,3])
    with cf1:
        rng = st.selectbox("Time Range", ["Today","Last 7 days","Last 14 days","Last 30 days","All time"], key="ana_range")
    cutoff_map = {"Today":1,"Last 7 days":7,"Last 14 days":14,"Last 30 days":30,"All time":3650}
    cutoff = now - timedelta(days=cutoff_map[rng]) if rng != "Today" else now.replace(hour=0,minute=0,second=0,microsecond=0)

    act = act_df.copy()
    if not act.empty and "Timestamp" in act.columns:
        act = act[act["Timestamp"] >= cutoff]

    def ch_out(ch, out_filter=None):
        if act.empty or "Channel" not in act.columns: return 0
        sub = act[act["Channel"]==ch]
        if out_filter: sub = sub[sub["Outcome"].isin(out_filter)]
        return len(sub)

    dials        = ch_out("Call")
    contacts     = ch_out("Call", CONNECTED_OUTS)
    contact_rate = round(contacts/dials*100 if dials else 0,1)
    meetings     = ch_out("Call", {"Meeting set"})
    emails_sent  = ch_out("Email",{"Sent"})
    email_reply  = ch_out("Email",{"Replied"})
    email_bounce = ch_out("Email",{"Bounced"})
    bounce_rate  = round(email_bounce/emails_sent*100 if emails_sent else 0,1)
    li_out       = ch_out("LinkedIn",{"Outreach done"})
    li_resp      = ch_out("LinkedIn",{"Response received"})
    li_rate      = round(li_resp/li_out*100 if li_out else 0,1)
    total_leads  = len(leads_df)
    hot_leads    = int((leads_df["Status"]=="Hot").sum()) if not leads_df.empty else 0
    warm_leads   = int((leads_df["Status"]=="Warm").sum()) if not leads_df.empty else 0
    active_reps  = act["Username"].nunique() if not act.empty else 0
    today_acts   = len(act[pd.to_datetime(act["Timestamp"],utc=True).dt.date==today]) if not act.empty else 0

    st.markdown(sl("📞 CALL KPIs"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(dials,"Dials")}{kpi_tile(contacts,"Contacts","green")}{kpi_tile(f"{contact_rate}%","Contact Rate","amber")}{kpi_tile(meetings,"Meetings 🗓","red")}</div>', unsafe_allow_html=True)

    st.markdown(sl("✉️ EMAIL KPIs"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(emails_sent,"Emails Sent")}{kpi_tile(email_reply,"Replies","green")}{kpi_tile(f"{bounce_rate}%","Bounce Rate","red")}</div>', unsafe_allow_html=True)

    st.markdown(sl("🔗 LINKEDIN KPIs"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(li_out,"Outreach","purple")}{kpi_tile(li_resp,"Responses","green")}{kpi_tile(f"{li_rate}%","Response Rate","amber")}</div>', unsafe_allow_html=True)

    st.markdown(sl("🔥 PIPELINE"), unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-strip">{kpi_tile(total_leads,"Total Leads")}{kpi_tile(warm_leads,"Warm","amber")}{kpi_tile(hot_leads,"Hot 🔥","red")}{kpi_tile(active_reps,"Active Reps","purple")}{kpi_tile(today_acts,"Today","green")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col_lb, col_fn = st.columns(2)

    with col_lb:
        st.markdown(sl("🏆 LEADERBOARD"), unsafe_allow_html=True)
        if not act.empty and is_admin:
            lb    = act.groupby("Username").size().reset_index(name="n").sort_values("n",ascending=False)
            max_t = lb["n"].max() or 1
            rc    = ["gold","silver","bronze"]
            html  = "".join([f'<div class="lb-row"><div class="lb-rank {rc[i] if i<3 else ""}">#{i+1}</div><div class="lb-name">{r["Username"]}</div><div class="lb-bar-wrap"><div class="lb-bar" style="width:{int(r["n"]/max_t*100)}%"></div></div><div class="lb-count">{r["n"]}</div></div>' for i,(idx,r) in enumerate(lb.iterrows())])
            st.markdown(f'<div class="op-card" style="padding:0;">{html}</div>', unsafe_allow_html=True)
            if "Channel" in act.columns:
                st.markdown(sl("CHANNEL BREAKDOWN"), unsafe_allow_html=True)
                pivot = act.groupby(["Username","Channel"]).size().reset_index(name="n").pivot(index="Username",columns="Channel",values="n").fillna(0).astype(int)
                st.dataframe(pivot, use_container_width=True)
        elif not is_admin:
            st.info("You can see your own stats above.")

    with col_fn:
        st.markdown(sl("🔽 FUNNEL"), unsafe_allow_html=True)
        if not leads_df.empty:
            total_a = len(leads_df[leads_df["Status"]!="DNC"]) or 1
            colors  = {"Call":"#00A7A7","Email":"#F0A500","LinkedIn":"#9B72CF"}
            fn_html = ""
            for s in SEQUENCE:
                n = int((leads_df["SequenceStep"]==s["step"]).sum())
                p = round(n/total_a*100)
                fn_html += f'<div class="funnel-step"><div class="funnel-label">Step {s["step"]}: {s["label"]}</div><div class="funnel-bar-wrap"><div class="funnel-bar" style="width:{p}%;background:{colors[s["channel"]]}"></div></div><div class="funnel-pct">{p}%</div><div class="funnel-n">{n}</div></div>'
            for label,filt,color in [("Warm",leads_df["Status"]=="Warm","#F0A500"),("Hot 🔥",leads_df["Status"]=="Hot","#E05252"),("DNC",leads_df["Status"]=="DNC","#4A5A6A")]:
                n=int(filt.sum()); p=round(n/total_a*100)
                fn_html += f'<div class="funnel-step"><div class="funnel-label">{label}</div><div class="funnel-bar-wrap"><div class="funnel-bar" style="width:{p}%;background:{color}"></div></div><div class="funnel-pct">{p}%</div><div class="funnel-n">{n}</div></div>'
            st.markdown(fn_html, unsafe_allow_html=True)

    # Daily chart
    st.markdown("---")
    st.markdown(sl("📈 DAILY VOLUME"), unsafe_allow_html=True)
    if not act.empty and "Timestamp" in act.columns:
        act["date"] = pd.to_datetime(act["Timestamp"],utc=True).dt.date
        daily = act.groupby("date").size().reset_index(name="count")
        all_d = pd.date_range(start=cutoff.date() if hasattr(cutoff,"date") else today, end=today, freq="D").date
        daily = pd.DataFrame({"date":all_d}).merge(daily,on="date",how="left").fillna(0)
        daily["count"] = daily["count"].astype(int)
        max_c = daily["count"].max() or 1
        bars  = "".join([f'<div title="{r["date"]}: {r["count"]}" style="flex:1;min-width:3px;height:{max(int(r["count"]/max_c*64),2)}px;background:#00A7A7;border-radius:2px 2px 0 0;opacity:{0.3+0.7*(r["count"]/max_c):.2f}"></div>' for _,r in daily.iterrows()])
        st.markdown(f'<div class="op-card"><div style="display:flex;align-items:flex-end;gap:2px;height:68px;">{bars}</div><div style="display:flex;justify-content:space-between;margin-top:.2rem;"><span style="font-size:.6rem;color:var(--muted);">{daily["date"].iloc[0]}</span><span style="font-size:.6rem;color:var(--muted);">{daily["date"].iloc[-1]}</span></div></div>', unsafe_allow_html=True)

    # Feed
    st.markdown("---")
    st.markdown(sl("📋 ACTIVITY FEED"), unsafe_allow_html=True)
    if not act.empty:
        feed = act.sort_values("Timestamp",ascending=False).head(20)
        ch_c = {"Call":"var(--teal)","Email":"var(--amber)","LinkedIn":"var(--purple)"}
        html = ""
        for _,r in feed.iterrows():
            ts = pd.to_datetime(r["Timestamp"],utc=True)
            m  = int((now-ts).total_seconds()/60)
            age= f"{m}m" if m<60 else (f"{m//60}h" if m<1440 else f"{m//1440}d")
            ch = r.get("Channel",""); cc=ch_c.get(ch,"var(--muted)")
            html += f'<div class="feed-row"><span style="color:var(--muted);font-family:\'DM Mono\',monospace;font-size:.62rem;min-width:36px;">{age}</span><span style="font-weight:600;min-width:60px;color:var(--teal);font-size:.78rem;">{r.get("Username","")}</span><span style="color:{cc};min-width:58px;font-size:.72rem;">{ch}</span><span style="color:#CCDDEE;min-width:75px;font-size:.78rem;">{str(r.get("ContactName",""))[:18]}</span><span style="color:var(--muted);font-style:italic;font-size:.72rem;">{r.get("Outcome","")}</span></div>'
        st.markdown(f'<div class="op-card" style="max-height:240px;overflow-y:auto;">{html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TAB: MANAGE LEADS
# ─────────────────────────────────────────────
def tab_manage_leads():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.3rem;">📋 LEAD MANAGEMENT + IMPORT</h2>', unsafe_allow_html=True)

    df = load_leads()

    # ── IMPORT ───────────────────────────────────────────────
    with st.expander("📥 IMPORT FROM CSV / EXCEL", expanded=False):
        uploaded = st.file_uploader("Upload file", type=["csv","xlsx","xls"], key="import_file")
        if uploaded is not None:
            try:
                raw = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
                st.success(f"File loaded: {len(raw)} rows, {len(raw.columns)} columns")

                # Show all columns from file so user can see what's coming in
                with st.expander(f"📋 Preview columns ({len(raw.columns)})", expanded=False):
                    st.write(raw.columns.tolist())
                    st.dataframe(raw.head(3), use_container_width=True)

                mapped   = map_import_df(raw)
                url_cols = detect_url_columns(raw)
                if url_cols:
                    st.info(f"🔗 URL columns preserved: {', '.join(url_cols)}")

                # Column selector for preview
                all_preview_cols = mapped.columns.tolist()
                default_preview  = [c for c in ["ContactName","Company","Title","Phone","Email","Industry","Status"] if c in all_preview_cols]
                chosen_preview   = st.multiselect("Preview columns", all_preview_cols, default=default_preview, key="import_preview_cols")
                if chosen_preview:
                    st.dataframe(mapped[chosen_preview].head(10), use_container_width=True)

                ic1, ic2 = st.columns(2)
                with ic1:
                    append_mode = st.radio("Import mode", ["Append to existing","Replace all leads"], index=0)
                with ic2:
                    default_step = st.selectbox("Start at step", list(range(1,8)), format_func=lambda x:f"Step {x}: {get_step_info(x)['label']}")
                    mapped["SequenceStep"] = mapped["SequenceStep"].where(mapped["SequenceStep"]>0, default_step)

                if st.button("✅ CONFIRM IMPORT", use_container_width=True, key="btn_confirm_import"):
                    if append_mode == "Append to existing" and not df.empty:
                        all_cols = list(set(df.columns.tolist()+mapped.columns.tolist()))
                        combined = pd.concat([df.reindex(columns=all_cols), mapped.reindex(columns=all_cols)], ignore_index=True)
                        combined = combined.drop_duplicates(subset=["LeadID"], keep="last")
                    else:
                        combined = mapped
                    if save_leads(combined):
                        invalidate_leads_cache()
                        st.success(f"✓ Imported {len(mapped)} leads. Total: {len(combined)}. Columns preserved: {len(combined.columns)}")
                        st.rerun()
            except Exception as e:
                st.error(f"Import error: {e}")

    st.markdown("---")

    # ── ADD SINGLE LEAD ───────────────────────────────────────
    with st.expander("➕ ADD SINGLE LEAD", expanded=False):
        c1,c2,c3 = st.columns(3)
        with c1: cn=st.text_input("Contact Name *",key="new_cn"); comp=st.text_input("Company *",key="new_comp"); title=st.text_input("Title",key="new_title")
        with c2: phone=st.text_input("Phone",key="new_phone"); email=st.text_input("Email",key="new_email"); ind=st.text_input("Industry",key="new_ind")
        with c3: rev=st.text_input("Revenue",key="new_rev"); status=st.selectbox("Status",STATUSES,key="new_status"); step=st.selectbox("Start Step",list(range(1,8)),format_func=lambda x:f"Step {x}: {get_step_info(x)['label']}",key="new_step")
        if st.button("ADD LEAD",use_container_width=True,key="btn_add"):
            if not cn.strip() or not comp.strip():
                st.error("Name and Company required.")
            else:
                new = {c:"" for c in CORE_LEAD_COLS}
                new.update({"LeadID":f"L-{int(time.time()*1000)}","ContactName":cn.strip(),"Company":comp.strip(),"Title":title.strip(),"Phone":phone.strip(),"Email":email.strip(),"Industry":ind.strip(),"Revenue":rev.strip(),"Status":status,"SequenceStep":step})
                df = pd.concat([df,pd.DataFrame([new])],ignore_index=True)
                if save_leads(df): invalidate_leads_cache(); log_activity(new["LeadID"],cn.strip(),"","","Lead Created",""); st.success(f"'{cn}' added ✓"); st.rerun()

    # ── FILTER + VIEW ─────────────────────────────────────────
    st.markdown("---")
    f1,f2,f3 = st.columns(3)
    with f1: fst=st.multiselect("Status",STATUSES,default=STATUSES,key="flt_status")
    with f2: fsp=st.multiselect("Step",list(range(1,8)),default=list(range(1,8)),format_func=lambda x:f"S{x}",key="flt_step")
    with f3: fsq=st.text_input("Search",placeholder="Name / Company…",key="flt_search")

    if not df.empty:
        v = df.copy()
        if fst: v=v[v["Status"].isin(fst)]
        if fsp: v=v[v["SequenceStep"].isin(fsp)]
        if fsq.strip():
            s=fsq.lower()
            v=v[v["ContactName"].str.lower().str.contains(s,na=False)|v["Company"].str.lower().str.contains(s,na=False)]

        # Column selector for the table
        all_cols = v.columns.tolist()
        default_show = [c for c in ["ContactName","Company","Title","Phone","Email","Industry","Revenue","Status","SequenceStep","LastTouched"] if c in all_cols]
        chosen_cols  = st.multiselect("Columns to display", all_cols, default=default_show, key="manage_display_cols")
        if not chosen_cols: chosen_cols = default_show

        st.dataframe(v[chosen_cols], use_container_width=True, height=400)
        st.caption(f"{len(v)} leads · {len(df.columns)} total columns in sheet")

        # Export
        csv_data = v.to_csv(index=False).encode()
        st.download_button("⬇ Export filtered leads as CSV", csv_data, "leads_export.csv", "text/csv", key="btn_export")

    # ── EDIT ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**EDIT LEAD**")
    if not df.empty:
        opts   = {f"{r['ContactName']} — {r['Company']} ({r['LeadID']})": r["LeadID"] for _,r in df.iterrows()}
        chosen = st.selectbox("Select Lead",["— select —"]+list(opts.keys()),key="edit_sel")
        if chosen != "— select —":
            row = df[df["LeadID"]==opts[chosen]].iloc[0]
            ec1,ec2 = st.columns(2)
            with ec1:
                es=st.selectbox("Status",STATUSES,index=STATUSES.index(str(row.get("Status","Cold"))),key="edit_st")
                ep=st.selectbox("Step",list(range(1,8)),index=max(int(row.get("SequenceStep",1))-1,0),format_func=lambda x:f"{x}: {get_step_info(x)['label']}",key="edit_sp")
            with ec2:
                en=st.text_area("Notes",value=str(row.get("Notes","")),height=90,key="edit_notes")
            if st.button("💾 UPDATE",use_container_width=True,key="btn_update"):
                now_s=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                for col,val in [("Status",es),("SequenceStep",ep),("Notes",en),("LastTouched",now_s),("LastTouchedBy",st.session_state.username)]:
                    df.loc[df["LeadID"]==opts[chosen],col]=val
                if save_leads(df): invalidate_leads_cache(); log_activity(opts[chosen],str(row.get("ContactName","")),"","",f"Manual Update → {es}",en); st.success("Updated ✓"); st.rerun()

# ─────────────────────────────────────────────
#  TAB: ACTIVITY LOG
# ─────────────────────────────────────────────
def tab_activity():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.3rem;">📋 ACTIVITY LOG</h2>', unsafe_allow_html=True)
    df = load_activity()
    if df.empty: st.info("No activity yet."); return

    is_admin = (st.session_state.user_role == "admin")
    if not is_admin:
        df = df[df["Username"]==st.session_state.username]

    now=datetime.now(timezone.utc); today=now.date()
    tdf=df[pd.to_datetime(df["Timestamp"],utc=True).dt.date==today] if not df.empty else df

    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.metric("Total",len(df))
    with k2: st.metric("Today",len(tdf))
    with k3: st.metric("Reps Today",tdf["Username"].nunique() if is_admin else 1)
    with k4: st.metric("Dials Today",len(tdf[tdf["Channel"]=="Call"]) if "Channel" in tdf.columns else 0)
    with k5: st.metric("Emails Today",len(tdf[tdf["Channel"]=="Email"]) if "Channel" in tdf.columns else 0)

    st.markdown("---")
    f1,f2,f3 = st.columns(3)
    with f1:
        users_opts = ["All"]+sorted(df["Username"].dropna().unique().tolist()) if is_admin else [st.session_state.username]
        fu = st.selectbox("Operator",users_opts,key="act_fu")
    with f2:
        fc = st.selectbox("Channel",["All","Call","Email","LinkedIn"],key="act_fc") if "Channel" in df.columns else "All"
    with f3:
        fo = st.text_input("Search",placeholder="outcome / notes…",key="act_fo")

    show = df.copy()
    if fu != "All": show=show[show["Username"]==fu]
    if fc != "All" and "Channel" in show.columns: show=show[show["Channel"]==fc]
    if fo.strip() and "Outcome" in show.columns:
        s=fo.lower(); show=show[show["Outcome"].str.lower().str.contains(s,na=False)|show["Notes"].str.lower().str.contains(s,na=False)]

    show=show.sort_values("Timestamp",ascending=False).head(300)
    dcols=[c for c in ["Timestamp","Username","ContactName","Channel","Outcome","Action","Notes"] if c in show.columns]
    st.dataframe(show[dcols],use_container_width=True,height=480)

# ─────────────────────────────────────────────
#  TAB: AI WORKSHOP
# ─────────────────────────────────────────────
def tab_ai():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.3rem;">🤖 AI MESSAGE WORKSHOP</h2>', unsafe_allow_html=True)
    st.caption("Draft messages for any lead — standalone, outside the queue.")
    c1,c2=st.columns(2)
    with c1: contact=st.text_input("Contact Name",key="ai_c"); company=st.text_input("Company",key="ai_co"); industry=st.text_input("Industry",key="ai_i")
    with c2: revenue=st.text_input("Revenue",key="ai_r"); mtype=st.radio("Type",["Follow-up Email","LinkedIn Message"],horizontal=True,key="ai_t"); notes=st.text_area("Context",height=70,key="ai_n")
    if st.button("⚡ GENERATE",use_container_width=True,key="btn_ai"):
        if not contact or not company: st.error("Need name and company.")
        else:
            row={"ContactName":contact,"Company":company,"Industry":industry,"Revenue":revenue,"Notes":notes}
            dtype="email" if "Email" in mtype else "linkedin"
            with st.spinner("Generating…"):
                subj,body=generate_ai_draft(row,dtype)
            if dtype=="email":
                st.markdown(sl("SUBJECT"),unsafe_allow_html=True); st.code(subj)
            st.markdown(sl("BODY"),unsafe_allow_html=True)
            st.markdown(f'<div class="op-card" style="border-color:var(--teal);font-size:.88rem;white-space:pre-wrap;">{body}</div>',unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        login_screen()
        return
    render_sidebar()
    tabs = st.tabs(["⚙️ SETUP","📞 DIAL QUEUE","📊 ANALYTICS","📋 MANAGE LEADS","📋 ACTIVITY LOG","🤖 AI WORKSHOP"])
    with tabs[0]: tab_setup()
    with tabs[1]: tab_dial_queue()
    with tabs[2]: tab_analytics()
    with tabs[3]: tab_manage_leads()
    with tabs[4]: tab_activity()
    with tabs[5]: tab_ai()

if __name__ == "__main__":
    main()
