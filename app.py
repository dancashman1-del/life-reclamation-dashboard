# app.py — Life Reclamation Project (Streamlit) — FULL REPLACEMENT (Copy-Rich + SAL per-age bullets)
# requirements.txt should include:
# streamlit
# plotly

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go


# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Life Reclamation Project — RAMP Protocol", layout="wide")


# ----------------------------
# CSS
# ----------------------------
st.markdown(
    """
<style>
.block-container { padding-top: 1.0rem; }
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #fbf7f0 0%, #f7f2ea 60%, #f5efe6 100%);
}

/* Left panel card */
.left-card {
  background: rgba(255,255,255,0.72);
  border: 2px solid rgba(0,0,0,0.12);
  border-radius: 18px;
  padding: 18px 18px 14px 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

/* Right panel cards */
.right-card {
  background: rgba(255,255,255,0.72);
  border: 2px solid rgba(0,0,0,0.12);
  border-radius: 18px;
  padding: 16px 16px 14px 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
  margin-bottom: 14px;
}
.right-title {
  font-weight: 900;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  font-size: 14px;
  opacity: 0.85;
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 8px;
}
.right-icon {
  font-size: 18px;
  line-height: 18px;
}
.right-body {
  font-size: 14px;
  line-height: 1.45;
  opacity: 0.9;
}

/* SAL per-age bullets: smaller + 2 columns when lots of items */
.age-bullets {
  column-count: 2;
  column-gap: 28px;
  margin: 0;
  padding-left: 18px;
  line-height: 1.55;
  font-size: 13px;
}
@media (max-width: 1200px) {
  .age-bullets { column-count: 1; }
}

/* Plot rounding */
.js-plotly-plot, .plotly, .plot-container { border-radius: 18px !important; }
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------
# TITLES
# ----------------------------
TITLE = "Life Reclamation Project — RAMP Protocol"
SUBTITLE = "The intervention path — first 5 years, massive reversal"


# ----------------------------
# SERIES KNOTS
# ----------------------------
SAL_KNOTS = [
    (0, 78),
    (20, 77),
    (45, 66),
    (55, 50),
    (62, 38),
    (70, 20),
    (77, 5),
]

LRP_KNOTS = [
    (55, 52),
    (60, 78),
    (65, 78),  # hold high 5 years
    (75, 70),
    (85, 62),
    (90, 58),
    (91, 55),  # faster drop begins ~90–91
    (92, 44),  # still far above SAL@77
]


# ----------------------------
# WINDOWS
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


# ----------------------------
# COPY: HIGH-QUALITY DEFAULTS + SPECIFIC OVERRIDES
# ----------------------------
DEFAULT_COPY = {
    "LRP": {
        "left_title": "Reclamation (deliberate, compounding)",
        "bullets": [
            "Strength training is non-negotiable — protect muscle and power",
            "Zone 2 becomes your default engine; HIIT stays dosed",
            "Sleep is treated like a keystone habit (not a nice-to-have)",
            "Real food most of the time — cravings lose their grip",
        ],
        "diag": "Capacity is the vital sign. You’re raising the ceiling, not just managing symptoms.",
        "rx": "Strength + Zone 2 + small HIIT dose; protein and sleep as guardrails.",
        "ce": "You notice drift early — and correct while it’s still cheap.",
    },
    "SAL": {
        "left_title": "Default Path (drift)",
        "bullets": [
            "Fitness erodes slowly — until it suddenly feels like “old age”",
            "Pain avoidance replaces strength work",
            "Screens replace movement; movement becomes “optional”",
            "Health becomes reactive (appointments, meds, setbacks)",
        ],
        "diag": "Decline is invisible in the moment and obvious in hindsight.",
        "rx": "“Wait and see” becomes the plan — until you’re forced to act.",
        "ce": "The warning light is ignored until it’s loud.",
    },
}

# Window-specific upgrades (add more anytime; these cover the key LRP windows + SAL midlife)
COPY_BY_WINDOW = {
    ("LRP", (55, 60)): {
        "left_title": "Reclamation Begins (first 5 years)",
        "bullets": [
            "Strength becomes non-negotiable (legs, back, grip, carries)",
            "Zone 2 base rebuilt; hiking feels easier within months",
            "Sleep regularized — mornings feel powerful again",
            "Real food replaces “dieting”; cravings quiet down",
        ],
        "diag": "Baseline labs & BP improve fast once compliance is real.",
        "rx": "Strength + Zone 2 + HIIT; protect sleep; 95% real food.",
        "ce": "Biomarkers drift quietly — until they don’t.",
    },
    ("LRP", (60, 65)): {
        "left_title": "Peak Window (hold the line)",
        "bullets": [
            "Keep strength heavy and consistent — don’t “graduate” from it",
            "Zone 2 feels easier — that’s the engine getting efficient",
            "Trips/hikes become identity, not exercise",
            "Stress hygiene protects sleep and appetite",
        ],
        "diag": "Doctor is stunned — keep doing whatever you’re doing.",
        "rx": "Same basics; tighten consistency; keep progressive strength.",
        "ce": "Maintain the system before life tests it.",
    },
    ("LRP", (85, 90)): {
        "left_title": "Late Decades (still capable)",
        "bullets": [
            "Power work stays safe and small — but stays",
            "Strength protects joints and independence",
            "Cardio protects brain and stamina",
            "Purpose keeps you out of the chair",
        ],
        "diag": "You’re aging — but your slope is still yours.",
        "rx": "Strength 2x/week minimum; Zone 2 weekly; HIIT only if recovery is strong.",
        "ce": "One small lapse is fine; a pattern is not.",
    },
    ("LRP", (90, 92)): {
        "left_title": "The Steeper Drop (still above default)",
        "bullets": [
            "The line drops faster now — but from a much higher place",
            "You still move, still climb stairs, still travel",
            "You’re managing recovery, not surrendering capacity",
            "You finish functional — not fragile",
        ],
        "diag": "The goal was never immortality — it was preserved function.",
        "rx": "Protect strength + protein; keep walking; simplify, don’t stop.",
        "ce": "Keep it safe. Keep it consistent. Keep it yours.",
    },

    ("SAL", (40, 50)): {
        "left_title": "Default Path (midlife drift)",
        "bullets": [
            "Work and stress crowd out training",
            "Weight creeps up; sleep gets lighter",
            "More sitting; less power, less balance",
            "Health feels “fine” — but capacity is shrinking",
        ],
        "diag": "You still look normal — but the decline has already started.",
        "rx": "Occasional bursts of effort, no system, no progression.",
        "ce": "The light flickers… you call it ‘life’ and move on.",
    },
    ("SAL", (65, 70)): {
        "left_title": "Default Path (the narrowing)",
        "bullets": [
            "Stairs feel harder; you blame age",
            "Minor injuries linger; activity shrinks further",
            "More appointments; more caution",
            "Strength fades — then confidence follows",
        ],
        "diag": "The window for easy reversal is closing.",
        "rx": "Meds may help numbers; they don’t rebuild capacity.",
        "ce": "The warning becomes the new normal.",
    },
}


def get_copy(mode: str, window: tuple[int, int]) -> dict:
    base = DEFAULT_COPY[mode].copy()
    override = COPY_BY_WINDOW.get((mode, window))
    if override:
        base.update(override)
    return base


# ----------------------------
# SAL: AGE-BY-AGE “SAD LIFE” BULLETS
# ----------------------------
def sal_line_for_age(age: int) -> str:
    # Quick, age-appropriate “sad drift” lines (you can refine anytime)
    if age < 10:
        return "More screens, less outside play."
    if age < 20:
        return "Activity becomes optional; posture and sleep worsen."
    if age < 30:
        return "Fitness is episodic; consistency never forms."
    if age < 40:
        return "Sitting dominates; stress + convenience eating build."
    if age < 50:
        return "‘Fine’ on the surface; capacity quietly shrinking."
    if age < 55:
        return "Aches appear; you avoid loading and lifting."
    if age < 60:
        return "More caution, less challenge; strength drops fast."
    if age < 65:
        return "Stairs and hikes get negotiated, not enjoyed."
    if age < 70:
        return "Appointments and meds increase; confidence decreases."
    if age < 75:
        return "Falls risk rises; travel narrows; independence slips."
    return "Frailty accelerates; help becomes necessary."


def build_sal_age_bullets(window: tuple[int, int]) -> list[str]:
    start, end = window
    return [f"Age {a}: {sal_line_for_age(a)}" for a in range(start, end + 1)]


# ----------------------------
# SERIES HELPERS
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
# SESSION STATE
# ----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "LRP"
if "age_index" not in st.session_state:
    st.session_state.age_index = 1  # default to 60–65 for LRP


# ----------------------------
# TOP BAR
# ----------------------------
top_left, top_mid, top_right = st.columns([1.3, 6, 1.3], vertical_alignment="center")

with top_left:
    lrp_mode = st.toggle("LRP", value=(st.session_state.mode == "LRP"), key="lrp_toggle")

with top_mid:
    st.markdown(f"<h1 style='text-align:center; margin:0;'>{TITLE}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; margin-top:2px; opacity:0.70;'>{SUBTITLE}</p>", unsafe_allow_html=True)

with top_right:
    show_other = st.checkbox("Show other line", value=True, key="show_other_line")


# Mode switch handling
new_mode = "LRP" if lrp_mode else "SAL"
if new_mode != st.session_state.mode:
    st.session_state.mode = new_mode
    if new_mode == "LRP":
        st.session_state.age_index = LRP_WINDOWS.index((60, 65)) if (60, 65) in LRP_WINDOWS else 0
    else:
        st.session_state.age_index = SAL_WINDOWS.index((40, 50)) if (40, 50) in SAL_WINDOWS else 0


MODE = st.session_state.mode
WINDOWS = LRP_WINDOWS if MODE == "LRP" else SAL_WINDOWS
st.session_state.age_index = max(0, min(st.session_state.age_index, len(WINDOWS) - 1))
start_age, end_age = WINDOWS[st.session_state.age_index]


# ----------------------------
# NAV
# ----------------------------
nav_left, nav_mid, nav_right = st.columns([1, 3, 1], vertical_alignment="center")

with nav_left:
    if st.button("←", key="nav_left_btn", use_container_width=True):
        st.session_state.age_index = max(0, st.session_state.age_index - 1)

with nav_mid:
    st.markdown(
        f"<div style='text-align:center; font-weight:900; font-size:18px; padding:6px 0;'>{MODE} {start_age}–{end_age}</div>",
        unsafe_allow_html=True,
    )

with nav_right:
    if st.button("→", key="nav_right_btn", use_container_width=True):
        st.session_state.age_index = min(len(WINDOWS) - 1, st.session_state.age_index + 1)


# ----------------------------
# LAYOUT
# ----------------------------
left, center, right = st.columns([2.6, 5.2, 2.6], gap="large")

copy = get_copy(MODE, (start_age, end_age))


# LEFT PANEL
with left:
    if MODE == "SAL":
        # Age-by-age bullets for SAL
        age_bullets = build_sal_age_bullets((start_age, end_age))
        st.markdown(
            f"""
<div class="left-card">
  <div style="font-weight:900; font-size:20px; margin-bottom:10px;">{copy["left_title"]}</div>
  <ul class="age-bullets">
    {''.join([f"<li>{b}</li>" for b in age_bullets])}
  </ul>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        # Curated bullets for LRP
        st.markdown(
            f"""
<div class="left-card">
  <div style="font-weight:900; font-size:20px; margin-bottom:10px;">{copy["left_title"]}</div>
  <ul style="margin:0; padding-left:20px; line-height:1.7;">
    {''.join([f"<li>{b}</li>" for b in copy["bullets"]])}
  </ul>
</div>
""",
            unsafe_allow_html=True,
        )


# RIGHT PANEL (rounded rectangles with room for “quotes”)
def right_card(title: str, icon: str, body: str):
    st.markdown(
        f"""
<div class="right-card">
  <div class="right-title"><span class="right-icon">{icon}</span> {title}</div>
  <div class="right-body">{body}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    right_card("Diagnosis", "🩺", copy["diag"])
    right_card("Prescription", "📋", copy["rx"])
    right_card("Check Engine Light", "🟢", copy["ce"])


# ----------------------------
# BUILD SERIES
# ----------------------------
sal_x, sal_y = interpolate_from_knots(SAL_KNOTS, 0, 77, 1)
lrp_x, lrp_y = interpolate_from_knots(LRP_KNOTS, 55, 92, 1)

if MODE == "SAL":
    active_x, active_y = segment_between(sal_x, sal_y, start_age, end_age)
else:
    active_x, active_y = segment_between(lrp_x, lrp_y, start_age, end_age)


# ----------------------------
# PLOT
# ----------------------------
fig = go.Figure()

SAL_BASE = "rgba(180,80,80,0.33)"
SAL_ACTIVE = "rgba(160,60,60,1.0)"
LRP_BASE = "rgba(0,120,70,0.55)"
LRP_ACTIVE = "rgba(0,120,70,1.0)"

if MODE == "SAL":
    fig.add_trace(go.Scatter(x=sal_x, y=sal_y, mode="lines", name="SAL", line=dict(color=SAL_BASE, width=5), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=active_x, y=active_y, mode="lines", name="SAL active", line=dict(color=SAL_ACTIVE, width=10), hoverinfo="skip"))
    if show_other:
        fig.add_trace(go.Scatter(x=lrp_x, y=lrp_y, mode="lines", name="LRP (compare)", line=dict(color=LRP_BASE, width=4), hoverinfo="skip"))
else:
    fig.add_trace(go.Scatter(x=lrp_x, y=lrp_y, mode="lines", name="LRP", line=dict(color=LRP_BASE, width=5), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=active_x, y=active_y, mode="lines", name="LRP active", line=dict(color=LRP_ACTIVE, width=10), hoverinfo="skip"))
    if show_other:
        fig.add_trace(go.Scatter(x=sal_x, y=sal_y, mode="lines", name="SAL (compare)", line=dict(color=SAL_BASE, width=4), hoverinfo="skip"))

# SAL death marker (if SAL visible)
if MODE == "SAL" or show_other:
    fig.add_trace(
        go.Scatter(
            x=[77],
            y=[sal_y[-1]],
            mode="markers+text",
            name="SAL death",
            marker=dict(size=9, color="rgba(160,60,60,0.85)"),
            text=["77"],
            textposition="bottom center",
            hoverinfo="skip",
        )
    )

fig.update_layout(
    height=560,
    margin=dict(l=30, r=15, t=10, b=40),
    plot_bgcolor="rgba(245,240,232,1)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)

fig.update_xaxes(title_text="Age", range=[0, 92], showgrid=True, gridcolor="rgba(0,0,0,0.06)", zeroline=False)
fig.update_yaxes(range=[0, 100], showgrid=True, gridcolor="rgba(0,0,0,0.06)", zeroline=False)

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

st.caption("Bullets and cards now change by window. In SAL mode, the left panel shows age-by-age drift bullets for the selected range.")
