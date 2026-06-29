# Supervisor comment response - 2026-06-29

Clean revised file:

- `Thesis drafts/Thesis_Draft_29-06-2026_revised_method_v2.docx`

Marked-up comparison file:

- `Thesis drafts/Thesis_Draft_29-06-2026_revised_method_marked_changes.docx`

Revised file with supervisor comments retained:

- `Thesis drafts/Thesis_Draft_29-06-2026_revised_method_comments_retained.docx`

Original reviewed file preserved:

- `Thesis drafts/Thesis_Draft_22-06-2026_with_comments.docx`

## Main changes made

1. Reworked the abstract so it focuses on the methodology and main outcomes instead of naming specific buildings.
2. Replaced "HEAT paper" wording with "reference encoder-assisted clustering method" or similar phrasing.
3. Renamed the background subsection from "HEAT paper as reference" to "Reference encoder-assisted clustering method".
4. Rephrased the introduction/problem setting to emphasize the need to use available district-heating substation data for anomaly detection.
5. Made the research questions more general.
6. Rephrased the configuration question as: "What is the impact of changing the configuration settings of the proposed methodology on the expected anomaly-detection results?"
7. Replaced the flow explanation with measured-flow wording, avoiding emphasis on calculated flow rate as a thesis contribution.
8. Numbered the thermal power/flow relation as Equation (1).
9. Expanded the Method section with a formal autoencoder model:
   - input window definition
   - encoder mapping
   - decoder reconstruction
   - reconstruction-loss objective
   - total anomaly score
   - per-feature reconstruction error
   - dominant-feature attribution
10. Added numbered equations for the 3-sigma threshold and anomaly decision rule.
11. Added a numbered KMeans objective for the clustering section.
12. Restored the flow relation to the mass-flow form:
   - `m = P / (c_p (T_s - T_r))`
13. Renumbered numerical references so citations appear in first-use order and the bibliography follows that order.
14. Expanded the abstract again so it describes the method, evaluation approach, and main thesis outcome without naming individual buildings.
15. Renamed "Related-work positioning" to "Related work".

## Message to supervisor

The revised draft addresses the comments in the reviewed part of the document and expands the Method section with the requested mathematical formulation of the autoencoder model. The original commented file has been preserved, the clean revised version is saved as `Thesis_Draft_29-06-2026_revised_method_v2.docx`, a marked-up version showing the main removed/added wording is saved as `Thesis_Draft_29-06-2026_revised_method_marked_changes.docx`, and a supervisor-review version with the original comments retained is saved as `Thesis_Draft_29-06-2026_revised_method_comments_retained.docx`.
