import streamlit as st
import plotly.graph_objects as go
import textwrap

st.set_page_config(page_title="LRP — Health", layout="wide")

# =============================
# GLOBAL UI SCALE
# =============================
UI_SCALE = 0.86

def rem(x):
    return f"{x * UI_SCALE}rem"

def md(html: str):
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)

# -----------------------------
# Simple SVG icons (Diagnosis / Prescription / Engine)
# -----------------------------
ICON_DIAG = """
<svg viewBox="0 0 24 24" aria-hidden="true">
  <path fill="currentColor" d="M19 3h-3.5a3.5 3.5 0 0 0-7 0H5a2 2 0 0 0-2 2v2h18V5a2 2 0 0 0-2-2Zm-7-1a1.5 1.5 0 0 1 1.5 1.5h-3A1.5 1.5 0 0 1 12 2Z"/>
  <path fill="currentColor" d="M3 9v10a2 2 0 0 0 2 2h6v-2H5V9H3Zm16 0v10h-6v2h6a2 2 0 0 0 2-2V9h-2Z"/>
  <path fill="currentColor" d="M11 11h2v7h-2z"/>
  <path fill="currentColor" d="M8 14h8v2H8z"/>
</svg>
"""

ICON_RX = """
<svg viewBox="0 0 24 24" aria-hidden="true">
  <path fill="currentColor" d="M6 3h7a4 4 0 0 1 0 8H9v2h3.2l3.9 5.7-1.7 1.2L10.8 15H9v6H6V3Zm3 2v4h4a2 2 0 0 0 0-4H9Z"/>
  <path fill="currentColor" d="M16.2 13.3 21 20h-2.5l-3.6-5.1z"/>
</svg>
"""

ENGINE_SVG = """
<svg viewBox="0 0 64 64" aria-hidden="true">
  <g fill="none" stroke="currentColor" stroke-width="6.2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 22 h24 v20 H18 z"/>
    <path d="M24 22 v-6 h12 v6"/>
    <path d="M18 30 h-6 v8 h6"/>
    <path d="M42 30 h10 v8 H42"/>
    <path d="M22 42 h16"/>
  </g>
</svg>
"""

# -----------------------------
# CSS
# -----------------------------
md(f"""
<style>
/* BIG safe top gutter — fixes clipping under Streamlit Cloud chrome */
.block-container {{
  padding-top: {rem(2.35)};
  padding-bottom: {rem(0.9)};
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
  display:flex;
  align-items:center;
  gap: 10px;
  font-size: {rem(0.78)};
  text-transform: uppercase;
  color: rgba(0,0,0,0.55);
  letter-spacing: 0.4px;
  margin-bottom: {rem(0.35)};
}}
.label .ico {{
  width: {rem(1.15)};
  height: {rem(1.15)};
  color: rgba(0,0,0,0.45);
}}

.body {{
  font-size: {rem(0.98)};
  color: rgba(0,0,0,0.78);
  line-height: 1.45em;
}}

.engine-wrap {{
  margin-top: {rem(0.15)};
  display:flex;
  align-items:center;
  gap: {rem(0.5)};
}}
.engine-big {{
  width: {rem(3.3)};
  height: {rem(3.0)};
  color: rgba(0,150,80,0.95);
}}
.engine-big svg {{
  width: 100%;
  height: 100%;
}}

/* Nav strip (feels like a slider) */
.nav-strip {{
  display:flex;
  flex-direction:column;
  gap: {rem(0.5)};
}}
.nav-center {{
  text-align:center;
  font-weight: 850;
  font-size: {rem(0.95)};
  color: rgba(0,0,0,0.70);
}}
.dots {{
  display:flex;
  justify-content:center;
  gap: {rem(0.35)};
}}
.dot {{
  width: {rem(0.5)};
  height: {rem(0.5)};
  border-radius: 999px;
  background: rgba(0,0,0,0.16);
}}
.dot.on {{
  background: rgba(220,0,0,0.75);
}}

/* Streamlit buttons: more slide-native */
div.stButton > button {{
  border-radius: 12px;
  padding: 0.55rem 0.85rem;
  font-weight: 650;
}}
</style>

<div class="lrp-layer">
""")

# -----------------------------
# DATA
# -----------------------------
BANDS = [
    (0, 5, "Health is assumed and unexamined."),
    (5, 10, "Activity is natural and effortless."),
    # we'll add more bands later — this nav scales automatically
]

if "idx" not in st.session_state:
    st.session_state.idx = 0

def health_value(age: float) -> float:
    # keep your curve
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
# TOP ROW: Title | Nav | Bullets
# -----------------------------
col_title, col_nav, col_bul = st.columns([1.45, 0.85, 1.70], gap="large")

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
    # Buttons
    b1, b2 = st.columns(2)
    with b1:
        if st.button("◀ Previous", disabled=(st.session_state.idx == 0), use_container_width=True):
            st.session_state.idx -= 1
            st.rerun()
    with b2:
        if st.button("Next ▶", disabled=(st.session_state.idx == len(BANDS) - 1), use_container_width=True):
            st.session_state.idx += 1
            st.rerun()

    # Center label + dots (the "slider feel")
    dots_html = "".join(
        f'<div class="dot {"on" if i == st.session_state.idx else ""}"></div>'
        for i in range(len(BANDS))
    )
    md(f"""
<div class="nav-strip">
  <div class="nav-center">Ages {a0}–{a1}</div>
  <div class="dots">{dots_html}</div>
</div>
""")

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
# PLOT — "SURPRISE": show ONLY selected band (no grey future line)
# -----------------------------
seg_x = list(range(a0, a1 + 1))
seg_y = [health_value(a) for a in seg_x]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=seg_x, y=seg_y,
    mode="lines",
    line=dict(color="red", width=8, shape="spline"),
    hoverinfo="skip"
))

tickvals = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,77,80,85,90,92]
ticktext = [f"<b>{v}</b>" if v in (77, 92) else str(v) for v in tickvals]

fig.update_layout(
    height=int(520 * UI_SCALE),
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
        showline=True,            # axis line
        linecolor="rgba(0,0,0,0.18)",
        linewidth=1,
        mirror=False
    ),
    yaxis=dict(
        range=[0, 100],
        tickvals=[85, 55, 25],
        ticktext=["Fit", "Functional", "Frail"],
        gridcolor="rgba(0,0,0,0.06)",
        zeroline=False,
        showline=True,            # axis line
        linecolor="rgba(0,0,0,0.18)",
        linewidth=1,
        mirror=False
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
  <div class="label"><span class="ico">{ICON_DIAG}</span> Diagnosis</div>
  <div class="body">Everything looks normal and on track for age.</div>

  <div class="label" style="margin-top:{rem(0.75)};"><span class="ico">{ICON_RX}</span> Prescription</div>
  <div class="body">
    Stay on schedule with vaccinations. Use antibiotics and fever reducers when needed.
    Kids are resilient — there’s nothing to worry about.
  </div>

  <div class="label" style="margin-top:{rem(0.85)};">Check Engine</div>
  <div class="engine-wrap">
    <div class="engine-big" title="Engine status (green)">{ENGINE_SVG}</div>
  </div>
</div>
""")

with r:
    md('<div class="lrp-card">')
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    md("</div>")

md("</div>")  # close lrp-layer
