# ADR 0001: Seoul Bike Sharing Demand Project Scope

Status: Accepted
Date: 2026-07-07

## Context

The BMDS2003 assignment requires a group data science project using CRISP-DM and Python. The selected title is "Seoul Bike Sharing Demand".

The dataset is a regression dataset about hourly public bicycle rentals in Seoul, with weather, date, season, holiday, and functioning-day information. The assignment requires a professionally written report, Python implementation files, machine learning models, and a simple deployment prototype.

This group has four members, so the project must include four machine learning models. The evaluation section should include at least 15 comparison points across the four models so the report demonstrates more than a shallow metric-only comparison.

The grading rubric gives high weight to model selection, preprocessing, exploratory analysis, visualisation, advanced analytics discussion, report structure, presentation, and a functional prototype.

## Decision

Frame the project as a regression problem under the "bike supply planning" project frame:

"Predict the hourly number of rented bikes in Seoul using weather, calendar, and operational features, so bike-sharing operators can plan bike supply and reduce shortages during high-demand periods."

Use CRISP-DM as the report structure:

1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modelling
5. Evaluation
6. Deployment
7. Conclusion

Recommended baseline model:

- Multiple Linear Regression

Recommended comparison models:

- Decision Tree Regressor
- Random Forest Regressor
- Gradient Boosting Regressor, or XGBoost-style regressor if allowed

Recommended evaluation metrics:

- MAE
- RMSE
- R2
- Adjusted R2, if the report wants to connect directly to the regression notes

Minimum comparison requirement:

- Compare all four models using at least 15 comparison points. These do not need to be 15 different metrics; they can combine metrics, charts, error analysis, interpretability, and practical deployment considerations.
- Recommended comparison points:
  1. MAE
  2. RMSE
  3. R2
  4. Adjusted R2
  5. Cross-validation score
  6. Training score vs testing score gap
  7. Error distribution or residual plot
  8. Actual vs predicted plot
  9. Error by hour
  10. Error by season
  11. Error by holiday or functioning day
  12. Prediction range realism
  13. Model interpretability
  14. Feature importance or coefficient explanation
  15. Training/tuning complexity

Recommended prototype:

- A Streamlit app where users enter weather/calendar conditions and receive a predicted hourly rented-bike count.
- Include simple charts such as predicted demand by hour, feature importance, and actual vs predicted values.

## Consequences

This scope aligns with the dataset's official regression task and the assignment rubric. It also gives the report a practical business story: operations planning for bike availability.

The main risk is treating hourly rows as random independent records. The team should discuss whether to use a chronological train/test split or a standard random split. A chronological split is more realistic for forecasting, while a random split may produce easier model performance.

The GitHub example is intentionally ignored for project planning. The team should still avoid copying any Kaggle notebook structure or text directly.

## Why This Project Frame

Bike supply planning is the recommended frame because it is practical, easy to explain, and directly connected to a regression target. It also supports a simple prototype: enter expected conditions and estimate the number of bikes likely to be rented in a given hour.

The team must choose one project frame because the frame controls the whole report: business objective, feature engineering, train/test split, model justification, evaluation discussion, prototype design, and conclusion. Mixing several frames would make the report feel unfocused and harder to defend during presentation.
