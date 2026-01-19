# app.py — Life Reclamation Dashboard (Single-file Streamlit app)
# Drop into GitHub and deploy on Streamlit Cloud.
#
# Views:
# 1) Timeline view: age-by-age SAL vs LRP trajectory + narrative (Diagnosis / Prescription)
# 2) Threshold view (formerly “Gandalf”): Health / Wealth / SILO thresholds, in both modes
#
# Notes:
# - “Hitting the Switchback” marker is fixed at age 55.
# - Health: red → green
# - Wealth: amber → teal
# - SILO: below-ground filled gray / above-ground outline
#
# Source inspiration for SAL age-bucket narrative is based on your “Typical American Life” draft notes. :contentReference[oaicite:0]{index=0}

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------
# Page config + light styling
# -----------------------------
st.set_page_config(
    page_title="Life Reclamation Dashboard",
    page_icon="🧭",
    layout="wide",
)

st.markdown(
    """
<style>
/* tighten default spacing a bit */
.block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
h1, h2, h3 { letter-spacing: -0.02em; }

/* “dashboard” cards */
.lrp-card {
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  padding: 14px 14px 12px 14px;
}
.small-muted { color: rgba(255,255,255,0.65); font-size: 0.92rem; }
.tiny-muted { color: rgba(255,255,255,0.55); font-size: 0.82rem; }

/* Threshold “pill” label */
.pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.04);
}

/* SILO ground line */
.groundline {
  height: 2px;
  background: rgba(255,255,255,0.22);
  border-radius: 99px;
}

/* bar container */
.bar-wrap {
  width: 100%;
  max-width: 520px;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.03);
  padding: 12px;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Constants
# -----------------------------
SWITCHBACK_AGE = 55

# For this dashboard we keep “lifespan” adjustable but bounded.
MIN_AGE = 0
MAX_AGE = 100


# -----------------------------
# Narrative (SAL / LRP) buckets
# -----------------------------
@dataclass(frozen=True)
class BucketNarrative:
    title: str
    subtitle: str
    diagnosis: List[str]
    prescription: List[str]


def _bucket_key(age: int) -> str:
    # 0-5, 5-10, ... 90-95, 95-100
    lo = (age // 5) * 5
    hi = lo + 5
    if age >= 100:
        lo, hi = 100, 105
    return f"{lo:02d}-{hi:02d}"


def build_narratives() -> Tuple[Dict[str, BucketNarrative], Dict[str, BucketNarrative]]:
    """
    SAL text is loosely derived from your draft “Typical American Life” notes.
    LRP text is an uplifted alternative (same age buckets).
    Keep these short: the UI is meant to be skimmable.
    """
    sal: Dict[str, BucketNarrative] = {}
    lrp: Dict[str, BucketNarrative] = {}

    # --- SAL (Typical American Life) ---
    sal["00-05"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 0–5",
        diagnosis=[
            "Healthy (but the default path is being set).",
        ],
        prescription=[
            "Breast milk + mostly whole foods (some sweets).",
            "Lots of physical play; minimal screen time; strong bonding; good sleep.",
        ],
    )
    sal["05-10"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 5–10",
        diagnosis=[
            "Diet quality starts sliding; dopamine distractions begin.",
        ],
        prescription=[
            "Sugary cereals, nuggets, candy, chips, juices become common.",
            "Some physical play, but games/shows start taking over; bonding decreases.",
        ],
    )
    sal["10-15"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 10–15",
        diagnosis=[
            "“Healthy?” (exercise narrows to organized sports).",
        ],
        prescription=[
            "Fast food and snacking increase.",
            "First phone + social scrolling begins; gaming rises; sleep quality slips.",
        ],
    )
    # From here we keep the spirit but compress repetition
    sal["15-20"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 15–20",
        diagnosis=["Sedentary drift + processed food normalization."],
        prescription=[
            "More refined grains/sugars/bad oils.",
            "More scrolling/streaming; activity mainly incidental.",
        ],
    )
    sal["20-25"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 20–25",
        diagnosis=["Weight gain and fatigue become background noise."],
        prescription=[
            "Primarily processed / fast food.",
            "Gaming/scrolling + studying + alcohol; movement drops.",
        ],
    )
    sal["25-30"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 25–30",
        diagnosis=["Sedentary career patterns cement."],
        prescription=[
            "Desk job; low daily movement; sleep debt accumulates.",
            "“Maybe lose some weight” attempts begin, but environment stays the same.",
        ],
    )
    sal["30-35"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 30–35",
        diagnosis=["Stress rises; energy drops; aches appear."],
        prescription=[
            "More screen-based decompression (scrolling/streaming).",
            "Alcohol creeps up; processed foods persist.",
        ],
    )
    sal["35-40"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 35–40",
        diagnosis=["Mood and sleep issues show up."],
        prescription=[
            "Poor sleep becomes chronic; stress coping turns passive.",
            "Medications may start (e.g., SSRI) rather than root-cause change.",
        ],
    )
    sal["40-45"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 40–45",
        diagnosis=["Blood pressure / metabolic warning signs."],
        prescription=[
            "“Cut salt, maybe lose weight” + meds; lifestyle shifts are modest.",
            "Sedentary work continues; sleep remains poor.",
        ],
    )
    sal["45-50"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 45–50",
        diagnosis=["Elevated HbA1c, chronic stress."],
        prescription=[
            "More meds; some diet improvements, but behavior is inconsistent.",
            "Movement still not structured.",
        ],
    )
    sal["50-55"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 50–55",
        diagnosis=["Pain episodes turn chronic; resilience is low."],
        prescription=[
            "Specialists + prescriptions become the default response.",
            "Coping is still screen-heavy; recovery is weak.",
        ],
    )
    sal["55-60"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 55–60",
        diagnosis=["Big diagnosis era (autoimmune, heart, cancer risk rises)."],
        prescription=[
            "Procedures/meds; “maybe exercise now” arrives late.",
            "Some diet cleanup, but baseline fitness is limited.",
        ],
    )
    sal["60-65"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 60–65",
        diagnosis=["Major event risk: heart disease / cancer."],
        prescription=[
            "Treatment-focused; activity becomes short walks.",
            "Sleep often still poor; frailty slope begins.",
        ],
    )
    sal["65-70"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 65–70",
        diagnosis=["Cognitive decline signals may appear."],
        prescription=[
            "Medications and supervision increase.",
            "Life narrows; strength and balance are fragile.",
        ],
    )
    sal["70-75"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 70–75",
        diagnosis=["Falls / rigidity / compounding disability."],
        prescription=[
            "Assisted living may begin; polypharmacy grows.",
            "Independence shrinks quickly.",
        ],
    )
    sal["75-80"] = BucketNarrative(
        title="A Typical American Life",
        subtitle="Health • ages 75–80",
        diagnosis=["End-of-life window for the default path."],
        prescription=[
            "Comfort care mindset; limited mobility.",
            "The “engine light” has been on for decades.",
        ],
    )

    # --- LRP (Life Reclamation Path) ---
    # The structure: early-life is already decent, but the “switchback” is the conscious turn at 55.
    # LRP peaks at ~60 (after ~5 years of doing the right things), then gentle decline, still functional at 92.
    for lo in range(0, 105, 5):
        k = f"{lo:02d}-{(lo+5):02d}"
        if k == "00-05":
            lrp[k] = BucketNarrative(
                title="Life Reclamation Path",
                subtitle="Health • ages 0–5",
                diagnosis=["Strong start."],
                prescription=[
                    "Same basics: whole foods, play, sleep, bonding.",
                    "Build a lifelong identity: “I move every day.”",
                ],
            )
        elif lo < SWITCHBACK_AGE:
            # pre-switchback: better-than-average habits accumulate slowly
            lrp[k] = BucketNarrative(
                title="Life Reclamation Path",
                subtitle=f"Health • ages {lo}–{lo+5}",
                diagnosis=["Mostly functional, with drift kept in check."],
                prescription=[
                    "Maintain strength + aerobic base (Zone 2) as non-negotiables.",
                    "Reduce screen-based coping; protect sleep; walk daily.",
                ],
            )
        elif lo == SWITCHBACK_AGE:
            lrp[k] = BucketNarrative(
                title="Life Reclamation Path",
                subtitle=f"Health • ages {lo}–{lo+5}",
                diagnosis=["Hitting the Switchback — choose your trajectory."],
                prescription=[
                    "Commit to 5-year rebuild: strength 2–3x/week + Zone 2 3x/week.",
                    "Design environment: protein-first meals, steps, sunlight, sleep.",
                    "Tie in Wealth + Purpose to reduce stress and sustain change.",
                ],
            )
        elif lo < 65:
            lrp[k] = BucketNarrative(
                title="Life Reclamation Path",
                subtitle=f"Health • ages {lo}–{lo+5}",
                diagnosis=["Rebuild phase: capacity rises quickly."],
                prescription=[
                    "Progressive strength; Zone 2 volume; occasional HIIT; mobility.",
                    "Track “engine indicators”: waist, BP, VO₂, strength benchmarks.",
                ],
            )
        elif lo < 80:
            lrp[k] = BucketNarrative(
                title="Life Reclamation Path",
                subtitle=f"Health • ages {lo}–{lo+5}",
                diagnosis=["Maintenance phase: protect the peak."],
                prescription=[
                    "Keep intensity; prioritize balance + power; prevent falls.",
                    "Purpose + community: keep showing up.",
                ],
            )
        else:
            lrp[k] = BucketNarrative(
                title="Life Reclamation Path",
                subtitle=f"Health • ages {lo}–{lo+5}",
                diagnosis=["Longevity phase: functional independence is the goal."],
                prescription=[
                    "Strength minimums, daily walking, mobility, social connection.",
                    "Simplify and protect the essentials.",
                ],
            )

    return sal, lrp


SAL_NARR, LRP_NARR = build_narratives()


# -----------------------------
# Trajectory math
# -----------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def smoothstep(t: float) -> float:
    # cubic smoothstep 0..1
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def health_score(age: int, mode: str) -> float:
    """
    0..100 (higher is better).
    SAL: gradual decline then steeper; death around 77.
    LRP: baseline okay, switchback at 55, peak ~60, then slow decline; still functional at 92.
    """
    a = float(age)
    if mode == "SAL":
        # good early, then drift, then compounding
        # piecewise curve with accelerated decline after 55
        base = 92 - 0.35 * a  # slow erosion
        accel = 0.0
        if a > 40:
            accel += (a - 40) * 0.55
        if a > 55:
            accel += (a - 55) * 1.10
        if a > 70:
            accel += (a - 70) * 1.60
        s = base - accel
        # “death” around 77: force near-zero thereafter
        if a >= 77:
            s = 2.0
        return clamp(s, 0, 100)

    # LRP
    # before switchback: mild drift (but not catastrophic)
    if a < SWITCHBACK_AGE:
        s = 90 - 0.20 * a
        return clamp(s, 0, 100)

    # after switchback: improve over ~5 years, peak at 60, then slow decline
    # improvement from age 55 to 60
    t = (a - SWITCHBACK_AGE) / 5.0  # 0..1 at age 60
    improve = 18 * smoothstep(t)  # up to +18
    # slow decline after 60
    decline = 0.0
    if a > 60:
        decline += (a - 60) * 0.45
    if a > 75:
        decline += (a - 75) * 0.55
    if a > 85:
        decline += (a - 85) * 0.70

    # baseline at 55
    s0 = 90 - 0.20 * SWITCHBACK_AGE
    s = s0 + improve - decline

    # keep functional at 92 (roughly 45–60)
    if a >= 92:
        s = max(s, 48.0)
    return clamp(s, 0, 100)


def wealth_score(age: int, mode: str) -> float:
    """
    0..100 (higher is better).
    SAL: modest climb, stress dips, late-life drawdown risk.
    LRP: similar climb but with better intentionality, lower stress drag, more “memory dividends.”
    """
    a = float(age)

    # base accumulation curve (slow early, faster mid-career, taper)
    # logistic-ish
    accum = 100 / (1 + math.exp(-(a - 45) / 10))
    accum = (accum - 5) * 1.05  # shift/scale

    if mode == "SAL":
        # stress / obligations / reactive decisions
        drag = 0.0
        if 25 <= a <= 55:
            drag += 10 * smoothstep((a - 25) / 30)
        if a > 55:
            drag += 12 * smoothstep((a - 55) / 15)  # healthcare + late planning
        if a > 70:
            drag += 10 * smoothstep((a - 70) / 10)  # drawdown anxiety / costs
        s = accum - drag
        return clamp(s, 0, 100)

    # LRP
    # better systems, less drag, intentional spending windows
    drag = 0.0
    if 25 <= a <= 55:
        drag += 6 * smoothstep((a - 25) / 30)
    if a > 55:
        drag += 5 * smoothstep((a - 55) / 15)
    # slight uplift for “die-with-zero” style alignment (not hoarding)
    uplift = 6 * smoothstep((a - 35) / 25)
    s = accum - drag + uplift
    return clamp(s, 0, 100)


def silo_score(age: int, mode: str) -> float:
    """
    -100..+100 (below ground = autopilot / disconnection, above ground = presence / meaning).
    SAL: trends downward; LRP: switchback flips upward and stabilizes.
    """
    a = float(age)

    if mode == "SAL":
        # early is neutral-to-positive, then screens/stress pull below ground
        s = 25 - 1.2 * a
        if a > 25:
            s -= 10 * smoothstep((a - 25) / 20)
        if a > 45:
            s -= 18 * smoothstep((a - 45) / 15)
        if a > 65:
            s -= 10 * smoothstep((a - 65) / 12)
        return clamp(s, -100, 100)

    # LRP
    if a < SWITCHBACK_AGE:
        s = 20 - 0.45 * a  # small drift, not catastrophic
        return clamp(s, -100, 100)

    # post switchback: move above ground and stay
    t = (a - SWITCHBACK_AGE) / 4.0  # faster shift
    lift = 85 * smoothstep(t)  # up to +85
    # a gentle decline very late
    late = 0.0
    if a > 80:
        late = (a - 80) * 0.35
    s0 = 20 - 0.45 * SWITCHBACK_AGE
    s = s0 + lift - late
    return clamp(s, -100, 100)


def build_df(mode: str, max_age: int) -> pd.DataFrame:
    ages = list(range(MIN_AGE, max_age + 1))
    rows = []
    for age in ages:
        rows.append(
            {
                "age": age,
                "health": health_score(age, mode),
                "wealth": wealth_score(age, mode),
                "silo": silo_score(age, mode),
            }
        )
    return pd.DataFrame(rows)


# -----------------------------
# Plot helpers
# -----------------------------
def health_band_label(h: float) -> str:
    if h >= 70:
        return "Fit"
    if h >= 45:
        return "Functional"
    return "Frail"


def wealth_band_label(w: float) -> str:
    if w >= 70:
        return "Rich"
    if w >= 40:
        return "Enough"
    return "Poor"


def plot_timeline(df: pd.DataFrame, title: str, y_label: str, y_min: float, y_max: float,
                  switchback_age: int = SWITCHBACK_AGE, switchback_label: str = "Hitting the Switchback") -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["age"],
            y=df[title],
            mode="lines",
            line=dict(width=5),
            hovertemplate="Age %{x}<br>" + title.capitalize() + ": %{y:.1f}<extra></extra>",
            name=title.capitalize(),
        )
    )

    # Switchback marker
    fig.add_vline(
        x=switchback_age,
        line_width=2,
        line_dash="dash",
        opacity=0.9,
    )
    fig.add_annotation(
        x=switchback_age,
        y=y_max,
        xanchor="left",
        yanchor="top",
        text=f"<b>{switchback_label}</b><br><span style='font-size:12px;opacity:0.75'>Age {switchback_age}</span>",
        showarrow=False,
        bgcolor="rgba(0,0,0,0.35)",
        bordercolor="rgba(255,255,255,0.18)",
        borderwidth=1,
        borderpad=8,
    )

    fig.update_layout(
        height=330,
        margin=dict(l=20, r=16, t=20, b=20),
        xaxis=dict(title="Age", range=[MIN_AGE, int(df["age"].max())]),
        yaxis=dict(title=y_label, range=[y_min, y_max]),
        showlegend=False,
    )
    return fig


def plot_health(df: pd.DataFrame) -> go.Figure:
    # Add Fit/Functional/Frail bands
    fig = plot_timeline(df, "health", "Health (Fit → Frail)", 0, 100)
    fig.add_hrect(y0=70, y1=100, opacity=0.10, line_width=0)
    fig.add_hrect(y0=45, y1=70, opacity=0.07, line_width=0)
    fig.add_hrect(y0=0, y1=45, opacity=0.10, line_width=0)
    fig.add_annotation(x=2, y=95, text="<b>Fit</b>", showarrow=False, opacity=0.7)
    fig.add_annotation(x=2, y=58, text="<b>Functional</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=2, y=18, text="<b>Frail</b>", showarrow=False, opacity=0.7)
    return fig


def plot_wealth(df: pd.DataFrame) -> go.Figure:
    fig = plot_timeline(df, "wealth", "Wealth (Poor → Rich)", 0, 100)
    fig.add_hrect(y0=70, y1=100, opacity=0.10, line_width=0)
    fig.add_hrect(y0=40, y1=70, opacity=0.07, line_width=0)
    fig.add_hrect(y0=0, y1=40, opacity=0.10, line_width=0)
    fig.add_annotation(x=2, y=95, text="<b>Rich</b>", showarrow=False, opacity=0.7)
    fig.add_annotation(x=2, y=55, text="<b>Enough</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=2, y=16, text="<b>Poor</b>", showarrow=False, opacity=0.7)
    return fig


def plot_silo(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["age"],
            y=df["silo"],
            mode="lines",
            line=dict(width=5),
            hovertemplate="Age %{x}<br>SILO: %{y:.0f}<extra></extra>",
            name="SILO",
        )
    )

    # Ground line at 0
    fig.add_hline(y=0, line_width=2, line_dash="solid", opacity=0.65)

    # Switchback marker
    fig.add_vline(x=SWITCHBACK_AGE, line_width=2, line_dash="dash", opacity=0.9)
    fig.add_annotation(
        x=SWITCHBACK_AGE,
        y=100,
        xanchor="left",
        yanchor="top",
        text=f"<b>Hitting the Switchback</b><br><span style='font-size:12px;opacity:0.75'>Age {SWITCHBACK_AGE}</span>",
        showarrow=False,
        bgcolor="rgba(0,0,0,0.35)",
        bordercolor="rgba(255,255,255,0.18)",
        borderwidth=1,
        borderpad=8,
    )

    # Light shading below ground
    fig.add_hrect(y0=-100, y1=0, opacity=0.08, line_width=0)

    fig.update_layout(
        height=330,
        margin=dict(l=20, r=16, t=20, b=20),
        xaxis=dict(title="Age", range=[MIN_AGE, int(df["age"].max())]),
        yaxis=dict(title="SILO (Below-ground → Above-ground)", range=[-100, 100]),
        showlegend=False,
    )
    fig.add_annotation(x=2, y=75, text="<b>Above ground</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=2, y=-75, text="<b>Below ground</b>", showarrow=False, opacity=0.65)
    return fig


# -----------------------------
# Threshold view (Gandalf-style)
# -----------------------------
def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.strip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _interp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"rgb({r},{g},{b})"


def _bar_gradient_html(value_0_100: float, c_lo: str, c_hi: str, label: str, sublabel: str) -> str:
    """
    Horizontal gradient bar with a marker for the current value.
    """
    v = clamp(value_0_100, 0, 100)
    # marker position in %
    marker_left = v

    # marker color: slightly brighter
    marker_color = _interp_color(c_lo, c_hi, v / 100.0)

    return f"""
<div class="bar-wrap">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:10px;">
    <div>
      <div style="font-weight:700;font-size:1.05rem;">{label}</div>
      <div class="tiny-muted">{sublabel}</div>
    </div>
    <div class="pill"><b>{v:.0f}</b> / 100</div>
  </div>

  <div style="height:14px;"></div>

  <div style="position:relative;height:20px;border-radius:999px;
              background: linear-gradient(90deg, {c_lo}, {c_hi});
              border: 1px solid rgba(255,255,255,0.14);">
    <div style="position:absolute;left:{marker_left}%;top:-8px;transform:translateX(-50%);
                width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;
                border-bottom:10px solid rgba(255,255,255,0.85);"></div>
    <div style="position:absolute;left:{marker_left}%;top:0;transform:translateX(-50%);
                width:3px;height:20px;border-radius:99px;background: rgba(0,0,0,0.35);
                box-shadow: 0 0 0 2px rgba(255,255,255,0.25), 0 0 14px {marker_color};"></div>
  </div>

  <div style="display:flex;justify-content:space-between;margin-top:8px;" class="tiny-muted">
    <div>Low</div><div>High</div>
  </div>
</div>
"""


def _silo_threshold_html(value_m100_p100: float, label: str, sublabel: str) -> str:
    """
    SILO: below-ground filled gray / above-ground outline
    Render as a vertical-ish “ground” concept but still horizontal for simplicity.
    """
    v = clamp(value_m100_p100, -100, 100)

    # map -100..+100 to 0..100 for position
    pos = (v + 100) / 2

    # below-ground fill %
    below_fill = clamp((0 - v) / 100.0, 0.0, 1.0)  # 0..1
    below_fill_pct = below_fill * 100

    # “above ground” outline intensity
    above_pct = clamp((v / 100.0), 0.0, 1.0) * 100

    return f"""
<div class="bar-wrap">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:10px;">
    <div>
      <div style="font-weight:700;font-size:1.05rem;">{label}</div>
      <div class="tiny-muted">{sublabel}</div>
    </div>
    <div class="pill"><b>{v:.0f}</b> / 100</div>
  </div>

  <div style="height:14px;"></div>

  <!-- groundline -->
  <div class="groundline"></div>

  <div style="height:10px;"></div>

  <!-- below ground: filled gray -->
  <div style="position:relative;height:20px;border-radius:999px;
              background: rgba(255,255,255,0.04);
              border: 1px solid rgba(255,255,255,0.14); overflow:hidden;">
    <div style="position:absolute;left:0;top:0;height:20px;width:{below_fill_pct}%;
                background: rgba(190,190,190,0.55);"></div>

    <!-- above ground: outline only -->
    <div style="position:absolute;left:0;top:0;height:20px;width:{above_pct}%;
                border: 2px solid rgba(240,240,240,0.55); border-right:none;
                box-sizing:border-box; border-radius:999px;"></div>

    <!-- marker -->
    <div style="position:absolute;left:{pos}%;top:-8px;transform:translateX(-50%);
                width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;
                border-bottom:10px solid rgba(255,255,255,0.85);"></div>
    <div style="position:absolute;left:{pos}%;top:0;transform:translateX(-50%);
                width:3px;height:20px;border-radius:99px;background: rgba(0,0,0,0.35);
                box-shadow: 0 0 0 2px rgba(255,255,255,0.25);"></div>
  </div>

  <div style="display:flex;justify-content:space-between;margin-top:8px;" class="tiny-muted">
    <div>Below ground</div><div>Above ground</div>
  </div>
</div>
"""


def threshold_view(mode: str, age: int):
    df = build_df(mode, max_age=MAX_AGE)

    h = float(df.loc[df["age"] == age, "health"].iloc[0])
    w = float(df.loc[df["age"] == age, "wealth"].iloc[0])
    s = float(df.loc[df["age"] == age, "silo"].iloc[0])

    # band labels
    hb = health_band_label(h)
    wb = wealth_band_label(w)
    sb = "Above ground" if s >= 0 else "Below ground"

    st.markdown(
        f"""
<div class="lrp-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
    <div>
      <div style="font-size:1.2rem;font-weight:800;">Threshold View</div>
      <div class="small-muted">A quick “at-a-glance” readout for <b>{mode}</b> at <b>Age {age}</b>.</div>
    </div>
    <div class="pill">Switchback at <b>55</b> → <span style="opacity:0.8;">Hitting the Switchback</span></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        st.markdown(
            _bar_gradient_html(
                h,
                c_lo="#B00020",   # deep red
                c_hi="#00C853",   # green
                label="Health",
                sublabel=f"Band: <b>{hb}</b> (red → green)",
            ),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            _bar_gradient_html(
                w,
                c_lo="#FFB300",   # amber
                c_hi="#00BFA5",   # teal
                label="Wealth",
                sublabel=f"Band: <b>{wb}</b> (amber → teal)",
            ),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            _silo_threshold_html(
                s,
                label="SILO (Presence / Meaning)",
                sublabel=f"State: <b>{sb}</b> (below-ground fill / above-ground outline)",
            ),
            unsafe_allow_html=True,
        )

    # Small legend / interpretation row
    st.markdown(
        f"""
<div class="lrp-card" style="margin-top:12px;">
  <div style="font-weight:700;margin-bottom:6px;">Interpretation</div>
  <div class="small-muted">
    Health at <b>{h:.0f}</b> suggests <b>{hb}</b> capacity.
    Wealth at <b>{w:.0f}</b> suggests <b>{wb}</b> stability.
    SILO at <b>{s:.0f}</b> suggests <b>{sb}</b> orientation.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------
# Timeline view
# -----------------------------
def timeline_view(mode: str, age: int, max_age: int):
    df = build_df(mode, max_age=max_age)

    # Current values
    row = df.loc[df["age"] == age].iloc[0]
    h, w, s = float(row["health"]), float(row["wealth"]), float(row["silo"])

    # Narrative bucket
    key = _bucket_key(age)
    narr = (SAL_NARR if mode == "SAL" else LRP_NARR).get(key, None)

    # Header card
    st.markdown(
        f"""
<div class="lrp-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;">
    <div>
      <div style="font-size:1.2rem;font-weight:800;">Timeline View</div>
      <div class="small-muted">Age-by-age trajectory for <b>{mode}</b> (with the Switchback at <b>55</b>).</div>
    </div>
    <div class="pill">Age {age} • Health <b>{h:.0f}</b> • Wealth <b>{w:.0f}</b> • SILO <b>{s:.0f}</b></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 1])

    with left:
        st.plotly_chart(plot_health(df), use_container_width=True)
        st.plotly_chart(plot_wealth(df), use_container_width=True)
        st.plotly_chart(plot_silo(df), use_container_width=True)

    with right:
        # Narrative panel
        if narr is None:
            st.markdown(
                """
<div class="lrp-card">
  <div style="font-weight:800;font-size:1.05rem;">Narrative</div>
  <div class="small-muted">No narrative found for this age bucket.</div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
<div class="lrp-card">
  <div style="font-weight:900;font-size:1.05rem;">{narr.title}</div>
  <div class="small-muted" style="margin-top:2px;">{narr.subtitle} • <b>Bucket {key}</b></div>

  <div style="height:10px;"></div>

  <div style="font-weight:800;">Diagnosis</div>
  <ul style="margin-top:6px;">
    {''.join([f'<li>{x}</li>' for x in narr.diagnosis])}
  </ul>

  <div style="height:6px;"></div>

  <div style="font-weight:800;">Prescription</div>
  <ul style="margin-top:6px;">
    {''.join([f'<li>{x}</li>' for x in narr.prescription])}
  </ul>

  <div style="height:10px;"></div>
  <div class="tiny-muted">
    Tip: If you want the subheading text to subtly change by age for SAL (instead of staying constant),
    we can add a dedicated SAL “headline-by-bucket” map the same way this narrative works.
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

        # Switchback explainer
        if age < SWITCHBACK_AGE:
            sb_text = "The switchback is ahead — the default slope still feels manageable."
        elif age == SWITCHBACK_AGE:
            sb_text = "You are at the switchback — this is where trajectory becomes intentional."
        else:
            sb_text = "Past the switchback — compounding returns (or compounding costs) dominate."

        st.markdown(
            f"""
<div class="lrp-card" style="margin-top:12px;">
  <div style="font-weight:800;">Switchback Check</div>
  <div class="small-muted" style="margin-top:6px;">{sb_text}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# -----------------------------
# Sidebar controls
# -----------------------------
st.title("🧭 Life Reclamation Dashboard")
st.caption("Single-file Streamlit app • Timeline + Threshold views • SAL vs LRP modes")

with st.sidebar:
    st.header("Controls")

    view = st.radio(
        "View",
        ["Timeline view", "Threshold view"],
        index=0,
    )

    mode = st.radio(
        "Mode",
        ["SAL", "LRP"],
        index=0,
        help="SAL = default trajectory. LRP = Life Reclamation Path (switchback at age 55).",
    )

    max_age = st.slider(
        "Max age shown on timeline",
        min_value=80,
        max_value=100,
        value=92 if mode == "LRP" else 85,
        step=1,
    )

    age = st.slider(
        "Age",
        min_value=MIN_AGE,
        max_value=max_age,
        value=min(55, max_age),
        step=1,
    )

    st.divider()
    st.markdown(
        """
**Legend**
- Health: Fit / Functional / Frail
- Wealth: Poor / Enough / Rich
- SILO: Below-ground ↔ Above-ground
"""
    )

# -----------------------------
# Main render
# -----------------------------
if view == "Threshold view":
    threshold_view(mode=mode, age=age)
else:
    timeline_view(mode=mode, age=age, max_age=max_age)

# Footer note
st.markdown(
    """
<div class="tiny-muted" style="margin-top:18px;opacity:0.85;">
Built for the Life Reclamation Project. Switchback marker is fixed at age 55 (“Hitting the Switchback”).
</div>
""",
    unsafe_allow_html=True,
)
