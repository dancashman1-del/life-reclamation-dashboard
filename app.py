import math
import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Standard American Life — Health Timeline", page_icon="🧭", layout="wide")

# -----------------------------
# Background (parchment + faint mountains)
# -----------------------------
MOUNTAIN_SVG = """
<svg viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <path d="M0,210
           C120,170 210,185 330,150
           C430,120 520,155 620,130
           C720,105 820,150 920,125
           C1020,100 1100,145 1200,120
           L1200,260 L0,260 Z"
        fill="rgba(0,0,0,0.06)"/>
  <path d="M0,235
           C140,205 260,230 360,195
           C470,160 560,215 680,175
           C790,140 900,220 1030,165
           C1110,130 1165,175 1200,155
           L1200,260 L0,260 Z"
        fill="rgba(0,0,0,0.09)"/>
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
.stApp {{
  background:
    radial-gradient(900px 520px at 20% 0%, rgba(0,0,0,0.05), rgba(0,0,0,0.00) 60%),
    linear-gradient(180deg, #fbf7ef 0%, #f7f1e6 100%);
  color: #1f1f1f;
}}
/* mountains */
.lrp-mountains {{
  position: fixed;
  left: 0; right: 0; bottom: -10px;
  height: 240px;
  pointer-events: none;
  opacity: 0.40;     /* make them visible */
  z-index: 0;
}}
.block-container {{
  position: relative;
  z-index: 1;
  padding-bottom: 160px;
  max-width: 1600px; /* allow more width for chart */
}}
/* tighten Streamlit top padding */
.block-container {{
  padding-top: 1.5rem;
}}
/* Typography */
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
/* Cards */
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
/* Bullets */
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
/* Band nav row */
.bandrow {{
  display:flex;
  justify-content:center;
  align-items:center;
  gap: 16px;
  margin: 10px 0 14px 0;
}}
.bandpill {{
  font-size: 22px;
  font-weight: 800;
}}
/* Make the band buttons look like the slide */
div.stButton > button {{
  border-radius: 14px;
  padding: 6px 14px;
  border: 1px solid rgba(0,0,0,0.10);
  background: rgba(255,255,255,0.92);
}}
/* Right column header icons */
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
  font-weight: 850;
}}
.engine-sub {{
  font-size: 14px;
  opacity: 0.78;
}}
</style>

<div class="lrp-mountains">{MOUNTAIN_SVG}</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
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

def band_label_for_age(age: int) -> str:
    a0 = (age // 5) * 5
    a1 = a0 + 5
    a0 = max(0, a0)
    a1 = min(95, a1)
    return f"{a0}-{a1}"

# -----------------------------
# SAL capacity curve (more realistic: Fit → Functional → Frail)
# -----------------------------
def capacity_curve(age: float) -> float:
    """
    A more realistic Standard American Life curve:
    - strong early adulthood
    - gradual drift into Functional by ~50s/60s
    - sharp decline after ~70
    - hits Frail by late 70s
    """
    age = float(age)

    # Start near Fit, then slow drift
    s = 86 - 0.32 * max(age - 20, 0)          # gradual decline
    s -= 0.55 * max(age - 60, 0)              # steeper after 60
    s -= 1.10 * max(age - 70, 0)              # sharper after 70

    # Keep early life stable
    if age < 20:
        s = 82 + 0.15 * age                   # ~82 at 0, ~85 at 20

    return clamp(s, 0, 100)

# Check engine proxy (kept, but hidden unless Advanced opened)
def check_engine_score(age: float, risk: float, years_consistent: float) -> float:
    age = float(age)
    age_penalty = 0.30 * max(age - 25, 0) + 0.55 * max(age - 60, 0)
    risk_penalty = 0.45 * risk
    consistency_boost = 2.0 * clamp(years_consistent, 0, 12)
    return clamp(88 - age_penalty - risk_penalty + consistency_boost, 0, 100)

# -----------------------------
# Stage content (still placeholders—swap with your real deck copy later)
# -----------------------------
LEFT_STAGE = {
    "55-60": ("Medicalized Living", [
        "Multiple medications begin; side effects stack quietly",
        "Sleep fragments; fatigue becomes baseline",
        "Movement becomes cautious; joints “protected”",
        "Pain management replaces performance",
    ]),
    "50-55": ("Medicalized Living", [
        "Markers creep upward; warnings ignored",
        "Strength fades; stiffness becomes “normal”",
        "Sleep quality declines quietly",
        "Movement volume drops as life gets busy",
    ]),
    "60-65": ("Medicalized Living", [
        "More appointments; more complexity",
        "Recovery slows; minor issues linger",
        "Balance declines if untrained",
        "Social life narrows with energy",
    ]),
}
RIGHT_STAGE = {
    "55-60": ("Managing conditions", "Adjust meds; reduce risk"),
    "50-55": ("Managing drift", "Intervene: strength, Zone 2, nutrition"),
    "60-65": ("Prevent compounding", "Simplify meds; train balance; protect sleep"),
}

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="h1">A Standard American Life — Health Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">What happens if nothing intervenes</div>', unsafe_allow_html=True)

# -----------------------------
# Band navigation ONLY (remove the big sliders from the UI)
# -----------------------------
if "age" not in st.session_state:
    st.session_state.age = 55  # start around your example

# Centered nav row (← 50-55 →)
navL, navM, navR = st.columns([1, 2, 1])
with navL:
    if st.button("←", key="prev_band"):
        st.session_state.age = max(5, st.session_state.age - 5)
with navM:
    band = band_label_for_age(st.session_state.age)
    st.markdown(f"<div class='bandrow'><div class='bandpill'>{band}</div></div>", unsafe_allow_html=True)
with navR:
    if st.button("→", key="next_band"):
        st.session_state.age = min(92, st.session_state.age + 5)

age = st.session_state.age
band = band_label_for_age(age)

# Optional advanced controls (collapsed by default so you don’t see big bars)
with st.expander("Advanced (optional)", expanded=False):
    conditioning = st.slider("Current Conditioning (fast)", -25, 25, 0)
    risk = st.slider("Biomarker Risk (slow)", 0, 100, 35)
    years_consistent = st.slider("Years Consistent (slow)", 0, 12, 3)

# Defaults when Advanced closed
conditioning = locals().get("conditioning", 0)
risk = locals().get("risk", 35)
years_consistent = locals().get("years_consistent", 3)

# Scores
base = capacity_curve(age)
zone_score = clamp(base + conditioning, 0, 100)
zone_name, zone_dot = label_zone(zone_score)
engine = check_engine_score(age, risk=risk, years_consistent=years_consistent)
engine_name, engine_dot = label_engine(engine)

# Stage text
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

# -----------------------------
# Main 3-column layout: widen chart by tightening sides
# -----------------------------
colL, colC, colR = st.columns([1.0, 2.15, 1.0], gap="large")

with colL:
    bullets_html = "".join([f"<div class='b'><div class='dot'></div><div>{t}</div></div>" for t in left_bullets])
    st.markdown(
        f"""
<div class="card">
  <h3>{left_title}</h3>
  <div class="bullets">{bullets_html}</div>
</div>
""",
        unsafe_allow_html=True
    )

with colC:
    ages = np.arange(0, 93, 1)
    cap = np.array([capacity_curve(a) for a in ages])

    fig = go.Figure()

    # Life curve (pale pink)
    fig.add_trace(go.Scatter(
        x=ages, y=cap,
        mode="lines",
        line=dict(width=5, color="rgba(194, 122, 122, 0.42)"),
        hoverinfo="skip"
    ))

    # Highlight current band segment (red)
    a0 = (age // 5) * 5
    seg_x = np.arange(a0, min(a0 + 5, 92) + 1, 1)
    seg_y = np.array([capacity_curve(x) for x in seg_x])
    fig.add_trace(go.Scatter(
        x=seg_x, y=seg_y,
        mode="lines",
        line=dict(width=7, color="rgba(170, 30, 30, 0.95)"),
        hoverinfo="skip"
    ))

    # End marker at 77 (like your slide)
    fig.add_shape(type="line", x0=77, x1=77, y0=0, y1=100,
                  line=dict(color="rgba(0,0,0,0.28)", width=5))

    fig.update_layout(
        height=560,  # taller
        margin=dict(l=55, r=22, t=10, b=60),
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
        ),
        yaxis=dict(
            range=[0, 100],
            tickmode="array",
            tickvals=[20, 55, 85],
            ticktext=["Frail", "Functional", "Fit"],
            showgrid=False,
            zeroline=False,
            linecolor="rgba(0,0,0,0.35)",
        ),
        showlegend=False
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
