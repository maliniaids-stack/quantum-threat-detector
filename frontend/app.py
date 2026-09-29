"""Stage 12 — Enterprise Streamlit dashboard for QDS Threat Detection.
Run: streamlit run frontend/app.py (backend must be running on :8000)
Pure statistics-based detection engine — No AI/ML models.
"""
import os
import datetime
import json
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API = os.getenv("QDS_API", "http://127.0.0.1:8000")

# ── Professional SVG Icon Library ─────────────────────────────────────────────
ICONS = {
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "check_circle": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "x_circle": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    "alert_triangle": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "alert_octagon": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "database": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "lock": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "key": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21 2-2 2m-1.5 1.5L16 7l-1.5-1.5m-3 3L8 12l2 2-6 6H2v-2l6-6-2-2 3.5-3.5"/></svg>',
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/></svg>',
    "radio": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="2"/><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"/></svg>',
    "file_text": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "sliders": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "terminal": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
}


def icon(name: str, color: str = "#0F172A", size: int = 16) -> str:
    template = ICONS.get(name, ICONS["info"])
    return template.format(s=size, c=color)


LABELS = {
    "legitimate": "Legitimate Signature (Honest Protocol)",
    "blind_forgery": "Forgery — Blind State Guess",
    "informed_forgery": "Forgery — Intercept & Measure (Informed)",
    "replay": "Replay Attack (Stale Nonce / Timestamp)",
    "impersonation": "Signer Impersonation (Key Mismatch)",
    "unauthorized_verifier": "Unauthorized Verifier (Unregistered)",
    "channel_manipulation": "Quantum Channel Manipulation (Eavesdropper)",
}

VERDICT_ICONS = {
    "ACCEPT": "check_circle",
    "INCONCLUSIVE": "alert_triangle",
    "REJECT": "alert_octagon",
}

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QDS Threat Detection Engine | SIH 26141",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Professional Institutional CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0F172A;
}

.stApp {
    background-color: #FFFFFF;
}

/* Header Section */
.app-header {
    background-color: #FFFFFF;
    border-bottom: 2px solid #E2E8F0;
    padding: 18px 0 16px 0;
    margin-bottom: 24px;
}
.app-header-title {
    color: #0F172A;
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0;
}
.app-header-meta {
    color: #475569;
    font-size: 0.875rem;
    margin-top: 4px;
    font-weight: 400;
}
.app-badge-academic {
    display: inline-block;
    background-color: #F1F5F9;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-left: 8px;
}

/* Institutional Content Cards */
.solid-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    padding: 20px;
    margin-bottom: 20px;
}
.solid-card-header {
    font-size: 0.95rem;
    font-weight: 600;
    color: #0F172A;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 8px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Verdict Banners with Solid Colors */
.verdict-banner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 16px 24px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 1.25rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.verdict-banner-accept {
    background-color: #16A34A;
    color: #FFFFFF;
    border: 1px solid #15803D;
}
.verdict-banner-reject {
    background-color: #DC2626;
    color: #FFFFFF;
    border: 1px solid #B91C1C;
}
.verdict-banner-inconclusive {
    background-color: #D97706;
    color: #FFFFFF;
    border: 1px solid #B45309;
}

/* Metric Display Unit */
.metric-box {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 14px 16px;
    text-align: left;
}
.metric-box-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748B;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.metric-box-val {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0F172A;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 6px;
}
.metric-box-sub {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 2px;
}

/* Reality Check Columns */
.audit-item-real {
    border-left: 4px solid #16A34A;
    background-color: #F0FDF4;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #166534;
    margin-bottom: 8px;
    border-radius: 0 4px 4px 0;
}
.audit-item-simulated {
    border-left: 4px solid #D97706;
    background-color: #FFFBEB;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #92400E;
    margin-bottom: 8px;
    border-radius: 0 4px 4px 0;
}
.audit-item-not-claimed {
    border-left: 4px solid #DC2626;
    background-color: #FEF2F2;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #991B1B;
    margin-bottom: 8px;
    border-radius: 0 4px 4px 0;
}

/* System Status Tag */
.status-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}
.status-tag-green {
    background-color: #DCFCE7;
    color: #166534;
    border: 1px solid #86EFAC;
}
.status-tag-red {
    background-color: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FCA5A5;
}
.status-tag-yellow {
    background-color: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
}

/* Clean Tabs Navigation */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 20px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 4px 4px 0 0;
    padding: 10px 18px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #475569;
    border: 1px solid transparent;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0F172A;
    background-color: #F8FAFC;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    font-weight: 600 !important;
    border-color: #E2E8F0 #E2E8F0 #FFFFFF #E2E8F0 !important;
    border-bottom: 2px solid #0F172A !important;
}

/* Code & monospace elements */
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ── Corporate Top Navigation Header ──────────────────────────────────────────
header_html = f"""
<div class="app-header">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <h1 class="app-header-title">
                {icon('shield', '#0F172A', 26)}
                Quantum-Inspired Cyber Threat Detection Engine
                <span class="app-badge-academic">SIH 26141 Prototype</span>
            </h1>
            <div class="app-header-meta">
                Digital Signature Security Architecture · Gottesman-Chuang Pauli Protocol · Pure Statistical Hypothesis Testing (No AI/ML)
            </div>
        </div>
        <div style="text-align:right;">
            <span class="status-tag status-tag-green">
                {icon('activity', '#166534', 14)} Engine Online (:8000)
            </span>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# ── API Client Helper ─────────────────────────────────────────────────────────
def call(method: str, path: str, **kw):
    try:
        r = requests.request(method, API + path, timeout=120, **kw)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Backend communication error: {e}")
        st.info("Ensure the FastAPI service is active via: uvicorn backend.main:app --host 127.0.0.1 --port 8000")
        st.stop()


# ── Plotly Light Enterprise Theme ────────────────────────────────────────────
PLOT_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#F8FAFC",
    font=dict(family="Inter, sans-serif", color="#1E293B", size=12),
    margin=dict(l=48, r=24, t=48, b=48),
    xaxis=dict(
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
        linecolor="#94A3B8",
    ),
    yaxis=dict(
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
        linecolor="#94A3B8",
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WORKSPACE TABS
# ═══════════════════════════════════════════════════════════════════════════════

tab_lab, tab_hist, tab_curve, tab_shor, tab_real = st.tabs([
    "Evaluation Lab",
    "Audit Trail & Ledger",
    "Detection Sensitivity",
    "Quantum Advantage (Shor)",
    "System Constraints",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: EVALUATION LAB
# ═══════════════════════════════════════════════════════════════════════════════

with tab_lab:
    col_controls, col_results = st.columns([1, 2.5], gap="large")

    with col_controls:
        st.markdown(
            f'<div class="solid-card"><div class="solid-card-header">{icon("sliders", "#0F172A", 16)} Scenario Configuration</div>',
            unsafe_allow_html=True,
        )
        attack = st.selectbox(
            "Evaluation Scenario",
            list(LABELS),
            format_func=LABELS.get,
            help="Select attack profile to execute through the quantum measurement verification pipeline.",
        )
        strength = st.slider(
            "Channel Interception Ratio (Eve)",
            0.0, 1.0, 0.5, 0.05,
            disabled=attack != "channel_manipulation",
            help="Proportion of Bell state and public key qubits intercepted by eavesdropper.",
        )

        run_clicked = st.button("Execute Protocol Simulation", type="primary", use_container_width=True)
        if run_clicked:
            with st.spinner("Processing quantum measurement operators..."):
                st.session_state["last"] = call("POST", f"/simulate/{attack}", params={"strength": strength})

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="solid-card"><div class="solid-card-header">{icon("file_text", "#0F172A", 16)} Threat Taxonomy</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
        - **Legitimate**: Authorized signer, honest transmission.
        - **Blind Forgery**: Forger selects random eigenstates ($p_1 = 0.50$).
        - **Informed Forgery**: Forger measures in random basis ($p_1 = 0.333$).
        - **Replay Attack**: Captured signature replayed with expired timestamp.
        - **Impersonation**: Unauthorized entity signs with unlinked private key.
        - **Unauthorized Verifier**: Verification requested without distributed public key.
        - **Channel Manipulation**: Intercept-resend eavesdropping exceeding QBER limit.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    res = st.session_state.get("last")

    with col_results:
        if not res:
            st.markdown(
                f"""
                <div class="solid-card" style="text-align:center; padding: 48px 24px;">
                    <div style="margin-bottom:12px;">{icon('terminal', '#64748B', 32)}</div>
                    <div style="font-weight:600; color:#0F172A; font-size:1.1rem;">Simulation Engine Idle</div>
                    <div style="color:#64748B; font-size:0.875rem; margin-top:4px;">
                        Select a scenario from the configuration panel and click <strong>Execute Protocol Simulation</strong> to evaluate quantum state verification.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            verdict = res["verdict"]
            v_class = "accept" if verdict == "ACCEPT" else ("reject" if verdict == "REJECT" else "inconclusive")
            v_icon = VERDICT_ICONS.get(verdict, "info")

            # Solid Color Verdict Banner
            banner_html = f"""
            <div class="verdict-banner verdict-banner-{v_class}">
                {icon(v_icon, '#FFFFFF', 24)}
                VERDICT: {verdict}
            </div>
            """
            st.markdown(banner_html, unsafe_allow_html=True)

            # Metric Cards
            m1, m2, m3, m4 = st.columns(4)
            attack_type = res["attack_type"]
            threat_score = res["threat_score"]
            forgery_p = res["forgery_probability"]
            observed_err = (
                f"{res['stats']['observed_rate']:.2%}" if res.get("stats") else "N/A"
            )

            with m1:
                st.markdown(
                    f"""<div class="metric-box">
                        <div class="metric-box-label">Classification {icon('shield', '#64748B', 14)}</div>
                        <div class="metric-box-val" style="font-size:1.1rem; padding-top:6px;">{attack_type}</div>
                        <div class="metric-box-sub">Taxonomy label</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with m2:
                t_color = "#DC2626" if threat_score >= 70 else ("#D97706" if threat_score >= 30 else "#16A34A")
                st.markdown(
                    f"""<div class="metric-box">
                        <div class="metric-box-label">Threat Index {icon('alert_triangle', '#64748B', 14)}</div>
                        <div class="metric-box-val" style="color:{t_color}">{threat_score}<span style="font-size:0.9rem; color:#64748B;">/100</span></div>
                        <div class="metric-box-sub">Normalized risk</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f"""<div class="metric-box">
                        <div class="metric-box-label">P(Forger) {icon('cpu', '#64748B', 14)}</div>
                        <div class="metric-box-val">{forgery_p:.4f}</div>
                        <div class="metric-box-sub">Alternative hypothesis</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with m4:
                st.markdown(
                    f"""<div class="metric-box">
                        <div class="metric-box-label">Mismatch Rate {icon('activity', '#64748B', 14)}</div>
                        <div class="metric-box-val">{observed_err}</div>
                        <div class="metric-box-sub">Sampled qubits</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

            # Metadata Table Card
            ts = datetime.datetime.fromtimestamp(res["timestamp"])
            st.markdown(
                f"""
                <div class="solid-card" style="padding:14px 18px; margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#475569; flex-wrap:wrap; gap:8px;">
                        <span><strong>Signature ID:</strong> <code>{res['signature_id']}</code></span>
                        <span><strong>Signer:</strong> {res['signer']}</span>
                        <span><strong>Verifier:</strong> {res['verifier']}</span>
                        <span><strong>Recorded:</strong> {ts:%Y-%m-%d %H:%M:%S UTC}</span>
                    </div>
                    <div style="margin-top:10px; padding-top:8px; border-top:1px solid #F1F5F9; font-size:0.875rem;">
                        <strong>Diagnostic Assessment:</strong> {res['reason']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Mismatch Bar Chart with Solid Threshold Bounds
            if res.get("stats"):
                th = res["thresholds"]
                s = res["stats"]
                blocks = list(range(1, len(s["block_mismatches"]) + 1))

                # Color each block bar by solid category
                colors = []
                for val in s["block_mismatches"]:
                    if val <= th["accept_max"]:
                        colors.append("#16A34A")  # Solid green
                    elif val <= th["reject_min"]:
                        colors.append("#D97706")  # Solid yellow
                    else:
                        colors.append("#DC2626")  # Solid red

                fig = go.Figure()
                fig.add_bar(
                    x=blocks,
                    y=s["block_mismatches"],
                    name="Block Mismatches",
                    marker=dict(
                        color=colors,
                        line=dict(width=1, color="#0F172A"),
                    ),
                    hovertemplate="Digest Block %{x}<br>Observed Mismatches: %{y}<extra></extra>",
                )
                fig.add_hline(
                    y=s["expected_per_block"],
                    line=dict(dash="dash", color="#64748B", width=1.5),
                    annotation_text=f"Expected Honest ({s['expected_per_block']:.1f})",
                    annotation_position="top right",
                    annotation_font=dict(color="#475569", size=10),
                )
                fig.add_hline(
                    y=th["accept_max"],
                    line=dict(color="#16A34A", width=2),
                    annotation_text=f"Accept Bound (s_a <= {th['accept_max']})",
                    annotation_position="bottom right",
                    annotation_font=dict(color="#166534", size=10),
                )
                fig.add_hline(
                    y=th["reject_min"],
                    line=dict(color="#DC2626", width=2),
                    annotation_text=f"Reject Bound (s_v > {th['reject_min']})",
                    annotation_position="top right",
                    annotation_font=dict(color="#991B1B", size=10),
                )

                y_max = max(max(s["block_mismatches"]), th["reject_min"]) * 1.25
                fig.update_layout(
                    **PLOT_LAYOUT,
                    title="Digest Block Mismatch Distribution vs. Derived Decision Bounds",
                    xaxis_title="Digest Bit Block Index",
                    yaxis_title=f"Mismatches (per {th['block_size']} Pauli Qubits)",
                    yaxis=dict(range=[0, y_max]),
                    height=360,
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

                col_metrics_l, col_metrics_r = st.columns(2)
                with col_metrics_l:
                    st.markdown(
                        f"""
                        <div class="solid-card" style="padding:12px 16px; margin:0;">
                            <div style="font-weight:600; font-size:0.85rem; color:#0F172A; margin-bottom:4px;">HYPOTHESIS STATISTICS</div>
                            <div style="font-size:0.8rem; color:#475569; line-height:1.6;">
                                • Observed error: <strong>{s['observed_rate']:.3%}</strong> (Baseline: {s['expected_rate']:.1%})<br>
                                • p-Value (Honest): <strong>{s['p_value_honest']:.2e}</strong><br>
                                • Peak block mismatch: <strong>{s['worst_block']}</strong> / {th['block_size']} qubits
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_metrics_r:
                    if res.get("channel"):
                        ch = res["channel"]
                        healthy = ch["healthy"]
                        ch_class = "status-tag-green" if healthy else "status-tag-red"
                        ch_state = "CHANNEL SECURE" if healthy else "CHANNEL COMPROMISED"
                        st.markdown(
                            f"""
                            <div class="solid-card" style="padding:12px 16px; margin:0;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-weight:600; font-size:0.85rem; color:#0F172A;">BELL TEST TELEMETRY</span>
                                    <span class="status-tag {ch_class}">{ch_state}</span>
                                </div>
                                <div style="font-size:0.8rem; color:#475569; line-height:1.6; margin-top:4px;">
                                    • Measured QBER: <strong>{ch['qber']:.3%}</strong><br>
                                    • Security limit: <strong>{ch['qber_threshold']:.3%}</strong> ({ch['test_pairs']} Bell pairs)
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: AUDIT TRAIL & LEDGER
# ═══════════════════════════════════════════════════════════════════════════════

with tab_hist:
    st.markdown(
        f'<div class="solid-card-header">{icon("database", "#0F172A", 18)} Cryptographic Audit Ledger</div>',
        unsafe_allow_html=True,
    )

    audit_result = call("GET", "/audit/verify")

    if audit_result["valid"]:
        st.markdown(
            f"""
            <div class="audit-item-real" style="margin-bottom:16px;">
                <strong>HASH CHAIN INTEGRITY VERIFIED</strong>: All SHA-256 blocks validated across sequential cryptographic entries.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="audit-item-not-claimed" style="margin-bottom:16px;">
                <strong>HASH CHAIN COMPROMISED</strong>: Validation failed at transaction sequence index #{audit_result['broken_at_event']}.
            </div>
            """,
            unsafe_allow_html=True,
        )

    hist = call("GET", "/history")
    if hist:
        df = pd.DataFrame(hist)
        display_cols = ["id", "ts", "signature_id", "signer", "verifier", "verdict",
                        "attack_type", "observed_rate", "forgery_prob", "threat_score"]
        df_display = df[[c for c in display_cols if c in df.columns]].copy()
        if "ts" in df_display.columns:
            df_display["ts"] = pd.to_datetime(df_display["ts"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
            df_display = df_display.rename(columns={"ts": "Timestamp (UTC)"})

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "verdict": st.column_config.TextColumn("Verdict", width="small"),
                "threat_score": st.column_config.ProgressColumn("Threat Score", min_value=0, max_value=100),
            },
        )

        st.download_button(
            "Export Audit Log (JSON)",
            json.dumps(hist, indent=2, default=str),
            "qds_audit_ledger.json",
            mime="application/json",
            use_container_width=True,
        )
    else:
        st.info("No transaction events recorded. Execute a scenario in the Evaluation Lab to generate ledger entries.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: DETECTION SENSITIVITY (MONTE CARLO)
# ═══════════════════════════════════════════════════════════════════════════════

with tab_curve:
    st.markdown(
        f'<div class="solid-card-header">{icon("activity", "#0F172A", 18)} Empirical Sensitivity vs. Eavesdropper Strength</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Evaluation of the two-threshold statistical hypothesis classifier as an intercept-resend eavesdropper (Eve) "
        "samples an increasing fraction of transmitted quantum states. Data generated via Monte Carlo verification trials."
    )

    trials = st.slider("Monte Carlo Iterations per Increment", 10, 100, 30, help="Higher sample sizes decrease binomial sampling variance.")

    if st.button("Generate Empirical Response Curve", type="primary", use_container_width=True):
        with st.spinner(f"Computing {trials} trials across 8 interception levels..."):
            data = call("GET", "/detection-curve", params={"trials": trials})
            d = pd.DataFrame(data)

            fig = go.Figure()
            curves = [
                ("accept", "#16A34A", "Accept (Honest Protocol)"),
                ("inconclusive", "#D97706", "Inconclusive (Marginal Space)"),
                ("reject", "#DC2626", "Reject (Attack Classified)"),
                ("channel_flagged", "#0284C7", "Channel Flagged (QBER Alarm)"),
            ]
            for col, color, name in curves:
                fig.add_scatter(
                    x=d["eve_fraction"],
                    y=d[col],
                    name=name,
                    line=dict(color=color, width=2.5),
                    mode="lines+markers",
                    marker=dict(size=6, color=color),
                    hovertemplate=f"{name}<br>Interception Fraction: %{{x:.0%}}<br>Rate: %{{y:.1%}}<extra></extra>",
                )

            fig.update_layout(
                **PLOT_LAYOUT,
                title="Detection Probability as Function of Quantum Channel Eavesdropping",
                xaxis_title="Eavesdropper Interception Fraction (Eve)",
                yaxis_title="Observed Empirical Probability",
                yaxis=dict(range=[0, 1.05]),
                height=420,
                legend=dict(
                    x=0.02, y=0.98,
                    bgcolor="#FFFFFF",
                    bordercolor="#E2E8F0",
                    borderwidth=1,
                ),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Notice the sharp transition where QBER and per-block mismatches force the decision from Accept to Reject, "
                "bound mathematically by the Chernoff/binomial bounds."
            )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: QUANTUM ADVANTAGE (SHOR'S ALGORITHM)
# ═══════════════════════════════════════════════════════════════════════════════

with tab_shor:
    st.markdown(
        f'<div class="solid-card-header">{icon("cpu", "#0F172A", 18)} Quantum Vulnerability Context: Shor Period Finding</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    Classical public-key signatures (RSA, ECDSA) rely on the discrete logarithm or prime factorization problems.
    Polynomial-time quantum period-finding (Shor's Algorithm) reduces the integer factorization problem to $O((\\log N)^3)$ operations.
    In contrast, Quantum Digital Signatures (QDS) enforce information-theoretic security via quantum measurement collapse and no-cloning.
    """)

    if st.button("Execute Shor Period-Finding Simulation (N = 15)", type="primary", use_container_width=True):
        with st.spinner("Executing 8-qubit period finding quantum circuit..."):
            r = call("GET", "/shor-toy")

        st.markdown(
            f"""
            <div class="audit-item-real" style="margin-bottom:16px;">
                <strong>FACTORIZATION CONVERGED</strong>: Integer composite N = {r['N']} resolved to non-trivial factors <strong>{r['factors_found']}</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        counts = r["counts"]
        phases = sorted(counts.keys())
        fig = go.Figure()
        fig.add_bar(
            x=phases,
            y=[counts[p] for p in phases],
            marker=dict(
                color="#0F172A",
                line=dict(color="#334155", width=1),
            ),
            hovertemplate="Quantum Register Measurement: %{x}<br>Counts: %{y}<extra></extra>",
        )
        fig.update_layout(
            **PLOT_LAYOUT,
            title="QFT Output State Distribution for Order-Finding Circuit",
            xaxis_title="Phase Estimation Bitstring (Counting Register)",
            yaxis_title="Shot Frequency (Aer Simulator)",
            height=340,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info("Academic Scope: Demonstrates Shor circuit mechanics on simulator. Real RSA-2048 factorization requires millions of fault-tolerant physical qubits.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: SYSTEM CONSTRAINTS & HONESTY
# ═══════════════════════════════════════════════════════════════════════════════

with tab_real:
    st.markdown(
        f'<div class="solid-card-header">{icon("lock", "#0F172A", 18)} Academic Scope & Boundary Disclosures</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "In strict adherence to Smart India Hackathon guidelines (SIH 26141), this framework maintains complete transparency "
        "distinguishing analytical quantum physics principles from classical software simulation."
    )

    rc = call("GET", "/reality-check")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(f"#### {icon('check_circle', '#16A34A', 18)} Validated Principles", unsafe_allow_html=True)
        st.caption("Underlying mathematical models and quantum mechanics")
        for item in rc["real"]:
            st.markdown(f'<div class="audit-item-real">• {item}</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown(f"#### {icon('alert_triangle', '#D97706', 18)} Software Simulation", unsafe_allow_html=True)
        st.caption("Computational state vectors emulating physical hardware")
        for item in rc["simulated"]:
            st.markdown(f'<div class="audit-item-simulated">• {item}</div>', unsafe_allow_html=True)

    with col_c:
        st.markdown(f"#### {icon('alert_octagon', '#DC2626', 18)} Excluded Claims", unsafe_allow_html=True)
        st.caption("Explicitly disclaimed commercial / hardware capabilities")
        for item in rc["not_claimed"]:
            st.markdown(f'<div class="audit-item-not-claimed">• {item}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    **Core Academic Integrity Statement**:
    All quantum states are represented as complex linear algebra vectors on a classical processor.
    No physical quantum hardware is interfaced. The detection mechanism operates strictly on binomial statistical hypothesis testing,
    explicitly rejecting machine learning heuristics in favor of verifiable probabilistic guarantees.
    """)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#64748B; font-size:0.8rem; padding-bottom:20px;">
        Quantum-Inspired Cyber Threat Detection Framework · SIH Problem Statement 26141 · Built for Verifiable Research
    </div>
    """,
    unsafe_allow_html=True,
)
