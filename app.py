"""
Master of Ops — Team Execution OS  v3.0
Auto-Dial Outbound Cockpit | Industrial Premium
"""

import streamlit as st
import pandas as pd
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timezone, timedelta
import time, urllib.parse, random, smtplib, io
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

:root {
    --bg:#0B0F14; --surface:#131920; --panel:#1A2330; --border:#263040;
    --teal:#00A7A7; --teal-dim:#007A7A; --amber:#F0A500; --red:#E05252;
    --green:#3DBA72; --purple:#9B72CF; --text:#FFFFFF; --muted:#8899AA;
    --radius:4px;
}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:'IBM Plex Sans',sans-serif;}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
[data-testid="stToolbar"]{display:none;}
h1,h2,h3{font-family:'Barlow Condensed',sans-serif!important;letter-spacing:.05em;text-transform:uppercase;}

/* Cards */
.op-card{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);padding:1.1rem 1.4rem;margin-bottom:.6rem;}
.op-card-teal{border-left:3px solid var(--teal);}
.cockpit-panel{background:var(--panel);border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.2rem;height:100%;}

/* KPI strip */
.kpi-strip{display:flex;gap:.6rem;margin-bottom:1.2rem;flex-wrap:wrap;}
.kpi{flex:1;min-width:90px;background:var(--panel);border:1px solid var(--border);border-top:2px solid var(--teal);padding:.6rem .9rem;border-radius:var(--radius);text-align:center;}
.kpi.amber{border-top-color:var(--amber);} .kpi.red{border-top-color:var(--red);}
.kpi.green{border-top-color:var(--green);} .kpi.purple{border-top-color:var(--purple);}
.kpi-val{font-family:'Barlow Condensed',sans-serif;font-size:1.8rem;font-weight:800;color:var(--teal);line-height:1;}
.kpi.amber .kpi-val{color:var(--amber);} .kpi.red .kpi-val{color:var(--red);}
.kpi.green .kpi-val{color:var(--green);} .kpi.purple .kpi-val{color:var(--purple);}
.kpi-label{font-size:.58rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-top:.15rem;}
.kpi-sub{font-size:.6rem;color:var(--green);margin-top:.1rem;}

/* Lead card */
.lead-block{background:var(--panel);border:1px solid var(--teal);border-radius:var(--radius);padding:1.2rem 1.4rem;margin-bottom:.75rem;}
.lead-name{font-family:'Barlow Condensed',sans-serif;font-size:1.7rem;font-weight:800;letter-spacing:.05em;}
.lead-company{font-family:'DM Mono',monospace;font-size:.88rem;color:var(--teal);}

/* Badges */
.badge{display:inline-block;padding:.12rem .55rem;border-radius:2px;font-size:.62rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-family:'Barlow Condensed',sans-serif;}
.badge-cold{background:#1E3A5F;color:#7AB8F5;} .badge-warm{background:#4A2E00;color:var(--amber);}
.badge-hot{background:#4A1010;color:var(--red);} .badge-dnc{background:#2A2A2A;color:var(--muted);}

/* Intel chips */
.intel-grid{display:flex;flex-wrap:wrap;gap:.4rem;margin:.5rem 0;}
.intel-chip{background:var(--surface);border:1px solid var(--border);border-radius:3px;padding:.2rem .55rem;font-size:.7rem;color:#CCDDEE;}
.intel-chip span{color:var(--muted);font-size:.62rem;margin-right:.3rem;}

/* Step bar */
.step-bar{display:flex;gap:.3rem;margin:.5rem 0;align-items:center;}
.step-dot{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:.78rem;border:1px solid var(--border);color:var(--muted);background:var(--surface);}
.step-dot.active{background:var(--teal);border-color:var(--teal);color:#000;}
.step-dot.done{background:var(--teal-dim);border-color:var(--teal-dim);color:#000;}
.step-line{flex:1;height:1px;background:var(--border);}

/* Dial button */
.dial-btn-wrap{text-align:center;margin:.8rem 0;}
.dial-number{font-family:'DM Mono',monospace;font-size:1.6rem;font-weight:500;color:var(--teal);letter-spacing:.08em;margin:.4rem 0;}

/* Channel pill */
.ch-call{background:#0A2A2A;color:var(--teal);} .ch-email{background:#2A2A00;color:var(--amber);}
.ch-li{background:#1A0A2A;color:var(--purple);}

/* Funnel */
.funnel-step{display:flex;align-items:center;gap:.8rem;padding:.55rem .9rem;margin:.2rem 0;border-radius:var(--radius);background:var(--panel);border:1px solid var(--border);}
.funnel-label{font-family:'Barlow Condensed',sans-serif;font-size:.9rem;font-weight:700;letter-spacing:.04em;min-width:160px;}
.funnel-bar-wrap{flex:1;height:7px;background:var(--border);border-radius:3px;}
.funnel-bar{height:7px;border-radius:3px;}
.funnel-pct{font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);min-width:36px;text-align:right;}
.funnel-n{font-family:'DM Mono',monospace;font-size:.88rem;font-weight:500;min-width:30px;text-align:right;}

/* Leaderboard */
.lb-row{display:flex;align-items:center;gap:.65rem;padding:.5rem .9rem;border-bottom:1px solid var(--border);}
.lb-row:hover{background:rgba(255,255,255,.02);}
.lb-rank{font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;font-weight:800;color:var(--muted);width:26px;text-align:center;}
.lb-rank.gold{color:#FFD700;} .lb-rank.silver{color:#C0C0C0;} .lb-rank.bronze{color:#CD7F32;}
.lb-name{flex:1;font-weight:500;font-size:.88rem;}
.lb-bar-wrap{width:100px;height:5px;background:var(--border);border-radius:3px;}
.lb-bar{height:5px;background:var(--teal);border-radius:3px;}
.lb-count{font-family:'DM Mono',monospace;font-size:.82rem;color:var(--teal);min-width:28px;text-align:right;}

/* Feed */
.feed-row{display:flex;gap:.65rem;padding:.4rem 0;border-bottom:1px solid var(--border);font-size:.8rem;}

/* Inputs */
.stTextInput input,.stTextArea textarea{background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;}
.stSelectbox div[data-baseweb="select"]{background:var(--surface)!important;border:1px solid var(--border)!important;}
.stSelectbox div[data-baseweb="select"] *{color:var(--text)!important;}
.stMultiSelect div[data-baseweb="select"]{background:var(--surface)!important;border:1px solid var(--border)!important;}
.stMultiSelect div[data-baseweb="select"] *{color:var(--text)!important;}

/* Buttons */
.stButton>button{background:var(--teal)!important;color:#000!important;border:none!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.85rem!important;letter-spacing:.1em!important;text-transform:uppercase!important;border-radius:var(--radius)!important;padding:.4rem 1rem!important;}
.stButton>button:hover{background:var(--teal-dim)!important;}
.stLinkButton a{background:var(--panel)!important;color:var(--teal)!important;border:1px solid var(--teal)!important;font-family:'Barlow Condensed',sans-serif!important;font-weight:700!important;font-size:.8rem!important;letter-spacing:.08em!important;text-transform:uppercase!important;border-radius:var(--radius)!important;padding:.3rem .9rem!important;}

/* Tabs */
[data-baseweb="tab-list"]{background:var(--surface)!important;border-bottom:1px solid var(--border)!important;gap:0!important;}
[data-baseweb="tab"]{font-family:'Barlow Condensed',sans-serif!important;font-size:.88rem!important;letter-spacing:.07em!important;text-transform:uppercase!important;color:var(--muted)!important;background:transparent!important;border-radius:0!important;padding:.55rem 1.1rem!important;}
[aria-selected="true"][data-baseweb="tab"]{color:var(--teal)!important;border-bottom:2px solid var(--teal)!important;}

/* Misc */
[data-testid="stDataFrame"]{border:1px solid var(--border)!important;border-radius:var(--radius)!important;}
hr{border-color:var(--border)!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--surface);}
::-webkit-scrollbar-thumb{background:var(--teal-dim);border-radius:2px;}
.logo-mark{font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--teal);}
.logo-sub{font-size:.58rem;letter-spacing:.2em;color:var(--muted);text-transform:uppercase;}
.section-label{font-family:'Barlow Condensed',sans-serif;font-size:.68rem;letter-spacing:.2em;color:var(--muted);text-transform:uppercase;margin:1rem 0 .4rem;}
.setup-card{background:linear-gradient(135deg,#0A1A2A,#0B1E1E);border:1px solid var(--teal);border-radius:var(--radius);padding:1.8rem;margin:1rem 0;}

/* Auto-dial session banner */
.session-banner{background:linear-gradient(90deg,#002A2A,#0A1A2A);border:1px solid var(--teal);border-radius:var(--radius);padding:.6rem 1.2rem;display:flex;align-items:center;justify-content:space-between;margin-bottom:.8rem;}
.session-active{font-family:'Barlow Condensed',sans-serif;font-size:.85rem;font-weight:700;letter-spacing:.12em;color:var(--teal);}
.session-pulse{display:inline-block;width:8px;height:8px;background:var(--green);border-radius:50%;margin-right:.5rem;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.3;}}

@media(max-width:768px){.kpi-strip{flex-wrap:wrap;}.kpi{min-width:42%;}.lb-bar-wrap{display:none;}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONSTANTS & CONFIG
# ─────────────────────────────────────────────
SHEET_LEADS    = "Leads"
SHEET_ACTIVITY = "ActivityLog"

# 7-step outreach sequence
SEQUENCE = [
    {"step":1,"channel":"Call",     "label":"Cold Call #1"},
    {"step":2,"channel":"Email",    "label":"Intro Email"},
    {"step":3,"channel":"LinkedIn", "label":"LinkedIn Connect"},
    {"step":4,"channel":"Call",     "label":"Follow-up Call"},
    {"step":5,"channel":"Email",    "label":"Value Email"},
    {"step":6,"channel":"LinkedIn", "label":"LinkedIn Message"},
    {"step":7,"channel":"Call",     "label":"Decision Call"},
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
EMAIL_OUTCOMES  = ["Sent","Replied","Bounced"]
LI_OUTCOMES     = ["Outreach done","Response received"]
CONNECTED_OUTS  = {"Connected – decision maker","Connected – gatekeeper only","Meeting set"}

STATUSES   = ["Cold","Warm","Hot","DNC"]
TEAM_USERS = ["Alex","Jordan","Morgan","Taylor","Casey","Riley","Drew","Skyler","Quinn","Avery"]

CORE_LEAD_COLS = [
    "LeadID","ContactName","Company","Title","Phone","Email","Industry","Revenue",
    "Status","SequenceStep","Notes","LastTouched","LastTouchedBy","LockedBy","LockTime",
]
ACTIVITY_COLS = [
    "ActivityID","Timestamp","Username","LeadID","ContactName",
    "Channel","Outcome","Action","Notes",
]

# URL-like column names to auto-detect during import
URL_COL_HINTS = [
    "linkedin","linkedin url","person linkedin","contact linkedin",
    "company linkedin","website","company website","url","profile",
]

# Intel fields to surface in the cockpit
INTEL_FIELDS = [
    ("# Employees","Employees"), ("Employees","Employees"),
    ("Annual Revenue","Revenue"), ("Revenue","Revenue"),
    ("Industry","Industry"), ("City","City"), ("State","State"),
    ("Country","Country"), ("Keywords","Keywords"),
    ("Primary Intent Topic","Intent Topic"),
    ("Intent Score","Intent Score"),
    ("Total Funding","Total Funding"),
    ("Latest Funding","Latest Funding"),
]

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "logged_in":False,"username":"",
        "active_lead_id":None,"ai_draft":"","ai_subject":"",
        "dial_session":False,"email_panel_open":False,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
#  GOOGLE SHEETS
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_conn()

def load_leads():
    try:
        df = conn.read(worksheet=SHEET_LEADS, ttl=0)
        if df is None or df.empty or "LeadID" not in df.columns:
            return pd.DataFrame(columns=CORE_LEAD_COLS)
        df["LeadID"]       = df["LeadID"].astype(str)
        df["SequenceStep"] = pd.to_numeric(df.get("SequenceStep",1),errors="coerce").fillna(1).astype(int)
        df["Status"]       = df["Status"].fillna("Cold")
        df["LastTouched"]  = pd.to_datetime(df["LastTouched"],errors="coerce",utc=True)
        df["LockTime"]     = pd.to_datetime(df["LockTime"],errors="coerce",utc=True)
        df["LockedBy"]     = df["LockedBy"].fillna("")
        df["Notes"]        = df["Notes"].fillna("")
        return df
    except Exception as e:
        st.error(f"Leads load error: {e}")
        return pd.DataFrame(columns=CORE_LEAD_COLS)

def load_activity():
    try:
        df = conn.read(worksheet=SHEET_ACTIVITY, ttl=0)
        if df is None or df.empty or "ActivityID" not in df.columns:
            return pd.DataFrame(columns=ACTIVITY_COLS)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"],errors="coerce",utc=True)
        return df
    except Exception:
        return pd.DataFrame(columns=ACTIVITY_COLS)

def save_leads(df):
    try:
        conn.update(worksheet=SHEET_LEADS, data=df)
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

def bootstrap_sheets():
    try:
        conn.update(worksheet=SHEET_LEADS,    data=pd.DataFrame(columns=CORE_LEAD_COLS))
        conn.update(worksheet=SHEET_ACTIVITY, data=pd.DataFrame(columns=ACTIVITY_COLS))
        return True, "Both sheets initialised ✓"
    except Exception as e:
        return False, str(e)

def seed_demo_data():
    industries = ["Automotive","Aerospace","Food & Bev","Heavy Equipment","Plastics","Metal Fab"]
    companies  = [
        ("Apex Precision Parts","Sarah Chen","VP Operations","(312) 555-0142","s.chen@apexprecision.com"),
        ("Ironclad Fabrication","Marcus Webb","Plant Manager","(415) 555-0193","m.webb@ironclad.com"),
        ("Summit Aerospace","Diana Patel","Director of Procurement","(213) 555-0167","d.patel@summitaero.com"),
        ("CoreTech Manufacturing","James Okafor","COO","(312) 555-0188","j.okafor@coretech.com"),
        ("BlueLine Plastics","Rachel Torres","Supply Chain Lead","(617) 555-0154","r.torres@blueline.com"),
        ("Forgemaster Industries","Tom Kramer","CEO","(503) 555-0171","t.kramer@forgemaster.com"),
        ("Velocity Automotive","Lisa Nguyen","Operations Director","(734) 555-0139","l.nguyen@velocityauto.com"),
        ("Meridian Metal Works","Evan Shaw","Purchasing Manager","(216) 555-0182","e.shaw@meridianmetal.com"),
    ]
    reps     = ["Alex","Jordan","Morgan","Taylor"]
    statuses = ["Cold","Warm","Hot","Cold","Warm","Hot","Cold","Warm"]
    steps    = [1,2,3,4,1,2,3,1]
    now      = datetime.now(timezone.utc)
    leads, acts = [], []

    for i,((comp,contact,title,phone,email),status,step) in enumerate(zip(companies,statuses,steps)):
        lid = f"L-DEMO-{i+1:03d}"
        lts = (now-timedelta(days=random.randint(0,12))).strftime("%Y-%m-%dT%H:%M:%SZ")
        rep = reps[i%len(reps)]
        leads.append({
            "LeadID":lid,"ContactName":contact,"Company":comp,"Title":title,
            "Phone":phone,"Email":email,"Industry":industries[i%len(industries)],
            "Revenue":["$2M-$5M","$5M-$20M","$20M-$50M","$50M+"][i%4],
            "Status":status,"SequenceStep":step,
            "Notes":"Showed interest in Q3 pricing. Follow up on lead time concerns." if status!="Cold" else "",
            "LastTouched":lts,"LastTouchedBy":rep,"LockedBy":"","LockTime":"",
        })
        for j in range(random.randint(2,4)):
            ch = ["Call","Email","LinkedIn"][j%3]
            out = CALL_OUTCOMES[j%len(CALL_OUTCOMES)] if ch=="Call" else (EMAIL_OUTCOMES[j%len(EMAIL_OUTCOMES)] if ch=="Email" else LI_OUTCOMES[j%len(LI_OUTCOMES)])
            acts.append({
                "ActivityID":f"ACT-D-{i*10+j}",
                "Timestamp":(now-timedelta(days=random.randint(1,14))).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Username":reps[(i+j)%len(reps)],"LeadID":lid,"ContactName":contact,
                "Channel":ch,"Outcome":out,"Action":f"Step {j+1} touch","Notes":"Demo entry",
            })

    try:
        conn.update(worksheet=SHEET_LEADS,    data=pd.DataFrame(leads))
        conn.update(worksheet=SHEET_ACTIVITY, data=pd.DataFrame(acts))
        return True, f"Seeded {len(leads)} leads + {len(acts)} activities ✓"
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────
#  LEAD ROUTING & LOCKS
# ─────────────────────────────────────────────
def score_lead(row):
    now = datetime.now(timezone.utc)
    if row["Status"] == "DNC": return -9999
    lb = str(row.get("LockedBy","")).strip()
    lt = row.get("LockTime")
    if lb and lb != st.session_state.username:
        if pd.notna(lt) and (now-lt).total_seconds() < 600: return -9998
    last = row["LastTouched"]
    age  = (now-last).total_seconds()/86400 if pd.notna(last) else 30
    mult = {"Hot":3.0,"Warm":1.5,"Cold":1.0}.get(row["Status"],0.5)
    step_bonus = (8 - int(row["SequenceStep"])) * 8
    return (age*5 + step_bonus) * mult

def get_next_lead(df):
    if df.empty: return None
    df = df.copy()
    df["_score"] = df.apply(score_lead, axis=1)
    df = df[df["_score"] > -9000]
    return None if df.empty else df.sort_values("_score",ascending=False).iloc[0]

def lock_lead(df, lid):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    df.loc[df["LeadID"]==lid,"LockedBy"] = st.session_state.username
    df.loc[df["LeadID"]==lid,"LockTime"]  = now
    return df

def unlock_lead(df, lid):
    df.loc[df["LeadID"]==lid,"LockedBy"] = ""
    df.loc[df["LeadID"]==lid,"LockTime"]  = ""
    return df

def advance_lead(df, lid, new_status, new_notes):
    """Save outcome and advance SequenceStep."""
    now_s = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row   = df[df["LeadID"]==lid].iloc[0]
    cur   = int(row["SequenceStep"])
    nxt   = min(cur+1, 7)
    df.loc[df["LeadID"]==lid,"Status"]        = new_status
    df.loc[df["LeadID"]==lid,"SequenceStep"]  = nxt
    df.loc[df["LeadID"]==lid,"LastTouched"]   = now_s
    df.loc[df["LeadID"]==lid,"LastTouchedBy"] = st.session_state.username
    if new_notes.strip():
        existing = str(row["Notes"]).strip()
        df.loc[df["LeadID"]==lid,"Notes"] = (f"{existing}\n[{now_s[:10]}] {new_notes}").strip()
    df = unlock_lead(df, lid)
    return df

# ─────────────────────────────────────────────
#  EMAIL SENDING
# ─────────────────────────────────────────────
def get_email_identities():
    """Return list of (label, from_addr, smtp_config) from secrets."""
    identities = []
    try:
        ident_cfg = st.secrets.get("email_identities", {})
        for label, cfg in ident_cfg.items():
            identities.append({
                "label":    label,
                "from":     cfg.get("from_address",""),
                "host":     cfg.get("smtp_host","smtp.gmail.com"),
                "port":     int(cfg.get("smtp_port",587)),
                "user":     cfg.get("smtp_user",""),
                "password": cfg.get("smtp_password",""),
            })
    except Exception:
        pass
    return identities

def send_email(identity, to_addr, subject, body):
    """Send email via SMTP. Returns (success, message)."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = identity["from"]
        msg["To"]      = to_addr
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(identity["host"], identity["port"], timeout=15) as s:
            s.starttls()
            s.login(identity["user"], identity["password"])
            s.sendmail(identity["from"], [to_addr], msg.as_string())
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
        return "Subject: Quick follow-up", "No AI key set — write your message here."
    genai.configure(api_key=key)
    model   = genai.GenerativeModel("gemini-1.5-flash")
    contact  = lead_row.get("ContactName","there")
    company  = lead_row.get("Company","the company")
    industry = lead_row.get("Industry","manufacturing")
    revenue  = lead_row.get("Revenue","unknown")
    notes    = lead_row.get("Notes","no prior notes")

    if draft_type == "email":
        prompt = f"""Write a B2B follow-up sales email.
Lead: {contact} at {company} | Industry: {industry} | Revenue: {revenue}
Prior notes: {notes}
Rules: Professional, operator-first, zero jargon, simple language.
MAX 3 sentence body. Include a subject line on the first line starting with "Subject: ".
No fluff. Make it worth opening."""
    else:
        prompt = f"""Write a LinkedIn connection/message for B2B outreach.
Lead: {contact} at {company} | Industry: {industry} | Revenue: {revenue}
Prior notes: {notes}
Rules: Human, witty but professional. MAX 3 sentences. No "I hope this finds you well." """

    try:
        text = model.generate_content(prompt).text.strip()
        if draft_type == "email":
            lines = text.split("\n")
            subj  = lines[0].replace("Subject:","").strip() if lines[0].lower().startswith("subject:") else f"Following up — {company}"
            body  = "\n".join(lines[1:]).strip()
            return subj, body
        return "", text
    except Exception as e:
        return "Subject: Follow-up", f"Gemini error: {e}"

# ─────────────────────────────────────────────
#  CSV/EXCEL IMPORT HELPERS
# ─────────────────────────────────────────────
def detect_url_columns(df):
    """Return list of columns that are URL-like."""
    url_cols = []
    for col in df.columns:
        cl = col.lower().strip()
        if any(h in cl for h in URL_COL_HINTS):
            url_cols.append(col)
        elif df[col].dtype == object:
            sample = df[col].dropna().head(5).astype(str)
            if sample.str.startswith("http").any():
                url_cols.append(col)
    return list(set(url_cols))

COLUMN_MAP = {
    "first name":        None,  # handled separately
    "last name":         None,
    "full name":         "ContactName",
    "name":              "ContactName",
    "contact name":      "ContactName",
    "company":           "Company",
    "company name":      "Company",
    "organization":      "Company",
    "title":             "Title",
    "job title":         "Title",
    "position":          "Title",
    "phone":             "Phone",
    "phone number":      "Phone",
    "mobile":            "Phone",
    "email":             "Email",
    "email address":     "Email",
    "work email":        "Email",
    "industry":          "Industry",
    "revenue":           "Revenue",
    "annual revenue":    "Revenue",
}

def map_import_df(raw_df):
    """Map raw import columns to core fields, preserve extras."""
    df = raw_df.copy()
    rename = {}
    first_name_col, last_name_col = None, None

    for col in df.columns:
        cl = col.lower().strip()
        if "first name" in cl or cl == "first":
            first_name_col = col
        elif "last name" in cl or cl == "last":
            last_name_col = col
        elif cl in COLUMN_MAP and COLUMN_MAP[cl]:
            rename[col] = COLUMN_MAP[cl]

    df = df.rename(columns=rename)

    # Combine first+last if ContactName missing
    if "ContactName" not in df.columns:
        if first_name_col and last_name_col:
            df["ContactName"] = (df[first_name_col].fillna("").astype(str).str.strip() + " " +
                                 df[last_name_col].fillna("").astype(str).str.strip()).str.strip()
        elif first_name_col:
            df["ContactName"] = df[first_name_col].fillna("").astype(str).str.strip()

    # Ensure core cols exist
    for col in CORE_LEAD_COLS:
        if col not in df.columns:
            df[col] = ""

    # Generate LeadIDs for rows missing them
    for i, row in df.iterrows():
        if not str(row.get("LeadID","")).strip() or str(row["LeadID"]) == "nan":
            df.at[i,"LeadID"] = f"L-{int(time.time()*1000)}-{i}"

    df["Status"]       = df["Status"].replace("",pd.NA).fillna("Cold")
    df["SequenceStep"] = pd.to_numeric(df["SequenceStep"],errors="coerce").fillna(1).astype(int)
    df["Notes"]        = df["Notes"].fillna("")
    df["LockedBy"]     = df["LockedBy"].fillna("")
    df["LockTime"]     = df["LockTime"].fillna("")

    return df

# ─────────────────────────────────────────────
#  UI HELPERS
# ─────────────────────────────────────────────
def sl(txt): return f'<div class="section-label">{txt}</div>'

def status_badge(status):
    cls = {"Cold":"badge-cold","Warm":"badge-warm","Hot":"badge-hot","DNC":"badge-dnc"}.get(status,"badge-cold")
    return f'<span class="badge {cls}">{status}</span>'

def channel_badge(ch):
    cls = {"Call":"ch-call","Email":"ch-email","LinkedIn":"ch-li"}.get(ch,"ch-call")
    icons= {"Call":"📞","Email":"✉️","LinkedIn":"🔗"}
    return f'<span class="badge {cls}">{icons.get(ch,"")} {ch}</span>'

def step_indicator(current_step):
    parts = []
    for s in SEQUENCE:
        n = s["step"]
        cls = "done" if n<current_step else ("active" if n==current_step else "")
        icons = {"Call":"📞","Email":"✉️","LinkedIn":"🔗"}
        icon  = icons.get(s["channel"],"·")
        label = s["label"]
        parts.append(f'<div class="step-dot {cls}" title="Step {n}: {label}">{icon}</div>')
        if n < 7: parts.append('<div class="step-line"></div>')
    st.markdown(f'<div class="step-bar">{"".join(parts)}</div>', unsafe_allow_html=True)

def get_step_info(step_num):
    for s in SEQUENCE:
        if s["step"] == step_num:
            return s
    return {"step":step_num,"channel":"Call","label":f"Step {step_num}"}

def render_intel_panel(row):
    """Render the intel chips for a lead row."""
    chips = []
    seen  = set()

    # Structured intel fields
    for src_col, label in INTEL_FIELDS:
        if src_col in row.index:
            val = str(row.get(src_col,"")).strip()
            if val and val not in ("nan","","None") and label not in seen:
                chips.append(f'<div class="intel-chip"><span>{label}</span>{val}</div>')
                seen.add(label)

    # Revenue/Industry fallback
    for col, label in [("Revenue","Revenue"),("Industry","Industry")]:
        if label not in seen:
            val = str(row.get(col,"")).strip()
            if val and val not in ("nan","","None"):
                chips.append(f'<div class="intel-chip"><span>{label}</span>{val}</div>')

    if not chips:
        return

    st.markdown(sl("COMPANY INTEL"), unsafe_allow_html=True)
    st.markdown(f'<div class="intel-grid">{"".join(chips)}</div>', unsafe_allow_html=True)

def render_url_buttons(row):
    """Render LinkedIn/website link buttons for a lead row."""
    url_cols = detect_url_columns(pd.DataFrame([row]))
    if not url_cols:
        return

    links = []
    for col in url_cols:
        val = str(row.get(col,"")).strip()
        if not val or val in ("nan","None",""): continue
        if not val.startswith("http"): val = "https://" + val
        cl = col.lower()
        if "person" in cl or ("linkedin" in cl and "company" not in cl):
            links.append(("👤 Contact LinkedIn", val))
        elif "company" in cl and "linkedin" in cl:
            links.append(("🏢 Company LinkedIn", val))
        elif "website" in cl or "web" in cl:
            links.append(("🌐 Company Website", val))
        else:
            links.append((f"🔗 {col}", val))

    if not links:
        return

    st.markdown(sl("QUICK LINKS"), unsafe_allow_html=True)
    cols = st.columns(len(links))
    for i,(label,url) in enumerate(links):
        with cols[i]:
            st.link_button(label, url, use_container_width=True)

def kpi_tile(val, label, cls="", sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi {cls}"><div class="kpi-val">{val}</div><div class="kpi-label">{label}</div>{sub_html}</div>'

# ─────────────────────────────────────────────
#  TAB: DIAL QUEUE (COCKPIT)
# ─────────────────────────────────────────────
def tab_dial_queue():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📞 DIAL QUEUE — OUTBOUND COCKPIT</h2>',
                unsafe_allow_html=True)

    df = load_leads()
    if df.empty:
        st.info("No leads loaded. Go to **Setup** to bootstrap + seed, or **Manage Leads** to import.")
        return

    active = df[df["Status"] != "DNC"]
    total  = len(df)
    hot    = int((df["Status"]=="Hot").sum())
    warm   = int((df["Status"]=="Warm").sum())

    st.markdown(
        f'<div class="kpi-strip">'
        f'{kpi_tile(total,"Total Leads")}'
        f'{kpi_tile(warm,"Warm","amber")}'
        f'{kpi_tile(hot,"Hot 🔥","red")}'
        f'{kpi_tile(len(active),"In Queue","green")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Session controls ──────────────────────
    if not st.session_state.dial_session:
        if st.button("▶  START AUTO DIAL SESSION", use_container_width=True):
            st.session_state.dial_session = True
            st.session_state.active_lead_id = None
            st.session_state.ai_draft = ""
            st.session_state.ai_subject = ""
            st.session_state.email_panel_open = False
            st.rerun()
        st.caption("Auto-dial loads leads one after another. After each save, the next lead loads automatically.")
        return

    # ── Session active banner ─────────────────
    col_banner, col_stop = st.columns([4,1])
    with col_banner:
        st.markdown(
            '<div class="session-banner">'
            '<span><span class="session-pulse"></span>'
            '<span class="session-active">AUTO DIAL SESSION ACTIVE</span></span>'
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

    # ── Load / lock next lead ─────────────────
    lead = get_next_lead(df)
    if lead is None:
        st.success("✅ Queue clear — all leads actioned or locked by teammates.")
        st.session_state.dial_session = False
        return

    lead_id = lead["LeadID"]
    step_num = int(lead["SequenceStep"])
    step_info = get_step_info(step_num)
    channel   = step_info["channel"]
    status    = lead["Status"]

    if st.session_state.active_lead_id != lead_id:
        df = lock_lead(df, lead_id)
        save_leads(df)
        st.session_state.active_lead_id = lead_id
        st.session_state.ai_draft   = ""
        st.session_state.ai_subject = ""
        st.session_state.email_panel_open = (channel == "Email")

    # ── COCKPIT LAYOUT: Left (main) + Right (intel) ──
    col_main, col_intel = st.columns([3,2])

    with col_main:
        # Lead header
        st.markdown(f"""
        <div class="lead-block">
            <div class="lead-company">{lead.get('Company','—')}</div>
            <div class="lead-name">{lead.get('ContactName','—')}</div>
            <div style="color:var(--muted);font-size:.8rem;margin:.2rem 0;">
                {lead.get('Title','—')}
            </div>
            <div style="margin-top:.5rem;display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;">
                {status_badge(status)}
                {channel_badge(channel)}
                <span style="font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);">
                    Step {step_num}/7: {step_info['label']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        step_indicator(step_num)

        # ── CALL PANEL ────────────────────────
        if channel == "Call":
            phone = str(lead.get("Phone","")).strip()
            tel_url = f"tel:{phone.replace(' ','').replace('-','').replace('(','').replace(')','')}"

            st.markdown(sl("📞 CALL PANEL"), unsafe_allow_html=True)
            st.markdown(f'<div class="op-card"><div class="dial-number">{phone or "No phone on file"}</div></div>', unsafe_allow_html=True)

            if phone:
                st.link_button(f"📲 DIAL NOW — {phone}", tel_url, use_container_width=True)
                st.caption("Tapping opens your phone dialer with this number pre-loaded. Return here to log the outcome.")
            else:
                st.warning("No phone number for this lead.")

            st.markdown(sl("LOG CALL OUTCOME"), unsafe_allow_html=True)
            call_outcome = st.selectbox("Outcome *", ["— select —"] + CALL_OUTCOMES, key="call_out")
            call_notes   = st.text_area("Call notes *", placeholder="What happened? Any intel? Next steps?", height=80, key="call_notes")
            new_status   = st.selectbox("Update Status", STATUSES, index=STATUSES.index(status), key="call_status")

            btn_disabled = (call_outcome == "— select —" or not call_notes.strip())
            if st.button("✅ SAVE CALL & NEXT LEAD", use_container_width=True, disabled=btn_disabled):
                df = load_leads()
                df = advance_lead(df, lead_id, new_status, call_notes)
                if save_leads(df):
                    log_activity(lead_id, str(lead.get("ContactName","")),
                                 "Call", call_outcome,
                                 f"Step {step_num}: {step_info['label']}", call_notes)
                    st.session_state.active_lead_id = None
                    st.session_state.email_panel_open = False
                    st.success("Logged ✓ — Loading next lead…"); time.sleep(0.6); st.rerun()

            if btn_disabled and call_outcome != "— select —":
                st.caption("⚠ Fill in notes to save.")

        # ── LINKEDIN PANEL ────────────────────
        elif channel == "LinkedIn":
            st.markdown(sl("🔗 LINKEDIN TRACKING"), unsafe_allow_html=True)
            st.markdown('<div class="op-card">', unsafe_allow_html=True)
            li_notes = st.text_input("Short note (optional)", placeholder="e.g. Sent connection request", key="li_notes")

            lc1, lc2 = st.columns(2)
            with lc1:
                if st.button("✅ OUTREACH DONE", use_container_width=True):
                    df = load_leads()
                    df = advance_lead(df, lead_id, status, li_notes or "LinkedIn outreach done")
                    if save_leads(df):
                        log_activity(lead_id, str(lead.get("ContactName","")),
                                     "LinkedIn", "Outreach done",
                                     f"Step {step_num}: {step_info['label']}", li_notes)
                        st.session_state.active_lead_id = None
                        st.success("Logged ✓ — next lead…"); time.sleep(0.5); st.rerun()
            with lc2:
                if st.button("💬 RESPONSE RECEIVED", use_container_width=True):
                    df = load_leads()
                    df = advance_lead(df, lead_id, "Warm", li_notes or "LinkedIn response received")
                    if save_leads(df):
                        log_activity(lead_id, str(lead.get("ContactName","")),
                                     "LinkedIn", "Response received",
                                     f"Step {step_num}: {step_info['label']}", li_notes)
                        st.session_state.active_lead_id = None
                        st.success("Logged ✓ → Status: Warm"); time.sleep(0.5); st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # ── EMAIL PANEL (in-queue) ────────────
        if channel == "Email" or st.session_state.email_panel_open:
            st.markdown(sl("✉️ EMAIL PANEL"), unsafe_allow_html=True)
            identities = get_email_identities()

            if not identities:
                st.info("Add email identities to Streamlit secrets to enable sending. See Setup tab.")
            else:
                identity_labels = [i["label"] for i in identities]
                sel_ident_label = st.selectbox("Send from", identity_labels, key="email_from")
                sel_ident = next(i for i in identities if i["label"]==sel_ident_label)

                if not st.session_state.ai_subject or not st.session_state.ai_draft:
                    with st.spinner("Drafting email…"):
                        subj, body = generate_ai_draft(lead, "email")
                        st.session_state.ai_subject = subj
                        st.session_state.ai_draft   = body

                to_addr = st.text_input("To", value=str(lead.get("Email","")), key="email_to")
                subject = st.text_input("Subject", value=st.session_state.ai_subject, key="email_subj")
                body    = st.text_area("Body", value=st.session_state.ai_draft, height=130, key="email_body")

                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("📤 SEND EMAIL", use_container_width=True):
                        if not to_addr.strip():
                            st.error("To address required.")
                        else:
                            ok, msg = send_email(sel_ident, to_addr, subject, body)
                            if ok:
                                df = load_leads()
                                df = advance_lead(df, lead_id, status, f"Email sent: {subject}")
                                save_leads(df)
                                log_activity(lead_id, str(lead.get("ContactName","")),
                                             "Email","Sent",f"Step {step_num}: {step_info['label']}",
                                             f"Subject: {subject}")
                                st.success(msg)
                                st.session_state.email_panel_open = False
                                st.session_state.active_lead_id = None
                                time.sleep(0.6); st.rerun()
                            else:
                                st.error(f"Send failed: {msg}")
                with ec2:
                    if st.button("📝 LOG EMAIL MANUALLY", use_container_width=True):
                        df = load_leads()
                        df = advance_lead(df, lead_id, status, f"Email logged: {subject}")
                        save_leads(df)
                        log_activity(lead_id, str(lead.get("ContactName","")),
                                     "Email","Sent",f"Step {step_num}: {step_info['label']}",
                                     f"Subject: {subject} (manual log)")
                        st.session_state.active_lead_id = None
                        time.sleep(0.5); st.rerun()

            # Quick reply/bounce buttons for existing emails
            st.markdown(sl("MARK PRIOR EMAIL"), unsafe_allow_html=True)
            rb1, rb2 = st.columns(2)
            with rb1:
                if st.button("↩ MARK REPLIED", use_container_width=True):
                    log_activity(lead_id, str(lead.get("ContactName","")), "Email","Replied","Manual mark","")
                    st.success("Replied logged.")
            with rb2:
                if st.button("⛔ MARK BOUNCED", use_container_width=True):
                    log_activity(lead_id, str(lead.get("ContactName","")), "Email","Bounced","Manual mark","")
                    st.success("Bounce logged.")

        # Toggle email panel for call/li steps
        if channel != "Email" and not st.session_state.email_panel_open:
            if st.button("✉ ADD EMAIL THIS SESSION", use_container_width=True):
                st.session_state.email_panel_open = True
                st.rerun()

        # ── Skip ──────────────────────────────
        if st.button("⏭ SKIP THIS LEAD", use_container_width=True):
            df = load_leads()
            df = unlock_lead(df, lead_id)
            save_leads(df)
            st.session_state.active_lead_id = None
            st.session_state.email_panel_open = False
            st.rerun()

        # ── DNC ───────────────────────────────
        if st.button("🚫 MARK DNC", use_container_width=True):
            df = load_leads()
            df.loc[df["LeadID"]==lead_id,"Status"] = "DNC"
            df = unlock_lead(df, lead_id)
            save_leads(df)
            log_activity(lead_id, str(lead.get("ContactName","")), "Call","Not interested","DNC marked","")
            st.session_state.active_lead_id = None
            st.rerun()

    # ── RIGHT: Intel Panel ────────────────────
    with col_intel:
        st.markdown(sl("CONTACT INFO"), unsafe_allow_html=True)
        st.markdown(f"""
        <div class="op-card" style="font-size:.82rem;line-height:1.9;">
            <div style="color:var(--muted);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem;">Phone</div>
            <div style="font-family:'DM Mono',monospace;color:var(--teal);font-size:1rem;margin-bottom:.6rem;">{lead.get('Phone','—')}</div>
            <div style="color:var(--muted);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">Email</div>
            <div style="font-family:'DM Mono',monospace;font-size:.8rem;margin-bottom:.6rem;">{lead.get('Email','—')}</div>
            <div style="color:var(--muted);font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.2rem;">Company</div>
            <div style="margin-bottom:.4rem;">{lead.get('Company','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        render_intel_panel(lead)
        render_url_buttons(lead)

        # ── News link ─────────────────────────
        company_enc = urllib.parse.quote_plus(str(lead.get("Company","")))
        news_url = f"https://www.google.com/search?q={company_enc}+news&tbm=nws"
        st.markdown(sl("RESEARCH"), unsafe_allow_html=True)
        st.link_button("📰 COMPANY NEWS", news_url, use_container_width=True)

        # ── Prior notes ───────────────────────
        notes_val = str(lead.get("Notes","")).strip()
        if notes_val:
            st.markdown(sl("PRIOR NOTES"), unsafe_allow_html=True)
            st.markdown(
                f'<div class="op-card op-card-teal" style="font-size:.82rem;white-space:pre-wrap;max-height:180px;overflow-y:auto;">{notes_val}</div>',
                unsafe_allow_html=True,
            )

        # ── AI LinkedIn draft ─────────────────
        if channel == "LinkedIn":
            st.markdown(sl("AI LINKEDIN DRAFT"), unsafe_allow_html=True)
            if not st.session_state.ai_draft:
                if st.button("⚡ GENERATE LI DRAFT", use_container_width=True):
                    with st.spinner("Drafting…"):
                        _, body = generate_ai_draft(lead, "linkedin")
                        st.session_state.ai_draft = body
            if st.session_state.ai_draft:
                st.markdown(
                    f'<div class="op-card" style="border-color:var(--purple);font-size:.82rem;white-space:pre-wrap;">{st.session_state.ai_draft}</div>',
                    unsafe_allow_html=True,
                )

# ─────────────────────────────────────────────
#  TAB: ANALYTICS
# ─────────────────────────────────────────────
def tab_analytics():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📊 OPS ANALYTICS — COMMAND VIEW</h2>',
                unsafe_allow_html=True)

    leads_df = load_leads()
    act_df   = load_activity()
    now      = datetime.now(timezone.utc)
    today    = now.date()

    if leads_df.empty and act_df.empty:
        st.info("No data. Go to Setup → Seed Demo Data.")
        return

    cf1, cf2, _ = st.columns([1,1,3])
    with cf1:
        rng = st.selectbox("Time Range",["Last 7 days","Last 14 days","Last 30 days","All time"])
    cutoff = now - timedelta(days={"Last 7 days":7,"Last 14 days":14,"Last 30 days":30,"All time":3650}[rng])

    act = act_df.copy()
    if not act.empty and "Timestamp" in act.columns:
        act = act[act["Timestamp"] >= cutoff]

    # ── Channel-based KPIs ────────────────────
    def ch_out(ch, out_filter=None):
        if act.empty or "Channel" not in act.columns: return 0
        sub = act[act["Channel"]==ch]
        if out_filter: sub = sub[sub["Outcome"].isin(out_filter)]
        return len(sub)

    dials        = ch_out("Call")
    contacts     = ch_out("Call", CONNECTED_OUTS)
    contact_rate = round(contacts/dials*100 if dials else 0, 1)
    meetings     = ch_out("Call", {"Meeting set"})
    emails_sent  = ch_out("Email", {"Sent"})
    email_reply  = ch_out("Email", {"Replied"})
    email_bounce = ch_out("Email", {"Bounced"})
    bounce_rate  = round(email_bounce/emails_sent*100 if emails_sent else 0, 1)
    li_out       = ch_out("LinkedIn", {"Outreach done"})
    li_resp      = ch_out("LinkedIn", {"Response received"})
    li_rate      = round(li_resp/li_out*100 if li_out else 0, 1)
    total_leads  = len(leads_df) if not leads_df.empty else 0
    hot_leads    = int((leads_df["Status"]=="Hot").sum()) if not leads_df.empty else 0
    active_reps  = act["Username"].nunique() if not act.empty else 0
    today_acts   = len(act[pd.to_datetime(act["Timestamp"],utc=True).dt.date==today]) if not act.empty else 0

    # ── KPI STRIP 1: Call ─────────────────────
    st.markdown(sl("📞 CALL PERFORMANCE"), unsafe_allow_html=True)
    st.markdown(
        f'<div class="kpi-strip">'
        f'{kpi_tile(dials,"Dials")}'
        f'{kpi_tile(contacts,"Contacts","green")}'
        f'{kpi_tile(f"{contact_rate}%","Contact Rate","amber")}'
        f'{kpi_tile(meetings,"Meetings Set","red")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── KPI STRIP 2: Email ────────────────────
    st.markdown(sl("✉️ EMAIL PERFORMANCE"), unsafe_allow_html=True)
    st.markdown(
        f'<div class="kpi-strip">'
        f'{kpi_tile(emails_sent,"Emails Sent")}'
        f'{kpi_tile(email_reply,"Replies","green")}'
        f'{kpi_tile(f"{bounce_rate}%","Bounce Rate","red")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── KPI STRIP 3: LinkedIn ─────────────────
    st.markdown(sl("🔗 LINKEDIN PERFORMANCE"), unsafe_allow_html=True)
    st.markdown(
        f'<div class="kpi-strip">'
        f'{kpi_tile(li_out,"LI Outreach","purple")}'
        f'{kpi_tile(li_resp,"LI Responses","green")}'
        f'{kpi_tile(f"{li_rate}%","LI Response Rate","amber")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── KPI STRIP 4: Pipeline ─────────────────
    st.markdown(sl("🔥 PIPELINE"), unsafe_allow_html=True)
    st.markdown(
        f'<div class="kpi-strip">'
        f'{kpi_tile(total_leads,"Total Leads")}'
        f'{kpi_tile(hot_leads,"Hot 🔥","red")}'
        f'{kpi_tile(active_reps,"Active Reps","purple")}'
        f'{kpi_tile(today_acts,"Today Actions","green")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Leaderboard + Funnel ──────────────────
    st.markdown("---")
    col_lb, col_fn = st.columns(2)

    with col_lb:
        st.markdown(sl("🏆 REP LEADERBOARD (ALL TOUCHES)"), unsafe_allow_html=True)
        if not act.empty:
            lb = act.groupby("Username").size().reset_index(name="touches").sort_values("touches",ascending=False)
            max_t = lb["touches"].max() or 1
            ranks = ["gold","silver","bronze"]
            lb_html = ""
            for rank, (_, r) in enumerate(lb.iterrows(), 1):
                rc  = ranks[rank-1] if rank<=3 else ""
                pct = int(r["touches"]/max_t*100)
                lb_html += f'<div class="lb-row"><div class="lb-rank {rc}">#{rank}</div><div class="lb-name">{r["Username"]}</div><div class="lb-bar-wrap"><div class="lb-bar" style="width:{pct}%"></div></div><div class="lb-count">{r["touches"]}</div></div>'
            st.markdown(f'<div class="op-card" style="padding:0;">{lb_html}</div>', unsafe_allow_html=True)

        # Per-channel breakdown per rep
        if not act.empty and "Channel" in act.columns:
            st.markdown(sl("REP CHANNEL BREAKDOWN"), unsafe_allow_html=True)
            pivot = (act.groupby(["Username","Channel"]).size()
                       .reset_index(name="n")
                       .pivot(index="Username",columns="Channel",values="n")
                       .fillna(0).astype(int))
            st.dataframe(pivot, use_container_width=True)

    with col_fn:
        st.markdown(sl("🔽 SEQUENCE FUNNEL"), unsafe_allow_html=True)
        if not leads_df.empty:
            total_a = len(leads_df[leads_df["Status"]!="DNC"]) or 1
            def pct(n): return round(n/total_a*100)
            def fn_row(label, n, color):
                p = pct(n)
                return f'<div class="funnel-step"><div class="funnel-label">{label}</div><div class="funnel-bar-wrap"><div class="funnel-bar" style="width:{p}%;background:{color}"></div></div><div class="funnel-pct">{p}%</div><div class="funnel-n">{n}</div></div>'

            fn_html = ""
            for s in SEQUENCE:
                n = int((leads_df["SequenceStep"]==s["step"]).sum())
                colors = {"Call":"#00A7A7","Email":"#F0A500","LinkedIn":"#9B72CF"}
                fn_html += fn_row(f"Step {s['step']}: {s['label']}", n, colors[s["channel"]])

            fn_html += fn_row("Warm 🌡", int((leads_df["Status"]=="Warm").sum()), "#F0A500")
            fn_html += fn_row("Hot 🔥",  int((leads_df["Status"]=="Hot").sum()),  "#E05252")
            fn_html += fn_row("DNC 🚫",  int((leads_df["Status"]=="DNC").sum()),  "#4A5A6A")
            st.markdown(fn_html, unsafe_allow_html=True)

    # ── Daily volume chart ────────────────────
    st.markdown("---")
    st.markdown(sl("📈 DAILY ACTIVITY VOLUME"), unsafe_allow_html=True)

    if not act.empty and "Timestamp" in act.columns:
        act["date"] = pd.to_datetime(act["Timestamp"],utc=True).dt.date
        daily = (act.groupby("date").size().reset_index(name="count"))
        all_days = pd.date_range(start=cutoff.date(), end=today, freq="D").date
        daily = pd.DataFrame({"date":all_days}).merge(daily, on="date", how="left").fillna(0)
        daily["count"] = daily["count"].astype(int)
        max_c = daily["count"].max() or 1
        bars  = "".join([
            f'<div title="{r["date"]}: {r["count"]}" style="flex:1;min-width:4px;height:{max(int(r["count"]/max_c*68),2)}px;background:#00A7A7;border-radius:2px 2px 0 0;opacity:{0.3+0.7*(r["count"]/max_c):.2f}"></div>'
            for _,r in daily.iterrows()
        ])
        st.markdown(
            f'<div class="op-card"><div style="display:flex;align-items:flex-end;gap:2px;height:72px;">{bars}</div>'
            f'<div style="display:flex;justify-content:space-between;margin-top:.25rem;">'
            f'<span style="font-size:.62rem;color:var(--muted);">{daily["date"].iloc[0]}</span>'
            f'<span style="font-size:.62rem;color:var(--muted);">{daily["date"].iloc[-1]}</span></div></div>',
            unsafe_allow_html=True,
        )

    # ── Activity feed ─────────────────────────
    st.markdown("---")
    st.markdown(sl("📋 LIVE ACTIVITY FEED"), unsafe_allow_html=True)
    if not act.empty:
        feed = act.sort_values("Timestamp",ascending=False).head(25)
        feed_html = ""
        ch_colors = {"Call":"var(--teal)","Email":"var(--amber)","LinkedIn":"var(--purple)"}
        for _,r in feed.iterrows():
            ts = pd.to_datetime(r["Timestamp"],utc=True)
            m  = int((now-ts).total_seconds()/60)
            age = f"{m}m ago" if m<60 else (f"{m//60}h ago" if m<1440 else f"{m//1440}d ago")
            ch  = r.get("Channel","")
            cc  = ch_colors.get(ch,"var(--muted)")
            feed_html += f'<div class="feed-row"><span style="color:var(--muted);font-family:\'DM Mono\',monospace;font-size:.67rem;min-width:52px;">{age}</span><span style="font-weight:600;min-width:65px;color:var(--teal)">{r.get("Username","")}</span><span style="color:{cc};min-width:62px;font-size:.75rem;">{ch}</span><span style="color:#CCDDEE;min-width:80px;">{r.get("ContactName","")}</span><span style="color:var(--muted);font-style:italic;font-size:.78rem;">{r.get("Outcome","")}</span></div>'
        st.markdown(f'<div class="op-card" style="max-height:280px;overflow-y:auto;">{feed_html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TAB: MANAGE LEADS + CSV IMPORT
# ─────────────────────────────────────────────
def tab_manage_leads():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📋 LEAD MANAGEMENT + IMPORT</h2>',
                unsafe_allow_html=True)
    df = load_leads()

    # ── CSV/EXCEL IMPORT ─────────────────────
    with st.expander("📥 IMPORT FROM CSV / EXCEL", expanded=False):
        uploaded = st.file_uploader("Upload file", type=["csv","xlsx","xls"], key="import_file")
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    raw = pd.read_csv(uploaded)
                else:
                    raw = pd.read_excel(uploaded)

                st.success(f"File loaded: {len(raw)} rows, {len(raw.columns)} columns")
                st.caption(f"Columns found: {', '.join(raw.columns.tolist())}")

                mapped = map_import_df(raw)
                url_cols = detect_url_columns(raw)
                if url_cols:
                    st.info(f"URL columns detected and preserved: {', '.join(url_cols)}")

                preview_cols = [c for c in ["ContactName","Company","Title","Phone","Email","Industry","Status"] if c in mapped.columns]
                st.dataframe(mapped[preview_cols].head(8), use_container_width=True)

                ic1, ic2 = st.columns(2)
                with ic1:
                    append_mode = st.radio("Import mode", ["Append to existing","Replace all leads"], index=0)
                with ic2:
                    default_step = st.selectbox("Start at sequence step", [1,2,3,4,5,6,7],
                                                format_func=lambda x: f"Step {x}: {get_step_info(x)['label']}")
                    mapped["SequenceStep"] = mapped["SequenceStep"].where(mapped["SequenceStep"]>0, default_step)

                if st.button("✅ CONFIRM IMPORT", use_container_width=True):
                    if append_mode == "Append to existing" and not df.empty:
                        # Merge: keep all columns from both
                        all_cols = list(set(df.columns.tolist() + mapped.columns.tolist()))
                        df_full  = df.reindex(columns=all_cols)
                        map_full = mapped.reindex(columns=all_cols)
                        combined = pd.concat([df_full, map_full], ignore_index=True)
                        # De-duplicate by LeadID
                        combined = combined.drop_duplicates(subset=["LeadID"], keep="last")
                    else:
                        combined = mapped

                    if save_leads(combined):
                        st.success(f"Imported {len(mapped)} leads ✓  (Total now: {len(combined)})")
                        st.rerun()

            except Exception as e:
                st.error(f"Import error: {e}")

    st.markdown("---")

    # ── ADD SINGLE LEAD ───────────────────────
with st.expander("➕ ADD SINGLE LEAD", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        cn = st.text_input("Contact Name *", key="new_contact_name")
        comp = st.text_input("Company *", key="new_company")
        title = st.text_input("Title", key="new_title")
    with c2:
        phone = st.text_input("Phone", key="new_phone")
        email = st.text_input("Email", key="new_email")
        ind = st.text_input("Industry", key="new_industry")
    with c3:
        rev = st.text_input("Revenue", key="new_revenue")
        status = st.selectbox("Status", STATUSES, key="new_status")
        step = st.selectbox(
            "Start Step",
            [1, 2, 3, 4, 5, 6, 7],
            format_func=lambda x: f"Step {x}: {get_step_info(x)['label']}",
            key="new_step",
        )

        if st.button("ADD LEAD", use_container_width=True):
            if not cn.strip() or not comp.strip():
                st.error("Name and Company are required.")
            else:
                new = {c:"" for c in CORE_LEAD_COLS}
                new.update({"LeadID":f"L-{int(time.time()*1000)}","ContactName":cn.strip(),
                            "Company":comp.strip(),"Title":title.strip(),"Phone":phone.strip(),
                            "Email":email.strip(),"Industry":ind.strip(),"Revenue":rev.strip(),
                            "Status":status,"SequenceStep":step,"Notes":"","LockedBy":"","LockTime":""})
                df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                if save_leads(df):
                    log_activity(new["LeadID"],cn.strip(),"","","Lead Created","")
                    st.success(f"'{cn}' added ✓"); st.rerun()

    # ── FILTER + VIEW ─────────────────────────
    st.markdown("---")
    f1,f2,f3 = st.columns(3)
    with f1: fst=st.multiselect("Status",STATUSES,default=STATUSES)
    with f2: fsp=st.multiselect("Step",list(range(1,8)),default=list(range(1,8)),
                                 format_func=lambda x:f"S{x}:{get_step_info(x)['label'][:12]}")
    with f3: fsq=st.text_input("Search",placeholder="Name / Company…")

    if not df.empty:
        v = df.copy()
        if fst: v=v[v["Status"].isin(fst)]
        if fsp: v=v[v["SequenceStep"].isin(fsp)]
        if fsq.strip(): s=fsq.lower(); v=v[v["ContactName"].str.lower().str.contains(s,na=False)|v["Company"].str.lower().str.contains(s,na=False)]
        display_cols = [c for c in ["LeadID","ContactName","Company","Industry","Status","SequenceStep","LastTouched","LockedBy"] if c in v.columns]
        st.dataframe(v[display_cols].sort_values("SequenceStep"), use_container_width=True, height=360)
        st.caption(f"{len(v)} leads shown · {len(df.columns)} columns preserved in sheet")

    # ── EDIT LEAD ─────────────────────────────
    st.markdown("---")
    st.markdown("**EDIT LEAD**")
    if not df.empty:
        opts = {f"{r['ContactName']} — {r['Company']} ({r['LeadID']})": r["LeadID"] for _,r in df.iterrows()}
        chosen = st.selectbox("Select Lead",["— select —"]+list(opts.keys()))
        if chosen != "— select —":
            row = df[df["LeadID"]==opts[chosen]].iloc[0]
            ec1,ec2 = st.columns(2)
            with ec1:
                es=st.selectbox("Status",STATUSES,index=STATUSES.index(str(row.get("Status","Cold"))))
                ep=st.selectbox("Step",list(range(1,8)),index=max(int(row.get("SequenceStep",1))-1,0),
                                 format_func=lambda x:f"{x}: {get_step_info(x)['label']}")
            with ec2:
                en=st.text_area("Notes",value=str(row.get("Notes","")),height=100)
            if st.button("💾 UPDATE LEAD",use_container_width=True):
                for col,val in [("Status",es),("SequenceStep",ep),("Notes",en),
                                 ("LastTouched",datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
                                 ("LastTouchedBy",st.session_state.username)]:
                    df.loc[df["LeadID"]==opts[chosen],col]=val
                if save_leads(df):
                    log_activity(opts[chosen],str(row.get("ContactName","")),"","",f"Manual Update → {es}",en)
                    st.success("Updated ✓"); st.rerun()

# ─────────────────────────────────────────────
#  TAB: ACTIVITY LOG
# ─────────────────────────────────────────────
def tab_activity():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">📋 TEAM ACTIVITY LOG</h2>', unsafe_allow_html=True)
    df   = load_activity()
    if df.empty: st.info("No activity yet."); return
    now  = datetime.now(timezone.utc); today = now.date()
    tdf  = df[pd.to_datetime(df["Timestamp"],utc=True).dt.date==today]

    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.metric("Total Actions",len(df))
    with k2: st.metric("Today's Actions",len(tdf))
    with k3: st.metric("Active Reps Today",tdf["Username"].nunique())
    with k4: st.metric("Dials Today",len(tdf[tdf.get("Channel",pd.Series())=="Call"]) if "Channel" in tdf.columns else 0)
    with k5: st.metric("Emails Today",len(tdf[tdf.get("Channel",pd.Series())=="Email"]) if "Channel" in tdf.columns else 0)

    st.markdown("---")
    f1,f2,f3 = st.columns(3)
    with f1: fu=st.selectbox("Operator",["All"]+sorted(df["Username"].dropna().unique().tolist()))
    with f2: fc=st.selectbox("Channel",["All"]+["Call","Email","LinkedIn"]) if "Channel" in df.columns else None
    with f3: fo=st.text_input("Search outcome/notes",placeholder="e.g. voicemail")

    show = df.copy()
    if fu != "All": show=show[show["Username"]==fu]
    if fc and fc != "All" and "Channel" in show.columns: show=show[show["Channel"]==fc]
    if fo.strip() and "Outcome" in show.columns:
        s=fo.lower(); show=show[show["Outcome"].str.lower().str.contains(s,na=False)|show["Notes"].str.lower().str.contains(s,na=False)]

    show = show.sort_values("Timestamp",ascending=False).head(300)
    dcols=[c for c in ["Timestamp","Username","ContactName","Channel","Outcome","Action","Notes"] if c in show.columns]
    st.dataframe(show[dcols], use_container_width=True, height=500)

# ─────────────────────────────────────────────
#  TAB: AI WORKSHOP
# ─────────────────────────────────────────────
def tab_ai():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">🤖 AI MESSAGE WORKSHOP</h2>', unsafe_allow_html=True)
    st.caption("Draft messages for any lead standalone — outside the live queue.")
   c1, c2 = st.columns(2)
with c1:
    contact = st.text_input("Contact Name", key="ai_contact_name")
    company = st.text_input("Company", key="ai_company")
    industry = st.text_input("Industry", key="ai_industry")
with c2:
    revenue = st.text_input("Revenue", key="ai_revenue")
    mtype = st.radio(
        "Type",
        ["Follow-up Email", "LinkedIn Message"],
        horizontal=True,
        key="ai_type",
    )
    notes = st.text_area("Context", height=80, key="ai_context")
    if st.button("⚡ GENERATE DRAFT",use_container_width=True):
        if not contact or not company: st.error("Need name and company.")
        else:
            row={"ContactName":contact,"Company":company,"Industry":industry,"Revenue":revenue,"Notes":notes}
            with st.spinner("Drafting…"):
                dtype = "email" if "Email" in mtype else "linkedin"
                subj, body = generate_ai_draft(row, dtype)
            if dtype == "email":
                st.markdown(sl("SUBJECT"), unsafe_allow_html=True)
                st.code(subj)
            st.markdown(sl("BODY"), unsafe_allow_html=True)
            st.markdown(f'<div class="op-card" style="border-color:var(--teal);font-size:.9rem;white-space:pre-wrap;">{body}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TAB: SETUP
# ─────────────────────────────────────────────
def tab_setup():
    st.markdown('<h2 style="color:#00A7A7;font-size:1.4rem;">⚙️ SYSTEM SETUP — START HERE</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="setup-card">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.55rem;font-weight:800;letter-spacing:.1em;color:#00A7A7;margin-bottom:.4rem;">ZERO → LIVE IN 5 STEPS</div>
        <div style="color:#8899AA;font-size:.84rem;">Follow in order. Bootstrapper handles the sheet setup.</div>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01","GOOGLE SHEET","#00A7A7",
         'Create a blank sheet at <a href="https://sheets.google.com" target="_blank" style="color:#00A7A7">sheets.google.com</a>. Add two tabs: <code>Leads</code> and <code>ActivityLog</code>.'),
        ("02","GCP SERVICE ACCOUNT","#F0A500",
         "Enable Sheets API + Drive API. Create a Service Account, download JSON key."),
        ("03","SHARE SHEET","#3DBA72",
         "Share your Sheet with the service account email as <strong>Editor</strong>."),
        ("04","STREAMLIT SECRETS","#9B72CF",
         f"""Paste into App Settings → Secrets:<br>
<pre style="background:#0B0F14;padding:.7rem;border-radius:4px;font-size:.7rem;color:#00A7A7;overflow-x:auto;">[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_ID/edit"
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\nKEY\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "name@project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

GEMINI_API_KEY = "your-gemini-key"

[email_identities.Gmail]
from_address = "you@gmail.com"
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "you@gmail.com"
smtp_password = "your-app-password"

[email_identities.OpsEmail]
from_address = "ops@masterofops.com"
smtp_host = "mail.masterofops.com"
smtp_port = 587
smtp_user = "ops@masterofops.com"
smtp_password = "your-password"</pre>"""),
        ("05","BOOTSTRAP & DEPLOY","#00A7A7",
         "Use buttons below. Bootstrap → Seed Demo → go to Dial Queue."),
    ]

    for num,title,color,body in steps:
        st.markdown(f'<div style="display:flex;gap:1rem;margin:.5rem 0;padding:1rem;background:var(--panel);border:1px solid var(--border);border-left:3px solid {color};border-radius:4px;"><div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.9rem;font-weight:800;color:{color};min-width:38px;line-height:1;">{num}</div><div><div style="font-family:\'Barlow Condensed\',sans-serif;font-size:.82rem;font-weight:700;letter-spacing:.1em;color:{color};margin-bottom:.3rem;">{title}</div><div style="font-size:.8rem;color:#CCDDEE;line-height:1.65;">{body}</div></div></div>', unsafe_allow_html=True)

    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("**Bootstrap Sheets**"); st.caption("Writes headers to both sheets.")
        if st.button("🚀 BOOTSTRAP",use_container_width=True):
            ok,msg = bootstrap_sheets()
            (st.success if ok else st.error)(msg)
    with c2:
        st.markdown("**Seed Demo Data**"); st.caption("8 leads + activity for dashboard testing.")
        if st.button("🧪 SEED DEMO",use_container_width=True):
            ok,msg = seed_demo_data()
            (st.success if ok else st.error)(msg)
    with c3:
        st.markdown("**Test Connection**"); st.caption("Confirm read/write works.")
        if st.button("🔌 TEST",use_container_width=True):
            df = load_leads()
            st.success(f"Connected ✓ — {len(df)} leads found.") if df is not None else st.error("Failed. Check secrets.")

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
    st.caption("To change the sequence, edit the SEQUENCE constant at the top of streamlit_app.py")

    st.markdown("---")
    st.markdown(f'<div style="font-size:.7rem;color:#4A5A6A;line-height:1.9;"><strong style="color:#8899AA;">Leads columns:</strong> {" · ".join(CORE_LEAD_COLS)}<br><strong style="color:#8899AA;">ActivityLog columns:</strong> {" · ".join(ACTIVITY_COLS)}<br><strong style="color:#8899AA;">Extra columns</strong> from CSV import are automatically preserved.</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────
def login_screen():
    st.markdown('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:70vh;gap:1rem;"><div style="font-family:\'Barlow Condensed\',sans-serif;font-size:3rem;font-weight:800;letter-spacing:.15em;color:#00A7A7;text-transform:uppercase;">⚙ Master of Ops</div><div style="font-size:.68rem;letter-spacing:.3em;color:#8899AA;text-transform:uppercase;margin-top:-.7rem;">Team Execution OS v3 — Auto-Dial Outbound Cockpit</div><div style="height:1px;width:280px;background:#263040;margin:.5rem 0;"></div></div>', unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown("**SELECT OPERATOR**")
        name=st.selectbox("",["— choose —"]+TEAM_USERS,label_visibility="collapsed")
        custom=st.text_input("Or enter your name",placeholder="Your name…")
        if st.button("🔓 ENTER THE OPS FLOOR",use_container_width=True):
            chosen=custom.strip() if custom.strip() else name
            if chosen and chosen!="— choose —":
                st.session_state.username=chosen; st.session_state.logged_in=True; st.rerun()
            else: st.error("Pick a name.")

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f'<div style="padding:1rem 0 1.3rem 0;border-bottom:1px solid var(--border);margin-bottom:.9rem;"><div class="logo-mark">⚙ Master of Ops</div><div class="logo-sub">Execution OS v3.0</div></div><div style="font-size:.68rem;color:#8899AA;margin-bottom:.8rem;">Operator: <span style="color:#00A7A7;font-weight:600">{st.session_state.username}</span></div>', unsafe_allow_html=True)

        session_state = "🟢 SESSION ACTIVE" if st.session_state.dial_session else "⚫ No session"
        st.markdown(f'<div style="font-size:.68rem;color:#8899AA;margin-bottom:.8rem;">{session_state}</div>', unsafe_allow_html=True)

        if st.button("⬅ Logout",use_container_width=True):
            if st.session_state.active_lead_id:
                df=load_leads()
                if not df.empty: df=unlock_lead(df,st.session_state.active_lead_id); save_leads(df)
            for k in ["logged_in","username","active_lead_id","ai_draft","ai_subject","dial_session","email_panel_open"]:
                st.session_state[k]=False if k in ["logged_in","dial_session","email_panel_open"] else ""
            st.rerun()

        st.markdown("---")
        for line in ["⚙️ Setup → Go Live","📞 Dial Queue → Cockpit","📊 Analytics → KPIs","📋 Manage → Import + Edit","📋 Activity → Full Log","🤖 AI Workshop"]:
            st.markdown(f'<div style="font-size:.76rem;color:#8899AA;padding:.18rem 0;">{line}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f'<div style="font-size:.58rem;color:#4A5A6A;line-height:1.7;text-align:center;">7-step sequence | Locks: 10 min<br>SMTP email | tel: dialer links<br>CSV/Excel import | URL columns</div>', unsafe_allow_html=True)

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
