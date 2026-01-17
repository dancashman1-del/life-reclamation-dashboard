# app.py — Life Reclamation Project (Streamlit) — FULL REPLACEMENT
# Deploy on Streamlit Cloud:
# - Ensure requirements.txt includes:
#   streamlit
#   plotly

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go


# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Life Reclamation Project — RAMP Protocol", layout="wide")


# ----------------------------
# GLOBAL STYLES (cards / gauges)
# ----------------------------
st.markdown(
    """
<style>
/* Soft background */
.block-container { padding-top: 1.0rem; }
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #fbf7f0 0%, #f7f2ea 60%, #f5efe6 100%);
}

/* Remove extra gap above header */
h1, h2, h3 { margin-bottom: 0.25rem; }

/* Left bullet card */
.lrp-card {
  background: rgba(255,255,255,0.72);
  border: 2px solid rgba(0,0,0,0.08);
  border-radius: 18px;
  padding: 18px 18px 14px 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

/* Generic rounded card */
.rounded-card {
  background: rgba(255,255,255,0.72);
  border: 2px solid rgba(0,0,0,0.08);
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
  margin-bottom: 14px;
}

/* Gauge circle (airplane-instrument vibe) */
.gauge-wrap {
  background: rgba(255,255,255,0.72);
  border: 2px solid rgba(0,0,0,0.10);
  border-radius: 18px;
  padding: 14px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
  margin-bottom: 14px;
}
.gauge {
  width: 210px;
  height: 210px;
  margin: 0 auto;
  border-radius: 999px;
  border: 4px solid rgba(0,0,0,0.70); /* black outline */
  background: rgba(255,255,255,0.40);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 18px;
}
.gauge-title {
  font-weight: 900;
  letter-spacing: 0.3px;
  font-size: 14px;
  margin-bottom: 8px;
  text-transform: uppercase;
  opacity: 0.85;
}
.gauge-icon {
  font-size: 28px;
  line-height: 28px;
  margin-bottom: 10px;
}
.gauge-body {
  font-size: 13px;
  line-height: 1.35;
  opacity: 0.9;
}

/* Make Plotly chart corners match */
.js-plotly-plot, .plotly, .plot-container {
  border-radius: 18px !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------
# COPY (per-window)
# ----------------------------
TITLE = "Life Reclamation Project — RAMP Protocol"
SUBTITLE = "The intervention path — first 5 years, massive reversal"


# ----------------------------
# SERIES DEFINITIONS (KNOTS)
# ----------------------------
# SAL ends at 77 (death marker)
SAL_KNOTS = [
    (0, 78),
    (20, 77),
    (45, 66),
    (55, 50),
    (62, 38),
    (70, 20),
    (77, 5),
]

# LRP peaks by 60, stays high 60–65, gradual decline, faster only ~90–92
LRP_KNOTS = [
    (55, 52),
    (60, 78),
    (65, 78),
    (75, 70),
    (85, 62),
    (90, 58),
    (91, 55),
    (92, 44),
]


# ----------------------------
# WINDOW CHAPTERS (advancing segments)
# ----------------------------
SAL_WINDOWS = [
    (0, 5),
    (5, 10),
    (10, 20),
    (20, 30),
    (30, 40),
    (40, 50),
    (50, 55),
    (55, 60),
    (60, 65),
    (65, 70),
    (70, 75),
    (75, 77),
]

LRP_WINDOWS = [
    (55, 60),
    (60, 65),
    (65, 70),
    (70, 75),
    (75, 80),
    (80, 85),
    (85, 90),
    (90, 92),
]


PHASE_COPY = {
    # LRP examples
    ("LRP", (55, 60)): {
        "left_title": "Reclamation Begins (first 5 years)",
        "bullets": [
            "Strength training becomes non-negotiable",
            "Zone 2 base rebuilt; hiking feels easier",
            "Sleep regularized; mornings feel powerful",
            "Real food replaces “dieting”",
        ],
        "diag": "Baseline labs & BP improve fast once compliance is real.",
        "rx": "Self-initiated strength + Zone 2 + HIIT; protect sleep; 95% real food.",
        "ce": "Biomarkers drift quietly — until they don’t.",
    },
    ("LRP", (60, 65)): {
        "left_title": "Peak Window (hold the line)",
        "bullets": [
            "Keep strength heavy and consistent",
            "Zone 2 feels “easy” — that’s the point",
            "Trips and hikes become identity, not “exercise”",
            "Stress hygiene keeps cravings quiet",
        ],
        "diag": "Doctor is stunned — keep doing whatever you’re doing.",
        "rx": "Same basics, tighter sleep, and continued strength intent.",
        "ce": "Maintain the system before life tests it.",
    },
    # SAL examples (simple defaults)
    ("SAL", (60, 65)): {
        "left_title": "Default Path (minimized early, medicated later)",
        "bullets": [
            "Movement becomes optional",
            "Sleep drifts, stress rises",
            "Food becomes convenience",
            "Health becomes reactive",
        ],
        "diag": "Small issues accumulate quietly over time.",
        "rx": "“Wait and see” becomes the plan — until it’s not.",
        "ce": "The warning light shows up late, not early.",
    },
}

DEFAULT_COPY = {
    "LRP": {
        "left_title": "Sustained Advantage (stay deliberate)",
        "bullets": [
            "Protect training like a meeting",
            "Keep protein and steps boringly consistent",
            "Use travel as active living fuel",
            "Course-correct early, not later",
        ],
        "diag": "Maintenance works when it’s real maintenance.",
        "rx": "Strength 2x/week minimum; Zone 2 base; HIIT sparingly.",
        "ce": "Small lapses compound — so do small wins.",
    },
    "SAL": {
        "left_title": "Default Path (drift)",
        "bullets": [
            "Fitness erodes gradually",
            "Pain avoidance replaces training",
            "More sitting, less strength",
            "More meds, less capacity",
        ],
        "diag": "Decline looks slow—until it suddenly isn’t.",
        "rx": "Medication manages symptoms, not capacity.",
        "ce": "The warning light is ignored until it’s loud.",
    },
}


def get_phase_copy(mode: str, window: tuple[int, int]) -> dict:
    return PHASE_COPY.get((mode, window), DEFAULT_COPY[mode])


# ----------------------------
# MATH HELPERS
# ----------------------------
def interpolate_from_knots(knots: list[tuple[int, float]], x_min: int, x_max: int, step: int = 1):
    knots = sorted(knots, key=lambda t: t[0])
    xs, ys = [], []

    for x in range(x_min, x_max + 1, step):
        if x <= knots[0][0]:
            xs.append(x); ys.append(knots[0][1]); continue
        if x >= knots[-1][0]:
            xs.append(x); ys.append(knots[-1][1]); continue

        for i in range(len(knots) - 1):
            x0, y0 = knots[i]
            x1, y1 = knots[i + 1]
            if x0 <= x <= x1:
                t = 0 if x1 == x0 else (x - x0) / (x1 - x0)
                y = y0 + t * (y1 - y0)
                xs.append(x); ys.append(y)
                break

    return xs, ys


def segment_between(xs, ys, start_x: int, end_x: int):
    seg_x, seg_y = [], []
    for x, y in zip(xs, ys):
        if start_x <= x <= end_x:
            seg_x.append(x); seg_y.append(y)
    return seg_x, seg_y


# ----------------------------
# SESSION STATE (robust navigation)
# ----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "LRP"  # default

if "age_index" not in st.session_state:
    # default to 60–65 in whichever mode we start
    st.session_state.age_index = 1  # LRP_WINDOWS[1] is (60,65)


# ----------------------------
# TOP BAR: TOGGLE + TITLE
# ----------------------------
top_left, top_mid, top_right = st.columns([1.3, 6, 1.3], vertical_alignment="center")

with top_left:
    lrp_mode = st.toggle("LRP", value=(st.session_state.mode == "LRP"), key="lrp_toggle")

with top_mid:
    st.markdown(f"<h1 style='text-align:center; margin: 0;'>{TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; margin-top: 2px; opacity: 0.70;'>{SUBTITLE}</p>", unsafe_allow_html=True)

with top_right:
    # optional comparison control
    show_other = st.checkbox("Show other line", value=True, key="show_other_line")


# Handle mode switch cleanly and clamp indices
new_mode = "LRP" if lrp_mode else "SAL"
if new_mode != st.session_state.mode:
    st.session_state.mode = new_mode
    # pick a sensible default window when switching
    if new_mode == "LRP":
        st.session_state.age_index = LRP_WINDOWS.index((60, 65)) if (60, 65) in LRP_WINDOWS else 0
    else:
        st.session_state.age_index = SAL_WINDOWS.index((60, 65)) if (60, 65) in SAL_WINDOWS else 0


MODE = st.session_state.mode
WINDOWS = LRP_WINDOWS if MODE == "LRP" else SAL_WINDOWS

# clamp index in case WINDOWS changed
st.session_state.age_index = max(0, min(st.session_state.age_index, len(WINDOWS) - 1))
start_age, end_age = WINDOWS[st.session_state.age_index]


# ----------------------------
# NAV: LEFT/RIGHT ARROWS (keys fix)
# ----------------------------
nav_left, nav_mid, nav_right = st.columns([1, 3, 1], vertical_alignment="center")

with nav_left:
    if st.button("←", key="nav_left_btn", use_container_width=True):
        st.session_state.age_index = max(0, st.session_state.age_index - 1)

with nav_mid:
    label = f"{MODE} {start_age}–{end_age}"
    st.markdown(
        f"<div style='text-align:center; font-weight:800; font-size:18px; padding: 6px 0;'>{label}</div>",
        unsafe_allow_html=True,
    )

with nav_right:
    if st.button("→", key="nav_right_btn", use_container_width=True):
        st.session_state.age_index = min(len(WINDOWS) - 1, st.session_state.age_index + 1)


# ----------------------------
# LAYOUT: LEFT / CHART / RIGHT
# ----------------------------
left, center, right = st.columns([2.4, 5.4, 2.4], gap="large")

copy = get_phase_copy(MODE, (start_age, end_age))


# LEFT: bullets
with left:
    st.markdown(
        f"""
<div class="lrp-card">
  <div style="font-weight:900; font-size: 20px; margin-bottom: 10px;">{copy["left_title"]}</div>
  <ul style="margin:0; padding-left: 20px; line-height:1.7;">
    {''.join([f"<li>{b}</li>" for b in copy["bullets"]])}
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )


# RIGHT: gauge-style cards (circular border)
def gauge_card(title: str, icon: str, body: str):
    st.markdown(
        f"""
<div class="gauge-wrap">
  <div class="gauge">
    <div class="gauge-title">{title}</div>
    <div class="gauge-icon">{icon}</div>
    <div class="gauge-body">{body}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


with right:
    gauge_card("Diagnosis", "🩺", copy["diag"])
    gauge_card("Prescription", "📋", copy["rx"])
    gauge_card("Check Engine", "🟢", copy["ce"])


# ----------------------------
# BUILD SERIES
# ----------------------------
# SAL full series (0–77)
sal_x, sal_y = interpolate_from_knots(SAL_KNOTS, 0, 77, 1)
# LRP full series (55–92)
lrp_x, lrp_y = interpolate_from_knots(LRP_KNOTS, 55, 92, 1)

# Active segment belongs to current MODE
if MODE == "SAL":
    active_x, active_y = segment_between(sal_x, sal_y, start_age, end_age)
else:
    active_x, active_y = segment_between(lrp_x, lrp_y, start_age, end_age)


# ----------------------------
# PLOTLY FIGURE
# ----------------------------
fig = go.Figure()

# Colors
SAL_BASE = "rgba(180,80,80,0.35)"
SAL_ACTIVE = "rgba(180,80,80,1.0)"
LRP_BASE = "rgba(0,120,70,0.55)"
LRP_ACTIVE = "rgba(0,120,70,1.0)"

# Show primary mode line (base + active)
if MODE == "SAL":
    # SAL base
    fig.add_trace(go.Scatter(x=sal_x, y=sal_y, mode="lines", name="SAL", line=dict(color=SAL_BASE, width=5), hoverinfo="skip"))
    # SAL active highlight
    fig.add_trace(go.Scatter(x=active_x, y=active_y, mode="lines", name="SAL active", line=dict(color=SAL_ACTIVE, width=10), hoverinfo="skip"))

    # Optional: show LRP faintly for comparison
    if show_other:
        fig.add_trace(go.Scatter(x=lrp_x, y=lrp_y, mode="lines", name="LRP (compare)", line=dict(color=LRP_BASE, width=4), hoverinfo="skip"))

else:
    # LRP base
    fig.add_trace(go.Scatter(x=lrp_x, y=lrp_y, mode="lines", name="LRP", line=dict(color=LRP_BASE, width=5), hoverinfo="skip"))
    # LRP active highlight
    fig.add_trace(go.Scatter(x=active_x, y=active_y, mode="lines", name="LRP active", line=dict(color=LRP_ACTIVE, width=10), hoverinfo="skip"))

    # Optional: show SAL faintly for comparison
    if show_other:
        fig.add_trace(go.Scatter(x=sal_x, y=sal_y, mode="lines", name="SAL (compare)", line=dict(color=SAL_BASE, width=4), hoverinfo="skip"))

# Death marker for SAL at 77 (always show if SAL is visible in any form)
if (MODE == "SAL") or show_other:
    fig.add_trace(
        go.Scatter(
            x=[77],
            y=[sal_y[-1]],
            mode="markers+text",
            name="SAL death",
            marker=dict(size=9, color="rgba(180,80,80,0.85)"),
            text=["77"],
            textposition="bottom center",
            hoverinfo="skip",
        )
    )

# Layout
fig.update_layout(
    height=540,
    margin=dict(l=30, r=15, t=10, b=35),
    plot_bgcolor="rgba(245,240,232,1)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)

fig.update_xaxes(
    title_text="Age",
    range=[0, 92],
    showgrid=True,
    gridcolor="rgba(0,0,0,0.06)",
    zeroline=False,
)

fig.update_yaxes(
    range=[0, 100],
    showgrid=True,
    gridcolor="rgba(0,0,0,0.06)",
    zeroline=False,
)

# Zone labels
for y, label in [(80, "Fit"), (50, "Functional"), (20, "Frail")]:
    fig.add_annotation(
        x=2,
        y=y,
        text=label,
        showarrow=False,
        font=dict(size=14, color="rgba(0,0,0,0.45)"),
        xanchor="left",
        yanchor="middle",
    )

with center:
    st.plotly_chart(fig, use_container_width=True)

st.caption("Arrows advance the highlighted segment for the currently selected mode (SAL or LRP).")
