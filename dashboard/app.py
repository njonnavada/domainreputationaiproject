import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.orchestrator import DomainReputationOrchestrator

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Domain Reputation AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .main-header h1 { color: #ffffff; font-size: 2rem; font-weight: 700; margin: 0; }
  .main-header p  { color: #a0aec0; font-size: 0.95rem; margin: 0.3rem 0 0 0; }
  .zeta-badge {
    background: linear-gradient(135deg, #e94560, #c62a47);
    color: white; padding: 0.4rem 1rem;
    border-radius: 20px; font-size: 0.8rem; font-weight: 600;
    letter-spacing: 1px;
  }

  .metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.2s;
  }
  .metric-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
  .metric-value      { font-size: 2rem; font-weight: 700; margin: 0.2rem 0; }
  .metric-label      { color: #718096; font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
  .metric-delta      { font-size: 0.78rem; margin-top: 0.3rem; }

  .status-badge-good    { background:#d4edda; color:#155724; padding:0.6rem 1.4rem; border-radius:30px; font-weight:700; font-size:1.1rem; display:inline-block; }
  .status-badge-average { background:#fff3cd; color:#856404; padding:0.6rem 1.4rem; border-radius:30px; font-weight:700; font-size:1.1rem; display:inline-block; }
  .status-badge-bad     { background:#f8d7da; color:#721c24; padding:0.6rem 1.4rem; border-radius:30px; font-weight:700; font-size:1.1rem; display:inline-block; }

  .issue-critical { background:#fff5f5; border-left:4px solid #e53e3e; padding:0.9rem 1.2rem; border-radius:0 8px 8px 0; margin:0.5rem 0; }
  .issue-warning  { background:#fffaf0; border-left:4px solid #dd6b20; padding:0.9rem 1.2rem; border-radius:0 8px 8px 0; margin:0.5rem 0; }
  .issue-info     { background:#ebf8ff; border-left:4px solid #3182ce; padding:0.9rem 1.2rem; border-radius:0 8px 8px 0; margin:0.5rem 0; }
  .issue-title    { font-weight:600; font-size:0.92rem; margin-bottom:0.25rem; }
  .issue-detail   { font-size:0.82rem; color:#4a5568; }

  .rec-card {
    background:#ffffff; border:1px solid #e2e8f0;
    border-radius:10px; padding:1rem 1.2rem; margin:0.4rem 0;
    display:flex; align-items:flex-start; gap:0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  }
  .rec-rank   { background:#0f3460; color:white; width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; flex-shrink:0; }
  .rec-action { font-size:0.88rem; font-weight:500; color:#2d3748; }
  .rec-meta   { font-size:0.75rem; color:#718096; margin-top:0.2rem; }
  .tag        { display:inline-block; padding:0.15rem 0.5rem; border-radius:4px; font-size:0.7rem; font-weight:600; margin-right:0.3rem; }
  .tag-high   { background:#fed7d7; color:#c53030; }
  .tag-medium { background:#feebc8; color:#c05621; }
  .tag-low    { background:#bee3f8; color:#2b6cb0; }
  .tag-effort-low    { background:#c6f6d5; color:#276749; }
  .tag-effort-medium { background:#fefcbf; color:#744210; }
  .tag-effort-high   { background:#fed7d7; color:#c53030; }

  .positive-item { background:#f0fff4; border-left:3px solid #38a169; padding:0.6rem 1rem; border-radius:0 6px 6px 0; margin:0.3rem 0; font-size:0.85rem; color:#276749; }
  .section-title { font-size:1.1rem; font-weight:700; color:#1a202c; margin:1.2rem 0 0.8rem 0; padding-bottom:0.4rem; border-bottom:2px solid #e2e8f0; }
  .data-source-badge { font-size:0.75rem; padding:0.2rem 0.6rem; border-radius:10px; }
  .source-api  { background:#c6f6d5; color:#276749; }
  .source-mock { background:#bee3f8; color:#2b6cb0; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div>
    <h1>🛡️ Domain Reputation AI</h1>
    <p>Multi-agent system for email domain health classification, diagnosis & recommendations</p>
  </div>
  <div class="zeta-badge">ZETA GLOBAL</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
_thresholds_path = Path(__file__).parent.parent / "config" / "thresholds.json"
with open(_thresholds_path) as f:
    default_thresholds = json.load(f)["thresholds"]

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    st.markdown("### 📅 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=datetime.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To", value=datetime.today())

    st.markdown("---")
    st.markdown("### 🎛️ Reputation Thresholds")
    st.caption("Drag sliders to customize what qualifies as GOOD vs AVERAGE.")

    custom_thresholds = {}

    with st.expander("📬 Open Rate (%)", expanded=False):
        good_or = st.slider("Good ≥", 5.0, 50.0, float(default_thresholds["open_rate"]["good"]), 0.5, key="or_good")
        avg_or  = st.slider("Average ≥", 1.0, float(good_or - 0.5), float(default_thresholds["open_rate"]["average"]), 0.5, key="or_avg")
        custom_thresholds["open_rate"] = {"good": good_or, "average": avg_or}

    with st.expander("👤 Genuine Open Rate (%)", expanded=False):
        good_gor = st.slider("Good ≥", 5.0, 40.0, float(default_thresholds["genuine_open_rate"]["good"]), 0.5, key="gor_good")
        avg_gor  = st.slider("Average ≥", 1.0, float(good_gor - 0.5), float(default_thresholds["genuine_open_rate"]["average"]), 0.5, key="gor_avg")
        custom_thresholds["genuine_open_rate"] = {"good": good_gor, "average": avg_gor}

    with st.expander("🖱️ Click Rate (%)", expanded=False):
        good_cr = st.slider("Good ≥", 0.5, 10.0, float(default_thresholds["click_rate"]["good"]), 0.1, key="cr_good")
        avg_cr  = st.slider("Average ≥", 0.1, float(good_cr - 0.1), float(default_thresholds["click_rate"]["average"]), 0.1, key="cr_avg")
        custom_thresholds["click_rate"] = {"good": good_cr, "average": avg_cr}

    with st.expander("📦 Delivery Rate (%)", expanded=False):
        good_dr = st.slider("Good ≥", 85.0, 99.9, float(default_thresholds["delivery_rate"]["good"]), 0.5, key="dr_good")
        avg_dr  = st.slider("Average ≥", 75.0, float(good_dr - 0.5), float(default_thresholds["delivery_rate"]["average"]), 0.5, key="dr_avg")
        custom_thresholds["delivery_rate"] = {"good": good_dr, "average": avg_dr}

    with st.expander("🚨 Abuse / Spam Rate (%)", expanded=False):
        good_ar = st.slider("Good ≤", 0.01, 1.0, float(default_thresholds["abuse_rate"]["good"]), 0.01, key="ar_good")
        avg_ar  = st.slider("Average ≤", float(good_ar + 0.01), 2.0, float(default_thresholds["abuse_rate"]["average"]), 0.01, key="ar_avg")
        custom_thresholds["abuse_rate"] = {"good": good_ar, "average": avg_ar}

    with st.expander("📤 Hard Bounce Rate (%)", expanded=False):
        good_hr = st.slider("Good ≤", 0.5, 5.0, float(default_thresholds["hard_error_rate"]["good"]), 0.5, key="hr_good")
        avg_hr  = st.slider("Average ≤", float(good_hr + 0.5), 15.0, float(default_thresholds["hard_error_rate"]["average"]), 0.5, key="hr_avg")
        custom_thresholds["hard_error_rate"] = {"good": good_hr, "average": avg_hr}

    with st.expander("🚪 Unsubscribe Rate (%)", expanded=False):
        good_ur = st.slider("Good ≤", 0.1, 1.0, float(default_thresholds["unsub_rate"]["good"]), 0.1, key="ur_good")
        avg_ur  = st.slider("Average ≤", float(good_ur + 0.1), 3.0, float(default_thresholds["unsub_rate"]["average"]), 0.1, key="ur_avg")
        custom_thresholds["unsub_rate"] = {"good": good_ur, "average": avg_ur}

    st.markdown("---")
    if st.button("↺ Reset to Defaults", use_container_width=True):
        st.rerun()

# ── Demo hint ─────────────────────────────────────────────────────────────────
with st.expander("💡 Demo Domains — click to copy a domain name for testing", expanded=False):
    st.markdown("Use these pre-configured domains to see each reputation state:")
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.markdown("**❌ BAD Reputation**")
        for d in ["bad-reputation.com", "bounce-heavy.net", "spammy-sender.org"]:
            st.code(d, language=None)
    with dc2:
        st.markdown("**⚠️ AVERAGE Reputation**")
        for d in ["mid-tier-mail.com", "average-domain.net"]:
            st.code(d, language=None)
    with dc3:
        st.markdown("**✅ GOOD Reputation**")
        for d in ["great-sender.com", "healthy-domain.net", "top-performer.org"]:
            st.code(d, language=None)
    st.caption("Any other domain name will also work — results vary based on domain name.")

# ── Main Input ────────────────────────────────────────────────────────────────
st.markdown("### 🔍 Analyze a Domain")
col_inp, col_btn = st.columns([4, 1])
with col_inp:
    domain_input = st.text_input("", placeholder="e.g.  bad-reputation.com", label_visibility="collapsed")
with col_btn:
    analyze_clicked = st.button("Analyze →", type="primary", use_container_width=True)

# ── Batch Analysis ────────────────────────────────────────────────────────────
with st.expander("📋 Batch Analysis — analyze multiple domains at once"):
    bulk_text = st.text_area(
        "Enter one domain per line", height=120,
        placeholder="bad-reputation.com\nmid-tier-mail.com\ngreat-sender.com",
    )
    run_batch = st.button("Run Batch Analysis", type="secondary")

# ── Helper functions ──────────────────────────────────────────────────────────
def gauge_chart(score: float, label: str, color: str) -> go.Figure:
    color_map = {"green": ["#48bb78", "#38a169"], "orange": ["#ed8936", "#dd6b20"], "red": ["#fc8181", "#e53e3e"]}
    c = color_map.get(color, color_map["green"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        delta={"reference": 70, "valueformat": ".1f"},
        number={"suffix": "/100", "font": {"size": 36, "color": "#1a202c"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cbd5e0"},
            "bar":  {"color": c[1], "thickness": 0.25},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  40], "color": "#fff5f5"},
                {"range": [40, 70], "color": "#fffaf0"},
                {"range": [70, 100],"color": "#f0fff4"},
            ],
            "threshold": {"line": {"color": c[0], "width": 4}, "thickness": 0.75, "value": score},
        },
        title={"text": f"<b>{label}</b>", "font": {"size": 16, "color": "#4a5568"}},
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor="white")
    return fig


def radar_chart(metric_scores: dict) -> go.Figure:
    labels = [k.replace("_", " ").title() for k in metric_scores]
    values = list(metric_scores.values())
    values.append(values[0])
    labels.append(labels[0])
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill="toself",
        fillcolor="rgba(15,52,96,0.15)", line=dict(color="#0f3460", width=2),
        marker=dict(size=6, color="#0f3460"),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10))),
        showlegend=False, height=320,
        margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor="white",
    )
    return fig


def render_metrics_cards(metrics: dict):
    cols = st.columns(4)
    cards = [
        ("📬 Open Rate",         f"{metrics['open_rate']}%",         metrics['open_rate'],         20, True),
        ("👤 Genuine Open Rate", f"{metrics['genuine_open_rate']}%",  metrics['genuine_open_rate'], 15, True),
        ("🖱️ Click Rate",       f"{metrics['click_rate']}%",         metrics['click_rate'],         2, True),
        ("📦 Delivery Rate",    f"{metrics['delivery_rate']}%",      metrics['delivery_rate'],      95, True),
        ("🚨 Abuse Rate",       f"{metrics['abuse_rate']}%",         metrics['abuse_rate'],         0.1,False),
        ("📤 Hard Bounce",      f"{metrics['hard_error_rate']}%",    metrics['hard_error_rate'],    2,  False),
        ("🚪 Unsub Rate",       f"{metrics['unsub_rate']}%",         metrics['unsub_rate'],         0.5,False),
        ("📊 Total Sent",       f"{metrics['total_sent']:,}",        None,                          None,None),
    ]
    for i, (label, value, val, threshold, higher) in enumerate(cards):
        with cols[i % 4]:
            if val is not None and threshold is not None:
                if higher:
                    color = "#38a169" if val >= threshold else ("#dd6b20" if val >= threshold * 0.5 else "#e53e3e")
                else:
                    color = "#38a169" if val <= threshold else ("#dd6b20" if val <= threshold * 3 else "#e53e3e")
            else:
                color = "#0f3460"
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value" style="color:{color}">{value}</div>
            </div>""", unsafe_allow_html=True)


def render_diagnosis(diagnosis: dict):
    st.markdown('<div class="section-title">🩺 Diagnosis — Root Cause Analysis</div>', unsafe_allow_html=True)

    severity_icons = {"critical": "🔴", "warning": "🟠", "info": "🔵"}
    severity_labels= {"critical": "CRITICAL", "warning": "WARNING", "info": "INFO"}

    if not diagnosis["issues"]:
        st.success("✅ No significant issues detected. Domain reputation looks healthy!")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Issues",     diagnosis["issue_count"])
        c2.metric("Critical",         diagnosis["critical_count"], delta=None)
        c3.metric("Warnings",         diagnosis["warning_count"])

        st.markdown("<br>", unsafe_allow_html=True)
        for issue in diagnosis["issues"]:
            css_class = f"issue-{issue['severity']}"
            icon = severity_icons.get(issue["severity"], "⚪")
            badge = severity_labels.get(issue["severity"], "INFO")
            st.markdown(f"""
            <div class="{css_class}">
              <div class="issue-title">{icon} [{badge}] {issue['reason']}</div>
              <div class="issue-detail">{issue['detail']} &nbsp;|&nbsp; <b>Current value:</b> {issue['value']}%</div>
            </div>""", unsafe_allow_html=True)

    if diagnosis["positives"]:
        st.markdown("<br>**✅ What's working well:**", unsafe_allow_html=True)
        for pos in diagnosis["positives"]:
            st.markdown(f'<div class="positive-item">✅ {pos["message"]}</div>', unsafe_allow_html=True)


def render_recommendations(rec_data: dict):
    st.markdown('<div class="section-title">💡 Recommendations — Action Plan</div>', unsafe_allow_html=True)

    if not rec_data["recommendations"]:
        st.success("No specific actions needed at this time.")
        return

    tab1, tab2, tab3 = st.tabs([
        f"📋 All Actions ({rec_data['total']})",
        f"🔥 Critical First ({len(rec_data['critical_actions'])})",
        f"⚡ Quick Wins ({len(rec_data['quick_wins'])})"
    ])

    def _render_recs(recs):
        impact_tag = {"High": "tag-high", "Medium": "tag-medium", "Low": "tag-low"}
        effort_tag = {"Low": "tag-effort-low", "Medium": "tag-effort-medium", "High": "tag-effort-high"}
        for r in recs:
            it = impact_tag.get(r["impact"], "tag-low")
            et = effort_tag.get(r["effort"], "tag-effort-medium")
            st.markdown(f"""
            <div class="rec-card">
              <div class="rec-rank">{r['rank']}</div>
              <div>
                <div class="rec-action">{r['action']}</div>
                <div class="rec-meta">
                  <span class="tag {it}">Impact: {r['impact']}</span>
                  <span class="tag {et}">Effort: {r['effort']}</span>
                  <span style="color:#718096;font-size:0.72rem;">
                    {r['metric'].replace('_',' ').title()}
                  </span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    with tab1:
        _render_recs(rec_data["recommendations"])
    with tab2:
        _render_recs(rec_data["critical_actions"]) if rec_data["critical_actions"] else st.info("No critical actions.")
    with tab3:
        _render_recs(rec_data["quick_wins"]) if rec_data["quick_wins"] else st.info("No quick wins identified.")


def render_full_result(result: dict):
    m   = result["metrics"]
    cls = result["classification"]

    # ── Top row: gauge + status + radar ──────────────────────────────────────
    source_cls   = "source-api" if result["data_source"] == "api" else "source-mock"
    source_label = "Live API" if result["data_source"] == "api" else "Demo Data"

    col_g, col_s, col_r = st.columns([1, 1, 1])

    with col_g:
        st.plotly_chart(gauge_chart(cls["overall_score"], "Reputation Score", cls["color"]), use_container_width=True)

    with col_s:
        st.markdown("<br><br>", unsafe_allow_html=True)
        badge_cls = f"status-badge-{cls['label'].lower()}"
        st.markdown(f"""
        <div style="text-align:center">
          <div style="font-size:0.85rem;color:#718096;margin-bottom:0.5rem;">OVERALL STATUS</div>
          <div class="{badge_cls}">{cls['emoji']} {cls['label']}</div>
          <br>
          <span class="data-source-badge {source_cls}">📡 {source_label}</span>
          <br><br>
          <div style="font-size:0.82rem;color:#4a5568">
            <b>Domain:</b> {result['domain']}<br>
            <b>Period:</b> {result['start_date']} → {result['end_date']}<br>
            <b>Score:</b> {cls['overall_score']} / 100
          </div>
        </div>""", unsafe_allow_html=True)

    with col_r:
        st.plotly_chart(radar_chart(cls["metric_scores"]), use_container_width=True)

    st.markdown("---")

    # ── Metric cards ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)
    render_metrics_cards(m)

    st.markdown("---")

    # ── Metric score breakdown bar ────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Per-Metric Score Breakdown</div>', unsafe_allow_html=True)
    scores_df = pd.DataFrame([
        {"Metric": k.replace("_", " ").title(), "Score": v,
         "Color": "green" if v >= 70 else ("orange" if v >= 40 else "red")}
        for k, v in cls["metric_scores"].items()
    ])
    color_map = {"green": "#48bb78", "orange": "#ed8936", "red": "#fc8181"}
    fig_bar = go.Figure()
    for _, row in scores_df.iterrows():
        fig_bar.add_trace(go.Bar(
            x=[row["Score"]], y=[row["Metric"]], orientation="h",
            marker_color=color_map[row["Color"]],
            text=f"{row['Score']}", textposition="outside",
            name=row["Metric"], showlegend=False,
        ))
    fig_bar.add_vline(x=70, line_dash="dash", line_color="#38a169", annotation_text="Good", annotation_position="top")
    fig_bar.add_vline(x=40, line_dash="dash", line_color="#dd6b20", annotation_text="Average", annotation_position="top")
    fig_bar.update_layout(
        xaxis=dict(range=[0, 115], title="Score (0–100)"),
        yaxis=dict(title=""),
        height=320, margin=dict(l=10, r=40, t=20, b=20),
        paper_bgcolor="white", plot_bgcolor="#fafafa",
        barmode="overlay",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── Diagnosis ─────────────────────────────────────────────────────────────
    render_diagnosis(result["diagnosis"])

    st.markdown("---")

    # ── Recommendations ───────────────────────────────────────────────────────
    render_recommendations(result["recommendations"])

    st.markdown("---")

    # ── Raw metrics table ─────────────────────────────────────────────────────
    with st.expander("🔍 View Raw Metrics Data"):
        raw = {k: v for k, v in m.items() if k not in ("domain", "start_date", "end_date", "source")}
        df = pd.DataFrame(list(raw.items()), columns=["Metric", "Value"])
        df["Metric"] = df["Metric"].str.replace("_", " ").str.title()
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Single Domain Analysis ────────────────────────────────────────────────────
if analyze_clicked and domain_input.strip():
    orchestrator = DomainReputationOrchestrator()
    with st.spinner(f"🤖 Agents analyzing **{domain_input.strip()}** …"):
        result = orchestrator.analyze(
            domain     = domain_input.strip(),
            start_date = start_date.strftime("%Y-%m-%d"),
            end_date   = end_date.strftime("%Y-%m-%d"),
            custom_thresholds=custom_thresholds,
        )
    st.success(f"Analysis complete for **{domain_input.strip()}**")
    render_full_result(result)

elif analyze_clicked:
    st.warning("Please enter a domain name.")

# ── Batch Analysis ────────────────────────────────────────────────────────────
if run_batch and bulk_text.strip():
    domains = [d.strip() for d in bulk_text.strip().splitlines() if d.strip()]
    orchestrator = DomainReputationOrchestrator()

    rows = []
    progress = st.progress(0, text="Running batch analysis…")

    for i, domain in enumerate(domains):
        result = orchestrator.analyze(
            domain     = domain,
            start_date = start_date.strftime("%Y-%m-%d"),
            end_date   = end_date.strftime("%Y-%m-%d"),
            custom_thresholds=custom_thresholds,
        )
        cls = result["classification"]
        m   = result["metrics"]
        rows.append({
            "Domain":          domain,
            "Status":          cls["label"],
            "Score":           cls["overall_score"],
            "Open Rate %":     m["open_rate"],
            "Click Rate %":    m["click_rate"],
            "Delivery Rate %": m["delivery_rate"],
            "Abuse Rate %":    m["abuse_rate"],
            "Hard Bounce %":   m["hard_error_rate"],
            "Issues":          result["diagnosis"]["issue_count"],
            "Critical":        result["diagnosis"]["critical_count"],
        })
        progress.progress((i + 1) / len(domains), text=f"Analyzed {i+1}/{len(domains)} domains…")

    progress.empty()
    df = pd.DataFrame(rows)

    st.markdown('<div class="section-title">📋 Batch Results</div>', unsafe_allow_html=True)

    summary_cols = st.columns(3)
    summary_cols[0].metric("Total Analyzed", len(df))
    summary_cols[1].metric("Good",    len(df[df["Status"] == "GOOD"]))
    summary_cols[2].metric("Need Attention", len(df[df["Status"].isin(["AVERAGE","BAD"])]))

    def _color_status(val):
        colors = {"GOOD": "background-color:#d4edda;color:#155724",
                  "AVERAGE": "background-color:#fff3cd;color:#856404",
                  "BAD": "background-color:#f8d7da;color:#721c24"}
        return colors.get(val, "")

    styled_df = df.style.applymap(_color_status, subset=["Status"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    bad_domains = df[df["Status"] == "BAD"]
    if not bad_domains.empty:
        st.markdown("**🔴 Domains requiring immediate attention:**")
        for _, row in bad_domains.iterrows():
            st.markdown(f"- **{row['Domain']}** — Score: {row['Score']}, Critical Issues: {row['Critical']}")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Batch Report (CSV)", csv, "domain_reputation_report.csv", "text/csv")

elif run_batch:
    st.warning("Please enter at least one domain.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#a0aec0;font-size:0.8rem;padding:1rem 0">
  🛡️ <b>Domain Reputation AI</b> &nbsp;|&nbsp;
  Zeta Global Buildathon 2026 &nbsp;|&nbsp;
  Powered by Multi-Agent Architecture &nbsp;|&nbsp;
  Classifier · Diagnosis · Recommendation Agents
</div>
""", unsafe_allow_html=True)
