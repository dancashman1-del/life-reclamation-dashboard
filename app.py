# app.py — Life Reclamation Project (Streamlit) — single-file drop-in replacement
# - LRP toggle at upper-left
# - Green LRP line "advances" by age window
# - Removes any moving/advancing red SAL line (SAL is static + faint only)
# - LRP: peak by 60, stays high 60–65, then gradual decline; faster only ~90–92
# Run: streamlit run app.py

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go


# ----------------------------
# CONFIG / STYLE
# ----------------------------
st.set_page_config(page_title="Life Reclamation Project — RAMP Protocol", layout="wide")

TITLE = "Life Reclamation Project — RAMP Protocol"
SUBTITLE = "The intervention path — first 5 years, massive reversal"

# Chart scale (0–100 works well for Fit/Functional/Frail)
Y_MIN, Y_MAX = 0, 100


# ----------------------------
# DATA HELPERS
# ----------------------------
def interpolate_from_knots(knots: list[tuple[int, float]], x_min: int, x_max: int, step: int = 1):
    """
    Linear interpolation between knot points (x,y). Returns (xs, ys) at integer steps.
    """
    xs, ys = [], []
    knots = sorted(knots, key=lambda t: t[0])

    for x in range(x_min, x_max + 1, step):
        # Find segment containing x
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
            seg_x.append(x)
            seg_y.append(y)
    return seg_x, seg_y


# ----------------------------
# SERIES DEFINITIONS
# ----------------------------
# SAL (default path): static + faint. Ends at 77 (death marker).
# Adjust these knots to match your exact visual. Keeping it simple & smooth.
SAL_KNOTS = [
    (0, 78),
    (20, 77),
    (45, 66),
    (55, 50),
    (62, 38),
    (70, 20),
    (77, 5),   # "death" around 77
]

# LRP (intervention path): peak by 60, flat 60–65, gradual decline, faster only ~90–92.
LRP_KNOTS = [
    (55, 52),
    (60, 78),  # peak by 60
    (65, 78),  # stays high for 5 years (60–65)
    (75, 70),
    (85, 62),
    (90, 58),
    (91, 55),  # begin faster drop around 90–91
    (92, 44),  # still far above SAL at 77
]


# Age windows for advancing highlight.
# These are the "chapters" the arrow buttons step through.
AGE_WINDOWS = [
    (55, 60),
    (60, 65),
    (65, 70),
    (70, 75),
    (75, 80),
    (80, 85),
    (85, 90),
    (90, 92),
]


# Simple example bullet copy by rhetorical “phase”
# (Replace these with your real bullets / per-window copy.)
PHASE_COPY = {
    (55, 60): {
        "left_title": "Reclamation Begins (first 5 years)",
        "bullets": [
            "Strength training becomes non-negotiable",
            "Zone 2 base rebuilt; hiking feels easier",
            "Sleep regularized; mornings feel powerful",
            "Real food replaces “dieting”",
        ],
        "diag": "Baseline labs & BP improve fast once compliance is real.",
        "rx": "Strength + Zone 2 + HIIT; protect sleep; 95% real food.",
        "ce": "Biomarkers drift quietly — until they don’t.",
    },
    (60, 65): {
        "left_title": "Peak Window (hold the line)",
        "bullets": [
            "Keep strength heavy and consistent",
            "Zone 2 feels “easy” — that’s the point",
            "Trips and hikes become identity, not “exercise”",
            "Stress hygiene keeps cravings quiet",
        ],
        "diag": "Doctor is stunned — keep doing whatever you’re doing.",
        "rx": "Same basics, tighter sleep, a little more strength intent.",
        "ce": "Maintain the system before life tests it.",
    },
    (65, 70): {
        "left_title": "Strong & Capable (momentum phase)",
        "bullets": [
            "You’re still in the driver’s seat",
            "Muscle is your retirement account",
            "Cardio protects the decades ahead",
            "Purpose keeps you out of the chair",
        ],
        "diag": "Aging is happening — but you’re winning the slope.",
        "rx": "Progressive strength; Zone 2 weekly minimum; HIIT dosed.",
        "ce": "Don’t trade movement for screens.",
    },
    "default": {
        "left_title": "Sustained Advantage (stay deliberate)",
        "bullets": [
            "Protect training like a meeting",
            "Keep protein and steps boringly consistent",
            "Use travel as “active living” fuel",
            "Course-correct early, not later",
        ],
        "diag": "Maintenance works when it’s real maintenance.",
        "rx": "Strength 2x/week minimum; Zone 2 base; HIIT sparingly.",
        "ce": "Small lapses compound — so do small wins.",
    },
}


def get_phase_copy(window):
    return PHASE_COPY.get(window, PHASE_COPY["default"])


# ----------------------------
# STATE (fixes “stuck age” issues)
# ----------------------------
if "age_index" not in st.session_state:
    # Default to 60–65 since that's the window you referenced in the screenshot
    st.session_state.age_index = AGE_WINDOWS.index((60, 65)) if (60, 65) in AGE_WINDOWS else 0


# ----------------------------
# TOP BAR: TOGGLE + TITLE
# ----------------------------
top_left, top_mid, top_right = st.columns([1.2, 6, 1.2], vertical_alignment="center")

with top_left:
    lrp_mode = st.toggle("LRP", value=True)

with top_mid:
    st.markdown(f"<h1 style='text-align:center; margin-bottom:0;'>{TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; margin-top:0; opacity:0.7;'>{SUBTITLE}</p>", unsafe_allow_html=True)

with top_right:
    st.write("")  # spacer


# ----------------------------
# NAV + WINDOW DISPLAY
# ----------------------------
nav_left, nav_mid, nav_right = st.columns([1, 3, 1], vertical_alignment="center")

with nav_left:
    if st.button("←", use_container_width=True):
        st.session_state.age_index = max(0, st.session_state.age_index - 1)

with nav_mid:
    start_age, end_age = AGE_WINDOWS[st.session_state.age_index]
    st.markdown(
        f"<div style='text-align:center; font-weight:600; font-size:18px;'>"
        f"{start_age}–{end_age}"
        f"</div>",
        unsafe_allow_html=True,
    )

with nav_right:
    if st.button("→", use_container_width=True):
        st.session_state.age_index = min(len(AGE_WINDOWS) - 1, st.session_state.age_index + 1)


# ----------------------------
# LAYOUT: LEFT / CHART / RIGHT
# ----------------------------
left, center, right = st.columns([2.3, 5.2, 2.3], gap="large")

phase = get_phase_copy((start_age, end_age))

with left:
    st.markdown(
        f"""
        <div style="background: rgba(255,255,255,0.75); border-radius: 16px; padding: 18px; box-shadow: 0 2px 14px rgba(0,0,0,0.05);">
          <div style="font-weight: 800; font-size: 20px; margin-bottom: 10px;">{phase["left_title"]}</div>
          <ul style="margin:0; padding-left: 22px; line-height: 1.7;">
            {''.join([f"<li>{b}</li>" for b in phase["bullets"]])}
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    def card(title, body):
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.75); border-radius: 16px; padding: 16px; margin-bottom: 14px;
                        box-shadow: 0 2px 14px rgba(0,0,0,0.05);">
              <div style="font-weight: 800; margin-bottom: 8px;">{title}</div>
              <div style="opacity: 0.85; line-height: 1.5;">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    card("Diagnosis", phase["diag"])
    card("Prescription", phase["rx"])
    card("Check Engine Light", phase["ce"])


# ----------------------------
# BUILD SERIES
# ----------------------------
# SAL series (static, ends at 77)
sal_x, sal_y = interpolate_from_knots(SAL_KNOTS, 0, 77, 1)

# LRP series (0–92). Before 55, we can either keep it flat-ish or hide it.
# Here: show from 55 onward only to avoid implying earlier life trajectory.
lrp_x, lrp_y = interpolate_from_knots(LRP_KNOTS, 55, 92, 1)

# Active segment (LRP only) for current window
active_lrp_x, active_lrp_y = segment_between(lrp_x, lrp_y, start_age, end_age)


# ----------------------------
# PLOTLY FIGURE
# ----------------------------
fig = go.Figure()

# Optional: show SAL faintly even when LRP is on (keeps the comparison visible).
# If you want SAL hidden during LRP mode, set show_sal_in_lrp = False.
show_sal_in_lrp = True

if (not lrp_mode) or show_sal_in_lrp:
    fig.add_trace(
        go.Scatter(
            x=sal_x,
            y=sal_y,
            mode="lines",
            name="SAL (static)",
            line=dict(color="rgba(180,80,80,0.35)", width=4),
            hoverinfo="skip",
        )
    )
    # SAL death marker at 77
    fig.add_trace(
        go.Scatter(
            x=[77],
            y=[sal_y[-1]],
            mode="markers+text",
            name="SAL death",
            marker=dict(size=8, color="rgba(180,80,80,0.75)"),
            text=["77"],
            textposition="bottom center",
            hoverinfo="skip",
        )
    )

if lrp_mode:
    # Full LRP line (static base)
    fig.add_trace(
        go.Scatter(
            x=lrp_x,
            y=lrp_y,
            mode="lines",
            name="LRP (static)",
            line=dict(color="rgba(0,120,70,0.55)", width=5),
            hoverinfo="skip",
        )
    )

    # LRP advancing segment (thicker, brighter) — this is the ONLY advancing line.
    fig.add_trace(
        go.Scatter(
            x=active_lrp_x,
            y=active_lrp_y,
            mode="lines",
            name="LRP (active window)",
            line=dict(color="rgba(0,120,70,1.0)", width=9),
            hoverinfo="skip",
        )
    )

# Axes + background
fig.update_layout(
    height=520,
    margin=dict(l=40, r=20, t=10, b=40),
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
    range=[Y_MIN, Y_MAX],
    showgrid=True,
    gridcolor="rgba(0,0,0,0.06)",
    zeroline=False,
)

# Labels on Y axis for Fit / Functional / Frail (at approximate bands)
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

# Footer note (optional)
st.caption("Tip: The green highlight advances by window; SAL is static and never “moves.”")
