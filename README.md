# Anomaly Detection in District Heating Substations

This repository contains the code, result tables, and figures for a master's thesis on anomaly detection in district-heating substations. The project uses historical operational data from a small district-heating network and prepares the same workflow for later testing on live sensor data.

The work is inspired by the HEAT paper:

> HEAT: Hierarchical-constrained Encoder-Assisted Time series clustering for fault detection in district heating substations

HEAT is treated as a methodological reference, not as something copied unchanged. The available thesis dataset is smaller, has limited labels, and has longer historical coverage. For that reason, the main method in this project is a per-building reconstruction-based anomaly detector, with clustering used as a supporting interpretation layer.

## Current Thesis Direction

The current pipeline is:

1. Read district-heating Excel sheets.
2. Clean timestamps, active-heating periods, missing values, and irregular sampling.
3. Build 24-hour windows with three model channels:
   - supply temperature
   - return temperature
   - flow
4. Train a 1D convolutional autoencoder on historical windows.
5. Reconstruct each window and compute reconstruction error.
6. Flag anomalous windows using a training-distribution threshold, currently the 3-sigma rule.
7. Attribute each anomaly to the dominant feature: supply, return, or flow.
8. Compare anomaly results with engineering references such as low delta-T.
9. Use clustering as a secondary view of operating regimes and anomaly families.
10. Review outputs with the supervisor/domain expert because complete fault labels are not available.

The thesis currently focuses on seven heating-consumer sheets:

- `cons_abat_cisneros`
- `cons_abat_garriga`
- `cons_abat_marcet`
- `cons_abat_oliba`
- `cons_hostatgeria_DHW_radiators`
- `cons_hostatgeria_underfloor_hea`
- `cons_nostra_senyora`

## Why This Is an Unsupervised Problem

The historical data does not contain a complete set of confirmed fault labels. That means this project cannot yet report standard supervised metrics such as accuracy, recall, or F1-score against a trusted ground truth.

Instead, the evaluation uses a weak-label strategy:

- reconstruction-error distributions
- anomaly counts and anomaly rates
- dominant-feature attribution
- comparison with low delta-T events
- inspection of top anomaly windows
- cross-building consistency checks
- supervisor/domain interpretation

Future live data will be used to strengthen validation when operational context, event notes, alarms, or maintenance information become available.

## Method Summary

### Autoencoder

Each retained input window is a multivariate time series with shape:

```text
3 channels x 96 samples
```

The 96 samples correspond to 24 hours at 15-minute resolution.

The autoencoder contains:

```text
encoder:
  Conv1d
  ReLU
  MaxPool
  Conv1d
  ReLU
  MaxPool

decoder:
  ConvTranspose1d
  ReLU
  ConvTranspose1d
```

The model is trained to reconstruct normal-looking historical windows. A window is considered more anomalous when the reconstructed output differs strongly from the input.

### Thresholding

The final thesis result pack uses a 3-sigma threshold:

```text
threshold = mean(training_error) + 3 * std(training_error)
```

A window is flagged when its reconstruction error is above this threshold.

Earlier experiments also compared the 99th percentile threshold. The threshold comparison is kept because the two rules can behave differently depending on the shape of each building's training-error distribution.

### Dominant-Feature Attribution

For each flagged window, reconstruction error is also computed separately for each channel:

- supply temperature
- return temperature
- flow

The feature with the largest reconstruction error is treated as the dominant anomaly feature. This is currently the clearest way to explain whether an anomaly is supply-related, return-related, or flow-related.

### Clustering

Two clustering views have been explored:

1. Operating-regime clustering on all retained windows.
2. Anomaly-only clustering on flagged windows.

Clustering is not the main detector. It is used to organize and interpret patterns after reconstruction-based scoring.

## Repository Structure

```text
.
|-- Codes/
|   |-- scripts/          Main runnable scripts
|   `-- src/              Shared model, feature, and utility code
|-- Results/
|   |-- figures/          Generated figures used for supervisor notes and thesis drafting
|   |-- tables/           Generated CSV summaries and supervisor update notes
|   |-- models/           Trained model files, ignored by git
|   `-- processed_data/   Prepared windows and intermediate data, ignored by git
|-- Data/                 Raw/private data, ignored by git
|-- Articles/             Papers and PDFs, ignored by git
|-- Materials/            Local notes/material, ignored by git
|-- Thesis drafts/        Word drafts and templates, ignored by git
|-- requirements.txt
`-- README.md
```

## Why `Thesis drafts/` Is Not on GitHub

`Thesis drafts/` is intentionally ignored in `.gitignore`.

Reasons:

- Word files and exported PDFs are binary and can become large quickly.
- Drafts often contain supervisor comments, personal metadata, or unpublished writing.
- Versioning `.docx` files in git is usually not useful because diffs are unreadable.
- The thesis draft is being shared through the supervisor's shared folder instead.

The repository tracks the code and generated result assets needed to reproduce or explain the work. The written thesis draft itself should remain in the shared OneDrive/supervisor folder unless there is a specific reason to publish a PDF later.

## Main Scripts

Run commands from the repository root using the project virtual environment:

```powershell
.\.venv\Scripts\python.exe <script>
```

### Data Understanding

```text
Codes/src/data_inventory.py
Codes/scripts/summarize_dhc_heating.py
Codes/scripts/analyze_power_scaling.py
```

Purpose:

- inspect workbook sheets and columns
- identify likely timestamp, temperature, flow, and power columns
- summarize usable heating-consumer sheets
- sanity-check power/flow assumptions

### Baseline Engineering Checks

```text
Codes/scripts/run_baseline_delta_t.py
Codes/scripts/run_dhc_delta_t_baseline.py
```

Purpose:

- compute supply-return temperature difference
- detect unusually low delta-T periods
- provide an engineering reference for autoencoder anomalies

### Autoencoder Pipeline

```text
Codes/scripts/prepare_autoencoder_windows.py
Codes/scripts/train_autoencoder.py
Codes/scripts/inspect_autoencoder_windows.py
Codes/scripts/compare_autoencoder_runs.py
Codes/scripts/compare_autoencoder_lenses.py
```

Purpose:

- prepare 24-hour model windows
- train the 1D convolutional autoencoder
- compute reconstruction scores
- inspect top anomaly windows
- compare raw and stabilized flow variants
- compare results across buildings

### Interpretation and Clustering

```text
Codes/scripts/cluster_autoencoder_windows.py
Codes/scripts/cluster_detected_anomalies.py
Codes/scripts/summarize_anomaly_feature_types.py
Codes/scripts/build_supervisor_review_tables.py
Codes/scripts/plot_cross_building_comparisons.py
```

Purpose:

- summarize anomaly types
- cluster operating regimes
- cluster flagged anomaly windows
- build supervisor-review tables and figures
- compare anomaly counts across buildings

### Thesis Draft Helper

```text
Codes/scripts/revise_thesis_draft_june19.py
```

Purpose:

- local helper for updating the Word thesis draft
- not part of the anomaly-detection model itself
- kept so the current draft-generation work is documented

## Important Result Files

Useful tables:

```text
Results/tables/supervisor_update_2026-06-07.md
Results/tables/supervisor_results_sheet_2026-06-07.csv
Results/tables/threshold_method_comparison_2026-06-07.csv
Results/tables/anomaly_feature_type_sheet_summary_stabilized_log.csv
Results/tables/cluster_sheet_summary_stabilized_log.csv
```

Useful figures:

```text
Results/figures/thesis_selected7_anomaly_summary.png
Results/figures/thesis_selected7_feature_type_by_sheet.png
Results/figures/thesis_selected7_baseline_vs_autoencoder.png
Results/figures/thesis_selected7_window_cluster_distribution.png
Results/figures/threshold_distribution_by_sheet_2026-06-07.png
Results/figures/per_sheet_anomaly_feature_heatmaps_2026-06-07.png
Results/figures/reconstruction_overlay_cons_abat_garriga_stabilized_log_top01.png
Results/figures/reconstruction_overlay_cons_hostatgeria_underfloor_hea_stabilized_log_top01.png
```

## Local Setup

Create and activate a Python environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Most scripts assume the private data files exist locally under `Data/`.

## Reproducibility Notes

The repository intentionally does not include:

- raw Excel workbooks
- large intermediate processed arrays
- trained model checkpoints
- Word thesis drafts
- private PDFs or supervisor material

These are ignored through `.gitignore`. To reproduce the full workflow on another machine, place the private data files in the same local folder structure or update the paths in the scripts.

## Current Status

The current thesis draft is based on:

- seven-building historical result pack
- 3-sigma thresholding
- dominant-feature anomaly interpretation
- low delta-T comparison
- operating-regime clustering as a secondary view
- weak-label evaluation with supervisor review

The next major validation step is to apply the pipeline to the upcoming one to two months of live data and compare detected anomalies with supervisor/domain interpretation.
