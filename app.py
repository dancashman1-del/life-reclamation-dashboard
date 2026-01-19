# app.py — Life Reclamation Dashboard (Bucket selector + 3 tabs)
# Single-file Streamlit app suitable for GitHub + Streamlit Cloud
#
# Guarantees:
# - No year-by-year age slider: ONLY bucket selector (0–5, 5–10, ...; SAL ends 75–77, LRP ends 90–92)
# - Bullets always visible for selected bucket
# - Separate tabs for Health / Wealth / SILO with proper Y-axis labels
# - SILO blocks only shown on SILO tab
#
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------
# Page config + styling
# -----------------------------
st.set_page_config(page_title="Life Reclamation Dashboard", page_icon="🧭", layout="wide")

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

/* SILO bucket tiles */
.silo-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(110px, 1fr));
  gap: 10px;
}
@media (max-width: 1200px) { .silo-grid { grid-template-columns: repeat(4, minmax(110px, 1fr)); } }
@media (max-width: 850px)  { .silo-grid { grid-template-columns: repeat(3, minmax(110px, 1fr)); } }

.silo-tile {
  border-radius: 14px;
  padding: 10px 10px 8px 10px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.02);
}
.silo-tile.active {
  outline: 2px solid rgba(255,255,255,0.35);
  box-shadow: 0 0 0 2px rgba(255,255,255,0.08);
}
.silo-label {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.75);
  margin-bottom: 8px;
  display:flex; justify-content:space-between; gap:8px;
}
.silo-ground { height: 2px; background: rgba(255,255,255,0.18); border-radius: 99px; margin: 2px 0 8px 0; }
.silo-bar {
  height: 18px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.03);
  overflow: hidden; position: relative;
}
.silo-fill { position:absolute; left:0; top:0; bottom:0; background: rgba(190,190,190,0.55); }
.silo-outline {
  position:absolute; left:0; top:0; bottom:0;
  border: 2px solid rgba(240,240,240,0.55);
  border-right: none; box-sizing: border-box; border-radius: 999px;
}
.silo-score { font-size: 0.74rem; color: rgba(255,255,255,0.55); margin-top: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

SWITCHBACK_AGE = 55
SAL_END_AGE = 77
LRP_END_AGE = 92


# -----------------------------
# Buckets: 0–5, 5–10, ... custom last bucket
# -----------------------------
def bucket_edges_for_mode(mode: str) -> List[Tuple[int, int]]:
    if mode == "SAL":
        edges = [(lo, lo + 5) for lo in range(0, 75, 5)]
        edges.append((75, 77))
        return edges
    edges = [(lo, lo + 5) for lo in range(0, 90, 5)]
    edges.append((90, 92))
    return edges


def bucket_key(lo: int, hi: int) -> str:
    return f"{lo:02d}-{hi:02d}"


def bucket_midpoint(lo: int, hi: int) -> int:
    return int(round((lo + hi) / 2))


# -----------------------------
# Narrative
# -----------------------------
@dataclass(frozen=True)
class BucketNarrative:
    title: str
    subheading: str
    diagnosis: List[str]
    prescription: List[str]


def build_narratives() -> Tuple[Dict[str, BucketNarrative], Dict[str, BucketNarrative]]:
    sal: Dict[str, BucketNarrative] = {}
    lrp: Dict[str, BucketNarrative] = {}

    def sal_set(lo, hi, sub, diag, rx):
        sal[bucket_key(lo, hi)] = BucketNarrative(
            title="A Typical American Life",
            subheading=sub,
            diagnosis=diag,
            prescription=rx,
        )

    # A few filled; others fall back to placeholders (you can fill later)
    sal_set(0, 5, "The default path begins — quietly.",
            ["Healthy (but the default path is being set)."],
            ["Whole foods + play + sleep (baseline is strong)."])

    sal_set(5, 10, "Food quality slips. Screen-time grows.",
            ["Diet and screens begin their quiet takeover."],
            ["Sugary snacks + more devices; less free play."])

    sal_set(10, 15, "Movement narrows. Dopamine rises.",
            ["“Healthy?” (exercise narrows to organized sports)."],
            ["Fast food rises; sleep slips; scrolling starts."])

    sal_set(55, 60, "Minimized early, medicated later — plus stress and drift.",
            ["Big diagnosis era (autoimmune, heart, cancer risk rises)."],
            ["Procedures/meds; “maybe exercise now” arrives late.",
             "Some diet cleanup, but baseline fitness is limited."])

    sal_set(75, 77, "The end is often long and expensive.",
            ["End-of-life window for the default path."],
            ["Mobility is limited; dependence rises fast."])

    def lrp_set(lo, hi, sub, diag, rx):
        lrp[bucket_key(lo, hi)] = BucketNarrative(
            title="Life Reclamation Path",
            subheading=sub,
            diagnosis=diag,
            prescription=rx,
        )

    for lo, hi in bucket_edges_for_mode("LRP"):
        if (lo, hi) == (0, 5):
            lrp_set(lo, hi, "Build the identity early.",
                    ["Strong start."],
                    ["“I move every day.” Whole foods + play + sleep."])
        elif (lo, hi) == (55, 60):
            lrp_set(lo, hi, "Hitting the Switchback.",
                    ["This is the conscious turn — trajectory becomes intentional."],
                    ["5-year rebuild: strength 2–3x/week + Zone 2 3x/week.",
                     "Design environment: protein-first, steps, sleep, sunlight.",
                     "Reduce stress via Wealth + Purpose alignment."])
        elif lo < 55:
            lrp_set(lo, hi, "Stay functional. Don’t drift.",
                    ["Mostly functional; drift kept in check."],
                    ["Keep strength + aerobic base non-negotiable.",
                     "Limit screen-based coping; protect sleep."])
        elif lo < 65:
            lrp_set(lo, hi, "Rebuild fast. Peak by ~60.",
                    ["Capacity rises quickly with consistency."],
                    ["Progressive strength; Zone 2 volume; mobility + balance."])
        elif lo < 80:
            lrp_set(lo, hi, "Protect the peak.",
                    ["Maintenance phase: prevent the slide."],
                    ["Keep intensity; prioritize power + balance; stay social."])
        else:
            lrp_set(lo, hi, "Finish functional.",
                    ["Longevity phase: independence is the goal."],
                    ["Strength minimums; daily walking; simplify essentials."])

    return sal, lrp


SAL_NARR, LRP_NARR = build_narratives()


# -----------------------------
# Scoring functions
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

    if a < SWITCHBACK_AGE:
        return clamp(90 - 0.20 * a, 0, 100)

    t = (a - SWITCHBACK_AGE) / 5.0
    improve = 18 * smoothstep(t)
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

    if a < SWITCHBACK_AGE:
        return clamp(20 - 0.45 * a, -100, 100)

    t = (a - SWITCHBACK_AGE) / 4.0
    lift = 85 * smoothstep(t)
    late = (a - 80) * 0.35 if a > 80 else 0.0
    s0 = 20 - 0.45 * SWITCHBACK_AGE
    return clamp(s0 + lift - late, -100, 100)


def build_df(mode: str) -> pd.DataFrame:
    end_age = SAL_END_AGE if mode == "SAL" else LRP_END_AGE
    ages = list(range(0, end_age + 1))
    rows = [{"age": a,
             "health": health_score(a, mode),
             "wealth": wealth_score(a, mode),
             "silo": silo_score(a, mode)} for a in ages]
    return pd.DataFrame(rows)


# -----------------------------
# Plots
# -----------------------------
def add_switchback(fig: go.Figure, y_top: float):
    fig.add_vline(x=SWITCHBACK_AGE, line_width=2, line_dash="dash", opacity=0.9)
    fig.add_annotation(
        x=SWITCHBACK_AGE,
        y=y_top,
        xanchor="left",
        yanchor="top",
        text=f"<b>Hitting the Switchback</b><br><span style='font-size:12px;opacity:0.75'>Age {SWITCHBACK_AGE}</span>",
        showarrow=False,
        bgcolor="rgba(0,0,0,0.35)",
        bordercolor="rgba(255,255,255,0.18)",
        borderwidth=1,
        borderpad=8,
    )


def plot_health(df: pd.DataFrame) -> go.Figure:
    end_age = int(df["age"].max())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["age"], y=df["health"], mode="lines", line=dict(width=6),
                             hovertemplate="Age %{x}<br>Health: %{y:.1f}<extra></extra>"))

    # bands
    fig.add_hrect(y0=70, y1=100, opacity=0.10, line_width=0)
    fig.add_hrect(y0=45, y1=70, opacity=0.07, line_width=0)
    fig.add_hrect(y0=0, y1=45, opacity=0.10, line_width=0)

    # labels
    fig.add_annotation(x=1, y=95, text="<b>Fit</b>", showarrow=False, opacity=0.75)
    fig.add_annotation(x=1, y=58, text="<b>Functional</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=1, y=18, text="<b>Frail</b>", showarrow=False, opacity=0.75)

    add_switchback(fig, y_top=100)

    fig.update_layout(
        height=430,
        margin=dict(l=30, r=20, t=15, b=25),
        xaxis=dict(title="Age", range=[0, end_age]),
        yaxis=dict(title="Health (Fit → Frail)", range=[0, 100]),
        showlegend=False,
    )
    return fig


def plot_wealth(df: pd.DataFrame) -> go.Figure:
    end_age = int(df["age"].max())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["age"], y=df["wealth"], mode="lines", line=dict(width=6),
                             hovertemplate="Age %{x}<br>Wealth: %{y:.1f}<extra></extra>"))

    # bands
    fig.add_hrect(y0=70, y1=100, opacity=0.10, line_width=0)
    fig.add_hrect(y0=40, y1=70, opacity=0.07, line_width=0)
    fig.add_hrect(y0=0, y1=40, opacity=0.10, line_width=0)

    # labels
    fig.add_annotation(x=1, y=95, text="<b>Rich</b>", showarrow=False, opacity=0.75)
    fig.add_annotation(x=1, y=55, text="<b>Enough</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=1, y=16, text="<b>Poor</b>", showarrow=False, opacity=0.75)

    add_switchback(fig, y_top=100)

    fig.update_layout(
        height=430,
        margin=dict(l=30, r=20, t=15, b=25),
        xaxis=dict(title="Age", range=[0, end_age]),
        yaxis=dict(title="Wealth (Poor → Rich)", range=[0, 100]),
        showlegend=False,
    )
    return fig


def plot_silo(df: pd.DataFrame) -> go.Figure:
    end_age = int(df["age"].max())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["age"], y=df["silo"], mode="lines", line=dict(width=6),
                             hovertemplate="Age %{x}<br>SILO: %{y:.0f}<extra></extra>"))

    fig.add_hline(y=0, line_width=2, opacity=0.65)

    add_switchback(fig, y_top=100)

    fig.update_layout(
        height=430,
        margin=dict(l=30, r=20, t=15, b=25),
        xaxis=dict(title="Age", range=[0, end_age]),
        yaxis=dict(title="SILO (Below-ground → Above-ground)", range=[-100, 100]),
        showlegend=False,
    )

    fig.add_annotation(x=1, y=75, text="<b>Above ground</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=1, y=-75, text="<b>Below ground</b>", showarrow=False, opacity=0.65)

    return fig


# -----------------------------
# SILO blocks
# -----------------------------
def silo_blocks(df: pd.DataFrame, mode: str, active_lo: int, active_hi: int):
    tiles = []
    for lo, hi in bucket_edges_for_mode(mode):
        bucket = df[(df["age"] >= lo) & (df["age"] <= hi)]
        v = float(bucket["silo"].mean()) if len(bucket) else 0.0

        below_fill = clamp((0 - v) / 100.0, 0.0, 1.0)
        below_pct = below_fill * 100
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
<div class="lrp-card">
  <div style="font-weight:800;">SILO “silos” by age bucket</div>
  <div class="small-muted" style="margin-top:4px;">
    Below-ground = filled gray • Above-ground = outline • Highlight = selected bucket
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
# UI
# -----------------------------
st.title("🧭 Life Reclamation Dashboard")
st.caption("Bucketed life chapters • SAL vs LRP • Separate graphs for clean labels")

with st.sidebar:
    st.header("Controls")

    mode = st.radio("Mode", ["SAL", "LRP"], index=0)

    edges = bucket_edges_for_mode(mode)
    labels = [f"{lo}–{hi}" for lo, hi in edges]
    chosen = st.selectbox("Life chapter (bucket)", labels, index=0)
    idx = labels.index(chosen)
    lo, hi = edges[idx]

    st.divider()
    st.markdown(
        """
**Legend**
- Health bands: Fit / Functional / Frail  
- Wealth bands: Rich / Enough / Poor  
- SILO: Below-ground ↔ Above-ground  
- Switchback: Age 55
"""
    )

# Data + representative age
df = build_df(mode)
age_repr = bucket_midpoint(lo, hi)
row = df.loc[df["age"] == age_repr].iloc[0]
h, w, s = float(row["health"]), float(row["wealth"]), float(row["silo"])

# Narrative (fallback if missing)
key = bucket_key(lo, hi)
narr = (SAL_NARR if mode == "SAL" else LRP_NARR).get(
    key,
    BucketNarrative(
        title=("A Typical American Life" if mode == "SAL" else "Life Reclamation Path"),
        subheading="(Subheading TBD for this bucket)",
        diagnosis=["(Add diagnosis bullets for this bucket.)"],
        prescription=["(Add prescription bullets for this bucket.)"],
    ),
)

# Header card (always)
st.markdown(
    f"""
<div class="lrp-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;">
    <div>
      <div style="font-size:1.2rem;font-weight:800;">Timeline View</div>
      <div class="small-muted">{narr.subheading}</div>
    </div>
    <div class="pill">{mode} • Bucket <b>{lo}–{hi}</b> • Health <b>{h:.0f}</b> • Wealth <b>{w:.0f}</b> • SILO <b>{s:.0f}</b></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

left, right = st.columns([1.35, 1])

with left:
    tab_h, tab_w, tab_s = st.tabs(["Health", "Wealth", "SILO"])

    with tab_h:
        st.plotly_chart(plot_health(df), use_container_width=True)

    with tab_w:
        st.plotly_chart(plot_wealth(df), use_container_width=True)

    with tab_s:
        # You can keep the SILO line if you want, but blocks are the primary.
        st.plotly_chart(plot_silo(df), use_container_width=True)
        silo_blocks(df, mode=mode, active_lo=lo, active_hi=hi)

with right:
    # Bullets always shown
    st.markdown(
        f"""
<div class="lrp-card">
  <div style="font-weight:900;font-size:1.05rem;">{narr.title}</div>
  <div class="small-muted" style="margin-top:2px;">Bucket <b>{lo}–{hi}</b></div>

  <div style="height:12px;"></div>

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
