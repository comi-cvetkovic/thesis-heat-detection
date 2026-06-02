# Supervisor Update - 2026-05-25

## 1. Goal of this iteration

From the previous supervisor meeting, the main follow-up items were:

1. Investigate whether the assumed power unit (`kW`) is reliable, because some derived-flow values looked unrealistic.
2. Prepare clustering results for the next meeting.

This update focuses on those two items.

## 2. Power unit / derived-flow sanity check

### 2.1 Why this was necessary

The autoencoder currently uses three input channels:

- supply temperature
- return temperature
- derived flow

The derived flow is computed with:

`m = Power / (Cp * (Ts - Tr))`

If the `kW` assumption is fixed but `delta-T` becomes very small, or if the formula is not equally meaningful across subsystems, the derived flow can become misleading.

### 2.2 What was tested

A power-scaling sanity check was added. For each main DHC sheet, the script computes the median derived flow under several assumptions:

- `W`
- `10W`
- `100W`
- `kW`
- `10kW`

The script also computes the scale factor that would make the median flow roughly `1.5`, since the supervisor indicated expected values should often be around `1-2`.

Important update after the later supervisor discussion:

```text
The power column should be treated as kW for all sheets.
```

So this check should now be interpreted as a consistency check under a fixed `kW` assumption, not as an open unit-selection question.

Output file:

- `Results/tables/power_scaling_sanity_check.csv`

### 2.3 Current results

The check was extended to all currently usable heating-consumer sheets.

Main output:

- `Results/tables/power_scaling_all_heating_sheets.csv`

| Workbook | Sheet | Median power (active) | Median delta-T (active) | Median flow if `kW` | `kW` plausible? |
| --- | --- | ---: | ---: | ---: | --- |
| `_2.xlsx` | `cons_hostatgeria_DHW_radiators` | 30.6 | 5.46 | 1.410 | Yes |
| `_1.xlsx` | `cons_abat_cisneros` | 65.8 | 11.79 | 1.669 | Yes |
| `_2.xlsx` | `cons_abat_oliba` | 30.0 | 3.92 | 2.033 | Borderline high |
| `_1.xlsx` | `cons_abat_marcet` | 31.7 | 9.31 | 0.926 | Borderline low |
| `_1.xlsx` | `cons_abat_garriga` | 12.7 | 8.84 | 0.365 | No |
| `_2.xlsx` | `cons_hostatgeria_underfloor_hea` | 10.9 | 32.46 | 0.0818 | No |
| `_2.xlsx` | `cons_nostra_senyora` | 1.0 | 9.77 | 0.0214 | No |

### 2.4 Interpretation

This does **not** support one single clean flow interpretation across all sheets, even under the fixed `kW` assumption.

Observations:

1. `cons_hostatgeria_DHW_radiators` and `cons_abat_cisneros` fit the `kW` assumption well.
2. `cons_abat_oliba` is close, but slightly high.
3. `cons_abat_marcet` is below the expected range, but not wildly so.
4. `cons_abat_garriga`, `cons_hostatgeria_underfloor_hea`, and `cons_nostra_senyora` are clearly inconsistent with the simple `kW` interpretation.

So the situation is probably one of these:

- the `kW` assumption is reasonable for some sheets but not all
- the formula is not equally meaningful for all subsystems
- some sheets correspond to very different hydraulic regimes
- some channels may not be directly comparable in the way originally assumed

Working conclusion:

`kW` is now the assumed power unit for all sheets, based on supervisor guidance, but the derived-flow interpretation is not validated consistently across the full set of heating-consumer sheets.

## 3. Clustering results

### 3.1 Why clustering was changed

Because the number of substations/buildings is small, clustering whole buildings is weak. Instead, clustering was done on **time windows**.

Each retained 24-hour window is represented by summary features derived from the same daily windows used by the autoencoder.

This makes clustering a way of grouping **operating regimes**, not entire buildings.

### 3.2 Clustering setup

The clustering was run on:

- `cons_abat_oliba`
- `cons_hostatgeria_underfloor_hea`
- `cons_hostatgeria_DHW_radiators`
- `cons_nostra_senyora`

Using:

- 24-hour windows
- 15-minute resolution
- stabilized flow lens
- KMeans with `4` clusters

Window summary features used for clustering:

- supply median
- supply standard deviation
- return median
- return standard deviation
- flow median
- flow standard deviation
- delta-T median
- delta-T 5th percentile
- delta-T minimum
- mean active-heating fraction

Main outputs:

- `Results/tables/cluster_summary_stabilized_log.csv`
- `Results/tables/cluster_sheet_summary_stabilized_log.csv`
- `Results/tables/clustered_windows_stabilized_log.csv`
- `Results/figures/cluster_pca_scatter_stabilized_log.png`

### 3.3 Cluster-level results

| Cluster | Windows | Autoencoder anomaly windows | Anomaly rate | Median supply | Median return | Median flow | Median delta-T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0` | 1348 | 9 | 0.0067 | 79.16 | 70.18 | 0.538 | 7.59 |
| `1` | 551 | 6 | 0.0109 | 74.86 | 67.02 | 0.898 | 6.64 |
| `2` | 321 | 1 | 0.0031 | 77.99 | 45.33 | 0.059 | 29.92 |
| `3` | 1244 | 0 | 0.0000 | 78.76 | 72.98 | 0.814 | 6.77 |

### 3.4 Per-sheet cluster composition

Key per-sheet results:

- `cons_hostatgeria_underfloor_hea`
  - 320 windows in cluster `2`
  - 3 windows in cluster `1`
  - all 3 windows in cluster `1` are autoencoder anomalies

- `cons_abat_oliba`
  - mostly cluster `0` with 762 windows
  - secondary presence in cluster `1` with 161 windows
  - most of its autoencoder anomalies appear in clusters `0` and `1`

- `cons_hostatgeria_DHW_radiators`
  - mostly cluster `3` with 844 windows
  - secondary presence in cluster `1` with 205 windows
  - no autoencoder anomalies in the current clustered summary

- `cons_nostra_senyora`
  - spread across clusters `0`, `1`, and `3`
  - no autoencoder anomalies in the current clustered summary

### 3.5 Interpretation

This is the first useful clustering result.

Main observations:

1. The underfloor-heating sheet forms a very distinctive operating regime.
   - Cluster `2` is essentially its normal regime.
   - It has very high delta-T and very low flow compared with the other sheets.

2. The strongest underfloor-heating anomalies fall outside its dominant regime.
   - The 3 strongest anomalous windows move into cluster `1`.
   - That is useful because it means clustering is helping separate normal regime windows from unusual regime windows.

3. Cluster `3` looks like the most stable normal regime.
   - It has `1244` windows and zero autoencoder anomalies.
   - It is dominated by `cons_hostatgeria_DHW_radiators` and part of `cons_nostra_senyora`.

4. Clusters `0` and `1` contain most of the autoencoder anomalies.
   - These likely correspond to more mixed or transitional operating regimes.

Working conclusion:

`Time-window clustering appears useful as a secondary interpretation tool, especially for separating normal and abnormal operating regimes rather than grouping whole buildings.`

## 4. Relationship between clustering and autoencoder results

The clustering is not replacing the autoencoder.

Current method roles:

- autoencoder = primary anomaly detector
- low delta-T baseline = simple engineering reference
- clustering = secondary interpretation layer

What clustering adds:

1. It shows that the underfloor-heating windows mostly occupy a distinct normal regime.
2. It shows that several anomalous windows move out of that dominant regime.
3. It gives a way to discuss operating-state structure even if labels are limited.

This aligns well with the supervisor's latest request: prepare some clustering and show results, without making clustering the entire thesis.

## 4.1 How anomalies are actually detected in the autoencoder

This point needed clarification.

The current autoencoder does **not** run three completely separate anomaly detectors.

Instead, it works in two layers:

1. **joint detection**
   - the model takes all three channels together:
     - supply temperature
     - return temperature
     - flow feature
   - it reconstructs the full 24-hour multivariate window
   - one total reconstruction error is computed for the whole window
   - a window is flagged if this total error is above the training `99th percentile`

2. **feature attribution**
   - after reconstruction, the error is also broken down by channel
   - this gives:
     - `supply_temp_c_reconstruction_mse`
     - `return_temp_c_reconstruction_mse`
     - flow-feature reconstruction MSE
   - for each channel, a separate training `99th percentile` threshold is also computed
   - this lets us say:
     - whether a specific channel was itself unusually hard to reconstruct
     - which channel had the largest error in the flagged window

So the current method is:

`joint anomaly detection + per-feature attribution`

not:

`three fully independent anomaly detectors`

### 4.2 What this now gives us

For each scored window, the output tables now include:

- total `reconstruction_mse`
- `is_reconstruction_anomaly`
- per-channel reconstruction MSE values
- per-channel anomaly flags
- `dominant_anomalous_feature`

This means we can now answer questions like:

- "Was this anomaly mainly a supply-temperature anomaly?"
- "Was it mainly a return-temperature anomaly?"
- "Was it mainly driven by the flow feature?"

### 4.3 Examples from the current results

From `cons_hostatgeria_underfloor_hea`:

- `2024-04-03 18:45`
  - total reconstruction MSE: `4.694`
  - dominant anomalous feature: `supply_temp_c`
  - supply-channel MSE: `8.822`
  - return-channel MSE: `2.168`
  - flow-channel MSE: `3.092`
  - overlaps low delta-T anomalies: yes

- `2024-10-25 18:45`
  - total reconstruction MSE: `2.809`
  - dominant anomalous feature: `return_temp_c`
  - supply-channel MSE: `0.157`
  - return-channel MSE: `6.934`
  - flow-channel MSE: `1.338`
  - overlaps low delta-T anomalies: no

This is useful because the two anomalous windows are not abnormal in the same way:

- the April anomaly is mainly a **supply-temperature** anomaly
- the October anomaly is mainly a **return-temperature** anomaly

From `cons_abat_oliba` under the stabilized-flow lens:

- `2025-03-02 18:45`
  - total reconstruction MSE: `0.385`
  - dominant anomalous feature: `return_temp_c`
  - supply-channel MSE: `0.186`
  - return-channel MSE: `0.510`
  - stabilized-flow-channel MSE: `0.459`

This is important because under the stabilized lens, Abat Oliba is no longer obviously dominated by flow blow-up. The anomaly becomes interpretable in terms of temperature behavior as well.

### 4.4 What still remains open

If the supervisor wants each feature to be treated entirely on its own, the next step would be one of these:

1. train separate single-channel autoencoders
2. use the current per-channel reconstruction errors as primary feature-specific anomaly detectors
3. combine both approaches and compare them

Right now, the implementation is still multivariate first, because the joint relationships between supply, return, and flow are physically meaningful. But it now also reports which feature is driving each anomaly.

## 5. Comparison of the two clustering methods

Because the question came up whether clustering should be used together with the autoencoder, a direct comparison was added between:

1. feature-space clustering
   - cluster daily windows using hand-engineered summary features
2. latent-space clustering
   - cluster daily windows using the latent representations produced by the trained autoencoder encoder

This comparison was run on the two most important sheets:

- `cons_hostatgeria_underfloor_hea`
- `cons_abat_oliba`

Outputs:

- `Results/tables/clustering_method_comparison_cons_hostatgeria_underfloor_hea_stabilized_log.csv`
- `Results/tables/clustering_method_comparison_cons_abat_oliba_stabilized_log.csv`
- feature-cluster summaries and latent-cluster summaries for each sheet
- PCA scatter plots for both methods

### 5.1 Results for `cons_hostatgeria_underfloor_hea`

| Method | Silhouette score | Anomaly clusters used | Max cluster anomaly rate |
| --- | ---: | ---: | ---: |
| feature clustering | 0.296 | 2 | 0.083 |
| latent clustering | 0.103 | 3 | 0.053 |

Interpretation:

- Feature clustering separates the underfloor-heating windows more clearly.
- Autoencoder anomalies are more concentrated in a smaller number of feature clusters.
- Latent clustering works, but the anomaly structure is more diffuse.

### 5.2 Results for `cons_abat_oliba`

| Method | Silhouette score | Anomaly clusters used | Max cluster anomaly rate |
| --- | ---: | ---: | ---: |
| feature clustering | 0.231 | 2 | 0.034 |
| latent clustering | 0.221 | 3 | 0.019 |

Interpretation:

- The separation quality of the two methods is closer than in the underfloor-heating case.
- Even here, feature clustering still concentrates anomalies slightly better.
- Latent clustering does not currently provide a stronger anomaly-regime separation than the engineered feature clustering.

### 5.3 Working conclusion from the comparison

At this stage:

- feature-space clustering is more useful operationally
- latent-space clustering is technically interesting, but not yet more informative than feature clustering

So the current best role assignment is:

- autoencoder = main anomaly detector
- feature clustering = best current regime-interpretation layer
- latent clustering = useful comparison experiment, but not yet the preferred clustering method

## 6. Joint vs per-feature autoencoders

Because the supervisor asked whether anomalies should also be visible feature by feature, a second autoencoder path was added:

- one `joint` autoencoder using all three channels together
- three `univariate` autoencoders, one for each feature:
  - `supply_temp_c`
  - `return_temp_c`
  - flow feature

This lets us compare:

1. multivariate anomaly detection based on relationships between variables
2. single-feature anomaly detection based on one channel at a time

Outputs:

- `Results/tables/autoencoder_joint_vs_univariate_cons_hostatgeria_underfloor_hea_stabilized_log.csv`
- `Results/tables/autoencoder_joint_vs_univariate_cons_abat_oliba_stabilized_log.csv`
- matching comparison figures in `Results/figures/`

### 6.1 Results for `cons_hostatgeria_underfloor_hea`

| Model | Flagged windows | Flag rate | Overlap with joint anomalies |
| --- | ---: | ---: | ---: |
| `joint` | 4 | 0.0124 | 4 |
| `supply_temp_c` only | 3 | 0.0093 | 3 |
| `return_temp_c` only | 5 | 0.0155 | 2 |
| `flow` only | 3 | 0.0093 | 1 |

Interpretation:

- the strongest underfloor-heating anomalies are captured well by the `supply_temp_c`-only model
- the `return_temp_c`-only model finds the important October anomaly and also adds a few extra candidate days
- the flow-only model overlaps less with the joint anomalies

Working conclusion:

For underfloor heating, the joint model remains useful, but the anomaly story is strongly influenced by the temperature channels, especially supply temperature.

### 6.2 Results for `cons_abat_oliba`

| Model | Flagged windows | Flag rate | Overlap with joint anomalies |
| --- | ---: | ---: | ---: |
| `joint` | 12 | 0.0126 | 12 |
| `supply_temp_c` only | 8 | 0.0084 | 2 |
| `return_temp_c` only | 9 | 0.0094 | 3 |
| `flow` only | 8 | 0.0084 | 0 |

Interpretation:

- the joint model flags more windows than any single-feature model
- overlap between the joint anomalies and the univariate anomalies is weak
- under the stabilized lens, the flow-only model has zero overlap with the joint anomalies

Working conclusion:

For Abat Oliba, the joint model appears to be detecting interactions between variables rather than only single-channel extremes. That supports keeping the multivariate model as the main detector.

### 6.3 Overall interpretation

This comparison shows two useful things:

1. some anomalies are visible clearly in one feature alone
2. some anomalies are only convincing when the variables are considered together

So the best current role assignment is:

- joint autoencoder = primary anomaly detector
- per-feature autoencoders = comparison and interpretability layer

## 7. Current working conclusions

Current conclusions after this iteration:

1. The power unit is now assumed to be `kW` for all sheets, based on supervisor guidance.
2. The flow interpretation remains unresolved globally even under that fixed `kW` assumption.
3. Some sheets fit the resulting expected flow range much better than others.
4. Time-window clustering is now implemented and producing interpretable structure.
5. `cons_hostatgeria_underfloor_hea` remains the strongest primary case study.
6. Clustering supports the idea that its anomalies correspond to windows that leave its dominant normal regime.
7. Feature-space clustering currently looks more useful than latent-space clustering for meeting interpretation needs.
8. Per-feature autoencoders are useful for interpretation, but the joint autoencoder still appears to carry information that single-feature models miss.

## 8. Questions to ask the supervisor

### Data and units

1. Are all `Power Interval Trend Log` channels supposed to use the same unit?
2. If the expected flow is around `1-2`, does that expectation apply to all sheets, or only to some substations?
3. Does the derived-flow formula make physical sense for underfloor-heating and `cons_nostra_senyora` in the same way as it does for Abat Oliba or DHW radiators?
4. Should small or negative `Supply - Return` periods be treated as invalid/off-state periods, or as valid operational behavior?

### Clustering and methodology

5. Is the supervisor comfortable with clustering daily windows instead of clustering whole buildings?
6. Does the supervisor think the underfloor-heating regime separation is meaningful from an operational point of view?
7. Would the supervisor prefer the thesis to report clustering mainly as regime interpretation, not as the main anomaly detector?

### Validation

8. Are there logs, alarms, maintenance notes, or known abnormal dates for the anomalous April 2024 and October 2024 windows?
9. Would it be acceptable to treat historical anomaly windows as candidate events and then validate them through engineering interpretation when labels are absent?
10. For thesis reporting, would the supervisor prefer the joint autoencoder to remain the main detector, with per-feature autoencoders used as explanation/comparison models?

## 9. Recommended next work

If the supervisor agrees with the direction, the next steps should be:

1. Keep the `kW` assumption fixed and investigate why the same flow formula behaves differently across sheets.
2. Keep `cons_hostatgeria_underfloor_hea` as the primary case.
3. Use clustering as a supporting analysis for operating-regime interpretation.
4. Compare `24h` windows with `12h` windows to test whether shorter windows improve sensitivity without making interpretation worse.
5. Continue preparing the pipeline so the same reconstruction and clustering framework can later be used on incoming real-time data.
