# app.py — Life Reclamation Dashboard (Single-file Streamlit app)
# Drop into GitHub and deploy on Streamlit Cloud.
#
# Key updates vs prior version:
# - No "max age shown" slider. SAL ends at 77, LRP ends at 92 automatically.
# - Timeline can show Health/Wealth/SILO on ONE chart (any combo), or as small multiples.
# - SILO is displayed as age-range "blocks" (0–5, 5–10, ...; SAL ends 75–77, LRP ends 90–92).
# - "Threshold view" is replaced with an optional Snapshot expander (you can remove later).
#
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
.block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
h1, h2, h3 { letter-spacing: -0.02em; }

.lrp-card {
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  padding: 14px 14px 12px 14px;
}
.small-muted { color: rgba(255,255,255,0.65); font-size: 0.92rem; }
.tiny-muted { color: rgba(255,255,255,0.55); font-size: 0.82rem; }
.pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.04);
}

/* SILO block grid */
.silo-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(110px, 1fr));
  gap: 10px;
}
@media (max-width: 1200px) {
  .silo-grid { grid-template-columns: repeat(4, minmax(110px, 1fr)); }
}
@media (max-width: 850px) {
  .silo-grid { grid-template-columns: repeat(3, minmax(110px, 1fr)); }
}
.silo-tile {
  border-radius: 14px;
  padding: 10px 10px 8px 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.02);
  position: relative;
}
.silo-tile.active {
  outline: 2px solid rgba(255,255,255,0.35);
  box-shadow: 0 0 0 2px rgba(255,255,255,0.08);
}
.silo-label {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.75);
  margin-bottom: 8px;
  display:flex;
  justify-content:space-between;
  gap:8px;
}
.silo-ground {
  height: 2px;
  background: rgba(255,255,255,0.18);
  border-radius: 99px;
  margin: 2px 0 8px 0;
}
.silo-bar {
  height: 18px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.03);
  overflow: hidden;
  position: relative;
}
.silo-fill {
  position:absolute; left:0; top:0; bottom:0;
  background: rgba(190,190,190,0.55);
}
.silo-outline {
  position:absolute; left:0; top:0; bottom:0;
  border: 2px solid rgba(240,240,240,0.55);
  border-right: none;
  box-sizing: border-box;
  border-radius: 999px;
}
.silo-score {
  font-size: 0.74rem;
  color: rgba(255,255,255,0.55);
  margin-top: 6px;
}

/* Snapshot bars */
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
MIN_AGE = 0

SAL_END_AGE = 77
LRP_END_AGE = 92


# -----------------------------
# Buckets: 0–5, 5–10, ... with custom last bucket
# -----------------------------
def bucket_edges_for_mode(mode: str) -> List[Tuple[int, int]]:
    """
    Returns list of (lo, hi) inclusive bounds, where hi is inclusive.
    SAL: ... 70–75, 75–77
    LRP: ... 85–90, 90–92
    """
    if mode == "SAL":
        edges = []
        for lo in range(0, 75, 5):
            edges.append((lo, lo + 5))
        edges.append((75, 77))
        return edges

    edges = []
    for lo in range(0, 90, 5):
        edges.append((lo, lo + 5))
    edges.append((90, 92))
    return edges


def bucket_for_age(age: int, mode: str) -> Tuple[int, int]:
    edges = bucket_edges_for_mode(mode)
    for lo, hi in edges:
        if lo <= age <= hi:
            return lo, hi
    # fallback
    return edges[-1]


def bucket_key(lo: int, hi: int) -> str:
    return f"{lo:02d}-{hi:02d}"


# -----------------------------
# Narrative text buckets
# -----------------------------
@dataclass(frozen=True)
class BucketNarrative:
    title: str
    subtitle: str
    diagnosis: List[str]
    prescription: List[str]


def build_narratives() -> Tuple[Dict[str, BucketNarrative], Dict[str, BucketNarrative]]:
    """
    Keep these short/skimmable. You can rewrite copy later—this is wiring + structure.
    """
    sal: Dict[str, BucketNarrative] = {}
    lrp: Dict[str, BucketNarrative] = {}

    # SAL: define a few explicitly; others will be generic fallbacks
    def sal_set(lo, hi, diag, rx):
        sal[bucket_key(lo, hi)] = BucketNarrative(
            title="A Typical American Life",
            subtitle=f"Health • ages {lo}–{hi}",
            diagnosis=diag,
            prescription=rx,
        )

    sal_set(0, 5, ["Healthy (but the default path is being set)."], ["Whole foods + play + sleep (baseline is strong)."])
    sal_set(5, 10, ["Diet and screens begin their quiet takeover."], ["Sugary snacks + more devices; less free play."])
    sal_set(10, 15, ["“Healthy?” (exercise narrows to organized sports)."], ["Fast food rises; sleep slips; scrolling starts."])
    sal_set(35, 40, ["Mood and sleep issues show up."], ["Passive coping increases; root causes go unaddressed."])
    sal_set(55, 60, ["Big diagnosis era (autoimmune, heart, cancer risk rises)."], ["Procedures/meds; “maybe exercise now” arrives late."])
    sal_set(75, 77, ["End-of-life window for the default path."], ["Mobility is limited; dependence rises fast."])

    # LRP: generic structure + special switchback bucket
    def lrp_set(lo, hi, diag, rx):
        lrp[bucket_key(lo, hi)] = BucketNarrative(
            title="Life Reclamation Path",
            subtitle=f"Health • ages {lo}–{hi}",
            diagnosis=diag,
            prescription=rx,
        )

    # Fill LRP for all buckets
    for lo, hi in bucket_edges_for_mode("LRP"):
        if (lo, hi) == (0, 5):
            lrp_set(lo, hi, ["Strong start."], ["Build identity: “I move every day.”"])
        elif (lo, hi) == (55, 60):
            lrp_set(
                lo,
                hi,
                ["Hitting the Switchback — choose your trajectory."],
                [
                    "5-year rebuild: strength 2–3x/week + Zone 2 3x/week.",
                    "Design the environment: protein-first, steps, sleep, sunlight.",
                    "Reduce financial stress + increase purpose to sustain change.",
                ],
            )
        elif lo < 55:
            lrp_set(lo, hi, ["Mostly functional; drift kept in check."], ["Keep strength + aerobic base non-negotiable."])
        elif lo < 65:
            lrp_set(lo, hi, ["Rebuild phase: capacity rises quickly."], ["Progressive strength; Zone 2 volume; mobility."])
        elif lo < 80:
            lrp_set(lo, hi, ["Maintenance: protect the peak."], ["Keep intensity; prioritize power + balance."])
        else:
            lrp_set(lo, hi, ["Longevity: independence is the goal."], ["Strength minimums; walk daily; simplify essentials."])

    return sal, lrp


SAL_NARR, LRP_NARR = build_narratives()


# -----------------------------
# Trajectory math
# -----------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def smoothstep(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def health_score(age: int, mode: str) -> float:
    a = float(age)
    if mode == "SAL":
        base = 92 - 0.35 * a
        accel = 0.0
        if a > 40:
            accel += (a - 40) * 0.55
        if a > 55:
            accel += (a - 55) * 1.10
        if a > 70:
            accel += (a - 70) * 1.60
        s = base - accel
        if a >= 77:
            s = 2.0
        return clamp(s, 0, 100)

    # LRP
    if a < SWITCHBACK_AGE:
        return clamp(90 - 0.20 * a, 0, 100)

    t = (a - SWITCHBACK_AGE) / 5.0
    improve = 18 * smoothstep(t)  # peak ~60
    decline = 0.0
    if a > 60:
        decline += (a - 60) * 0.45
    if a > 75:
        decline += (a - 75) * 0.55
    if a > 85:
        decline += (a - 85) * 0.70

    s0 = 90 - 0.20 * SWITCHBACK_AGE
    s = s0 + improve - decline
    if a >= 92:
        s = max(s, 48.0)
    return clamp(s, 0, 100)


def wealth_score(age: int, mode: str) -> float:
    a = float(age)
    accum = 100 / (1 + math.exp(-(a - 45) / 10))
    accum = (accum - 5) * 1.05

    if mode == "SAL":
        drag = 0.0
        if 25 <= a <= 55:
            drag += 10 * smoothstep((a - 25) / 30)
        if a > 55:
            drag += 12 * smoothstep((a - 55) / 15)
        if a > 70:
            drag += 10 * smoothstep((a - 70) / 10)
        return clamp(accum - drag, 0, 100)

    drag = 0.0
    if 25 <= a <= 55:
        drag += 6 * smoothstep((a - 25) / 30)
    if a > 55:
        drag += 5 * smoothstep((a - 55) / 15)
    uplift = 6 * smoothstep((a - 35) / 25)
    return clamp(accum - drag + uplift, 0, 100)


def silo_score(age: int, mode: str) -> float:
    a = float(age)
    if mode == "SAL":
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
        return clamp(20 - 0.45 * a, -100, 100)

    t = (a - SWITCHBACK_AGE) / 4.0
    lift = 85 * smoothstep(t)
    late = (a - 80) * 0.35 if a > 80 else 0.0
    s0 = 20 - 0.45 * SWITCHBACK_AGE
    return clamp(s0 + lift - late, -100, 100)


def build_df(mode: str) -> pd.DataFrame:
    end_age = SAL_END_AGE if mode == "SAL" else LRP_END_AGE
    ages = list(range(MIN_AGE, end_age + 1))
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
# Labels
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


# -----------------------------
# Plot: single combined chart or small multiples
# -----------------------------
def add_switchback(fig: go.Figure, y_top: float, x: int = SWITCHBACK_AGE):
    fig.add_vline(x=x, line_width=2, line_dash="dash", opacity=0.9)
    fig.add_annotation(
        x=x,
        y=y_top,
        xanchor="left",
        yanchor="top",
        text=f"<b>Hitting the Switchback</b><br><span style='font-size:12px;opacity:0.75'>Age {x}</span>",
        showarrow=False,
        bgcolor="rgba(0,0,0,0.35)",
        bordercolor="rgba(255,255,255,0.18)",
        borderwidth=1,
        borderpad=8,
    )


def plot_combined(df: pd.DataFrame, series: List[str], silo_mode: str) -> go.Figure:
    """
    series: subset of ["health","wealth","silo"]
    silo_mode:
      - "Normalized (0–100)"
      - "Native (-100..100) on 2nd axis"
    """
    has_silo = "silo" in series
    use_secondary = has_silo and (silo_mode.startswith("Native"))

    fig = make_subplots(specs=[[{"secondary_y": use_secondary}]])

    # Axis ranges
    end_age = int(df["age"].max())

    # Always use primary y 0..100 (health/wealth)
    y_top = 100

    if "health" in series:
        fig.add_trace(
            go.Scatter(
                x=df["age"],
                y=df["health"],
                mode="lines",
                line=dict(width=5),
                name="Health",
                hovertemplate="Age %{x}<br>Health: %{y:.1f}<extra></extra>",
            ),
            secondary_y=False,
        )

    if "wealth" in series:
        fig.add_trace(
            go.Scatter(
                x=df["age"],
                y=df["wealth"],
                mode="lines",
                line=dict(width=5),
                name="Wealth",
                hovertemplate="Age %{x}<br>Wealth: %{y:.1f}<extra></extra>",
            ),
            secondary_y=False,
        )

    if "silo" in series:
        if silo_mode.startswith("Normalized"):
            y = (df["silo"] + 100) / 2.0
            fig.add_trace(
                go.Scatter(
                    x=df["age"],
                    y=y,
                    mode="lines",
                    line=dict(width=5),
                    name="SILO (norm)",
                    hovertemplate="Age %{x}<br>SILO (normalized): %{y:.1f}<extra></extra>",
                ),
                secondary_y=False,
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df["age"],
                    y=df["silo"],
                    mode="lines",
                    line=dict(width=5),
                    name="SILO",
                    hovertemplate="Age %{x}<br>SILO: %{y:.0f}<extra></extra>",
                ),
                secondary_y=True,
            )

    add_switchback(fig, y_top=y_top)

    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=18, b=20),
        xaxis=dict(title="Age", range=[MIN_AGE, end_age]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )

    fig.update_yaxes(title_text="Health / Wealth (0–100)", range=[0, 100], secondary_y=False)

    if use_secondary:
        fig.update_yaxes(title_text="SILO (-100..100)", range=[-100, 100], secondary_y=True)
    else:
        # if silo normalized is on primary, keep primary title generic
        if has_silo and silo_mode.startswith("Normalized") and len(series) == 1 and series[0] == "silo":
            fig.update_yaxes(title_text="SILO (normalized 0–100)", range=[0, 100], secondary_y=False)

    return fig


def plot_small_multiple(df: pd.DataFrame, series: List[str], silo_mode: str) -> List[go.Figure]:
    figs = []
    end_age = int(df["age"].max())

    if "health" in series:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["age"], y=df["health"], mode="lines", line=dict(width=5)))
        add_switchback(fig, y_top=100)
        fig.update_layout(height=280, margin=dict(l=20, r=16, t=12, b=18))
        fig.update_xaxes(title="Age", range=[MIN_AGE, end_age])
        fig.update_yaxes(title="Health (Fit → Frail)", range=[0, 100])
        figs.append(fig)

    if "wealth" in series:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["age"], y=df["wealth"], mode="lines", line=dict(width=5)))
        add_switchback(fig, y_top=100)
        fig.update_layout(height=280, margin=dict(l=20, r=16, t=12, b=18))
        fig.update_xaxes(title="Age", range=[MIN_AGE, end_age])
        fig.update_yaxes(title="Wealth (Poor → Rich)", range=[0, 100])
        figs.append(fig)

    if "silo" in series:
        fig = go.Figure()
        if silo_mode.startswith("Normalized"):
            y = (df["silo"] + 100) / 2.0
            fig.add_trace(go.Scatter(x=df["age"], y=y, mode="lines", line=dict(width=5)))
            fig.update_yaxes(title="SILO (normalized)", range=[0, 100])
        else:
            fig.add_trace(go.Scatter(x=df["age"], y=df["silo"], mode="lines", line=dict(width=5)))
            fig.update_yaxes(title="SILO (-100..100)", range=[-100, 100])

        add_switchback(fig, y_top=100 if silo_mode.startswith("Normalized") else 100)
        fig.update_layout(height=280, margin=dict(l=20, r=16, t=12, b=18))
        fig.update_xaxes(title="Age", range=[MIN_AGE, end_age])
        figs.append(fig)

    return figs


# -----------------------------
# SILO Blocks (age-range tiles)
# -----------------------------
def silo_blocks(df: pd.DataFrame, mode: str, active_age: int):
    edges = bucket_edges_for_mode(mode)
    active_lo, active_hi = bucket_for_age(active_age, mode)
    tiles = []

    for lo, hi in edges:
        # mean SILO over bucket
        bucket = df[(df["age"] >= lo) & (df["age"] <= hi)]
        v = float(bucket["silo"].mean()) if len(bucket) else 0.0

        # below-ground fill percentage
        below_fill = clamp((0 - v) / 100.0, 0.0, 1.0)   # 0..1
        below_pct = below_fill * 100

        # above-ground outline percentage
        above_pct = clamp(v / 100.0, 0.0, 1.0) * 100

        active = (lo == active_lo and hi == active_hi)

        tiles.append(
            f"""
<div class="silo-tile {'active' if active else ''}">
  <div class="silo-label">
    <div><b>{lo}–{hi}</b></div>
    <div style="opacity:0.85;">{int(round(v))}</div>
  </div>
  <div class="silo-ground"></div>
  <div class="silo-bar">
    <div class="silo-fill" style="width:{below_pct}%;"></div>
    <div class="silo-outline" style="width:{above_pct}%;"></div>
  </div>
  <div class="silo-score">{'Below ground' if v < 0 else 'Above ground'}</div>
</div>
"""
        )

    st.markdown(
        f"""
<div class="lrp-card" style="margin-top:12px;">
  <div style="font-weight:800;">SILO blocks by age range</div>
  <div class="small-muted" style="margin-top:4px;">
    Below-ground = filled gray • Above-ground = outline • Highlight = your current bucket
  </div>
  <div style="height:12px;"></div>
  <div class="silo-grid">
    {''.join(tiles)}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# -----------------------------
# Snapshot (optional)
# -----------------------------
def _hex_to_rgb(hex_color: str):
    h = hex_color.strip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _interp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"rgb({r},{g},{b})"


def _bar_gradient_html(value_0_100: float, c_lo: str, c_hi: str, label: str, sublabel: str) -> str:
    v = clamp(value_0_100, 0, 100)
    marker_left = v
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


# -----------------------------
# Timeline view renderer
# -----------------------------
def timeline_view(mode: str, age: int, series: List[str], chart_layout: str, silo_mode: str, show_snapshot: bool):
    df = build_df(mode)
    end_age = int(df["age"].max())

    # clamp age to end_age
    age = min(age, end_age)

    row = df.loc[df["age"] == age].iloc[0]
    h, w, s = float(row["health"]), float(row["wealth"]), float(row["silo"])

    lo, hi = bucket_for_age(age, mode)
    key = bucket_key(lo, hi)
    narr = (SAL_NARR if mode == "SAL" else LRP_NARR).get(key)

    # Header
    st.markdown(
        f"""
<div class="lrp-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;">
    <div>
      <div style="font-size:1.2rem;font-weight:800;">Timeline View</div>
      <div class="small-muted">Mode: <b>{mode}</b> • Ends at <b>Age {end_age}</b> • Switchback at <b>55</b></div>
    </div>
    <div class="pill">Age {age} • Health <b>{h:.0f}</b> • Wealth <b>{w:.0f}</b> • SILO <b>{s:.0f}</b></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.35, 1])

    with left:
        if chart_layout == "Single chart":
            fig = plot_combined(df, series=series, silo_mode=silo_mode)
            st.plotly_chart(fig, use_container_width=True)
        else:
            figs = plot_small_multiple(df, series=series, silo_mode=silo_mode)
            for fig in figs:
                st.plotly_chart(fig, use_container_width=True)

        # SILO blocks always shown (this is your new primary SILO visualization)
        silo_blocks(df, mode=mode, active_age=age)

    with right:
        # Narrative
        if narr:
            st.markdown(
                f"""
<div class="lrp-card">
  <div style="font-weight:900;font-size:1.05rem;">{narr.title}</div>
  <div class="small-muted" style="margin-top:2px;">{narr.subtitle} • <b>Bucket {lo}–{hi}</b></div>

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
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
<div class="lrp-card">
  <div style="font-weight:800;">Narrative</div>
  <div class="small-muted" style="margin-top:6px;">
    No narrative found for this bucket yet. (Easy to add copy for this age range.)
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

        # Optional Snapshot (this replaces your confusing Threshold view)
        if show_snapshot:
            with st.expander("Snapshot (optional, at-a-glance)", expanded=False):
                hb = health_band_label(h)
                wb = wealth_band_label(w)
                silo_norm = (s + 100) / 2

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        _bar_gradient_html(
                            h, "#B00020", "#00C853",
                            "Health", f"Band: <b>{hb}</b> (red → green)"
                        ),
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        _bar_gradient_html(
                            w, "#FFB300", "#00BFA5",
                            "Wealth", f"Band: <b>{wb}</b> (amber → teal)"
                        ),
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    _bar_gradient_html(
                        silo_norm, "#5C5C5C", "#EAEAEA",
                        "SILO (normalized)", "Below-ground ↔ Above-ground (shown as 0–100 here)"
                    ),
                    unsafe_allow_html=True,
                )


# -----------------------------
# App UI
# -----------------------------
st.title("🧭 Life Reclamation Dashboard")
st.caption("Timeline-first • SAL vs LRP • Configurable graph + SILO blocks by age bucket")

with st.sidebar:
    st.header("Controls")

    mode = st.radio("Mode", ["SAL", "LRP"], index=0)
    end_age = SAL_END_AGE if mode == "SAL" else LRP_END_AGE

    # Age slider auto-bounded
    age = st.slider("Age", min_value=MIN_AGE, max_value=end_age, value=min(55, end_age), step=1)

    st.divider()
    st.subheader("Graph")

    chart_layout = st.radio("Layout", ["Single chart", "Small multiples"], index=0)

    # Pick which series to show
    series = st.multiselect(
        "Show on graph",
        options=["health", "wealth", "silo"],
        default=["health"],
        help="Choose any combination. SILO can be normalized or put on a secondary axis.",
    )
    if not series:
        series = ["health"]

    silo_mode = "Normalized (0–100)"
    if "silo" in series and (("health" in series) or ("wealth" in series)):
        silo_mode = st.radio(
            "If SILO is on the same chart:",
            ["Normalized (0–100)", "Native (-100..100) on 2nd axis"],
            index=0,
        )
    elif "silo" in series:
        silo_mode = st.radio(
            "SILO scale:",
            ["Normalized (0–100)", "Native (-100..100)"],
            index=0,
        )

    st.divider()
    show_snapshot = st.checkbox("Show Snapshot (optional)", value=False)

    st.divider()
    st.markdown(
        """
**Legend**
- Health: Fit / Functional / Frail
- Wealth: Poor / Enough / Rich
- SILO blocks: below-ground fill / above-ground outline
"""
    )

timeline_view(
    mode=mode,
    age=age,
    series=series,
    chart_layout=chart_layout,
    silo_mode=silo_mode,
    show_snapshot=show_snapshot,
)

st.markdown(
    """
<div class="tiny-muted" style="margin-top:18px;opacity:0.85;">
Switchback marker is fixed at age 55 (“Hitting the Switchback”). SAL ends at 77; LRP ends at 92.
</div>
""",
    unsafe_allow_html=True,
)
