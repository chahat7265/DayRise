
import html
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="DayRise | Small Steps, Big Dreams",
    page_icon="🌅",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
TASKS_FILE = BASE_DIR / "tasks.json"
NOTES_FILE = BASE_DIR / "notes.json"
MOODS_FILE = BASE_DIR / "moods.json"
SETTINGS_FILE = BASE_DIR / "settings.json"

TZ = ZoneInfo("Asia/Kolkata")  # change if your users are elsewhere
NOW = datetime.now(TZ)
TODAY = NOW.date()
TODAY_STR = TODAY.isoformat()

QUOTES = [
    "Small steps still move you forward.",
    "Start before you feel ready.",
    "Progress, not perfection.",
    "Rest is part of the work.",
    "One focused hour beats five distracted ones.",
    "Future you is watching. Make them proud.",
    "Done is better than perfect.",
]

PRIORITIES = ["High", "Medium", "Low"]
MOOD_SCORE = {"Low": 1, "Dreamy": 2, "Calm": 3, "Happy": 4, "Motivated": 5}
MOOD_OPTIONS = {
    "🌞 Happy": "Happy",
    "🌷 Calm": "Calm",
    "🌧️ Low": "Low",
    "⚡ Motivated": "Motivated",
    "🌙 Dreamy": "Dreamy",
}
MOOD_MESSAGES = {
    "Happy": "Keep this light close. ✨",
    "Calm": "You don't have to rush what's growing. 🌿",
    "Low": "You're allowed to rest. One hard day isn't your whole story. ♡",
    "Motivated": "Put that energy into one small step. 🌟",
    "Dreamy": "Keep dreaming while you figure things out. 🌙",
}


# ---------------- STORAGE HELPERS ----------------

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_tasks():
    data = load_json(TASKS_FILE, [])
    if not isinstance(data, list):
        return []
    tasks = []
    for item in data:
        if isinstance(item, str):
            item = {"text": item}
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            tasks.append({
                "id": str(item.get("id") or uuid.uuid4().hex),
                "text": item["text"],
                "done": bool(item.get("done", False)),
                "priority": item.get("priority", "Medium"),
                "done_date": item.get("done_date"),
            })
    return tasks


def save_tasks():
    save_json(TASKS_FILE, st.session_state.tasks)


# ---------------- TASK ACTIONS ----------------

def add_task_text(text, priority="Medium"):
    st.session_state.tasks.append({
        "id": uuid.uuid4().hex,
        "text": text,
        "done": False,
        "priority": priority,
        "done_date": None,
    })
    save_tasks()


def add_task_from_form():
    text = st.session_state.get("new_task", "").strip()
    if not text:
        st.toast("Write a task first.", icon="✍️")
        return
    add_task_text(text, st.session_state.get("new_priority", "Medium"))
    st.toast("Task added. Let's go!", icon="🌱")


def add_suggestion_as_task():
    text = st.session_state.get("suggestion_task", "").strip()
    if text:
        add_task_text(text)
        st.toast("Added to your list.", icon="✅")


def toggle_task(task_id):
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            task["done"] = st.session_state[f"task_{task_id}"]
            task["done_date"] = TODAY_STR if task["done"] else None
            break
    save_tasks()
    tasks = st.session_state.tasks
    if tasks and all(t["done"] for t in tasks):
        st.session_state.celebrate = True
    elif st.session_state[f"task_{task_id}"]:
        st.toast("Nice, one more done!", icon="🔥")


def delete_task(task_id):
    st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != task_id]
    save_tasks()


def current_streak(tasks):
    days = {t["done_date"] for t in tasks if t.get("done_date")}
    day = TODAY
    if day.isoformat() not in days:
        day -= timedelta(days=1)
    streak = 0
    while day.isoformat() in days:
        streak += 1
        day -= timedelta(days=1)
    return streak


# ---------------- SESSION INIT ----------------

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "notes" not in st.session_state:
    notes = load_json(NOTES_FILE, [])
    st.session_state.notes = notes if isinstance(notes, list) else []
if "moods" not in st.session_state:
    moods = load_json(MOODS_FILE, {})
    st.session_state.moods = moods if isinstance(moods, dict) else {}
if "settings" not in st.session_state:
    settings = load_json(SETTINGS_FILE, {})
    st.session_state.settings = settings if isinstance(settings, dict) else {}

if st.session_state.pop("celebrate", False):
    st.balloons()
    st.toast("All tasks done. You're unstoppable!", icon="🎉")


# ---------------- STYLES ----------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Sora:wght@600;700;800&display=swap');

:root {
  --ink: #14122B;
  --panel: #1F1B42;
  --panel-2: #2A2557;
  --violet: #7C5CFF;
  --coral: #FF6B9A;
  --amber: #FFB23E;
  --mint: #3DE0B5;
  --text: #F3F0FF;
  --muted: #A9A3D1;
}

html, body, .stApp, [class*="st-"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3, .display { font-family: 'Sora', sans-serif !important; letter-spacing: -0.02em; }

.stApp {
  background:
    radial-gradient(900px 500px at 90% -10%, rgba(124, 92, 255, .25), transparent 60%),
    radial-gradient(700px 400px at -10% 30%, rgba(255, 107, 154, .12), transparent 60%),
    var(--ink);
  color: var(--text);
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1180px; padding-top: 1.5rem; padding-bottom: 4rem; }

/* ---------- Hero: the one big animated moment ---------- */
.hero {
  position: relative; overflow: hidden; border-radius: 28px;
  padding: 56px 44px 96px; margin-bottom: 26px; min-height: 280px;
  background: linear-gradient(180deg, #2A1F5C 0%, #6A3F93 50%, #FF6B9A 100%);
  background-size: 100% 160%; animation: sky 2.4s ease-out both;
}
.hero::after {
  content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 52px; z-index: 3;
  background: var(--ink);
  clip-path: polygon(0 62%, 10% 42%, 26% 64%, 44% 34%, 60% 58%, 78% 36%, 100% 56%, 100% 100%, 0 100%);
}
.sun {
  position: absolute; right: 9%; bottom: -78px; width: 190px; height: 190px; z-index: 1;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 38%, #FFE9A8, #FFB23E 58%, #FF8A4C);
  box-shadow: 0 0 90px 36px rgba(255, 178, 62, .45);
  animation: rise 2.2s cubic-bezier(.2, .8, .2, 1) both, glow 6s ease-in-out 2.2s infinite alternate;
}
.hero-text { position: relative; z-index: 2; max-width: 620px; }
.hero h1 { color: #fff; font-size: clamp(32px, 5vw, 54px); line-height: 1.05; margin: 0 0 10px; }
.hero .date { color: #FFE9C7; font-size: 15px; margin: 0 0 4px; }
.hero .sub { color: #fff; opacity: .88; font-size: 17px; margin: 0; }

@keyframes rise { from { transform: translateY(190px); opacity: .3; } to { transform: none; opacity: 1; } }
@keyframes glow { from { box-shadow: 0 0 80px 28px rgba(255, 178, 62, .35); } to { box-shadow: 0 0 120px 50px rgba(255, 178, 62, .55); } }
@keyframes sky { from { background-position: 0 100%; } to { background-position: 0 0; } }

/* ---------- Stat cards ---------- */
.stat {
  background: var(--panel); border: 1px solid rgba(255, 255, 255, .07);
  border-radius: 20px; padding: 20px 22px; min-height: 128px;
  transition: transform .2s ease, border-color .2s ease;
}
.stat:hover { transform: translateY(-3px); border-color: rgba(255, 178, 62, .5); }
.stat .label { color: var(--muted); font-size: 14px; }
.stat .num { font-family: 'Sora', sans-serif; font-size: 40px; font-weight: 800; line-height: 1.2; margin-top: 6px; }
.stat .foot { color: var(--muted); font-size: 13px; margin-top: 4px; }
.num-amber { color: var(--amber); }
.num-mint { color: var(--mint); }
.num-coral { color: var(--coral); }
.num-violet { color: #A996FF; }

/* ---------- Progress ring (animates from 0 to value) ---------- */
@property --p { syntax: '<number>'; inherits: false; initial-value: 0; }
.ring-wrap { display: flex; align-items: center; gap: 22px; }
.ring {
  --p: 0; width: 132px; height: 132px; border-radius: 50%; flex: none;
  display: grid; place-items: center;
  background: conic-gradient(var(--amber) calc(var(--p) * 1%), rgba(255, 255, 255, .09) 0);
  animation: fill 1.6s cubic-bezier(.2, .8, .2, 1) .3s forwards;
}
@keyframes fill { to { --p: var(--target); } }
.ring span {
  width: 102px; height: 102px; border-radius: 50%; background: var(--panel);
  display: grid; place-items: center; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 26px;
}

/* ---------- Cards, quote, chips ---------- */
.card {
  background: var(--panel); border: 1px solid rgba(255, 255, 255, .07);
  border-radius: 20px; padding: 22px 24px;
}
.quote { border-left: 4px solid var(--coral); background: var(--panel-2); border-radius: 6px 20px 20px 6px; padding: 20px 24px; }
.quote p { font-family: 'Sora', sans-serif; font-size: 20px; margin: 0; line-height: 1.4; }
.quote small { color: var(--muted); }
.chip { font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 999px; display: inline-block; margin-top: 8px; }
.chip-high { background: rgba(255, 107, 154, .18); color: var(--coral); }
.chip-medium { background: rgba(255, 178, 62, .18); color: var(--amber); }
.chip-low { background: rgba(61, 224, 181, .16); color: var(--mint); }
.note-date { color: var(--coral); font-size: 13px; font-weight: 700; }

/* ---------- Streamlit widget polish ---------- */
button[data-baseweb="tab"] { font-family: 'Sora', sans-serif; font-weight: 600; font-size: 16px; padding: 12px 18px; }
div[data-baseweb="tab-highlight"] { background: linear-gradient(90deg, var(--coral), var(--amber)) !important; height: 3px !important; }

div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {
  border-radius: 999px; min-height: 46px; font-weight: 700;
  border: 1px solid rgba(255, 255, 255, .15); transition: transform .15s ease, box-shadow .15s ease;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover, div.stDownloadButton > button:hover {
  transform: translateY(-2px); box-shadow: 0 8px 22px rgba(255, 107, 154, .25);
}
button[kind="primary"], button[kind="primaryFormSubmit"],
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {
  background: linear-gradient(90deg, var(--coral), var(--amber)) !important; color: #2A1235 !important; border: none !important;
}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, div[data-baseweb="select"] > div {
  border-radius: 14px; background: var(--panel); border-color: rgba(255, 255, 255, .1);
}
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 18px; }
[data-testid="stSidebar"] { background: #100E24; }

@media (max-width: 640px) {
  .hero { padding: 36px 22px 90px; }
  .sun { width: 130px; height: 130px; right: 4%; bottom: -58px; }
  .stat .num { font-size: 32px; }
}
@media (prefers-reduced-motion: reduce) {
  .hero, .sun, .ring { animation: none !important; }
  .ring { --p: var(--target); }
  .stat, div.stButton > button { transition: none; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def block(markup):
    """Flatten HTML so Markdown doesn't treat indented lines as code."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("### 🌅 DayRise")
    name = st.text_input(
        "What should we call you?",
        value=st.session_state.settings.get("name", ""),
        placeholder="Your name",
    ).strip()
    if name != st.session_state.settings.get("name", ""):
        st.session_state.settings["name"] = name
        save_json(SETTINGS_FILE, st.session_state.settings)
    st.caption("Small steps. Big dreams.")


# ---------------- DERIVED DATA ----------------

tasks = st.session_state.tasks
total = len(tasks)
completed = sum(1 for t in tasks if t["done"])
pending = total - completed
percent = round(completed / total * 100) if total else 0
streak = current_streak(tasks)

hour = NOW.hour
if hour < 12:
    greeting = "Good morning"
elif hour < 17:
    greeting = "Good afternoon"
elif hour < 21:
    greeting = "Good evening"
else:
    greeting = "Still up"
who = f", {html.escape(name)}" if name else ""

if total == 0:
    subline = "Add your first task and start the day."
elif pending == 0:
    subline = "Everything is done. Enjoy the sunrise."
else:
    subline = f"{completed} of {total} tasks done. {pending} to go."

# ---------------- HERO ----------------

block(f"""
<div class="hero">
  <div class="sun"></div>
  <div class="hero-text">
    <h1>{greeting}{who} 🌅</h1>
    <p class="date">{TODAY.strftime("%A, %d %B %Y")}</p>
    <p class="sub">{subline}</p>
  </div>
</div>
""")

# ---------------- TABS ----------------

tab_home, tab_tasks, tab_focus, tab_notes, tab_mood = st.tabs(
    ["🏠 Home", "📋 Tasks", "⏱️ Focus", "📓 Notes", "🌷 Mood"]
)

# ================= HOME =================
with tab_home:
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "Total tasks", total, "num-violet", "Every goal starts somewhere"),
        (c2, "Completed", completed, "num-mint", "Look at you go"),
        (c3, "Still to do", pending, "num-coral", "One step at a time"),
        (c4, "Day streak 🔥", streak, "num-amber", "Days with a finished task"),
    ]
    for col, label, value, cls, foot in stats:
        with col:
            block(f"""
            <div class="stat">
              <div class="label">{label}</div>
              <div class="num {cls}">{value}</div>
              <div class="foot">{foot}</div>
            </div>
            """)

    st.write("")
    left, right = st.columns([1, 1.3])

    with left:
        block(f"""
        <div class="card">
          <div class="ring-wrap">
            <div class="ring" style="--target:{percent}"><span>{percent}%</span></div>
            <div>
              <div class="display" style="font-size:20px;font-weight:700;">Today's progress</div>
              <div style="color:var(--muted);font-size:14px;margin-top:6px;">
                {completed} of {total} tasks complete
              </div>
            </div>
          </div>
        </div>
        """)

    with right:
        st.markdown("**Tasks finished this week**")
        last7 = [TODAY - timedelta(days=i) for i in range(6, -1, -1)]
        counts = [sum(1 for t in tasks if t.get("done_date") == d.isoformat()) for d in last7]
        week_df = pd.DataFrame({"Tasks done": counts}, index=pd.to_datetime(last7))
        st.bar_chart(week_df, color="#FFB23E", height=200)

    quote = QUOTES[TODAY.toordinal() % len(QUOTES)]
    st.write("")
    block(f"""
    <div class="quote">
      <p>"{quote}"</p>
      <small>Today's reminder</small>
    </div>
    """)

    st.write("")
    st.subheader("Find your next step")
    f1, f2, f3 = st.columns(3)
    with f1:
        energy = st.selectbox("Energy level", ["High", "Medium", "Low"], index=1)
    with f2:
        time_available = st.selectbox("Time you have", ["30 minutes", "1 hour", "2 hours", "4+ hours"])
    with f3:
        goal = st.selectbox("Focus area", ["Academics", "Programming", "Fitness", "Career", "Personal Development"])

    if st.button("Find my next step", type="primary", use_container_width=True):
        if energy == "Low":
            tip = f"Pick one gentle {goal.lower()} task and rest after it."
        elif energy == "High" and goal == "Programming":
            tip = "Great time for deep coding or DSA practice."
        elif time_available == "30 minutes":
            tip = f"One small {goal.lower()} task, 25 focused minutes."
        elif time_available == "4+ hours":
            tip = f"Plan a long {goal.lower()} session with breaks."
        else:
            tip = f"Start with one clear {goal.lower()} priority at a steady pace."
        st.session_state.suggestion = tip
        st.session_state.suggestion_task = f"{goal}: {tip}"

    if st.session_state.get("suggestion"):
        st.success(st.session_state.suggestion)
        st.button("＋ Add this to my tasks", on_click=add_suggestion_as_task)

# ================= TASKS =================
with tab_tasks:
    st.subheader("My to-do list")

    with st.form("add_task_form", clear_on_submit=True):
        t1, t2 = st.columns([4, 1])
        with t1:
            st.text_input("What do you want to get done?", key="new_task",
                          placeholder="Practice DSA, read a chapter, take a walk...")
        with t2:
            st.selectbox("Priority", PRIORITIES, index=1, key="new_priority")
        st.form_submit_button("＋ Add to my list", type="primary",
                              on_click=add_task_from_form, use_container_width=True)

    view = st.radio("Show", ["All", "To do", "Done"], horizontal=True, label_visibility="collapsed")
    order = {"High": 0, "Medium": 1, "Low": 2}
    shown = sorted(tasks, key=lambda t: (t["done"], order.get(t["priority"], 1)))
    if view == "To do":
        shown = [t for t in shown if not t["done"]]
    elif view == "Done":
        shown = [t for t in shown if t["done"]]

    if not shown:
        st.info("Nothing here yet. Add a task above to get started.")

    for task in shown:
        with st.container(border=True):
            a, b, c = st.columns([6, 1.4, 0.8])
            with a:
                st.checkbox(task["text"], value=task["done"], key=f"task_{task['id']}",
                            on_change=toggle_task, args=(task["id"],))
            with b:
                p = task.get("priority", "Medium")
                block(f'<span class="chip chip-{p.lower()}">{p}</span>')
            with c:
                st.button("🗑️", key=f"del_{task['id']}", help="Delete task",
                          on_click=delete_task, args=(task["id"],))

# ================= FOCUS =================
with tab_focus:
    st.subheader("Focus timer")
    st.caption("Work for 25 minutes, then take a 5 minute break.")
    components.html("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@500;700&family=Sora:wght@700&display=swap');
  body { margin:0; font-family:'DM Sans',sans-serif; color:#F3F0FF; display:flex; flex-direction:column; align-items:center; }
  .modes button, .ctrl button { font-family:inherit; font-weight:700; border-radius:999px; padding:10px 20px; border:1px solid rgba(255,255,255,.2); background:#1F1B42; color:#F3F0FF; cursor:pointer; margin:0 4px; }
  .modes button.on { background:#7C5CFF; border-color:#7C5CFF; }
  .ctrl .go { background:linear-gradient(90deg,#FF6B9A,#FFB23E); color:#2A1235; border:none; }
  .dial { position:relative; width:240px; height:240px; margin:20px 0; }
  svg { transform:rotate(-90deg); }
  .time { position:absolute; inset:0; display:grid; place-items:center; font-family:'Sora',sans-serif; font-size:52px; }
  .msg { height:22px; color:#A9A3D1; font-size:14px; }
</style>
<div class="modes"><button id="m25" class="on">Focus 25</button><button id="m5">Break 5</button></div>
<div class="dial">
  <svg width="240" height="240" viewBox="0 0 240 240">
    <circle cx="120" cy="120" r="104" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="14"/>
    <circle id="arc" cx="120" cy="120" r="104" fill="none" stroke="#FFB23E" stroke-width="14"
            stroke-linecap="round" stroke-dasharray="653.45" stroke-dashoffset="0"/>
  </svg>
  <div class="time" id="time">25:00</div>
</div>
<div class="ctrl"><button class="go" id="go">Start</button><button id="reset">Reset</button></div>
<div class="msg" id="msg"></div>
<script>
  const C = 653.45; let total = 1500, left = total, timer = null;
  const $ = id => document.getElementById(id);
  function draw() {
    const m = String(Math.floor(left / 60)).padStart(2, '0'), s = String(left % 60).padStart(2, '0');
    $('time').textContent = m + ':' + s;
    $('arc').style.strokeDashoffset = C * (1 - left / total);
  }
  function stop() { clearInterval(timer); timer = null; $('go').textContent = 'Start'; }
  function setMode(sec, id) {
    stop(); total = left = sec; $('msg').textContent = '';
    $('m25').classList.toggle('on', id === 'm25'); $('m5').classList.toggle('on', id === 'm5'); draw();
  }
  $('m25').onclick = () => setMode(1500, 'm25');
  $('m5').onclick = () => setMode(300, 'm5');
  $('reset').onclick = () => { stop(); left = total; $('msg').textContent = ''; draw(); };
  $('go').onclick = () => {
    if (timer) { stop(); return; }
    $('go').textContent = 'Pause'; $('msg').textContent = 'Stay with one thing.';
    timer = setInterval(() => {
      left--; draw();
      if (left <= 0) { stop(); $('msg').textContent = 'Session complete. Nice work!'; }
    }, 1000);
  };
  draw();
</script>
""", height=420)

# ================= NOTES =================
with tab_notes:
    st.subheader("Little notes to myself")

    with st.form("note_form", clear_on_submit=True):
        note_title = st.text_input("Title", placeholder="A reminder, an idea, a win...")
        note_text = st.text_area("What's on your mind?", height=120)
        save_note = st.form_submit_button("Save note", type="primary")
        if save_note:
            if note_text.strip():
                st.session_state.notes.append({
                    "id": uuid.uuid4().hex,
                    "title": note_title.strip() or "A little thought",
                    "text": note_text.strip(),
                    "date": TODAY_STR,
                })
                save_json(NOTES_FILE, st.session_state.notes)
                st.toast("Note saved.", icon="📝")
            else:
                st.warning("Write something in the note first.")

    if st.session_state.notes:
        st.download_button(
            "Download my notes",
            data=json.dumps(st.session_state.notes, indent=2, ensure_ascii=False),
            file_name="dayrise_notes.json",
            mime="application/json",
        )
        for note in reversed(st.session_state.notes):
            with st.container(border=True):
                block(f'<div class="note-date">{html.escape(note.get("date", ""))}</div>')
                st.markdown(f"#### {note.get('title', 'A little thought')}")
                st.write(note.get("text", ""))
                if st.button("Delete note", key=f"delnote_{note['id']}"):
                    st.session_state.notes = [n for n in st.session_state.notes if n["id"] != note["id"]]
                    save_json(NOTES_FILE, st.session_state.notes)
                    st.rerun()
    else:
        st.info("Your notes will show up here. Write your first one above.")

# ================= MOOD =================
with tab_mood:
    st.subheader("How are you feeling today?")
    st.caption("No pressure to be productive every day.")

    saved = st.session_state.moods.get(TODAY_STR, "Dreamy")
    labels = list(MOOD_OPTIONS.keys())
    default_idx = next((i for i, l in enumerate(labels) if MOOD_OPTIONS[l] == saved), 4)
    picked = st.selectbox("Pick the vibe that feels like you", labels, index=default_idx)

    if st.button("Save today's mood", type="primary"):
        value = MOOD_OPTIONS[picked]
        st.session_state.moods[TODAY_STR] = value
        save_json(MOODS_FILE, st.session_state.moods)
        st.success(f"Saved: {value}")
        st.info(MOOD_MESSAGES[value])
    else:
        st.caption(MOOD_MESSAGES.get(saved, ""))

    mood_rows = {
        pd.to_datetime(day): MOOD_SCORE[m]
        for day, m in st.session_state.moods.items()
        if m in MOOD_SCORE
    }
    if mood_rows:
        st.markdown("**Your mood trend** (1 = Low, 5 = Motivated)")
        mood_df = pd.DataFrame({"Mood": pd.Series(mood_rows).sort_index()})
        st.line_chart(mood_df, color="#FF6B9A", height=220)
    else:
        st.caption("Save a mood to start your trend chart.")

# ---------------- FOOTER ----------------

st.divider()
st.caption("DayRise 🌅 | Small steps. Big dreams. Made with care ♡")