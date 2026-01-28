import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="LRP Slide — Health 0–5", layout="wide")

# -----------------------------
# Mountain background (side-only)
# -----------------------------
# Two SVG layers. We position them on the left and right margins only.
# The center plot area remains clean because the plot sits in a white card.
MOUNTAIN_SVG_FAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
  <path d="M0,420 L120,320 L240,380 L360,260 L480,340 L600,220 L720,320 L900,240 L900,500 L0,500 Z"
        fill="rgba(0,0,0,0.06)"/>
</svg>
"""

MOUNTAIN_SVG_NEAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
  <path d="M0,460 L140,360 L280,430 L420,300 L560,410 L700,280 L820,370 L900,320 L900,500 L0,500 Z"
        fill="rgba(0,0,0,0.10)"/>
</svg>
"""

def svg_data_uri(svg: str) -> str:
    # Minify-ish and URI encode minimally for CSS embedding.
    svg = svg.replace("\n", "").replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "'")
    return f"data:image/svg+xml,{svg}"

far_uri = svg_data_uri(MOUNTAIN_SVG_FAR)
near_uri = svg_data_uri(MOUNTAIN_SVG_NEAR)

st.markdown(
    f"""
    <style>
      /* Page background */
      .stApp {{
        background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(250,250,250,1) 100%);
      }}

      /* Side mountain layers — LEFT */
      .lrp-mtn-left {{
        position: fixed;
        left: 0;
        top: 90px;
        width: 22vw;
        height: calc(100vh - 90px);
        background-image: url("{far_uri}"), url("{near_uri}");
        background-repeat: no-repeat, no-repeat;
        background-size: 120% auto, 130% auto;
        background-position: left 45%, left 70%;
        pointer-events: none;
        z-index: 0;
        opacity: 1;
      }}

      /* Side mountain layers — RIGHT */
      .lrp-mtn-right {{
        position: fixed;
        right: 0;
        top: 90px;
        width: 22vw;
        height: calc(100vh - 90px);
        background-image: url("{far_uri}"), url("{near_uri}");
        background-repeat: no-repeat, no-repeat;
        background-size: 120% auto, 130% auto;
        background-position: right 45%, right 70%;
        transform: scaleX(-1);
        pointer-events: none;
        z-index: 0;
        opacity: 1;
      }}

      /* Ensure content sits above the mountains */
      .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
      }}

      /* Slide title styling */
      .lrp-title {{
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: 0.2px;
        margin: 0;
      }}
      .lrp-subtitle {{
        margin-top: 0.25rem;
        font-size: 1.05rem;
        color: rgba(0,0,0,0.65);
      }}

      /* Card look */
      .lrp-card {{
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 18px;
        padding: 16px 16px 10px 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        backdrop-filter: blur(3px);
      }}

      .lrp-label {{
        font-size: 0.85rem;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        color: rgba(0,0,0,0.55);
        margin-bottom: 6px;
      }}

      .lrp-pill {{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(0,0,0,0.12);
        background: rgba(0,0,0,0.03);
        font-weight: 650;
        font-size: 0.95rem;
      }}

      .lrp-bullet {{
        margin: 0.25rem 0;
        line-height: 1.35rem;
      }}

      /* Make plotly background clean */
      .js-plotly-plot .plotly .main-svg {{
        border-radius: 14px;
      }}
    </style>

    <div class="lrp-mtn-left"></div>
    <div class="lrp-mtn-right"></div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Slide content (Health · SAL · Ages 0–5)
# -----------------------------
TITLE = "HEALTH · SAL · Ages 0–5"
TERM = "health /helTH/"
DEF_SAL = "the absence of disease or infirmity"
DEF_LRP = "also: the capacity to live, move, and engage fully with life"

CHAPTER = "Beginnings — health is assumed and unexamined."
BULLETS = [
    "Lots of unstructured play, exploration, and bonding with parents",
    "Sleep is mostly protected; routines feel supportive and calming",
    "Daycare schedules, frequent illness, and hand-offs begin to disrupt rhythm",
    "Screens are introduced occasionally to soothe, distract, or buy quiet",
]
DIAGNOSIS = "Everything looks normal and on track for age."
PRESCRIPTION = (
    "Stay on schedule with vaccinations. Use antibiotics and fever reducers when needed. "
    "Kids are resilient — there’s nothing to worry about."
)
CHECK_ENGINE = "🟢 GREEN"

# -----------------------------
# Plot: simple trajectory stub (0–92)
# -----------------------------
# For this first slide, keep it clean: one line with the early segment emphasized.
# We'll later swap in the full SAL curve you already designed.
ages = list(range(0, 93))
# A simple illustrative curve: high early, then slowly down; you can replace later.
y = []
for a in ages:
    if a <= 10:
        y.append(92)
    elif a <= 40:
        y.append(92 - (a - 10) * 0.55)
    elif a <= 75:
        y.append(75 - (a - 40) * 0.85)
    else:
        y.append(45 - (a - 75) * 2.0)
y = [max(5, v) for v in y]

fig = go.Figure()
fig.add_trace(go.Scatter(x=ages, y=y, mode="lines", line=dict(width=4), hoverinfo="skip"))

# Emphasize the current age band (0–5) with a subtle highlight band
fig.add_vrect(x0=0, x1=5, fillcolor="rgba(0,0,0,0.06)", line_width=0)

# Axes: Fit / Functional / Frail vibe without heavy labels
fig.update_layout(
    height=420,
    margin=dict(l=40, r=20, t=20, b=40),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
        title="Age",
        range=[0, 92],
        tickmode="array",
        tickvals=[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,77,80,85,90,92],
        gridcolor="rgba(0,0,0,0.06)",
        zeroline=False,
    ),
    yaxis=dict(
        range=[0, 100],
        tickmode="array",
        tickvals=[85, 55, 25],
        ticktext=["Fit", "Functional", "Frail"],
        gridcolor="rgba(0,0,0,0.06)",
        zeroline=False,
    ),
    showlegend=False,
)

# -----------------------------
# Layout
# -----------------------------
# Title row
st.markdown(
    f"""
    <div class="lrp-card">
      <p class="lrp-title">{TITLE}</p>
      <div class="lrp-subtitle">
        <span style="font-weight:700;">{TERM}</span><br/>
        <span>{DEF_SAL}</span><br/>
        <span style="opacity:0.85;">{DEF_LRP}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")  # small spacer

# Main row: left instruments, center plot, right bullets
left, center, right = st.columns([1.05, 1.8, 1.35], gap="large")

with left:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="lrp-label">Chapter Descriptor</div><div style="font-weight:750;">{CHAPTER}</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown(f'<div class="lrp-label">Diagnosis</div><div style="font-size:1.0rem;">{DIAGNOSIS}</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown(f'<div class="lrp-label">Prescription</div><div style="font-size:1.0rem;">{PRESCRIPTION}</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown(f'<div class="lrp-label">Check Engine</div><div class="lrp-pill">{CHECK_ENGINE}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with center:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    st.markdown('<div class="lrp-label">Bullets</div>', unsafe_allow_html=True)
    for b in BULLETS:
        st.markdown(f'<div class="lrp-bullet">• {b}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.caption("Slide 1 template — mountains are confined to the side margins so the graph stays clean.")
