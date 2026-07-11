# Website implementation plan

## Objective

Enhance the Streamlit website so it includes:

- the existing prediction page,
- a dedicated model comparison page,
- a dedicated page explaining which model was selected for prediction and why,
- charts and graphs displayed directly inside the website, following the style expected by the assignment example.

## Proposed website structure

The website will be reorganized from a single-page app into a small multi-page Streamlit application with the following pages:

1. `Prediction`
2. `Model comparison`
3. `Why this model was chosen`

This structure keeps the forecasting tool separate from the reporting and justification content, which makes the website clearer for assignment presentation.

## Implementation plan

### 1. Refactor the app into a multi-page Streamlit website

- Update the current app entry file to use Streamlit multi-page navigation.
- Create separate page files so each section of the website has a focused purpose.
- Keep the prediction feature as the main operational page.

## 2. Reuse existing project outputs as website data sources

The website will read directly from existing project files instead of recreating results manually.

Main data sources:

- `models/model_comparison.csv`
- `models/model_metadata.json`
- `models/feature_importance_best_model.csv`
- existing chart images in `figures/`

This ensures consistency between the report, trained models, and website content.

## 3. Keep and polish the prediction page

- Preserve the current demand prediction workflow.
- Keep the input controls for time, weather, season, holiday, and functioning day.
- Retain the predicted rented-bike result and buffer chart.
- Adjust the page layout so it fits the new website navigation cleanly.

## 4. Add a model comparison page

This page will compare all four required models:

1. Multiple Linear Regression
2. Decision Tree Regressor
3. Random Forest Regressor
4. Gradient Boosting Regressor

Planned content for this page:

- model comparison summary cards,
- model ranking table,
- RMSE comparison chart,
- explanation of important evaluation measures such as RMSE, MAE, R2, fit time, and overfitting gap,
- short interpretation of which models performed better and which performed worse.

## 5. Add a page explaining why the chosen model was selected

This page will focus on the final selected model, which is currently:

- `Random Forest Regressor`

Planned content for this page:

- the selected model name,
- the model selection reason from metadata,
- explanation of why it is more suitable than the others,
- visual evidence to support the decision.

Planned supporting charts:

- actual vs predicted,
- residual distribution,
- error by hour,
- error by season,
- feature importance.

## 6. Show charts for each model within the website

To satisfy the requirement that the graph and chart should also be displayed within the website, the model-related pages will include visual sections rather than text-only summaries.

Planned approach:

- use the existing overall model comparison chart,
- display best-model evaluation charts on the chosen-model page,
- add model-level visual summaries if needed so each of the four models is represented clearly inside the website.

This will help explain both:

- which model was used for prediction,
- why that model was chosen over the alternatives.

## 7. Final verification

After implementation:

- run the website locally,
- verify page navigation,
- verify that all tables, graphs, and charts display correctly,
- confirm the explanation aligns with the example and assignment expectations,
- refine labels and layout for clearer presentation.

## Expected outcome

The final website should allow the user to:

- make a rental demand prediction,
- compare the trained models visually,
- understand which model is used in the prediction system,
- see why the selected model was chosen based on performance and suitability.

## Confirmed submission enhancement awaiting implementation

A fourth page titled `Project insights` is documented in [`planning/demand-drivers-implementation-plan.md`](demand-drivers-implementation-plan.md).

The interview confirmed that this page is required for submission and that all twelve variables must be individually selectable. It will present interactive EDA showing how individual time, weather, calendar, and operating variables are associated with rented-bike demand. It is **not yet implemented or deployed**. The dedicated plan contains the confirmed UI behaviour, chart contract, data requirements, acceptance criteria, and remaining approval step.

## Recommended final page flow

1. `Prediction` page for forecasting demand
2. `Model comparison` page for comparing all models
3. `Why this model was chosen` page for final model justification

The confirmed navigation flow is:

1. `Prediction`
2. `Project insights`
3. `Model comparison`
4. `Why this model was chosen`
