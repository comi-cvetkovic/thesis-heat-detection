# Thesis Project: Fault Detection in District Heating Substations

This repository contains the working material for a master's thesis on anomaly/fault detection in district heating systems. The current goal is to replicate and adapt the method from the paper:

**HEAT: Hierarchical-constrained Encoder-Assisted Time series clustering for fault detection in district heating substations**

After reproducing the paper's approach, the method will be applied to sensor data from a hotel/building in Catalunya and extended with improvements suitable for the available data and thesis objectives.

## Project Goal

The project has three main objectives:

1. Understand and reproduce the HEAT method from the academic paper.
2. Apply the replicated method to the available hotel/district heating sensor data from Catalunya.
3. Propose, implement, and evaluate improvements to the original approach.

## Dataset Comparison and Method Implications

The available Montserrat / Abat Oliba data is meaningfully different from the dataset used in the HEAT paper. This affects how closely the original method should be reproduced and how much emphasis should be placed on clustering.

| Aspect | Montserrat / Abat Oliba project | HEAT example paper |
| --- | --- | --- |
| System type | Real micro-district heating network in Montserrat, Catalunya, with multiple buildings / heat exchangers. | Real district heating network in southern Shandong, China. |
| Scale | Much smaller: around 10-12 consumer/building-level datasets, plus generation plant data. | Much larger: 248 substations. |
| Time coverage | Stronger long-term coverage. Many temperature series span multiple years, and the DHC heating sheets inspected so far run up to July 2025. | Short but dense: January 2024 only, 31 days. |
| Sampling rate | Mostly high-frequency, often around 5-15 minute intervals depending on sheet/sensor. | Fixed 5-minute logging, giving 8,928 samples per substation. |
| Main columns | Most DHC building sheets contain timestamp, power, return temperature, and supply temperature. Abat Oliba internal data also contains richer building-level signals such as DH temperatures, room/floor temperatures, DHW temperatures, outdoor temperature, humidity, setpoints, and air quality. | Timestamp, primary supply temperature, primary return temperature, primary flow, outdoor temperature, delta-T, energy consumption, and water volume. |
| Flow data | Not consistently available directly. Flow can be estimated from power and delta-T using the supervisor formula, but units must be validated. | Direct flow rate is available in L/min. |
| Labels / known faults | Mostly unlabeled so far. This is the biggest weakness for evaluation. | Partially labeled with known fault types and normal behavior. |
| Network/topology information | Strong contextual advantage: reports, pipe/layout information, pump information, and building-specific context are available. | HEAT approximated topology from supply-temperature similarity rather than using real geographic layout directly. |
| Best suited method | Per-substation time-series anomaly detection, physics-informed features, robust thresholds, reconstruction error, and expert review. Clustering can still be used as a small supporting comparison, but it should not be the central method. | HEAT-style clustering is well suited because 248 substations provide many peers for cluster-based comparison. |

Practical implication: this thesis should treat HEAT as the reference paper and methodological inspiration, not as a method to reproduce unchanged. With only around 10-12 substations, cluster assignments will be less statistically stable and less useful for peer-group fault detection. The stronger direction is to build a robust reconstruction-based per-substation anomaly-detection pipeline using long time coverage, thermal features, operational context, and limited cross-substation comparison where it is defensible.

Updated technical direction:

1. Prioritize the autoencoder as the main method: reconstruct three-channel windows containing supply temperature, return temperature, and derived water flow.
2. Use per-substation baselines as interpretable references: low delta-T, rolling MAD, percentile thresholds, and power/delta-T/flow consistency checks.
3. Use clustering only as a secondary analysis: compare similar buildings, operating windows, or latent representations, but do not make the thesis depend on discovering many stable substation clusters.
4. Use the long historical coverage as the main strength: learn normal seasonal and operating patterns within each substation.
5. Add physics-informed validation: derive flow from `m = Power / (Cp * delta-T)`, check units, and flag physically inconsistent periods.
6. Evaluate through triangulation: plots, anomaly event tables, maintenance/alarm information if available, and supervisor/domain review.

## Repository Structure

```text
.
├── Articles/
│   └── Academic papers and supporting literature
├── Codes/
│   └── Source code, notebooks, experiments, and replication work
├── Data/
│   ├── Abat Oliba Building/
│   │   └── Main building/hotel sensor data
│   ├── DHC network/
│   │   └── District heating/cooling network data, reports, and drawings
│   └── old/
│       └── Older data exports and reference material
├── Materials/
│   └── Notes, supervisor material, slides, and supporting files
├── Results/
│   └── Experiment outputs, plots, tables, and model results
├── Thesis drafts/
│   └── Written thesis drafts and related documents
├── 1-s2.0-S2666546825000801-main.pdf
│   └── Main HEAT paper
└── README.md
```

## Important Local Files

Current files detected in the workspace:

- `1-s2.0-S2666546825000801-main.pdf` - main HEAT paper.
- `Articles/1-s2.0-S0360544224037940-main.pdf` - additional academic paper.
- `Data/Abat Oliba Building/Abat_Oliba/Abat_Oliba_Data.xlsx` - main building/hotel dataset.
- `Data/DHC network/data/District Heating_updated_16_07_2025_1.xlsx` - district heating data export.
- `Data/DHC network/data/District Heating_updated_16_07_2025_2.xlsx` - district heating data export.
- `Data/DHC network/data/District Cooling_updated_16_07_2025.xlsx` - district cooling data export.
- `Data/DHC network/Report.docx` - network report.
- `Data/DHC network/drawings/` - heating/cooling drawings.
- `Data/20250915_Modbus.xlsx` - Modbus/sensor metadata or register information.
- `Data/old/` - older data versions and building plan.

## Context From Previous ChatGPT Discussion

Recommended stack
1. Core language/environment

Use:

Python 3.11 or 3.12
Jupyter Notebook / JupyterLab for exploration
VS Code for writing reusable scripts
Conda environment for package management

Why: your project is experimental and data-heavy, so notebooks are useful for understanding the data, but final code should eventually be organized into scripts.

2. Data loading and cleaning

Use:

pandas for Excel loading, timestamp handling, resampling, interpolation, missing values, feature calculation.
NumPy for numerical operations.
openpyxl for reading .xlsx files.

Pandas has strong built-in support for time-series indexing, resampling, and date/time handling, which you will need for aligning supply temperature, return temperature, and flow data.

You will use this for:

timestamp
supply_temperature
return_temperature
flow_kg_s
delta_T = supply - return
power = flow * cp * delta_T
3. Visualization

Use:

matplotlib for thesis-quality plots.
Plotly for interactive exploration.
seaborn optionally for quick statistical plots, but final thesis figures can be cleaner in matplotlib.

You will need plots for:

supply vs return temperature,
ΔT over time,
flow over time,
power over time,
missing data heatmaps,
cluster comparisons,
anomaly markers.
4. Classical machine learning and clustering

Use:

scikit-learn for standard clustering, preprocessing, PCA, scaling, metrics.
SciPy for hierarchical clustering and linkage functions.
tslearn for time-series clustering and DTW-based comparisons.

Scikit-learn supports many clustering algorithms for unlabelled data, while tslearn is specifically built for time-series clustering and includes methods like time-series k-means and DTW-based tools.

Use these baselines:

Global MAD detection
HAC clustering
PCA + HAC
TimeSeriesKMeans
Spectral clustering
HEAT-like constrained HAC
5. Deep learning / autoencoder

For the Convolutional Autoencoder, I recommend PyTorch rather than TensorFlow/Keras.

Both are fine, but PyTorch is usually easier to debug and customize when you need to implement research-style models. PyTorch supports CPU and GPU tensor computation and is widely used for research workflows.

Use PyTorch for:

1D convolutional autoencoder,
latent representation extraction,
reconstruction error experiments,
possible LSTM autoencoder later.

TensorFlow/Keras is also valid, and TensorFlow has official autoencoder tutorials, but I would only choose it if you want a slightly simpler high-level API.

My recommendation:

PyTorch for the thesis implementation.
Keras only if you want faster/simple prototyping.
6. Anomaly detection

Implement this yourself in Python rather than relying on a black-box package.

You need custom logic anyway:

For each cluster:
    compute ΔT
    compute median ΔT
    compute MAD
    compute modified z-score
    flag low ΔT anomalies

Also test:

global MAD,
cluster-level MAD,
rolling-window MAD,
percentile threshold,
power/flow residual anomalies.

This will be easier to explain in the thesis than using a black-box anomaly package.

7. Experiment tracking

Use simple tools first:

CSV files for results,
saved plots,
a config.yaml file for experiment settings.

Later, use:

MLflow or Weights & Biases only if experiments become hard to track.

For your thesis, a simple results folder is probably enough:

results/
  figures/
  tables/
  models/
  processed_data/
  experiment_logs.csv
8. Project structure

I would organize it like this:

thesis-heat-detection/
│
├── data/
│   ├── raw/
│   ├── processed/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_global_anomaly_detection.ipynb
│   ├── 04_clustering_baselines.ipynb
│   ├── 05_autoencoder_clustering.ipynb
│   ├── 06_heat_method.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── features.py
│   ├── clustering.py
│   ├── autoencoder.py
│   ├── anomaly_detection.py
│   ├── evaluation.py
│   ├── plotting.py
│
├── configs/
│   └── experiment_config.yaml
│
├── results/
│   ├── figures/
│   ├── tables/
│   ├── models/
│
├── requirements.txt
└── README.md

This makes the project look serious and reproducible.

What I would use for each thesis stage
Stage	Tools
Read Excel data	pandas, openpyxl
Clean timestamps/missing values	pandas, NumPy
Feature engineering	pandas, NumPy
Plot signals	matplotlib, Plotly
Baseline anomaly detection	custom Python, SciPy
Clustering	scikit-learn, SciPy, tslearn
DTW distances	tslearn
Autoencoder	PyTorch
Results tables	pandas
Final figures	matplotlib
Report writing	Overleaf / LaTeX or Word
Version control	Git + GitHub

### High-Level Summary

Paste a short summary of what was already discussed:

```text
TODO: Paste summary here.
```

### Agreed Thesis Direction

Paste any agreed scope, research questions, or thesis framing:

```text
TODO: Paste thesis direction here.
```

### Important Decisions Already Made

Examples:

- Which data source is considered primary.
- Which sensors or variables should be used.
- Which time period should be analyzed first.
- Which baseline methods should be implemented.
- Which improvements to HEAT were considered promising.

```text
TODO: Paste decisions here.
```

### Open Questions

Paste unresolved questions from the previous chat:

```text
TODO: Paste open questions here.
```

## Paper Replication Notes

Use this section to collect details needed to replicate the HEAT paper.

### Method Summary

```text
TODO: Paste or write a concise explanation of the HEAT method.
```

### Original Paper Pipeline

Expected items to document:

- Input data format.
- Preprocessing steps.
- Time-series segmentation/windowing.
- Encoder architecture.
- Clustering method.
- Hierarchical constraints.
- Fault/anomaly scoring.
- Evaluation metrics.

```text
TODO: Paste paper pipeline details here.
```

### Assumptions Made by the Paper

```text
TODO: Paste assumptions here.
```

### Reproduction Checklist

- [ ] Extract exact method details from the paper.
- [ ] Identify required input variables.
- [ ] Recreate preprocessing pipeline.
- [ ] Implement or reproduce encoder model.
- [ ] Implement hierarchical-constrained clustering.
- [ ] Reproduce anomaly/fault detection logic.
- [ ] Validate reproduction on a small sample or synthetic test.
- [ ] Compare reproduced results with paper results where possible.

## Available Data Notes

Use this section to document what each dataset contains.

### Flow-Rate Calculation

Supervisor-provided formula for the mass flow rate on the user side of each DHC-connected heat exchanger:

```text
m = Power / (Cp * (Ts - Tr))
```

Where:

- `m` is mass flow rate in `kg/s`.
- `Power` is heat power in `W`.
- `Cp` is water specific heat capacity in `J/(kg C)`.
- `Ts` is supply temperature in `C`.
- `Tr` is return temperature in `C`.

The project config currently uses:

```text
Cp = 4180 J/(kg C)
```

Important unit check: if power is stored as `kW`, convert it to `W` before applying the formula.

### Main Building/Hotel Dataset

File:

```text
Data/Abat Oliba Building/Abat_Oliba/Abat_Oliba_Data.xlsx
```

Notes:

```text
TODO: Paste description of the dataset, sensors, columns, units, and date range.
```

### District Heating Data

Files:

```text
Data/DHC network/data/District Heating_updated_16_07_2025_1.xlsx
Data/DHC network/data/District Heating_updated_16_07_2025_2.xlsx
```

Notes:


```text
TODO: Paste description of district heating variables and metadata.
```

### District Cooling Data

File:

```text
Data/DHC network/data/District Cooling_updated_16_07_2025.xlsx
```

Notes:

```text
TODO: Paste description of cooling variables and whether they are relevant.
```

### Modbus / Sensor Metadata

File:

```text
Data/20250915_Modbus.xlsx
```

Notes:

```text
TODO: Paste useful metadata, sensor naming, register mappings, and units.
```

## Data Understanding Checklist

- [ ] List all available sheets in each Excel file.
- [ ] Identify timestamp columns and sampling frequency.
- [ ] Identify measured variables and units.
- [ ] Identify missing values and irregular sampling.
- [ ] Identify duplicate or inconsistent columns.
- [ ] Map raw sensor names to physical meaning.
- [ ] Determine which variables correspond to HEAT paper inputs.
- [ ] Select an initial time period for experiments.
- [ ] Decide whether labels, alarms, or maintenance logs are available.

## Planned Technical Workflow

1. Inspect all data files and create a data inventory.
2. Build a clean preprocessing pipeline.
3. Build autoencoder-ready three-channel windows: supply temperature, return temperature, and derived water flow.
4. Train a reconstruction-based autoencoder and score windows using reconstruction error.
5. Build per-substation anomaly-detection baselines using delta-T, derived flow, and rolling/seasonal thresholds as interpretable references.
6. Treat clustering as a secondary comparison or ablation, not the central thesis method.
7. Evaluate detected anomalies using available operational knowledge, labels, maintenance/alarm records, or expert review.
8. Save results, plots, and experiment notes in `Results/`.

## Candidate Improvements to Explore

Paste or refine improvement ideas from previous discussions:

```text
TODO: Paste improvement ideas here.
```

Possible categories:

- Better preprocessing for missing or irregular sensor data.
- Alternative encoder architectures.
- Smaller-scale clustering or operating-regime grouping as a secondary comparison.
- Domain-informed feature engineering.
- Robust anomaly scoring.
- Explainability for detected faults.
- Evaluation methods when labels are limited or unavailable.

## Experiment Log

Use this section to record experiments as they are run.

### Experiment Template

```text
Experiment ID:
Date:
Goal:
Data files:
Time range:
Variables used:
Preprocessing:
Model/method:
Parameters:
Results:
Observations:
Next action:
```

## Supervisor Notes

Paste relevant comments, constraints, or recommendations from the supervisor:

With this email, I would like to explain to you the simple equation for calculating the water flow rate (m) on the user side at each DHC-connected heat exchanger. m = Power/(Cp.(Ts-Tr)).
Where: m is the mass flow rate [kg/s]; Cp is the water specific heat coefficient [J/Kg.C]; Ts is the supply temperature [C], and Tr is the return temperature [C].
 
Also, I have recently set up a database recording data from all sensors in real time. I will provide you with access to this data once I have at least two months of recorded data

## Thesis Writing Notes

Use this section to collect writing-relevant ideas.

### Possible Research Questions

```text
TODO: Paste or draft research questions here.
```

### Contributions

```text
TODO: Paste possible thesis contributions here.
```

### Evaluation Plan

```text
TODO: Paste evaluation strategy here.
```

## Reproducibility Notes

Document software setup once the implementation starts.

```text
Recommended setup:

.\.venv\Scripts\Activate.ps1
python Codes/src/data_inventory.py --max-rows-per-sheet 5000
```

Current local setup:

- Python 3.11.9 is installed.
- A project-local virtual environment exists at `.venv/`.
- Dependencies from `requirements.txt` are installed in `.venv/`.

Potential future files:

- `requirements.txt` or `environment.yml`
- `Codes/`
- `Results/`
- `notebooks/`

## Immediate Next Steps

- [x] Paste relevant context from the previous ChatGPT project chat into this README.
- [x] Inspect the Excel files and create a dataset inventory.
- [x] Extract the HEAT paper methodology into implementation requirements.
- [x] Decide the first minimal replication target: `Ground floor` and `First floor` from the Abat Oliba workbook for a pipeline baseline.
- [x] Start a baseline script in `Codes/`.
- [x] Map the real district-heating DHC sheets before drawing thesis conclusions from the baseline.
- [x] Build the first autoencoder-ready dataset using supply temperature, return temperature, and derived water flow.
- [x] Train a first reconstruction autoencoder smoke test on `cons_hostatgeria_underfloor_hea`.
- [ ] Inspect autoencoder reconstruction-error windows and compare them with low-delta-T baseline anomalies.
- [ ] Add rolling or seasonal thresholds for per-substation anomaly detection.
- [ ] Validate power and flow units before using derived flow as a thesis feature.

## Current Code Entry Points

### Data Inventory

Script:

```text
Codes/src/data_inventory.py
```

Purpose:

- Lists workbook sheets.
- Summarizes rows, columns, missing values, and numeric columns.
- Flags candidate timestamp, supply-temperature, return-temperature, flow, power, and energy columns by name.
- Attempts to infer datetime ranges and sampling intervals for likely timestamp columns.

Outputs:

```text
Results/tables/data_inventory_sheets.csv
Results/tables/data_inventory_columns.csv
Results/tables/data_inventory_errors.csv
```

### Baseline Low Temperature-Separation Detection

Script:

```text
Codes/scripts/run_baseline_delta_t.py
```

Purpose:

- Reads timestamped Excel sheets whose real headers are preceded by blank/note rows.
- Computes `delta_t_c = Supply Temperature - Return Temperature`.
- Computes `temperature_separation_c = abs(delta_t_c)` so the first pipeline works on the likely cooling/climatization test sheets.
- Applies a robust MAD modified z-score baseline for low temperature separation.
- Saves compact summaries, detailed processed records, and figures.

Command:

```text
.\.venv\Scripts\python.exe Codes\scripts\run_baseline_delta_t.py
```

Outputs:

```text
Results/tables/baseline_delta_t_summary.csv
Results/processed_data/baseline_delta_t_ground_floor.csv
Results/processed_data/baseline_delta_t_first_floor.csv
Results/figures/baseline_delta_t_ground_floor.png
Results/figures/baseline_delta_t_first_floor.png
```

Current baseline result:

- `Ground floor`: 212,293 rows, 2022-01-27 to 2025-02-06, median temperature separation about 1.49 C, 0 anomalies at z <= -3.5.
- `First floor`: 288,435 rows, 2020-12-26 to 2025-02-06, median temperature separation about 2.24 C, 0 anomalies at z <= -3.5.

### DHC Heating Candidate Summary

Script:

```text
Codes/scripts/summarize_dhc_heating.py
```

Purpose:

- Summarizes likely district-heating candidate sheets from the DHC workbooks.
- Computes `delta_t_c = Supply Temperature - Return Temperature`.
- Reports date range, median power, median delta-T, positive delta-T fraction, and active-heating fraction.
- Estimates mass flow from power assuming power is in `kW`, using the supervisor formula.

Command:

```text
.\.venv\Scripts\python.exe Codes\scripts\summarize_dhc_heating.py
```

Output:

```text
Results/tables/dhc_heating_sheet_summary.csv
```

Current interpretation:

- `cons_abat_oliba`, `cons_hostatgeria_DHW_radiators`, `cons_hostatgeria_underfloor_hea`, and `cons_nostra_senyora` are the most relevant immediate DHC sheets from the second heating workbook.
- `cons_abat_cisneros`, `cons_abat_garriga`, and `cons_abat_marcet` are also technically usable but may be less central unless they map to the thesis building scope.
- `cons_nostra_senyora` includes a `flow (kg/s)` column, but the reported values do not match the supervisor formula under a simple `kW` power assumption. Treat that flow column as unvalidated until units are confirmed.

### DHC Low Delta-T Baseline

Script:

```text
Codes/scripts/run_dhc_delta_t_baseline.py
```

Purpose:

- Runs a low delta-T anomaly baseline on selected DHC heating sheets.
- Filters to active heating periods using `power > 0` and `Supply - Return > 0`.
- Computes robust MAD modified z-scores on active-heating `delta_t_c`.
- Flags unusually low active-heating delta-T values.

Command:

```text
.\.venv\Scripts\python.exe Codes\scripts\run_dhc_delta_t_baseline.py
```

Outputs:

```text
Results/tables/dhc_delta_t_baseline_summary.csv
Results/processed_data/dhc_delta_t_baseline_*.csv
Results/figures/dhc_delta_t_baseline_*.png
```

Current baseline result:

- `cons_abat_oliba`: 67,207 active rows, median active delta-T about 3.92 C, 0 anomalies at z <= -3.5.
- `cons_hostatgeria_DHW_radiators`: 258,918 active rows, median active delta-T about 5.46 C, 0 anomalies at z <= -3.5.
- `cons_hostatgeria_underfloor_hea`: 123,461 active rows, median active delta-T about 32.46 C, 940 anomalies at z <= -3.5.
- `cons_nostra_senyora`: 265,570 active rows, median active delta-T about 9.77 C, 0 anomalies at z <= -3.5.

### Autoencoder Window Preparation

Script:

```text
Codes/scripts/prepare_autoencoder_windows.py
```

Purpose:

- Builds fixed-length windows for the reconstruction autoencoder.
- Uses the supervisor-requested three input channels:
  - supply temperature
  - return temperature
  - derived water flow
- Derives water flow from `m = Power / (Cp * (Ts - Tr))`, assuming source power is in `kW`.
- Filters to active heating periods where `power > 0`, `Supply - Return > 0`, and derived flow is finite and positive.
- Resamples to a fixed 15-minute interval, interpolates short gaps, standardizes the three channels, and writes compressed NumPy windows.

Command:

```text
.\.venv\Scripts\python.exe Codes\scripts\prepare_autoencoder_windows.py
```

Outputs:

```text
Results/processed_data/autoencoder_windows_cons_hostatgeria_underfloor_hea.npz
Results/tables/autoencoder_windows_cons_hostatgeria_underfloor_hea_summary.csv
```

Current result:

- Sheet: `cons_hostatgeria_underfloor_hea`
- Features: `supply_temp_c`, `return_temp_c`, `derived_flow_kg_s`
- Resampling: 15 minutes
- Window length: 24 hours
- Window stride: 12 hours
- Minimum active-heating share per retained window: 60%
- Minimum complete-data share per retained window: 85%
- Prepared windows: 323
- Time range after active-heating resampling: 2022-01-10 to 2025-07-16

### Autoencoder Reconstruction Baseline

Scripts:

```text
Codes/src/autoencoder.py
Codes/scripts/train_autoencoder.py
```

Purpose:

- Trains a small 1D convolutional autoencoder on the prepared three-channel windows.
- The model input and output are the same shape: supply temperature, return temperature, and derived flow over one time window.
- Reconstruction error is used as the anomaly score.
- The first threshold is the 99th percentile of training reconstruction error.

Command:

```text
.\.venv\Scripts\python.exe Codes\scripts\train_autoencoder.py --epochs 10
```

Outputs:

```text
Results/models/autoencoder_cons_hostatgeria_underfloor_hea.pt
Results/tables/autoencoder_training_history_cons_hostatgeria_underfloor_hea.csv
Results/tables/autoencoder_scores_cons_hostatgeria_underfloor_hea.csv
Results/tables/autoencoder_summary_cons_hostatgeria_underfloor_hea.csv
Results/figures/autoencoder_reconstruction_error_cons_hostatgeria_underfloor_hea.png
```

Current smoke-test result:

- Windows: 323 total, split into 258 train windows and 65 test windows.
- Training loss ended around 0.49 after 10 epochs on the corrected window set.
- 99th-percentile training reconstruction threshold: about 2.222 MSE on normalized channels.
- Flagged windows: 4 total.
- Highest reconstruction-error windows currently start around 2024-04-03, 2024-04-04, and 2024-10-25.

### Flagged Autoencoder Window Inspection

Script:

```text
Codes/scripts/inspect_autoencoder_windows.py
```

Purpose:

- Inspects the top reconstruction-error windows from the autoencoder.
- Compares each flagged window against the raw three channels and the low delta-T baseline.
- Produces a summary table and one multi-panel figure per flagged window.

Command:

```text
.\.venv\Scripts\python.exe Codes\scripts\inspect_autoencoder_windows.py
```

Outputs:

```text
Results/tables/inspect_autoencoder_cons_hostatgeria_underfloor_hea_summary.csv
Results/figures/inspect_autoencoder_cons_hostatgeria_underfloor_hea_*.png
```

Current inspection result:

- The corrected top flagged windows are true 24-hour windows with 96 resampled points each.
- Three of the strongest flagged windows overlap heavily with low delta-T anomalies around 2024-04-03 to 2024-04-05.
- One flagged window around 2024-10-25 does not overlap low delta-T anomalies, which suggests the autoencoder may also detect a different abnormal operating regime.
