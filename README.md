# Inventory Discrepancy Finder

An evidence-based inventory investigation prototype for e-commerce fulfilment centres.

## Problem

In fulfilment centres, physical inventory can become difficult to locate when the recorded system location does not match the actual stock location. This can cause pick failures, delays and additional manual investigation.

This project helps identify the most likely location of missing inventory using operational scan and movement evidence.

## Proposed Solution

The system combines:

- Put-away scans
- Move events
- Pick failures
- Cycle counts
- Location master data

For a selected SKU, the discrepancy engine generates and ranks candidate locations based on available evidence.

The system communicates uncertainty using confidence levels and flags low-confidence or contradictory cases for human verification instead of automatic inventory correction.

## Key Features

- Inventory discrepancy investigation
- SKU-level evidence analysis
- Evidence-based candidate location ranking
- Confidence and uncertainty classification
- WMS/system-location baseline comparison
- Ground-truth evaluation
- Normal-day and disruption scenarios
- Streaming event-feed validation
- Automated testing
- Data-quality monitoring
- Human-in-the-loop verification
- Audit trail for investigation decisions
- Investigation-effort proxy
- Controlled self-validation

## Application Pages

1. **Operations Overview** – Overall fulfilment and inventory information
2. **Discrepancy Finder** – Identify suspicious inventory locations
3. **SKU Investigation** – Review evidence for a selected SKU
4. **Performance & Scenarios** – Compare baseline and prototype performance
5. **Edge & Failure Cases** – Test uncertain and contradictory situations
6. **70% Review** – Review implementation status, data quality, monitoring and validation evidence

## End-to-End Workflow

The prototype follows this workflow:

1. Incoming event feed
2. Data validation
3. Discrepancy detection
4. Candidate location ranking
5. Uncertainty communication
6. Human verification
7. Audit trail
8. Prototype monitoring

## Project Structure

```text
Inventory_Discrepancy_Finder/
│
├── app.py
├── discrepancy_engine.py
├── generate_data.py
├── evaluation.py
├── ranking_evaluation.py
├── stakeholder_validation.py
├── stream_loader.py
├── requirements.txt
│
├── data/
│   ├── inventory.csv
│   ├── putaway_scans.csv
│   ├── move_events.csv
│   ├── pick_failures.csv
│   ├── cycle_counts.csv
│   ├── location_master.csv
│   ├── ground_truth.csv
│   └── audit_log.csv
│
└── tests/
    ├── test_engine.py
    ├── test_baseline.py
    ├── test_edge_cases.py
    ├── test_evaluation.py
    ├── test_ranking_evaluation.py
    ├── test_stakeholder_validation.py
    └── test_stream_loader.py
Evaluation Results
The prototype includes six deterministic ground-truth scenarios.
Ranking Evaluation
Metric	Result
Recoverable cases	2/2
Recoverable Top-1 – Baseline	0/2 (0%)
Recoverable Top-1 – Prototype	2/2 (100%)
Overall Top-1	33.3%
Overall Top-3	100%
Overall Top-5	100%
Safe-failure cases	4/4


The recoverable Top-1 comparison evaluates the two scenarios where a correct location can be recovered from the available evidence.
The remaining scenarios evaluate safe handling of uncertainty, missing evidence, invalid locations and contradictory evidence.
The evidence score is used as a ranking strength and is not presented as a calibrated probability.
Automated Testing
The project includes an automated pytest suite covering:
- Discrepancy engine behaviour
- Baseline comparison
- Edge and failure cases
- Investigation-effort evaluation
- Ranking evaluation
- Stakeholder-validation workflow
- Streaming event-feed validation
Current test result:
35/35 tests passed
Streaming Event-Feed Validation
The prototype includes a lightweight streaming-data loader that validates incoming CSV event feeds.
Supported event feeds include:
- Put-away events
- Move events
- Pick failures
- Cycle counts
The loader validates required columns, timestamps and file availability before events are used by the prototype.
This simulates integration with incoming WMS/API event data without claiming a live production WMS connection.
Human Verification and Audit Trail
The prototype uses a human-in-the-loop approach.
Operators can review the recommended location, evidence and uncertainty before deciding whether to proceed with physical verification or investigate further.
Investigation decisions are recorded in an audit trail for traceability.
Investigation Effort
A prototype investigation-effort proxy is included to compare the amount of historical evidence that would need to be reviewed against the ranked candidate set produced by the prototype.
This is a prototype measurement and should not be interpreted as a real warehouse time-to-locate study.
A real user-timing study is planned for a later stage.
Data Quality Monitoring
The 70% prototype includes monitoring across the operational datasets to check:
- Dataset availability
- Row counts
- Required columns
- Timestamp validity
- Data completeness
Safety Approach
The system is designed to avoid false certainty.
When evidence is weak or contradictory, the system reports lower confidence and recommends verification rather than automatically changing inventory records.
Human verification is required before inventory correction.
Technology
- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Scikit-learn
- Pytest
- Synthetic fulfilment-centre operational data
- Evidence-based candidate ranking
How to Run
Install the dependencies:
pip install -r requirements.txt

Generate the dataset if required:
python3 generate_data.py

Run the Streamlit application:
streamlit run app.py

Run the automated tests:
pytest -q

Responsible AI
The prototype communicates uncertainty through confidence levels and keeps humans involved in inventory correction decisions.
Synthetic data is used during development and evaluation. Before production deployment, the system should be validated against real operational data and monitored for incorrect recommendations.
The evidence score is a ranking signal rather than a calibrated probability.
Project Status
70% Implementation Milestone – Completed
The current prototype includes:
- End-to-end working Streamlit application
- Multi-signal discrepancy engine
- Evidence-based candidate ranking
- Confidence and uncertainty handling
- Baseline comparison
- Ground-truth evaluation
- Normal and disruption scenarios
- Streaming event-feed validation
- Automated testing
- Data-quality monitoring
- Human verification workflow
- Audit trail
- Investigation-effort proxy
- Controlled self-validation
Beyond 70%
The following are intentionally left for later stages:
- External stakeholder/user validation
- Real warehouse time-to-locate study
- Probability calibration
- Live WMS/API integration
- Production deployment
These items are not claimed as completed in the current 70% milestone.
