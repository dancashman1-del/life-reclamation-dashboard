import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="LRP Slide — Health", layout="wide")

# -----------------------------
# Background mountains (bottom band + side hints)
# -----------------------------
MOUNTAIN_SVG_FAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="520" viewBox="0 0 1400 520">
  <path d="M0,420 L170,315 L330,385 L520,250 L700,360 L880,215 L1040,330 L1220,240 L1400,280 L1400,520 L0,520 Z"
        fill="rgba(0,0,0,0.05)"/>
</svg>
"""

MOUNTAIN_SVG_NEAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="520" viewBox="0 0 1400 520">
  <path d="M0,475 L200,360 L390,445 L600,295 L780,430 L980,275 L1160,375 L1400,315 L1400,520 L0,520 Z"
        fill="rgba(0,0,0,0.12)"/>
</svg>
"""

def svg_data_uri(svg: str) -> str:
    svg = svg.replace("\n", "").replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "'")
    return f"data:image/svg+xml,{svg}"

far_uri = svg_data_uri(MOUNTAIN_SVG_FAR)
near_uri = svg_data_uri(MOUNTAIN_SVG_NEAR)

# Bigger engine icon (fill container better)
ENGINE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" aria-hidden="true">
  <g fill="none" stroke="currentColor" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 22 h24 v20 H18 z"/>
    <path d="M24 22 v-6 h12 v6"/>
    <path d="M18 30 h-6 v8 h6"/>
    <path d="M42 30 h10 v8 H42"/>
    <path d="M22 42 h16"/>
    <path d="M24 32 h0"/>
    <path d="M32 32 h0"/>
    <path d="M40 32 h0"/>
  </g>
</svg>
"""

st.markdown(
f"""
<style>
  .stApp {{
    background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(250,250,250,1) 100%);
  }}

  /* High as possible WITHOUT clipping */
  .block-container {{
    position: relative;
    z-index: 1;
    padding-top: 0.45rem;     /* safe top */
    padding-bottom: 1.0rem;
  }}
  .block-container > div:first-child {{
    margin-top: -0.25rem;     /* lift slightly but safe */
  }}

  /* Full-width bottom band: "rises" left->right, then reappears */
  .lrp-mtn-bottom {{
    position: fixed;
    left: 0;
    right: 0;
    bottom: -2vh;
    height: 55vh;
    background-image: url("{far_uri}"), url("{near_uri}");
    background-repeat: repeat-x, repeat-x;
    background-size: 85% auto, 92% auto;
    background-position: 38% 92%, 52% 104%;
    pointer-events: none;
    z-index: 0;

    clip-path: polygon(
      0% 82%,
      40% 82%,
      62% 76%,
      78% 70%,
      100% 60%,
      100% 100%,
      0% 100%
    );
  }}

  /* Side hints (right closer) */
  .lrp-mtn-left {{
    position: fixed;
    left: 0;
    top: 56px;
    width: 15vw;
    height: calc(100vh - 56px);
    background-image: url("{far_uri}"), url("{near_uri}");
    background-repeat: no-repeat, no-repeat;
    background-size: 170% auto, 200% auto;
    background-position: left 56%, left 84%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.95;
  }}

  .lrp-mtn-right {{
    position: fixed;
    right: 0;
    top: 56px;
    width: 36vw;              /* closer */
    height: calc(100vh - 56px);
    background-image: url("{far_uri}"), url("{near_uri}");
    background-repeat: no-repeat, no-repeat;
    background-size: 170% auto, 215% auto;
    background-position: right 48%, right 86%;
    transform: scaleX(-1);
    pointer-events: none;
    z-index: 0;
    opacity: 0.95;
  }}

  .lrp-card {{
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    backdrop-filter: blur(3px);
  }}

  /* Slide title */
  .lrp-title {{
    font-size: 1.78rem;
    font-weight: 900;
    margin: 0 0 0.25rem 0;
  }}

  /* Dictionary entry */
  .dict-line1 {{
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin-top: 2px;
  }}
  .dict-headword {{
    font-size: 1.30rem;
    font-weight: 900;
    color: rgba(0,0,0,0.86);
  }}
  .dict-meta {{
    font-size: 0.95rem;
    color: rgba(0,0,0,0.48);
    font-weight: 650;
    letter-spacing: 0.2px;
  }}
  .dict-pron {{
    font-size: 1.02rem;
    color: rgba(0,0,0,0.60);
    font-style: italic;
    margin-top: 2px;
  }}
  .dict-defs {{
    margin-top: 8px;
    color: rgba(0,0,0,0.74);
    font-size: 1.02rem;
    line-height: 1.35rem;
  }}
  .dict-def {{
    display: grid;
    grid-template-columns: 22px 1fr;
    column-gap: 8px;
    margin: 4px 0;
  }}
  .dict-num {{
    color: rgba(0,0,0,0.45);
    font-weight: 750;
  }}

  .lrp-bullets-heading {{
    font-size: 1.08rem;
    font-weight: 900;
    color: rgba(0,0,0,0.78);
    margin-bottom: 10px;
  }}

  .lrp-bullets-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 18px;
  }}

  .lrp-bullet {{
    font-size: 1.0rem;
    color: rgba(0,0,0,0.78);
    line-height: 1.35rem;
  }}

  .lrp-label {{
    font-size: 0.85rem;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: rgba(0,0,0,0.55);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .lrp-label .emoji {{
    font-size: 1.45rem; /* bigger */
    line-height: 1;
  }}

  /* Big engine indicator */
  .lrp-engine-pill {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 84px;
    height: 62px;
    border-radius: 20px;
    border: 1px solid rgba(0,0,0,0.12);
    background: rgba(0,0,0,0.03);
    color: rgba(0,160,80,0.95);
    padding: 6px;
  }}
  .lrp-engine-pill svg {{
    width: 78%;
    height: 78%;
  }}

  /* Slider spacing */
  div[data-testid="stSlider"] {{
    padding-top: 0.15rem;
  }}
</style>

<div class="lrp-mtn-bottom"></div>
<div class="lrp-mtn-left"></div>
<div class="lrp-mtn-right"></div>
""",
unsafe_allow_html=True
)

# -----------------------------
# Content (extend later)
# -----------------------------
HEALTH_SAL = {
    (0, 5): {
        "title": "HEALTH · SAL · Ages 0–5",
        "headword": "health",
        "pos": "noun",
        "pron": "/helTH/",
        "def1": "the absence of disease or infirmity",
        "def2": "also: the capacity to live, move, and engage fully with life",
        "bul_heading": "Health is assumed and unexamined.",
        "bullets": [
            "Lots of unstructured play, exploration, and bonding with parents",
            "Sleep is mostly protected; routines feel supportive and calming",
            "Daycare schedules, frequent illness, and hand-offs begin to disrupt rhythm",
            "Screens are introduced occasionally to soothe, distract, or buy quiet",
        ],
        "diagnosis": "Everything looks normal and on track for age.",
        "prescription": (
            "Stay on schedule with vaccinations. Use antibiotics and fever reducers when needed. "
            "Kids are resilient — there’s nothing to worry about."
        ),
    },
    (5, 10): {
        "title": "HEALTH · SAL · Ages 5–10",
        "headword": "health",
        "pos": "noun",
        "pron": "/helTH/",
        "def1": "the absence of disease or infirmity",
        "def2": "also: the capacity to live, move, and engage fully with life",
        "bul_heading": "Activity is natural and effortless.",
        "bullets": [
            "Real play with friends is still common; movement happens naturally and joyfully",
            "A first sport or activity is introduced — with fruit snacks and juice boxes as the reward",
            "Screens and online entertainment increasingly fill “in-between” time",
            "Busy schedules lead to quicker meals and less intentional nutrition",
        ],
        "diagnosis": "Healthy growth and development within expected ranges.",
        "prescription": (
            "Keep doing what you’re doing. Encourage activity, limit treats when you can, "
            "and address issues as they come up."
        ),
    },
}

bands = list(HEALTH_SAL.keys())
band_labels = [f"{a}–{b}" for a, b in bands]

# -----------------------------
# SAL curve (smooth arc):
# - 0–10: high
# - 55: ~35 (lower functional / upper frail)
# - ends at 77; blank to 92
# We sample yearly points, then render as spline.
# -----------------------------
def sal_health_value(age: float) -> float:
    if age <= 10:
        return 92.0

    if age <= 55:
        # gently accelerating decline (curved)
        # t in [0..1]
        t = (age - 10) / (55 - 10)
        # ease-in curve
        curved = t**1.35
        return 92.0 + (35.0 - 92.0) * curved

    if age <= 77:
        # steeper late decline (also curved)
        t = (age - 55) / (77 - 55)
        curved = t**1.20
        return 35.0 + (15.0 - 35.0) * curved

    return 15.0

# Context (0..77)
ages_context = [a for a in range(0, 78)]
y_context = [sal_health_value(a) for a in ages_context]

# Segment highlight
# We sample yearly points within the band to match the spline style
def segment_points(a0: int, a1: int):
    xs = [a for a in range(a0, a1 + 1)]
    ys = [sal_health_value(a) for a in xs]
    return xs, ys

# -----------------------------
# Top row: title card | slider | bullets card
# -----------------------------
col_title, col_slider, col_bullets = st.columns([1.45, 0.55, 1.70], gap="large")

with col_slider:
    idx = st.slider("Age band", 0, len(bands) - 1, 0)
    st.caption(f"Ages {band_labels[idx]}")

band = bands[idx]
c = HEALTH_SAL[band]

with col_title:
    st.markdown(
f"""
<div class="lrp-card">
  <div class="lrp-title">{c["title"]}</div>

  <div class="dict-line1">
    <div class="dict-headword">{c["headword"]}</div>
    <div class="dict-meta">• {c["pos"]}</div>
  </div>

  <div class="dict-pron">{c["pron"]}</div>

  <div class="dict-defs">
    <div class="dict-def"><div class="dict-num">1)</div><div>{c["def1"]}</div></div>
    <div class="dict-def"><div class="dict-num">2)</div><div>{c["def2"]}</div></div>
  </div>
</div>
""",
unsafe_allow_html=True
    )

with col_bullets:
    b = c["bullets"]
    st.markdown(
f"""
<div class="lrp-card">
  <div class="lrp-bullets-heading">{c["bul_heading"]}</div>
  <div class="lrp-bullets-grid">
    <div class="lrp-bullet">• {b[0]}</div>
    <div class="lrp-bullet">• {b[1]}</div>
    <div class="lrp-bullet">• {b[2]}</div>
    <div class="lrp-bullet">• {b[3]}</div>
  </div>
</div>
""",
unsafe_allow_html=True
    )

st.write("")

# -----------------------------
# Plot (taller + smooth)
# -----------------------------
a0, a1 = band
ages_seg, y_seg = segment_points(a0, a1)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=ages_context,
    y=y_context,
    mode="lines",
    line=dict(width=2.6, color="rgba(0,0,0,0.22)", shape="spline"),
    hoverinfo="skip",
))

fig.add_trace(go.Scatter(
    x=ages_seg,
    y=y_seg,
    mode="lines",
    line=dict(width=8, color="red", shape="spline"),
    hoverinfo="skip",
))

tickvals = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,77,80,85,90,92]
ticktext = [f"<b>{v}</b>" if v in (77, 92) else str(v) for v in tickvals]

fig.update_layout(
    height=590,
    margin=dict(l=35, r=20, t=10, b=35),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
        title="Age",
        range=[0, 92],
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
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
# Bottom row: left instruments + graph
# -----------------------------
left, center = st.columns([1.05, 2.95], gap="large")

with left:
    st.markdown(
f"""
<div class="lrp-card">
  <div class="lrp-label"><span class="emoji">🩺</span> Diagnosis</div>
  <div style="font-size:1.02rem; color:rgba(0,0,0,0.78); margin-bottom:14px;">
    {c["diagnosis"]}
  </div>

  <div class="lrp-label"><span class="emoji">💊</span> Prescription</div>
  <div style="font-size:1.02rem; color:rgba(0,0,0,0.78); margin-bottom:18px;">
    {c["prescription"]}
  </div>

  <div class="lrp-label">Check Engine</div>
  <div class="lrp-engine-pill" title="Engine status (green)">
    {ENGINE_SVG}
  </div>
</div>
""",
unsafe_allow_html=True
    )

with center:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
