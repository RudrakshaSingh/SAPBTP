# 🚀 Unit 15 — DataOps, CI/CD & Deployment

> **Module**: Module 6 — DevOps  
> **Duration**: Day 27 (8 hours)  
> **Date**: 04-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — DevOps Fundamentals

### Q1. What is DevOps? What problems does it solve?

**A:** **DevOps** is a culture and set of practices that combines **software development (Dev)** and **IT operations (Ops)** to shorten the development lifecycle and deliver software continuously.

**Problems DevOps solves:**

| Problem (Before DevOps) | Solution (DevOps) |
|-------------------------|-------------------|
| Dev and Ops teams don't communicate | Shared responsibility and tools |
| Manual deployments → errors, delays | Automated CI/CD pipelines |
| "Works on my machine" | Containerization (Docker) |
| Long release cycles (months) | Continuous deployment (hours/minutes) |
| Difficult to scale | Infrastructure as Code (IaC) |
| No feedback on production issues | Monitoring and observability |

**DevOps lifecycle:**
```
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor → (back to Plan)
```

---

### Q2. What is CI/CD? Explain each component.

**A:** **CI/CD = Continuous Integration / Continuous Delivery (or Deployment)**

| Component | What It Means | Key Practice |
|-----------|--------------|-------------|
| **Continuous Integration (CI)** | Developers frequently merge code to a shared branch; automated builds and tests run | Merge at least daily; never break main |
| **Continuous Delivery (CD)** | Code is always in a deployable state; deployment to production is manual but one-click | Staging environment always ready |
| **Continuous Deployment** | Every passing build is automatically deployed to production | No manual deployment step |

**CI/CD Pipeline:**
```
Code Push → [Build] → [Unit Tests] → [Integration Tests] → [Security Scan]
                                                                → [Deploy to Staging]
                                                                → [E2E Tests]
                                                                → [Deploy to Production]
```

---

### Q3. What are the popular CI/CD tools?

**A:**

| Tool | Company | Key Feature |
|------|---------|------------|
| **GitHub Actions** | GitHub | YAML workflows, tightly integrated with GitHub |
| **GitLab CI/CD** | GitLab | Built into GitLab, very powerful |
| **Jenkins** | Open source | Highly customizable, huge plugin ecosystem |
| **Azure DevOps** | Microsoft | Enterprise-grade, integrates with Azure |
| **CircleCI** | CircleCI | Cloud-native, fast |
| **SAP Continuous Integration & Delivery** | SAP | Built for SAP BTP deployments |

---

### Q4. What is a CI/CD pipeline for a Python/FastAPI GenAI project?

**A:**

```yaml
# .github/workflows/ci-cd.yml (GitHub Actions)
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        run: pytest tests/ -v --cov=app

      - name: Lint
        run: |
          pip install flake8
          flake8 app.py --max-line-length=100

  deploy:
    needs: test          # Only deploy if tests pass
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'   # Only deploy from main branch
    steps:
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy my-rag-api \
            --image gcr.io/my-project/my-rag-api:latest \
            --platform managed \
            --region us-central1
```

---

## 🔹 Section 2 — Containerization

### Q5. How do you containerize a FastAPI application?

**A:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY .env.example .env

# Expose the port FastAPI runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t my-rag-api .
docker run -p 8000:8000 -e GOOGLE_API_KEY=... my-rag-api
```

---

### Q6. What is Docker Compose? When is it used?

**A:** **Docker Compose** orchestrates multiple containers that work together as a single application.

```yaml
# docker-compose.yml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - db
    volumes:
      - ./app.py:/app/app.py  # Hot reload in development

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: rag_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"

volumes:
  postgres_data:
```

```bash
docker-compose up -d           # Start all services
docker-compose down            # Stop all services
docker-compose logs -f api     # View API logs
```

---

## 🔹 Section 3 — DataOps

### Q7. What is DataOps?

**A:** **DataOps** applies DevOps principles to data pipelines — automating, testing, monitoring, and continuously improving data workflows.

| DevOps Practice | DataOps Equivalent |
|----------------|-------------------|
| CI/CD for code | CI/CD for data pipelines |
| Unit tests | Data quality tests |
| Version control (Git) | Data version control (DVC) |
| Monitoring | Data drift detection |
| Infrastructure as Code | Pipeline as Code (Airflow DAGs, dbt) |

**DataOps principles:**
1. **Automate** — No manual data processing steps.
2. **Test** — Validate data quality at every stage.
3. **Version** — Track data and pipeline versions.
4. **Monitor** — Alert on data quality issues immediately.
5. **Collaborate** — Data engineers + scientists + analysts work together.

---

### Q8. What is data versioning? What tools support it?

**A:** **Data versioning** tracks changes to datasets over time, similar to how Git tracks code changes.

| Tool | What It Does |
|------|-------------|
| **DVC (Data Version Control)** | Git-like versioning for datasets and ML models |
| **Delta Lake** | ACID transactions and versioning for data lakes |
| **Apache Iceberg** | Table format with time travel and versioning |
| **lakeFS** | Git-like branching for data lakes |

```bash
# DVC example:
dvc init
dvc add data/employees.csv      # Track this file with DVC (not Git)
git add data/employees.csv.dvc  # Commit the pointer, not the data
dvc push                        # Upload actual data to S3/GCS

# Roll back to previous version:
git checkout v1.0 data/employees.csv.dvc
dvc checkout
```

---

### Q9. What is data quality testing? How is it automated?

**A:**

```python
# Great Expectations example (leading data quality framework)
import great_expectations as gx

# Define expectations for your data
context = gx.get_context()
suite = context.add_expectation_suite("employee_data_suite")

# Define what "good data" looks like
suite.expect_column_to_exist("emp_id")
suite.expect_column_values_to_not_be_null("emp_id")
suite.expect_column_values_to_be_unique("emp_id")
suite.expect_column_values_to_not_be_null("salary")
suite.expect_column_values_to_be_between("salary", min_value=0, max_value=10_000_000)
suite.expect_column_values_to_be_in_set("department", ["Engineering", "HR", "Finance"])

# Run validation
checkpoint = context.add_checkpoint(
    name="employee_checkpoint",
    batch_request=batch_request,
    expectation_suite_name="employee_data_suite"
)
results = checkpoint.run()

if not results["success"]:
    # Send alert, fail the pipeline
    raise DataQualityError("Employee data quality check failed!")
```

---

## 🔹 Section 4 — Deployment Strategies

### Q10. What are the common deployment strategies?

**A:**

| Strategy | How It Works | Risk | Downtime |
|----------|-------------|------|---------|
| **Blue-Green** | Run two identical environments; switch traffic from Blue (old) to Green (new) | Low (instant rollback) | None |
| **Canary** | Route small % of traffic (1-5%) to new version; gradually increase if healthy | Low | None |
| **Rolling** | Replace old instances one by one with new ones | Medium | Minimal |
| **Recreate** | Stop all old instances, start all new ones | High (if new version has bugs) | Yes |
| **Feature Flags** | Deploy new code but hide behind a flag; enable for specific users | Very low | None |

**Blue-Green in practice:**
```
Old: Blue [v1.0] ← 100% traffic
New: Green [v2.0] ← 0% traffic

Test Green → If healthy:
Switch: Green [v2.0] ← 100% traffic
        Blue [v1.0] ← 0% (keep as rollback for 24h)
```

---

### Q11. What is Infrastructure as Code (IaC)?

**A:** **IaC** means managing infrastructure (servers, networks, databases) through code/configuration files instead of manual GUI/CLI setup.

| Tool | Language | Best For |
|------|----------|---------|
| **Terraform** | HCL | Multi-cloud infrastructure |
| **AWS CloudFormation** | YAML/JSON | AWS-native resources |
| **Azure ARM/Bicep** | JSON/Bicep | Azure resources |
| **Pulumi** | Python, TypeScript | Multi-cloud with real languages |
| **Ansible** | YAML | Configuration management |

**Benefits:**
- **Reproducible** — Same code → same infrastructure every time.
- **Version controlled** — Track infrastructure changes in Git.
- **Automated** — Create/destroy environments in minutes.
- **Documentation** — Infrastructure IS the documentation.

---

### Q12. What is monitoring and observability for AI systems?

**A:**

| Concept | What It Tracks |
|---------|---------------|
| **Logging** | Events, errors, API calls |
| **Metrics** | Response time, token count, error rate, cost |
| **Tracing** | Full request path across microservices |
| **Alerting** | Notify when metrics breach thresholds |

**AI-specific monitoring:**
- **Model drift** — Model performance degrades over time (data distribution changes).
- **Data drift** — Input data distribution changes from training distribution.
- **LLM cost tracking** — Monitor token consumption and costs per request.
- **Hallucination rate** — Track % of responses flagged as low-quality.
- **Latency percentiles** — P50, P95, P99 response times.

```python
# Logging in FastAPI
import logging
import time

logger = logging.getLogger(__name__)

@app.post("/ask")
def ask(req: AskRequest):
    start = time.time()
    try:
        result = run_rag(req.question)
        duration = time.time() - start
        logger.info(f"success|question_len={len(req.question)}|duration={duration:.2f}s")
        return result
    except Exception as e:
        logger.error(f"error|{e}|question={req.question[:50]}")
        raise
```

---

## 🔹 Section 5 — SAP BTP Deployment

### Q13. How do you deploy a Python app to SAP BTP Cloud Foundry?

**A:**

```yaml
# manifest.yml
applications:
  - name: my-rag-api
    memory: 512M
    instances: 1
    buildpacks:
      - python_buildpack
    command: uvicorn app:app --host 0.0.0.0 --port $PORT
    env:
      GOOGLE_API_KEY: ((google-api-key))
    services:
      - my-hana-db
```

```bash
# Deploy to Cloud Foundry
cf login -a https://api.cf.eu10.hana.ondemand.com
cf push my-rag-api
cf env my-rag-api              # View environment variables
cf logs my-rag-api --recent    # View logs
cf scale my-rag-api -i 3       # Scale to 3 instances
```

---

### Q14. What is SAP CI/CD for BTP?

**A:** **SAP Continuous Integration & Delivery** is a managed CI/CD service on SAP BTP.

**Features:**
- Automated pipeline configuration for CAP (Node.js, Java), SAPUI5, and custom apps.
- Integrated with SAP systems (ABAP, SAP Fiori).
- No infrastructure to manage — fully managed by SAP.
- Supports GitHub, GitLab, Bitbucket as source repositories.

**Pipeline stages:**
1. **Build** — Install dependencies, build the app.
2. **Unit Tests** — Run automated tests.
3. **Malware Scan** — Security scanning.
4. **Lint** — Code quality checks.
5. **Deploy** — Deploy to SAP BTP environment.

---

## 🔹 Section 6 — Quick Fire Questions

### Q15. What is the difference between DevOps, DataOps, and MLOps?

**A:**

| Aspect | DevOps | DataOps | MLOps |
|--------|--------|---------|-------|
| Focus | Software delivery | Data pipeline delivery | ML model lifecycle |
| Artifacts | Code, apps | Data pipelines, datasets | ML models, training code |
| Key challenge | Deployment speed | Data quality, freshness | Model drift, reproducibility |
| Tools | GitHub Actions, Docker | Airflow, dbt, Great Expectations | MLflow, Weights & Biases, Kubeflow |

---

### Q16. What is Git branching strategy?

**A:**

**Gitflow:**
- `main` — Production code only.
- `develop` — Integration branch.
- `feature/xyz` — New features.
- `hotfix/xyz` — Emergency production fixes.

**Trunk-based development (preferred for CI/CD):**
- Only one main branch.
- All developers merge daily.
- Feature flags for incomplete features.
- CI/CD runs on every merge.

---

### Q17. What is a secret manager? Why not store secrets in code?

**A:** A **secret manager** securely stores and controls access to secrets (API keys, passwords, certificates).

| Why NOT in code | Secret Manager |
|-----------------|----------------|
| Git history is forever | Secrets stored encrypted |
| Anyone with repo access sees secrets | Role-based access control |
| Hard to rotate (update many files) | Rotate in one place; apps auto-refresh |
| Shared secrets across environments | Different secrets per environment |

**Tools:** AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, HashiCorp Vault, SAP Credential Store (on BTP).

```python
# Reading from secret manager (instead of .env):
import boto3
client = boto3.client("secretsmanager")
secret = client.get_secret_value(SecretId="google-api-key")
GOOGLE_API_KEY = secret["SecretString"]
```

---

> **💡 Viva Tip:** For DevOps questions, focus on the **pipeline flow** — code push → test → build → deploy. Be ready to explain HOW you would deploy your RAG project to production (Docker, CI/CD, environment variables, monitoring).

---

*End of Unit 15 — DataOps, CI/CD & Deployment 🚀*
