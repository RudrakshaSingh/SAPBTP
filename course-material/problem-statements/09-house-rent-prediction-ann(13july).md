# Problem Statement 9 — House Rent Prediction Using Artificial Neural Network

| | |
|---|---|
| **Project Title** | House Rent Prediction Using Artificial Neural Network |
| **Domain** | Real Estate Analytics |
| **Topic** | Deep Learning — ANN Regression (TensorFlow / Keras) |
| **Deliverable** | Google Colab notebook + ANN model + training charts + prediction |

---

## 1. Business Scenario

You are working as a junior deep learning engineer for a real-estate analytics company. The company wants to help tenants and property owners estimate the expected monthly rent of a house or flat based on property details.

Currently, rent estimation is done manually by brokers using experience and local knowledge, which is often inconsistent. The company wants an **Artificial Neural Network regression model** that predicts monthly house rent using historical rental data.

## 2. Machine Learning Problem

Build a supervised deep learning **regression** model using ANN to predict **Monthly Rent**. Since rent is a continuous numerical value, this is a regression problem.

## 3. Target Variable

`Monthly_Rent` — examples: 12000, 18000, 25000, 42000. The model should predict a numeric rent value.

## 4. Dataset Description

| Column Name | Description | Type |
|---|---|---|
| `Property_ID` | Unique property ID | Categorical |
| `City` | City where property is located | Categorical |
| `Area_Locality` | Locality or area name | Categorical |
| `Property_Type` | Apartment, Independent House, Villa | Categorical |
| `BHK` | Number of bedrooms | Numerical |
| `Size_sqft` | Total property size in square feet | Numerical |
| `Bathroom_Count` | Number of bathrooms | Numerical |
| `Furnishing_Status` | Furnished, Semi-Furnished, Unfurnished | Categorical |
| `Floor_Number` | Floor on which property is located | Numerical |
| `Total_Floors` | Total floors in building | Numerical |
| `Parking_Available` | Yes or No | Categorical |
| `Distance_to_Metro_km` | Distance from metro/major transport | Numerical |
| `Property_Age_Years` | Age of property | Numerical |
| `Monthly_Rent` | **Target variable** | Numerical |

## 5. Sample Data

| City | Property_Type | BHK | Size_sqft | Furnishing_Status | Parking_Available | Distance_to_Metro_km | Property_Age_Years | Monthly_Rent |
|---|---|---|---|---|---|---|---|---|
| Bangalore | Apartment | 2 | 950 | Semi-Furnished | Yes | 1.2 | 5 | 28000 |
| Pune | Apartment | 1 | 600 | Unfurnished | No | 3.5 | 8 | 14000 |
| Mumbai | Apartment | 2 | 850 | Furnished | Yes | 0.8 | 4 | 52000 |
| Delhi | Independent House | 3 | 1500 | Semi-Furnished | Yes | 2.1 | 10 | 45000 |
| Hyderabad | Villa | 4 | 2400 | Furnished | Yes | 4.0 | 3 | 75000 |

## 6. Project Objective

Build an end-to-end ANN regression model that predicts monthly rent based on property characteristics. By the end, you should be able to:

- Understand regression using ANN
- Identify input features and target variable
- Handle numerical and categorical features
- Perform exploratory data analysis
- Handle missing values
- Apply scaling and one-hot encoding
- Build an ANN regression model
- Train the model using TensorFlow/Keras
- Evaluate using MAE, RMSE, and R² Score
- Reduce overfitting using Dropout and EarlyStopping
- Save the trained model
- Predict rent for a new property

---

## 7. Hands-on Tasks

### Task 1: Load or Create Dataset

Create or load a house rent dataset. **Minimum dataset size: 3000 to 5000 records.**

Check: number of rows, number of columns, column names, data types, first five records, missing values.

### Task 2: Understand the Problem

Answer:

1. What is the target variable?
2. Is this regression or classification?
3. Why is rent prediction a regression problem?
4. Which columns are numerical?
5. Which columns are categorical?

### Task 3: Exploratory Data Analysis

Analyze:

- Monthly rent distribution
- Rent by city
- Rent by BHK
- Rent by property type
- Size vs rent relationship
- Furnishing status vs rent
- Distance to metro vs rent
- Correlation between numerical columns and rent

*Example questions:* Does rent increase with property size? Which city has higher average rent? Does furnished property have higher rent? Does distance from metro affect rent?

### Task 4: Handle Missing Values

| Column Type | Missing Value Treatment |
|---|---|
| Numerical columns | Median imputation |
| Categorical columns | Most frequent, or `Unknown` |

*Examples:* `Size_sqft` missing → fill with median size. `Furnishing_Status` missing → fill with most frequent category.

### Task 5: Data Preprocessing

ANN needs numerical input, so preprocessing is essential.

| Column Type | Preprocessing |
|---|---|
| Numerical columns | `SimpleImputer` + `StandardScaler` |
| Categorical columns | `SimpleImputer` + `OneHotEncoder` |

Use `ColumnTransformer`, `Pipeline`, `SimpleImputer`, `StandardScaler`, `OneHotEncoder`.

### Task 6: Train-Test Split

Split 80% training / 20% testing.

### Task 7: Build Baseline Model

Before ANN, build a simple baseline using `DummyRegressor` — it predicts the average rent for all properties. The ANN should perform better than this.

---

## 8. ANN Model Building

### Suggested Architecture

```
Input Layer
   ↓
Dense Layer with 128 neurons + ReLU
   ↓
Dropout Layer
   ↓
Dense Layer with 64 neurons + ReLU
   ↓
Dropout Layer
   ↓
Dense Layer with 32 neurons + ReLU
   ↓
Output Layer with 1 neuron
```

**Why does the output layer have 1 neuron?**
Because this is a regression problem — the model predicts one continuous value (Predicted Monthly Rent). For regression the final layer is `Dense(1)`; no sigmoid or softmax is needed.

### Suggested Code Structure

```python
model = Sequential([
    Input(shape=(input_dim,)),
    Dense(128, activation="relu"),
    Dropout(0.3),
    Dense(64, activation="relu"),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(1)
])
```

### Compile the Model

```python
model.compile(
    optimizer="adam",
    loss="mse",
    metrics=["mae"]
)
```

| Component | Meaning |
|---|---|
| `adam` | Optimizer that updates weights |
| `mse` | Mean Squared Error loss for regression |
| `mae` | Mean Absolute Error metric |

---

## 9. Model Training

```python
history = model.fit(
    X_train_processed,
    y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=[early_stop]
)
```

Observe: training loss, validation loss, training MAE, validation MAE.

---

## 10. Model Evaluation

| Metric | Meaning |
|---|---|
| MAE | Average rent prediction error |
| RMSE | Penalizes large rent prediction errors |
| R² Score | Explains how well the model captures rent variation |

*Example:* `MAE = 2500` → on average the model is making a rent prediction error of ₹2,500.

### Expected Evaluation Table

| Model | MAE | RMSE | R² Score |
|---|---|---|---|
| Dummy Regressor | 15000 | 19000 | 0.00 |
| Linear Regression | 6000 | 8500 | 0.68 |
| Random Forest Regressor | 3800 | 5700 | 0.84 |
| ANN Regressor | 3200 | 5000 | 0.88 |

---

## 11. Overfitting Control

**Dropout** — randomly switches off some neurons during training to reduce overfitting.

**EarlyStopping** — stops training when validation loss stops improving, avoiding unnecessary training and preventing memorization.

```python
early_stop = EarlyStopping(
    monitor="val_loss",
    patience=10,
    restore_best_weights=True
)
```

---

## 12. Prediction for New Property

| Feature | Value |
|---|---|
| City | Bangalore |
| Area_Locality | Whitefield |
| Property_Type | Apartment |
| BHK | 2 |
| Size_sqft | 1050 |
| Bathroom_Count | 2 |
| Furnishing_Status | Semi-Furnished |
| Floor_Number | 5 |
| Total_Floors | 12 |
| Parking_Available | Yes |
| Distance_to_Metro_km | 1.5 |
| Property_Age_Years | 4 |

**Expected output:** Predicted Monthly Rent ≈ ₹32,000

---

## 13. Final Deliverables

1. Google Colab notebook
2. Dataset or synthetic dataset generation code
3. EDA charts
4. Preprocessing pipeline
5. Baseline model result
6. ANN model architecture
7. Training vs validation loss chart
8. Training vs validation MAE chart
9. MAE, RMSE, and R² Score
10. Final prediction for new property
11. Short business interpretation

## 14. Success Criteria

- Clearly define the regression problem
- Correctly identify features and target
- Handle missing values
- Encode categorical variables
- Scale numerical variables
- Build ANN with proper architecture
- Use MSE loss for regression
- Evaluate using MAE, RMSE, and R² Score
- Beat the baseline model
- Use Dropout or EarlyStopping
- Predict rent for a new property

## 15. Student Discussion Questions

1. Why is house rent prediction a regression problem?
2. Why does ANN need numerical input?
3. Why do we scale numerical columns before ANN?
4. Why do we use `Dense(1)` in the output layer?
5. Why do we not use sigmoid in regression output?
6. What is the role of MSE loss?
7. What does MAE mean in rent prediction?
8. What does RMSE tell us?
9. What does R² Score explain?
10. How does Dropout reduce overfitting?
11. What is EarlyStopping?
12. How can this model help a real-estate company?

---

## Final One-line Problem Statement

> Build an Artificial Neural Network regression model that predicts monthly house rent using property size, city, BHK, furnishing status, property type, floor details, parking availability, distance to metro, and property age.
