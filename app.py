import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Life Timeline", page_icon="🧭", layout="wide")

# -----------------------------
# Background (parchment + 2-layer mountains; darker; rises to the right)
# -----------------------------
MOUNTAINS_SVG = """
<svg viewBox="0 0 1200 320" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <path d="M0,260
           C140,235 270,250 380,220
           C520,180 610,215 740,185
           C880,150 980,210 1090,165
           C1150,140 1185,130 1200,120
           L1200,320 L0,320 Z"
        fill="rgba(0,0,0,0.080)"/>
  <path d="M0,295
           C160,270 290,300 410,265
           C540,230 650,285 790,240
           C925,200 1000,275 1120,215
           C1170,185 1190,170 1200,150
           L1200,320 L0,320 Z"
        fill="rgba(0,0,0,0.165)"/>
</svg>
"""

def engine_svg(color_hex: str, size: int = 62) -> str:
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 18h18l4 6h6v8h-4l-2 6h-2v8H22v-6h-6v-8h4l2-6h2z"
        fill="{color_hex}" opacity="0.98"/>
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
  height: 290px;
  pointer-events: none;
  opacity: 0.93;
  z-index: 0;
}}
.block-container {{
  position: relative;
  z-index: 1;
  padding-bottom: 190px;
  max-width: 1700px;
  padding-top: 0.8rem;
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
  grid-template-columns: 1fr;   /* single column */
  gap: 10px;
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

.sep {{
  height:1px;
  background:rgba(0,0,0,0.08);
  margin: 14px 0;
}}

.kpi-title {{
  font-size: 16px;
  font-weight: 900;
  margin: 0 0 10px 0;
}}
.kpi-row {{
  display:flex;
  gap: 14px;
  align-items:center;
}}
.kpi-sub {{
  font-size: 13px;
  opacity: 0.72;
  margin-top: 4px;
}}
</style>

<div class="lrp-mountains">{MOUNTAINS_SVG}</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def band_label_for_age(age: int) -> str:
    a0 = (age // 5) * 5
    a1 = a0 + 5
    a0 = max(0, a0)
    a1 = min(95, a1)
    return f"{a0}-{a1}"

# -----------------------------
# SAL curve (ends ~12 at 77)
# -----------------------------
def sal_capacity(age: float) -> float:
    pts = np.array([
        [0,  88],
        [15, 86],
        [25, 80],
        [35, 73],
        [45, 66],
        [50, 55],
        [55, 48],
        [60, 42],
        [65, 36],
        [70, 26],
        [75, 16],
        [77, 12],
    ], dtype=float)
    return float(np.interp(age, pts[:, 0], pts[:, 1]))

# LRP curve (peaks near 60, stays functional at 92)
def lrp_capacity(age: float) -> float:
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
# SAL color rules (your rules)
# Zone: yellow 20–30; red 30+
# Engine: yellow 30–45; red 45–77
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

# LRP band controls
LRP_BANDS = ["55-60", "60-65", "65-70", "70-75", "75-80", "80-85", "85-90", "90-92"]

def band_start(b: str) -> int:
    return int(b.split("-")[0])

def band_end(b: str) -> int:
    return int(b.split("-")[1])

# LRP colors (display-only)
def lrp_engine_color_for_band(band: str) -> str:
    idx = LRP_BANDS.index(band)
    if idx <= 5:
        return "#39b66a"
    if idx == 6:
        return "#d6a400"
    return "#c63b3b"

def lrp_zone_color_for_band(band: str) -> str:
    idx = LRP_BANDS.index(band)
    if idx <= 5:
        return "#39b66a"
    if idx == 6:
        return "#d6a400"
    return "#c63b3b"

# -----------------------------
# Copy: SAL titles more descriptive (short, readable)
# -----------------------------
SAL_LEFT_STAGE = {
    "0-5":  ("Built to Move\n(natural training)", [
        "Movement is natural; play provides daily training",
        "Sleep is abundant; recovery is effortless",
        "Food habits form early; sugar normalizes fast",
        "Screens begin to replace outdoor hours",
    ]),
    "5-10": ("Sitting Starts\n(activity narrows)", [
        "Recess still helps; sitting begins to dominate",
        "Sports become seasonal—not daily movement",
        "Ultra-processed snacks become routine",
        "Sleep starts slipping as schedules grow",
    ]),
    "10-15": ("Teen Drift\n(mobility tightens)", [
        "Activity drops; posture and mobility tighten",
        "Social stress rises; comfort eating increases",
        "Strength work is rare; peak potential is missed",
        "Sleep becomes inconsistent; energy dips appear",
    ]),
    "15-20": ("Sedentary Default\n(screens win)", [
        "Sedentary time spikes; screens win the day",
        "Fast food + sugar drinks feel “normal”",
        "Injuries linger without strength foundations",
        "Sleep debt becomes lifestyle",
    ]),
    "20-25": ("Early Decline\n(quiet erosion)", [
        "Energy drops; “no time” becomes the reason",
        "Muscle loss starts; strength training is absent",
        "Stress climbs; sleep quality erodes",
        "Biomarkers start drifting—unnoticed",
    ]),
    "25-30": ("Weight Creep\n(consistency fades)", [
        "Weight gain begins quietly",
        "Fitness becomes optional; consistency fades",
        "Alcohol + late nights blunt recovery",
        "Sitting becomes the default posture",
    ]),
    "30-35": ("Metabolic Slide\n(inflammation rises)", [
        "Metabolic health slips; inflammation rises",
        "Back/hip/shoulder issues become common",
        "Fat gain accelerates; muscle loss continues",
        "Cardio fitness falls below daily needs",
    ]),
    "35-40": ("Chronic “Normal”\n(aches + fatigue)", [
        "Chronic aches become “normal” baseline",
        "Blood pressure/markers creep upward",
        "Recovery slows; setbacks linger",
        "Stress becomes constant background noise",
    ]),
    "40-45": ("Warning Signs\n(labs creep up)", [
        "First real warning signs appear on labs",
        "Sleep apnea risk rises; fatigue persists",
        "Movement becomes cautious; joints “protected”",
        "Motivation drops; habits calcify",
    ]),
    "45-50": ("Medicalized Living\n(meds begin)", [
        "Multiple medications begin; side effects stack quietly",
        "Sleep fragments; fatigue becomes baseline",
        "Pain management replaces performance",
        "Capacity drops; life becomes smaller",
    ]),
    "50-55": ("Conditions Collect\n(appointments rise)", [
        "Conditions collect: metabolic, joints, mood, sleep",
        "Strength drops; fall risk starts rising",
        "More appointments; less capacity",
        "“Normal for your age” becomes the refrain",
    ]),
    "55-60": ("Polypharmacy Risk\n(tradeoffs grow)", [
        "Polypharmacy becomes common; tradeoffs increase",
        "Balance declines if untrained",
        "Recovery slows; setbacks compound",
        "Independence starts to feel fragile",
    ]),
    "60-65": ("Mobility Shrinks\n(stairs become a barrier)", [
        "Hospital visits become more likely events",
        "Mobility shrinks; stairs become a barrier",
        "Sarcopenia accelerates without strength work",
        "Fear of injury limits activity further",
    ]),
    "65-70": ("Frail Transition\n(falls become pivotal)", [
        "Falls become a turning-point risk",
        "Frailty arrives sooner than expected",
        "Care needs increase; independence declines",
        "Life becomes smaller and more cautious",
    ]),
    "70-75": ("Frail\n(reserves are thin)", [
        "Capacity drops steeply; reserves are thin",
        "Chronic conditions drive daily decisions",
        "Simple tasks require planning and help",
        "More time managing health than living life",
    ]),
    "75-80": ("Frail\n(cascade decline risk)", [
        "High risk of hospitalization + cascade decline",
        "Assistive devices become common",
        "Loss of autonomy becomes real",
        "Caregiver dependence increases",
    ]),
}

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

# LRP: titles should NOT repeat the same header; make them band-specific and punchy
LRP_LEFT_STAGE = {
    "55-60": ("RAMP: Reversal Phase\n(rapid turnaround)", [
        "Strength training becomes non-negotiable",
        "Zone 2 base rebuilt; hiking feels easier",
        "Sleep regularized; mornings become powerful",
        "Risk downshifts: cancer, autoimmune, Alzheimer’s risk ↓ vs SAL",
    ]),
    "60-65": ("RAMP: Momentum\n(resilience compounds)", [
        "Capacity stays high; resilience grows",
        "Balance + mobility become deliberate training",
        "Labs improve; inflammation trends down",
        "Purpose expands: adventures, projects, people",
    ]),
    "65-70": ("RAMP: The Outlier\n(strong legs, strong life)", [
        "You become the outlier in your peer group",
        "Leg strength + gait protect independence",
        "HIIT is strategic, not punishing",
        "Consistency beats intensity—again and again",
    ]),
    "70-75": ("RAMP: High Function\n(independence intact)", [
        "Still hiking, still traveling, still strong",
        "Falls prevention is a top priority",
        "Community + purpose stay active",
        "Recovery rituals protect the engine",
    ]),
    "75-80": ("RAMP: Preserve Autonomy\n(life stays big)", [
        "Independence preserved; life stays big",
        "Daily movement becomes identity",
        "Strength stays in the program",
        "Healthspan is still the mission",
    ]),
    "80-85": ("RAMP: Simplify & Sustain\n(safe consistency)", [
        "Still capable; still engaged",
        "Simple routines, executed consistently",
        "Strength + gait + balance maintained",
        "Joy, connection, and meaning stay central",
    ]),
    "85-90": ("RAMP: Compressed Morbidity\n(planned support)", [
        "Compressed morbidity becomes real",
        "Support is planned—not reactive",
        "Movement continues, safely",
        "Legacy and love rise in priority",
    ]),
    "90-92": ("RAMP: Finish Strong\n(present + functional)", [
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

# -----------------------------
# Session state
# -----------------------------
if "sal_age" not in st.session_state:
    st.session_state.sal_age = 55
if "lrp_on" not in st.session_state:
    st.session_state.lrp_on = True
if "lrp_idx" not in st.session_state:
    st.session_state.lrp_idx = 0

# -----------------------------
# Header changes with LRP
# -----------------------------
sal_age = st.session_state.sal_age
sal_band = band_label_for_age(sal_age)

if st.session_state.lrp_on and sal_age >= 55:
    title = "Life Reclamation Project — RAMP Protocol"
    subtitle = "The intervention path — intentional living, compounding vitality"
else:
    title = "A Standard American Life — Health Timeline"
    subtitle = "The default path — minimized early, medicated later"

st.markdown(f'<div class="h1">{title}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub">{subtitle}</div>', unsafe_allow_html=True)

# -----------------------------
# Controls row
# -----------------------------
c1, c2, c3, c4, c5, c6, c7 = st.columns([2.0, 0.8, 1.4, 0.8, 1.2, 1.2, 2.6], vertical_alignment="center")

with c2:
    st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
    if st.button("←", key="sal_prev"):
        st.session_state.sal_age = max(0, st.session_state.sal_age - 5)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"<span class='pill'>{band_label_for_age(st.session_state.sal_age)}</span>", unsafe_allow_html=True)

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

# recompute after potential changes
sal_age = st.session_state.sal_age
sal_band = band_label_for_age(sal_age)
lrp_band = LRP_BANDS[st.session_state.lrp_idx]

# Copy selection
if st.session_state.lrp_on and sal_age >= 55 and lrp_band in LRP_LEFT_STAGE:
    left_title, left_bullets = LRP_LEFT_STAGE[lrp_band]
    diag_text, rx_text = LRP_RIGHT_STAGE[lrp_band]
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
    diag_text, rx_text = SAL_RIGHT_STAGE.get(sal_band, ("“You’re fine.”", "“Carry on.”"))

# -----------------------------
# KPI colors
# -----------------------------
sal_eng_col = sal_engine_color(sal_age)
sal_zone_col = sal_zone_color(sal_age)

lrp_eng_col = lrp_engine_color_for_band(lrp_band)
lrp_zone_col = lrp_zone_color_for_band(lrp_band)

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
    # X range changes in LRP mode (0–92) but chart pixel width stays same
    x_max = 92 if (st.session_state.lrp_on and sal_age >= 55) else 77

    # SAL curve
    xs_sal = np.arange(0, 78, 1)
    ys_sal = np.array([sal_capacity(x) for x in xs_sal])

    # Highlight segment: SAL only when NOT LRP
    a0 = (sal_age // 5) * 5
    seg_x = np.arange(a0, min(a0 + 5, 77) + 1, 1)
    seg_y = np.array([sal_capacity(x) for x in seg_x])

    fig, ax = plt.subplots(figsize=(11.2, 5.9), dpi=140)
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    ax.plot(xs_sal, ys_sal, linewidth=3.8, color=(0.76, 0.54, 0.54, 0.55))

    if not (st.session_state.lrp_on and sal_age >= 55):
        ax.plot(seg_x, seg_y, linewidth=5.0, color=(0.67, 0.10, 0.10, 0.95))

    if x_max == 92:
        ax.plot([77, 92], [12, 12], linewidth=3.2, color=(0.76, 0.54, 0.54, 0.18))

    # LRP progressive line
    if st.session_state.lrp_on and sal_age >= 55:
        cur_end = band_end(lrp_band)
        for b in LRP_BANDS:
            b0, b1 = band_start(b), band_end(b)
            if b1 <= cur_end:
                lxs = np.arange(b0, min(b1, cur_end) + 1, 1)
                lys = np.array([lrp_capacity(x) for x in lxs])
                is_active = (b == lrp_band)
                if is_active:
                    ax.plot(lxs, lys, linewidth=4.4, color=(0.10, 0.45, 0.25, 0.80))
                else:
                    ax.plot(lxs, lys, linewidth=3.4, color=(0.10, 0.45, 0.25, 0.35))

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, 100)

    xt = list(range(0, x_max + 1, 5))
    ax.set_xticks(xt)
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

    # KPI card: remove SAL gauges in LRP mode (your request)
    if st.session_state.lrp_on and sal_age >= 55:
        kpi_html = f"""
<div class="card">
  <div class="kpi-title">Check Engine Light</div>
  <div class="kpi-row">
    <div>{engine_svg(lrp_eng_col, size=66)}</div>
    <div>
      <div class="kpi-sub">Biomarkers stabilize through sustained intervention.</div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-title">Fitness Zone</div>
  <div class="kpi-row">
    <div style="width:66px;height:66px;border-radius:999px;background:{lrp_zone_col};opacity:0.92;"></div>
    <div>
      <div class="kpi-sub">Capacity stays higher — and recovers faster.</div>
    </div>
  </div>
</div>
"""
    else:
        kpi_html = f"""
<div class="card">
  <div class="kpi-title">Check Engine Light</div>
  <div class="kpi-row">
    <div>{engine_svg(sal_eng_col, size=66)}</div>
    <div>
      <div class="kpi-sub">Biomarkers drift quietly — until they don’t.</div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-title">Fitness Zone</div>
  <div class="kpi-row">
    <div style="width:66px;height:66px;border-radius:999px;background:{sal_zone_col};opacity:0.92;"></div>
    <div>
      <div class="kpi-sub">Day-to-day capacity: stairs, energy, strength, breath.</div>
    </div>
  </div>
</div>
"""
    st.markdown(kpi_html, unsafe_allow_html=True)
