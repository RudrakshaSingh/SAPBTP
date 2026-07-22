# Problem Statement 8 — Loan Default Risk Prediction Using ML Classification

| | |
|---|---|
| **Project Title** | Loan Default Risk Prediction Using Machine Learning Classification |
| **Domain** | Fintech / Lending |
| **Topic** | Supervised Learning — Binary Classification |
| **Deliverable** | Google Colab notebook + confusion matrix + model comparison + final model |

---

## 1. Business Scenario

You are working as a junior machine learning engineer for a fintech company. The company gives personal loans to customers. Before approving a loan, the risk team wants to know whether a customer is likely to **default or not default**.

Currently, loan approval is done manually using basic rules like income, credit score, employment type, and existing loan amount. This process is slow and sometimes inaccurate. The company wants a **classification model** that predicts whether a customer is risky or safe.

## 2. Machine Learning Problem

Build a supervised machine learning classification model to predict:

> Will the customer default on the loan?

## 3. Target Variable

`Loan_Default`

| Value | Meaning |
|---|---|
| `0` | Customer will not default |
| `1` | Customer may default |

Since the output is either 0 or 1, this is a **binary classification** problem.

## 4. Dataset Description

| Column Name | Description | Type |
|---|---|---|
| `Customer_ID` | Unique customer ID | Categorical |
| `Age` | Customer age | Numerical |
| `Monthly_Income` | Monthly income of customer | Numerical |
| `Credit_Score` | Credit score of customer | Numerical |
| `Loan_Amount` | Requested loan amount | Numerical |
| `Loan_Tenure_Months` | Loan repayment period | Numerical |
| `Existing_EMI` | Existing monthly EMI | Numerical |
| `Employment_Type` | Salaried, Self-employed, Business, Unemployed | Categorical |
| `Education_Level` | Graduate, Postgraduate, Diploma, School | Categorical |
| `Marital_Status` | Single, Married | Categorical |
| `Dependents` | Number of dependents | Numerical |
| `Previous_Default` | Whether customer defaulted earlier | Categorical |
| `Loan_Default` | **Target variable — 0 or 1** | |

## 5. Sample Data

| Age | Monthly_Income | Credit_Score | Loan_Amount | Employment_Type | Previous_Default | Loan_Default |
|---|---|---|---|---|---|---|
| 25 | 35000 | 720 | 300000 | Salaried | No | 0 |
| 42 | 60000 | 580 | 900000 | Business | Yes | 1 |
| 31 | 45000 | 690 | 500000 | Self-employed | No | 0 |
| 38 | 30000 | 550 | 700000 | Salaried | Yes | 1 |
| 29 | 75000 | 760 | 400000 | Salaried | No | 0 |

## 6. Project Objective

Build an end-to-end classification model that identifies customers who may default on a loan. By the end, you should be able to:

- Understand classification problem statements
- Identify input features and target variable
- Perform exploratory data analysis
- Handle numerical and categorical data
- Handle missing values
- Encode categorical columns
- Scale numerical columns
- Train classification models
- Evaluate using classification metrics
- Compare multiple models
- Tune hyperparameters
- Make predictions for new customers

---

## 7. Hands-on Tasks

### Task 1: Load the Dataset

Load the loan customer dataset into pandas. Check: number of rows, number of columns, first 5 records, column names, data types, missing values.

### Task 2: Understand the Problem

Answer:

1. What is the target variable?
2. Is this regression or classification?
3. Why is loan default prediction a classification problem?
4. Which columns are numerical?
5. Which columns are categorical?

### Task 3: Exploratory Data Analysis

Understand:

- Distribution of loan default values
- Credit score distribution
- Income vs loan default
- Loan amount vs loan default
- Previous default vs current default
- Employment type vs default
- Correlation between numerical columns

### Task 4: Handle Missing Values

| Column Type | Suggested Method |
|---|---|
| Numerical columns | Median imputation |
| Categorical columns | Most frequent, or `Unknown` |

*Examples:* Age missing → fill with median age. Employment_Type missing → fill with most frequent category.

### Task 5: Data Preprocessing

| Column Type | Preprocessing |
|---|---|
| Numerical columns | `SimpleImputer` + `StandardScaler` |
| Categorical columns | `SimpleImputer` + `OneHotEncoder` |

Use `ColumnTransformer`, `Pipeline`, `SimpleImputer`, `StandardScaler`, `OneHotEncoder`.

### Task 6: Train-Test Split

Split 80% training / 20% testing. Use **stratification** because the target class may be imbalanced.

```python
train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### Task 7: Build Baseline Model

Create a baseline model using `DummyClassifier` as a simple benchmark. Any real ML model should perform better than this.

### Task 8: Train Classification Models

| Model | Purpose |
|---|---|
| Logistic Regression | Simple classification model |
| Decision Tree Classifier | Rule-based tree model |
| Random Forest Classifier | Advanced ensemble model |
| Gradient Boosting Classifier | Strong boosting-based model |

### Task 9: Evaluate the Models

| Metric | Meaning |
|---|---|
| Accuracy | Overall correct predictions |
| Precision | Out of predicted defaulters, how many actually defaulted |
| Recall | Out of actual defaulters, how many the model caught |
| F1-score | Balance between precision and recall |
| ROC-AUC | Ability to separate risky and safe customers |

### Task 10: Confusion Matrix

| Actual / Predicted | Predicted Safe | Predicted Default |
|---|---|---|
| **Actual Safe** | True Negative | False Positive |
| **Actual Default** | False Negative | True Positive |

Explain:

- **False Negative** is dangerous — a risky customer is predicted as safe.
- **False Positive** — a safe customer is wrongly marked risky.

### Task 11: Model Comparison

Create a table (illustrative expected values):

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|---|---|---|---|---|
| Dummy Classifier | 0.70 | 0.00 | 0.00 | 0.00 | 0.50 |
| Logistic Regression | 0.81 | 0.72 | 0.65 | 0.68 | 0.84 |
| Decision Tree | 0.78 | 0.66 | 0.70 | 0.68 | 0.76 |
| Random Forest | 0.86 | 0.80 | 0.75 | 0.77 | 0.89 |
| Gradient Boosting | 0.87 | 0.82 | 0.76 | 0.79 | 0.91 |

Decide: which model has the best recall, best precision, best ROC-AUC, and which should be selected for business use.

### Task 12: Hyperparameter Tuning

Tune the Random Forest Classifier:

| Hyperparameter | Values |
|---|---|
| `n_estimators` | 50, 100, 200 |
| `max_depth` | 5, 10, 15 |
| `min_samples_split` | 2, 5, 10 |
| `class_weight` | None, balanced |

Use `GridSearchCV` with cross-validation and **ROC-AUC scoring**.

### Task 13: Feature Importance

Find the most important features. Expected: `Credit_Score`, `Monthly_Income`, `Loan_Amount`, `Existing_EMI`, `Previous_Default`, `Employment_Type`, `Loan_Tenure_Months`.

Explain which factors increase the chance of loan default.

### Task 14: New Customer Prediction

| Feature | Value |
|---|---|
| Age | 35 |
| Monthly_Income | 40000 |
| Credit_Score | 590 |
| Loan_Amount | 800000 |
| Loan_Tenure_Months | 48 |
| Existing_EMI | 12000 |
| Employment_Type | Self-employed |
| Education_Level | Graduate |
| Marital_Status | Married |
| Dependents | 2 |
| Previous_Default | Yes |

**Expected output:** `Prediction: Loan Default Risk = High`, `Class: 1`

---

## 8. Final Deliverables

1. Google Colab notebook
2. Dataset or generated dataset
3. EDA charts
4. Preprocessing pipeline
5. Trained classification models
6. Confusion matrix
7. Classification report
8. Model comparison table
9. Final selected model
10. New customer prediction example

## 9. Success Criteria

- Correctly define the classification problem
- Handle missing values properly
- Encode categorical variables
- Scale numerical variables
- Train multiple classification models
- Beat the Dummy Classifier baseline
- Use accuracy, precision, recall, F1-score, and ROC-AUC
- Explain false positives and false negatives
- Select the final model based on business need

## 10. Business Interpretation

For this problem, **recall is very important** — missing a risky customer is dangerous.

- **False Negative** = actual defaulter predicted as safe → financial loss to the company.
- **False Positive** = safe customer wrongly predicted as risky → rejects good customers and reduces business.

So the final model should balance: **high recall + good precision + strong ROC-AUC**.

---

## Final One-line Problem Statement

> Build a supervised machine learning classification model that predicts whether a loan applicant is likely to default using income, credit score, loan amount, EMI, employment type, and previous default history.
