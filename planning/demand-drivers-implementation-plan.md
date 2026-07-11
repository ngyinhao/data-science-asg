# Project insights page implementation plan

## Status

**Interview scope confirmed. Ready for implementation approval; nothing in this plan has been implemented or deployed yet.**

This document records the confirmed addition of an interactive exploratory-data-analysis page to the Streamlit website. The interview decisions have been incorporated below. Application implementation and deployment still require explicit approval.

## Confirmed interview decisions

| Decision | Confirmation | Implementation interpretation |
|---|---|---|
| Page title | Confirmed | Use `Project insights`. |
| Submission status | Confirmed | This page is a required submission component, not an optional presentation enhancement. It must receive the same validation and deployment QA as the existing pages. |
| Navigation position | Confirmed | Use the recommended position between `Prediction` and `Model comparison`. |
| Variable coverage | Confirmed | All twelve variables must be individually selectable and clickable. |
| Functioning-day handling | Confirmed by recommendation | Provide an explicit functioning-day filter. Default weather analysis to functioning days, while allowing `All days` and `Not functioning` for transparency. |
| Rainfall and snowfall bands | Confirmed by recommendation | Use the data-supported bands defined in this plan. |
| Mean versus median | Confirmed by recommendation | Show both. Emphasise mean for consistency with existing EDA statements and median for resistance to outliers. |
| Combined-effects view | Confirmed by recommendation | Use hour by season as the primary heatmap. Temperature remains fully covered in its individual-variable chart. |
| Downloadable filtered data | Confirmed by recommendation | Include a CSV download inside a collapsed expander so it supports reproducibility without cluttering the page. |
| Extra lecturer formatting | Confirmed | No additional requirements for subtitles, captions, screenshots, or report cross-references were provided. Standard analytical labels and captions are still required for clarity. |

## Objective

Add a `Project insights` page that explains how individual time, weather, calendar, and operating variables are associated with hourly rented-bike demand.

The page should help a reader answer:

- when demand is usually highest or lowest,
- which weather conditions are associated with higher or lower demand,
- how demand differs across seasons, holidays, and operating states,
- how much data supports each comparison,
- and how these observed relationships differ from model-based feature importance or sensitivity.

The page is supporting EDA for the bike-supply-planning story. It must not present an observed association as proof that a variable causes demand to change.

## Confirmed navigation position

Recommended page order:

1. `Prediction`
2. `Project insights`
3. `Model comparison`
4. `Why this model was chosen`

This order moves from the operational result to the evidence behind demand, then to model evaluation and final model selection.

## Confirmed page structure

### 1. Summary

Start with a short explanation of the dataset grain and analytical scope:

- one row represents one hour,
- the target is hourly rented-bike count,
- comparisons are descriptive associations,
- filters can change the population included in a chart.

Show a compact summary of the strongest existing EDA findings:

- peak average demand occurs at 18:00,
- the lowest average demand occurs at 04:00,
- summer has the highest average demand and winter the lowest,
- temperature has a positive correlation of approximately 0.54 with demand,
- dry hours average approximately 739 rentals,
- hours with at least 5 mm of rain average approximately 73 rentals,
- hours without snow average approximately 732 rentals, compared with approximately 185 during snow,
- non-functioning periods have near-zero demand.

These values must be recalculated from the prepared dataset during implementation rather than hard-coded into chart logic.

### 2. Overview visual

Add a correlation heatmap for numeric variables.

**Question:** Which numeric variables have the strongest positive or negative relationship with rented-bike demand?

**Information to show:**

- correlation coefficient in each cell or tooltip,
- a diverging scale centred on zero,
- variables ordered consistently,
- a note that correlation does not prove causation.

The heatmap should act as a high-level index, not the only evidence for individual variables.

### 3. Individual-variable explorer

Provide a single clickable selector so the user can choose one variable at a time. All twelve variables are required. This avoids placing twelve large charts on one page while still covering every required predictor.

Confirmed variables:

- hour,
- temperature,
- humidity,
- wind speed,
- visibility,
- dew-point temperature,
- solar radiation,
- rainfall,
- snowfall,
- season,
- holiday status,
- functioning-day status.

Each selection should update the chart, takeaway, units, sample size, and interpretation.

#### Numeric continuous variables

Variables: temperature, humidity, wind speed, visibility, dew point, and solar radiation.

**Recommended chart:** binned mean-and-median demand profile with points and a connecting line.

**Information to show:**

- variable range on the horizontal axis,
- average and median rented-bike count,
- observation count for each bin,
- exact bin range and values in the tooltip,
- optional raw-point sample only if it remains readable and performant.

Using bins will reveal the overall shape more clearly than plotting all 8,760 overlapping points. Bin definitions must remain consistent when users apply filters.

#### Rainfall and snowfall

**Recommended chart:** grouped box plot or dot-and-interval comparison using meaningful exposure bands.

Confirmed rainfall bands, supported by the prepared dataset:

- no rain: 0 mm,
- light rain: greater than 0 to 1 mm,
- moderate rain: greater than 1 to 5 mm,
- heavy rain: greater than 5 mm.

The current full-dataset sample sizes are 8,232, 280, 182, and 66 respectively. Tooltips must display the post-filter sample sizes because filtering will change them.

Confirmed snowfall bands:

- no snow: 0 cm,
- light snow: greater than 0 to 1 cm,
- heavier snow: greater than 1 cm.

The current full-dataset sample sizes are 8,317, 255, and 188 respectively. These bands retain enough observations to make a comparison without inventing many sparse categories.

**Information to show:** median, mean, spread, sample size, and the exact definition of each band. The mean should be the primary marked value because the existing report uses average demand; the median should remain visible to show whether outliers influence that average. Sparse post-filter bands should be clearly flagged.

#### Hour

**Recommended chart:** interactive 24-hour line-and-point profile.

**Information to show:** average and median demand at each hour, observation count, and annotations for the highest and lowest hours.

#### Season

**Recommended chart:** seasonal box plot.

**Information to show:** median, interquartile range, overall range or outliers, mean, and sample size. This is more informative than comparing four averages alone.

#### Holiday and functioning-day status

**Recommended chart:** paired dot-and-interval comparison.

**Information to show:** average, median, sample size, absolute difference, and percentage difference between groups. The functioning-day chart should clearly explain why zero-demand records are operationally meaningful.

### 4. Combined-effects view

Add one matrix view for an interaction that supports the supply-planning story.

**Confirmed choice:** hour-by-season heatmap of average rented-bike demand.

**Question:** At which combinations of hour and season is demand highest?

**Information to show:** average rented-bike count, observation count in the tooltip, a consistent scale, and a visible annotation or accompanying sentence identifying the highest-demand combinations.

This is preferred over hour by temperature band because each hour-season cell has broad coverage and the result translates directly into seasonal supply scheduling. Temperature remains available as one of the twelve individual variable views, so the page does not need a second heatmap that repeats the same evidence.

### 5. Interpretation and limitations

End with a concise explanation that:

- these charts describe historical associations,
- variables can be related to one another,
- filtering can change apparent relationships,
- feature importance describes how the selected model uses variables,
- prediction-page sensitivity curves describe model response while other inputs are held fixed,
- neither EDA nor model response alone proves a causal effect.

## Confirmed interactions and UI behaviour

- A searchable `st.selectbox` for the twelve-variable explorer. A selectbox is preferable to twelve pills or buttons because it stays readable on mobile and gives every variable an explicit clickable option.
- A four-value season filter using `st.pills` with multi-selection: Spring, Summer, Autumn, and Winter. All seasons are selected by default.
- A functioning-day `st.segmented_control` with `Functioning days`, `All days`, and `Not functioning`. Weather-variable views default to `Functioning days` because the 295 non-functioning records all have zero rentals and would otherwise confound weather-demand interpretation.
- Hour, season, holiday, and functioning-day views may automatically switch to `All days` when excluding a group would invalidate the comparison. The active population must always be stated above the chart.
- Hover tooltips containing exact values and observation counts.
- Pan or zoom only for charts where it improves inspection.
- A `Reset filters` button that restores all seasons and the appropriate functioning-day default.
- A collapsed `Download filtered data` expander containing a CSV download for the currently filtered historical rows. The label must say `filtered data`, not `future data`, because this page presents historical observations rather than future forecasts.

Filters should be limited to those that materially change the analytical question. Too many controls would make the page harder to explain during assessment.

### Proposed page layout

1. Page title and a one-sentence EDA-versus-causation explanation.
2. Compact insight summary cards.
3. A bordered filter container with the variable selector, season filter, functioning-day filter, and reset action.
4. One full-width individual-variable chart with its takeaway and sample context.
5. The hour-by-season combined-effects heatmap.
6. Correlation overview and interpretation notes in a secondary section.
7. Collapsed methodology and filtered-data download expanders.

On mobile, controls and charts should stack vertically. On desktop, the variable selector and filters may share one responsive horizontal container. The chart itself should remain full-width so labels and tooltips stay readable.

## Data source and preparation

Primary source:

- `data/processed/seoul_bike_prepared.csv`

Supporting documented findings:

- `report/eda_observations.md`
- `report/project_report_draft.md`

Implementation should add a cached data loader and perform inexpensive filtering outside the cached load. All derived fields, including bins and readable category labels, should be created in one reusable preparation function.

Required QA checks:

- confirm 8,760 hourly records before filters,
- verify target and feature units,
- verify category values and ordering,
- verify every bin has enough observations for a defensible comparison,
- reconcile displayed summary values with `report/eda_observations.md`,
- ensure non-functioning-day zero demand is explained rather than silently removed,
- verify chart tooltips and labels at laptop and mobile widths.
- verify the filtered CSV contains only the rows represented by the active filters and never changes the source dataset.

## Visual and accessibility policy

- Use interactive Altair charts rendered with `st.altair_chart`.
- Use blue as the main mark colour with orange or gold for a meaningful comparator.
- Use a diverging palette only for signed correlation values.
- Use up to five colours only when category identity is necessary, such as the four seasons.
- Do not rely on colour alone; preserve meaning through position, marker form, line style, labels, or faceting.
- Keep chart backgrounds consistent with the existing Streamlit theme.
- Provide readable titles, units, context, and sample sizes.
- Avoid decorative chart types that distort comparisons, including 3D charts and unnecessary pie charts.

## Proposed code changes after approval

- Add `app/app_pages/project_insights.py`.
- Register the page in `app/streamlit_app.py`.
- Add cached prepared-data loading to `app/app_utils.py`.
- Add reusable EDA chart builders to `app/chart_utils.py` or a focused `app/eda_chart_utils.py` module.
- Add the approved visuals to `planning/interactive-chart-map.md` after implementation.
- Update the report only if the final website wording or calculated findings change the submitted narrative.

## Acceptance criteria

The proposed work will be complete when:

- the new page appears in the approved navigation position,
- every selected variable has an analytically appropriate interactive view,
- all tooltips include exact demand values and sample context,
- the summary statements match the processed dataset,
- EDA association, model feature importance, and model sensitivity are clearly distinguished,
- the page works in light and dark themes and at desktop and mobile widths,
- the application passes local validation without console errors,
- the approved changes are committed, pushed, and verified on the live Streamlit deployment.

## Interview confirmation checklist

- [x] Use the page title `Project insights`.
- [x] Treat the page as required for submission.
- [x] Place it between `Prediction` and `Model comparison`.
- [x] Make all twelve variables individually selectable.
- [x] Provide functioning-day filtering with the recommended weather-analysis default.
- [x] Use data-supported rainfall and snowfall bands.
- [x] Show both mean and median, with mean as the primary report-consistent value.
- [x] Use hour by season for the combined-effects heatmap.
- [x] Provide filtered historical data download in a collapsed expander.
- [x] Record that there are no extra lecturer requirements for subtitles, captions, screenshots, or report cross-references.
- [ ] Approve application implementation and deployment.

## Deferred until approval

No application code, chart output, report text, Git commit, or deployment change should be made from this plan until the interview decisions are reviewed and implementation is explicitly approved.
