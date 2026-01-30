import streamlit as st
import plotly.graph_objects as go

# =========================
# AUTHORITATIVE TEXT SOURCE
# =========================
# Populated from: "Life Reclamation Project Health text for SAL and LRP Slides.docx"
# (Dan confirmed these docs are authoritative.)
BANDS = [{'a0': 0,
  'a1': 5,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Health is assumed and unexamined.',
  'bullets': ['Lots of unstructured play, exploration, and bonding with parents',
              'Sleep is mostly protected; routines feel supportive and calming',
              'Daycare schedules, frequent illness, and hand-offs begin to disrupt rhythm',
              'Screens are introduced occasionally to soothe, distract, or buy quiet'],
  'diagnosis': 'Everything looks normal and on track for age.',
  'prescription': 'Stay on schedule with the ~25 to 35 vaccinations. Use antibiotics and fever reducers when needed. Kids are resilient — there’s nothing to worry about.',
  'engine': 'green'},
 {'a0': 5,
  'a1': 10,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Activity is natural and effortless.',
  'bullets': ['Real play with friends is still common; movement happens naturally and joyfully',
              'A first sport or activity is introduced — with fruit snacks and juice boxes as the reward',
              'Screens and online entertainment increasingly fill “in-between” time',
              'Busy schedules lead to quicker meals and less intentional nutrition'],
  'diagnosis': 'Healthy growth and development within expected ranges.',
  'prescription': 'Keep doing what you’re doing. Encourage activity, limit treats when you can, and address issues as they come up.',
  'engine': 'green'},
 {'a0': 10,
  'a1': 15,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Structure increases, resilience masks cost.',
  'bullets': ['Organized sports and activities increase, but free play declines',
              'Screens, games, and phones begin to dominate downtime and social life',
              'Sleep duration and quality erodes due to early schedules and late-night stimulation',
              'Food choices tilt increasingly toward convenience and peer-influenced habits'],
  'diagnosis': 'Typical adolescent changes; fatigue, mood swings, and irregular sleep are common.',
  'prescription': 'Try to get enough sleep, eat reasonably well, and stay active when schedules allow. This phase usually passes.',
  'engine': 'green'},
 {'a0': 15,
  'a1': 20,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Activity stays high as recovery slips.',
  'bullets': ['Fitness takes a back seat, with perhaps one school sport remaining as the last truly demanding activity',
              'Sleep erodes further due to school demands, increased screen time, and social schedules',
              'Caffeine, sugar, and ultra-processed foods are used to manage energy and stress',
              'Strength training, cardio, and recovery, that were never foundational, slip even further away'],
  'diagnosis': 'Occasional bouts of anxiety, low mood, and emotional volatility are considered normal at this age. Plus weight gain.',
  'prescription': 'Try reducing screen time, get some fresh air, and manage stress. Revisit if problems persist or worsen.',
  'engine': 'yellow'},
 {'a0': 20,
  'a1': 25,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Movement is quietly replaced.',
  'bullets': ['Physical activity declines sharply as college and early career demands dominate daily life',
              'Long hours seated at a laptop replace movement, with posture and mobility beginning to suffer',
              'Sleep irregularities worsen due to deadlines, online social demands, and screen exposure',
              'Convenience foods, caffeine, and snacks are used to sustain focus and productivity while alcohol is used to unwind and decompress'],
  'diagnosis': 'Young and generally healthy despite irregular routines.',
  'prescription': 'Focus on stress management. Eat right when you can, stay active when possible, and don’t worry too much — you’re young!',
  'engine': 'yellow'},
 {'a0': 25,
  'a1': 30,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Health competes with productivity.',
  'bullets': ['Fitness becomes sporadic, squeezed in only when time and energy allow',
              'Long hours sitting at work carry over into evenings and weekends',
              'Along with weight gain, minor aches and stiffness appear, but are dismissed as temporary or stress-related',
              'Sleep and nutrition are traded for productivity, convenience, social life, and more routine alcohol use'],
  'diagnosis': 'Lifestyle strain and weight gain is noted, but nothing is outside normal expectations.',
  'prescription': 'Try to eat better, exercise more, and get more sleep. Small changes add up.',
  'engine': 'yellow'},
 {'a0': 30,
  'a1': 35,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': '“I’ll get back to it later.”',
  'bullets': ['Career and family demands make any attempt at consistent training feel nearly impossible',
              'Sitting, stress, and mental load dominate most days',
              'Weight gain, stiffness, and recurring pain accelerates',
              'Health is managed reactively, with plans to “get back on track” later'],
  'diagnosis': 'Weight gain, fatigue, and aches are typical at this stage of life.',
  'prescription': 'Work on balance. Lose a little weight if you can, be more active when time allows.',
  'engine': 'yellow'},
 {'a0': 35,
  'a1': 40,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Stress and decline feel ordinary.',
  'bullets': ['Work and family responsibilities and distractions consume most discretionary time',
              'Chronic stress, decreased productivity and long hours accumulate',
              'Lingering pain and fatigue is ever present',
              'Health is discussed more than acted upon'],
  'diagnosis': 'Cumulative stress effects are apparent, though labs remain acceptable.',
  'prescription': 'Continue monitoring. Lifestyle changes may help if symptoms worsen.',
  'engine': 'yellow'},
 {'a0': 40,
  'a1': 45,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Warning lights flicker.',
  'bullets': ['Energy and resilience decline is becoming pronounced',
              'Blood pressure, cholesterol, and weight creep ever upward',
              'Exercise remains aspirational, never habitual',
              'Health is outsourced to annual checkups, and red flag deferrals'],
  'diagnosis': 'Risk factors are emerging, but consistent with “normal aging.”',
  'prescription': 'Watch the numbers. Eat right, exercise more, and we’ll recheck next year.',
  'engine': 'yellow'},
 {'a0': 45,
  'a1': 50,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Prevention gives way to control.',
  'bullets': ['Health concerns feel more personal as peers face diagnoses',
              'Medications or guidance are introduced',
              'Physical activity is cautiously introduced but dropped',
              'Capacity continues to decline'],
  'diagnosis': 'Blood pressure, cholesterol, or weight are trending upward.',
  'prescription': 'Try diet and exercise first. If trends continue, medication can help.',
  'engine': 'orange'},
 {'a0': 50,
  'a1': 55,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Comfort replaces capability.',
  'bullets': ['Daily routines adjust to avoid discomfort',
              'Strength, balance, and power have diminished greatly',
              'Travel and hobbies are chosen with limits in mind',
              'Health decisions prioritize symptom control'],
  'diagnosis': 'Age-related functional decline is within expected limits.',
  'prescription': 'Adjust activities to what you can do. Avoid overdoing it.',
  'engine': 'orange'},
 {'a0': 55,
  'a1': 60,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Decline steepens.',
  'bullets': ['Strength and stamina drop faster than expected',
              'Pain and chronic conditions shape daily choices',
              'Exercise becomes “therapy,” not growth',
              'Independence remains, but health is fading, shrinking'],
  'diagnosis': 'Early chronic conditions such as prediabetes or hypertension are identified.',
  'prescription': 'Begin standard medical therapy. Focus on compliance and monitoring.',
  'engine': 'red'},
 {'a0': 60,
  'a1': 65,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Effort carries a cost.',
  'bullets': ['Independence persists, but effort requires planning',
              'Strength and aerobic capacity have eroded',
              'Medications are routine',
              'Activities are chosen to minimize falls and fractures'],
  'diagnosis': 'We are doing what we can. Multiple risk factors have pharmaceutical answers.',
  'prescription': 'Prioritize safety and consistency.',
  'engine': 'red'},
 {'a0': 65,
  'a1': 70,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Confidence fades.',
  'bullets': ['Physical confidence declines',
              'Recovery becomes unreliable',
              'Medications expand',
              'Daily choices prioritize safety'],
  'diagnosis': 'Declined strength is attributed to normal aging.',
  'prescription': 'Simplify routines. Avoid injury.',
  'engine': 'red'},
 {'a0': 70,
  'a1': 75,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Risk becomes central.',
  'bullets': ['Restricting daily activities, outings, or hobbies around limited energy levels',
              'Independence relies on complex, daily medication management with side effects',
              'Bone density is greatly reduced while minor scrapes or bruises take longer to heal',
              'Recovery from illness or injury requires a longer-term rest or physical therapy'],
  'diagnosis': 'Falls and slower recovery are expected at this age.',
  'prescription': 'Use assistive devices. Modify living space.',
  'engine': 'red'},
 {'a0': 75,
  'a1': 77,
  'slide_title': 'HEALTH · STANDARD AMERICAN LIFE',
  'word': 'health',
  'pos': 'noun',
  'phon': '/helTH/',
  'def1': 'the absence of disease or infirmity',
  'def2': 'also: the capacity to live, move, and engage fully with life',
  'heading': 'Decline ends abruptly.',
  'bullets': ['Multiple health conditions (heart disease, diabetes, dementia) are likely to coexist and interact, complicating treatment and recovery',
              'Rapid reduction in strength, walking speed, and overall energy levels makes daily activities extremely hard',
              'The failing immune system turns minor illness into life threatening pneumonia or sepsis',
              'A prolonged homebound or nursing-home physical decline ends in Death'],
  'diagnosis': 'Serious illness or injury is common.',
  'prescription': 'Hospitalization, rehab, or hospice. Focus on comfort.',
  'engine': 'red'}]

# -------------------------
# App config
# -------------------------
st.set_page_config(page_title="LRP • Health (SAL)", layout="wide")

# -------------------------
# Minimal CSS (aims to fit at 100% zoom as well as possible)
# -------------------------
st.markdown(
    """
<style>
/* Give enough top padding so nothing clips */
.block-container { padding-top: 1.7rem; padding-bottom: 1.2rem; max-width: 1500px; }

/* Cards */
.lrp-card {
  background: rgba(255,255,255,0.96);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  padding: 18px 18px 16px 18px;
}

.lrp-title {
  font-weight: 800;
  letter-spacing: 0.5px;
  font-size: 26px;
  margin-bottom: 10px;
}

.lrp-dictword {
  font-size: 22px;
  font-weight: 800;
  margin-top: 6px;
}
.lrp-pos {
  font-size: 14px;
  color: rgba(0,0,0,0.55);
  font-weight: 600;
  margin-left: 8px;
}
.lrp-phon {
  font-size: 18px;
  color: rgba(0,0,0,0.50);
  margin-top: 6px;
  font-style: italic;
}
.lrp-def {
  font-size: 16px;
  margin-top: 10px;
  line-height: 1.35;
}
.lrp-defnum {
  color: rgba(0,0,0,0.55);
  font-weight: 800;
  display: inline-block;
  width: 26px;
}

.lrp-heading {
  font-size: 20px;
  font-weight: 900;
  margin: 0 0 10px 0;
}

.lrp-bullets {
  font-size: 15px;
  line-height: 1.4;
}
.lrp-bullets ul {
  margin: 0;
  padding-left: 18px;
}
.lrp-bullets li {
  margin: 6px 0;
}

/* Left diagnosis card */
.lrp-label {
  font-weight: 900;
  letter-spacing: 0.6px;
  font-size: 12px;
  color: rgba(0,0,0,0.55);
  margin-top: 6px;
  text-transform: uppercase;
  display:flex;
  align-items:center;
  gap:10px;
}
.lrp-body {
  font-size: 15px;
  line-height: 1.45;
  margin-top: 6px;
  margin-bottom: 10px;
}

/* Icons */
.lrp-ico {
  font-size: 26px;
  width: 30px;
  text-align: center;
}
.engine-svg {
  width: 64px;
  height: 64px;
}

/* Navigation */
.ages-label {
  font-size: 22px;
  font-weight: 900;
  text-align:center;
  margin-top: 10px;
}
.dots {
  display:flex;
  justify-content:center;
  gap: 6px;
  margin-top: 8px;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(0,0,0,0.18);
}
.dot.active {
  background: #d11a1a;
}

/* Plot container tweak */
.plot-card {
  padding: 10px 14px 6px 14px;
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------
# Session state
# -------------------------
if "idx" not in st.session_state:
    st.session_state.idx = 0

# -------------------------
# Helpers
# -------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def engine_svg(color_key: str) -> str:
    palette = {
        "green": "#17a34a",
        "yellow": "#f59e0b",
        "orange": "#f97316",
        "red": "#ef4444",
    }
    c = palette.get(color_key, "#17a34a")
    # Bigger engine, no outer circle
    return f"""
<svg class="engine-svg" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-label="Check engine">
  <rect x="10" y="20" width="44" height="26" rx="6" fill="{c}" opacity="0.18"/>
  <path d="M22 22h20c3 0 6 3 6 6v12c0 3-3 6-6 6H22c-3 0-6-3-6-6V28c0-3 3-6 6-6z" fill="{c}"/>
  <path d="M18 30h-6v10h6" fill="{c}"/>
  <path d="M52 30h6v10h-6" fill="{c}"/>
  <rect x="26" y="28" width="12" height="12" rx="2" fill="white" opacity="0.92"/>
  <path d="M26 18h12v4H26z" fill="{c}"/>
  <path d="M28 46h8v4h-8z" fill="{c}"/>
</svg>
"""

def dots_html(active_idx: int, n: int) -> str:
    dots = []
    for i in range(n):
        cls = "dot active" if i == active_idx else "dot"
        dots.append(f'<div class="{cls}"></div>')
    return '<div class="dots">' + "".join(dots) + "</div>"

def health_curve_points():
    # y-scale: Fit ~3, Functional ~2, Frail ~1
    # Tuned so that ~55 is near the Functional/Frail boundary (slightly above Frail).
    return [
        (0, 2.92),
        (10, 2.92),
        (25, 2.70),
        (40, 2.35),
        (55, 2.06),
        (65, 1.85),
        (77, 1.62),
        (92, 1.22),
    ]

def build_health_fig(x_end: float):
    pts = health_curve_points()

    # Build red segment (0 -> x_end) by clipping curve
    xs = []
    ys = []
    for (x, y) in pts:
        if x <= x_end:
            xs.append(x); ys.append(y)
        else:
            break

    # Ensure we end exactly at x_end (linear interpolation on the next segment)
    if x_end > xs[-1]:
        # find the next point
        next_idx = len(xs)
        if next_idx < len(pts):
            x0, y0 = xs[-1], ys[-1]
            x1, y1 = pts[next_idx]
            if x1 != x0 and x_end < x1:
                t = (x_end - x0) / (x1 - x0)
                xs.append(x_end)
                ys.append(y0 + t * (y1 - y0))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="lines",
        line=dict(color="#d11a1a", width=6, shape="spline", smoothing=0.7),
        hoverinfo="skip",
        name="Health (current)"
    ))

    tickvals = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,77,80,85,90,92]
    ticktext = [f"<b>{v}</b>" if v in (77,92) else str(v) for v in tickvals]

    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=16, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )

    fig.update_xaxes(
        range=[0, 92],
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        title_text="Age",
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor="rgba(0,0,0,0.24)",
        ticks="outside",
        tickfont=dict(size=12, color="rgba(0,0,0,0.55)"),
        titlefont=dict(size=14, color="rgba(0,0,0,0.55)"),
    )

    fig.update_yaxes(
        range=[0.9, 3.1],
        tickmode="array",
        tickvals=[3,2,1],
        ticktext=["Fit","Functional","Frail"],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.06)",
        showline=True,
        linewidth=1,
        linecolor="rgba(0,0,0,0.24)",
        ticks="",
        tickfont=dict(size=13, color="rgba(0,0,0,0.55)"),
    )

    return fig

# -------------------------
# Navigation controls
# -------------------------
def prev():
    st.session_state.idx = clamp(st.session_state.idx - 1, 0, len(BANDS)-1)

def next_():
    st.session_state.idx = clamp(st.session_state.idx + 1, 0, len(BANDS)-1)

# -------------------------
# Render
# -------------------------
b = BANDS[st.session_state.idx]

col1, col2, col3 = st.columns([1.65, 0.90, 1.45], gap="large")

with col1:
    st.markdown(
        f"""
<div class="lrp-card">
  <div class="lrp-title">{b["slide_title"]}</div>

  <div class="lrp-dictword">
    {b["word"]} <span class="lrp-pos">· {b["pos"]}</span>
  </div>
  <div class="lrp-phon">{b["phon"]}</div>

  <div class="lrp-def"><span class="lrp-defnum">1)</span> {b["def1"]}</div>
  <div class="lrp-def"><span class="lrp-defnum">2)</span> {b["def2"]}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown('<div class="lrp-card">', unsafe_allow_html=True)
    cprev, cnext = st.columns(2)
    with cprev:
        st.button("◀ Previous", on_click=prev, use_container_width=True, disabled=(st.session_state.idx==0))
    with cnext:
        st.button("Next ▶", on_click=next_, use_container_width=True, disabled=(st.session_state.idx==len(BANDS)-1))
    st.markdown(f'<div class="ages-label">Ages {b["a0"]}–{b["a1"]}</div>', unsafe_allow_html=True)
    st.markdown(dots_html(st.session_state.idx, len(BANDS)), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    bullets_html = "<ul>" + "".join([f"<li>{x}</li>" for x in b["bullets"]]) + "</ul>"
    st.markdown(
        f"""
<div class="lrp-card">
  <div class="lrp-heading">{b["heading"]}</div>
  <div class="lrp-bullets">{bullets_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

left, right = st.columns([1.1, 2.9], gap="large")

with left:
    st.markdown(
        f"""
<div class="lrp-card">
  <div class="lrp-label"><span class="lrp-ico">🩺</span>DIAGNOSIS</div>
  <div class="lrp-body">{b["diagnosis"]}</div>

  <div class="lrp-label" style="margin-top:12px;"><span class="lrp-ico">💊</span>PRESCRIPTION</div>
  <div class="lrp-body">{b["prescription"]}</div>

  <div class="lrp-label" style="margin-top:12px;"><span class="lrp-ico">🛠️</span>CHECK ENGINE</div>
  <div style="margin-top:8px;">
    {engine_svg(b["engine"])}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

with right:
    st.markdown('<div class="lrp-card plot-card">', unsafe_allow_html=True)
    # Red line grows cumulatively: show up to END of current band.
    fig = build_health_fig(b["a1"])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
