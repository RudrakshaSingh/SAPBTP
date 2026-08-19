# ☁️ Unit 17 — SAP CAP & HANA Cloud

> **Module**: Module 7 — SAP Business AI  
> **Duration**: Day 29 (8 hours)  
> **Date**: 06-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — SAP Cloud Application Programming Model (CAP)

### Q1. What is SAP CAP (Cloud Application Programming Model)?

**A:** **SAP CAP** is SAP's official, opinionated framework for building **cloud-native business applications** on SAP BTP. It provides a model-driven development approach where you define your data model and services in a high-level language (CDS), and CAP generates most of the boilerplate code.

**Key philosophy:** "Focus on your domain — not on technical plumbing."

| What CAP Provides | Details |
|-------------------|---------|
| **CDS (Core Data Services)** | Domain modeling language for data + services |
| **Node.js / Java runtimes** | Service logic implementation |
| **Auto-generated APIs** | OData v4 and REST from CDS definitions |
| **Database abstraction** | SQLite (dev) → HANA Cloud (prod) with same code |
| **Built-in security** | XSUAA integration, role-based auth |
| **Built-in multi-tenancy** | Serve multiple customers from one deployment |
| **Event handling** | Synchronous (OData) + Asynchronous (Event Mesh) |
| **SAP integrations** | Native connectors to S/4HANA, SuccessFactors |

---

### Q2. What is CDS (Core Data Services)?

**A:** **CDS** is a domain-specific language (DSL) used in CAP to define:
- **Data models** (entities, relationships)
- **Services** (which entities to expose, how)
- **Annotations** (UI behavior, security, documentation)

```cds
// db/schema.cds — Data Model
namespace com.accenture.training;

using { cuid, managed } from '@sap/cds/common';

entity Employees : cuid, managed {
  name        : String(100) not null;
  email       : String(100) @assert.unique;
  department  : Association to Departments;
  salary      : Decimal(12,2);
  joiningDate : Date;
  active      : Boolean default true;
}

entity Departments : cuid {
  name      : String(100);
  manager   : Association to Employees;
  employees : Composition of many Employees on employees.department = $self;
}

// Aspects: Reusable field sets
aspect Timestamps {
  createdAt  : DateTime @cds.on.insert: $now;
  modifiedAt : DateTime @cds.on.update: $now;
}
```

**What `cuid` and `managed` give you automatically:**
- `cuid` → Auto-generated UUID primary key.
- `managed` → `createdAt`, `createdBy`, `modifiedAt`, `modifiedBy` fields auto-populated.

---

### Q3. How do you define a CAP service?

**A:**

```cds
// srv/employee-service.cds — Service Definition
using com.accenture.training from '../db/schema';

service EmployeeService @(path: '/api/v1') {

  // Expose entity as read-only (GET only)
  @readonly
  entity Departments as projection on training.Departments;

  // Full CRUD on Employees
  entity Employees as projection on training.Employees;

  // Custom action (POST with custom logic)
  action transferEmployee(employeeId: UUID, newDeptId: UUID)
         returns { success: Boolean; message: String };

  // Custom function (GET with business logic)
  function getEmployeesByDept(deptId: UUID)
           returns array of Employees;
}
```

**What CAP auto-generates from this:**
- `GET /api/v1/Employees` — List all employees.
- `GET /api/v1/Employees/{id}` — Get employee by ID.
- `POST /api/v1/Employees` — Create employee.
- `PATCH /api/v1/Employees/{id}` — Update employee.
- `DELETE /api/v1/Employees/{id}` — Delete employee.
- `POST /api/v1/transferEmployee` — Custom action.
- `GET /api/v1/getEmployeesByDept(deptId='...')` — Custom function.
- `/api/v1/$metadata` — OData metadata document.

---

### Q4. How do you add business logic to a CAP service?

**A:**

```javascript
// srv/employee-service.js — Service Implementation
const cds = require('@sap/cds')

module.exports = class EmployeeService extends cds.ApplicationService {

  async init() {
    const { Employees } = this.entities

    // Hook: Run before every CREATE
    this.before('CREATE', Employees, async (req) => {
      // Validate salary
      if (req.data.salary < 0) {
        req.reject(400, 'Salary cannot be negative')
      }
      // Auto-set email to lowercase
      if (req.data.email) {
        req.data.email = req.data.email.toLowerCase()
      }
    })

    // Hook: Run after every READ
    this.after('READ', Employees, (employees) => {
      // Mask salary for non-managers (based on user role)
      employees.forEach(emp => {
        if (!this.currentUser.is('Manager')) {
          emp.salary = null  // Hide salary from non-managers
        }
      })
    })

    // Custom action implementation
    this.on('transferEmployee', async (req) => {
      const { employeeId, newDeptId } = req.data
      const db = await cds.connect.to('db')
      await db.update(Employees, employeeId).set({ department_ID: newDeptId })
      return { success: true, message: `Employee transferred to department ${newDeptId}` }
    })

    await super.init()
  }
}
```

**CAP event hooks:**

| Hook | When It Runs | Use For |
|------|-------------|---------|
| `before` | Before DB operation | Validation, input transformation |
| `on` | Instead of default DB operation | Custom business logic |
| `after` | After DB operation | Post-processing, data masking |

---

### Q5. What is CDS Annotations? How do Fiori Elements use them?

**A:** **Annotations** in CDS add metadata to entities/services that tools like SAP Fiori Elements use to auto-generate UIs.

```cds
// UI Annotations for automatic Fiori Elements app generation
annotate EmployeeService.Employees with @(
  // Generate a List Report page
  UI.LineItem: [
    { $Type: 'UI.DataField', Value: name, Label: 'Name' },
    { $Type: 'UI.DataField', Value: email, Label: 'Email' },
    { $Type: 'UI.DataField', Value: department.name, Label: 'Department' }
  ],

  // Object page header
  UI.HeaderInfo: {
    TypeName: 'Employee',
    TypeNamePlural: 'Employees',
    Title: { Value: name }
  },

  // Form layout for detail view
  UI.FieldGroup#GeneralInfo: {
    Data: [
      { Value: name },
      { Value: email },
      { Value: salary },
      { Value: joiningDate }
    ]
  }
);

// Security annotation
annotate EmployeeService with @(requires: 'authenticated-user');
annotate EmployeeService.Employees with @(restrict: [
  { grant: 'READ', to: 'Employee' },
  { grant: '*', to: 'HR_Manager' }
]);
```

---

### Q6. What is the CAP project structure?

**A:**

```
my-cap-project/
├── db/
│   ├── schema.cds          ← Entity definitions (data model)
│   └── data/               ← CSV seed data for local dev
│       └── employees.csv
├── srv/
│   ├── employee-service.cds ← Service + API definitions
│   └── employee-service.js  ← Business logic handlers
├── app/
│   └── employees/           ← Fiori Elements app (auto-generated or manual)
│       └── webapp/
├── package.json             ← npm dependencies + cds configuration
└── .env                     ← Local environment variables

package.json CDS config:
{
  "cds": {
    "requires": {
      "db": {
        "kind": "hana",         ← Use HANA Cloud in production
        "[development]": {
          "kind": "sqlite"      ← Use SQLite locally (auto-created)
        }
      }
    }
  }
}
```

**Development commands:**
```bash
npm install         # Install dependencies
cds watch           # Start local dev server with live reload (SQLite)
cds deploy --to hana  # Deploy schema to HANA Cloud
cds build           # Build for production (Cloud Foundry)
cf push             # Deploy to SAP BTP
```

---

### Q7. What is OData? Why does SAP use it?

**A:** **OData (Open Data Protocol)** is a standard REST protocol for CRUD operations on data, developed by Microsoft and widely adopted by SAP.

**OData vs Plain REST:**

| Aspect | Plain REST | OData |
|--------|-----------|-------|
| Standard | No standard | OASIS standard |
| Metadata | No standard way | `$metadata` endpoint |
| Filtering | Custom implementation | Standardized `$filter` |
| Sorting | Custom | Standardized `$orderby` |
| Paging | Custom | Standardized `$top`, `$skip` |
| Expanding | Custom | Standardized `$expand` |
| Count | Custom | Standardized `$count` |

**OData query examples (CAP auto-supports all):**
```
GET /api/v1/Employees                         → All employees
GET /api/v1/Employees/42                      → Employee with ID 42
GET /api/v1/Employees?$filter=salary gt 70000 → Employees earning > 70K
GET /api/v1/Employees?$select=name,email      → Only name and email fields
GET /api/v1/Employees?$top=10&$skip=20        → Pagination (page 3 of 10/page)
GET /api/v1/Employees?$orderby=salary desc    → Sort by salary descending
GET /api/v1/Employees?$expand=department      → Include department details
GET /api/v1/Employees/$count                  → Total count
```

---

## 🔹 Section 2 — SAP HANA Cloud

### Q8. What is SAP HANA? How is it different from regular databases?

**A:** **SAP HANA (High-performance ANalytic Appliance)** is an **in-memory, columnar database** that can handle both OLTP (transactions) and OLAP (analytics) workloads in a single database.

**Key architectural differences:**

| Feature | Traditional DB (MySQL/PostgreSQL) | SAP HANA |
|---------|----------------------------------|----------|
| **Primary storage** | Disk (data read into memory cache) | RAM (main storage = memory) |
| **Storage orientation** | Row-based | Column-based |
| **OLTP** | Excellent | Good |
| **OLAP** | Poor (needs data warehouse) | Excellent |
| **Aggregation** | Pre-computed and stored separately | Computed in real-time |
| **Compression** | Moderate | Very high (column compression) |
| **Index types** | B-tree, hash | Inverted index, B-tree, spatial, vector |
| **AI/ML built-in** | No | Yes (PAL, APL) |
| **Cost** | Free/low | Very high (enterprise) |

---

### Q9. Why is column-oriented storage important for analytics?

**A:**

**Row storage (traditional):**
```
Row 1: [emp_id=1, name="Alice", dept="HR", salary=80000]
Row 2: [emp_id=2, name="Bob",   dept="IT", salary=95000]
Row 3: [emp_id=3, name="Carol", dept="HR", salary=75000]
```
→ To compute `SUM(salary)` for HR dept, must read ALL columns of ALL rows.

**Column storage (HANA):**
```
salary column: [80000, 95000, 75000, 82000, ...]
dept column:   ["HR",  "IT",  "HR",  "Finance", ...]
```
→ To compute `SUM(salary)` for HR: Read ONLY salary + dept columns. Much faster!

**Benefits:**
- **High compression** — Similar values in a column compress very well.
- **Faster analytics** — Only read the columns you need.
- **Vectorized operations** — CPU can process many values simultaneously.

---

### Q10. What is SAP HANA Cloud?

**A:** **SAP HANA Cloud** is the **managed cloud version** of SAP HANA, available as a service on SAP BTP.

**Key differences from on-premise HANA:**

| Aspect | HANA On-Premise | HANA Cloud |
|--------|----------------|------------|
| Infrastructure | Customer manages | SAP manages |
| Scaling | Manual, fixed hardware | Elastic (scale up/down in minutes) |
| Backups | Customer responsibility | Automatic daily backups |
| Patching | Customer schedules | SAP handles |
| Data lakes | Separate product | Native integration (HANA Data Lake) |
| Vector Engine | Requires manual setup | Built-in, native support |
| Cost | Large CapEx | Monthly subscription |

---

### Q11. What are the HANA Cloud components?

**A:**

```
SAP HANA Cloud
    ├── HANA Database (in-memory, columnar, relational)
    ├── HANA Data Lake (cold storage for large volumes)
    ├── HANA Vector Engine (embedding storage + similarity search)
    └── HANA Graph Engine (graph queries)

Additional services:
    ├── Data Warehouse Cloud (DWC) — Analytics and data warehousing
    └── SAP Analytics Cloud (SAC) — BI dashboards and planning
```

---

### Q12. What is the HANA PAL (Predictive Analysis Library)?

**A:** **PAL** is a collection of machine learning algorithms **built directly into HANA Cloud** — running inside the database.

**Advantage:** Data doesn't need to leave the database for ML. Compute goes TO the data (not data to compute).

**PAL algorithms:**

| Category | Algorithms Available |
|----------|---------------------|
| **Classification** | Decision trees, Random Forest, SVM, KNN, Logistic Regression |
| **Regression** | Linear, Polynomial, Random Forest Regression |
| **Clustering** | K-Means, DBSCAN, Hierarchical |
| **Time Series** | ARIMA, Triple Exponential Smoothing, Auto-ARIMA |
| **Anomaly Detection** | Isolation Forest, One-Class SVM |
| **Recommendation** | ALS (Alternating Least Squares) |

```sql
-- K-Means clustering using PAL inside HANA
CALL _SYS_AFL.PAL_KMEANS(
    "INPUT_DATA",    -- Input table
    "PARAMETER",     -- K=3, max_iter=100
    "CLUSTER_ID",    -- Output: cluster assignments
    "CLUSTER_CENTER" -- Output: cluster centroids
) WITH OVERVIEW;
```

---

### Q13. How do you connect to SAP HANA Cloud from Python?

**A:**

```python
# Using hdbcli (SAP HANA Python client)
from hdbcli import dbapi

# Connection using service key credentials
conn = dbapi.connect(
    address='your-instance.hanacloud.ondemand.com',
    port=443,
    user='DBADMIN',
    password='YourPassword',
    encrypt=True,
    sslValidateCertificate=True
)

# Execute SQL
cursor = conn.cursor()
cursor.execute("SELECT * FROM EMPLOYEES WHERE SALARY > 70000")
results = cursor.fetchall()
for row in results:
    print(row)

# Pandas integration
import pandas as pd
df = pd.read_sql("SELECT NAME, SALARY FROM EMPLOYEES", conn)
print(df.head())

# Connection using environment variables (BTP style)
import os, json
vcap = json.loads(os.environ.get('VCAP_SERVICES', '{}'))
hana_creds = vcap['hana'][0]['credentials']
conn = dbapi.connect(
    address=hana_creds['host'],
    port=hana_creds['port'],
    user=hana_creds['user'],
    password=hana_creds['password'],
    encrypt=True
)
```

---

### Q14. What are Calculation Views in SAP HANA?

**A:** **Calculation Views** are virtual analytical models defined in HANA that compute complex aggregations, joins, and transformations in real-time.

```
Raw Tables:
    SALES_ORDERS + CUSTOMERS + PRODUCTS

Calculation View: "CV_SALES_ANALYSIS"
    → Joins SALES_ORDERS + CUSTOMERS + PRODUCTS
    → Filters: active customers only
    → Aggregates: SUM(revenue) GROUP BY customer, product, month
    → Adds calculated columns: revenue_growth_pct

BI Tool queries CV_SALES_ANALYSIS → Gets pre-computed result in milliseconds
```

**Why Calculation Views instead of SQL Views:**
- Pushed down to HANA's in-memory engine → much faster.
- Graphically designed (drag-drop in SAP BAS or HANA Studio).
- Support star schemas, hierarchies, currency conversion.

---

## 🔹 Section 3 — CAP + HANA Integration

### Q15. How does CAP connect to HANA Cloud in production?

**A:**

```javascript
// package.json — Configure HANA in production
{
  "cds": {
    "requires": {
      "db": {
        "kind": "hana-cloud",
        "[production]": {
          "kind": "hana-cloud"
        },
        "[development]": {
          "kind": "sqlite",
          "credentials": { "database": ":memory:" }
        }
      }
    }
  }
}
```

```bash
# Deploy CDS schema to HANA Cloud (creates tables automatically)
cds deploy --to hana

# CAP reads credentials from:
# 1. VCAP_SERVICES env var (when deployed to Cloud Foundry)
# 2. .env file (local development with tunnel to HANA)
# 3. default-env.json (local development alternative)
```

**CAP auto-generates HANA tables from CDS entities:**
```cds
entity Employees {
  key ID    : UUID;
  name      : String(100);
  salary    : Decimal;
}
```
→ CAP creates HANA table: `COM_ACCENTURE_EMPLOYEES` with columns ID, NAME, SALARY.

---

### Q16. What is SAP Business Application Studio (BAS)?

**A:** **SAP Business Application Studio** is SAP's cloud-based IDE for developing BTP applications — a managed VS Code environment with SAP-specific extensions.

**Pre-installed for:**
- CAP development (CDS language support, CAP commands).
- Fiori development (Page Map, Guided Development).
- SAP Build (low-code tools).
- ABAP development.
- Python/Node.js general development.

**Access:** Available as a service on SAP BTP.

---

## 🔹 Section 4 — Quick Fire Questions

### Q17. What is the difference between CAP and ABAP?

**A:**

| Aspect | CAP | ABAP |
|--------|-----|------|
| Language | JavaScript (Node.js) or Java | ABAP (SAP-proprietary) |
| Platform | SAP BTP Cloud Foundry/Kyma | SAP S/4HANA / ABAP Environment |
| Use case | New cloud-native extensions | Extend SAP core, classic customizations |
| Learning curve | Moderate (standard tech) | High (SAP-specific language) |
| "Clean core" | ✅ Yes — runs on BTP | ✅ Yes (via RAP model) |

---

### Q18. What is a CAP "action" vs a CAP "function"?

**A:**

| | Function | Action |
|-|----------|--------|
| **HTTP method** | GET | POST |
| **Side effects** | No (read-only) | Yes (can modify data) |
| **OData type** | `FunctionImport` | `ActionImport` |
| **Example** | `getRecommendations(empId)` | `approveLeave(requestId)` |

---

### Q19. What is `cds watch` and what does it do?

**A:** `cds watch` starts the CAP development server with:
- **Auto-reload** — Restarts on every file change.
- **SQLite in-memory DB** — No HANA needed for local dev.
- **Mock authentication** — Use query parameters for user/role testing.
- **Live data seeding** — Loads CSV data from `db/data/` on start.
- **Opens browser** — Shows the running service URLs.

```bash
$ cds watch
[cds] - Loaded model from 3 file(s): db/schema.cds, srv/service.cds
[cds] - Serving EmployeeService at /api/v1 { impl: srv/service.js }
[cds] - server listening on { url: 'http://localhost:4004' }

# Visit http://localhost:4004 → See all available endpoints
# Visit http://localhost:4004/api/v1/$metadata → OData metadata
```

---

### Q20. What is VCAP_SERVICES?

**A:** **VCAP_SERVICES** is a Cloud Foundry environment variable that contains connection credentials for all service instances bound to an application. CAP and most SAP BTP applications read credentials from it automatically.

```json
{
  "hana": [{
    "credentials": {
      "host": "your-instance.hanacloud.ondemand.com",
      "port": "443",
      "user": "DBUSER",
      "password": "secret",
      "schema": "MY_SCHEMA"
    }
  }],
  "xsuaa": [{
    "credentials": {
      "clientid": "sb-myapp!t1234",
      "clientsecret": "...",
      "url": "https://myorg.authentication.eu10.hana.ondemand.com"
    }
  }]
}
```

---

> **💡 Viva Tip:** CAP is the **standard framework** for SAP BTP development. If asked how to build an enterprise version of your hackathon project on SAP, the answer is: CAP (Node.js) + HANA Cloud + Fiori Elements UI. Know the basic CDS syntax and the `before/on/after` event hook pattern.

---

*End of Unit 17 — SAP CAP & HANA Cloud ☁️*
