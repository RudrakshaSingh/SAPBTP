# Problem Statement 7 — Employee Salary Prediction Using ML Regression

| | |
|---|---|
| **Project Title** | Employee Salary Prediction Using Machine Learning Regression |
| **Domain** | HR Analytics |
| **Topic** | Supervised Learning — Regression |
| **Deliverable** | Google Colab notebook + model comparison + final model |

---

## 1. Business Scenario

You are working as a junior machine learning engineer for an HR analytics company. The company helps organizations estimate employee salaries based on professional details such as years of experience, education level, job role, city, skill score, certification count, and previous company rating.

Currently, salary estimation is done manually by HR teams. This process is slow, inconsistent, and sometimes biased. The company wants to build a **machine learning regression model** that predicts the expected salary of an employee using historical employee data.

## 2. Machine Learning Problem

Build a supervised learning **regression** model that predicts employee salary.

**Target Variable:** `Salary` — a continuous numeric value, hence a regression problem.

## 3. Dataset Description

| Column Name | Description | Data Type |
|---|---|---|
| `Employee_ID` | Unique employee ID | Categorical |
| `Age` | Age of employee | Numeric |
| `Years_Experience` | Total years of work experience | Numeric |
| `Education_Level` | Bachelor, Master, PhD | Categorical |
| `Job_Role` | Analyst, Developer, Manager, Data Scientist, Consultant | Categorical |
| `City` | Bangalore, Hyderabad, Pune, Delhi, Mumbai | Categorical |
| `Skill_Score` | Technical skill score out of 100 | Numeric |
| `Certifications` | Number of certifications completed | Numeric |
| `Previous_Company_Rating` | Rating of previous company from 1 to 5 | Numeric |
| `Salary` | Annual salary in INR | **Numeric — Target** |

## 4. Sample Data

| Age | Years_Experience | Education_Level | Job_Role | City | Skill_Score | Certifications | Previous_Company_Rating | Salary |
|---|---|---|---|---|---|---|---|---|
| 24 | 1 | Bachelor | Analyst | Pune | 65 | 1 | 3.5 | 450000 |
| 28 | 4 | Master | Developer | Bangalore | 78 | 2 | 4.0 | 850000 |
| 32 | 7 | Master | Data Scientist | Hyderabad | 88 | 4 | 4.2 | 1450000 |
| 38 | 12 | PhD | Manager | Mumbai | 82 | 5 | 4.5 | 2200000 |
| 26 | 3 | Bachelor | Consultant | Delhi | 72 | 2 | 3.8 | 700000 |

## 5. Project Objective

Build an end-to-end regression model that predicts employee salary based on profile and career-related features. By the end, you should be able to:

- Understand regression problem statements
- Load and explore data
- Identify input features and target variable
- Handle categorical and numerical columns
- Apply preprocessing using pipelines
- Train regression models
- Evaluate model performance
- Compare multiple models
- Tune model hyperparameters
- Save and reuse the final model

---

## 6. Hands-on Tasks

### Task 1: Load the Dataset

Load the employee salary dataset into a pandas DataFrame. Check: number of rows, number of columns, first five records, column names, data types.

### Task 2: Understand the Problem

Answer:

1. What is the target variable?
2. Is this classification or regression?
3. Why is salary prediction a regression problem?
4. Which columns are numerical?
5. Which columns are categorical?

### Task 3: Exploratory Data Analysis

Analyze:

- Salary distribution
- Experience vs salary relationship
- Education level vs salary
- Job role vs salary
- City-wise salary pattern
- Correlation between numeric features and salary
- Missing values
- Outliers in salary

### Task 4: Data Preprocessing

| Column Type | Technique |
|---|---|
| Numeric columns | `StandardScaler` |
| Categorical columns | `OneHotEncoder` |
| Target column | Keep as numeric |

Create a preprocessing pipeline using `ColumnTransformer`, `Pipeline`, `StandardScaler`, `OneHotEncoder`.

### Task 5: Train-Test Split

Split 80% training / 20% testing. The model should learn from training data and be evaluated on unseen testing data.

### Task 6: Build Baseline Model

Create a baseline using `DummyRegressor` — it predicts the average salary for every employee. Any real ML model should perform better than this baseline.

### Task 7: Train Regression Models

Train at least four regression models:

| Model | Purpose |
|---|---|
| Linear Regression | Simple baseline ML model |
| Ridge Regression | Handles overfitting using L2 regularization |
| Lasso Regression | Handles overfitting and feature selection using L1 regularization |
| Random Forest Regressor | Advanced tree-based model |

### Task 8: Evaluate Model Performance

| Metric | Meaning |
|---|---|
| MAE | Average salary prediction error |
| RMSE | Penalizes large salary prediction errors |
| R² Score | Shows how well the model explains salary variation |

*Example interpretation:* `MAE = 75000` → on average the model is making a salary prediction error of ₹75,000.

### Task 9: Compare Models

Create a model comparison table (illustrative expected values):

| Model | MAE | RMSE | R² Score |
|---|---|---|---|
| Dummy Regressor | 350000 | 420000 | 0.00 |
| Linear Regression | 120000 | 160000 | 0.72 |
| Ridge Regression | 115000 | 150000 | 0.75 |
| Lasso Regression | 118000 | 155000 | 0.73 |
| Random Forest Regressor | 85000 | 120000 | 0.86 |

Identify: which model has the lowest MAE, lowest RMSE, highest R², and which should be the final model.

### Task 10: Hyperparameter Tuning

Tune the Random Forest Regressor:

| Hyperparameter | Values |
|---|---|
| `n_estimators` | 50, 100, 200 |
| `max_depth` | 5, 10, 15 |
| `min_samples_split` | 2, 5, 10 |

Use `GridSearchCV` with cross-validation and R² scoring to find the best combination.

### Task 11: Feature Importance

Find the most important features affecting salary prediction. Expected important features: `Years_Experience`, `Skill_Score`, `Job_Role`, `Education_Level`, `Certifications`, `City`.

Explain which features are most important and why.

### Task 12: Make New Prediction

Predict salary for a new employee:

| Feature | Value |
|---|---|
| Age | 30 |
| Years_Experience | 6 |
| Education_Level | Master |
| Job_Role | Data Scientist |
| City | Bangalore |
| Skill_Score | 85 |
| Certifications | 3 |
| Previous_Company_Rating | 4.2 |

**Expected output:** Predicted Salary ≈ ₹13,50,000

---

## 7. Final Deliverables

1. Google Colab notebook
2. Cleaned dataset
3. EDA charts
4. Trained regression models
5. Model comparison table
6. Final selected model
7. Feature importance analysis
8. New salary prediction example
9. Short project summary

## 8. Success Criteria

- Clear regression problem definition
- Proper preprocessing
- Multiple regression models compared
- Evaluated using MAE, RMSE, and R² Score
- Beats the Dummy Regressor baseline
- Uses cross-validation or hyperparameter tuning
- Final model explained in business terms

## 9. Student Discussion Questions

1. Why is salary prediction a regression problem?
2. Why do we need train-test split?
3. Why do we encode categorical variables?
4. Why do we scale numerical variables?
5. Which model performed best and why?
6. What does MAE mean in salary prediction?
7. Why can Random Forest perform better than Linear Regression?
8. What is overfitting in this project?
9. How do Ridge and Lasso help reduce overfitting?
10. How can this model be used by HR teams?

## 10. Extension Task

Improve the project by adding:

- Experience category: Fresher, Junior, Mid-level, Senior
- Remote work option
- Company size
- Industry type
- Location cost index
- Model deployment using Streamlit

---

## Final One-line Problem Statement

> Build a supervised machine learning regression model that predicts employee salary using experience, education, job role, city, skill score, certifications, and company rating, then evaluate and improve the model using regression metrics and hyperparameter tuning.
