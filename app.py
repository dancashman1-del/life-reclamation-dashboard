# app.py — Life Reclamation Dashboard (Bucket selector + 3 tabs, slide-first)
# Single-file Streamlit app suitable for GitHub + Streamlit Cloud
#
# Updates per your latest notes:
# - SAL: NO switchback dotted line at 55 (only LRP shows switchback marker)
# - SAL: show explicit end marker at Age 77 on graphs
# - Buckets: 0–5, 5–10, ... 70–75, then 75–77 (SAL). LRP ends 90–92.
# - “Locked” SAL bullets: narrative copy defined for ALL buckets (no placeholders)
# - SILO tab: blocks (“silos”) are primary; trajectory line moved to optional expander
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
# Buckets
# -----------------------------
def bucket_edges_for_mode(mode: str) -> List[Tuple[int, int]]:
    # hi inclusive
    if mode == "SAL":
        edges = [(lo, lo + 5) for lo in range(0, 75, 5)]  # 0–5 ... 70–75
        edges.append((75, 77))  # death window
        return edges
    edges = [(lo, lo + 5) for lo in range(0, 90, 5)]  # 0–5 ... 85–90
    edges.append((90, 92))
    return edges


def bucket_key(lo: int, hi: int) -> str:
    return f"{lo:02d}-{hi:02d}"


def bucket_midpoint(lo: int, hi: int) -> int:
    return int(round((lo + hi) / 2))


def end_age_for_mode(mode: str) -> int:
    return SAL_END_AGE if mode == "SAL" else LRP_END_AGE


def x_ticks_for_mode(mode: str) -> List[int]:
    end_age = end_age_for_mode(mode)
    ticks = list(range(0, (end_age // 5) * 5 + 1, 5))
    if end_age not in ticks:
        ticks.append(end_age)
    return ticks


# -----------------------------
# Narrative
# -----------------------------
@dataclass(frozen=True)
class BucketNarrative:
    title: str
    subheading: str
    diagnosis: List[str]
    prescription: List[str]


def _sal_subheading(lo: int, hi: int) -> str:
    # subtle evolution, tying in stress/purpose lightly (your earlier request)
    if hi <= 10:
        return "The default path begins — quietly."
    if hi <= 25:
        return "Drift grows: more comfort, less movement."
    if hi <= 40:
        return "Stress and convenience start calling the shots."
    if hi <= 55:
        return "Health is now negotiated: time, money, and meaning get squeezed."
    if hi <= 70:
        return "Diagnosed and managed — but capacity keeps sliding."
    return "The end is often long, expensive, and dependent."


def build_narratives() -> Tuple[Dict[str, BucketNarrative], Dict[str, BucketNarrative]]:
    sal: Dict[str, BucketNarrative] = {}
    lrp: Dict[str, BucketNarrative] = {}

    # --- SAL: LOCKED-IN for all buckets ---
    for lo, hi in bucket_edges_for_mode("SAL"):
        k = bucket_key(lo, hi)

        # Defaults (consistent SAL framing)
        diag = []
        rx = []

        if (lo, hi) == (0, 5):
            diag = ["Healthy (but the default path is being set)."]
            rx = ["Whole foods + play + sleep (baseline is strong)."]
        elif (lo, hi) == (5, 10):
            diag = ["Diet and screens begin their quiet takeover."]
            rx = ["Sugary snacks + more devices; less free play."]
        elif (lo, hi) == (10, 15):
            diag = ["Exercise narrows; sleep and attention slip."]
            rx = ["Convenience food rises; scrolling becomes normal."]
        elif (lo, hi) == (15, 20):
            diag = ["Identity shifts: performance → appearance → approval."]
            rx = ["Less unstructured movement; more sitting and snacking."]
        elif (lo, hi) == (20, 25):
            diag = ["Career entry: sleep debt and cheap calories."]
            rx = ["Gym is optional; “I’ll start later” becomes the plan."]
        elif (lo, hi) == (25, 30):
            diag = ["Stress ramps; coping becomes passive."]
            rx = ["Screen decompression replaces training; food quality declines."]
        elif (lo, hi) == (30, 35):
            diag = ["Body composition drifts; aches become background noise."]
            rx = ["Coffee and convenience run the day; movement becomes sporadic."]
        elif (lo, hi) == (35, 40):
            diag = ["Mood, sleep, and energy start wobbling."]
            rx = ["Short-term fixes; root causes stay unaddressed."]
        elif (lo, hi) == (40, 45):
            diag = ["Metabolic risk climbs quietly (BP, lipids, glucose)."]
            rx = ["More meds are discussed; exercise still inconsistent."]
        elif (lo, hi) == (45, 50):
            diag = ["The gap widens: time and stress squeeze healthy habits."]
            rx = ["Less strength and Zone 2; more sitting and compensating."]
        elif (lo, hi) == (50, 55):
            diag = ["Warning lights flicker — but life is busy."]
            rx = ["Checkups increase; training remains optional."]
        elif (lo, hi) == (55, 60):
            diag = ["Big diagnosis era (autoimmune, heart, cancer risk rises)."]
            rx = [
                "Procedures/meds; “maybe exercise now” arrives late.",
                "Some diet cleanup, but baseline fitness is limited.",
                "Financial stress and low purpose can amplify drift and coping.",
            ]
        elif (lo, hi) == (60, 65):
            diag = ["Capacity drops faster; recovery is slower."]
            rx = ["More specialists; less movement; fear of injury grows."]
        elif (lo, hi) == (65, 70):
            diag = ["Frailty risk rises: falls, weakness, isolation."]
            rx = ["Mobility work is reactive; strength is minimal."]
        elif (lo, hi) == (70, 75):
            diag = ["Independence narrows; “small problems” become big."]
            rx = ["Assistance increases; activity becomes avoidance."]
        elif (lo, hi) == (75, 77):
            diag = ["End-of-life window for the default path."]
            rx = ["Mobility is limited; dependence rises fast."]
        else:
            diag = ["Default-path drift continues."]
            rx = ["Reactive care; limited rebuild."]

        sal[k] = BucketNarrative(
            title="A Typical American Life",
            subheading=_sal_subheading(lo, hi),
            diagnosis=diag,
            prescription=rx,
        )

    # --- LRP: solid defaults + switchback emphasis ---
    def lrp_subheading(lo: int, hi: int) -> str:
        if hi <= 25:
            return "Build the identity early: “I move every day.”"
        if hi <= 55:
            return "Stay functional. Don’t drift."
        if (lo, hi) == (55, 60):
            return "Hitting the Switchback."
        if hi <= 65:
            return "Rebuild fast. Peak by ~60."
        if hi <= 80:
            return "Protect the peak."
        return "Finish functional."

    for lo, hi in bucket_edges_for_mode("LRP"):
        k = bucket_key(lo, hi)
        if (lo, hi) == (55, 60):
            diag = ["This is the conscious turn — trajectory becomes intentional."]
            rx = [
                "5-year rebuild: strength 2–3x/week + Zone 2 3x/week.",
                "Design environment: protein-first, steps, sleep, sunlight.",
                "Reduce financial stress + increase purpose to sustain change.",
            ]
        elif hi <= 55:
            diag = ["Mostly functional; drift kept in check."]
            rx = ["Strength + aerobic base stay non-negotiable.", "Protect sleep; limit screen-based coping."]
        elif hi <= 65:
            diag = ["Capacity rises quickly with consistency."]
            rx = ["Progressive strength; Zone 2 volume; mobility + balance."]
        elif hi <= 80:
            diag = ["Maintenance phase: prevent the slide."]
            rx = ["Keep intensity; prioritize power + balance; stay social."]
        else:
            diag = ["Longevity phase: independence is the goal."]
            rx = ["Strength minimums; daily walking; simplify essentials."]

        lrp[k] = BucketNarrative(
            title="Life Reclamation Path",
            subheading=lrp_subheading(lo, hi),
            diagnosis=diag,
            prescription=rx,
        )

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

    if a < SWITCHBACK_AGE:
        return clamp(20 - 0.45 * a, -100, 100)

    t = (a - SWITCHBACK_AGE) / 4.0
    lift = 85 * smoothstep(t)
    late = (a - 80) * 0.35 if a > 80 else 0.0
    s0 = 20 - 0.45 * SWITCHBACK_AGE
    return clamp(s0 + lift - late, -100, 100)


def build_df(mode: str) -> pd.DataFrame:
    end_age = end_age_for_mode(mode)
    ages = list(range(0, end_age + 1))
    rows = [{"age": a, "health": health_score(a, mode), "wealth": wealth_score(a, mode), "silo": silo_score(a, mode)} for a in ages]
    return pd.DataFrame(rows)


# -----------------------------
# Plot helpers
# -----------------------------
def add_end_marker(fig: go.Figure, end_age: int, y_top: float):
    fig.add_vline(x=end_age, line_width=2, opacity=0.5)
    fig.add_annotation(
        x=end_age,
        y=y_top,
        xanchor="right",
        yanchor="top",
        text=f"<b>End</b><br><span style='font-size:12px;opacity:0.75'>Age {end_age}</span>",
        showarrow=False,
        bgcolor="rgba(0,0,0,0.25)",
        bordercolor="rgba(255,255,255,0.14)",
        borderwidth=1,
        borderpad=6,
    )


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


def base_layout(fig: go.Figure, mode: str, y_title: str, y_range: List[int], show_switchback: bool, y_top_for_annotations: float):
    end_age = end_age_for_mode(mode)
    tickvals = x_ticks_for_mode(mode)

    if show_switchback:
        add_switchback(fig, y_top=y_top_for_annotations)

    add_end_marker(fig, end_age=end_age, y_top=y_top_for_annotations)

    fig.update_layout(
        height=430,
        margin=dict(l=30, r=20, t=15, b=25),
        xaxis=dict(title="Age", range=[0, end_age], tickmode="array", tickvals=tickvals),
        yaxis=dict(title=y_title, range=y_range),
        showlegend=False,
    )


def plot_health(df: pd.DataFrame, mode: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["age"], y=df["health"], mode="lines", line=dict(width=6),
                             hovertemplate="Age %{x}<br>Health: %{y:.1f}<extra></extra>"))

    # bands
    fig.add_hrect(y0=70, y1=100, opacity=0.10, line_width=0)
    fig.add_hrect(y0=45, y1=70, opacity=0.07, line_width=0)
    fig.add_hrect(y0=0, y1=45, opacity=0.10, line_width=0)

    # labels (left-ish)
    fig.add_annotation(x=1, y=95, text="<b>Fit</b>", showarrow=False, opacity=0.75)
    fig.add_annotation(x=1, y=58, text="<b>Functional</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=1, y=18, text="<b>Frail</b>", showarrow=False, opacity=0.75)

    base_layout(
        fig,
        mode=mode,
        y_title="Health (Fit → Frail)",
        y_range=[0, 100],
        show_switchback=(mode == "LRP"),
        y_top_for_annotations=100,
    )
    return fig


def plot_wealth(df: pd.DataFrame, mode: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["age"], y=df["wealth"], mode="lines", line=dict(width=6),
                             hovertemplate="Age %{x}<br>Wealth: %{y:.1f}<extra></extra>"))

    # bands
    fig.add_hrect(y0=70, y1=100, opacity=0.10, line_width=0)
    fig.add_hrect(y0=40, y1=70, opacity=0.07, line_width=0)
    fig.add_hrect(y0=0, y1=40, opacity=0.10, line_width=0)

    fig.add_annotation(x=1, y=95, text="<b>Rich</b>", showarrow=False, opacity=0.75)
    fig.add_annotation(x=1, y=55, text="<b>Enough</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=1, y=16, text="<b>Poor</b>", showarrow=False, opacity=0.75)

    base_layout(
        fig,
        mode=mode,
        y_title="Wealth (Poor → Rich)",
        y_range=[0, 100],
        show_switchback=(mode == "LRP"),
        y_top_for_annotations=100,
    )
    return fig


def plot_silo(df: pd.DataFrame, mode: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["age"], y=df["silo"], mode="lines", line=dict(width=6),
                             hovertemplate="Age %{x}<br>SILO: %{y:.0f}<extra></extra>"))
    fig.add_hline(y=0, line_width=2, opacity=0.65)

    fig.add_annotation(x=1, y=75, text="<b>Above ground</b>", showarrow=False, opacity=0.65)
    fig.add_annotation(x=1, y=-75, text="<b>Below ground</b>", showarrow=False, opacity=0.65)

    base_layout(
        fig,
        mode=mode,
        y_title="SILO (Below-ground → Above-ground)",
        y_range=[-100, 100],
        show_switchback=(mode == "LRP"),
        y_top_for_annotations=100,
    )
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
st.caption("Bucketed life chapters • SAL vs LRP • Tabs for clean labels")

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
- LRP only: Switchback at Age 55  
- SAL: Ends at Age 77
"""
    )

df = build_df(mode)
age_repr = bucket_midpoint(lo, hi)

row = df.loc[df["age"] == age_repr].iloc[0]
h, w, s = float(row["health"]), float(row["wealth"]), float(row["silo"])

key = bucket_key(lo, hi)
narr = (SAL_NARR if mode == "SAL" else LRP_NARR)[key]

# Header card
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
        st.plotly_chart(plot_health(df, mode), use_container_width=True)

    with tab_w:
        st.plotly_chart(plot_wealth(df, mode), use_container_width=True)

    with tab_s:
        # Primary: blocks (no line-first confusion)
        silo_blocks(df, mode=mode, active_lo=lo, active_hi=hi)

        # Optional: show the SILO trajectory line
        with st.expander("Show SILO trajectory line (optional)", expanded=False):
            st.plotly_chart(plot_silo(df, mode), use_container_width=True)

with right:
    # Bullets always shown and "locked" by bucket
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
