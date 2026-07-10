# EDA Observations

These notes answer the project EDA questions for bike supply planning.

- **Highest Hour**: 18:00 has the highest average rented-bike demand.
- **Lowest Hour**: 4:00 has the lowest average rented-bike demand.
- **Highest Season**: Summer has the highest average demand.
- **Lowest Season**: Winter has the lowest average demand.
- **Temperature**: Demand generally increases with temperature; the correlation is 0.54.
- **Rainfall**: Rainfall reduces demand: dry-hour average is 739, while hours with at least 5 mm rain average 73.
- **Snowfall**: Snowfall reduces demand: no-snow average is 732, while snow hours average 185.
- **Holiday**: No Holiday has higher average demand than Holiday.
- **Functioning Day**: When Functioning Day is No, demand drops heavily and is usually near zero.
- **Strongest Features**: The strongest numeric relationships are temperature_c, hour, dew_point_temperature_c, solar_radiation_mj_per_m2, humidity_pct.

## Chart Notes

- `01_demand_by_hour.png`: Demand is highest around 18:00 and lowest around 4:00.
- `02_demand_by_season.png`: Summer has the highest average demand, while Winter has the lowest.
- `03_demand_by_holiday.png`: The higher-demand holiday group is No Holiday.
- `04_demand_by_functioning_day.png`: Non-functioning rows show near-zero demand, so this field is important for operational interpretation.
- `05_temperature_vs_rented_bike_count.png`: Temperature has a correlation of 0.54 with rented bike count.
- `06_rainfall_vs_rented_bike_count.png`: Average demand is 739 in dry hours and 163 in rainy hours.
- `07_correlation_heatmap.png`: The strongest numeric relationships with demand are temperature_c, hour, dew_point_temperature_c.
- `snowfall_observation`: Average demand is 732 without snowfall and 185 when snowfall is recorded.