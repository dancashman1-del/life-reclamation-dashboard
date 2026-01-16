import math
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Life Reclamation Dashboard", page_icon="🧭", layout="wide")

# -----------------------------
# Background: subtle double mountains
# -----------------------------
MOUNTAIN_SVG = """
<svg viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <defs>
    <linearGradient id="fog" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="rgba(255,255,255,0.00)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0.12)"/>
    </linearGradient>
  </defs>

  <!-- back range (very faint) -->
  <path d="M0,210
           C120,170 210,185 330,150
           C430,120 520,155 620,130
           C720,105 820,150 920,125
           C1020,100 1100,145 1200,120
           L1200,260 L0,260 Z"
        fill="rgba(255,255,255,0.045)"/>

  <!-- front range (slightly darker) -->
  <path d="M0,235
           C140,205 260,230 360,195
           C470,160 560,215 680,175
           C790,140 900,220 1030,165
           C1110,130 1165,175 1200,155
           L1200,260 L0,260 Z"
        fill="rgba(255,255,255,0.075)"/>

  <rect x="0" y="0" width="1200" height="260" fill="url(#fog)"/>
</svg>
"""

st.markdown(
    f"""
<style>
/* Base */
html, body, [class*="css"] {{
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
}}
.stApp {{
  background:
    radial-gradient(1200px 600px at 15% 0%, rgba(255,255,255,0.09), rgba(255,255,255,0.00) 60%),
    radial-gradient(1000px 520px at 85% 10%, rgba(255,255,255,0.06), rgba(255,255,255,0.00) 55%),
    linear-gradient(180deg, #0c1726 0%, #09101b 100%);
}}
.lrp-mountains {{
  position: fixed;
  left: 0; right: 0; bottom: 0;
  height: 220px;
  pointer-events: none;
  opacity: 0.95;
  z-index: 0;
}}
/* Make sure content stays above mountains */
.block-container {{
  position: relative;
  z-index: 1;
  padding-bottom: 190px; /* keeps footer art from overlapping content */
}}

.h1 {{
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: rgba(255,255,255,0.92);
  margin: 2px 0 4px 0;
}}
.sub {{
  font-size: 14px;
  color: rgba(255,255,255,0.68);
  margin: 0 0 14px 0;
}}

.card {{
  border-radius: 18px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  padding: 14px 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.20);
}}

.card h3 {{
  margin: 0 0 8px 0;
  font-size: 16px;
  color: rgba(255,255,255,0.85);
}}

.small {{
  color: rgba(255,255,255,0.68);
  font-size: 12px;
}}

hr {{
  border: none;
  border-top: 1px solid rgba(255,255,255,0.12);
  margin: 14px 0;
}}

.chips {{
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}}
.chip {{
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border-radius: 999px;
  padding: 10px 12px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  color: rgba(255,255,255,0.86);
  font-size: 13px;
}}
.chip .emoji {{
  font-size: 16px;
}}

.kpi {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}}
.kpi .box {{
  border-radius: 14px;
  padding: 12px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
}}
.kpi .label {{
  font-size: 12px;
  color: rgba(255,255,255,0.65);
}}
.kpi .value {{
  font-size: 20px;
  font-weight: 800;
  color: rgba(255,255,255,0.92);
  letter-spacing: -0.02em;
}}
.pill {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  padding: 8px 10px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  font-size: 13px;
  color: rgba(255,255,255,0.85);
}}
</style>

<div class="lrp-mountains">{MOUNTAIN_SVG}</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Scoring helpers
# -----------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def label_zone(score: float):
    # Zone is "responsive capacity" (can change quickly)
    if score >= 70:
        return "Fit", "🟢"
    if score >= 40:
        return "Functional", "🟡"
    return "Frail", "🔴"

def label_engine(score: float):
    # Check engine is "risk / biomarkers / longevity drift" (slower to change)
    if score >= 70:
        return "Green", "🟢"
    if score >= 45:
        return "Yellow", "🟡"
    return "Red", "🔴"

# -----------------------------
# Two separate models:
# 1) Capacity curve (healthspan/fitness trajectory)
# 2) Check engine (risk / biomarkers proxy)
# -----------------------------
def capacity_curve(age: float, path: str) -> float:
    """
    Returns a baseline capacity score (0-100) by age.
    'Standard Drift' should be NOT automatically Fit at 25.
    'LRP Engaged' includes the lift around 55->60.
    """
    age = float(age)

    if path == "Standard Drift":
        # A deliberately more pessimistic baseline so 20s can still be yellow if out of shape.
        # Starts around Functional, drifts down, sharper decline late-life.
        s = 68.0 - 0.22 * max(age - 20, 0)              # slow drift
        s -= 0.35 * max(age - 60, 0)                    # steeper after 60
        s -= 0.55 * max(age - 75, 0)                    # steeper after 75
        # gentle childhood/teen ramp
        if age < 20:
            s = 62 + 0.30 * age                         # ~62 at 0, ~68 at 20
        return clamp(s, 0, 100)

    # LRP Engaged: modest decline + intervention lift around 55, peak 60, then decline
    base = 82 - 0.20 * max(age - 25, 0)                 # healthier baseline
    on = 1 / (1 + math.exp(-(age - 55) / 1.2))
    off = 1 / (1 + math.exp((age - 61) / 1.3))
    boost = 15.0 * on * off                              # intervention peak ~60

    post60 = max(age - 60, 0)
    decline = 0.30 * post60                               # gradual
    decline += 0.55 * max(age - 75, 0)                    # faster by 75
    decline += 0.75 * max(age - 80, 0)                    # more by 80

    s = base + boost - decline

    # Finish bottom end of Functional at 92 (~40)
    if age >= 85:
        t = clamp((age - 85) / 7.0, 0, 1)
        s = (1 - t) * s + t * 40.0

    return clamp(s, 0, 100)

def check_engine_score(age: float, risk: float, years_consistent: float) -> float:
    """
    Proxy score (0-100) for longevity/biomarker risk.
    - 'risk' is a user-controlled factor: higher risk lowers score.
    - 'years_consistent' improves score slowly (longer-term habit effect).
    """
    age = float(age)
    # Age-based headwind
    age_penalty = 0.35 * max(age - 25, 0)               # slow drift
    age_penalty += 0.55 * max(age - 60, 0)              # steeper later

    # Risk factor: 0 (low) -> 100 (high), map to penalty
    risk_penalty = 0.45 * risk

    # Consistency effect (slow): 0..10+ years yields meaningful lift
    consistency_boost = 2.0 * clamp(years_consistent, 0, 12)

    score = 88 - age_penalty - risk_penalty + consistency_boost
    return clamp(score, 0, 100)

# -----------------------------
# Stage text (5-year bands)
# -----------------------------
def band_label_for_age(age: int) -> str:
    a0 = (age // 5) * 5
    a1 = a0 + 5
    if a0 < 0: a0 = 0
    if a1 > 95: a1 = 95
    return f"{a0}-{a1}"

STAGE_TEXT = {
    "0-5":   ("Foundation", "Attachment, sleep rhythms, movement play, food environment."),
    "5-10":  ("Play & Capacity", "Mobility, coordination, confidence, active play becomes identity."),
    "10-15": ("Systems Online", "Habits form fast; posture, sleep, and social context matter."),
    "15-20": ("Launchpad", "Strength, athleticism, recovery. Avoid the first big habit slide."),
    "20-25": ("Early Adulthood", "Build a base: strength + aerobic engine. Avoid “sedentary career drift.”"),
    "25-30": ("Compounding", "Small routines compound. Weight and markers respond quickly here."),
    "30-35": ("Busy Years", "Protect sleep, keep strength training non-negotiable."),
    "35-40": ("Durability", "Joint care, consistency, stress management; keep the engine tuned."),
    "40-45": ("Midlife Signals", "Don’t ignore drift. Track basics: BP, waist, lipids, A1c."),
    "45-50": ("Resilience", "Strength and Zone 2 are “insurance.” Prevent the slow slide."),
    "50-55": ("Decision Point", "Drift accelerates unless you intervene. Time for a deliberate plan."),
    "55-60": ("Intervention Window", "5-year push can change your decade. Peak capacity is reachable."),
    "60-65": ("Maintain Peak", "Sustain habits; protect recovery. Strength preserves independence."),
    "65-70": ("Freedom Years", "Train for travel and stairs. Keep biomarkers boring."),
    "70-75": ("Friction Adds Up", "Falls, recovery, and muscle loss become costly. Train smart."),
    "75-80": ("Steeper Slope", "Intensity becomes precision. Keep legs strong; protect balance."),
    "80-85": ("Simplify & Win", "Short, frequent sessions. Sleep and protein are huge."),
    "85-90": ("Functional Focus", "Independence is the goal. Prevent frailty with consistency."),
    "90-95": ("Finish Strong", "Bottom of Functional is still a win: mobility, clarity, dignity."),
}

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="h1">Life Reclamation Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Pilot your healthspan with intention — not drift.</div>', unsafe_allow_html=True)

# -----------------------------
# Controls: Age + scenario + sliders
# -----------------------------
c1, c2, c3, c4 = st.columns([2.3, 1.4, 1.6, 1.7], gap="large")

with c1:
    age = st.slider("Age", min_value=5, max_value=92, value=58, step=1)
with c2:
    path = st.selectbox("Trajectory", ["LRP Engaged", "Standard Drift"])
with c3:
    conditioning = st.slider("Current Conditioning (fast)", -25, 25, 0,
                             help="Short-term fitness lever: how you feel / perform right now. Can change in weeks.")
with c4:
    risk = st.slider("Biomarker Risk (slow)", 0, 100, 35,
                     help="Longer-term risk lever: weight/metabolic health, BP, lipids, inflammation, smoking, etc.")

years_consistent = st.slider("Years Consistent (slow)", 0, 12, 3,
                             help="How long you've been consistently doing the basics. Changes the Check Engine slowly.")

# Stage band navigation (prev/next 5-year band)
band = band_label_for_age(age)
prev_col, band_col, next_col = st.columns([1, 2, 1])
with prev_col:
    if st.button("⬅ Prev band"):
        age = max(5, age - 5)
with band_col:
    st.markdown(f"<div class='pill'>Age band: <b>{band}</b></div>", unsafe_allow_html=True)
with next_col:
    if st.button("Next band ➡"):
        age = min(92, age + 5)

# Compute scores
base_capacity = capacity_curve(age, path)
zone_score = clamp(base_capacity + conditioning, 0, 100)
zone_name, zone_dot = label_zone(zone_score)

engine_score = check_engine_score(age, risk=risk, years_consistent=years_consistent)
engine_name, engine_dot = label_engine(engine_score)

stage_title, stage_desc = STAGE_TEXT.get(band, ("", ""))

# -----------------------------
# Chips under slider (2 + 2)
# -----------------------------
chip_left, chip_right = st.columns([1, 1], gap="large")
with chip_left:
    st.markdown(
        """
<div class="chips">
  <div class="chip"><span class="emoji">🧠</span><span>Diagnosis: know your baseline</span></div>
  <div class="chip"><span class="emoji">🛠️</span><span>Prescription: small levers → big compounding</span></div>
</div>
""",
        unsafe_allow_html=True,
    )
with chip_right:
    st.markdown(
        """
<div class="chips">
  <div class="chip"><span class="emoji">🔧</span><span>Check Engine: biomarkers & risk drift</span></div>
  <div class="chip"><span class="emoji">🏃</span><span>Zone: performance & capacity now</span></div>
</div>
""",
        unsafe_allow_html=True,
    )

# Add breathing room so chart sits lower (your request)
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# -----------------------------
# Main layout: Left cockpit cards + Right chart
# -----------------------------
left, right = st.columns([1.05, 1.75], gap="large")

with left:
    st.markdown(
        f"""
<div class="card">
  <h3>Check Engine</h3>
  <div class="small">Longer-term risk: biomarkers, disease odds, longevity drift.</div>
  <hr/>
  <div class="kpi">
    <div class="box">
      <div class="label">Engine Score</div>
      <div class="value">{engine_score:.1f}</div>
    </div>
    <div class="box">
      <div class="label">Status</div>
      <div class="value">{engine_dot} {engine_name}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="card">
  <h3>Zone</h3>
  <div class="small">Responsive capacity: stairs, hikes, strength, energy. Changes faster.</div>
  <hr/>
  <div class="kpi">
    <div class="box">
      <div class="label">Zone Score</div>
      <div class="value">{zone_score:.1f}</div>
    </div>
    <div class="box">
      <div class="label">Zone</div>
      <div class="value">{zone_dot} {zone_name}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Diagnosis / Prescription (now back)
    st.markdown('<div class="card"><h3>Diagnosis</h3>', unsafe_allow_html=True)
    st.markdown(f"<div class='small'><b>Age band:</b> {band} — <b>{stage_title}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small'>{stage_desc}</div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<div class='small'><b>What to watch:</b> sleep, waist, BP, A1c, strength, aerobic base.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>Prescription</h3>', unsafe_allow_html=True)
    st.markdown("<div class='small'><b>Minimum effective dose:</b> 2× strength + 2× Zone 2 weekly.</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'><b>Protect:</b> sleep, protein, mobility, consistency.</div>", unsafe_allow_html=True)
    st.markdown("<div class='small'><b>Upgrade:</b> add intensity carefully, keep joints happy.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    # Trajectory data
    ages = np.arange(5, 93, 1)
    cap = np.array([capacity_curve(float(a), path) for a in ages])
    zone_line = np.array([clamp(capacity_curve(float(a), path) + conditioning, 0, 100) for a in ages])

    fig = go.Figure()

    # Bands
    fig.add_hrect(y0=0, y1=40, fillcolor="rgba(255,255,255,0.05)", line_width=0)
    fig.add_hrect(y0=40, y1=70, fillcolor="rgba(255,255,255,0.08)", line_width=0)
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,255,255,0.11)", line_width=0)

    # Baseline capacity line
    fig.add_trace(go.Scatter(
        x=ages, y=cap, mode="lines",
        name="Capacity baseline",
        line=dict(width=4),
        opacity=0.85
    ))

    # Zone (responsive) line
    fig.add_trace(go.Scatter(
        x=ages, y=zone_line, mode="lines",
        name="Zone (with conditioning)",
        line=dict(width=3, dash="dot"),
        opacity=0.65
    ))

    # Current marker
    fig.add_trace(go.Scatter(
        x=[age], y=[zone_score],
        mode="markers",
        name="You are here",
        marker=dict(size=14)
    ))

    # Labels
    fig.add_annotation(x=8, y=85, text="FIT", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.70)"))
    fig.add_annotation(x=10, y=55, text="FUNCTIONAL", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.65)"))
    fig.add_annotation(x=8, y=20, text="FRAIL", showarrow=False, font=dict(size=12, color="rgba(255,255,255,0.60)"))

    fig.update_layout(
        height=720,  # Taller chart (your request)
        margin=dict(l=30, r=30, t=20, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Age",
            range=[5, 92],
            tickmode="array",
            tickvals=[5, 10, 20, 30, 40, 50, 55, 60, 70, 75, 80, 85, 92],
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
        ),
        yaxis=dict(
            title="Capacity (Fit → Frail)",
            range=[0, 100],
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.00,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.75)"),
        ),
        font=dict(color="rgba(255,255,255,0.82)"),
    )

    st.markdown(
        """
<div class="card">
  <h3>Healthspan Trajectory</h3>
  <div class="small">
    Solid line = baseline capacity (long arc). Dotted = Zone (fast changes). Marker = current.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)
