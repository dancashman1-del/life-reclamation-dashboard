import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="A Standard American Life — Health Timeline",
    page_icon="🧭",
    layout="wide",
)

# -----------------------------
# Background (parchment + 2-layer mountains, darker + rising right)
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
        fill="rgba(0,0,0,0.07)"/>
  <!-- front/darker range (rises to the right) -->
  <path d="M0,295
           C160,270 290,300 410,265
           C540,230 650,285 790,240
           C925,200 1000,275 1120,215
           C1170,185 1190,170 1200,150
           L1200,320 L0,320 Z"
        fill="rgba(0,0,0,0.14)"/>
</svg>
"""

def engine_svg(color_hex: str) -> str:
    return f"""
<svg width="46" height="46" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 18h18l4 6h6v8h-4l-2 6h-2v8H22v-6h-6v-8h4l2-6h2z"
        fill="{color_hex}" opacity="0.96"/>
  <path d="M24 28h16v16H24z" fill="white" opacity="0.22"/>
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
  height: 280px;
  pointer-events: none;
  opacity: 0.90;  /* darker overall */
  z-index: 0;
}}
.block-container {{
  position: relative;
  z-index: 1;
  padding-bottom: 180px;
  max-width: 1700px;
  padding-top: 1.0rem;
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
  gap: 10px 18px;
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

/* centered nav group */
.navbtn > div > button {{
  border-radius: 14px !important;
  padding: 6px 12px !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
  background: rgba(255,255,255,0.92) !important;
}}

.pill {{
  display:inline-block;
  font-size: 18px;
  font-weight: 850;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255,255,255,0.75);
  border: 1px solid rgba(0,0,0,0.08);
}}
.pill-dark {{
  background: rgba(0,0,0,0.04);
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

# -----------------------------
# SAL curve (tuned to your red sketch; ends ~12 at 77)
# -----------------------------
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
    return float(np.interp(age, pts[:, 0], pts[:, 1]))

# Optional LRP overlay curve (simple first pass; we can refine later)
def lrp_capacity(age: float) -> float:
    # Peaks at ~60, then slow decline; still functional at 92
    pts = np.array([
        [55, 55],
        [60, 78],
        [70, 74],
        [75, 70],
        [80, 62],
        [85, 58],
        [92, 55],
    ], dtype=float)
    return float(np.interp(age, pts[:, 0], pts[:, 1]))

# -----------------------------
# SAL check engine + zone color rules (your rules)
# Zone: yellow 20–25; red 30–35+; deeper red later
# Check engine: yellow 30–45; red 45–77
# -----------------------------
def sal_zone_color(age: float) -> str:
    if age < 20:
        return "#39b66a"
    if age < 30:
        return "#d6a400"
    if age < 50:
        return "#c63b3b"
    return "#9d1f1f"

def sal_engine_color(age: float) -> str:
    if age < 30:
        return "#39b66a"
    if age < 45:
        return "#d6a400"
    return "#c63b3b"

# Simple engine/zone scores (we can later tie to biomarker sliders)
def sal_engine_score(age: float) -> float:
    # stays “fine” early; then declines into midlife
    return clamp(94 - 0.35 * max(age - 30, 0), 40, 95)

def sal_zone_score(age: float) -> float:
    # mostly “feel-able” earlier; more responsive
    return clamp(sal_capacity(age), 0, 100)

# -----------------------------
# Copy: Left bullets for SAL (all bands)
# -----------------------------
SAL_LEFT_STAGE = {
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
        "Energy drops; “no time” becomes the reason",
        "Muscle loss starts; strength training is absent",
        "Stress climbs; sleep quality erodes",
        "Biomarkers start drifting—unnoticed",
    ]),
    "25-30": ("Standard Living", [
        "Weight gain begins quietly",
        "Fitness becomes optional; consistency fades",
        "Alcohol + late nights blunt recovery",
        "Sitting becomes the default posture",
    ]),
    "30-35": ("Standard Living", [
        "Metabolic health slips; inflammation rises",
        "Back/hip/shoulder issues become common",
        "Fat gain accelerates; muscle loss continues",
        "Cardio fitness falls below daily needs",
    ]),
    "35-40": ("Standard Living", [
        "Chronic aches become “normal” baseline",
        "Blood pressure/markers creep upward",
        "Recovery slows; setbacks linger",
        "Stress becomes constant background noise",
    ]),
    "40-45": ("Standard Living", [
        "First real warning signs appear on labs",
        "Sleep apnea risk rises; fatigue persists",
        "Movement becomes cautious; joints “protected”",
        "Motivation drops; habits calcify",
    ]),
    "45-50": ("Medicalized Living", [
        "Multiple medications begin; side effects stack quietly",
        "Sleep fragments; fatigue becomes baseline",
        "Pain management replaces performance",
        "Capacity drops; life becomes smaller",
    ]),
    "50-55": ("Medicalized Living", [
        "Conditions collect: metabolic, joints, mood, sleep",
        "Strength drops; fall risk starts rising",
        "More appointments; less capacity",
        "“Normal for your age” becomes the refrain",
    ]),
    "55-60": ("Medicalized Living", [
        "Polypharmacy becomes common; tradeoffs increase",
        "Balance declines if untrained",
        "Recovery slows; setbacks compound",
        "Independence starts to feel fragile",
    ]),
    "60-65": ("Medicalized Living", [
        "Hospital visits become more likely events",
        "Mobility shrinks; stairs become a barrier",
        "Sarcopenia accelerates without strength work",
        "Fear of injury limits activity further",
    ]),
    "65-70": ("Frail Transition", [
        "Falls become a turning-point risk",
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
        "High risk of hospitalization + cascade decline",
        "Assistive devices become common",
        "Loss of autonomy becomes real",
        "Caregiver dependence increases",
    ]),
}

# -----------------------------
# SAL Diagnosis + Prescription (the “downplaying / carry on” voice)
# -----------------------------
SAL_RIGHT_STAGE = {
    "0-5":  ("“Nothing to worry about.”", "“They’ll grow out of it.”"),
    "5-10": ("“Kids bounce back.”", "“Just keep them busy.”"),
    "10-15": ("“Normal teenager stuff.”", "“Try to sleep more.”"),
    "15-20": ("“It’s stress.”", "“Do your best.”"),
    "20-25": ("“You’re young. You’re fine.”", "“Maybe walk more.”"),
    "25-30": ("“A little burnout.”", "“Try to get more sleep.”"),
    "30-35": ("“Welcome to your 30s.”", "“Diet and exercise.” (no plan)"),
    "35-40": ("“Borderline, but not urgent.”", "“We’ll watch it.”"),
    "40-45": ("“Common these days.”", "“Let’s check again next year.”"),
    "45-50": ("“Nothing serious—yet.”", "“Start a med to be safe.”"),
    "50-55": ("“Manage your conditions.”", "“Add meds one by one.”"),
    "55-60": ("“This is typical for your age.”", "“Adjust meds; reduce risk.”"),
    "60-65": ("“Stability is the goal.”", "“Treat symptoms as they appear.”"),
    "65-70": ("“Focus on safety.”", "“PT when needed; prevent falls.”"),
    "70-75": ("“Keep you comfortable.”", "“More meds; support as needed.”"),
    "75-80": ("“Do what you can.”", "“Assistive devices; supportive care.”"),
}

# -----------------------------
# LRP bands (55–92 only)
# -----------------------------
LRP_BANDS = ["55-60", "60-65", "65-70", "70-75", "75-80", "80-85", "85-90", "90-92"]

LRP_LEFT_STAGE = {
    "55-60": ("Life Reclamation (LRP)", [
        "Strength training becomes non-negotiable",
        "Zone 2 base rebuilt; hiking feels easier",
        "Sleep regularized; mornings become powerful",
        "Real-food baseline replaces “dieting”",
    ]),
    "60-65": ("Life Reclamation (LRP)", [
        "Capacity stays high; resilience grows",
        "Balance + mobility become deliberate training",
        "Labs improve; inflammation falls",
        "Purpose expands: adventures, projects, people",
    ]),
    "65-70": ("Life Reclamation (LRP)", [
        "You become the outlier in your peer group",
        "Leg strength + gait protect independence",
        "HIIT is strategic, not punishing",
        "Consistency beats intensity—again and again",
    ]),
    "70-75": ("Life Reclamation (LRP)", [
        "Still hiking, still traveling, still strong",
        "Falls prevention is a top priority",
        "Community + purpose stay active",
        "Recovery rituals protect the engine",
    ]),
    "75-80": ("Life Reclamation (LRP)", [
        "Independence preserved; life stays big",
        "Daily movement becomes identity",
        "Strength stays in the program",
        "Healthspan is the mission",
    ]),
    "80-85": ("Life Reclamation (LRP)", [
        "Still capable; still engaged",
        "Simple routines, executed consistently",
        "Strength + gait + balance maintained",
        "Joy, connection, and meaning stay central",
    ]),
    "85-90": ("Life Reclamation (LRP)", [
        "Compressed morbidity becomes real",
        "Support is planned—not reactive",
        "Movement continues, safely",
        "Legacy and love rise in priority",
    ]),
    "90-92": ("Life Reclamation (LRP)", [
        "Finishing strong—functional and present",
        "Small daily wins keep the system stable",
        "Sleep and connection remain core",
        "The view is grander than the climb",
    ]),
}

LRP_RIGHT_STAGE = {
    "55-60": ("Doctor is stunned — keep doing whatever you're doing.",
              "Self-initiated strength + Zone 2 + HIIT; 95% real-food; protect sleep."),
    "60-65": ("Labs look younger than your age.",
              "Consistency: strength, Zone 2, mobility; prioritize recovery."),
    "65-70": ("You’re a rare outlier — function is high.",
              "Maintain legs + balance; keep hiking; keep protein high."),
    "70-75": ("Capacity stays strong — independence intact.",
              "Train legs, balance, grip; keep routines simple and regular."),
    "75-80": ("Exceptional autonomy preserved.",
              "Daily movement; fall prevention; keep social purpose."),
    "80-85": ("Still independent — still capable.",
              "Strength + gait + balance; simplify inputs; protect sleep."),
    "85-90": ("Compressed morbidity — still thriving.",
              "Keep it safe, consistent, and joyful; protect recovery."),
    "90-92": ("Finishing strong.",
              "Movement, connection, sleep — the essentials."),
}

# LRP zone/engine scores (first pass: better than SAL, responsive to “consistency” later)
def lrp_engine_score(band: str) -> float:
    idx = LRP_BANDS.index(band)
    # very high and stable
    return clamp(88 - idx * 2.0, 72, 92)

def lrp_zone_score(band: str) -> float:
    idx = LRP_BANDS.index(band)
    # stays functional-to-fit for longer
    return clamp(78 - idx * 1.8, 60, 85)

def lrp_engine_color(score: float) -> str:
    if score >= 82:
        return "#39b66a"
    if score >= 72:
        return "#d6a400"
    return "#c63b3b"

def lrp_zone_color(score: float) -> str:
    if score >= 72:
        return "#39b66a"
    if score >= 55:
        return "#d6a400"
    return "#c63b3b"


# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="h1">A Standard American Life — Health Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">The default path — minimized early, medicated later</div>', unsafe_allow_html=True)

# -----------------------------
# Session state
# -----------------------------
if "sal_age" not in st.session_state:
    st.session_state.sal_age = 22  # 20–25
if "lrp_on" not in st.session_state:
    st.session_state.lrp_on = False
if "lrp_idx" not in st.session_state:
    st.session_state.lrp_idx = 0  # 55–60

# -----------------------------
# NAV ROW: SAL controls centered; LRP controls on the right
# -----------------------------
# 7 columns: spacer | SAL prev | SAL band | SAL next | spacer | LRP toggle | LRP band controls
c1, c2, c3, c4, c5, c6, c7 = st.columns([2.0, 0.8, 1.4, 0.8, 1.2, 1.2, 2.6], vertical_alignment="center")

with c2:
    st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
    if st.button("←", key="sal_prev"):
        st.session_state.sal_age = max(0, st.session_state.sal_age - 5)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    sal_band = band_label_for_age(st.session_state.sal_age)
    st.markdown(f"<span class='pill'>{sal_band}</span>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
    if st.button("→", key="sal_next"):
        st.session_state.sal_age = min(92, st.session_state.sal_age + 5)
    st.markdown("</div>", unsafe_allow_html=True)

with c6:
    st.session_state.lrp_on = st.toggle("LRP", value=st.session_state.lrp_on)

with c7:
    if st.session_state.lrp_on:
        l1, l2, l3 = st.columns([0.9, 1.4, 0.9], vertical_alignment="center")
        with l1:
            st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
            if st.button("←", key="lrp_prev"):
                st.session_state.lrp_idx = max(0, st.session_state.lrp_idx - 1)
            st.markdown("</div>", unsafe_allow_html=True)
        with l2:
            st.markdown(f"<span class='pill pill-dark'>LRP {LRP_BANDS[st.session_state.lrp_idx]}</span>", unsafe_allow_html=True)
        with l3:
            st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
            if st.button("→", key="lrp_next"):
                st.session_state.lrp_idx = min(len(LRP_BANDS) - 1, st.session_state.lrp_idx + 1)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='small'>LRP band: 55–92</span>", unsafe_allow_html=True)

# -----------------------------
# Derived values
# -----------------------------
sal_age = st.session_state.sal_age
sal_band = band_label_for_age(sal_age)

sal_engine_col = sal_engine_color(sal_age)
sal_engine_sc = sal_engine_score(sal_age)
sal_zone_sc = sal_zone_score(sal_age)
sal_zone_col = sal_zone_color(sal_age)

# LRP values if enabled
lrp_band = LRP_BANDS[st.session_state.lrp_idx]
lrp_eng_sc = lrp_engine_score(lrp_band)
lrp_eng_col = lrp_engine_color(lrp_eng_sc)
lrp_zone_sc = lrp_zone_score(lrp_band)
lrp_zone_col = lrp_zone_color(lrp_zone_sc)

# Copy selection
# Left bullets: SAL always on left; if LRP enabled AND SAL is 55+ then show LRP bullets
if st.session_state.lrp_on and sal_age >= 55 and lrp_band in LRP_LEFT_STAGE:
    left_title, left_bullets = LRP_LEFT_STAGE[lrp_band]
else:
    left_title, left_bullets = SAL_LEFT_STAGE.get(
        sal_band,
        ("Standard Living", [
            "Health drifts quietly without a plan",
            "Strength fades if untrained",
            "Sleep degrades under stress",
            "Food environment wins by default",
        ])
    )

# Right diag/rx: if LRP enabled AND SAL is 55+ show LRP; else SAL downplaying
if st.session_state.lrp_on and sal_age >= 55 and lrp_band in LRP_RIGHT_STAGE:
    diag_text, rx_text = LRP_RIGHT_STAGE[lrp_band]
else:
    diag_text, rx_text = SAL_RIGHT_STAGE.get(sal_band, ("“You’re fine.”", "“Carry on.”"))

# KPI selection: show SAL always, but if LRP enabled AND SAL 55+ show both stacks (SAL vs LRP)
show_lrp_kpis = st.session_state.lrp_on and sal_age >= 55

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

    # Highlight SAL current 5-year segment
    a0 = (sal_age // 5) * 5
    seg_x = np.arange(a0, min(a0 + 5, 77) + 1, 1)
    seg_y = np.array([sal_capacity(x) for x in seg_x])

    fig, ax = plt.subplots(figsize=(11.2, 5.9), dpi=140)
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    # SAL main + highlight
    ax.plot(xs, ys, linewidth=3.8, color=(0.76, 0.54, 0.54, 0.55))
    ax.plot(seg_x, seg_y, linewidth=5.0, color=(0.67, 0.10, 0.10, 0.95))

    # Optional LRP overlay (starts at 55)
    if st.session_state.lrp_on:
        lxs = np.arange(55, 93, 1)
        lys = np.array([lrp_capacity(x) for x in lxs])
        ax.plot(lxs, lys, linewidth=3.4, color=(0.10, 0.45, 0.25, 0.55))

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
  <div class="small" style="margin-top:10px; font-size:18px; opacity:0.92;">{diag_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="card">
  <div class="hdr"><div class="ico">℞</div><h3 style="margin:0;">Prescription</h3></div>
  <div class="small" style="margin-top:10px; font-size:18px; opacity:0.92;">{rx_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # KPI card: SAL always; if LRP enabled and 55+ show LRP under it
    if show_lrp_kpis:
        kpi_html = f"""
<div class="card">
  <div class="kpi-title" style="margin-bottom:10px;">Standard American Life</div>

  <div class="kpi-row">
    <div>{engine_svg(sal_engine_col)}</div>
    <div>
      <div class="kpi-sub">Engine score: <b>{sal_engine_sc:.1f}</b></div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-row">
    <div style="width:44px;height:44px;border-radius:999px;background:{sal_zone_col};opacity:0.92;"></div>
    <div>
      <div class="kpi-sub">Score: <b>{sal_zone_sc:.1f}</b></div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-title" style="margin-bottom:10px;">Life Reclamation Project</div>

  <div class="kpi-row">
    <div>{engine_svg(lrp_eng_col)}</div>
    <div>
      <div class="kpi-sub">Engine score: <b>{lrp_eng_sc:.1f}</b></div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-row">
    <div style="width:44px;height:44px;border-radius:999px;background:{lrp_zone_col};opacity:0.92;"></div>
    <div>
      <div class="kpi-sub">Score: <b>{lrp_zone_sc:.1f}</b></div>
    </div>
  </div>
</div>
"""
    else:
        kpi_html = f"""
<div class="card">
  <div class="kpi-row">
    <div>{engine_svg(sal_engine_col)}</div>
    <div>
      <p class="kpi-title">Check Engine</p>
      <div class="kpi-sub">Engine score: <b>{sal_engine_sc:.1f}</b></div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-row">
    <div style="width:44px;height:44px;border-radius:999px;background:{sal_zone_col};opacity:0.92;"></div>
    <div>
      <div class="kpi-sub">Score: <b>{sal_zone_sc:.1f}</b></div>
    </div>
  </div>
</div>
"""
    st.markdown(kpi_html, unsafe_allow_html=True)
