# Next Steps: Seoul Bike Supply Planning Project

Status: Completed build ready for review
Date: 2026-07-07

See also:

- `planning/process-checklist.md` for the completed checklist and validation evidence.
- `report/project_report_draft.md` for the current CRISP-DM report draft.
- `models/model_comparison.csv` for the full 29-column model comparison.

## Confirmed Direction

Project title:

- Seoul Bike Sharing Demand

Project frame:

- Bike Supply Planning

Main problem statement:

- Predict the hourly number of rented bikes in Seoul using weather, calendar, and operational features so bike-sharing operators can plan bike supply and reduce shortages during high-demand periods.

Target variable:

- Rented Bike Count

Problem type:

- Regression

Group requirement:

- Four members means four machine learning models are required.
- The evaluation includes more than 15 comparison points.

## Completed Outputs

- Data understanding notebook: `notebooks/01_data_understanding.ipynb`
- Data preparation notebook: `notebooks/02_data_preparation.ipynb`
- Modelling and evaluation notebook: `notebooks/03_modelling_evaluation.ipynb`
- Prepared dataset: `data/processed/seoul_bike_prepared.csv`
- Model comparison: `models/model_comparison.csv`
- Selected model: `models/best_model.pkl`
- Streamlit prototype: `app/streamlit_app.py`
- Prototype preview: `report/prototype_screenshot.png`
- Report draft: `report/project_report_draft.md`
- Validation script: `src/validate_project.py`

## Model Result Summary

Final selected model:

- Random Forest Regressor

Reason:

- It achieved the lowest test RMSE among the four required models while remaining suitable for a Streamlit prototype.

Model ranking by test RMSE:

1. Random Forest Regressor
2. Gradient Boosting Regressor
3. Decision Tree Regressor
4. Multiple Linear Regression

## Recommended Member Split

Member 1:

- Business understanding, project frame, dataset description, EDA for hour and season patterns.

Member 2:

- Data preparation, feature engineering, weather EDA, preprocessing decisions.

Member 3:

- Multiple Linear Regression, Decision Tree, tuning explanation, model comparison table.

Member 4:

- Random Forest, Gradient Boosting, final model selection, Streamlit prototype.

All members:

- Review the report draft, add names/student IDs, polish APA references, prepare presentation slides, and practise Q&A.

## Next Concrete Task

Review and polish the report draft for submission formatting. The core project build is complete; the next work is group review, lecturer-format alignment, and presentation preparation.
