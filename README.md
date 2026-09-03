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

For a selected SKU, the discrepancy engine generates and ranks candidate locations based on available evidence. The system also provides a confidence level to communicate uncertainty.

Low-confidence or contradictory cases are flagged for manual verification instead of automatic correction.

## Key Features

- Inventory discrepancy investigation
- SKU-level evidence analysis
- Evidence-based location ranking
- Confidence classification
- WMS/system-location baseline comparison
- Ground-truth evaluation
- Safety and failure-case testing
- Normal day vs urgent-demand disruption scenario
- Human-in-the-loop verification

## Application Pages

1. **Operations Overview** – Overall fulfilment and inventory information
2. **Discrepancy Finder** – Identify suspicious inventory locations
3. **SKU Investigation** – Review evidence for a selected SKU
4. **Performance & Scenarios** – Compare baseline and prototype performance
5. **Edge & Failure Cases** – Test uncertain and contradictory situations

## Project Structure

```text
Inventory_Discrepancy_Finder/
│
├── app.py
├── discrepancy_engine.py
├── generate_data.py
├── requirements.txt
│
└── data/
    ├── putaway_scans.csv
    ├── move_events.csv
    ├── pick_failures.csv
    ├── cycle_counts.csv
    ├── locations.csv
    ├── skus.csv
    └── ground_truth_cases.csv
Evaluation Results

The prototype was evaluated using six ground-truth scenarios.

Metric	Result
System/WMS Baseline Top-1	0% (0/2)
Prototype Top-1	100% (2/2)
Safety Cases	4/4 (100%)
Ground-truth Cases	6

The Top-1 comparison uses recoverable scenarios. The remaining scenarios test safe handling of uncertainty, missing evidence, invalid locations and contradictory evidence.

Safety Approach

The system is designed to avoid false certainty.

When evidence is weak or contradictory, the system reports low or insufficient confidence and recommends verification rather than automatically changing inventory records.

Technology
Python
Pandas
Streamlit
Synthetic fulfilment-centre data
Evidence-based ranking
How to Run

Install the dependencies:

pip install -r requirements.txt

Generate the dataset if required:

python3 generate_data.py

Run the Streamlit application:

streamlit run app.py
Responsible AI

The prototype communicates uncertainty through confidence levels and keeps humans involved in inventory correction decisions.

Synthetic data is used during development and evaluation. Before production deployment, the system should be validated against real operational data and monitored for incorrect recommendations.

Project Status

Review 1 – 35% Project Completion

The current prototype includes the end-to-end application, discrepancy engine, synthetic dataset, baseline comparison, ground-truth evaluation, safety testing and usability-oriented dashboard.

Future work includes stakeholder validation, broader performance testing and deployment readiness.


### GitHub-ல add பண்ணுவது

Repo open பண்ணி:

**Add file → Create new file → filename:**

```text
README.md
