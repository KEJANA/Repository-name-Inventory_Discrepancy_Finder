import streamlit as st
import pandas as pd
from pathlib import Path

from discrepancy_engine import load_data, find_discrepancies, investigate_sku

st.set_page_config(
    page_title="Fulfilment Intelligence",
    page_icon="◇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM
# ============================================================
st.markdown(
    """
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {
        background:#f5f7fa !important;
    }
    [data-testid="stAppViewContainer"] .block-container {
        max-width:1280px !important;
        padding:2.1rem 2.4rem 3rem !important;
    }
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4 {
        color:#172238 !important;
        opacity:1 !important;
    }
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] label {
        color:#53657f !important;
        opacity:1 !important;
    }
    .eyebrow {
        color:#60718d !important;
        font-size:.72rem;
        font-weight:800;
        letter-spacing:.12em;
        text-transform:uppercase;
        margin-bottom:.25rem;
    }
    .subtitle {
        color:#667892 !important;
        font-size:1rem;
        line-height:1.5;
        margin-top:-.35rem;
        margin-bottom:1.25rem;
    }
    section[data-testid="stSidebar"] { background:#0d172b !important; }
    section[data-testid="stSidebar"] * { color:#eef2f7 !important; }
    section[data-testid="stSidebar"] hr { border-color:#30405c !important; }
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background:#172742 !important;
        border-color:#3b4d6c !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] * { color:#fff !important; }
    [data-testid="stMetric"] {
        background:#fff !important;
        border:1px solid #dfe5ed !important;
        border-radius:14px !important;
        padding:1rem 1.1rem !important;
        min-height:128px !important;
        box-shadow:0 2px 8px rgba(23,34,56,.05) !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color:#172238 !important;
        opacity:1 !important;
    }
    [data-testid="stMetricLabel"] { color:#60718d !important; font-weight:700 !important; }
    [data-testid="stMetricValue"] { font-weight:800 !important; }
    [data-testid="stDataFrame"] {
        background:#fff !important;
        border:1px solid #dfe5ed !important;
        border-radius:12px !important;
        overflow:hidden;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:#fff !important;
        border-color:#dfe5ed !important;
        border-radius:14px !important;
    }
    [data-testid="stAppViewContainer"] [data-baseweb="input"] > div,
    [data-testid="stAppViewContainer"] [data-baseweb="select"] > div {
        background:#fff !important;
        border-color:#ccd5e2 !important;
    }
    [data-testid="stAppViewContainer"] [data-baseweb="input"] input,
    [data-testid="stAppViewContainer"] [data-baseweb="select"] * {
        color:#172238 !important;
        -webkit-text-fill-color:#172238 !important;
    }
    .status-normal {
        display:inline-block;padding:9px 14px;border:1px solid #86efac;
        border-radius:999px;background:#f0fdf4;color:#15803d !important;
        font-size:12px;font-weight:800;letter-spacing:.04em;text-align:center;
    }
    .status-disruption {
        display:inline-block;padding:9px 14px;border:1px solid #fbbf24;
        border-radius:999px;background:#fffbeb;color:#a16207 !important;
        font-size:12px;font-weight:800;letter-spacing:.04em;text-align:center;
    }
    .decision-card {
        background:#fff;border:1px solid #dfe5ed;border-radius:14px;padding:22px;
        min-height:150px;
    }
    .decision-label { color:#60718d !important;font-size:11px;font-weight:800;letter-spacing:.1em; }
    .decision-value { color:#172238 !important;font-size:27px;font-weight:850;margin-top:8px; }
    .decision-detail { color:#60718d !important;font-size:13px;margin-top:5px; }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_DIR = Path(__file__).resolve().parent / "data"

# ============================================================
# DATA / ENGINE
# ============================================================
@st.cache_data(show_spinner=False)
def get_data():
    return load_data(str(DATA_DIR))


@st.cache_data(show_spinner=True)
def get_discrepancies():
    return find_discrepancies(str(DATA_DIR))


inventory, putaway, moves, pick_failures, cycle_counts, locations = get_data()
discrepancies = get_discrepancies()
ground_truth = pd.read_csv(DATA_DIR / "ground_truth.csv")

pages = [
    "Operations Overview",
    "Discrepancy Finder",
    "SKU Investigation",
    "Performance & Scenarios",
    "Edge & Failure Cases",
    "35% Review",
]

if "page" not in st.session_state:
    st.session_state.page = pages[0]
if "scenario" not in st.session_state:
    st.session_state.scenario = "Normal Operating Day"

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="font-size:21px;font-weight:800;color:#fff;">◇ FULFILMENT</div>
        <div style="font-size:21px;font-weight:800;color:#fff;margin-top:4px;">INTELLIGENCE</div>
        <div style="font-size:13px;line-height:1.5;color:#b9c5d7;margin-top:12px;">
            Inventory-location<br>decision support
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("<div style='font-size:18px;font-weight:800;color:#fff;'>Workspace</div>", unsafe_allow_html=True)
    st.session_state.page = st.radio(
        "Workspace", pages, index=pages.index(st.session_state.page), label_visibility="collapsed"
    )
    st.divider()
    st.markdown("<div style='font-size:18px;font-weight:800;color:#fff;'>Operating scenario</div>", unsafe_allow_html=True)
    st.session_state.scenario = st.selectbox(
        "Scenario", ["Normal Operating Day", "Disruption / Urgent Demand"],
        index=0 if st.session_state.scenario == "Normal Operating Day" else 1,
    )
    st.divider()
    st.caption("Prototype v0.1")
    st.caption("Evidence-based scoring")
    st.caption("Synthetic operational dataset")

SCENARIO_CODE = "NORMAL" if st.session_state.scenario == "Normal Operating Day" else "DISRUPTION"


def scenario_failures():
    return pick_failures[pick_failures["scenario"] == SCENARIO_CODE]


def scenario_discrepancies():
    skus = set(scenario_failures()["sku"].dropna())
    return discrepancies[discrepancies["sku"].isin(skus)].copy()


def page_header(eyebrow, title, subtitle):
    left, right = st.columns([5.8, 1.2], gap="medium")
    with left:
        st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
        st.title(title)
        st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)
    with right:
        if SCENARIO_CODE == "NORMAL":
            st.markdown('<div class="status-normal">● NORMAL OPERATIONS</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-disruption">● DISRUPTION MODE</div>', unsafe_allow_html=True)


def section_intro(title, subtitle):
    st.header(title)
    st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)


def show_table(data):
    if data.empty:
        st.info("No records match the current filters.")
        return
    display = data.copy()
    if "evidence_score" in display.columns:
        display["evidence_score"] = display["evidence_score"].map(lambda x: f"{x:.2f}")
    if "Evidence Score" in display.columns:
        display["Evidence Score"] = display["Evidence Score"].map(lambda x: f"{x:.2f}")
    st.dataframe(display, use_container_width=True, hide_index=True)


def footer():
    st.divider()
    st.caption("Fulfilment Intelligence · Inventory-location discrepancy decision support · Prototype v0.1 · Synthetic operational data")

# ============================================================
# PAGE 1
# ============================================================
def operations_overview():
    page_header("WAREHOUSE CONTROL TOWER", "Operations Overview", "Inventory-location health and investigation workload")
    sf = scenario_failures()
    sd = scenario_discrepancies()
    investigations = sf["sku"].nunique()
    high_conf = int((sd["confidence"] == "High confidence").sum())
    priority_cases = int(sd["priority"].isin(["HIGH", "CRITICAL"]).sum())

    section_intro("Key operating metrics", "Live metrics calculated from the generated operational dataset.")
    c1,c2,c3 = st.columns(3, gap="medium")
    with c1: st.metric("Inventory Records", f"{len(inventory):,}"); st.caption("Inventory master records")
    with c2: st.metric("Investigations", f"{investigations:,}"); st.caption("Unique SKUs with pick failures")
    with c3: st.metric("High Confidence", f"{high_conf:,}"); st.caption("Engine-ranked candidates")
    c4,c5 = st.columns(2, gap="medium")
    with c4: st.metric("Pick Failures", f"{len(sf):,}"); st.caption(f"{st.session_state.scenario}")
    with c5: st.metric("Priority Cases", f"{priority_cases:,}"); st.caption("High + critical workload")

    section_intro("Operational signals", "Where failures are occurring and how strong the evidence is.")
    chart1,chart2 = st.columns(2, gap="medium")
    with chart1:
        with st.container(border=True):
            st.subheader("Pick failure pattern")
            st.bar_chart(sf["failure_reason"].value_counts())
    with chart2:
        with st.container(border=True):
            st.subheader("Confidence distribution")
            st.bar_chart(sd["confidence"].value_counts())

    section_intro("Priority investigations", "Cases where operational impact justifies immediate investigation.")
    priority_df = sd[sd["priority"].isin(["CRITICAL", "HIGH"])].copy()
    show_table(priority_df[["sku","expected_location","recommended_location","confidence","evidence_score","priority"]].head(10))
    st.info("Evidence scores rank candidate locations; they are not calibrated probabilities. Human verification remains required before correction.")
    footer()

# ============================================================
# PAGE 2
# ============================================================
def discrepancy_finder():
    page_header("INVESTIGATION QUEUE", "Discrepancy Finder", "Ranked candidate locations generated from warehouse evidence")
    data = scenario_discrepancies()
    c1,c2,c3 = st.columns(3, gap="medium")
    with c1: search = st.text_input("Search SKU", placeholder="SKU-00001")
    with c2: confidence = st.selectbox("Confidence", ["All","High confidence","Moderate confidence","Low confidence","Insufficient evidence"])
    with c3: priority = st.selectbox("Priority", ["All","HIGH","CRITICAL","STANDARD","REVIEW"])
    if search: data = data[data["sku"].str.contains(search.upper(), na=False)]
    if confidence != "All": data = data[data["confidence"] == confidence]
    if priority != "All": data = data[data["priority"] == priority]
    st.caption(f"{len(data):,} investigations matched")
    show_table(data[["sku","product_name","expected_location","recommended_location","evidence_score","confidence","priority"]].head(25))
    st.warning("Uncertainty policy: evidence scores are ranking strength, not probabilities. Manual verification is required before changing inventory records.")
    footer()

# ============================================================
# PAGE 3
# ============================================================
def sku_investigation():
    page_header("EVIDENCE-LED INVESTIGATION", "SKU Investigation", "Trace the operational evidence behind a location recommendation")
    available = scenario_discrepancies()["sku"].drop_duplicates().tolist()
    if not available:
        st.info("No investigation SKUs are available for this scenario.")
        return
    default = available.index("SKU-00001") if "SKU-00001" in available else 0
    selected = st.selectbox("Select SKU", available, index=default)
    row = inventory[inventory["sku"] == selected].iloc[0]
    result = investigate_sku(selected, inventory, putaway, moves, pick_failures, cycle_counts, locations)
    if result.empty:
        st.warning("Insufficient operational evidence for this SKU.")
        return
    best = result.iloc[0]

    with st.container(border=True):
        st.caption("SKU")
        st.subheader(selected)
        st.caption(row["product_name"])
    c1,c2,c3,c4 = st.columns(4, gap="medium")
    with c1: st.metric("System Location", row["system_location"]); st.caption("Current WMS record")
    with c2: st.metric("System Quantity", int(row["system_quantity"])); st.caption("Units expected")
    with c3: st.metric("Unit Value", f"£{row['unit_value']:.2f}"); st.caption("Inventory value")
    with c4: st.metric("Inventory Status", row["inventory_status"]); st.caption("Current status")

    section_intro("Investigation recommendation", "The recommendation is calculated from multiple operational signals.")
    c1,c2 = st.columns([2,1], gap="medium")
    with c1:
        with st.container(border=True):
            st.caption("FIRST LOCATION TO CHECK")
            st.markdown(f'<div class="decision-value">{best["candidate_location"]}</div>', unsafe_allow_html=True)
            st.write(best["recommended_action"])
    with c2:
        with st.container(border=True):
            st.caption("EVIDENCE ASSESSMENT")
            st.subheader(best["confidence"])
            st.write(f"Evidence score: **{best['evidence_score']:.2f}**")
            st.caption(best["evidence_strength"])
    st.warning("The score represents ranking strength, not a calibrated probability. Human verification is required before correction.")

    section_intro("Candidate locations", "Alternative locations remain visible so competing evidence can be assessed.")
    show_table(result[["rank","candidate_location","evidence_score","confidence","evidence_strength"]].head(8))

    section_intro("Why this location?", "Evidence contributing to the top-ranked candidate.")
    for reason in best["evidence"]:
        st.write(f"✓  {reason}")

    section_intro("Operational evidence trail", "Recent put-away scans, moves, failures and counts for this SKU.")
    events = []
    for _, r in putaway[putaway.sku == selected].tail(5).iterrows():
        events.append([r.timestamp, "Put-away scan", f"→ {r.destination_location}"])
    for _, r in moves[moves.sku == selected].tail(5).iterrows():
        events.append([r.timestamp, "Move event", f"{r.from_location} → {r.to_location}"])
    for _, r in pick_failures[pick_failures.sku == selected].tail(5).iterrows():
        events.append([r.timestamp, "Pick failure", f"Expected at {r.expected_location} · {r.failure_reason}"])
    for _, r in cycle_counts[cycle_counts.sku == selected].tail(3).iterrows():
        events.append([r.timestamp, "Cycle count", f"{r.location} · counted {r.counted_quantity} · variance {r.variance:+d}"])
    events_df = pd.DataFrame(events, columns=["Time","Event","Detail"]).sort_values("Time") if events else pd.DataFrame(columns=["Time","Event","Detail"])
    show_table(events_df)

    section_intro("Baseline comparison", "Simple last-known operational record versus the multi-signal recommendation.")
    last_known = None
    p = putaway[putaway.sku == selected][["timestamp","destination_location"]].rename(columns={"destination_location":"location"})
    m = moves[moves.sku == selected][["timestamp","to_location"]].rename(columns={"to_location":"location"})
    combined = pd.concat([p,m], ignore_index=True)
    if not combined.empty: last_known = combined.sort_values("timestamp").iloc[-1]["location"]
    c1,c2 = st.columns(2, gap="medium")
    with c1:
        with st.container(border=True):
            st.caption("SIMPLE LAST-KNOWN BASELINE")
            st.subheader(str(last_known) if last_known is not None else "No recorded location")
            st.write("Most recent put-away / move destination")
    with c2:
        with st.container(border=True):
            st.caption("MULTI-SIGNAL PROTOTYPE")
            st.subheader(best["candidate_location"])
            st.write("Evidence-weighted candidate ranking")
    footer()

# ============================================================
# PAGE 4
# ============================================================
def performance_page():
    page_header(
        "EVALUATION",
        "Performance & Scenarios",
        "Ground-truth evaluation, baseline comparison and disruption testing"
    )

    gt = ground_truth.copy()

    # Run the evidence engine for every ground-truth SKU.
    engine_results = {}
    for sku in gt["sku"]:
        engine_results[sku] = investigate_sku(
            sku,
            inventory,
            putaway,
            moves,
            pick_failures,
            cycle_counts,
            locations
        )

    # --------------------------------------------------------
    # RECOVERABLE CASES
    # Top-1 accuracy is measured only on cases where a specific
    # correct location should be recovered.
    # --------------------------------------------------------
    recoverable_types = [
        "CLEAR_RELOCATION",
        "URGENT_DEMAND_DISRUPTION"
    ]

    recoverable_cases = gt[
        gt["case_type"].isin(recoverable_types)
    ].copy()

    baseline_hits = 0
    prototype_hits = 0

    for _, r in recoverable_cases.iterrows():
        sku = r["sku"]
        target = str(r["actual_candidate_location"])

        # Baseline: current system / WMS location.
        inv_rows = inventory[inventory["sku"] == sku]
        system_location = (
            str(inv_rows.iloc[0]["system_location"])
            if not inv_rows.empty
            else ""
        )
        baseline_hits += int(system_location == target)

        # Prototype: evidence-based candidate ranking.
        res = engine_results[sku]
        prototype_hits += int(
            not res.empty
            and str(res.iloc[0]["candidate_location"]) == target
        )

    n = len(recoverable_cases)
    baseline_top1 = round(100 * baseline_hits / n) if n else 0
    prototype_top1 = round(100 * prototype_hits / n) if n else 0

    # --------------------------------------------------------
    # SAFETY CASES
    # These are evaluated on conservative handling, not Top-1
    # prediction accuracy.
    # --------------------------------------------------------
    safety_types = [
        "CONFLICTING_MOVEMENT",
        "NO_RECENT_SCAN",
        "INVALID_LOCATION",
        "CYCLE_COUNT_CONTRADICTION"
    ]

    safety_cases = gt[
        gt["case_type"].isin(safety_types)
    ].copy()

    safety_passes = 0
    eval_rows = []

    # --------------------------------------------------------
    # GROUND-TRUTH EVALUATION
    # --------------------------------------------------------
    for _, r in gt.iterrows():
        case_id = r["case_id"]
        case_type = r["case_type"]
        sku = r["sku"]
        res = engine_results[sku]

        top = res.iloc[0] if not res.empty else None
        top_candidate = (
            str(top["candidate_location"])
            if top is not None
            else "—"
        )
        confidence = (
            str(top["confidence"])
            if top is not None
            else "—"
        )
        target = str(r["actual_candidate_location"])

        passed = False
        behaviour = ""

        # Clear relocation: correct location should be ranked first.
        if case_type == "CLEAR_RELOCATION":
            passed = (
                top is not None
                and top_candidate == target
            )
            behaviour = (
                "Correct target ranked first"
                if passed
                else "Target not ranked first"
            )

        # Urgent demand: correct target should still rank first.
        elif case_type == "URGENT_DEMAND_DISRUPTION":
            passed = (
                top is not None
                and top_candidate == target
            )
            behaviour = (
                "Correct target ranked first under disruption"
                if passed
                else "Target not ranked first under disruption"
            )

        # Conflicting movement: conservative handling is a pass when
        # the system returns a candidate but keeps confidence low.
        elif case_type == "CONFLICTING_MOVEMENT":
            passed = (
                top is not None
                and confidence in [
                    "Low confidence",
                    "Insufficient evidence"
                ]
            )
            behaviour = (
                "Competing evidence handled conservatively; verification required"
                if passed
                else "Conflicting evidence handled too confidently"
            )

        # No recent scan: low/insufficient evidence must not be
        # treated as a confident correction.
        elif case_type == "NO_RECENT_SCAN":
            passed = (
                top is not None
                and confidence in [
                    "Low confidence",
                    "Insufficient evidence"
                ]
            )
            behaviour = (
                "No recent evidence; manual verification required"
                if passed
                else "Unsupported confidence"
            )

        # Invalid locations must never be recommended.
        elif case_type == "INVALID_LOCATION":
            passed = (
                top is not None
                and top_candidate != target
            )
            behaviour = (
                "Invalid location rejected"
                if passed
                else "Invalid location incorrectly recommended"
            )

        # Cycle-count contradiction: low/insufficient evidence means
        # the system is asking for verification instead of asserting
        # a correction.
        elif case_type == "CYCLE_COUNT_CONTRADICTION":
            passed = (
                top is not None
                and confidence in [
                    "Low confidence",
                    "Insufficient evidence"
                ]
            )
            behaviour = (
                "Contradiction handled conservatively; verification required"
                if passed
                else "Unsupported confidence"
            )

        else:
            passed = False
            behaviour = "Unrecognised evaluation case"

        if case_type in safety_types and passed:
            safety_passes += 1

        eval_rows.append(
            [
                case_id,
                case_type,
                top_candidate,
                confidence,
                "PASS" if passed else "CHECK",
                behaviour
            ]
        )

    # --------------------------------------------------------
    # TOP METRIC CARDS
    # --------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.metric(
            "System Baseline Top-1",
            f"{baseline_top1}%"
        )
        st.caption(
            f"{n} recoverable single-target cases"
        )

    with c2:
        st.metric(
            "Prototype Top-1",
            f"{prototype_top1}%"
        )
        st.caption(
            "Evidence-based candidate ranking"
        )

    with c3:
        st.metric(
            "Safety Cases",
            f"{safety_passes} / {len(safety_cases)}"
        )
        st.caption(
            "Conflict / missing / invalid / contradiction"
        )

    with c4:
        st.metric(
            "Ground Truth",
            f"{len(gt)} cases"
        )
        st.caption(
            "Deterministic evaluation set"
        )

    # --------------------------------------------------------
    # GROUND-TRUTH TABLE
    # --------------------------------------------------------
    section_intro(
        "Ground-truth evaluation",
        "Recoverable cases measure location-recovery accuracy. "
        "Safety cases measure whether the system avoids unsupported corrections."
    )

    show_table(
        pd.DataFrame(
            eval_rows,
            columns=[
                "Case",
                "Type",
                "Top Candidate",
                "Confidence",
                "Result",
                "Expected Behaviour"
            ]
        )
    )

    # --------------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------------
    section_intro(
        "How to interpret the evaluation",
        "The two metrics answer different operational questions."
    )

    st.write(
        f"**Baseline:** {baseline_hits}/{n} recoverable cases correctly "
        "identified using the current system/WMS location."
    )

    st.write(
        f"**Prototype:** {prototype_hits}/{n} recoverable cases correctly "
        "ranked first using multi-signal evidence."
    )

    st.write(
        f"**Safety:** {safety_passes}/{len(safety_cases)} safety cases "
        "passed conservative handling without unsupported correction."
    )

    st.caption(
        "Safety cases are intentionally excluded from Top-1 accuracy "
        "because their expected behaviour is uncertainty handling "
        "rather than forced location prediction."
    )

    # --------------------------------------------------------
    # NORMAL DAY VS DISRUPTION
    # --------------------------------------------------------
    section_intro(
        "Normal day vs disruption",
        "Operational volume from the generated dataset."
    )

    scenario_data = pd.DataFrame(
        {
            "Metric": [
                "Move events",
                "Pick failures"
            ],
            "Normal": [
                int((moves["scenario"] == "NORMAL").sum()),
                int((pick_failures["scenario"] == "NORMAL").sum())
            ],
            "Disruption": [
                int((moves["scenario"] == "DISRUPTION").sum()),
                int((pick_failures["scenario"] == "DISRUPTION").sum())
            ]
        }
    ).set_index("Metric")

    st.bar_chart(scenario_data)

    st.info(
        "Urgent demand increases operational priority; it does not "
        "artificially increase evidence confidence."
    )

    footer()

# ============================================================
# PAGE 5
# ============================================================
def edge_cases():
    page_header(
        "ROBUSTNESS TESTING",
        "Edge & Failure Cases",
        "Safe behaviour when evidence is incomplete, contradictory or invalid"
    )

    gt = ground_truth.copy()
    rows = []

    for _, r in gt.iterrows():
        res = investigate_sku(
            r["sku"],
            inventory,
            putaway,
            moves,
            pick_failures,
            cycle_counts,
            locations
        )

        top = res.iloc[0] if not res.empty else None
        case = r["case_type"]
        target = str(r["actual_candidate_location"])

        if case == "CLEAR_RELOCATION":
            passed = (
                top is not None
                and str(top["candidate_location"]) == target
            )

        elif case == "URGENT_DEMAND_DISRUPTION":
            passed = (
                top is not None
                and str(top["candidate_location"]) == target
            )

        elif case == "CONFLICTING_MOVEMENT":
            passed = (
                top is not None
                and str(top["confidence"]) in [
                    "Low confidence",
                    "Insufficient evidence"
                ]
            )

        elif case == "NO_RECENT_SCAN":
            passed = (
                top is not None
                and str(top["confidence"]) in [
                    "Low confidence",
                    "Insufficient evidence"
                ]
            )

        elif case == "INVALID_LOCATION":
            passed = (
                top is not None
                and str(top["candidate_location"]) != target
            )

        elif case == "CYCLE_COUNT_CONTRADICTION":
            passed = (
                top is not None
                and str(top["confidence"]) in [
                    "Low confidence",
                    "Insufficient evidence"
                ]
            )

        else:
            passed = False

        rows.append(
            [
                r["case_id"],
                case,
                "PASS" if passed else "CHECK"
            ]
        )

    show_table(
        pd.DataFrame(
            rows,
            columns=["Case", "Failure state", "Result"]
        )
    )

    section_intro(
        "Safe-failure design",
        "Rules that prevent unsupported inventory corrections."
    )

    rules = [
        "No evidence → no invented location.",
        "Conflicting evidence → lower certainty and expose alternatives.",
        "Invalid location → keep visible for audit, but never recommend it.",
        "Cycle-count contradiction → verify before correction.",
        "Urgent demand → increase operational priority, not evidence confidence."
    ]

    with st.container(border=True):
        for rule in rules:
            st.write(f"✓  {rule}")

    footer()

# PAGE 6 - 35% REVIEW
# ============================================================
def review_page():
    page_header(
        "PROJECT MILESTONE",
        "35% Review",
        "Implementation evidence, validation plan and deployment readiness",
    )

    st.progress(0.35, text="35% implementation milestone")

    # --------------------------------------------------------
    # 1. COMPLETED IMPLEMENTATION
    # --------------------------------------------------------
    section_intro(
        "Implementation completed",
        "Core fulfilment intelligence capabilities implemented in the working prototype.",
    )

    completed = [
        "Scenario definition: normal operating day and disruption / urgent demand",
        "Synthetic operational dataset",
        "Put-away scan integration",
        "Move event integration",
        "Pick failure integration",
        "Cycle count integration",
        "Location master integration",
        "Current system / WMS location baseline",
        "Evidence-based candidate location scoring",
        "Uncertainty classification",
        "Working inventory-location discrepancy finder",
        "SKU investigation workflow",
        "Normal vs disruption scenario comparison",
        "Deterministic edge and failure-case testing",
        "Ground-truth performance evaluation",
    ]

    for item in completed:
        st.write(f"✓  {item}")

    # --------------------------------------------------------
    # 2. BASELINE / PROTOTYPE APPROACH
    # --------------------------------------------------------
    section_intro(
        "Chosen approach",
        "Why an evidence-based ranking approach is appropriate for the prototype.",
    )

    with st.container(border=True):
        st.subheader("Baseline")
        st.write(
            "The baseline uses the current system / WMS location as the simple operational reference."
        )

        st.subheader("Prototype")
        st.write(
            "The prototype combines system location, put-away scans, move events, "
            "pick failures, cycle counts and quantity movement to rank candidate locations."
        )

        st.subheader("Why this approach?")
        st.write(
            "An explainable evidence-based approach is appropriate at prototype stage "
            "because warehouse users need to understand why a location was suggested. "
            "It also supports auditability and safe handling of uncertain or conflicting evidence."
        )

    # --------------------------------------------------------
    # 3. USABILITY WALKTHROUGH
    # --------------------------------------------------------
    section_intro(
        "Usability walkthrough",
        "Intended operator workflow from detecting a discrepancy to verifying a location.",
    )

    walkthrough = pd.DataFrame(
        [
            [
                1,
                "Operations Overview",
                "Identify investigation workload and priority cases",
            ],
            [
                2,
                "Discrepancy Finder",
                "Filter and select a SKU requiring investigation",
            ],
            [
                3,
                "SKU Investigation",
                "Review recommended location, confidence and evidence",
            ],
            [
                4,
                "Candidate Locations",
                "Compare alternative locations when evidence competes",
            ],
            [
                5,
                "Evidence Trail",
                "Review put-away, move, pick-failure and cycle-count events",
            ],
            [
                6,
                "Human Verification",
                "Verify the suggested physical location before correcting inventory",
            ],
        ],
        columns=["Step", "Screen", "Operator Action"],
    )

    show_table(walkthrough)

    # --------------------------------------------------------
    # 4. STAKEHOLDER VALIDATION
    # --------------------------------------------------------
    section_intro(
        "Stakeholder validation",
        "Short validation protocol to test whether the workflow is understandable and useful.",
    )

    st.info(
        "This section records the validation method. Do not claim stakeholder results "
        "until a real reviewer or warehouse-user walkthrough has been completed."
    )

    validation = pd.DataFrame(
        [
            [
                "Task 1",
                "Find a discrepancy",
                "Can the user identify which SKU needs investigation?",
                "To be completed",
            ],
            [
                "Task 2",
                "Interpret recommendation",
                "Can the user understand the first location to check?",
                "To be completed",
            ],
            [
                "Task 3",
                "Interpret uncertainty",
                "Can the user distinguish high, moderate and insufficient evidence?",
                "To be completed",
            ],
            [
                "Task 4",
                "Review evidence",
                "Can the user identify why the location was suggested?",
                "To be completed",
            ],
            [
                "Task 5",
                "Make a safe decision",
                "Does the user understand that physical verification is required?",
                "To be completed",
            ],
        ],
        columns=[
            "Task",
            "Activity",
            "Validation Question",
            "Result",
        ],
    )

    show_table(validation)

    # --------------------------------------------------------
    # 5. PERFORMANCE / MEASUREMENT
    # --------------------------------------------------------
    section_intro(
        "Measurement and success criteria",
        "Separating measured prototype results from operational targets that require user timing data.",
    )

    metrics = pd.DataFrame(
        [
            [
                "Baseline",
                "Current system / WMS location",
                "Measured using ground-truth evaluation",
            ],
            [
                "Prototype",
                "Evidence-based ranking",
                "Measured using ground-truth evaluation",
            ],
            [
                "Primary operational target",
                "≥20% reduction in investigation effort / time-to-locate",
                "Requires stakeholder timing study",
            ],
            [
                "Ranking metric",
                "Top-1 / Top-2 ground-truth performance",
                "Available from deterministic evaluation set",
            ],
        ],
        columns=["Measure", "Definition", "Status"],
    )

    show_table(metrics)

    st.warning(
        "Operational time-to-locate improvement must not be presented as a measured "
        "fact until real user timing data has been collected."
    )

    # --------------------------------------------------------
    # 6. ERROR ANALYSIS
    # --------------------------------------------------------
    section_intro(
        "Error analysis",
        "How the system behaves when the evidence is weak, contradictory or invalid.",
    )

    error_analysis = [
        "No recent scan → reduce confidence and avoid inventing a location.",
        "Conflicting movement evidence → expose competing destinations instead of hiding alternatives.",
        "Invalid / inactive location → retain for audit visibility but do not recommend it.",
        "Cycle-count contradiction → require verification before inventory correction.",
        "Urgent demand → increase operational priority, not evidence confidence.",
    ]

    with st.container(border=True):
        for item in error_analysis:
            st.write(f"✓  {item}")

    # --------------------------------------------------------
    # 7. ETHICS / RESPONSIBLE AI
    # --------------------------------------------------------
    section_intro(
        "Ethics and responsible AI",
        "Controls designed to prevent false precision and unsafe inventory corrections.",
    )

    ethics = [
        "Evidence scores are ranking strengths, not calibrated probabilities.",
        "Low or insufficient evidence is explicitly communicated to the operator.",
        "Conflicting evidence remains visible rather than being silently discarded.",
        "Invalid locations cannot become recommended correction targets.",
        "Inventory records are not automatically corrected by the prototype.",
        "A human operator remains responsible for physical verification and final correction.",
        "The current evaluation dataset is synthetic and must not be treated as production evidence.",
    ]

    with st.container(border=True):
        for item in ethics:
            st.write(f"✓  {item}")

    # --------------------------------------------------------
    # 8. DEPLOYMENT CHECKLIST
    # --------------------------------------------------------
    section_intro(
        "Deployment checklist",
        "Checks required before moving from prototype to a live fulfilment environment.",
    )

    deployment = pd.DataFrame(
        [
            ["Operational data sources", "Connect and validate live WMS event feeds", "Pending"],
            ["Location master", "Validate active / inactive location records", "Pending"],
            ["Timestamps", "Validate event ordering and timestamp quality", "Pending"],
            ["Data quality", "Monitor missing, duplicate and inconsistent scan events", "Pending"],
            ["Scoring engine", "Run automated unit and regression tests", "Pending"],
            ["Edge cases", "Run no-scan, conflict, invalid-location and count-contradiction tests", "Prototype tested"],
            ["Uncertainty UI", "Keep confidence and evidence visible to operators", "Implemented"],
            ["Human verification", "Require operator confirmation before correction", "Implemented"],
            ["Audit trail", "Record recommendation, evidence and final operator decision", "Pending"],
            ["Live validation", "Measure actual time-to-locate against baseline", "Pending"],
            ["Monitoring", "Track accuracy, false recommendations and operational impact", "Pending"],
        ],
        columns=["Area", "Required Check", "Status"],
    )

    show_table(deployment)

    # --------------------------------------------------------
    # 9. FINAL STATUS
    # --------------------------------------------------------
    section_intro(
        "35% milestone status",
        "Current evidence against the implementation requirements.",
    )

    status = pd.DataFrame(
        [
            ["Scenario definition", "Complete"],
            ["Baseline method", "Complete"],
            ["End-to-end working prototype", "Complete"],
            ["Operational signal integration", "Complete"],
            ["Uncertainty communication", "Complete"],
            ["Edge / failure testing", "Complete"],
            ["Ground-truth evaluation", "Complete"],
            ["Usability walkthrough", "Prototype workflow complete; user validation pending"],
            ["Stakeholder validation", "Pending real reviewer feedback"],
            ["Time-to-locate measurement", "Pending real user timing data"],
            ["Probability calibration", "Future production validation"],
            ["Deployment readiness", "Checklist defined; production integration pending"],
        ],
        columns=["Requirement", "Status"],
    )

    show_table(status)

    st.warning(
        "Prototype limitation: the operational dataset is synthetic and evidence scores "
        "are ranking strengths rather than calibrated probabilities. The system is "
        "decision support, not an automatic inventory-correction system."
    )

    footer()
    # ============================================================
# PAGE ROUTER
# ============================================================

if st.session_state.page == "Operations Overview":
    operations_overview()

elif st.session_state.page == "Discrepancy Finder":
    discrepancy_finder()

elif st.session_state.page == "SKU Investigation":
    sku_investigation()

elif st.session_state.page == "Performance & Scenarios":
    performance_page()

elif st.session_state.page == "Edge & Failure Cases":
    edge_cases()

elif st.session_state.page == "35% Review":
    review_page()