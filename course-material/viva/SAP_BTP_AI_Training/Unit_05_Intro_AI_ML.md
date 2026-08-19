# 🧠 Unit 5 — Introduction to AI & ML

> **Module**: Module 3 — AI / ML  
> **Duration**: Day 10–11 (16 hours)  
> **Dates**: 10-Jul-2026, 13-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — What is Artificial Intelligence?

### Q1. What is Artificial Intelligence (AI)?

**A:** **Artificial Intelligence** is the simulation of human intelligence by machines. AI systems can perceive, reason, learn, and make decisions — tasks that traditionally required human cognition.

**Types of AI by capability:**

| Type | Description | Example | Exists Today? |
|------|-------------|---------|---------------|
| **Narrow AI (ANI)** | Excels at one specific task | ChatGPT, Siri, Chess engine, Image recognition | ✅ Yes |
| **General AI (AGI)** | Human-level intelligence across any task | A machine that can do ANY intellectual task a human can | ❌ Not yet |
| **Super AI (ASI)** | Surpasses human intelligence in every way | Hypothetical superintelligent system | ❌ Theoretical |

**All current AI is Narrow AI** — impressive at specific tasks but cannot generalize to unrelated ones. A chess AI can't write poetry; a language model can't drive a car.

---

### Q2. What is the difference between AI, ML, Deep Learning, and Data Science?

**A:**

```
AI (broadest)
 └── Machine Learning (subset of AI)
      └── Deep Learning (subset of ML)

Data Science (overlapping field — uses AI/ML as tools)
```

| Field | Definition | Focus |
|-------|-----------|-------|
| **AI** | Machines simulating human intelligence | Making machines "smart" |
| **ML** | AI that learns from data without explicit programming | Pattern recognition from data |
| **Deep Learning** | ML using neural networks with many layers | Complex pattern recognition (images, language) |
| **Data Science** | Extracting insights from data | Analysis, visualization, storytelling |

**Relationship example:**
- **AI:** "Build a system that understands human language."
- **ML:** "Train a model on text data to predict the next word."
- **Deep Learning:** "Use a transformer neural network with attention mechanisms."
- **Data Science:** "Analyze which topics users ask about most and visualize trends."

---

### Q3. What are the main branches/subfields of AI?

**A:**

| Branch | What It Does | Example |
|--------|-------------|---------|
| **Machine Learning** | Learn patterns from data | Spam detection, recommendation systems |
| **Natural Language Processing (NLP)** | Understand and generate human language | ChatGPT, Google Translate, sentiment analysis |
| **Computer Vision** | Interpret visual information (images, video) | Face recognition, self-driving cars, medical imaging |
| **Robotics** | Physical machines that sense and act | Factory robots, surgical robots |
| **Expert Systems** | Rule-based decision systems | Medical diagnosis, tax preparation software |
| **Speech Recognition** | Convert speech to text and vice versa | Siri, Alexa, Google Assistant |
| **Generative AI** | Create new content (text, images, code, music) | ChatGPT, DALL-E, Midjourney, GitHub Copilot |

---

### Q4. What is the history/evolution of AI?

**A:**

| Era | Period | Key Events |
|-----|--------|------------|
| **Birth of AI** | 1950s | Turing Test (1950), "AI" coined at Dartmouth Conference (1956) |
| **Early enthusiasm** | 1960s–70s | Expert systems, ELIZA chatbot, perceptrons |
| **AI Winter 1** | 1974–80 | Hype didn't deliver; funding dried up |
| **Expert Systems boom** | 1980s | Rule-based systems in industry; Japan's 5th Gen project |
| **AI Winter 2** | 1987–93 | Expert systems too brittle; funding cut again |
| **ML Renaissance** | 1997–2010 | Deep Blue beats chess champion (1997), SVMs, random forests |
| **Deep Learning era** | 2012+ | AlexNet wins ImageNet (2012), GPUs enable neural networks |
| **Transformer revolution** | 2017+ | "Attention Is All You Need" paper; BERT, GPT series |
| **GenAI explosion** | 2022+ | ChatGPT (Nov 2022), DALL-E, Gemini, LLMs go mainstream |

---

## 🔹 Section 2 — Machine Learning Fundamentals

### Q5. What is Machine Learning? How is it different from traditional programming?

**A:**

| Aspect | Traditional Programming | Machine Learning |
|--------|------------------------|------------------|
| **Input** | Rules + Data | Data + Expected Output |
| **Output** | Answers | Rules (model) |
| **Approach** | Programmer writes explicit rules | Algorithm discovers rules from data |
| **Example** | `if email.contains("free money") → spam` | Model learns spam patterns from 10,000 labeled emails |
| **Adaptability** | Manual rule updates | Model improves with more data |

```
Traditional: Input + Rules → Output
ML:          Input + Output → Rules (Model)
```

**Key insight:** In ML, you don't tell the computer HOW to solve the problem. You show it examples and let it figure out the patterns.

---

### Q6. What are the types of Machine Learning?

**A:**

| Type | How It Learns | Data Needed | Example |
|------|--------------|-------------|---------|
| **Supervised Learning** | From labeled data (input → known output) | Labeled dataset | Email spam detection, house price prediction |
| **Unsupervised Learning** | From unlabeled data (find hidden patterns) | Unlabeled dataset | Customer segmentation, anomaly detection |
| **Semi-supervised Learning** | From a mix of labeled + unlabeled data | Mostly unlabeled + some labeled | Medical image classification (few labeled scans) |
| **Reinforcement Learning** | From rewards/penalties for actions | Environment + reward signal | Game AI (AlphaGo), robotics, self-driving cars |

---

### Q7. What is supervised learning? Explain with examples.

**A:** **Supervised learning** trains a model on **labeled data** — each training example has an input and a known correct output.

**Two main types:**

| Type | Output | Example | Algorithms |
|------|--------|---------|------------|
| **Classification** | Discrete categories | Is this email spam or not? (Yes/No) | Logistic Regression, Decision Trees, SVM, Neural Networks |
| **Regression** | Continuous numbers | What will this house sell for? ($350,000) | Linear Regression, Polynomial Regression, Random Forest |

**Process:**
```
1. Collect labeled data:     [Features] → [Label]
                             [3 beds, 2000 sqft, Mumbai] → ₹85 lakhs
                             [2 beds, 1200 sqft, Delhi]  → ₹60 lakhs

2. Train model:              Model learns: more beds + more sqft → higher price

3. Predict on new data:      [4 beds, 2500 sqft, Mumbai] → Model predicts ₹1.1 Cr
```

---

### Q8. What is unsupervised learning? Explain with examples.

**A:** **Unsupervised learning** finds patterns in **unlabeled data** — no known correct answers.

**Main types:**

| Type | What It Does | Example | Algorithms |
|------|-------------|---------|------------|
| **Clustering** | Group similar data points | Customer segments (high spenders vs budget shoppers) | K-Means, DBSCAN, Hierarchical |
| **Dimensionality Reduction** | Reduce features while preserving information | Compress 100 features to 10 for visualization | PCA, t-SNE, UMAP |
| **Association** | Find rules/relationships in data | "People who buy bread also buy butter" | Apriori, FP-Growth |
| **Anomaly Detection** | Find outliers that don't fit the pattern | Fraud detection, network intrusion | Isolation Forest, One-Class SVM |

**Clustering example:**
```
Customer data (no labels):
  Customer A: spends ₹50K/month, buys electronics
  Customer B: spends ₹5K/month, buys groceries
  Customer C: spends ₹45K/month, buys electronics

K-Means output:
  Cluster 1 (High-value tech): Customer A, Customer C
  Cluster 2 (Budget grocery):  Customer B
```

---

### Q9. What is reinforcement learning?

**A:** **Reinforcement learning (RL)** is where an **agent** learns by interacting with an **environment**, receiving **rewards** for good actions and **penalties** for bad ones.

**Key concepts:**

| Term | Meaning | Game Example |
|------|---------|-------------|
| **Agent** | The learner/decision-maker | The game player |
| **Environment** | The world the agent interacts with | The game board |
| **State** | Current situation | Board position |
| **Action** | What the agent can do | Move a piece |
| **Reward** | Feedback for an action | +1 for winning, -1 for losing |
| **Policy** | Strategy the agent follows | "When in state X, do action Y" |

**Real-world RL examples:**
- **AlphaGo** — Learned to play Go by playing millions of games against itself.
- **Self-driving cars** — Learn to navigate by driving in simulated environments.
- **Recommendation systems** — Learn which content keeps users engaged.
- **Robotics** — Robots learn to walk, grasp objects through trial and error.

---

## 🔹 Section 3 — ML Workflow & Key Concepts

### Q10. Explain the end-to-end ML workflow.

**A:**

```
1. Problem Definition     → "What business problem are we solving?"
        ↓
2. Data Collection        → Gather relevant data (databases, APIs, files)
        ↓
3. Data Preprocessing     → Clean, transform, handle missing values
        ↓
4. Exploratory Data       → Understand patterns, distributions, correlations
   Analysis (EDA)
        ↓
5. Feature Engineering    → Create/select relevant features
        ↓
6. Model Selection        → Choose algorithm(s) to try
        ↓
7. Model Training         → Feed data to algorithm; model learns patterns
        ↓
8. Model Evaluation       → Test model on unseen data; measure accuracy
        ↓
9. Hyperparameter Tuning  → Optimize model settings for best performance
        ↓
10. Deployment            → Put model into production (API, app, pipeline)
        ↓
11. Monitoring            → Track model performance over time; retrain as needed
```

---

### Q11. What is a feature? What is feature engineering?

**A:** A **feature** is an individual measurable property or characteristic of the data used as input to a model.

```
House Price Prediction:
  Features: [bedrooms, square_feet, location, age, has_garage]
  Target:   price
```

**Feature engineering** = Creating new, more informative features from existing data.

| Technique | Example |
|-----------|---------|
| **Derived features** | `age = current_year - birth_year` |
| **Binning** | Convert age → "child", "adult", "senior" |
| **One-hot encoding** | Convert "city: Mumbai" → `city_Mumbai=1, city_Delhi=0` |
| **Scaling** | Normalize salary from [30K-200K] to [0-1] |
| **Log transform** | Transform skewed distributions |
| **Interaction features** | `price_per_sqft = price / sqft` |
| **Text features** | TF-IDF, word count, sentiment score |
| **Date features** | Extract day_of_week, is_weekend, month from datetime |

**"Feature engineering is the most important skill in ML"** — better features often matter more than a better algorithm.

---

### Q12. What is the train/test split? Why do we need it?

**A:** We split data into **training set** (to learn) and **test set** (to evaluate). This prevents the model from being evaluated on data it has already seen.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
# 80% training, 20% testing
```

**Common splits:**

| Split | Training | Validation | Test |
|-------|----------|------------|------|
| **Simple** | 80% | — | 20% |
| **Three-way** | 70% | 15% | 15% |
| **K-Fold CV** | (K-1)/K | 1/K | Separate test set |

**Why we need it:**
- A model that memorizes training data (overfitting) may score 99% on training but 60% on new data.
- The test set simulates "real-world, unseen data."
- **Never train on test data** — it invalidates your evaluation.

---

### Q13. What is overfitting and underfitting?

**A:**

| Concept | What Happens | Training Accuracy | Test Accuracy | Cause | Fix |
|---------|-------------|-------------------|---------------|-------|-----|
| **Overfitting** | Model memorizes training data; fails on new data | Very high (99%) | Low (60%) | Too complex model, too little data | More data, regularization, simpler model, dropout |
| **Underfitting** | Model is too simple to capture patterns | Low (55%) | Low (50%) | Too simple model, not enough features | More features, more complex model, longer training |
| **Good fit** | Model generalizes well | High (90%) | High (88%) | Right balance | — |

**Analogy:**
- **Overfitting** = A student who memorizes exact exam answers but can't solve new questions.
- **Underfitting** = A student who didn't study enough and can't answer anything.
- **Good fit** = A student who understood the concepts and can apply them to new problems.

```
                    Underfitting    Good Fit    Overfitting
Training error:     High            Low         Very Low
Test error:         High            Low         High
Model complexity:   Too simple      Just right  Too complex
```

---

### Q14. What is cross-validation?

**A:** **Cross-validation** is a technique to evaluate model performance more reliably by training and testing on different subsets of data.

**K-Fold Cross-Validation (most common):**
```
Data: [A] [B] [C] [D] [E]    (5 folds)

Fold 1: Train on [B,C,D,E], Test on [A] → Score: 85%
Fold 2: Train on [A,C,D,E], Test on [B] → Score: 88%
Fold 3: Train on [A,B,D,E], Test on [C] → Score: 82%
Fold 4: Train on [A,B,C,E], Test on [D] → Score: 87%
Fold 5: Train on [A,B,C,D], Test on [E] → Score: 84%

Final Score: Average = 85.2% (more reliable than a single split)
```

**Why it's better than a single train/test split:**
- Every data point is used for both training and testing.
- Reduces variance in evaluation (one lucky/unlucky split won't skew results).
- Better estimate of model performance on unseen data.

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"Mean: {scores.mean():.2f}, Std: {scores.std():.2f}")
```

---

## 🔹 Section 4 — Common ML Algorithms

### Q15. Explain Linear Regression.

**A:** **Linear Regression** fits a straight line through data to predict a continuous target variable.

**Formula:** `y = mx + b` (simple) or `y = w₁x₁ + w₂x₂ + ... + b` (multiple)

```
House Price = (500 × sqft) + (10000 × bedrooms) + 50000
              weights/coefficients                  bias/intercept
```

**Key points:**
- Assumes a **linear relationship** between features and target.
- Minimizes the **sum of squared errors** (SSE) between predictions and actual values.
- Simple, interpretable, fast — good baseline model.
- Can be extended: **Polynomial Regression** for non-linear relationships.

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)

print(f"Coefficients: {model.coef_}")
print(f"Intercept: {model.intercept_}")
```

---

### Q16. Explain Logistic Regression.

**A:** **Logistic Regression** is used for **binary classification** (despite the name "regression"). It predicts the probability that an input belongs to a class.

**How it works:**
1. Compute a linear combination: `z = w₁x₁ + w₂x₂ + ... + b`
2. Pass through **sigmoid function**: `P(y=1) = 1 / (1 + e^(-z))`
3. Output is a probability between 0 and 1.
4. Apply threshold (usually 0.5): if P > 0.5 → Class 1, else → Class 0.

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)  # [P(class 0), P(class 1)]
```

**Use cases:** Spam detection, disease diagnosis, customer churn prediction.

---

### Q17. Explain Decision Trees and Random Forests.

**A:**

**Decision Tree:** A tree-like flowchart where each internal node tests a feature, each branch represents an outcome, and each leaf is a prediction.

```
                    Is salary > 50K?
                   /               \
                 Yes                No
                /                    \
        Has loan?              → Not approved
        /      \
      Yes       No
      /           \
  → Risky       → Approved
```

**Random Forest:** An **ensemble** of many decision trees. Each tree is trained on a random subset of data and features. Final prediction = majority vote (classification) or average (regression).

| Aspect | Decision Tree | Random Forest |
|--------|--------------|---------------|
| Overfitting | High risk | Low (averaging reduces variance) |
| Accuracy | Moderate | High |
| Interpretability | High (visual tree) | Lower (many trees) |
| Speed | Fast | Slower (many trees) |
| Feature importance | Yes | Yes (averaged across trees) |

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
importances = model.feature_importances_  # Which features matter most
```

---

### Q18. What is K-Means Clustering?

**A:** **K-Means** is an unsupervised algorithm that partitions data into **K clusters** based on similarity.

**Steps:**
1. Choose K (number of clusters).
2. Randomly initialize K centroids.
3. Assign each data point to the nearest centroid.
4. Recalculate centroids as the mean of assigned points.
5. Repeat steps 3-4 until centroids don't change (convergence).

**Choosing K — Elbow Method:**
- Run K-Means for K = 1, 2, 3, ..., 10.
- Plot K vs. inertia (sum of squared distances to centroid).
- The "elbow" (where improvement flattens) suggests the optimal K.

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X)
labels = kmeans.labels_        # Cluster assignments
centers = kmeans.cluster_centers_  # Centroid coordinates
```

---

### Q19. What is K-Nearest Neighbors (KNN)?

**A:** **KNN** classifies a new data point based on the **K closest training examples** in feature space.

**How it works:**
1. Choose K (e.g., K=5).
2. For a new point, find the 5 nearest neighbors (using Euclidean distance).
3. Majority vote → assign the most common class among neighbors.

| Aspect | Detail |
|--------|--------|
| **Type** | Supervised (classification and regression) |
| **Lazy learner** | No training phase — stores all data; computes at prediction time |
| **K value** | Small K → sensitive to noise (overfitting); Large K → smoother boundaries |
| **Distance metric** | Euclidean, Manhattan, Cosine |
| **Limitation** | Slow for large datasets (computes distance to ALL training points) |

---

### Q20. What is a Support Vector Machine (SVM)?

**A:** **SVM** finds the **optimal hyperplane** that separates classes with the **maximum margin** (widest gap between classes).

**Key concepts:**
- **Hyperplane** — A decision boundary (line in 2D, plane in 3D, hyperplane in nD).
- **Support vectors** — The data points closest to the hyperplane; they "support" it.
- **Margin** — The distance between the hyperplane and the nearest support vectors.
- **Kernel trick** — Transform non-linearly separable data into higher dimensions where a hyperplane CAN separate them.

**Kernels:**
- **Linear** — Straight line/plane separation.
- **RBF (Radial Basis Function)** — Curved, flexible boundaries.
- **Polynomial** — Polynomial-shaped boundaries.

---

## 🔹 Section 5 — Model Evaluation Metrics

### Q21. What are the key metrics for classification?

**A:**

**Confusion Matrix:**
```
                  Predicted
                Positive  Negative
Actual Positive   TP        FN
Actual Negative   FP        TN
```

| Metric | Formula | When to Use |
|--------|---------|-------------|
| **Accuracy** | (TP+TN) / Total | Balanced classes |
| **Precision** | TP / (TP+FP) | When false positives are costly (spam filter) |
| **Recall (Sensitivity)** | TP / (TP+FN) | When false negatives are costly (disease detection) |
| **F1-Score** | 2 × (Precision × Recall) / (Precision + Recall) | Imbalanced classes; balance precision and recall |
| **AUC-ROC** | Area under ROC curve | Overall model quality; threshold-independent |

**Example — Disease Detection:**
- **Precision:** Of all patients we diagnosed as sick, how many actually are? (Avoid unnecessary treatment)
- **Recall:** Of all actually sick patients, how many did we catch? (Don't miss any sick person)
- In healthcare, **recall is more important** — missing a disease (FN) is worse than a false alarm (FP).

---

### Q22. What are metrics for regression?

**A:**

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **MAE** (Mean Absolute Error) | avg(\|actual - predicted\|) | Average error in same units as target |
| **MSE** (Mean Squared Error) | avg((actual - predicted)²) | Penalizes large errors more |
| **RMSE** (Root MSE) | √MSE | Same units as target; interpretable |
| **R² (R-squared)** | 1 - (SS_res / SS_total) | Proportion of variance explained (0-1); closer to 1 = better |
| **MAPE** (Mean Absolute % Error) | avg(\|error/actual\| × 100) | Percentage error; scale-independent |

```python
from sklearn.metrics import mean_squared_error, r2_score

rmse = mean_squared_error(y_test, predictions, squared=False)
r2 = r2_score(y_test, predictions)
print(f"RMSE: {rmse:.2f}, R²: {r2:.3f}")
```

---

### Q23. What is the bias-variance tradeoff?

**A:**

| Concept | Meaning | Symptom |
|---------|---------|---------|
| **Bias** | Error from wrong assumptions; model is too simple | Underfitting — misses important patterns |
| **Variance** | Error from sensitivity to training data fluctuations; model is too complex | Overfitting — captures noise |

```
Total Error = Bias² + Variance + Irreducible Error

Simple Model:   High Bias, Low Variance   → Underfitting
Complex Model:  Low Bias, High Variance   → Overfitting
Optimal Model:  Balanced Bias & Variance  → Best generalization
```

**Tradeoff:** As you increase model complexity:
- Bias decreases (model captures more patterns).
- Variance increases (model becomes sensitive to training data).
- The sweet spot minimizes total error.

---

## 🔹 Section 6 — Deep Learning Basics

### Q24. What is a neural network?

**A:** A **neural network** is a computational model inspired by the human brain. It consists of layers of interconnected nodes (neurons) that transform input data into output predictions.

**Structure:**
```
Input Layer     Hidden Layers     Output Layer
[x₁] ──┐
        ├──→ [h₁] ──┐
[x₂] ──┤            ├──→ [h₃] ──→ [ŷ]
        ├──→ [h₂] ──┘
[x₃] ──┘
```

**How it works:**
1. Each connection has a **weight** (importance).
2. Each neuron computes: `output = activation(Σ(inputs × weights) + bias)`.
3. **Forward pass** — Data flows through the network to produce a prediction.
4. **Loss calculation** — Compare prediction to actual value.
5. **Backpropagation** — Adjust weights to minimize loss.
6. **Repeat** for many iterations (epochs).

---

### Q25. What is an activation function? Name the common ones.

**A:** An **activation function** introduces **non-linearity** into the network. Without it, a neural network is just a linear equation (no matter how many layers).

| Function | Formula | Output Range | Use Case |
|----------|---------|-------------|----------|
| **ReLU** | max(0, x) | [0, ∞) | Hidden layers (most common) |
| **Sigmoid** | 1/(1+e⁻ˣ) | (0, 1) | Binary classification output |
| **Softmax** | eˣⁱ/Σeˣ | (0, 1), sums to 1 | Multi-class classification output |
| **Tanh** | (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) | (-1, 1) | Hidden layers (less common now) |

**Why ReLU dominates:** Simple, fast to compute, avoids vanishing gradient problem.

---

### Q26. What is backpropagation?

**A:** **Backpropagation** is the algorithm that trains neural networks by computing gradients of the loss function with respect to each weight, then updating weights to minimize the loss.

**Steps:**
1. **Forward pass** — Feed input through network, get prediction.
2. **Compute loss** — How wrong is the prediction? (e.g., MSE, cross-entropy).
3. **Backward pass** — Compute gradient of loss w.r.t. each weight using chain rule of calculus.
4. **Update weights** — `weight = weight - learning_rate × gradient` (**gradient descent**).
5. **Repeat** for many epochs until loss converges.

**Learning rate:**
- Too high → Overshoots optimal weights; loss oscillates.
- Too low → Training is very slow; may get stuck in local minima.
- Typical values: 0.001, 0.01, 0.0001.

---

### Q27. What are CNNs and RNNs?

**A:**

| Architecture | Full Name | Best For | How It Works |
|-------------|-----------|---------|-------------|
| **CNN** | Convolutional Neural Network | Images, spatial data | Slides filters over input to detect features (edges, textures, objects) |
| **RNN** | Recurrent Neural Network | Sequential data (text, time series) | Has memory; output feeds back as input for next step |
| **LSTM** | Long Short-Term Memory | Long sequences | Improved RNN with gates to remember/forget info over long sequences |
| **Transformer** | — | Text, code, any sequence | Attention mechanism; processes entire sequence at once (parallel) |

**Why Transformers replaced RNNs:**
- RNNs process sequences one element at a time (slow, sequential).
- Transformers use **attention** to process all elements simultaneously (parallel, faster).
- Transformers handle long-range dependencies better.
- All modern LLMs (GPT, Gemini, BERT) are Transformers.

---

## 🔹 Section 7 — ML in Practice

### Q28. What is Scikit-learn?

**A:** **Scikit-learn** (sklearn) is Python's most popular ML library for classical (non-deep learning) algorithms.

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 2. Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train_scaled, y_train)

# 4. Predict and evaluate
predictions = model.predict(X_test_scaled)
print(accuracy_score(y_test, predictions))
print(classification_report(y_test, predictions))
```

**Consistent API:** Every sklearn model follows: `model.fit(X, y)` → `model.predict(X)` → `model.score(X, y)`.

---

### Q29. What is regularization? Explain L1 and L2.

**A:** **Regularization** adds a penalty to the loss function to prevent the model from becoming too complex (overfitting).

| Type | Penalty | Effect | Name |
|------|---------|--------|------|
| **L1** | Sum of absolute weights: λΣ\|wᵢ\| | Forces some weights to exactly 0 (feature selection) | Lasso |
| **L2** | Sum of squared weights: λΣwᵢ² | Shrinks all weights toward 0 (but none to exactly 0) | Ridge |
| **Elastic Net** | Combination of L1 + L2 | Both feature selection and shrinkage | Elastic Net |

**λ (lambda)** controls regularization strength:
- λ = 0 → No regularization (may overfit).
- λ very large → Very strong regularization (may underfit).

---

### Q30. What is hyperparameter tuning?

**A:** **Hyperparameters** are settings you configure BEFORE training (unlike model parameters that are LEARNED during training).

| Model Parameters (learned) | Hyperparameters (configured) |
|-----------------------------|------------------------------|
| Weights, biases | Learning rate, batch size |
| Split thresholds in trees | Number of trees, max depth |
| Support vectors | Kernel type, C value |

**Tuning methods:**

| Method | How It Works | Pros | Cons |
|--------|-------------|------|------|
| **Grid Search** | Try every combination of values | Thorough | Slow (exponential) |
| **Random Search** | Try random combinations | Faster; finds good results quicker | May miss optimal |
| **Bayesian Optimization** | Use previous results to guide search | Smart, efficient | Complex setup |

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 20, None],
}
grid_search = GridSearchCV(RandomForestClassifier(), param_grid, cv=5)
grid_search.fit(X_train, y_train)
print(grid_search.best_params_)  # {'max_depth': 10, 'n_estimators': 200}
```

---

## 🔹 Section 8 — AI Ethics & Real-World Considerations

### Q31. What is bias in AI/ML?

**A:** **Bias** in ML means the model systematically makes unfair or incorrect predictions for certain groups.

**Types of bias:**

| Type | Source | Example |
|------|--------|---------|
| **Historical bias** | Training data reflects past discrimination | Hiring model trained on historical data that favored men |
| **Sampling bias** | Training data not representative | Facial recognition trained mostly on light-skinned faces |
| **Label bias** | Incorrect or biased labels | Toxic content detector labels AAVE (African American Vernacular English) as toxic |
| **Confirmation bias** | Model reinforces existing patterns | Recommendation system creates filter bubbles |

**Mitigation:**
- Diverse, representative training data.
- Fairness metrics (equal accuracy across groups).
- Bias audits before deployment.
- Human oversight and feedback loops.

---

### Q32. What is explainability in AI?

**A:** **Explainability (XAI)** means understanding WHY an AI model made a specific prediction.

**Why it matters:**
- **Trust** — Users need to understand AI decisions to trust them.
- **Compliance** — Regulations (GDPR) give users the right to explanation.
- **Debugging** — Find and fix model errors.
- **Fairness** — Detect if model is using biased features.

**Explainability methods:**

| Method | What It Does |
|--------|-------------|
| **Feature importance** | Which features matter most to the model |
| **SHAP values** | How much each feature contributes to each prediction |
| **LIME** | Approximate complex model with interpretable local model |
| **Attention visualization** | Show which parts of input the model focuses on |

---

## 🔹 Section 9 — Quick Fire Questions

### Q33. What is the difference between a parameter and a hyperparameter?

**A:**
- **Parameter** — Learned during training (weights, biases). You don't set them.
- **Hyperparameter** — Set before training (learning rate, number of trees). You choose them.

---

### Q34. What is a loss function?

**A:** A **loss function** measures how wrong the model's predictions are. The goal of training is to minimize the loss.

| Loss Function | Used For | Formula |
|---------------|----------|---------|
| **MSE** | Regression | avg((actual - predicted)²) |
| **Cross-Entropy** | Classification | -Σ(y × log(ŷ)) |
| **Hinge Loss** | SVM | max(0, 1 - y × ŷ) |

---

### Q35. What is gradient descent?

**A:** **Gradient descent** is the optimization algorithm that minimizes the loss function by iteratively adjusting weights in the direction of steepest descent.

```
Repeat:
  1. Compute gradient (slope) of loss w.r.t. weights
  2. Update: weight = weight - learning_rate × gradient
  3. Until loss converges (stops decreasing)
```

**Variants:**
- **Batch GD** — Uses all training data per update (slow but stable).
- **Stochastic GD (SGD)** — Uses one sample per update (fast but noisy).
- **Mini-batch GD** — Uses a small batch (32-256) per update (best of both).
- **Adam** — Adaptive learning rate; most popular optimizer today.

---

### Q36. What is transfer learning?

**A:** **Transfer learning** reuses a model trained on one task as the starting point for a different but related task.

**Example:**
1. Take a CNN trained on ImageNet (14 million images, 20,000 categories).
2. Remove the last classification layer.
3. Add a new layer for your specific task (e.g., 5 disease types).
4. Fine-tune on your small medical image dataset (1,000 images).

**Why it works:**
- Early layers learn universal features (edges, textures, shapes).
- These features transfer across tasks.
- Requires much less data and training time.

**In NLP:** This is how LLMs work — GPT is pre-trained on vast text, then fine-tuned for specific tasks.

---

### Q37. What is the difference between AI and ML in the SAP context?

**A:**

| SAP Service | AI or ML? | What It Does |
|-------------|----------|--------------|
| **SAP AI Core** | ML platform | Train, deploy, and manage ML models |
| **SAP AI Launchpad** | ML management | Monitor and manage AI workflows |
| **SAP GenAI Hub** | Generative AI | Access LLMs (GPT, Gemini) for text generation |
| **SAP Joule** | AI copilot | Natural language assistant for SAP users |
| **SAP HANA PAL** | ML library | Predictive algorithms built into HANA database |
| **SAP Intelligent Robotic Process Automation** | AI + automation | Automate repetitive business processes |

**SAP positions AI as "Business AI"** — AI embedded directly into business processes (HR, finance, supply chain), not just standalone models.

---

> **💡 Viva Tip:** For AI/ML questions, always be ready to explain the **intuition** behind algorithms, not just memorize formulas. Evaluators want to know you understand WHY a technique works, not just how to call `model.fit()`.

---

*End of Unit 5 — Introduction to AI & ML 🧠*
