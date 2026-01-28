import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="LRP Slide — Health", layout="wide")

# -----------------------------
# Background mountains (side + full-bottom band)
# -----------------------------
MOUNTAIN_SVG_FAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500">
  <path d="M0,410 L140,315 L280,380 L420,250 L560,350 L700,215 L840,320 L1020,235 L1200,265 L1200,500 L0,500 Z"
        fill="rgba(0,0,0,0.05)"/>
</svg>
"""

MOUNTAIN_SVG_NEAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500">
  <path d="M0,465 L170,360 L330,435 L510,295 L670,415 L840,275 L1000,365 L1200,310 L1200,500 L0,500 Z"
        fill="rgba(0,0,0,0.11)"/>
</svg>
"""

def svg_data_uri(svg: str) -> str:
    svg = svg.replace("\n", "").replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "'")
    return f"data:image/svg+xml,{svg}"

far_uri = svg_data_uri(MOUNTAIN_SVG_FAR)
near_uri = svg_data_uri(MOUNTAIN_SVG_NEAR)

# -----------------------------
# Simple inline SVG "engine" icon (colorable)
# -----------------------------
ENGINE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 64 64" aria-hidden="true">
  <g fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
    <!-- engine block -->
    <path d="M18 22 h24 v20 H18 z"/>
    <!-- top intake -->
    <path d="M24 22 v-6 h12 v6"/>
    <!-- left pipe -->
    <path d="M18 30 h-6 v8 h6"/>
    <!-- right pipe -->
    <path d="M42 30 h10 v8 H42"/>
    <!-- bottom oil pan -->
    <path d="M22 42 h16"/>
    <!-- bolts / detail -->
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

      /* Side mountain layers */
      .lrp-mtn-left {{
        position: fixed;
        left: 0;
        top: 70px;
        width: 18vw;
        height: calc(100vh - 70px);
        background-image: url("{far_uri}"), url("{near_uri}");
        background-repeat: no-repeat, no-repeat;
        background-size: 155% auto, 175% auto;
        background-position: left 55%, left 80%;
        pointer-events: none;
        z-index: 0;
      }}

      .lrp-mtn-right {{
        position: fixed;
        right: 0;
        top: 70px;
        width: 28vw;
        height: calc(100vh - 70px);
        background-image: url("{far_uri}"), url("{near_uri}");
        background-repeat: no-repeat, no-repeat;
        background-size: 155% auto, 185% auto;
        background-position: right 50%, right 83%;
        transform: scaleX(-1);
        pointer-events: none;
        z-index: 0;
      }}

      /* Full-width bottom band so the range "continues behind the graph" */
      .lrp-mtn-bottom {{
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        height: 44vh;
        background-image: url("{far_uri}"), url("{near_uri}");
        background-repeat: repeat-x, repeat-x;
        background-size: 85% auto, 95% auto;
        background-position: 40% 90%, 55% 102%;
        opacity: 1;
        pointer-events: none;
        z-index: 0;
        /* Rise slightly left->right so it feels like the range continues */
        clip-path: polygon(0% 72%, 55% 72%, 100% 58%, 100% 100%, 0% 100%);
      }}

      .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 1.0rem;
        padding-bottom: 1.0rem;
      }}

      .lrp-card {{
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        backdrop-filter: blur(3px);
      }}

      .lrp-title {{
        font-size: 1.55rem;
        font-weight: 850;
        margin: 0;
      }}

      .lrp-def {{
        margin-top: 0.35rem;
        font-size: 1.05rem;
        color: rgba(0,0,0,0.70);
        line-height: 1.35rem;
      }}

      .lrp-term {{
        font-weight: 750;
        color: rgba(0,0,0,0.78);
      }}

      .lrp-bullets-heading {{
        font-size: 0.95rem;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        color: rgba(0,0,0,0.55);
        font-weight: 750;
        margin-bottom: 8px;
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

      .lrp-subtle {{
        color: rgba(0,0,0,0.60);
      }}

      .lrp-label {{
        font-size: 0.85rem;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        color: rgba(0,0,0,0.55);
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
      }}

      .lrp-icon {{
        font-size: 1.0rem;
        opacity: 0.85;
      }}

      .lrp-engine-pill {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 34px;
        border-radius: 999px;
        border: 1px solid rgba(0,0,0,0.12);
        background: rgba(0,0,0,0.03);
        color: rgba(0,160,80,0.90); /* green */
      }}
    </style>

    <div class="lrp-mtn-bottom"></div>
    <div class="lrp-mtn-left"></div>
    <div class="lrp-mtn-right"></div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Content data (expand later)
# -----------------------------
HEALTH_SAL = {
    (0, 5): {
        "title": "HEALTH · SAL · Ages 0–5",
        "term": "health /helTH/",
        "def1": "the absence of disease or infirmity",
        "def2": "also: the capacity to live, move, and engage fully with life",
        "summary_heading": "Life Snapshot",
        "chapter": "Beginnings — health is assumed and unexamined.",
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
        "engine_color": "green",
    },
    (5, 10): {
        "title": "HEALTH · SAL · Ages 5–10",
        "term": "health /helTH/",
        "def1": "the absence of disease or infirmity",
        "def2": "also: the capacity to live, move, and engage fully with life",
        "summary_heading": "Life Snapshot",
        "chapter": "Momentum — activity is natural and effortless.",
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
        "engine_color": "green",
    },
}

# -----------------------------
# Realistic SAL health curve (single-source-of-truth)
# NOTE: This is the "real curve" function we’ll keep refining once we bring back
# your canonical SAL points. For ages 0–10 it stays near Fit.
# -----------------------------
def sal_health_value(age: int) -> float:
    # High early years
    if age <= 10:
        return 92.0
    # gradual erosion into adulthood
    if age <= 40:
        return 92.0 - (age - 10) * 0.55
    # faster decline midlife
    if age <= 75:
        return 75.0 - (age - 40) * 0.85
    # end-stage slide (SAL "ends" around 75–77)
    return max(5.0, 45.0 - (age - 75) * 3.5)

# -----------------------------
# Selector (hidden label)
# -----------------------------
bands = list(HEALTH_SAL.keys())
band_index = st.slider("Age band", 0, len(bands) - 1, 0, label_visibility="collapsed")
band = bands[band_index]
content = HEALTH_SAL[band]

# -----------------------------
# Header: left title/defs, right bullets with heading
# -----------------------------
left_hdr, right_hdr = st.columns([1.25, 1.75], gap="large")

with left_hdr:
    st.markdown(
        f"""
        <div class="lrp-card">
          <p class="lrp-title">{content["title"]}</p>
          <div class="lrp-def">
            <div class="lrp-term">{content["term"]}</div>
            <div>{content["def1"]}</div>
            <div class="lrp-subtle">{content["def2"]}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_hdr:
    b = content["bullets"]
    st.markdown(
        f"""
        <div class="lrp-card">
          <div class="lrp-bullets-heading">{content["summary_heading"]}</div>
          <div class="lrp-bullets-grid">
            <div class="lrp-bullet">• {b[0]}</div>
            <div class="lrp-bullet">• {b[1]}</div>
            <div class="lrp-bullet">• {b[2]}</div>
            <div class="lrp-bullet">• {b[3]}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# -----------------------------
# Graph: tight band window (0–5 means 0..5 exactly)
# -----------------------------
a0, a1 = band
seg_ages = list(range(a0, a1 + 1))
seg_y = [sal_health_value(a) for a in seg_ages]

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=seg_ages,
        y=seg_y,
        mode="lines",
        line=dict(width=6, color="red"),  # requested: health line red
        hoverinfo="skip",
    )
)

fig.update_layout(
    height=470,
    margin=dict(l=35, r=20, t=10, b=35),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
        title="Age",
        range=[a0, a1],  # tight
        tickmode="linear",
        dtick=1,
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
# Bottom row: left instruments + big graph
# -----------------------------
left, center = st.columns([1.05, 2.95], gap="large")

with left:
    st.markdown(
        f"""
        <div class="lrp-card">
          <div style="font-weight:820; font-size:1.05rem; margin-bottom:14px;">
            {content["chapter"]}
          </div>

          <div class="lrp-label"><span class="lrp-icon">🩺</span> Diagnosis</div>
          <div style="font-size:1.0rem; color:rgba(0,0,0,0.78); margin-bottom:14px;">
            {content["diagnosis"]}
          </div>

          <div class="lrp-label"><span class="lrp-icon">💊</span> Prescription</div>
          <div style="font-size:1.0rem; color:rgba(0,0,0,0.78); margin-bottom:16px;">
            {content["prescription"]}
          </div>

          <div class="lrp-label">Check Engine</div>
          <div class="lrp-engine-pill" title="Engine status (green)">
            {ENGINE_SVG}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with center:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
