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

    # Ensure we end exactly at x_end (linear interpolation on next segment)
    if x_end > xs[-1]:
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
    ticktext = [str(v) for v in tickvals]  # NO HTML

    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=16, b=46),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        font=dict(color="rgba(0,0,0,0.55)")
    )

    fig.update_xaxes(
        range=[0, 92],
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        title=dict(text="Age", font=dict(size=14, color="rgba(0,0,0,0.55)")),
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor="rgba(0,0,0,0.24)",
        ticks="outside",
        tickfont=dict(size=12, color="rgba(0,0,0,0.55)"),
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

    # OPTIONAL: visually emphasize 77 and 92 without tick HTML
    fig.add_annotation(x=77, y=0.92, text="<b>77</b>", showarrow=False, yshift=-18)
    fig.add_annotation(x=92, y=0.92, text="<b>92</b>", showarrow=False, yshift=-18)

    return fig
