# Project Frame Options: Seoul Bike Sharing Demand

Status: Draft
Date: 2026-07-07

## Why A Project Frame Matters

A project frame is the main business story of the project. It decides what problem the team is solving, how the models are judged, what visuals matter most, and what the prototype should demonstrate.

For this assignment, the team should choose one main frame instead of mixing several. A single frame makes the report clearer and helps every section support the same objective.

## Option 1: Bike Supply Planning

Business question:

"How many bikes are likely to be rented in a specific hour, given the weather, date, season, holiday status, and operational conditions?"

Main user:

- Bike-sharing operator or city mobility planner.

Main decision supported:

- How many bikes should be available at different times and under different conditions.

Best model objective:

- Predict hourly rented bike count as accurately as possible.

Best prototype:

- A Streamlit demand estimator where the user selects hour, season, weather, holiday status, and functioning day, then receives a predicted rented-bike count.

Strengths:

- Strong fit with the dataset because the target is rented bike count.
- Clear business impact: reduce bike shortages and improve availability.
- Easy to explain in report and presentation.
- Allows useful EDA on hour, season, temperature, rainfall, and holiday patterns.
- Works well with standard regression models.

Weaknesses:

- It is less advanced than a full time-series forecasting project.
- The report must be careful not to claim exact station-level allocation because the dataset is city-level, not station-level.

Recommendation:

- Choose this as the main project frame. It is the best balance between assignment fit, business meaning, modelling feasibility, and prototype simplicity.

## Option 2: Weather Impact Analysis

Business question:

"How do weather conditions affect bike-sharing demand in Seoul?"

Main user:

- City analyst, transport planner, or operations analyst.

Main decision supported:

- Understand which weather conditions increase or reduce demand.

Best model objective:

- Explain the relationship between weather variables and rented bike count.

Best prototype:

- An interactive dashboard showing demand changes across temperature, humidity, rainfall, snowfall, visibility, and seasons.

Strengths:

- Very strong for exploratory data analysis.
- Easy to produce meaningful visualisations.
- Good for explaining feature importance.

Weaknesses:

- Weaker as the main machine learning frame because the assignment expects prediction, not only explanation.
- Calendar and time variables may be just as important as weather, so the frame may become too narrow.
- The prototype may look more like an EDA dashboard than a prediction deployment.

Recommendation:

- Use this as a supporting analysis inside the EDA and discussion sections, not as the main project frame.

## Option 3: Hourly Demand Forecasting

Business question:

"Can we forecast future hourly bike demand based on historical demand patterns and time-related features?"

Main user:

- Operations manager planning demand ahead of time.

Main decision supported:

- Prepare for expected high-demand or low-demand periods.

Best model objective:

- Predict future hourly rented bike count using past and current information.

Best prototype:

- A future-demand chart where the user selects a forecast period and sees predicted demand by hour or day.

Strengths:

- Sounds very realistic and professional.
- Encourages chronological train/test split and time-aware validation.
- Can produce strong presentation visuals.

Weaknesses:

- More complex than required for this assignment.
- The original dataset has weather features for each hour; for real forecasting, future weather may not be known exactly.
- Requires careful feature engineering, such as lag variables or rolling averages, if the team wants to make it truly time-series based.
- Easier to make methodological mistakes.

Recommendation:

- Do not choose this as the main frame unless the team wants extra complexity. It can be mentioned as a future improvement.

## Final Recommendation

Choose "Bike Supply Planning" as the main project frame.

Reason:

It keeps the project clearly predictive, business-focused, and realistic for a four-member assignment. It also lets the team include weather impact analysis and hourly trend analysis as supporting evidence without turning the entire project into a more difficult forecasting task.
