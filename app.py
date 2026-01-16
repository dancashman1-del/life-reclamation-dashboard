import math
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# Page
# ------------------------------------------------------------
st.set_page_config(page_title="Life Timeline", page_icon="🧭", layout="wide")

# ------------------------------------------------------------
# Bands
# ------------------------------------------------------------
SAL_BANDS = [
    (0, 5),
    (5, 10),
    (10, 15),
    (15, 20),
    (20, 25),
    (25, 30),
    (30, 35),
    (35, 40),
    (40, 45),
    (45, 50),
    (50, 55),
    (55, 60),
    (60, 65),
    (65, 70),
    (70, 75),
    (75, 77),
]

LRP_BANDS = [
    (55, 60),
    (60, 65),
    (65, 70),
    (70, 75),
    (75, 80),
    (80, 85),
    (85, 90),
    (90, 92),
]


def band_label(a, b):
    return f"{a}-{b}"


# ------------------------------------------------------------
# Background: parchment + darker rolling mountains (two layers, higher on right)
# ------------------------------------------------------------
MOUNTAINS = """
<svg viewBox="0 0 1200 280" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <!-- back (lighter) range -->
  <path d="M0,225
           C140,210 260,230 380,205
           C520,175 640,230 760,200
           C900,160 1020,235 1200,175
           L1200,280 L0,280 Z"
        fill="rgba(0,0,0,0.06)"/>

  <!-- front (darker) range - rises to the right -->
  <path d="M0,255
           C150,245 280,265 420,240
           C560,210 660,260 800,225
           C930,190 1030,250 1200,205
           L1200,280 L0,280 Z"
        fill="rgba(0,0,0,0.12)"/>
</svg>
"""

st.markdown(
    f"""
<style>
:root {{
  --paper: #fbf6ee;
  --paper2: #f6efe4;
  --ink: #1e1e1e;
  --muted: rgba(30,30,30,0.62);
  --card: rgba(255,255,255,0.88);
  --cardBorder: rgba(0,0,0,0.08);
  --shadow: 0 16px 40px rgba(0,0,0,0.10);
  --salLine: rgba(140, 60, 60, 0.28);
  --salLineStrong: rgba(150, 35, 35, 0.85);
  --lrpLine: rgba(25, 120, 70, 0.30);
  --lrpLineStrong: rgba(20, 120, 70, 0.80);
}}

.stApp {{
  background:
    radial-gradient(1000px 520px at 10% 0%, rgba(0,0,0,0.04), rgba(0,0,0,0) 60%),
    linear-gradient(180deg, var(--paper) 0%, var(--paper2) 100%);
  color: var(--ink);
}}

.mtn {{
  position: fixed;
  left: 0; right: 0; bottom: 0;
  height: 220px;
  pointer-events: none;
  opacity: 0.84; /* ~10% darker overall */
}}

.headerWrap {{
  text-align: center;
  margin-top: 10px;
  margin-bottom: 8px;
}}

.h1 {{
  font-size: 44px;
  font-weight: 900;
  letter-spacing: -0.02em;
  margin: 0;
}}

.h2 {{
  font-size: 16px;
  color: var(--muted);
  margin-top: 6px;
}}

.navRow {{
  display:flex;
  align-items:center;
  justify-content:center;
  gap: 14px;
  margin: 12px 0 6px 0;
}}

.pill {{
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255,255,255,0.65);
  border: 1px solid var(--cardBorder);
  font-weight: 700;
}}

.card {{
  background: var(--card);
  border: 1px solid var(--cardBorder);
  border-radius: 18px;
  box-shadow: var(--shadow);
  padding: 18px 18px;
}}

.cardTitle {{
  font-size: 22px;
  font-weight: 900;
  margin: 0 0 10px 0;
  line-height: 1.05;
}}

.bullets {{
  margin: 0;
  padding-left: 18px;
  color: rgba(30,30,30,0.88);
  font-size: 16px;
  line-height: 1.45;
}}

.smallIconBox {{
  width: 54px;
  height: 54px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  border: 2px solid rgba(0,0,0,0.10);
  background: rgba(255,255,255,0.60);
}}

.dot {{
  width: 54px;
  height: 54px;
  border-radius: 50%;
  border: 2px solid rgba(0,0,0,0.10);
}}

.gRow {{
  display:flex;
  align-items:center;
  gap: 14px;
  margin-top: 12px;
}}

.gLabel {{
  font-weight: 900;
  font-size: 16px;
  margin-bottom: 2px;
}}

.gHint {{
  color: var(--muted);
  font-size: 13px;
  line-height: 1.2;
}}

hr.sep {{
  border: none;
  height: 1px;
  background: rgba(0,0,0,0.08);
  margin: 14px 0;
}}
</style>

<div class="mtn">{MOUNTAINS}</div>
""",
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Curves (SAL + LRP)
# We model capacity on 0–100 where:
# 70+ = Fit, 40–70 = Functional, <40 = Frail
# ------------------------------------------------------------
def sal_capacity(age: float) -> float:
    """
    SAL curve: mostly Fit early, crosses into Functional around ~50,
    then compounds downward with steeper late-life decline, ending at 77.
    """
    # Base drift
    # Start near 82, slow drift to ~55 by ~50, then compounding.
    if age <= 18:
        y = 78 - 0.05 * age
    elif age <= 45:
        y = 77 - 0.42 * (age - 18)  # down into low 60s by mid-40s
    elif age <= 50:
        y = 65 - 1.8 * (age - 45)   # sharper drop into Functional by 50
    elif age <= 65:
        y = 56 - 1.25 * (age - 50)
    elif age <= 72:
        y = 37 - 2.3 * (age - 65)
    else:
        y = 21 - 3.2 * (age - 72)

    return float(max(6, min(90, y)))


def lrp_capacity(age: float) -> float:
    """
    LRP: intervention starts ~55, rapid gains by ~60, then slow decline,
    finishing at the bottom end of Functional at 92.
    """
    # Before 55, LRP is not shown (handled by plotting logic)
    # Segment: 55->60 improvement to peak
    if age <= 60:
        # start around 52 at 55, peak ~78 at 60
        t = (age - 55) / 5.0
        y = 52 + t * (78 - 52)
    else:
        # gradual decline to ~40 by 92
        t = (age - 60) / (92 - 60)
        y = 78 - t * (78 - 40)

    return float(max(10, min(92, y)))


# ------------------------------------------------------------
# Color logic for SAL/LRP "Check Engine" and "Fitness Zone"
# (No numbers shown—only icon color)
# ------------------------------------------------------------
def sal_fitness_zone_color(age: int) -> str:
    # Per your spec: Yellow at 20–25, Red from 30–35 onward
    if age < 20:
        return "#3db86a"  # green
    if age < 30:
        return "#d4a400"  # yellow/amber
    return "#b03030"      # red


def sal_check_engine_color(age: int) -> str:
    # Delayed vs zone: Yellow at 30–45, Red from 45–77
    if age < 30:
        return "#3db86a"
    if age < 45:
        return "#d4a400"
    return "#b03030"


def lrp_fitness_zone_color(age: int) -> str:
    # LRP generally green; allow slight amber late if you want later.
    if age < 85:
        return "#3db86a"
    return "#5aa86e"  # still green-ish


def lrp_check_engine_color(age: int) -> str:
    if age < 85:
        return "#3db86a"
    return "#5aa86e"


# ------------------------------------------------------------
# Copy: Left panel titles + bullets (SAL + LRP)
# (Bullets are single-column, one per line)
# ------------------------------------------------------------
SAL_LEFT = {
    "0-5":  ("Built to Move (natural training)", [
        "Movement is natural; play provides daily training",
        "Sleep is abundant; recovery feels effortless",
        "Food habits form early; sugar normalizes fast",
        "Screens begin to replace outdoor hours",
    ]),
    "5-10": ("Sitting Starts (activity narrows)", [
        "Recess still helps; sitting begins to dominate",
        "Sports become seasonal—not daily movement",
        "Ultra-processed snacks become routine",
        "Sleep starts slipping as schedules grow",
    ]),
    "10-15": ("Teen Drift (comfort wins)", [
        "Movement gets optional; screens become default",
        "Food becomes engineered—high reward, low satiety",
        "Stress rises; sleep gets irregular",
        "Purpose is thin; distraction fills the gap",
    ]),
    "15-20": ("Launch Years (habits lock in)", [
        "Late nights; sleep debt becomes normal",
        "Cheap calories beat real food",
        "Training stops; fitness becomes “for athletes”",
        "Money stress nudges comfort-eating + screens",
    ]),
    "20-25": ("Adulting Begins (quiet decline)", [
        "Energy drops; “no time” becomes the reason",
        "Stress climbs; sleep quality erodes",
        "Muscle loss starts; strength training is absent",
        "Budget habits + convenience steer food choices",
    ]),
    "25-30": ("Work Wins (health waits)", [
        "Fitness becomes occasional, not consistent",
        "Weight creeps; back/hip issues appear",
        "Fast food + alcohol normalize socially",
        "Purpose feels postponed; anxiety hums",
    ]),
    "30-35": ("Baseline Shifts (subtle warning)", [
        "Cardio capacity falls below daily needs",
        "More inflammation; recovery slows",
        "Doctor says: “Try to eat better.”",
        "Financial pressure keeps “healthy” expensive",
    ]),
    "35-40": ("Compounding (more sitting)", [
        "Metabolic health slips; fatigue becomes normal",
        "Strength fades if untrained",
        "Sleep degrades under stress",
        "Food environment wins by default",
    ]),
    "40-45": ("First Labels (borderline)", [
        "Labs drift; risk starts to show",
        "Pain management replaces performance",
        "Short-term relief beats long-term plan",
        "Stress + screens crowd out movement",
    ]),
    "45-50": ("Medicalized Living (conditions)", [
        "Multiple meds begin; side effects stack quietly",
        "Movement gets cautious; joints feel “protected”",
        "Sleep fragments; fatigue becomes baseline",
        "Money stress rises as health costs rise",
    ]),
    "50-55": ("Lower Ceiling (shrinking capacity)", [
        "Stairs feel harder; breath comes sooner",
        "Injuries linger; recovery slows",
        "Doctor says: “We’ll watch it.”",
        "Vacations become rest, not adventure",
    ]),
    "55-60": ("Maintenance Mode (manage)", [
        "More prescriptions; fewer capabilities",
        "Strength loss accelerates without training",
        "Social life becomes more sedentary",
        "Purpose narrows to obligations",
    ]),
    "60-65": ("Risk Stacks (quietly)", [
        "More diagnoses; more follow-ups",
        "Falls feel “possible” now",
        "Mobility shrinks; confidence shrinks",
        "You start avoiding what you used to do",
    ]),
    "65-70": ("Safety First (fragility)", [
        "Less spontaneity; more caution",
        "Muscle loss shows up everywhere",
        "Daily chores take more effort",
        "Medical visits become the rhythm",
    ]),
    "70-75": ("Frail Horizon (losses)", [
        "Independence wobbles",
        "Pain management becomes central",
        "Social circle shrinks; isolation rises",
        "The “default” feels inevitable",
    ]),
    "75-77": ("The Wall (too late)", [
        "A cascade event becomes likely",
        "Function drops fast once it drops",
        "Life gets smaller",
        "The cost—time, money, meaning—shows up",
    ]),
}

LRP_LEFT = {
    "55-60": ("Reclamation Begins (first 5 years)", [
        "Strength training becomes non-negotiable",
        "Zone 2 base rebuilt; hiking feels easier",
        "Sleep regularized; mornings feel powerful",
        "Real food replaces “dieting”",
    ]),
    "60-65": ("Momentum (vitality compounds)", [
        "Consistency becomes identity",
        "Bloodwork trends younger",
        "Mobility + balance become daily",
        "Purpose grows; stress falls",
    ]),
    "65-70": ("Outlier Status (function stays high)", [
        "Stairs, hills, travel feel normal again",
        "Strength protects joints + confidence",
        "Community + sport keep you moving",
        "Cancer/metabolic risk keeps dropping",
    ]),
    "70-75": ("Durability (independence protected)", [
        "Leg strength + balance prevent falls",
        "Recovery stays strong with sleep + protein",
        "Adventure remains on the calendar",
        "Your world stays big",
    ]),
    "75-80": ("High Function (small wins daily)", [
        "Training is simpler—but steady",
        "You walk farther than peers",
        "You choose effort on purpose",
        "The view is grander than the climb",
    ]),
    "80-85": ("Freedom (still capable)", [
        "You keep routines safe + consistent",
        "Strength preserves autonomy",
        "Connection reduces stress physiology",
        "You keep saying “yes” to life",
    ]),
    "85-90": ("Compressed Morbidity (still thriving)", [
        "You move daily—no heroics",
        "You protect sleep relentlessly",
        "You stay engaged with people + place",
        "Function stays in the game",
    ]),
    "90-92": ("Finishing Strong (essentials)", [
        "Movement, connection, sleep—core",
        "You keep it simple and safe",
        "Joy stays present",
        "You end functional—not fragile",
    ]),
}

SAL_RIGHT = {
    "0-5":  ("“Nothing to worry about.”", "“They’ll grow out of it.”"),
    "5-10": ("“Kids bounce back.”", "“Just keep them busy.”"),
    "10-15": ("“It’s a phase.”", "“Try to cut down on snacks.”"),
    "15-20": ("“Normal stress.”", "“Get more sleep if you can.”"),
    "20-25": ("“You’re fine.”", "“Carry on.”"),
    "25-30": ("“A little stress.”", "“Maybe walk more.”"),
    "30-35": ("“Borderline.”", "“Diet and exercise.”"),
    "35-40": ("“Common for your age.”", "“We’ll watch it.”"),
    "40-45": ("“Nothing urgent.”", "“Follow up next year.”"),
    "45-50": ("“Manage conditions.”", "“Start meds as needed.”"),
    "50-55": ("“It happens.”", "“Adjust meds; reduce risk.”"),
    "55-60": ("“Let’s manage this.”", "“Add meds; treat symptoms.”"),
    "60-65": ("“Stabilize.”", "“More meds, more monitoring.”"),
    "65-70": ("“Prevent falls.”", "“PT referral; reduce risk.”"),
    "70-75": ("“Keep you safe.”", "“Supportive care.”"),
    "75-77": ("“Comfort and safety.”", "“More meds; fewer risks.”"),
}

LRP_RIGHT = {
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

SAL_SUBHEAD = {
    "0-5":  "The default path — comfort first, movement fades quietly",
    "5-10": "The default path — more sitting, more snacks, less play",
    "10-15":"The default path — screens replace effort; purpose thins",
    "15-20":"The default path — stress rises; habits lock in",
    "20-25":"The default path — quiet drift begins",
    "25-30":"The default path — work wins; health waits",
    "30-35":"The default path — warning signs start; you adapt downward",
    "35-40":"The default path — compounding decline",
    "40-45":"The default path — first labels; no real plan",
    "45-50":"The default path — minimized early, medicated later",
    "50-55":"The default path — capacity shrinks; life gets smaller",
    "55-60":"The default path — manage conditions",
    "60-65":"The default path — risk stacks quietly",
    "65-70":"The default path — safety first",
    "70-75":"The default path — frailty approaches",
    "75-77":"The default path — the wall",
}

LRP_SUBHEAD = {
    "55-60":"The intervention path — first 5 years, massive reversal",
    "60-65":"The intervention path — consistency compounds",
    "65-70":"The intervention path — function stays high",
    "70-75":"The intervention path — durability protects independence",
    "75-80":"The intervention path — small daily wins",
    "80-85":"The intervention path — freedom through routine",
    "85-90":"The intervention path — compressed morbidity",
    "90-92":"The intervention path — finishing strong",
}


# ------------------------------------------------------------
# Session state (prevents “stuck band” issues)
# ------------------------------------------------------------
if "sal_idx" not in st.session_state:
    st.session_state.sal_idx = 0
if "lrp_idx" not in st.session_state:
    st.session_state.lrp_idx = 0
if "use_lrp" not in st.session_state:
    st.session_state.use_lrp = False


def clamp_indices():
    st.session_state.sal_idx = int(max(0, min(len(SAL_BANDS) - 1, st.session_state.sal_idx)))
    st.session_state.lrp_idx = int(max(0, min(len(LRP_BANDS) - 1, st.session_state.lrp_idx)))


# ------------------------------------------------------------
# Header + nav controls
# ------------------------------------------------------------
use_lrp = st.toggle("LRP", value=st.session_state.use_lrp, key="toggle_lrp")
st.session_state.use_lrp = use_lrp

sal_a, sal_b = SAL_BANDS[st.session_state.sal_idx]
sal_key = band_label(sal_a, sal_b)

if use_lrp:
    lrp_a, lrp_b = LRP_BANDS[st.session_state.lrp_idx]
    lrp_key = band_label(lrp_a, lrp_b)
else:
    lrp_key = None

title = "Life Reclamation Project — RAMP Protocol" if use_lrp else "A Standard American Life — Health Timeline"
subhead = (LRP_SUBHEAD.get(lrp_key) if use_lrp else SAL_SUBHEAD.get(sal_key)) or ""

st.markdown(
    f"""
<div class="headerWrap">
  <div class="h1">{title}</div>
  <div class="h2">{subhead}</div>
</div>
""",
    unsafe_allow_html=True
)

# Band nav row (SAL always; LRP appears as separate control when toggled)
nav_left, nav_mid, nav_right = st.columns([1, 3, 1])

with nav_mid:
    # Centered nav: SAL band
    c1, c2, c3, c4, c5 = st.columns([1, 1.2, 0.9, 1.2, 1])
    with c2:
        if st.button("←", key="sal_prev_btn"):
            st.session_state.sal_idx -= 1
            clamp_indices()
            st.rerun()
    with c3:
        st.markdown(f"<div class='pill'>{sal_key}</div>", unsafe_allow_html=True)
    with c4:
        if st.button("→", key="sal_next_btn"):
            st.session_state.sal_idx += 1
            clamp_indices()
            st.rerun()

with nav_right:
    if use_lrp:
        # LRP band controls on the right
        d1, d2, d3 = st.columns([1, 2, 1])
        with d1:
            if st.button("←", key="lrp_prev_btn"):
                st.session_state.lrp_idx -= 1
                clamp_indices()
                st.rerun()
        with d2:
            st.markdown(f"<div class='pill'>LRP {lrp_key}</div>", unsafe_allow_html=True)
        with d3:
            if st.button("→", key="lrp_next_btn"):
                st.session_state.lrp_idx += 1
                clamp_indices()
                st.rerun()


# ------------------------------------------------------------
# Layout: left bullets, center chart, right panels
# ------------------------------------------------------------
left, mid, right = st.columns([1.05, 2.2, 1.05], gap="large")

# Left: bullets
with left:
    if use_lrp and lrp_key in LRP_LEFT:
        left_title, bullets = LRP_LEFT[lrp_key]
    else:
        left_title, bullets = SAL_LEFT.get(sal_key, ("Standard Living", ["(copy coming soon)"]))

    st.markdown(
        "<div class='card'>"
        f"<div class='cardTitle'>{left_title}</div>"
        "<ul class='bullets'>"
        + "".join([f"<li>{b}</li>" for b in bullets])
        + "</ul></div>",
        unsafe_allow_html=True
    )

# Mid: Chart (matplotlib for precise “paper slide” look)
with mid:
    # X-range depends on LRP toggle
    x_max = 92 if use_lrp else 77

    xs = np.linspace(0, x_max, int((x_max - 0) * 4) + 1)

    # SAL plotted only to 77, even if x_max=92 (fade after death)
    xs_sal = xs[xs <= 77]
    ys_sal = np.array([sal_capacity(float(x)) for x in xs_sal])

    fig = plt.figure(figsize=(9.2, 5.4), dpi=140)
    ax = fig.add_subplot(111)

    # Background bands (Fit/Functional/Frail)
    ax.axhspan(70, 100, color=(0, 0, 0, 0.03), lw=0)
    ax.axhspan(40, 70,  color=(0, 0, 0, 0.05), lw=0)
    ax.axhspan(0,  40,  color=(0, 0, 0, 0.07), lw=0)

    # SAL line
    ax.plot(xs_sal, ys_sal, color="#b77a7a", lw=2.6, alpha=0.35)
    ax.plot(xs_sal, ys_sal, color="#a86666", lw=2.0, alpha=0.22)

    # Highlight current SAL band segment (red)
    hx = np.linspace(sal_a, sal_b, 30)
    hy = np.array([sal_capacity(float(x)) for x in hx])
    ax.plot(hx, hy, color="#b03030", lw=3.6, alpha=0.95)

    # Death marker at 77
    ax.axvline(77, color=(0, 0, 0, 0.18), lw=1.2)
    ax.text(77, -2.5, "77", ha="center", va="top", fontsize=10, color="#b03030", fontweight="bold")

    # LRP overlay
    if use_lrp:
        xs_lrp = xs[xs >= 55]
        ys_lrp = np.array([lrp_capacity(float(x)) for x in xs_lrp])

        # faint green line
        ax.plot(xs_lrp, ys_lrp, color="#1b7d4a", lw=2.3, alpha=0.30)

        # highlight current LRP band segment (darker green)
        hx2 = np.linspace(lrp_a, lrp_b, 30)
        hy2 = np.array([lrp_capacity(float(x)) for x in hx2])
        ax.plot(hx2, hy2, color="#167a47", lw=3.8, alpha=0.85)

        # keep SAL red highlight visible but slightly faded when LRP on
        ax.plot(hx, hy, color="#b03030", lw=3.2, alpha=0.55)

    # Axes styling
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, 100)

    ax.set_xlabel("Age", fontsize=11, color=(0, 0, 0, 0.65))
    ax.set_ylabel("", fontsize=10)

    # Fit/Functional/Frail labels
    ax.text(-2.5, 80, "Fit", ha="right", va="center", fontsize=10, color=(0, 0, 0, 0.55))
    ax.text(-2.5, 50, "Functional", ha="right", va="center", fontsize=10, color=(0, 0, 0, 0.55))
    ax.text(-2.5, 20, "Frail", ha="right", va="center", fontsize=10, color=(0, 0, 0, 0.55))

    ax.grid(False)
    for s in ax.spines.values():
        s.set_color((0, 0, 0, 0.18))
        s.set_linewidth(1.0)

    ax.tick_params(axis="both", labelsize=9, colors=(0, 0, 0, 0.55))

    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0.0))

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.pyplot(fig, clear_figure=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Right: Diagnosis / Prescription / Gauges
with right:
    if use_lrp:
        diag, rx = LRP_RIGHT.get(lrp_key, ("", ""))
        engine_color = lrp_check_engine_color(lrp_a)
        zone_color = lrp_fitness_zone_color(lrp_a)
    else:
        diag, rx = SAL_RIGHT.get(sal_key, ("", ""))
        engine_color = sal_check_engine_color(sal_a)
        zone_color = sal_fitness_zone_color(sal_a)

    # Diagnosis card
    st.markdown(
        "<div class='card'>"
        "<div class='gRow' style='margin-top:0;'>"
        "<div class='smallIconBox'>📋</div>"
        "<div><div class='gLabel'>Diagnosis</div></div>"
        "</div>"
        f"<div style='margin-top:10px; font-size:16px; color: rgba(30,30,30,0.86);'>{diag}</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Prescription card
    st.markdown(
        "<div class='card'>"
        "<div class='gRow' style='margin-top:0;'>"
        "<div class='smallIconBox'>℞</div>"
        "<div><div class='gLabel'>Prescription</div></div>"
        "</div>"
        f"<div style='margin-top:10px; font-size:16px; color: rgba(30,30,30,0.86);'>{rx}</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Gauges card (NO numbers; just icon + short hint)
    st.markdown(
        "<div class='card'>"
        "<div class='gLabel'>Check Engine Light</div>"
        "<div class='gRow'>"
        f"<div class='smallIconBox' style='border-color: rgba(0,0,0,0.10);'>"
        f"<svg width='36' height='36' viewBox='0 0 24 24' fill='{engine_color}' xmlns='http://www.w3.org/2000/svg'>"
        "<path d='M7 4h10l2 4h2v8h-2l-2 4H7l-2-4H3V8h2l2-4zm2.2 4.2-1-2h7.6l1 2H9.2z'/>"
        "</svg>"
        "</div>"
        "<div class='gHint'>Biomarkers drift quietly — until they don’t.</div>"
        "</div>"
        "<hr class='sep'/>"
        "<div class='gLabel'>Fitness Zone</div>"
        "<div class='gRow'>"
        f"<div class='dot' style='background:{zone_color};'></div>"
        "<div class='gHint'>Day-to-day capacity: stairs, energy, strength, breath.</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# Quick “guardrail”: if LRP is ON, ensure LRP index starts at 55–60
# ------------------------------------------------------------
if use_lrp and st.session_state.lrp_idx < 0:
    st.session_state.lrp_idx = 0
