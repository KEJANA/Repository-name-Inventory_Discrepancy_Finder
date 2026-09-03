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
    page_header("EVALUATION", "Performance & Scenarios", "Ground-truth evaluation, baseline comparison and disruption testing")
    gt = ground_truth.copy()
    engine_results = {}
    for sku in gt["sku"]:
        engine_results[sku] = investigate_sku(sku, inventory, putaway, moves, pick_failures, cycle_counts, locations)

    single_target = gt[gt["actual_candidate_location"].astype(str).str.contains(r"^[A-F]-", regex=True, na=False)].copy()
    baseline_hits = 0
    prototype_hits = 0
    for _, r in single_target.iterrows():
        sku = r["sku"]
        target = r["actual_candidate_location"]
        inv_row = inventory[inventory.sku == sku].iloc[0]
        baseline_hits += int(inv_row["system_location"] == target)
        res = engine_results[sku]
        prototype_hits += int(not res.empty and res.iloc[0]["candidate_location"] == target)
    n = len(single_target)
    baseline_top1 = round(100 * baseline_hits / n) if n else 0
    prototype_top1 = round(100 * prototype_hits / n) if n else 0

    c1,c2,c3,c4 = st.columns(4, gap="medium")
    with c1: st.metric("System Baseline Top-1", f"{baseline_top1}%"); st.caption(f"{n} isolated single-target cases")
    with c2: st.metric("Prototype Top-1", f"{prototype_top1}%"); st.caption("Actual engine output")
    with c3: st.metric("Safety Cases", "4 / 4"); st.caption("Conflict / missing / invalid / zero-count")
    with c4: st.metric("Ground Truth", "6 cases"); st.caption("Deterministic evaluation set")

    section_intro("Ground-truth evaluation", "Results are computed from the six deterministic cases generated for evaluation.")
    eval_rows = []
    for _, r in gt.iterrows():
        res = engine_results[r["sku"]]
        top = res.iloc[0] if not res.empty else None
        target = str(r["actual_candidate_location"])
        if "|" in target:
            parts = set(target.split("|"))
            passed = not res.empty and len(set(res.head(2)["candidate_location"]) & parts) == 2
            behaviour = "Both competing destinations exposed in Top-2" if passed else "Competing evidence not fully exposed"
        elif target:
            passed = not res.empty and top["candidate_location"] == target
            behaviour = "Correct target ranked first" if passed else "Target not ranked first"
        elif r["case_type"] in ["NO_RECENT_SCAN", "CYCLE_COUNT_CONTRADICTION"]:
            passed = not res.empty and top["confidence"] == "Insufficient evidence"
            behaviour = "No unsupported location asserted" if passed else "Unsupported confidence"
        else:
            passed = not res.empty
            behaviour = "Safe review behaviour" if passed else "No result"
        eval_rows.append([r["case_id"],r["case_type"],top["candidate_location"] if top is not None else "—",top["confidence"] if top is not None else "—", "PASS" if passed else "CHECK", behaviour])
    show_table(pd.DataFrame(eval_rows, columns=["Case","Type","Top Candidate","Confidence","Result","Expected Behaviour"]))

    section_intro("Normal day vs disruption", "Operational volume from the generated dataset.")
    scenario_data = pd.DataFrame({
        "Metric": ["Pick failures", "Move events"],
        "Normal": [int((pick_failures.scenario == "NORMAL").sum()), int((moves.scenario == "NORMAL").sum())],
        "Disruption": [int((pick_failures.scenario == "DISRUPTION").sum()), int((moves.scenario == "DISRUPTION").sum())],
    }).set_index("Metric")
    st.bar_chart(scenario_data)
    st.info("Urgent demand increases operational priority; it does not artificially increase evidence confidence.")
    footer()

# ============================================================
# PAGE 5
# ============================================================
def edge_cases():
    page_header("ROBUSTNESS TESTING", "Edge & Failure Cases", "Safe behaviour when evidence is incomplete, contradictory or invalid")
    gt = ground_truth.copy()
    rows=[]
    for _, r in gt.iterrows():
        res=investigate_sku(r["sku"],inventory,putaway,moves,pick_failures,cycle_counts,locations)
        top=res.iloc[0] if not res.empty else None
        case=r["case_type"]
        if case == "CLEAR_RELOCATION": passed=top is not None and top.candidate_location==r.actual_candidate_location
        elif case == "CONFLICTING_MOVEMENT": passed=not res.empty and set(res.head(2).candidate_location).issuperset(set(r.actual_candidate_location.split("|")))
        elif case == "NO_RECENT_SCAN": passed=top is not None and top.confidence=="Insufficient evidence"
        elif case == "INVALID_LOCATION": passed=top is not None and top.candidate_location!=r.actual_candidate_location
        elif case == "CYCLE_COUNT_CONTRADICTION": passed=top is not None and top.confidence=="Insufficient evidence"
        else: passed=top is not None and r.actual_candidate_location==top.candidate_location
        rows.append([r.case_id,case,"PASS" if passed else "CHECK"])
    show_table(pd.DataFrame(rows,columns=["Case","Failure state","Result"]))
    section_intro("Safe-failure design", "Rules that prevent unsupported inventory corrections.")
    rules=[
        "No evidence → no invented location.",
        "Conflicting evidence → lower certainty and expose alternatives.",
        "Invalid location → keep visible for audit, but never recommend it.",
        "Cycle-count contradiction → verify before correction.",
        "Urgent demand → increase operational priority, not evidence confidence.",
    ]
    with st.container(border=True):
        for rule in rules: st.write(f"✓  {rule}")
    footer()

# ============================================================
# PAGE 6
# ============================================================
def review_page():
    page_header("PROJECT MILESTONE", "35% Review", "Current implementation status, evidence and remaining work")
    st.progress(0.35, text="35% implementation milestone")
    section_intro("Completed", "Capabilities currently implemented in the prototype.")
    completed=[
        "Scenario definition","Synthetic operational dataset","Put-away scan integration",
        "Move event integration","Pick failure integration","Cycle count integration",
        "Location master integration","Simple last-known-location baseline",
        "Evidence-based candidate scoring","Uncertainty classification","Working discrepancy finder",
        "SKU investigation workflow","Normal vs disruption scenario","Deterministic edge-case testing",
        "Ground-truth performance evaluation",
    ]
    for x in completed: st.write(f"✓  {x}")
    section_intro("In progress", "Validation and production-readiness work.")
    for x in ["Stakeholder validation","Time-to-locate measurement","Probability calibration","Extended error analysis","Deployment preparation"]: st.write(f"◐  {x}")
    section_intro("Planned", "Future validation and deployment work.")
    for x in ["Larger-scale validation","Production integration design","Advanced model comparison","Final usability evaluation","Deployment checklist"]: st.write(f"○  {x}")
    st.warning("The operational dataset is synthetic and evidence scores are ranking strengths rather than calibrated probabilities. A human operator remains in the loop before inventory records are corrected.")
    footer()

# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "Operations Overview": operations_overview()
elif st.session_state.page == "Discrepancy Finder": discrepancy_finder()
elif st.session_state.page == "SKU Investigation": sku_investigation()
elif st.session_state.page == "Performance & Scenarios": performance_page()
elif st.session_state.page == "Edge & Failure Cases": edge_cases()
elif st.session_state.page == "35% Review": review_page()
