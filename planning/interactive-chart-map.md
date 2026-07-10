# Interactive chart map

This map records the purpose and source of each interactive Streamlit visual.

| Page | Analytical question | Chart form | Data source |
|---|---|---|---|
| Prediction | How should the forecast translate into a supply buffer? | Horizontal lollipop | Live model prediction |
| Prediction | How does predicted demand change across the selected day? | Area and line profile | Live 24-hour model scenarios |
| Prediction | How does the model respond to temperature while other inputs stay fixed? | Sensitivity line with reference rule | Live temperature model scenarios |
| Model comparison | Which model has the lowest held-out RMSE? | Ranked lollipop | `models/model_comparison.csv` |
| Model comparison | How do MAE, test RMSE, and cross-validation RMSE compare? | Grouped bars | `models/model_comparison.csv` |
| Model comparison | Which models show the largest train-test R2 gap? | Dumbbell | `models/model_comparison.csv` |
| Model comparison | Where are the largest segment-level errors? | Heatmap | `models/model_comparison.csv` |
| Chosen model | How closely do predictions follow actual demand? | Brushed scatter with ideal line | `models/test_predictions_best_model.csv` |
| Chosen model | Are residuals centered around zero? | Histogram with zero reference | `models/test_predictions_best_model.csv` |
| Chosen model | Which hours are hardest to predict? | Line and point profile | `models/test_predictions_best_model.csv` |
| Chosen model | How does error spread differ by season? | Box-and-whisker range | `models/test_predictions_best_model.csv` |
| Chosen model | Which features drive the selected model? | Interactive lollipop ranking | `models/feature_importance_best_model.csv` |

Palette policy: blue, orange, gold, pink, and olive are used only where category identity matters. Single-series charts use one root color plus neutral reference marks. Tooltips provide exact values, while line style, position, and marker shape preserve meaning without relying on color alone.
