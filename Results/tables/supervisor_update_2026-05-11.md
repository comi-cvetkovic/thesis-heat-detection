# Supervisor Update - 2026-05-11

## 1. What was done since the last session

The work moved from setup and simple baselines into a first reconstruction-based anomaly-detection pipeline.

Main steps completed:

1. Identified the most relevant district-heating sheets from the DHC exports.
2. Built a simple low delta-T anomaly baseline on the DHC sheets for comparison.
3. Switched the main method toward an autoencoder, following the supervisor's emphasis on reconstruction.
4. Used the three requested channels as autoencoder input:
   - supply temperature
   - return temperature
   - derived water flow from `m = Power / (Cp * (Ts - Tr))`
5. Built a preprocessing pipeline that:
   - reads the DHC sheet
   - converts timestamps
   - derives flow
   - keeps active-heating periods
   - resamples to 15-minute intervals
   - creates 24-hour windows with 12-hour stride
6. Trained first convolutional autoencoders for several candidate sheets.
7. Inspected the top flagged windows and compared them to the low delta-T baseline.
8. Added a second flow-based anomaly lens that is less sensitive to near-zero delta-T blow-ups.

## 2. What the autoencoder is doing

The autoencoder receives a 24-hour multivariate time window and tries to reconstruct it.

In this project, each input window has three channels:

- `Supply temperature`
- `Return temperature`
- `Derived water flow`

At 15-minute resolution, one 24-hour window contains:

- `96` time steps
- `3` channels

So one input is effectively a `3 x 96` time-series block.

The model structure is:

`input window -> encoder -> compressed latent representation -> decoder -> reconstructed window`

The training objective is:

`make reconstructed window as close as possible to original window`

Interpretation:

- If a window looks like normal operating behavior that the model has learned, reconstruction error is low.
- If a window looks unusual, reconstruction error is high.

So the anomaly score is:

`reconstruction error = mean squared difference between original and reconstructed window`

This is why the method is called reconstruction-based anomaly detection.

## 3. Important preprocessing detail

An early issue appeared in the first windowing version: "24-hour windows" could accidentally be built from compressed active-only points rather than true calendar windows.

That was corrected.

The current windowing logic now keeps only real calendar windows that satisfy:

- minimum active-heating share: `60%`
- minimum complete-data share: `85%`

This correction made the anomaly results much more trustworthy.

## 4. Current results

### 4.1 Multi-sheet raw-flow autoencoder comparison

Current summary:

| Sheet | Windows | Flagged windows | Notes |
| --- | ---: | ---: | --- |
| `cons_abat_oliba` | 955 | 8 | Strong anomalies, but initially dominated by very small delta-T causing large derived-flow values |
| `cons_hostatgeria_underfloor_hea` | 323 | 4 | Strongest interpretable case |
| `cons_hostatgeria_DHW_radiators` | 1075 | 13 | Harder to interpret |
| `cons_nostra_senyora` | 1111 | 9 | Harder to interpret, and flow consistency is questionable |

Interpretation:

- `cons_hostatgeria_underfloor_hea` is currently the best candidate for a thesis case study.
- `cons_abat_oliba` is interesting, but the raw flow channel can be dominated by very small delta-T values.
- `cons_hostatgeria_DHW_radiators` and `cons_nostra_senyora` still need more domain clarification before they can be used confidently.

### 4.2 Best current case: `cons_hostatgeria_underfloor_hea`

Raw-flow autoencoder result:

- `323` windows total
- `258` training windows
- `65` test windows
- `4` flagged windows

Top flagged windows:

- `2024-04-03 18:45` to `2024-04-04 18:45`
- `2024-04-03 06:45` to `2024-04-04 06:45`
- `2024-04-04 06:45` to `2024-04-05 06:45`
- `2024-10-25 18:45` to `2024-10-26 18:45`

Interpretation:

- Three of the top flagged windows overlap strongly with low delta-T anomalies.
- One flagged window around `2024-10-25` does not overlap low delta-T, which suggests the autoencoder may also detect a different abnormal operating regime.

This is currently the strongest result because:

1. the anomaly windows are few and interpretable
2. several overlap with a simple engineering baseline
3. the signal remains stable under a second flow lens

### 4.3 Second lens: stabilized flow feature

To reduce the effect of very small delta-T on the derived-flow channel, a second feature lens was added.

The stabilized flow feature does three things:

1. floors the delta-T denominator at `2.0 C`
2. clips the upper flow tail at the `99.5%` quantile
3. applies `log1p` scaling

This gives a second autoencoder lens:

- `raw` lens: direct derived flow
- `stabilized_log` lens: more numerically stable flow-derived feature

#### Lens comparison

| Sheet | Flow lens | Flagged windows | Top overlap with low delta-T |
| --- | --- | ---: | ---: |
| `cons_abat_oliba` | raw | 8 | 0 |
| `cons_abat_oliba` | stabilized_log | 12 | 0 |
| `cons_hostatgeria_underfloor_hea` | raw | 4 | 3 |
| `cons_hostatgeria_underfloor_hea` | stabilized_log | 4 | 3 |

Interpretation:

- For `cons_abat_oliba`, the stabilized lens is better behaved because the top anomalies are no longer obviously just flow blow-ups caused by near-zero delta-T.
- For `cons_hostatgeria_underfloor_hea`, the stabilized lens changes little, which is good. That suggests the underfloor-heating anomaly signal is not an artifact of the raw flow calculation.

## 5. Working conclusions

Current conclusions are provisional, but defensible:

1. Reconstruction-based anomaly detection is now working end to end on the real DHC data.
2. `cons_hostatgeria_underfloor_hea` is currently the best case study for deeper analysis.
3. `cons_abat_oliba` is also interesting, but its anomalies are more sensitive to how the flow feature is constructed.
4. The stabilized-flow lens is useful and should be kept as a safer secondary view.
5. The autoencoder is not only rediscovering low delta-T anomalies; at least one flagged window in the underfloor-heating sheet appears to represent a different abnormal regime.

What cannot yet be claimed:

- These anomalies are confirmed physical faults.
- The best flow formulation is finalized.
- The power units and flow interpretation are fully validated for all sheets.

So the current status is:

`credible anomaly candidates, not confirmed fault diagnoses`

## 6. How to explain the method verbally

Short version for discussion:

"We trained an autoencoder to reconstruct 24-hour windows of supply temperature, return temperature, and derived water flow. The model learns normal operating behavior. When the reconstruction error is high, that window is treated as anomalous because the model cannot represent it well using the normal patterns it learned."

Slightly longer version:

"The method uses three physically meaningful channels. Each day is turned into a short multivariate time series. The encoder compresses that daily behavior into a compact latent representation, and the decoder reconstructs the original signals. Reconstruction error is then used as an anomaly score. We compare that score with a simple low delta-T baseline to see whether the autoencoder is finding the same events or additional abnormal regimes."

## 7. Detailed explanation of how the autoencoder works

This section explains the implemented method in more detail.

### 7.1 What goes into the model

The model does not see raw Excel rows directly. It sees processed windows.

For one selected sheet:

1. The script reads timestamped sensor data.
2. It creates three channels:
   - `supply_temp_c`
   - `return_temp_c`
   - flow feature
3. The flow feature is either:
   - `derived_flow_kg_s` from the direct formula
   - or `stabilized_flow_log_feature` from the safer second lens
4. The data is filtered to active-heating periods:
   - power must be positive
   - `Supply - Return` must be positive
   - the flow feature must be finite and positive
5. The data is resampled to `15-minute` intervals.
6. The time series is split into overlapping `24-hour` windows with `12-hour` stride.

At 15-minute resolution:

- `24 hours = 96 time steps`
- `3 channels = supply, return, flow`

So one model input is:

`3 x 96`

This means:

- row 1 = supply temperature over a day
- row 2 = return temperature over a day
- row 3 = flow feature over a day

### 7.2 What the encoder does

The encoder is the compression part of the network.

Its purpose is to take a full daily multivariate signal and turn it into a smaller internal representation that still preserves the important structure of the window.

In the current model:

1. A 1D convolution scans the time dimension and learns local temporal patterns.
2. A `ReLU` nonlinearity keeps the model expressive.
3. A max-pooling layer reduces the temporal resolution by half.
4. A second convolution learns higher-level patterns.
5. Another max-pooling step compresses the representation again.

So the encoder gradually turns:

`3 x 96 -> richer hidden features -> shorter compressed sequence`

The compressed output is often called the latent representation.

Interpretation:

- similar daily operating windows should map to similar latent patterns
- unusual windows should be harder to represent compactly

### 7.3 What the decoder does

The decoder is the reconstruction part.

It takes the compressed latent representation and expands it back toward the original shape using transpose convolutions.

Its job is:

`latent representation -> reconstructed 3 x 96 window`

So the model output has the same dimensions as the input:

- reconstructed supply temperature
- reconstructed return temperature
- reconstructed flow feature

The decoder is not trying to predict the future. It is trying to rebuild the same window it was given.

### 7.4 What training means

Training means adjusting the model weights so that reconstruction becomes as accurate as possible for the training windows.

For each training batch:

1. The model receives the original normalized window.
2. It produces a reconstructed window.
3. The training loss is computed as mean squared error between the two.

The loss is:

`mean((reconstructed - original)^2)`

This happens over:

- all three channels
- all 96 time steps
- all windows in the batch

The optimizer then updates the model weights to reduce this error.

The training objective is therefore:

`learn normal historical daily behavior well enough to reconstruct it`

### 7.5 What reconstruction error means

After training, each window gets a single scalar score:

`reconstruction_mse`

This score is the average squared difference between:

- the original window
- the reconstructed window

Low score means:

- the model can reproduce the window well
- the window looks similar to learned normal patterns

High score means:

- the model reconstructs the window poorly
- the window is unusual relative to the training data

### 7.6 How a window is flagged

The current flagging rule is simple and unsupervised.

1. Use the first `80%` of windows in chronological order as training windows.
2. Train the autoencoder on those windows.
3. Compute reconstruction error for all windows.
4. Compute the `99th percentile` of training reconstruction error.
5. Flag any window whose reconstruction error is above that threshold.

So the anomaly rule is:

`flag window if reconstruction_error > training_p99_threshold`

Important implication:

- some training windows can also be flagged
- that is expected, because the threshold is derived from the training error distribution itself

This is not a bug. It simply means those windows are among the most unusual windows even within the training period.

### 7.7 Why the second flow lens was needed

The direct derived-flow formula is:

`m = Power / (Cp * delta-T)`

Problem:

- if `delta-T` becomes very small, the denominator becomes very small
- then the derived flow can become unrealistically large
- that large flow can dominate the autoencoder input and produce anomalies that are driven more by arithmetic instability than by real behavior

That is why a second flow lens was added:

- floor `delta-T` at `2.0 C`
- clip the upper flow tail
- apply `log1p`

This creates a safer third channel for the autoencoder:

`stabilized_flow_log_feature`

Interpretation:

- the raw lens is closer to the direct physical formula
- the stabilized lens is more robust when `delta-T` is small

### 7.8 What the current results mean technically

For `cons_hostatgeria_underfloor_hea`:

- the model finds only a few strong daily anomalies
- three of them overlap the low delta-T baseline
- one does not, which suggests an additional abnormal regime

For `cons_abat_oliba`:

- the raw lens was strongly influenced by near-zero delta-T causing very large flow values
- the stabilized lens produced more interpretable anomaly windows

So the method is doing two things at once:

1. confirming some anomalies already visible through simple engineering rules
2. revealing other daily patterns that the simple baseline does not isolate

## 8. Script-by-script explanation

This section explains each Python file, what it does, what it outputs, and how to interpret those outputs.

### 8.1 `Codes/src/features.py`

Purpose:

- Defines feature-engineering functions.

Main functions:

- `add_delta_t`
- `add_flow_from_power`
- `add_power_from_flow`
- `add_stabilized_flow_from_power`

Meaning:

- This file contains the physical transformations used by the project.
- It is where thermal engineering logic enters the pipeline.

Result interpretation:

- `delta_t_c` is the basic thermal separation feature.
- `derived_flow_kg_s` is the direct supervisor-based derived flow.
- `stabilized_flow_log_feature` is the safer alternative lens for autoencoder input.

### 8.2 `Codes/src/anomaly_detection.py`

Purpose:

- Implements robust statistical baselines using median absolute deviation.

Main functions:

- `median_absolute_deviation`
- `modified_z_score`
- `flag_low_delta_t`
- `flag_groupwise_low_delta_t`

Meaning:

- This is the simple non-neural reference method.
- It helps answer whether the autoencoder is finding anomalies that a straightforward engineering baseline would also find.

Result interpretation:

- If autoencoder anomalies overlap these low delta-T anomalies, that strengthens confidence.
- If they do not overlap, the autoencoder may be detecting a different regime or a feature-construction artifact.

### 8.3 `Codes/src/excel_timeseries.py`

Purpose:

- Reads Excel sheets where the real header row is not at the top of the sheet.

Meaning:

- Some building workbooks have blank rows or notes before the data header.
- This helper locates the true header row and returns a clean time-series frame.

Result interpretation:

- It is an ingestion utility rather than an analysis method.

### 8.4 `Codes/src/data_inventory.py`

Purpose:

- Creates workbook and column inventories for the Excel files.

Outputs:

- `Results/tables/data_inventory_sheets.csv`
- `Results/tables/data_inventory_columns.csv`
- `Results/tables/data_inventory_errors.csv`

Meaning:

- This was the first structured overview of what data exists.
- It helped identify likely timestamps, supply temperatures, return temperatures, power columns, and flow-related columns.

Result interpretation:

- It is a discovery tool, not an anomaly result.

### 8.5 `Codes/src/autoencoder.py`

Purpose:

- Defines the convolutional autoencoder architecture.

Meaning:

- This is the neural network itself.
- It contains the encoder and decoder used for reconstruction.

Result interpretation:

- It does not produce conclusions by itself.
- Its role is to transform a window into a reconstructed window.

### 8.6 `Codes/scripts/summarize_dhc_heating.py`

Purpose:

- Summarizes candidate DHC heating sheets.

Outputs:

- `Results/tables/dhc_heating_sheet_summary.csv`

Meaning:

- This script helped decide which sheets are usable and relevant.
- It reports date ranges, delta-T behavior, active-heating share, and rough flow plausibility.

Result interpretation:

- It is used for dataset selection and sanity checking.

### 8.7 `Codes/scripts/run_dhc_delta_t_baseline.py`

Purpose:

- Runs the low delta-T anomaly baseline on selected DHC sheets.

Outputs:

- `Results/tables/dhc_delta_t_baseline_summary.csv`
- processed row-level CSVs
- baseline figures

Meaning:

- This is the main simple baseline for the DHC sheets.

Result interpretation:

- It tells us where unusually low supply-return separation occurs.
- It gives a reference against which autoencoder results can be compared.

### 8.8 `Codes/scripts/prepare_autoencoder_windows.py`

Purpose:

- Builds the autoencoder-ready dataset.

Outputs:

- compressed window arrays in `Results/processed_data/`
- summary CSVs such as:
  - `autoencoder_windows_cons_hostatgeria_underfloor_hea_summary.csv`

Meaning:

- This is the key preprocessing step.
- It converts continuous historical time series into valid daily windows that can be fed to the model.

Result interpretation:

- The number of windows tells us how much usable historical training data is available.
- The summary also records which flow lens was used.

### 8.9 `Codes/scripts/train_autoencoder.py`

Purpose:

- Trains the autoencoder and computes reconstruction-based anomaly scores.

Outputs:

- model file in `Results/models/`
- `autoencoder_scores_*.csv`
- `autoencoder_summary_*.csv`
- `autoencoder_training_history_*.csv`
- reconstruction-error figure

Meaning:

- This script converts windows into anomaly scores.

Result interpretation:

- `train_loss` shows whether the model learned to reconstruct the data.
- `threshold_train_p99` is the cutoff used for anomaly flagging.
- `flagged_windows` is the count of windows above the threshold.

### 8.10 `Codes/scripts/inspect_autoencoder_windows.py`

Purpose:

- Inspects the top flagged windows in detail.

Outputs:

- `inspect_autoencoder_*_summary.csv`
- one multi-panel figure per flagged window

Meaning:

- This script translates abstract reconstruction scores into interpretable events.

Result interpretation:

- It shows:
  - which windows are most anomalous
  - whether they overlap low delta-T anomalies
  - what the raw supply/return/flow behavior looks like in those windows

### 8.11 `Codes/scripts/compare_autoencoder_runs.py`

Purpose:

- Compares autoencoder results across multiple sheets.

Outputs:

- `Results/tables/autoencoder_multi_sheet_comparison.csv`

Meaning:

- This is the cross-sheet ranking tool.

Result interpretation:

- It helped identify:
  - `cons_hostatgeria_underfloor_hea` as the strongest case
  - `cons_abat_oliba` as a secondary interesting case

### 8.12 `Codes/scripts/compare_autoencoder_lenses.py`

Purpose:

- Compares the raw-flow lens and stabilized-flow lens.

Outputs:

- `Results/tables/autoencoder_lens_comparison.csv`

Meaning:

- This is a robustness check on feature construction.

Result interpretation:

- If the same anomaly story survives both lenses, the result is more trustworthy.
- If the anomaly pattern changes dramatically, it suggests sensitivity to how the flow channel is defined.

## 9. Questions to ask the supervisor

These are the most useful questions for the next meeting.

### Data and units

1. Can the supervisor confirm the unit of `Power Interval Trend Log` for each sheet? Is it definitely `kW`?
2. When `Supply - Return` becomes very small or negative, should those periods be treated as sensor issues, off periods, or valid operating states?
3. Is the derived flow formula expected to be valid for all these sheets, or only for specific substations / exchangers?
4. For `cons_nostra_senyora`, why does the reported flow not match the derived flow under the simple unit assumption? Is the flow sensor in different units, or is the power value defined differently?

### Operational interpretation

5. Does `cons_hostatgeria_underfloor_hea` correspond to the most operationally meaningful subsystem for the thesis?
6. What happened operationally around `2024-04-03` to `2024-04-05` and `2024-10-25`? Are there logs, interventions, weather events, or control changes?
7. For `cons_abat_oliba`, are very small supply-return differences physically expected during some seasons or operating modes?
8. Is `cons_hostatgeria_DHW_radiators` a sheet where supply/return direction might be reversed or mixed with another operating mode?

### Thesis direction

9. Is the supervisor comfortable with treating clustering as secondary and keeping the thesis centered on reconstruction-based anomaly detection?
10. Would the supervisor prefer one main case study sheet plus two secondary comparison sheets, rather than trying to treat all sheets equally?
11. Should the thesis emphasize explainability and engineering interpretation over maximizing anomaly counts?

### Evaluation

12. Are there any maintenance records, alarms, or known abnormal periods that can be used as weak labels?
13. What would the supervisor consider a convincing validation result in the absence of labels?
14. Should anomalies be assessed at the point level, day-window level, or event level?

## 10. Recommended next work after the meeting

If the supervisor agrees with the current direction, the next tasks should be:

1. Confirm power units and flow interpretation.
2. Choose one primary thesis case:
   - likely `cons_hostatgeria_underfloor_hea`
3. Keep one secondary comparison case:
   - likely `cons_abat_oliba`
4. Inspect the flagged windows visually and relate them to operational behavior.
5. Decide whether the final thesis autoencoder should use:
   - raw derived flow
   - stabilized log-flow
   - or both as comparison experiments
