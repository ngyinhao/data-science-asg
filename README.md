# Seoul Bike Supply Planner

Project repository: [ngyinhao/data-science-asg](https://github.com/ngyinhao/data-science-asg)

Live application: [data-science-asg.streamlit.app](https://data-science-asg.streamlit.app/)

## Project Summary

This project is a Streamlit-based web application that estimates hourly bike rental demand in Seoul. It is designed as a decision-support prototype for bike supply planning, helping users explore how time, weather, season, holidays, and operating status may influence expected rented bike counts.

The application uses a trained machine learning model to generate demand estimates from user-selected input values. Supporting notebooks, scripts, model artifacts, figures, and reports are included in the project to document the data preparation, modelling, and evaluation workflow.

## Problem Statement and Objective

Bike-sharing systems need enough bikes at the right place and time to meet customer demand. If supply is too low, users may not find available bikes. If supply is too high, operators may waste effort and resources on unnecessary redistribution.

The objective of this project is to predict hourly rented bike demand using weather and calendar-related features, then present that prediction through a simple web interface. The broader goal is to support better short-term supply planning by turning historical demand patterns into an accessible forecasting tool.

## Dataset Information

The project uses the Seoul bike sharing dataset stored at `data/raw/SeoulBikeData.csv`.

Key points about the dataset:

- Target variable: `rented_bike_count`
- Main numeric features: hour, temperature, humidity, wind speed, visibility, dew point temperature, solar radiation, rainfall, snowfall, month, day, weekday, and weekend indicator
- Main categorical features: season, holiday, and functioning day
- Derived features: the original date field is expanded into `month`, `day`, `weekday`, and `is_weekend`

Preprocessing decisions used in the project:

- Column names are cleaned into consistent snake_case format
- Date values are converted into calendar-based features
- Categorical variables are one-hot encoded
- Numeric variables are imputed and scaled in the shared preprocessing pipeline
- Non-functioning-day rows are kept because closure periods are treated as operationally meaningful scenarios
- Demand outliers are kept so the model can still learn peak-demand situations

## Folder Structure

```text
Assignment/
|-- app/                  # Streamlit web app entry point
|-- data/
|   |-- raw/              # Original dataset
|   `-- processed/        # Cleaned and prepared dataset
|-- Documentation/        # Assignment references and supporting PDFs
|-- figures/              # Generated charts and visual outputs
|-- models/               # Trained models and model metadata
|-- notebooks/            # Data understanding, preparation, and modelling notebooks
|-- planning/             # Planning notes and decision records
|-- report/               # Draft report content and exported tables
|-- scripts/              # Helper scripts such as Streamlit launcher
|-- src/                  # Preprocessing, training, validation, and artifact scripts
|-- tmp/                  # Temporary runtime files
|-- requirements.txt      # Python dependencies
`-- README.md             # Project overview and usage guide
```

## Main Libraries Used

- `pandas` for data loading and preprocessing
- `numpy` for numerical operations
- `matplotlib` for charts and figures
- `scikit-learn` for preprocessing, model training, tuning, and evaluation
- `joblib` for saving and loading trained models
- `streamlit` for the web application interface
- `nbformat` for notebook-related handling in the project workflow

## How to Run the Website Locally

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start the Streamlit app

You can use the helper script:

```powershell
.\scripts\run_streamlit.ps1
```

Or run Streamlit directly:

```powershell
python -m streamlit run streamlit_app.py
```

The root launcher keeps the conventional Streamlit Community Cloud entry-point path
valid while page implementations stay organized in the `app/` package.

### 4. Open the website

After the app starts, open the local address shown in the terminal, which is usually:

```text
http://localhost:8501
```

## How to Host the Website Online

The deployed website is available at [https://data-science-asg.streamlit.app/](https://data-science-asg.streamlit.app/).

This project is best suited for Streamlit Community Cloud because the application is already built with Streamlit.

### Option: Streamlit Community Cloud

### 1. Prepare the project

Before deployment, make sure the project includes:

- `streamlit_app.py` (recommended deployment entry point)
- `app/streamlit_app.py` (application implementation)
- `requirements.txt`
- the `models/` folder with the trained model files
- the required data or generated assets used by the app

### 2. Upload the project to a Git repository

Push the full project to a Git hosting service such as GitHub.

### 3. Deploy on Streamlit Community Cloud

- Sign in to Streamlit Community Cloud
- Choose to create a new app from your repository
- Select the repository and branch
- Set the main file path to `streamlit_app.py`
- Start the deployment

### 4. Verify the deployment

After deployment finishes:

- open the hosted app URL
- test several input combinations
- confirm the model loads correctly and returns predictions

### Important deployment notes

- The hosted environment must install all packages listed in `requirements.txt`
- The `models/best_model.pkl` file must be present in the deployed project
- The app expects the project folder structure to remain consistent because paths are resolved relative to the project root

## Notes About Predictions, Assumptions, and Limitations

### Predictions

- The app predicts hourly rented bike demand, not exact real-world inventory needs at each station
- The displayed estimate is a model-based forecast derived from historical patterns in the dataset
- The app also shows simple supply buffer scenarios based on the predicted value

### Assumptions

- Historical demand patterns are informative for future planning scenarios
- The selected input variables capture enough of the key drivers of bike demand for a prototype tool
- A Random Forest Regressor is used as the selected model because it achieved the lowest test RMSE among the trained models in this project
- Negative predictions are clipped to zero before display because rental demand cannot be negative

### Limitations

- The app is a prototype for planning support and should not be treated as a fully operational dispatch system
- Predictions are based on the Seoul bike dataset only and may not generalize to other cities or operating conditions
- The model does not directly account for real-time station-level inventory, maintenance events, traffic disruptions, or sudden local events
- Results depend on the quality and representativeness of the historical dataset
- The train-test split is random rather than time-ordered, so evaluation may be more optimistic than a stricter future-forecast deployment setting
- User-entered scenarios outside the normal historical distribution may produce less reliable estimates
