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

If the power unit assumption is wrong, or if `delta-T` becomes very small, the derived flow can become misleading.

### 2.2 What was tested

A power-scaling sanity check was added. For each main DHC sheet, the script computes the median derived flow under several assumptions:

- `W`
- `10W`
- `100W`
- `kW`
- `10kW`

The script also computes the scale factor that would make the median flow roughly `1.5`, since the supervisor indicated expected values should often be around `1-2`.

Output file:

- `Results/tables/power_scaling_sanity_check.csv`

### 2.3 Current results

| Sheet | Median power (raw) | Median delta-T | Median flow if `kW` | Scale implied to reach flow `1.5` |
| --- | ---: | ---: | ---: | ---: |
| `cons_abat_oliba` | 30.0 | 3.92 | 2.03 | 819 |
| `cons_hostatgeria_DHW_radiators` | 30.6 | 5.46 | 1.41 | 1119 |
| `cons_hostatgeria_underfloor_hea` | 10.9 | 32.46 | 0.082 | 18672 |
| `cons_nostra_senyora` | 1.0 | 9.77 | 0.021 | 61258 |

### 2.4 Interpretation

This does **not** support one single clean answer for all sheets.

Observations:

1. For `cons_abat_oliba`, assuming `kW` gives a median derived flow of about `2.03`, which is already close to the supervisor's expected `1-2` range.
2. For `cons_hostatgeria_DHW_radiators`, assuming `kW` gives about `1.41`, also close to the expected range.
3. For `cons_hostatgeria_underfloor_hea`, assuming `kW` gives only about `0.082`.
4. For `cons_nostra_senyora`, assuming `kW` gives only about `0.021`.

So the situation is probably one of these:

- the `kW` assumption is reasonable for some sheets but not all
- the formula is not equally meaningful for all subsystems
- some sheets correspond to very different hydraulic regimes
- some channels may not be directly comparable in the way originally assumed

Working conclusion:

`kW` is still plausible for at least some sheets, but the derived-flow interpretation is not yet validated across the whole dataset.

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

## 5. Current working conclusions

Current conclusions after this iteration:

1. The power unit / flow interpretation remains unresolved globally.
2. The `kW` assumption still looks plausible for `cons_abat_oliba` and `cons_hostatgeria_DHW_radiators`.
3. The same assumption does not look equally plausible for `cons_hostatgeria_underfloor_hea` and `cons_nostra_senyora`.
4. Time-window clustering is now implemented and producing interpretable structure.
5. `cons_hostatgeria_underfloor_hea` remains the strongest primary case study.
6. Clustering supports the idea that its anomalies correspond to windows that leave its dominant normal regime.

## 6. Questions to ask the supervisor

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

## 7. Recommended next work

If the supervisor agrees with the direction, the next steps should be:

1. Confirm or narrow the power unit / scaling interpretation.
2. Keep `cons_hostatgeria_underfloor_hea` as the primary case.
3. Use clustering as a supporting analysis for operating-regime interpretation.
4. Compare `24h` windows with `12h` windows to test whether shorter windows improve sensitivity without making interpretation worse.
5. Continue preparing the pipeline so the same reconstruction and clustering framework can later be used on incoming real-time data.
