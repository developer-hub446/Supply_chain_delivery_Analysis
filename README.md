# Supply Chain Delivery and Inventory Risk

Which suppliers miss delivery commitments?

🔗 **[Live dashboard](https://developer-hub446.github.io/supply-chain-delivery-analysis/outputs/dashboard.html)**

## Overview

A distributor needs to prioritize supplier discussions using comparable delivery measures. This intermediate portfolio case study contains an original dataset, executable Python and SQL, an exploratory analysis, a notebook with saved outputs and an offline dashboard. It is designed for learning, portfolio development and interview practice.

**Data status:** Synthetic. **Observation period:** Fictional 2025. **Author:** Rohan Kumar.

## Problem statement

- **Business question:** Which suppliers miss delivery commitments?
- **Task:** Measure on-time-in-full delivery and identify low inventory coverage.
- **Skills demonstrated:** OTIF · fill rate · inventory coverage.
- **Decision supported:** Prioritize an investigation or controlled test using reproducible evidence.

## STAR case study

### Situation
A distributor needs to prioritize supplier discussions using comparable delivery measures.

### Task
Measure on-time-in-full delivery and identify low inventory coverage.

### Action
Validate ordered versus delivered units, combine timeliness and completeness at purchase-order grain and inspect supplier coverage. The workflow includes source profiling, explicit metric definitions, Python calculations, SQL checks and a documented handoff.

### Result
The executed analysis produced OTIF (%): 24.5385; Unit fill rate (%): 96.9342; Snapshots below 7 days coverage: 777.0000. The notebook also exports a group-level summary and an SQL reconciliation. These are measured analytical outputs from synthetic data; no operational improvement has been demonstrated.

## Dataset

- **Availability:** Included at [`data/raw.csv`](data/raw.csv).
- **Source:** Original simulation in [`generate_data.py`](generate_data.py), seed `202605`.
- **Dictionary and grain:** [`data/README.md`](data/README.md).
- **License:** Included synthetic data is CC0-1.0; code is MIT licensed.
- No external data download, credentials or personal records are required.
- Simulated relationships are teaching assumptions, not facts about an industry.

## KPI definitions and analytical decisions

One row per purchase order with a separate illustrative inventory snapshot for that order. OTIF requires both actual_days ≤ promised_days and full units delivered; fill rate is total delivered / total ordered. Coverage = stock / daily demand. Snapshot counts are not unique SKU counts.

Validate ordered versus delivered units, combine timeliness and completeness at purchase-order grain and inspect supplier coverage.

## Project workflow

1. Read the source and inspect its grain, missing values and duplicates.
2. Validate the data contract and handle fields according to their business meaning.
3. Calculate the defined metrics and segment-level summaries, then explore distributions, failure modes (late, short or both), monthly OTIF and low-coverage snapshots by supplier.
4. Run SQLite aggregation and reconcile shared measures against Python.
5. Generate the chart, CSV exports and standalone HTML dashboard.
6. Interpret the evidence, document limits and propose a next validation step.

## Verified results

The notebook was executed against the included dataset with an isolated in-process IPython session. Tables, printed checks and chart outputs remain embedded in the notebook.

| Metric | Executed value |
|---|---:|
| OTIF (%) | 24.5385 |
| Unit fill rate (%) | 96.9342 |
| Snapshots below 7 days coverage | 777.0000 |

These values describe this synthetic dataset and dependency environment. They are a reproducibility record, not a production benchmark.

![Analysis overview](outputs/overview.png)

## Evidence-based recommendation

Beacon has the lowest OTIF rate (21.90%). Review order size, lead time and delay causes before changing suppliers.

![Supporting analysis](outputs/detail.png)

The notebook contains the supporting breakdown in `outputs/detail.csv`. This recommendation is an investigation or validation step, not a claim of achieved impact.

## Dashboard and output files

View the [live dashboard](https://developer-hub446.github.io/supply-chain-delivery-analysis/outputs/dashboard.html) or download or clone [the repository](https://github.com/developer-hub446/supply-chain-delivery-analysis) and open [`outputs/dashboard.html`](outputs/dashboard.html) in a browser. It works offline and provides KPI cards, a chart and a searchable summary table. The text filter only filters table rows; it does not recompute cards or charts. GitHub's file view does not execute HTML dashboards.

| File | Purpose |
|---|---|
| [`analysis.ipynb`](analysis.ipynb) | Narrative analysis with executed code, tables and chart |
| [`analysis.py`](analysis.py) | Script companion with the same analysis code |
| [`analysis.sql`](analysis.sql) | Four SQLite queries over validated `facts`: supplier KPIs, failure modes, monthly OTIF, lowest-coverage orders |
| [`outputs/metrics.json`](outputs/metrics.json) | Machine-readable verified KPIs |
| [`outputs/summary.csv`](outputs/summary.csv) | Group-level analysis for Excel or BI tools |
| [`outputs/analysis_ready.csv`](outputs/analysis_ready.csv) | Validated analysis facts |
| [`outputs/sql_results.csv`](outputs/sql_results.csv) | Supplier KPI query results (reconciled to Python) |
| [`outputs/data_quality.csv`](outputs/data_quality.csv) | Source profiling evidence |
| [`outputs/detail.csv`](outputs/detail.csv) | Delay severity and median coverage by supplier |

## How to run

Requires Python 3 with `pandas`, `numpy`, `matplotlib` and `jupyterlab`:

```bash
python -m pip install pandas numpy matplotlib jupyterlab
python -m jupyterlab analysis.ipynb
```

Run notebook cells from top to bottom. To execute as a script from the project folder:

```bash
python analysis.py
```

To rebuild the original dataset:

```bash
python generate_data.py
```



## Limitations

Coverage is a snapshot heuristic using average daily demand. It comits variability, replenishment timing and service-level safety stock.

## Recommended next step

Introduce SKU-level demand distributions and validate an inventory policy over time.


## Technologies

Python, Pandas, NumPy, SQLite, Matplotlib, Jupyter and HTML.

## Author

**Rohan Kumar**

[GitHub](https://github.com/developer-hub446) · [LinkedIn](https://www.linkedin.com/in/rohankumarray/) · [Email](mailto:rk7038303@gmail.com)
