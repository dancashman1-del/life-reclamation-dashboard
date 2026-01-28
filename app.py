import streamlit as st
import plotly.graph_objects as go
import textwrap

st.set_page_config(page_title="LRP — Health", layout="wide")

# =============================
# GLOBAL UI SCALE (fits 100% better)
# =============================
UI_SCALE = 0.86

def rem(x):
    return f"{x * UI_SCALE}rem"

def md(html: str):
    """Render HTML safely (prevents accidental code-block / raw HTML showing)."""
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)

# -----------------------------
# Soft background mountains (optional, subtle)
# -----------------------------
MOUNTAIN_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="420" viewBox="0 0 1400 420">
  <path d="M0,320 L180,230 L340,280 L520,205 L700,285 L900,190 L1080,255 L1260,215 L1400,240 L1400,420 L0,420 Z"
        fill="rgba(0,0,0,0.05)"/>
  <path d="M0,365 L210,260 L390,335 L610,245 L780,335 L980,240 L1160,305 L1400,265 L1400,420 L0,420 Z"
        fill="rgba(0,0,0,0.08)"/>
</svg>
"""

def svg_uri(svg):
    return "data:image/svg+xml," + svg.replace("\n", "").replace("#", "%23").replace("<", "%3C").replace(">", "%3E")

MTN_URI = svg_uri(MOUNTAIN_SVG)

ENGINE_SVG = """
<svg viewBox="0 0 64 64" aria-hidden="true">
  <g fill="none" stroke="currentColor" stroke-width="5.6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 22 h24 v20 H18 z"/>
    <path d="M24 22 v-6 h12 v6"/>
    <path d="M18 30 h-6 v8 h6"/>
    <path d="M42 30 h10 v8 H42"/>
    <path d="M22 42 h16"/>
  </g>
</svg>
"""

# NOTE: TOP SAFE AREA is the key fix here.
# Streamlit Cloud's top-right chrome can overlap. This padding prevents clipping.
md(f"""
<style>
/* Safe top gutter so nothing clips under Streamlit Cloud chrome */
.block-container {{
  padding-top: {rem(1.55)};
  padding-bottom: {rem(0.9)};
}}

.lrp-bg {{
  position: fixed;
  bottom: -10vh;
  left: 0;
  right: 0;
  height: 42vh;
  background: url("{MTN_URI}") repeat-x;
  background-size: 82% auto;
  opacity: 0.85;
  z-index: 0;
  pointer-events: none;
}}

.lrp-layer {{
  position: relative;
  z-index: 1;
}}

.lrp-card {{
  background: rgba(255,255,255,0.96);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  padding: {rem(0.85)};
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}}

.lrp-title {{
  font-size: {rem(1.48)};
  font-weight: 900;
  margin: 0 0 {rem(0.35)} 0;
}}

.dict-line {{
  display:flex;
  align-items:baseline;
  gap: 10px;
  margin-top: 2px;
}}
.dict-head {{
  font-size: {rem(1.18)};
  font-weight: 900;
}}
.dict-meta {{
  font-size: {rem(0.88)};
  color: rgba(0,0,0,0.50);
  font-weight: 650;
}}
.dict-pron {{
  font-style: italic;
  color: rgba(0,0,0,0.62);
  margin-top: 4px;
}}
.dict-def {{
  display: grid;
  grid-template-columns: 22px 1fr;
  column-gap: 10px;
  margin-top: 6px;
  font-size: {rem(0.98)};
  color: rgba(0,0,0,0.76);
}}
.dict-num {{
  color: rgba(0,0,0,0.48);
  font-weight: 800;
}}

.bullets-title {{
  font-weight: 900;
  font-size: {rem(1.02)};
  margin-bottom: {rem(0.55)};
}}
.bullets {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: {rem(0.35)} {rem(0.95)};
  font-size: {rem(0.94)};
  color: rgba(0,0,0,0.78);
  line-height: 1.35em;
}}

.label {{
  font-size: {rem(0.78)};
  text-transform: uppercase;
  color: rgba(0,0,0,0.55);
  letter-spacing: 0.4px;
  margin-bottom: {rem(0.35)};
}}

.body {{
  font-size: {rem(0.98)};
  color: rgba(0,0,0,0.78);
  line-height: 1.45em;
}}

.engine {{
  width: {rem(3.7)};
  height: {rem(2.9)};
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.14);
  background: rgba(0,0,0,0.02);
  color: rgba(0,150,80,0.95);
  padding: {rem(0.18)};
}}
.engine svg {{
  width: 98%;
  height: 98%;
}}

/* Make Streamlit buttons look more "slide-native" */
div.stButton > button {{
  border-radius: 12px;
  padding: 0.55rem 0.85rem;
  font-weight: 650;
}}
</style>

<div class="lrp-bg"></div>
<div class="lrp-layer">
""")

# -----------------------------
# DATA
# -----------------------------
BANDS = [
    (0, 5, "Health is assumed and unexamined."),
    (5, 10, "Activity is natural and effortless."),
]

if "idx" not in st.session_state:
    st.session_state.idx = 0

def health_value(age: float) -> float:
    # Keep your curve
    if age <= 10:
        return 92.0
    if age <= 55:
        t = (age - 10) / 45
        return 92.0 - 57.0 * (t ** 1.35)
    if age <= 77:
        t = (age - 55) / 22
        return 35.0 - 20.0 * (t ** 1.2)
    return None

a0, a1, band_title = BANDS[st.session_state.idx]

# -----------------------------
# TOP ROW: Title | Buttons | Bullets
# -----------------------------
col_title, col_nav, col_bul = st.columns([1.45, 0.75, 1.70], gap="large")

with col_title:
    md(f"""
<div class="lrp-card">
  <div class="lrp-title">HEALTH · SAL · Ages {a0}–{a1}</div>
  <div class="dict-line">
    <div class="dict-head">health</div>
    <div class="dict-meta">• noun</div>
  </div>
  <div class="dict-pron">/helTH/</div>
  <div class="dict-def"><div class="dict-num">1)</div><div>the absence of disease or infirmity</div></div>
  <div class="dict-def"><div class="dict-num">2)</div><div>also: the capacity to live, move, and engage fully with life</div></div>
</div>
""")

with col_nav:
    # Only the buttons (no track, no helper text)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("◀", disabled=(st.session_state.idx == 0), use_container_width=True):
            st.session_state.idx -= 1
            st.rerun()
    with b2:
        if st.button("▶", disabled=(st.session_state.idx == len(BANDS) - 1), use_container_width=True):
            st.session_state.idx += 1
            st.rerun()

    # Small label so user knows where they are (optional but helpful)
    st.caption(f"Ages {a0}–{a1}")

with col_bul:
    md(f"""
<div class="lrp-card">
  <div class="bullets-title">{band_title}</div>
  <div class="bullets">
    <div>• Unstructured play, exploration, bonding</div>
    <div>• Sleep mostly protected</div>
    <div>• Daycare illness disrupts rhythm</div>
    <div>• Screens introduced occasionally</div>
  </div>
</div>
""")

st.write("")

# -----------------------------
# PLOT
# -----------------------------
ages_context = list(range(0, 78))
y_context = [health_value(a) for a in ages_context]

seg_x = list(range(a0, a1 + 1))
seg_y = [health_value(a) for a in seg_x]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=ages_context, y=y_context,
    mode="lines",
    line=dict(color="rgba(0,0,0,0.25)", width=2.6, shape="spline"),
    hoverinfo="skip"
))
fig.add_trace(go.Scatter(
    x=seg_x, y=seg_y,
    mode="lines",
    line=dict(color="red", width=7.5, shape="spline"),
    hoverinfo="skip"
))

tickvals = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,77,80,85,90,92]
ticktext = [f"<b>{v}</b>" if v in (77, 92) else str(v) for v in tickvals]

fig.update_layout(
    height=int(500 * UI_SCALE),
    margin=dict(l=30, r=20, t=8, b=30),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
        range=[0, 92],
        title="Age",
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        gridcolor="rgba(0,0,0,0.06)",
        zeroline=False,
    ),
    yaxis=dict(
        range=[0, 100],
        tickvals=[85, 55, 25],
        ticktext=["Fit", "Functional", "Frail"],
        gridcolor="rgba(0,0,0,0.06)",
        zeroline=False,
    ),
    showlegend=False
)

# -----------------------------
# BOTTOM ROW
# -----------------------------
l, r = st.columns([1.10, 2.90], gap="large")

with l:
    md(f"""
<div class="lrp-card">
  <div class="label">Diagnosis</div>
  <div class="body">Everything looks normal and on track for age.</div>

  <div class="label" style="margin-top:{rem(0.75)};">Prescription</div>
  <div class="body">
    Stay on schedule with vaccinations. Use antibiotics and fever reducers when needed.
    Kids are resilient — there’s nothing to worry about.
  </div>

  <div class="label" style="margin-top:{rem(0.85)};">Check Engine</div>
  <div class="engine" title="Engine status (green)">{ENGINE_SVG}</div>
</div>
""")

with r:
    md('<div class="lrp-card">')
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    md("</div>")

md("</div>")  # close lrp-layer
