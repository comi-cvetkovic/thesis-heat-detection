# Detailed Recap For Me - 2026-05-25

This note is for internal understanding. It is intentionally more detailed than the supervisor updates. The goal is to explain:

1. what was built
2. why each step was done
3. what each result means
4. which figures best illustrate the current findings

## 1. Big picture

The project started from the HEAT paper idea, but the current implementation has evolved into a more suitable structure for this dataset.

Current method roles:

- `autoencoder` = main anomaly detector
- `low delta-T baseline` = simple engineering reference
- `feature-space clustering` = main regime-interpretation tool
- `latent-space clustering` = comparison experiment

The most important shift was:

`from whole-building clustering to window-based analysis`

This happened because the number of buildings/substations is small, but each building has a long historical time series.

So instead of asking:

`which buildings are similar?`

the project now asks:

`which daily operating windows are similar, and which daily windows are unusual?`

## 2. Data used

The most relevant DHC sheets analyzed so far are:

- `cons_abat_oliba`
- `cons_hostatgeria_underfloor_hea`
- `cons_hostatgeria_DHW_radiators`
- `cons_nostra_senyora`

For the autoencoder, each window uses three channels:

- supply temperature
- return temperature
- a flow-based feature

There are currently two flow-based feature versions:

1. `raw` flow
   - direct use of the supervisor formula
   - `m = Power / (Cp * (Ts - Tr))`

2. `stabilized_log` flow
   - same physical idea, but safer numerically
   - floors small `delta-T`
   - clips extreme upper values
   - applies log scaling

Current supervisor-confirmed assumption:

- `Power Interval Trend Log` should be treated as `kW` for all sheets

## 3. Exact preprocessing pipeline

The pipeline is implemented mainly in:

- [prepare_autoencoder_windows.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/scripts/prepare_autoencoder_windows.py>)
- [features.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/src/features.py>)

The steps are:

1. Read one sheet from the Excel workbook.
2. Parse timestamps and sort chronologically.
3. Compute `delta_t_c = supply - return`.
4. Compute the flow feature:
   - raw or stabilized
   - using `Power` interpreted as `kW`
5. Define active-heating rows:
   - `power > 0`
   - `delta-T > 0`
   - flow feature finite and positive
6. Set non-active rows to `NaN` in the three channels.
7. Resample to `15-minute` intervals.
8. Interpolate only short gaps.
9. Build `24-hour` windows with `12-hour` stride.
10. Keep only windows with:
   - at least `60%` active-heating share
   - at least `85%` complete-data share
11. Standardize each channel:
   - subtract mean
   - divide by standard deviation

This gives a clean tensor for the autoencoder.

At 15-minute resolution:

- `24 hours = 96 time steps`
- `3 channels`

So one model input is:

`3 x 96`

## 4. Low delta-T baseline

The low delta-T baseline is the simplest anomaly detector in the project.

Implemented in:

- [run_dhc_delta_t_baseline.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/scripts/run_dhc_delta_t_baseline.py>)
- [anomaly_detection.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/src/anomaly_detection.py>)

It works like this:

1. Keep active-heating rows.
2. Compute modified z-scores of `delta-T`.
3. Flag rows whose `delta-T` is unusually low relative to the rest of the active data.

This is useful because:

- it is easy to explain physically
- it gives a simple benchmark
- it helps interpret the autoencoder

Important point:

This baseline is not the main method anymore, but it is still valuable because overlap between the autoencoder and low delta-T gives confidence that the model is seeing something physically meaningful.

Useful figures:

- [dhc_delta_t_baseline_cons_hostatgeria_underfloor_hea.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/dhc_delta_t_baseline_cons_hostatgeria_underfloor_hea.png>)
- [dhc_delta_t_baseline_cons_abat_oliba.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/dhc_delta_t_baseline_cons_abat_oliba.png>)

How to read them:

- the line is the active-heating `delta-T`
- flagged points are unusually low `delta-T`

## 5. Autoencoder: what it is and how it works

The model is defined in:

- [autoencoder.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/src/autoencoder.py>)

Current architecture:

1. `Conv1d(3 -> 16)`
2. `ReLU`
3. `MaxPool1d(2)`
4. `Conv1d(16 -> 16 latent channels)`
5. `ReLU`
6. `MaxPool1d(2)`
7. `ConvTranspose1d(16 -> 16)`
8. `ReLU`
9. `ConvTranspose1d(16 -> 3)`

Interpretation:

- the encoder compresses the original window
- the decoder reconstructs it
- the model is trained to make the reconstruction close to the original

Training script:

- [train_autoencoder.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/scripts/train_autoencoder.py>)

Training logic:

1. Use the first `80%` of windows as training windows.
2. Train the model with mean squared error loss.
3. After training, reconstruct all windows.
4. Compute one scalar reconstruction error per window:

`mean((reconstructed - original)^2)`

5. Compute the `99th percentile` of training reconstruction errors.
6. Flag any window whose reconstruction error is above that threshold.

That means:

- a flagged window is not “classified as a fault”
- it is simply a window that the model finds unusually hard to reconstruct

Useful figures:

- [autoencoder_reconstruction_error_cons_hostatgeria_underfloor_hea.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/autoencoder_reconstruction_error_cons_hostatgeria_underfloor_hea.png>)
- [autoencoder_reconstruction_error_cons_abat_oliba.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/autoencoder_reconstruction_error_cons_abat_oliba.png>)
- [autoencoder_reconstruction_error_cons_abat_oliba_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/autoencoder_reconstruction_error_cons_abat_oliba_stabilized_log.png>)

How to read them:

- x-axis = window start time
- y-axis = reconstruction MSE
- orange line = threshold
- red-highlighted windows = flagged anomalies

Meaning:

- a peak means the daily pattern was hard for the model to reconstruct
- the bigger the gap above the threshold, the more unusual the window is relative to historical training windows

## 5.1 Joint detection vs feature-specific detection

This is an important point.

The current autoencoder does **not** run three completely independent anomaly detectors.

Instead, it works in two layers:

1. **joint anomaly detection**
   - the model takes all three channels together
   - it reconstructs the full multivariate 24-hour window
   - one total reconstruction error is computed for the whole window
   - that total error is what currently decides whether the window is flagged

2. **per-feature attribution**
   - after reconstruction, the error is also split by channel
   - this gives a reconstruction MSE for:
     - `supply_temp_c`
     - `return_temp_c`
     - the flow feature
   - each channel also gets its own training `99th percentile` threshold
   - we then record:
     - whether that channel was anomalous on its own
     - which channel had the largest reconstruction error

So the current method is best described as:

`joint anomaly detection + per-feature attribution`

not:

`three separate feature-only anomaly detectors`

### Exact scoring logic

For each window:

1. compare reconstructed output to original input at every time step and channel
2. square the differences
3. average everything together to get one total window MSE
4. also average separately by channel across time

That means we now have:

- total `reconstruction_mse`
- `supply_temp_c_reconstruction_mse`
- `return_temp_c_reconstruction_mse`
- flow-feature reconstruction MSE

Thresholds:

- total anomaly threshold = training `99th percentile` of total window MSE
- per-channel threshold = training `99th percentile` of that channel MSE

This means a window can be:

- a total anomaly
- a supply-channel anomaly
- a return-channel anomaly
- a flow-channel anomaly

all at the same time or in different combinations.

### Why this matters

This lets us answer two different questions:

1. `Should this day be flagged at all?`
2. `Which feature is mainly responsible for the flag?`

This is important because district-heating behavior is multivariate. Some anomalies are really anomalies in the relationship between variables, not only in one single feature by itself.

### New score-table columns

The score tables now contain columns like:

- `reconstruction_mse`
- `is_reconstruction_anomaly`
- `supply_temp_c_reconstruction_mse`
- `return_temp_c_reconstruction_mse`
- `derived_flow_kg_s_reconstruction_mse` or `stabilized_flow_log_feature_reconstruction_mse`
- `is_supply_temp_c_channel_anomaly`
- `is_return_temp_c_channel_anomaly`
- flow-channel anomaly flag
- `dominant_anomalous_feature`

So now the anomaly can be described more precisely:

`The window was anomalous overall, and the main contributing feature was return temperature.`

## 6. Why the stabilized flow lens was added

Problem with raw flow:

`flow = Power / (Cp * delta-T)`

If `delta-T` gets close to zero:

- denominator gets small
- flow gets very large
- the autoencoder may react more to numerical blow-up than to real thermal behavior

This problem was especially visible in `cons_abat_oliba`.

The stabilized lens was added to reduce this issue.

Implemented in:

- [features.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/src/features.py>)

Stabilization method:

1. floor `delta-T` at `2.0 C`
2. clip the upper flow tail at the `99.5%` quantile
3. apply `log1p`

Why this helps:

- large spikes from near-zero `delta-T` are softened
- the flow channel still carries variation
- the model is less dominated by extreme derived-flow events

Useful result table:

- [autoencoder_lens_comparison.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_lens_comparison.csv>)

Current meaning:

- for `cons_abat_oliba`, the stabilized lens is clearly more interpretable
- for `cons_hostatgeria_underfloor_hea`, the main anomaly story is stable under both lenses

That is important because:

- if a result survives both lenses, it is more trustworthy
- if it changes drastically, it may be too dependent on the flow construction

## 7. Interpreting the strongest autoencoder cases

### 7.1 `cons_hostatgeria_underfloor_hea`

This is currently the strongest case study.

Main summary:

- [autoencoder_summary_cons_hostatgeria_underfloor_hea.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_summary_cons_hostatgeria_underfloor_hea.csv>)

Key numbers:

- `323` retained windows
- `258` train windows
- `65` test windows
- `4` flagged windows

Interpretation:

- few anomalies
- easy to inspect
- not noisy

Important inspection summary:

- [inspect_autoencoder_cons_hostatgeria_underfloor_hea_summary.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/inspect_autoencoder_cons_hostatgeria_underfloor_hea_summary.csv>)

Best inspection figures:

- [inspect_autoencoder_cons_hostatgeria_underfloor_hea_01.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_hostatgeria_underfloor_hea_01.png>)
- [inspect_autoencoder_cons_hostatgeria_underfloor_hea_02.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_hostatgeria_underfloor_hea_02.png>)
- [inspect_autoencoder_cons_hostatgeria_underfloor_hea_03.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_hostatgeria_underfloor_hea_03.png>)
- [inspect_autoencoder_cons_hostatgeria_underfloor_hea_04.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_hostatgeria_underfloor_hea_04.png>)

What those figures show:

- panel 1 = supply temperature
- panel 2 = return temperature
- panel 3 = flow feature
- panel 4 = `delta-T`

What the results mean:

- three of the strongest flagged windows overlap low delta-T anomalies around `2024-04-03` to `2024-04-05`
- one flagged window around `2024-10-25` does not overlap low delta-T

Interpretation:

- the autoencoder is partly confirming the simple baseline
- but it also appears capable of finding a different kind of unusual daily regime

Channel-level interpretation:

- `2024-04-03 18:45`
  - dominant anomalous feature: `supply_temp_c`
  - supply reconstruction MSE: `8.822`
  - return reconstruction MSE: `2.168`
  - flow reconstruction MSE: `3.092`
  - low delta-T overlap: yes

- `2024-10-25 18:45`
  - dominant anomalous feature: `return_temp_c`
  - supply reconstruction MSE: `0.157`
  - return reconstruction MSE: `6.934`
  - flow reconstruction MSE: `1.338`
  - low delta-T overlap: no

This matters because it shows the flagged days are not all anomalous in the same feature. Some are mainly supply-side anomalies, while another is mainly a return-temperature anomaly.

This is exactly the kind of result we want:

- interpretable
- not purely trivial
- not obviously just a numerical artifact

### 7.2 `cons_abat_oliba`

This is the second most interesting case.

Main multi-sheet summary:

- [autoencoder_multi_sheet_comparison.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_multi_sheet_comparison.csv>)
- [inspect_autoencoder_cons_abat_oliba_summary.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/inspect_autoencoder_cons_abat_oliba_summary.csv>)
- [inspect_autoencoder_cons_abat_oliba_stabilized_log_summary.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/inspect_autoencoder_cons_abat_oliba_stabilized_log_summary.csv>)

Raw-lens issue:

- the top anomalies were dominated by near-zero `delta-T`
- that created huge derived-flow values
- the raw lens was too easy to misread as “anomaly = blown-up flow”

Best raw-flow inspection figures:

- [inspect_autoencoder_cons_abat_oliba_01.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_abat_oliba_01.png>)
- [inspect_autoencoder_cons_abat_oliba_02.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_abat_oliba_02.png>)

What they mean:

- supply and return get very close
- raw derived flow jumps a lot
- anomaly score is dominated by that effect

Best stabilized-flow inspection figures:

- [inspect_autoencoder_cons_abat_oliba_stabilized_log_01.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_abat_oliba_stabilized_log_01.png>)
- [inspect_autoencoder_cons_abat_oliba_stabilized_log_02.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_abat_oliba_stabilized_log_02.png>)

What they mean:

- the top anomalies are no longer just giant flow blow-ups
- the windows still look unusual, but in a more moderate and believable way

Interpretation:

- Abat Oliba still matters
- but it needs more care in feature design
- it is currently better suited as a secondary case than as the primary thesis case

Channel-level meaning:

- under the raw-flow lens, the strongest anomalies are mostly **flow-driven**
- under the stabilized-flow lens, the strongest anomalies often become **return-temperature-driven** or **supply-temperature-driven**

Example from stabilized flow:

- `2025-03-02 18:45`
  - dominant anomalous feature: `return_temp_c`
  - supply reconstruction MSE: `0.186`
  - return reconstruction MSE: `0.510`
  - stabilized-flow reconstruction MSE: `0.459`

This is the clearest evidence that the stabilized lens improved interpretability. The anomaly is no longer explained mainly by a numerical flow spike.

## 8. Multi-sheet comparison: what it means

Main table:

- [autoencoder_multi_sheet_comparison.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_multi_sheet_comparison.csv>)

Current ranking:

1. `cons_hostatgeria_underfloor_hea`
2. `cons_abat_oliba`
3. `cons_hostatgeria_DHW_radiators`
4. `cons_nostra_senyora`

Why this ranking:

- underfloor heating has the clearest and smallest anomaly set
- Abat Oliba is interesting but more sensitive to flow-feature definition
- DHW radiators and Nostra Senyora are harder to interpret at the moment

This ranking is not a statement of “importance of building,” but a ranking of:

`which sheet currently gives the most defensible anomaly-analysis story`

## 9. Power scaling sanity check: what it means

Main file:

- [power_scaling_sanity_check.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/power_scaling_sanity_check.csv>)

Most important finding:

- `kW` gives plausible median flow values for:
  - `cons_abat_oliba`
  - `cons_hostatgeria_DHW_radiators`
- but not for:
  - `cons_hostatgeria_underfloor_hea`
  - `cons_nostra_senyora`

What that means:

There is probably **not one simple alternative unit** that fixes everything.

Likely explanations:

- the same power unit may not apply equally across sheets
- the same formula may not be physically appropriate for every subsystem
- the expected flow range of `1-2` may not apply to all subsystems

So this result does **not** prove a different unit directly. It proves:

`the current flow interpretation is inconsistent across sheets and must be validated with the supervisor`

## 10. Clustering: first method

This is the existing operating-regime clustering.

Script:

- [cluster_autoencoder_windows.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/scripts/cluster_autoencoder_windows.py>)

Method:

- build daily windows
- summarize each window with engineered statistics:
  - supply median/std
  - return median/std
  - flow median/std
  - delta-T median
  - delta-T 5th percentile
  - delta-T min
  - active fraction
- standardize the summary features
- run `KMeans` with `4` clusters

Interpretation:

- the clusters are **operating regimes**
- they are not whole-building clusters

Key result:

- [cluster_summary_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/cluster_summary_stabilized_log.csv>)
- [cluster_sheet_summary_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/cluster_sheet_summary_stabilized_log.csv>)
- [cluster_pca_scatter_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/cluster_pca_scatter_stabilized_log.png>)

Most important meaning:

- underfloor-heating windows mostly sit in cluster `2`
- its strongest anomalies fall into cluster `1`

So clustering is helping say:

`these anomalous days are not just noisy points; they move into a different operating regime`

That is a good use of clustering.

## 11. Clustering: second method

This is the latent-space clustering comparison.

Script:

- [compare_sheet_clustering_methods.py](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Codes/scripts/compare_sheet_clustering_methods.py>)

Method:

1. Train the autoencoder.
2. Pass windows through the encoder only.
3. Take the compressed latent representation.
4. Flatten it.
5. Cluster those latent vectors with `KMeans`.

This is conceptually tighter because:

- clustering uses what the autoencoder learned

But the key question is:

`is it actually more useful?`

Current answer: not yet.

Comparison files:

- [clustering_method_comparison_cons_hostatgeria_underfloor_hea_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/clustering_method_comparison_cons_hostatgeria_underfloor_hea_stabilized_log.csv>)
- [clustering_method_comparison_cons_abat_oliba_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/clustering_method_comparison_cons_abat_oliba_stabilized_log.csv>)

Underfloor heating:

- feature clustering silhouette: `0.296`
- latent clustering silhouette: `0.103`

Abat Oliba:

- feature clustering silhouette: `0.231`
- latent clustering silhouette: `0.221`

Meaning:

- for underfloor heating, feature clustering is clearly cleaner
- for Abat Oliba, they are closer, but feature clustering still concentrates anomalies better

Useful figures:

- [feature_cluster_scatter_cons_hostatgeria_underfloor_hea_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/feature_cluster_scatter_cons_hostatgeria_underfloor_hea_stabilized_log.png>)
- [latent_cluster_scatter_cons_hostatgeria_underfloor_hea_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/latent_cluster_scatter_cons_hostatgeria_underfloor_hea_stabilized_log.png>)
- [feature_cluster_scatter_cons_abat_oliba_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/feature_cluster_scatter_cons_abat_oliba_stabilized_log.png>)
- [latent_cluster_scatter_cons_abat_oliba_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/latent_cluster_scatter_cons_abat_oliba_stabilized_log.png>)

How to read them:

- each point = one daily window
- color = cluster
- highlighted outline points = autoencoder anomalies

Current conclusion:

- feature-space clustering is more useful operationally right now
- latent-space clustering is still worth mentioning as a comparison experiment

## 12. Joint vs per-feature autoencoders

To answer the supervisor's question more directly, a second autoencoder path was added:

- one `joint` autoencoder using all three channels together
- three `univariate` autoencoders, one per feature

This is useful because it tells us whether anomalies are:

- clearly visible in one feature alone
- or only visible when the variables are considered together

Main comparison tables:

- [autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.csv>)
- [autoencoder_joint_vs_univariate_cons_abat_oliba_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_joint_vs_univariate_cons_abat_oliba_stabilized_log.csv>)

Comparison figures:

- [autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.png>)
- [autoencoder_joint_vs_univariate_cons_abat_oliba_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/autoencoder_joint_vs_univariate_cons_abat_oliba_stabilized_log.png>)

### 12.1 Underfloor heating

Important numbers:

- joint model: `4` flagged windows
- supply-only model: `3` flagged windows, all `3` overlap joint anomalies
- return-only model: `5` flagged windows, `2` overlap joint anomalies
- flow-only model: `3` flagged windows, `1` overlaps joint anomalies

Interpretation:

- the strongest underfloor-heating anomalies are visible in the supply channel
- the return channel adds extra anomaly candidates, especially the October case
- the flow-only model is less aligned with the main anomaly story

So for underfloor heating:

- the joint model is still useful
- but the anomalies are strongly driven by temperature behavior

### 12.2 Abat Oliba

Important numbers:

- joint model: `12` flagged windows
- supply-only model: `8` flagged windows, `2` overlap joint anomalies
- return-only model: `9` flagged windows, `3` overlap joint anomalies
- flow-only model: `8` flagged windows, `0` overlap joint anomalies

Interpretation:

- the joint model is finding a broader set of anomalies than any single-feature model
- overlap with single-feature models is weak
- this is strongest evidence that the multivariate model is learning interactions, not just single-channel spikes

This is especially important for Abat Oliba because under the stabilized flow lens, the flow-only model no longer explains the joint anomaly set.

### 12.3 What this means methodologically

This comparison supports the following structure:

- `joint autoencoder` = main anomaly detector
- `per-feature autoencoders` = comparison and interpretability layer

That is better than replacing the joint model entirely, because:

- some anomalies are multivariate relationship anomalies
- some anomalies are easier to explain through one dominant feature

## 13. Best current story for the thesis

If I had to explain the current project in one clear chain:

1. Build daily windows from historical heating data.
2. Train an autoencoder to reconstruct normal daily thermal-hydraulic behavior.
3. Flag windows with high reconstruction error.
4. Compare those windows to a low delta-T engineering baseline.
5. Use clustering to understand which operating regimes are normal and which regimes contain anomalies.

The strongest current thesis case is:

`cons_hostatgeria_underfloor_hea`

Why:

- few anomalies
- interpretable windows
- overlap with engineering baseline
- stable under raw and stabilized flow lenses
- regime separation visible in clustering

## 14. What is still unresolved

These are the main open points:

1. The power unit is now assumed to be `kW` for all sheets, but the flow interpretation is still not globally resolved.
2. We do not yet have confirmed fault labels.
3. The best final window length is not fully tested.
4. Clustering is useful, but it is still secondary to the anomaly detector.
5. Abat Oliba is promising, but more sensitive to feature construction.
6. We have not yet decided whether thesis reporting should emphasize per-feature autoencoders only as interpretation or also as a formal benchmark.

## 15. What I should remember for discussion

The strongest points:

- reconstruction-based anomaly detection is working
- underfloor-heating is the best case
- stabilized flow improved interpretability
- clustering now has real results
- feature-space clustering is currently better than latent-space clustering
- per-feature autoencoders are now implemented and comparable to the joint model

The cautious points:

- anomalies are candidates, not confirmed faults
- power is now assumed to be `kW`, but the resulting flow interpretation is still not equally convincing for all sheets
- some sheets are harder to interpret than others
- not every anomaly is best explained by one feature alone

## 16. Best files to reread before talking to the supervisor

If time is short, focus on these:

1. [supervisor_update_2026-05-25.md](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/supervisor_update_2026-05-25.md>)
2. [autoencoder_multi_sheet_comparison.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_multi_sheet_comparison.csv>)
3. [power_scaling_sanity_check.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/power_scaling_sanity_check.csv>)
4. [cluster_summary_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/cluster_summary_stabilized_log.csv>)
5. [clustering_method_comparison_cons_hostatgeria_underfloor_hea_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/clustering_method_comparison_cons_hostatgeria_underfloor_hea_stabilized_log.csv>)
6. [autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.csv>)
7. [autoencoder_joint_vs_univariate_cons_abat_oliba_stabilized_log.csv](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/tables/autoencoder_joint_vs_univariate_cons_abat_oliba_stabilized_log.csv>)
8. [inspect_autoencoder_cons_hostatgeria_underfloor_hea_01.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_hostatgeria_underfloor_hea_01.png>)
9. [inspect_autoencoder_cons_abat_oliba_stabilized_log_01.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/inspect_autoencoder_cons_abat_oliba_stabilized_log_01.png>)
10. [cluster_pca_scatter_stabilized_log.png](</D:/Downloads/KTH/Masters Thesis/thesis-heat-detection/Results/figures/cluster_pca_scatter_stabilized_log.png>)
