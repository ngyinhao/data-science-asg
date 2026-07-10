# Seoul Bike Sharing Demand Glossary

## ADR

Architecture Decision Record. A short document that captures an important project decision, the context behind it, and its consequences.

## Baseline Model

A simple model used as the starting comparison point. For this project, Multiple Linear Regression is a good baseline because the target is numeric and the model is easy to explain.

## Bike Supply Planning

The recommended project frame. It treats the prediction as an operations planning problem: estimate how many bikes may be rented in a given hour so operators can prepare enough bikes.

## CRISP-DM

Cross Industry Standard Process for Data Mining. The assignment expects the project to follow this workflow: business understanding, data understanding, data preparation, modelling, evaluation, and deployment.

## MAE

Mean Absolute Error. The average absolute difference between predicted bike rentals and actual bike rentals.

## RMSE

Root Mean Squared Error. Similar to MAE, but larger errors are penalised more strongly.

## R2

R-squared. A regression score that explains how much variation in the target is explained by the model.

## Regression

A prediction task where the target value is numeric. In this project, the target is the hourly rented bike count.

## Rented Bike Count

The number of public bikes rented during a specific hour. This is the target variable to predict.

## Project Frame

The main business story of the project. It decides the objective, model justification, evaluation discussion, prototype design, and conclusion.

## Streamlit Prototype

A simple interactive Python web app. For this assignment, it can let a user enter conditions such as hour, season, temperature, humidity, rainfall, and holiday status, then show the predicted demand.
