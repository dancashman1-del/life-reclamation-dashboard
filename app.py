import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="LRP Slide — Health", layout="wide")

# -----------------------------
# Mountain background (side-only, closer to content)
# -----------------------------
MOUNTAIN_SVG_FAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
  <path d="M0,420 L120,320 L240,380 L360,260 L480,340 L600,220 L720,320 L900,240 L900,500 L0,500 Z"
        fill="rgba(0,0,0,0.05)"/>
</svg>
"""

MOUNTAIN_SVG_NEAR = """
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
  <path d="M0,460 L140,360 L280,430 L420,300 L560,410 L700,280 L820,370 L900,320 L900,500 L0,500 Z"
        fill="rgba(0,0,0,0.10)"/>
</svg>
"""

def svg_data_uri(svg: str) -> str:
    svg = svg.replace("\n", "").replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "'")
    return f"data:image/svg+xml,{svg}"

far_uri = svg_data_uri(MOUNTAIN_SVG_FAR)
near_uri = svg_data_uri(MOUNTAIN_SVG_NEAR)

st.markdown(
    f"""
    <style>
      .stApp {{
        background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(250,250,250,1) 100%);
      }}

      /* LEFT mountains slightly narrower */
      .lrp-mtn-left {{
        position: fixed;
        left: 0;
        top: 70px;
        width: 18vw;
        height: calc(100vh - 70px);
        background-image: url("{far_uri}"), url("{near_uri}");
        background-repeat: no-repeat, no-repeat;
        background-size: 140% auto, 155% auto;
        background-position: left 55%, left 78%;
        pointer-events: none;
        z-index: 0;
      }}

      /* RIGHT mountains closer / stronger */
      .lrp-mtn-right {{
        position: fixed;
        right: 0;
        top: 70px;
        width: 26vw;
        height: calc(100vh - 70px);
        background-image: url("{far_uri}"), url("{near_uri}");
        background-repeat: no-repeat, no-repeat;
        background-size: 145% auto, 165% auto;
        background-position: right 50%, right 80%;
        transform: scaleX(-1);
        pointer-events: none;
        z-index: 0;
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

      .lrp-bullets-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px 18px;
        margin-top: 6px;
      }}

      .lrp-bullet {{
        font-size: 1.0rem;
        color: rgba(0,0,0,0.78);
        line-height: 1.35rem;
      }}

      .lrp-subtle {{
        color: rgba(0,0,0,0.60);
      }}

      .lrp-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(0,0,0,0.12);
        background: rgba(0,0,0,0.03);
        font-weight: 700;
        font-size: 0.95rem;
      }}

      .lrp-dot {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: rgba(0,160,80,0.85);
        border: 1px solid rgba(0,0,0,0.15);
      }}

      /* Remove Streamlit extra whitespace between widgets a bit */
      div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stMarkdownContainer"]) {{
        margin-bottom: 0.2rem;
      }}
    </style>

    <div class="lrp-mtn-left"></div>
    <div class="lrp-mtn-right"></div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Content data (start with 0–5 and 5–10; add more later)
# -----------------------------
HEALTH_SAL = {
    (0, 5): {
        "title": "HEALTH · SAL · Ages 0–5",
        "term": "health /helTH/",
        "def1": "the absence of disease or infirmity",
        "def2": "also: the capacity to live, move, and engage fully with life",
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
        "check": "GREEN",
    },
    (5, 10): {
        "title": "HEALTH · SAL · Ages 5–10",
        "term": "health /helTH/",
        "def1": "the absence of disease or infirmity",
        "def2": "also: the capacity to live, move, and engage fully with life",
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
        "check": "GREEN",
    },
}

# -----------------------------
# Age band selector (simple slider)
# -----------------------------
bands = list(HEALTH_SAL.keys())
band_labels = [f"{a}–{b}" for a, b in bands]
band_index = st.slider("Age band", 0, len(bands) - 1, 0, label_visibility="collapsed")
band = bands[band_index]
content = HEALTH_SAL[band]

# -----------------------------
# Header card: title/defs on left, bullets on right (2×2)
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
# Graph: show ONLY the segment for the selected age band
# -----------------------------
# For now we use a simple baseline curve and just show the chosen segment.
# Later we’ll drop in your finalized SAL curve.
def sal_health_value(a: int) -> float:
    if a <= 10:
        return 92
    if a <= 40:
        return 92 - (a - 10) * 0.55
    if a <= 75:
        return 75 - (a - 40) * 0.85
    return max(5, 45 - (a - 75) * 2.0)

a0, a1 = band
seg_ages = list(range(a0, a1 + 1))
seg_y = [sal_health_value(a) for a in seg_ages]

fig = go.Figure()
fig.add_trace(go.Scatter(x=seg_ages, y=seg_y, mode="lines", line=dict(width=5), hoverinfo="skip"))

# Window the x-axis tightly around the band (gives more “zoomed-in” impact)
pad_left = 1
pad_right = 2
x_min = max(0, a0 - pad_left)
x_max = min(92, a1 + pad_right)

fig.update_layout(
    height=460,
    margin=dict(l=35, r=20, t=10, b=35),
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(
        title="Age",
        range=[x_min, x_max],
        tickmode="linear",
        dtick=1 if (x_max - x_min) <= 10 else 5,
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
# Bottom row: left "instruments" + big graph
# -----------------------------
left, center = st.columns([1.05, 2.95], gap="large")

with left:
    # No "Chapter Descriptor" label — just the line itself as a quiet kicker
    st.markdown(
        f"""
        <div class="lrp-card">
          <div style="font-weight:780; font-size:1.05rem; margin-bottom:12px;">
            {content["chapter"]}
          </div>

          <div style="font-size:0.85rem; letter-spacing:0.6px; text-transform:uppercase; color:rgba(0,0,0,0.55);">
            Diagnosis
          </div>
          <div style="font-size:1.0rem; color:rgba(0,0,0,0.78); margin-bottom:12px;">
            {content["diagnosis"]}
          </div>

          <div style="font-size:0.85rem; letter-spacing:0.6px; text-transform:uppercase; color:rgba(0,0,0,0.55);">
            Prescription
          </div>
          <div style="font-size:1.0rem; color:rgba(0,0,0,0.78); margin-bottom:14px;">
            {content["prescription"]}
          </div>

          <div style="font-size:0.85rem; letter-spacing:0.6px; text-transform:uppercase; color:rgba(0,0,0,0.55); margin-bottom:6px;">
            Check Engine
          </div>
          <div class="lrp-pill"><span class="lrp-dot"></span> {content["check"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with center:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.caption("Template: bullets moved to header-right; graph shows only the selected age-band segment; mountains stay in side margins.")
