import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="A Standard American Life — Health Timeline", page_icon="🧭", layout="wide")

# -----------------------------
# Background (parchment + 2-layer mountains that rise to the right)
# -----------------------------
MOUNTAINS_SVG = """
<svg viewBox="0 0 1200 320" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <!-- back/lighter range -->
  <path d="M0,260
           C140,235 270,250 380,220
           C520,180 610,215 740,185
           C880,150 980,210 1090,165
           C1150,140 1185,130 1200,120
           L1200,320 L0,320 Z"
        fill="rgba(0,0,0,0.05)"/>
  <!-- front/darker range (rises to the right) -->
  <path d="M0,295
           C160,270 290,300 410,265
           C540,230 650,285 790,240
           C925,200 1000,275 1120,215
           C1170,185 1190,170 1200,150
           L1200,320 L0,320 Z"
        fill="rgba(0,0,0,0.10)"/>
</svg>
"""

def engine_svg(color_hex: str) -> str:
    return f"""
<svg width="46" height="46" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 18h18l4 6h6v8h-4l-2 6h-2v8H22v-6h-6v-8h4l2-6h2z"
        fill="{color_hex}" opacity="0.95"/>
  <path d="M24 28h16v16H24z" fill="white" opacity="0.25"/>
</svg>
"""

st.markdown(
    f"""
<style>
.stApp {{
  background:
    radial-gradient(900px 520px at 20% 0%, rgba(0,0,0,0.05), rgba(0,0,0,0.00) 60%),
    linear-gradient(180deg, #fbf7ef 0%, #f7f1e6 100%);
  color: #1f1f1f;
}}
.lrp-mountains {{
  position: fixed;
  left: 0; right: 0; bottom: -18px;
  height: 270px;
  pointer-events: none;
  opacity: 0.75;   /* darker + more visible */
  z-index: 0;
}}
.block-container {{
  position: relative;
  z-index: 1;
  padding-bottom: 170px;
  max-width: 1650px;
  padding-top: 1.2rem;
}}

.h1 {{
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -0.02em;
  text-align: center;
  margin: 6px 0 0 0;
}}
.sub {{
  text-align: center;
  font-size: 18px;
  opacity: 0.70;
  margin: 4px 0 10px 0;
}}

.card {{
  border-radius: 18px;
  background: rgba(255,255,255,0.93);
  border: 1px solid rgba(0,0,0,0.08);
  padding: 18px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.06);
}}
.card h3 {{
  margin: 0 0 10px 0;
  font-size: 22px;
}}
.small {{
  font-size: 14px;
  opacity: 0.82;
}}

.bullets {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
  font-size: 18px;
  line-height: 1.25;
}}
.bullets .b {{
  display: flex;
  gap: 10px;
}}
.dot {{
  width: 9px;
  height: 9px;
  border-radius: 99px;
  background: rgba(0,0,0,0.55);
  margin-top: 8px;
  flex: 0 0 9px;
}}

/* Band nav: symmetrical + tight */
.bandrow {{
  display:flex;
  justify-content:center;
  align-items:center;
  gap: 12px;
  margin: 12px 0 14px 0;
}}
.bandpill {{
  font-size: 22px;
  font-weight: 850;
  min-width: 92px;
  text-align:center;
}}
.navbtn > div > button {{
  border-radius: 14px !important;
  padding: 6px 12px !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
  background: rgba(255,255,255,0.92) !important;
}}

.hdr {{
  display:flex;
  align-items:center;
  gap: 10px;
}}
.hdr .ico {{
  width: 28px; height: 28px;
  display:flex; align-items:center; justify-content:center;
  border-radius: 8px;
  background: rgba(0,0,0,0.05);
  font-weight: 800;
}}

.kpi-title {{
  font-size: 18px;
  font-weight: 900;
  margin: 0;
}}
.kpi-row {{
  display:flex;
  gap: 14px;
  align-items:center;
}}
.kpi-sub {{
  font-size: 14px;
  opacity: 0.78;
  margin-top: 4px;
}}
.sep {{
  height:1px;
  background:rgba(0,0,0,0.08);
  margin: 14px 0;
}}
</style>

<div class="lrp-mountains">{MOUNTAINS_SVG}</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def band_label_for_age(age: int) -> str:
    a0 = (age // 5) * 5
    a1 = a0 + 5
    a0 = max(0, a0)
    a1 = min(95, a1)
    return f"{a0}-{a1}"

# SAL curve (keep your tuned anchors)
def sal_capacity(age: float) -> float:
    pts = np.array([
        [0,  88],
        [15, 86],
        [25, 80],
        [35, 73],
        [45, 66],
        [50, 55],  # ~Functional by 50
        [55, 48],
        [60, 42],
        [65, 36],
        [70, 26],
        [75, 16],
        [77, 12],
    ], dtype=float)
    x = pts[:, 0]
    y = pts[:, 1]
    return float(np.interp(age, x, y))

# SAL Fit Zone color rules (per your instruction)
# - Yellow at 20–25
# - Red at 30–35 and onward
# - Deeper red later
def fit_zone_color_for_sal(age: float) -> str:
    if age < 20:
        return "#39b66a"  # green
    if age < 30:
        return "#d6a400"  # yellow
    if age < 50:
        return "#c63b3b"  # red
    return "#9d1f1f"      # deeper red later

# SAL Check Engine rules (delayed vs Fit Zone)
# - Yellow at 30–35, 35–40, 40–45
# - Red at 45–50 through 77
def check_engine_color_for_sal(age: float) -> tuple[str, str]:
    if age < 30:
        return "Green", "#39b66a"
    if age < 45:
        return "Yellow", "#d6a400"
    return "Red", "#c63b3b"

# -----------------------------
# Copy by band (no placeholders)
# -----------------------------
LEFT_STAGE = {
    "0-5": ("Standard Living", [
        "Movement is natural; play provides daily training",
        "Sleep is abundant; recovery is effortless",
        "Food habits form early; sugar normalizes fast",
        "Screens begin to replace outdoor hours",
    ]),
    "5-10": ("Standard Living", [
        "Recess still helps; sitting begins to dominate",
        "Sports become seasonal—not daily movement",
        "Ultra-processed snacks become routine",
        "Sleep starts slipping as schedules grow",
    ]),
    "10-15": ("Standard Living", [
        "Activity drops; posture and mobility tighten",
        "Social stress rises; comfort eating increases",
        "Strength work is rare; peak potential is missed",
        "Sleep becomes inconsistent; energy dips appear",
    ]),
    "15-20": ("Standard Living", [
        "Sedentary time spikes; screens win the day",
        "Fast food + sugar drinks feel “normal”",
        "Injuries linger without strength foundations",
        "Sleep debt becomes lifestyle",
    ]),
    "20-25": ("Standard Living", [
        "Work/life sitting begins to dominate",
        "Fitness becomes optional; consistency fades",
        "Alcohol + late nights blunt recovery",
        "Weight gain starts quietly",
    ]),
    "25-30": ("Standard Living", [
        "Energy drops; “no time” becomes the reason",
        "Muscle loss starts; strength training is absent",
        "Stress climbs; sleep quality erodes",
        "Biomarkers start drifting—unnoticed",
    ]),
    "30-35": ("Standard Living", [
        "Metabolic health slips; inflammation rises",
        "Back/hip/shoulder issues become common",
        "Fat gain accelerates; muscle loss continues",
        "Cardio fitness falls below functional needs",
    ]),
    "35-40": ("Standard Living", [
        "Chronic aches become “normal” baseline",
        "Blood pressure/markers creep upward",
        "Recovery slows; minor setbacks linger",
        "Fitness gaps show up in daily life",
    ]),
    "40-45": ("Medicalized Living", [
        "First real warnings: labs, BP, sleep apnea risk",
        "Pain management replaces performance goals",
        "Movement becomes cautious; joints “protected”",
        "Stress compounds; fatigue becomes baseline",
    ]),
    "45-50": ("Medicalized Living", [
        "Multiple medications begin; side effects stack quietly",
        "Sleep fragments; fatigue becomes baseline",
        "Movement becomes cautious; joints “protected”",
        "Pain management replaces performance",
    ]),
    "50-55": ("Medicalized Living", [
        "Conditions collect: metabolic, joints, mood, sleep",
        "Strength drops; falls risk begins to rise",
        "Social range narrows with energy",
        "More appointments; less capacity",
    ]),
    "55-60": ("Medicalized Living", [
        "Polypharmacy becomes common; tradeoffs increase",
        "Balance declines if untrained",
        "Recovery becomes slow; setbacks compound",
        "Independence starts to feel fragile",
    ]),
    "60-65": ("Medicalized Living", [
        "Hospital visits become more likely events",
        "Mobility shrinks; stairs become a barrier",
        "Sarcopenia accelerates without resistance training",
        "Fear of injury limits activity further",
    ]),
    "65-70": ("Frail Transition", [
        "Falls become a turning point risk",
        "Frailty arrives sooner than expected",
        "Care needs increase; independence declines",
        "Life becomes smaller and more cautious",
    ]),
    "70-75": ("Frail", [
        "Capacity drops steeply; reserves are thin",
        "Chronic conditions drive daily decisions",
        "Simple tasks require planning and help",
        "More time managing health than living life",
    ]),
    "75-80": ("Frail", [
        "High risk of hospitalization and cascade decline",
        "Assistive devices become common",
        "Loss of autonomy becomes real",
        "Caregiver dependence increases",
    ]),
}

RIGHT_STAGE = {
    "0-5": ("Set the trajectory early", "Protect sleep; build active play; limit ultra-processed foods"),
    "5-10": ("Keep movement daily", "Sports + play + strength basics; build simple routines"),
    "10-15": ("Prevent the slide", "Strength + sleep + protein; reduce sugar and screens"),
    "15-20": ("Build the base", "Train strength; develop Zone 2; make sleep non-negotiable"),
    "20-25": ("Guard against drift", "Consistency beats intensity; lift + walk + sleep"),
    "25-30": ("Stop the quiet decline", "Strength 2–3x/wk; Zone 2; reduce alcohol; track labs"),
    "30-35": ("Reverse early compounding", "Progressive strength; protein; steps; stress hygiene"),
    "35-40": ("Reclaim capacity", "Strength + balance + VO₂ work; simplify nutrition"),
    "40-45": ("Intervene decisively", "Train like medicine; fix sleep; reduce visceral fat"),
    "45-50": ("Rebuild the engine", "Strength + Zone 2; manage stress; monitor biomarkers"),
    "50-55": ("Prevent cascade", "Strength + mobility + balance; simplify meds; protect sleep"),
    "55-60": ("Maintain independence", "Train legs + balance; protein; fall-proof your life"),
    "60-65": ("Protect autonomy", "Strength + gait + balance; social + purpose"),
    "65-70": ("Delay frailty", "High-value training; prevent falls; simplify obligations"),
    "70-75": ("Preserve function", "Small daily wins; safe strength; support systems"),
    "75-80": ("Reduce risk", "Fall prevention; mobility support; maintain routines"),
}

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="h1">A Standard American Life — Health Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">The default path — gradual drift, then compounding decline</div>', unsafe_allow_html=True)

# -----------------------------
# Band navigation (true centered grouping)
# -----------------------------
if "age" not in st.session_state:
    st.session_state.age = 22  # 20–25

# Make a 5-column row so the center group is perfectly centered on the page
g1, g2, g3, g4, g5 = st.columns([2.2, 0.8, 1.2, 0.8, 2.2], vertical_alignment="center")

with g2:
    st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
    if st.button("←", key="prev_band"):
        st.session_state.age = max(0, st.session_state.age - 5)
    st.markdown("</div>", unsafe_allow_html=True)

with g3:
    band = band_label_for_age(st.session_state.age)
    st.markdown(f"<div class='bandrow'><div class='bandpill'>{band}</div></div>", unsafe_allow_html=True)

with g4:
    st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
    if st.button("→", key="next_band"):
        st.session_state.age = min(92, st.session_state.age + 5)
    st.markdown("</div>", unsafe_allow_html=True)

age = st.session_state.age
band = band_label_for_age(age)

# -----------------------------
# Values
# -----------------------------
base = sal_capacity(age)
zone_score = clamp(base, 0, 100)

zone_color = fit_zone_color_for_sal(age)  # SAL rule (age-driven)
engine_name, engine_color = check_engine_color_for_sal(age)

# Copy
left_title, left_bullets = LEFT_STAGE.get(
    band,
    ("Standard Living", [
        "Health drifts quietly without a plan",
        "Strength fades if untrained",
        "Sleep degrades under stress",
        "Food environment wins by default",
    ])
)
diag_text, rx_text = RIGHT_STAGE.get(band, ("Know your baseline", "Small levers → big compounding"))

# -----------------------------
# Layout
# -----------------------------
colL, colC, colR = st.columns([1.05, 2.70, 1.05], gap="large")

with colL:
    bullets_html = "".join([f"<div class='b'><div class='dot'></div><div>{t}</div></div>" for t in left_bullets])
    st.markdown(
        f"""
<div class="card">
  <h3>{left_title}</h3>
  <div class="bullets">{bullets_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with colC:
    xs = np.arange(0, 78, 1)
    ys = np.array([sal_capacity(x) for x in xs])

    a0 = (age // 5) * 5
    seg_x = np.arange(a0, min(a0 + 5, 77) + 1, 1)
    seg_y = np.array([sal_capacity(x) for x in seg_x])

    fig, ax = plt.subplots(figsize=(11.0, 5.8), dpi=140)
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    ax.plot(xs, ys, linewidth=3.8, color=(0.76, 0.54, 0.54, 0.55))
    ax.plot(seg_x, seg_y, linewidth=5.0, color=(0.67, 0.10, 0.10, 0.95))

    ax.axvline(77, linewidth=3.2, color=(0, 0, 0, 0.22))

    ax.set_xlim(0, 77)
    ax.set_ylim(0, 100)

    ax.set_xticks(list(range(0, 80, 5)))
    ax.set_xlabel("Age", fontsize=10, color=(0, 0, 0, 0.68))

    ax.set_yticks([20, 55, 85])
    ax.set_yticklabels(["Frail", "Functional", "Fit"], fontsize=10, color=(0, 0, 0, 0.68))

    ax.grid(False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color((0, 0, 0, 0.30))
    ax.spines["bottom"].set_color((0, 0, 0, 0.30))
    ax.tick_params(axis="x", colors=(0, 0, 0, 0.55), labelsize=8, length=0)
    ax.tick_params(axis="y", colors=(0, 0, 0, 0.55), labelsize=8, length=0)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig, clear_figure=True)
    st.markdown("</div>", unsafe_allow_html=True)

with colR:
    st.markdown(
        f"""
<div class="card">
  <div class="hdr"><div class="ico">📋</div><h3 style="margin:0;">Diagnosis</h3></div>
  <div class="small" style="margin-top:8px; font-size:18px; opacity:0.9;">{diag_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="card">
  <div class="hdr"><div class="ico">℞</div><h3 style="margin:0;">Prescription</h3></div>
  <div class="small" style="margin-top:8px; font-size:18px; opacity:0.9;">{rx_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Check Engine + Fit Zone (Fit Zone text removed per your request)
    st.markdown(
        f"""
<div class="card">
  <div class="kpi-row">
    <div>{engine_svg(engine_color)}</div>
    <div>
      <p class="kpi-title">Check Engine</p>
      <div class="small" style="font-size:18px; font-weight:800; color:{engine_color};">
        {engine_name}
      </div>
      <div class="kpi-sub">Yellow at 30–45; red from 45 onward</div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-row">
    <div style="width:44px;height:44px;border-radius:999px;background:{zone_color};opacity:0.92;"></div>
    <div>
      <div class="kpi-sub">Zone score: <b>{zone_score:.1f}</b></div>
      <div class="kpi-sub">Yellow at 20–30; red from 30 onward</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
