import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="LRP — Health", layout="wide")

# =============================
# GLOBAL UI SCALE (key change)
# =============================
UI_SCALE = 0.90  # tuned to fit 100% zoom on laptop

def rem(x):  # helper
    return f"{x * UI_SCALE}rem"

# -----------------------------
# Mountains (soft + atmospheric)
# -----------------------------
MOUNTAIN_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="400" viewBox="0 0 1400 400">
  <path d="M0,300 L180,210 L340,260 L520,190 L700,260 L900,180 L1080,240 L1260,200 L1400,220 L1400,400 L0,400 Z"
        fill="rgba(0,0,0,0.05)"/>
</svg>
"""

def svg_uri(svg):
    return "data:image/svg+xml," + svg.replace("\n", "").replace("#", "%23")

MTN_URI = svg_uri(MOUNTAIN_SVG)

ENGINE_SVG = """
<svg viewBox="0 0 64 64">
  <g fill="none" stroke="currentColor" stroke-width="4.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 22 h24 v20 H18 z"/>
    <path d="M24 22 v-6 h12 v6"/>
    <path d="M18 30 h-6 v8 h6"/>
    <path d="M42 30 h10 v8 H42"/>
    <path d="M22 42 h16"/>
  </g>
</svg>
"""

st.markdown(f"""
<style>
.block-container {{
  padding-top: {rem(0.8)};
  padding-bottom: {rem(1.0)};
}}

.lrp-bg {{
  position: fixed;
  bottom: -6vh;
  left: 0;
  right: 0;
  height: 38vh;
  background: url("{MTN_URI}") repeat-x;
  background-size: 80% auto;
  opacity: 0.65;
  z-index: 0;
}}

.lrp-card {{
  background: rgba(255,255,255,0.96);
  border-radius: 16px;
  padding: {rem(0.9)};
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}}

.lrp-title {{
  font-size: {rem(1.55)};
  font-weight: 900;
}}

.dict-head {{
  font-size: {rem(1.25)};
  font-weight: 900;
}}

.dict-meta {{
  font-size: {rem(0.85)};
  color: rgba(0,0,0,0.5);
}}

.dict-pron {{
  font-style: italic;
  color: rgba(0,0,0,0.6);
  margin-top: 2px;
}}

.dict-def {{
  display: grid;
  grid-template-columns: 22px 1fr;
  margin-top: 4px;
}}

.bullets-title {{
  font-weight: 900;
  font-size: {rem(1.0)};
  margin-bottom: 8px;
}}

.bullets {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 14px;
  font-size: {rem(0.95)};
}}

.label {{
  font-size: {rem(0.8)};
  text-transform: uppercase;
  color: rgba(0,0,0,0.55);
  margin-bottom: 4px;
}}

.engine {{
  width: {rem(3.4)};
  height: {rem(2.6)};
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  border: 1px solid rgba(0,0,0,0.15);
  color: rgba(0,150,80,0.95);
}}

.engine svg {{
  width: 92%;
  height: 92%;
}}
</style>

<div class="lrp-bg"></div>
""", unsafe_allow_html=True)

# -----------------------------
# DATA
# -----------------------------
BANDS = [
    (0, 5, "Health is assumed and unexamined."),
    (5, 10, "Activity is natural and effortless."),
]

if "idx" not in st.session_state:
    st.session_state.idx = 0

def health_value(age):
    if age <= 10:
        return 92
    if age <= 55:
        t = (age - 10) / 45
        return 92 - 57 * (t ** 1.35)
    if age <= 77:
        t = (age - 55) / 22
        return 35 - 20 * (t ** 1.2)
    return None

# -----------------------------
# NAV (Prev / Next)
# -----------------------------
nav1, nav2, nav3 = st.columns([1, 2, 1])

with nav1:
    if st.button("◀ Previous", disabled=st.session_state.idx == 0):
        st.session_state.idx -= 1

with nav3:
    if st.button("Next ▶", disabled=st.session_state.idx == len(BANDS) - 1):
        st.session_state.idx += 1

band = BANDS[st.session_state.idx]
a0, a1, band_title = band

# -----------------------------
# TOP ROW
# -----------------------------
c1, c2 = st.columns([1.4, 1.8], gap="large")

with c1:
    st.markdown(f"""
    <div class="lrp-card">
      <div class="lrp-title">HEALTH · SAL · Ages {a0}–{a1}</div>

      <div class="dict-head">health <span class="dict-meta">· noun</span></div>
      <div class="dict-pron">/helTH/</div>

      <div class="dict-def"><div>1)</div><div>the absence of disease or infirmity</div></div>
      <div class="dict-def"><div>2)</div><div>also: the capacity to live, move, and engage fully with life</div></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="lrp-card">
      <div class="bullets-title">{band_title}</div>
      <div class="bullets">
        <div>• Unstructured play, exploration, bonding</div>
        <div>• Sleep mostly protected</div>
        <div>• Daycare illness disrupts rhythm</div>
        <div>• Screens introduced occasionally</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# PLOT
# -----------------------------
ages = list(range(0, 78))
ys = [health_value(a) for a in ages]

seg_x = list(range(a0, a1 + 1))
seg_y = [health_value(a) for a in seg_x]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=ages, y=ys,
    line=dict(color="rgba(0,0,0,0.25)", width=2.5, shape="spline"),
    hoverinfo="skip"
))
fig.add_trace(go.Scatter(
    x=seg_x, y=seg_y,
    line=dict(color="red", width=7, shape="spline"),
    hoverinfo="skip"
))

fig.update_layout(
    height=int(520 * UI_SCALE),
    margin=dict(l=30, r=20, t=10, b=30),
    xaxis=dict(range=[0, 92], title="Age"),
    yaxis=dict(range=[0, 100],
               tickvals=[85, 55, 25],
               ticktext=["Fit", "Functional", "Frail"]),
    showlegend=False
)

# -----------------------------
# BOTTOM ROW
# -----------------------------
l, r = st.columns([1.1, 2.9], gap="large")

with l:
    st.markdown(f"""
    <div class="lrp-card">
      <div class="label">Diagnosis</div>
      Everything looks normal and on track for age.

      <div class="label" style="margin-top:10px;">Prescription</div>
      Stay on schedule with vaccinations. Use antibiotics when needed.

      <div class="label" style="margin-top:12px;">Check Engine</div>
      <div class="engine">{ENGINE_SVG}</div>
    </div>
    """, unsafe_allow_html=True)

with r:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
