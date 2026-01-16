import math
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Life Reclamation Dashboard",
    page_icon="🧭",
    layout="wide"
)

# -------------------------------------------------
# Subtle double-mountain SVG background
# -------------------------------------------------
MOUNTAIN_SVG = """
<svg viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <defs>
    <linearGradient id="fog" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="rgba(255,255,255,0.00)"/>
      <stop offset="100%" stop-color="rgba(255,255,255,0.10)"/>
    </linearGradient>
  </defs>

  <!-- back range (very faint) -->
  <path d="M0,210
           C120,170 210,185 330,150
           C430,120 520,155 620,130
           C720,105 820,150 920,125
           C1020,100 1100,145 1200,120
           L1200,260 L0,260 Z"
        fill="rgba(255,255,255,0.05)"/>

  <!-- front range (slightly darker) -->
  <path d="M0,235
           C140,205 260,230 360,195
           C470,160 560,215 680,175
           C790,140 900,220 1030,165
           C1110,130 1165,175 1200,155
           L1200,260 L0,260 Z"
        fill="rgba(255,255,255,0.08)"/>

  <rect x="0" y="0" width="1200" height="260" fill="url(#fog)"/>
</svg>
"""

st.markdown(
    f"""
<style>
.stApp {{
  background:
    radial-gradient(1200px 600px at 15% 0%, rgba(255,255,255,0.08), rgba(255,255,255,0.00) 60%),
    linear-gradient(180deg, #0b1523 0%, #09101b 100%);
  color: rgba(255,255,255,0.88);
}}

.lrp-mountains {{
  position: fixed;
  left: 0; right: 0; bottom: 0;
  height: 220px;
  pointer-events: none;
}}

.card {{
  border-radius: 18px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  padding: 16px;
}}

.title {{
  font-size: 34px;
  font-weight: 800;
  margin-bottom: 4px;
}}

.subtitle {{
  font-size: 14px;
  opacity: 0.7;
  margin-bottom: 18px;
}}
</style>

<div class="lrp-mountains">{MOUNTAIN_SVG}</div>
""",
    unsafe_allow_html=True
)

# -------------------------------------------------
# Healthspan curve model
# -------------------------------------------------
def life_curve(age: float) -> float:
    """
    0–100 scale
    70–100 = Fit
    40–70  = Functional
    <40    = Frail
    """

    base = 92 - 0.28 * max(age - 20, 0)

    on = 1 / (1 + math.exp(-(age - 55) / 1.2))
    off = 1 / (1 + math.exp((age - 61) / 1.3))
    boost = 16 * on * off

    post60 = max(age - 60, 0)
    decline = 0.42 * post60
    decline += 0.65 * max(age - 75, 0)
    decline += 0.85 * max(age - 80, 0)

    score = base + boost - decline

    if age >= 85:
        t = min((age - 85) / 7, 1)
        score = (1 - t) * score + t * 40

    return max(0, min(100, score))


def zone(score):
    if score >= 70:
        return "🟢 Fit"
    if score >= 40:
        return "🟡 Functional"
    return "🔴 Frail"


# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("<div class='title'>Life Reclamation Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Pilot your healthspan with intention — not drift.</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Controls
# -------------------------------------------------
age = st.slider("Age", 5, 92, 58)

score = life_curve(age)

# -------------------------------------------------
# Layout
# -------------------------------------------------
left, right = st.columns([1, 2])

with left:
    st.markdown(
        f"""
<div class="card">
<b>Check Engine</b><br><br>
<b>Score:</b> {score:.1f}<br>
<b>Zone:</b> {zone(score)}
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    ages = np.arange(5, 93)
    scores = [life_curve(a) for a in ages]

    fig = go.Figure()

    fig.add_hrect(y0=0, y1=40, fillcolor="rgba(255,255,255,0.05)", line_width=0)
    fig.add_hrect(y0=40, y1=70, fillcolor="rgba(255,255,255,0.08)", line_width=0)
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,255,255,0.12)", line_width=0)

    fig.add_trace(
        go.Scatter(
            x=ages,
            y=scores,
            mode="lines",
            line=dict(width=4),
            name="Trajectory",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[age],
            y=[score],
            mode="markers",
            marker=dict(size=14),
            name="You are here",
        )
    )

    fig.update_layout(
        height=620,
        margin=dict(l=30, r=30, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Age",
        yaxis_title="Capacity",
        yaxis_range=[0, 100],
        font=dict(color="rgba(255,255,255,0.85)"),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)
