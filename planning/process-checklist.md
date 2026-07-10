# Process Checklist: Seoul Bike Supply Planning Project

Status: Completed build
Date: 2026-07-07

## Completion Evidence

- [x] Validation script passed: `src/validate_project.py`.
- [x] Prepared dataset shape is 8,760 rows and 18 columns.
- [x] Four models were trained and compared.
- [x] Model comparison table contains 29 comparison columns, above the required 15.
- [x] Selected model is Random Forest Regressor.
- [x] Prototype sample prediction is 2,856.93 rented bikes for the default evening summer scenario.
- [x] 36 required paths were checked by the validator.

## Current Understanding

- [x] Assignment documentation has been reviewed.
- [x] Project title is confirmed as "Seoul Bike Sharing Demand".
- [x] Project frame is confirmed as "Bike Supply Planning".
- [x] Problem type is confirmed as regression.
- [x] Target variable is confirmed as `Rented Bike Count`.
- [x] Group size is confirmed as four members.
- [x] Four machine learning models are required.
- [x] Evaluation includes at least 15 comparison points.
- [x] GitHub repo example is ignored.
- [x] Dataset is available at `data/raw/SeoulBikeData.csv`.

## Dataset Notes

- [x] Raw dataset contains 8,760 rows and 14 columns.
- [x] Each row represents one hour of bike-sharing demand.
- [x] Main feature groups are calendar/time, weather, season, holiday, and functioning-day variables.
- [x] Missing values are formally checked in the EDA notebook and tables.
- [x] Duplicate rows are formally checked in the EDA notebook and tables.
- [x] Data types are formally checked in the EDA notebook and tables.
- [x] CSV is read with explicit `cp949` encoding.

## Project Direction

- [x] Main business problem:
  - Predict hourly rented-bike demand so bike-sharing operators can prepare enough bikes and reduce shortages during high-demand periods.
- [x] Main user:
  - Bike-sharing operator, city mobility planner, or operations manager.
- [x] Main prototype:
  - Streamlit app where users enter time, weather, season, holiday, and functioning-day conditions to estimate hourly rented-bike count.

## Project Structure

- [x] Created `notebooks/`.
- [x] Created `src/`.
- [x] Created `app/`.
- [x] Created `models/`.
- [x] Created `figures/`.
- [x] Created `report/`.
- [x] Created `data/processed/`.
- [x] Created launch helper at `scripts/run_streamlit.ps1`.

## Main Deliverables

- [x] Created `notebooks/01_data_understanding.ipynb`.
- [x] Created `notebooks/02_data_preparation.ipynb`.
- [x] Created `notebooks/03_modelling_evaluation.ipynb`.
- [x] Created reusable preprocessing script at `src/data_preprocessing.py`.
- [x] Created training and evaluation script at `src/train_models.py`.
- [x] Created artifact builder at `src/create_project_artifacts.py`.
- [x] Created validation script at `src/validate_project.py`.
- [x] Created Streamlit app at `app/streamlit_app.py`.
- [x] Created report draft at `report/project_report_draft.md`.
- [x] Created report-ready charts under `figures/`.
- [x] Created trained model outputs under `models/`.

## Immediate Checklist

1. [x] Create the missing folders.
2. [x] Start `notebooks/01_data_understanding.ipynb`.
3. [x] Load `data/raw/SeoulBikeData.csv`.
4. [x] Display dataset shape, first rows, column names, and data types.
5. [x] Check missing values and duplicates.
6. [x] Produce summary statistics for numeric columns.
7. [x] Produce count summaries for categorical columns.
8. [x] Create first EDA charts:
   - demand by hour
   - demand by season
   - demand by holiday
   - demand by functioning day
   - temperature vs rented bike count
   - rainfall vs rented bike count
   - correlation heatmap
9. [x] Write short observations under each chart.
10. [x] Save report-ready charts into `figures/`.

## EDA Questions Answered

- [x] Which hours have the highest and lowest rented-bike demand?
- [x] Which seasons have the highest and lowest demand?
- [x] Does demand increase as temperature increases?
- [x] Does heavy rainfall reduce demand?
- [x] Does snowfall reduce demand?
- [x] Are holidays different from non-holidays?
- [x] What happens when `Functioning Day` is `No`?
- [x] Which features are most strongly related to `Rented Bike Count`?

## Data Preparation Checklist

- [x] Convert `Date` into a date type.
- [x] Extract useful date features: month, day, weekday, and weekend.
- [x] Encode categorical variables:
  - `Seasons`
  - `Holiday`
  - `Functioning Day`
- [x] Keep non-functioning-day records and document why.
- [x] Keep outliers and discuss why peak demand matters for supply planning.
- [x] Scale numeric features for the linear regression baseline.
- [x] Split data into training and testing sets.
- [x] Document every preprocessing decision for the report.

## Four-Model Checklist

- [x] Model 1: Multiple Linear Regression as baseline.
- [x] Model 2: Decision Tree Regressor.
- [x] Model 3: Random Forest Regressor.
- [x] Model 4: Gradient Boosting Regressor.
- [x] Tune model parameters where appropriate.
- [x] Save trained model outputs for comparison and prototype use.

## Evaluation Checklist

- [x] Compare all four models using at least 15 comparison points.
- [x] Include MAE.
- [x] Include RMSE.
- [x] Include R2.
- [x] Include adjusted R2.
- [x] Include training score.
- [x] Include testing score.
- [x] Include training vs testing gap.
- [x] Include cross-validation score.
- [x] Include residual distribution.
- [x] Include actual vs predicted plot.
- [x] Include error by hour.
- [x] Include error by season.
- [x] Include error by holiday or functioning day.
- [x] Include feature importance or coefficient interpretation.
- [x] Include model interpretability discussion.
- [x] Include training/tuning complexity discussion.
- [x] Include suitability for Streamlit deployment.
- [x] Select the final best model and justify it.

## Report Checklist

- [x] Cover page.
- [x] Executive summary.
- [x] Business understanding.
- [x] Data understanding.
- [x] Data preparation.
- [x] Modelling.
- [x] Evaluation.
- [x] Deployment.
- [x] Conclusion.
- [x] APA 7 references.
- [x] Minimum five credible references.
- [x] At least two academic papers.
- [x] Charts, model outputs, and tables are included or linked so the report draft is self-contained.

## Prototype Checklist

- [x] Build a simple Streamlit app.
- [x] Add input controls for hour, season, temperature, humidity, rainfall, snowfall, holiday, and functioning day.
- [x] Load the final trained model.
- [x] Display predicted rented-bike count.
- [x] Include a supporting supply buffer chart/explanation.
- [x] Create report-ready prototype preview at `report/prototype_screenshot.png`.

## Stop Conditions Before Moving To Modelling

- [x] Dataset loading is stable.
- [x] Missing values and duplicates are checked.
- [x] EDA charts are generated.
- [x] Main EDA observations are written.
- [x] Data preparation decisions are documented for the report.

## Next Action

Review `report/project_report_draft.md` with the group, assign each member to explain one model or CRISP-DM section, then convert the report into the required final submission format.
