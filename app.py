import math
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="Life Reclamation Dashboard", page_icon="🧭", layout="wide")

# -------------------------------------------------
# Parchment + faint mountains background
# -------------------------------------------------
MOUNTAIN_SVG = """
<svg viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <!-- very faint back range -->
  <path d="M0,210
           C120,170 210,185 330,150
           C430,120 520,155 620,130
           C720,105 820,150 920,125
           C1020,100 1100,145 1200,120
           L1200,260 L0,260 Z"
        fill="rgba(0,0,0,0.05)"/>
  <!-- slightly darker front range -->
  <path d="M0,235
           C140,205 260,230 360,195
           C470,160 560,215 680,175
           C790,140 900,220 1030,165
           C1110,130 1165,175 1200,155
           L1200,260 L0,260 Z"
        fill="rgba(0,0,0,0.07)"/>
</svg>
"""

CHECK_ENGINE_BADGE = """
<svg width="92" height="92" viewBox="0 0 96 96" xmlns="http://www.w3.org/2000/svg">
  <rect x="6" y="6" width="84" height="84" rx="16" fill="white" stroke="rgba(195, 56, 56, 0.55)" stroke-width="3"/>
  <text x="48" y="42" text-anchor="middle" font-size="14" font-family="Arial" fill="rgb(163, 34, 34)" font-weight="700">CHECK</text>
  <text x="48" y="62" text-anchor="middle" font-size="14" font-family="Arial" fill="rgb(163, 34, 34)" font-weight="700">ENGINE</text>
</svg>
"""

st.markdown(
    f"""
<style>
/* Parchment background */
.stApp {{
  background:
    radial-gradient(900px 500px at 15% 0%, rgba(0,0,0,0.04), rgba(0,0,0,0.00) 60%),
    linear-gradient(180deg, #fbf7ef 0%, #f7f1e6 100%);
  color: #1f1f1f;
}}

/* fixed faint mountains */
.lrp-mountains {{
  position: fixed;
  left: 0; right: 0; bottom: 0;
  height: 220px;
  pointer-events: none;
  opacity: 0.28;           /* faint */
  z-index: 0;
}}
.block-container {{
  position: relative;
  z-index: 1;
  padding-bottom: 170px;
  max-width: 1400px;
}}

/* Typography */
.h1 {{
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -0.02em;
  text-align: center;
  margin-top: 10px;
  margin-bottom: 0px;
}}
.sub {{
  text-align: center;
  font-size: 18px;
  opacity: 0.72;
  margin-top: 4px;
  margin-bottom: 14px;
}}

/* Cards */
.card {{
  border-radius: 18px;
  background: rgba(255,255,255,0.92);
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
  opacity: 0.8;
}}
.hr {{
  height: 1px;
  background: rgba(0,0,0,0.08);
  margin: 12px 0;
}}

/* Two-column bullets */
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

/* Centered band nav */
.bandbar {{
  display:flex;
  justify-content:center;
  align-items:center;
  gap: 14px;
  margin: 10px 0 14px 0;
}}
.bandpill {{
  font-size: 22px;
  font-weight: 800;
}}
.navbtn button {{
  border-radius: 14px !important;
  padding: 6px 14px !important;
}}

/* Right column icon headers */
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

/* Check engine row */
.engine-row {{
  display:flex;
  align-items:center;
  gap: 16px;
}}
.engine-status {{
  font-size: 22px;
  font-weight: 800;
}}
.engine-sub {{
  font-size: 14px;
  opacity: 0.75;
}}

/* Streamlit widgets: make them blend with parchment */
[data-baseweb="select"] > div {{
  border-radius: 14px !important;
}}
.stSlider > div {{
  padding-top: 6px;
}}
</style>

<div class="lrp-mountains">{MOUNTAIN_SVG}</div>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def label_zone(score: float):
    if score >= 70:
        return "Fit", "🟢"
    if score >= 40:
        return "Functional", "🟡"
    return "Frail", "🔴"

def label_engine(score: float):
    if score >= 70:
        return "Green", "🟢"
    if score >= 45:
        return "Yellow", "🟡"
    return "Red", "🔴"

# -------------------------------------------------
# Curves (keep your separation idea)
# -------------------------------------------------
def capacity_curve(age: float) -> float:
    """
    Standard American drift baseline for the parchment timeline.
    0–100 capacity.
    """
    age = float(age)
    s = 86 - 0.23 * max(age - 20, 0)
    s -= 0.42 * max(age - 65, 0)
    s -= 0.70 * max(age - 75, 0)
    return clamp(s, 0, 100)

def check_engine_score(age: float, risk: float, years_consistent: float) -> float:
    age = float(age)
    age_penalty = 0.30 * max(age - 25, 0) + 0.55 * max(age - 60, 0)
    risk_penalty = 0.45 * risk
    consistency_boost = 2.0 * clamp(years_consistent, 0, 12)
    return clamp(88 - age_penalty - risk_penalty + consistency_boost, 0, 100)

def band_label_for_age(age: int) -> str:
    a0 = (age // 5) * 5
    a1 = a0 + 5
    a0 = max(0, a0)
    a1 = min(95, a1)
    return f"{a0}-{a1}"

# -------------------------------------------------
# Stage content (placeholder but real text)
# Replace these later with your exact deck copy.
# -------------------------------------------------
LEFT_STAGE = {
    "0-5": ("Standard Living", [
        "Movement is effortless; play builds coordination",
        "Sleep and nutrition patterns form quietly",
        "Environment sets defaults (food, screens, stress)",
        "Parents choose the runway—kids take off",
    ]),
    "50-55": ("Medicalized Living", [
        "Weight drift becomes “normal”",
        "Strength and mobility quietly fade",
        "Markers rise: BP, A1c, lipids",
        "Energy becomes more limited",
    ]),
    "55-60": ("Medicalized Living", [
        "Multiple medications begin; side effects stack quietly",
        "Sleep fragments; fatigue becomes baseline",
        "Movement becomes cautious; joints “protected”",
        "Pain management replaces performance",
    ]),
    "60-65": ("Medicalized Living", [
        "More appointments; more complexity",
        "Recovery slows; minor issues linger",
        "Balance and strength decline if untrained",
        "Social life narrows with energy",
    ]),
}

RIGHT_STAGE = {
    "55-60": ("Managing conditions", "Adjust meds; reduce risk"),
    "50-55": ("Risk rising", "Intervene: strength, Zone 2, nutrition"),
    "60-65": ("Prevent compounding", "Simplify meds; train balance; protect sleep"),
}

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown('<div class="h1">A Standard American Life — Health Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">What happens if nothing intervenes</div>', unsafe_allow_html=True)

# -------------------------------------------------
# Controls: age band nav + sliders (minimal)
# -------------------------------------------------
if "age" not in st.session_state:
    st.session_state.age = 58

# centered bandbar
c_prev, c_mid, c_next = st.columns([1, 2, 1])
with c_prev:
    if st.button("←", key="prev_band"):
        st.session_state.age = max(5, st.session_state.age - 5)
with c_mid:
    band = band_label_for_age(st.session_state.age)
    st.markdown(f"<div class='bandbar'><div class='bandpill'>{band}</div></div>", unsafe_allow_html=True)
with c_next:
    if st.button("→", key="next_band"):
        st.session_state.age = min(92, st.session_state.age + 5)

# Keep the slider, but make it secondary
age = st.slider("Age", 5, 92, st.session_state.age, step=1)
st.session_state.age = age
band = band_label_for_age(age)

# Zone conditioning (fast) + Check engine risk (slow)
cc1, cc2, cc3 = st.columns([1.2, 1.2, 1.2])
with cc1:
    conditioning = st.slider("Current Conditioning (fast)", -25, 25, 0)
with cc2:
    risk = st.slider("Biomarker Risk (slow)", 0, 100, 35)
with cc3:
    years_consistent = st.slider("Years Consistent (slow)", 0, 12, 3)

# Scores
base = capacity_curve(age)
zone_score = clamp(base + conditioning, 0, 100)
zone_name, zone_dot = label_zone(zone_score)

engine = check_engine_score(age, risk=risk, years_consistent=years_consistent)
engine_name, engine_dot = label_engine(engine)

# Stage content
left_title, left_bullets = LEFT_STAGE.get(
    band,
    ("Standard Living", [
        "Placeholder bullet 1",
        "Placeholder bullet 2",
        "Placeholder bullet 3",
        "Placeholder bullet 4",
    ])
)
diag_text, rx_text = RIGHT_STAGE.get(band, ("Managing conditions", "Adjust meds; reduce risk"))

# -------------------------------------------------
# Main 3-column layout (matches your parchment screenshot)
# -------------------------------------------------
colL, colC, colR = st.columns([1.05, 1.8, 1.05], gap="large")

# Left card: bullets in 2 columns
with colL:
    bullets_html = "".join([f"<div class='b'><div class='dot'></div><div>{t}</div></div>" for t in left_bullets])
    st.markdown(
        f"""
<div class="card">
  <h3>{left_title}</h3>
  <div class="bullets">
    {bullets_html}
  </div>
</div>
""",
        unsafe_allow_html=True
    )

# Center: chart card
with colC:
    ages = np.arange(0, 93, 1)
    cap = np.array([capacity_curve(a) for a in ages])

    fig = go.Figure()

    # main life curve
    fig.add_trace(go.Scatter(
        x=ages, y=cap,
        mode="lines",
        line=dict(width=5, color="rgba(194, 122, 122, 0.45)"),
        hoverinfo="skip"
    ))

    # highlight current band segment (red)
    a0 = (age // 5) * 5
    seg_x = np.arange(a0, min(a0 + 5, 92) + 1, 1)
    seg_y = np.array([capacity_curve(x) for x in seg_x])
    fig.add_trace(go.Scatter(
        x=seg_x, y=seg_y,
        mode="lines",
        line=dict(width=7, color="rgba(170, 30, 30, 0.95)"),
        hoverinfo="skip"
    ))

    # axes styling to match screenshot
    fig.update_layout(
        height=520,  # taller, with more bottom space feeling
        margin=dict(l=60, r=20, t=10, b=55),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Age",
            range=[0, 77],
            tickmode="array",
            tickvals=list(range(0, 80, 5)),
            showgrid=False,
            zeroline=False,
            linecolor="rgba(0,0,0,0.35)",
            mirror=False
        ),
        yaxis=dict(
            range=[0, 100],
            tickmode="array",
            tickvals=[20, 55, 85],
            ticktext=["Frail", "Functional", "Fit"],
            showgrid=False,
            zeroline=False,
            linecolor="rgba(0,0,0,0.35)"
        ),
        showlegend=False
    )

    # right boundary line (like “77” end marker)
    fig.add_shape(
        type="line",
        x0=77, x1=77, y0=0, y1=100,
        line=dict(color="rgba(0,0,0,0.25)", width=5)
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Right column: Diagnosis, Prescription, Check Engine
with colR:
    st.markdown(
        f"""
<div class="card">
  <div class="hdr"><div class="ico">📋</div><h3 style="margin:0;">Diagnosis</h3></div>
  <div class="small" style="margin-top:8px; font-size:18px; opacity:0.9;">{diag_text}</div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="card">
  <div class="hdr"><div class="ico">℞</div><h3 style="margin:0;">Prescription</h3></div>
  <div class="small" style="margin-top:8px; font-size:18px; opacity:0.9;">{rx_text}</div>
</div>
""",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Check Engine + Zone (you liked the Zone status)
    st.markdown(
        f"""
<div class="card">
  <h3 style="text-align:center; margin-bottom:10px;">Check Engine</h3>
  <div class="engine-row">
    <div>{CHECK_ENGINE_BADGE}</div>
    <div>
      <div class="engine-status">{engine_dot} {engine_name}</div>
      <div class="engine-sub">Engine score: <b>{engine:.1f}</b></div>
      <div class="engine-sub">Zone now: <b>{zone_dot} {zone_name}</b> ({zone_score:.1f})</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True
    )
