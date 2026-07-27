# Seoul Bike Sharing Demand

## Cover Page

**Project title:** Seoul Bike Sharing Demand  
**Project frame:** Bike Supply Planning  
**Problem type:** Regression  
**Target variable:** Rented Bike Count  
**Group size:** Four members  
**Required models:** Four machine learning models  

## Executive Summary

This project predicts hourly bike rental demand in Seoul so a bike-sharing operator can prepare enough bicycles during high-demand periods and avoid unnecessary oversupply during low-demand periods. The dataset contains hourly rental demand, weather, holiday, season, and system-functioning information.

The best model is **Random Forest Regressor** with test RMSE **181.46**, MAE **102.91**, and R2 **0.920**.

## 1. Business Understanding

The business problem is bike supply planning. The operational user is a bike-sharing operator, city mobility planner, or operations manager who needs a demand estimate before deciding how many bicycles should be available. The key decision is not simply which algorithm is most accurate, but which model provides trustworthy demand estimates for planning supply.

## 2. Data Understanding

The raw dataset has 8,760 hourly records and 14 original columns. It contains no missing values and no duplicate rows after formal checking. The target is hourly rented-bike count.

Main EDA findings:

- 18:00 has the highest average rented-bike demand.
- 4:00 has the lowest average rented-bike demand.
- Summer has the highest average demand.
- Winter has the lowest average demand.
- Demand generally increases with temperature; the correlation is 0.54.
- Rainfall reduces demand: dry-hour average is 739, while hours with at least 5 mm rain average 73.
- Snowfall reduces demand: no-snow average is 732, while snow hours average 185.
- No Holiday has higher average demand than Holiday.
- When Functioning Day is No, demand drops heavily and is usually near zero.
- The strongest numeric relationships are temperature_c, hour, dew_point_temperature_c, solar_radiation_mj_per_m2, humidity_pct.

Report-ready charts are saved in the `figures/` folder:

- `01_demand_by_hour.png`
- `02_demand_by_season.png`
- `03_demand_by_holiday.png`
- `04_demand_by_functioning_day.png`
- `05_temperature_vs_rented_bike_count.png`
- `06_rainfall_vs_rented_bike_count.png`
- `07_correlation_heatmap.png`

## 3. Data Preparation

- Date was converted to a date type and expanded into month, day, weekday, and weekend fields.
- Categorical variables were one-hot encoded: seasons, holiday, and functioning_day.
- Non-functioning-day records were kept because a zero-demand closure state is operationally meaningful.
- Demand outliers were kept because supply planning must understand peak demand rather than hide it.
- Numeric features were scaled so Multiple Linear Regression can be compared fairly with the tree models.

The prepared modelling dataset is saved as `data/processed/seoul_bike_prepared.csv`.

## 4. Modelling

The four required models are:

1. Multiple Linear Regression as a baseline.
2. Decision Tree Regressor.
3. Random Forest Regressor.
4. Gradient Boosting Regressor.

Tree and boosting models were tuned with cross-validation. The linear model was kept as a transparent baseline.

## 5. Evaluation

The project uses more than 15 comparison points: MAE, RMSE, R2, adjusted R2, training score, testing score, train-test gap, cross-validation RMSE, residual mean, residual standard deviation, maximum absolute error, error by hour, error by season, error by holiday, error by functioning day, feature importance or coefficient strength, interpretability, training and tuning complexity, Streamlit suitability, fit time, tuned parameters, and ranking.

| model | test_mae | test_rmse | test_r2 | adjusted_r2 | training_r2 | train_test_r2_gap | cross_validation_rmse | top_feature | rank_by_rmse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest Regressor | 102.912 | 181.461 | 0.920 | 0.919 | 0.984 | 0.064 | 180.639 | num__temperature_c | 1 |
| Gradient Boosting Regressor | 128.067 | 202.682 | 0.900 | 0.899 | 0.926 | 0.026 | 202.086 | num__temperature_c | 2 |
| Decision Tree Regressor | 138.193 | 241.534 | 0.858 | 0.857 | 0.938 | 0.081 | 242.036 | num__hour | 3 |
| Multiple Linear Regression | 306.454 | 421.051 | 0.567 | 0.565 | 0.559 | -0.008 | 431.239 | cat__functioning_day_No | 4 |

Final selection reason: Random Forest Regressor achieved the lowest test RMSE among the four required models while remaining suitable for a Streamlit prototype.

## 6. Deployment

The prototype is a Streamlit app located at `app/streamlit_app.py`. Users can enter hour, season, temperature, humidity, rainfall, snowfall, holiday status, and functioning-day status. The app loads `models/best_model.pkl` and displays the predicted rented-bike count with a simple supply buffer chart.

Prototype preview image: `report/prototype_screenshot.png`.

Project source code and deployment files: [ngyinhao/data-science-asg](https://github.com/ngyinhao/data-science-asg).

Live deployed prototype: [data-science-asg.streamlit.app](https://data-science-asg.streamlit.app/).

## 7. Conclusion

The bike supply planning frame makes the project practical: the model is judged by how well it supports an operations decision, not only by raw accuracy. The selected model should be used as a decision-support tool together with current station inventory, local events, and staff judgement.

## References

Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5-32. https://doi.org/10.1023/A:1010933404324

Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189-1232. https://doi.org/10.1214/aos/1013203451

Joe Beach Capital. (n.d.). *Seoul Bike Share Demand | Data Import*. Kaggle. https://www.kaggle.com/code/joebeachcapital/seoul-bike-share-demand-data-import

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825-2830. https://jmlr.org/papers/v12/pedregosa11a.html

Sathishkumar, V. E., Park, J., & Cho, Y. (2020). Using data mining techniques for bike sharing demand prediction in metropolitan city. *Computer Communications, 153*, 353-366. https://doi.org/10.1016/j.comcom.2020.02.007

Seoul Bike Sharing Demand [Dataset]. (2020). *UCI Machine Learning Repository*. https://doi.org/10.24432/C5F62R
