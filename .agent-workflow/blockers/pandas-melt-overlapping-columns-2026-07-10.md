# Pandas melt produced an empty marker dataset from overlapping columns

- **Date:** 2026-07-10
- **Context and intended action:** Validate the layered rainfall chart after changing its visible whisker calculation.
- **Symptom:** The Altair specification contained four distribution rows but zero rows for the mean/median marker layer.
- **Impact:** Mean and median markers were absent from rainfall, snowfall, season, holiday, and functioning-day interval charts even though the summary statistics and interval layer rendered.
- **Cause:** `DataFrame.melt` received `mean_demand` and `median_demand` in both `id_vars` and `value_vars`, so no value rows were produced for those fields.
- **Troubleshooting:** Inspecting the generated chart datasets exposed row counts `[4, 0]`, isolating the problem to the reshaped marker layer rather than Altair rendering.
- **Workaround:** Keep tooltip copies of mean and median as distinct identifier fields, and melt the original mean/median columns only as values.
- **Prevention:** Assert nonzero row counts for every layered chart dataset and avoid overlapping `id_vars` and `value_vars` in Pandas reshapes.

