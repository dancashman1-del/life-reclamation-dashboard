import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="A Standard American Life — Health Timeline", page_icon="🧭", layout="wide")

# -----------------------------
# Background (parchment + faint mountains)
# -----------------------------
MOUNTAIN_SVG = """
<svg viewBox="0 0 1200 260" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
  <path d="M0,210
           C120,170 210,185 330,150
           C430,120 520,155 620,130
           C720,105 820,150 920,125
           C1020,100 1100,145 1200,120
           L1200,260 L0,260 Z"
        fill="rgba(0,0,0,0.06)"/>
  <path d="M0,235
           C140,205 260,230 360,195
           C470,160 560,215 680,175
           C790,140 900,220 1030,165
           C1110,130 1165,175 1200,155
           L1200,260 L0,260 Z"
        fill="rgba(0,0,0,0.09)"/>
</svg>
"""

def engine_svg(color_hex: str) -> str:
    return f"""
<svg width="46" height="46" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 18h18l4 6h6v8h-4l-2 6h-2v8H22v-6h-6v-8h4l2-6h2z"
        fill="{color_hex}" opacity="0.95"/>
  <path d="M24 28h16v16H24z" fill="white" opacity="0.25"/>
</svg>
"""

st.markdown(
    f"""
<style>
.stApp {{
  background:
    radial-gradient(900px 520px at 20% 0%, rgba(0,0,0,0.05), rgba(0,0,0,0.00) 60%),
    linear-gradient(180deg, #fbf7ef 0%, #f7f1e6 100%);
  color: #1f1f1f;
}}
.lrp-mountains {{
  position: fixed;
  left: 0; right: 0; bottom: -10px;
  height: 240px;
  pointer-events: none;
  opacity: 0.45;
  z-index: 0;
}}
.block-container {{
  position: relative;
  z-index: 1;
  padding-bottom: 160px;
  max-width: 1650px;
  padding-top: 1.2rem;
}}

.h1 {{
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -0.02em;
  text-align: center;
  margin: 6px 0 0 0;
}}
.sub {{
  text-align: center;
  font-size: 18px;
  opacity: 0.70;
  margin: 4px 0 10px 0;
}}

.card {{
  border-radius: 18px;
  background: rgba(255,255,255,0.93);
  border: 1px solid rgba(0,0,0,0.08);
  padding: 18px;
  box-shadow: 0 10px 28px rgba(0,0,0,0.06);
}}
.card h3 {{
  margin: 0 0 10px 0;
  font-size: 22px;
}}
.small {{
  font-size: 14px;
  opacity: 0.82;
}}

.bullets {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
  font-size: 18px;
  line-height: 1.25;
}}
.bullets .b {{
  display: flex;
  gap: 10px;
}}
.dot {{
  width: 9px;
  height: 9px;
  border-radius: 99px;
  background: rgba(0,0,0,0.55);
  margin-top: 8px;
  flex: 0 0 9px;
}}

/* Band nav: pull arrows close to the band label */
.bandbar {{
  display:flex;
  justify-content:center;
  align-items:center;
  gap: 10px;
  margin: 12px 0 14px 0;
}}
.bandpill {{
  font-size: 22px;
  font-weight: 850;
  min-width: 92px;
  text-align:center;
}}
.navbtn button {{
  border-radius: 14px !important;
  padding: 6px 12px !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
  background: rgba(255,255,255,0.92) !important;
}}

.hdr {{
  display:flex;
  align-items:center;
  gap: 10px;
}}
.hdr .ico {{
  width: 28px; height: 28px;
  display:flex; align-items:center; justify-content:center;
  border-radius: 8px;
  background: rgba(0,0,0,0.05);
  font-weight: 800;
}}

.kpi-title {{
  font-size: 20px;
  font-weight: 900;
  margin: 0;
}}
.kpi-row {{
  display:flex;
  gap: 14px;
  align-items:center;
}}
.kpi-sub {{
  font-size: 14px;
  opacity: 0.78;
  margin-top: 4px;
}}
.sep {{
  height:1px;
  background:rgba(0,0,0,0.08);
  margin: 14px 0;
}}
</style>

<div class="lrp-mountains">{MOUNTAIN_SVG}</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def band_label_for_age(age: int) -> str:
    a0 = (age // 5) * 5
    a1 = a0 + 5
    a0 = max(0, a0)
    a1 = min(95, a1)
    return f"{a0}-{a1}"

def label_zone(score: float):
    # zone categories used only for coloring now (text removed per your request)
    if score >= 70:
        return "#39b66a"  # green
    if score >= 40:
        return "#d6a400"  # yellow
    return "#c63b3b"      # red

def engine_status_from_age_for_sal(age: float):
    """
    SAL messaging per your instruction:
    - Yellow by ~20–25
    - Red by ~30–35
    Keep it largely age-driven (not fitness-driven), because it's biomarkers/risk drift.
    """
    if age < 22:
        return "Green", "#39b66a"
    if age < 33:
        return "Yellow", "#d6a400"
    return "Red", "#c63b3b"

# -----------------------------
# SAL curve: anchor points adjusted to your red sketch
# - ~Functional by ~50
# - steeper decline through 60s/70s
# -----------------------------
def sal_capacity(age: float) -> float:
    pts = np.array([
        [0,  88],
        [15, 86],
        [25, 80],
        [35, 73],
        [45, 66],
        [50, 55],  # roughly Functional by 50
        [55, 48],
        [60, 42],
        [65, 36],
        [70, 26],
        [75, 16],
        [77, 12],
    ], dtype=float)
    x = pts[:, 0]
    y = pts[:, 1]
    return float(np.interp(age, x, y))

# -----------------------------
# Stage content (placeholder)
# -----------------------------
LEFT_STAGE = {
    "45-50": ("Medicalized Living", [
        "Multiple medications begin; side effects stack quietly",
        "Sleep fragments; fatigue becomes baseline",
        "Movement becomes cautious; joints “protected”",
        "Pain management replaces performance",
    ]),
    "50-55": ("Medicalized Living", [
        "Multiple medications begin; side effects stack quietly",
        "Sleep fragments; fatigue becomes baseline",
        "Movement becomes cautious; joints “protected”",
        "Pain management replaces performance",
    ]),
}
RIGHT_STAGE = {
    "45-50": ("Managing conditions", "Adjust meds; reduce risk"),
    "50-55": ("Managing conditions", "Adjust meds; reduce risk"),
}

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="h1">A Standard American Life — Health Timeline</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">What happens if nothing intervenes</div>', unsafe_allow_html=True)

# -----------------------------
# Band navigation (arrows tight to band label)
# -----------------------------
if "age" not in st.session_state:
    st.session_state.age = 47  # in the 45–50 band

b1, b2, b3 = st.columns([1, 1, 1])
with b1:
    st.write("")
with b2:
    left_btn, band_mid, right_btn = st.columns([1, 2, 1])
    with left_btn:
        st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
        if st.button("←", key="prev_band"):
            st.session_state.age = max(5, st.session_state.age - 5)
        st.markdown("</div>", unsafe_allow_html=True)
    with band_mid:
        band = band_label_for_age(st.session_state.age)
        st.markdown(f"<div class='bandbar'><div class='bandpill'>{band}</div></div>", unsafe_allow_html=True)
    with right_btn:
        st.markdown("<div class='navbtn'>", unsafe_allow_html=True)
        if st.button("→", key="next_band"):
            st.session_state.age = min(92, st.session_state.age + 5)
        st.markdown("</div>", unsafe_allow_html=True)
with b3:
    st.write("")

age = st.session_state.age
band = band_label_for_age(age)

# -----------------------------
# Values (no UI controls)
# -----------------------------
conditioning = 0  # keep stable for now; later we’ll add LRP controls on the same row (right side)
base = sal_capacity(age)
zone_score = clamp(base + conditioning, 0, 100)
zone_color = label_zone(zone_score)

engine_name, engine_color = engine_status_from_age_for_sal(age)

# Copy
left_title, left_bullets = LEFT_STAGE.get(
    band,
    ("Standard Living", ["Placeholder bullet 1", "Placeholder bullet 2", "Placeholder bullet 3", "Placeholder bullet 4"])
)
diag_text, rx_text = RIGHT_STAGE.get(band, ("Managing conditions", "Adjust meds; reduce risk"))

# -----------------------------
# Layout (wider chart + tight sides)
# -----------------------------
colL, colC, colR = st.columns([1.0, 2.55, 1.0], gap="large")

with colL:
    bullets_html = "".join([f"<div class='b'><div class='dot'></div><div>{t}</div></div>" for t in left_bullets])
    st.markdown(
        f"""
<div class="card">
  <h3>{left_title}</h3>
  <div class="bullets">{bullets_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with colC:
    xs = np.arange(0, 78, 1)
    ys = np.array([sal_capacity(x) for x in xs])

    a0 = (age // 5) * 5
    seg_x = np.arange(a0, min(a0 + 5, 77) + 1, 1)
    seg_y = np.array([sal_capacity(x) for x in seg_x])

    fig, ax = plt.subplots(figsize=(10.6, 5.7), dpi=140)
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    # pale curve + red segment
    ax.plot(xs, ys, linewidth=3.8, color=(0.76, 0.54, 0.54, 0.55))
    ax.plot(seg_x, seg_y, linewidth=5.0, color=(0.67, 0.10, 0.10, 0.95))

    # end marker
    ax.axvline(77, linewidth=3.2, color=(0, 0, 0, 0.22))

    ax.set_xlim(0, 77)
    ax.set_ylim(0, 100)

    ax.set_xticks(list(range(0, 80, 5)))
    ax.set_xlabel("Age", fontsize=10, color=(0, 0, 0, 0.68))

    ax.set_yticks([20, 55, 85])
    ax.set_yticklabels(["Frail", "Functional", "Fit"], fontsize=10, color=(0, 0, 0, 0.68))

    ax.grid(False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color((0, 0, 0, 0.30))
    ax.spines["bottom"].set_color((0, 0, 0, 0.30))
    ax.tick_params(axis="x", colors=(0, 0, 0, 0.55), labelsize=8, length=0)
    ax.tick_params(axis="y", colors=(0, 0, 0, 0.55), labelsize=8, length=0)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.pyplot(fig, clear_figure=True)
    st.markdown("</div>", unsafe_allow_html=True)

with colR:
    st.markdown(
        f"""
<div class="card">
  <div class="hdr"><div class="ico">📋</div><h3 style="margin:0;">Diagnosis</h3></div>
  <div class="small" style="margin-top:8px; font-size:18px; opacity:0.9;">{diag_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="card">
  <div class="hdr"><div class="ico">℞</div><h3 style="margin:0;">Prescription</h3></div>
  <div class="small" style="margin-top:8px; font-size:18px; opacity:0.9;">{rx_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Combined: Check Engine + Fit Zone
    st.markdown(
        f"""
<div class="card">
  <div class="kpi-row">
    <div>{engine_svg(engine_color)}</div>
    <div>
      <p class="kpi-title">Check Engine</p>
      <div class="small" style="font-size:18px; font-weight:800;">
        <span style="color:{engine_color};">●</span> {engine_name}
      </div>
      <div class="kpi-sub">SAL: age-driven early; risk compounds later</div>
    </div>
  </div>

  <div class="sep"></div>

  <div class="kpi-row">
    <div style="width:44px;height:44px;border-radius:999px;background:{zone_color};opacity:0.92;"></div>
    <div>
      <p class="kpi-title">Fit Zone</p>
      <div class="kpi-sub">Zone score: <b>{zone_score:.1f}</b></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
