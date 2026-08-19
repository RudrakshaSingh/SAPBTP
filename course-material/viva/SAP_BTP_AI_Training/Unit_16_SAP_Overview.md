# 🏢 Unit 16 — SAP Overview

> **Module**: Module 7 — SAP Business AI  
> **Duration**: Day 28 (8 hours)  
> **Date**: 05-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — SAP as a Company & Platform

### Q1. What is SAP? What does it stand for and what does it do?

**A:** **SAP** stands for **Systeme, Anwendungen und Produkte in der Datenverarbeitung** (German) — *Systems, Applications, and Products in Data Processing*.

Founded in 1972 in Walldorf, Germany by 5 former IBM engineers, SAP is the world's largest enterprise software company by revenue.

**What SAP does:**
- Provides **Enterprise Resource Planning (ERP)** software that runs every core business process of an enterprise.
- Serves: Finance, Procurement, Supply Chain, Manufacturing, Sales, HR, Customer Experience.
- **99 of the 100 largest global companies** use SAP.
- **400,000+ customers** in **180+ countries**.
- Handles **87% of global commerce** in some form.

**Key differentiator:** SAP integrates ALL business functions into ONE system with a shared database. No more siloed spreadsheets or disconnected systems.

---

### Q2. What is ERP? Why do enterprises need it?

**A:** **ERP (Enterprise Resource Planning)** is software that manages and integrates all core business processes through a **shared database**.

**Without ERP (siloed systems):**
```
Finance dept:     Excel/local software  ─┐
HR dept:          Separate HR system    ─┤─ No shared data
Supply chain:     Separate SCM tool     ─┤─ Manual reconciliation
Sales:            Separate CRM          ─┘─ Data inconsistency
```

**With ERP (integrated):**
```
Finance ─┐
HR      ─┤─ Shared SAP Database ─→ Real-time, consistent data
Supply  ─┤                       ─→ Single source of truth
Sales   ─┘                       ─→ Cross-functional reports
```

**Business benefits of ERP:**
- **Inventory control** — Know stock levels in real-time; no over/under ordering.
- **Financial accuracy** — When a sale happens, inventory + revenue + payables update automatically.
- **Compliance** — Automated audit trails for legal and regulatory reporting.
- **Efficiency** — Eliminate manual data entry between systems.
- **Decision-making** — Real-time dashboards with accurate data.

---

### Q3. What are SAP's main product lines?

**A:**

| Product | Category | What It Manages |
|---------|----------|----------------|
| **SAP S/4HANA** | ERP | Finance, Logistics, Manufacturing, Procurement |
| **SAP SuccessFactors** | HCM | HR, Payroll, Learning, Recruiting |
| **SAP Ariba** | Procurement | Supplier management, sourcing, contracts |
| **SAP Concur** | T&E | Travel booking, expense management |
| **SAP Analytics Cloud (SAC)** | Analytics | BI, planning, predictive analytics |
| **SAP Customer Experience (CX)** | CRM | Sales, marketing, commerce, service |
| **SAP Integrated Business Planning (IBP)** | Supply Chain | Demand planning, supply planning |
| **SAP Business Technology Platform (BTP)** | Platform | Cloud platform, integration, AI, development |

---

### Q4. What is the difference between SAP R/3, SAP ECC, and SAP S/4HANA?

**A:**

| Version | Era | Database | Architecture | UI |
|---------|-----|---------|-------------|-----|
| **SAP R/3** | 1992-2004 | Any RDBMS | 3-tier client-server | SAP GUI |
| **SAP ECC (ERP Central Component)** | 2004-2025 | Any RDBMS | Enhanced R/3 | SAP GUI |
| **SAP S/4HANA** | 2015-present | SAP HANA ONLY | Simplified, in-memory | SAP Fiori (web) |

**Why S/4HANA is a game-changer:**
- **HANA in-memory database** → Queries that took hours now take seconds.
- **Simplified data model** → Removed aggregate tables; compute in real-time.
- **Modern Fiori UI** → Responsive, web-based, mobile-friendly.
- **Built-in AI** → Machine learning capabilities embedded in business processes.
- **SAP's strategic product** → Maintenance of ECC ends in 2027.

---

### Q5. What is SAP BTP (Business Technology Platform)? Why is it SAP's most important platform?

**A:** **SAP BTP** is SAP's **unified cloud platform** that provides services and capabilities for:

| Pillar | What It Includes |
|--------|----------------|
| **Application Development** | CAP, Build Apps, Cloud Foundry, Kyma |
| **Automation** | Build Process Automation, SAP Intelligent RPA |
| **Integration** | SAP Integration Suite, Event Mesh, Open Connectors |
| **Data & Analytics** | SAP HANA Cloud, Data Warehouse Cloud, Analytics Cloud |
| **AI** | SAP AI Core, AI Launchpad, GenAI Hub |

**Why BTP is strategically critical:**
- It's SAP's answer to AWS/Azure/GCP — but purpose-built for SAP.
- It enables the **"clean core"** strategy — extend SAP without modifying core ECC/S/4.
- All new SAP capabilities (AI, GenAI, low-code) are built on BTP.
- It's how customers integrate SAP with non-SAP systems.

---

## 🔹 Section 2 — SAP BTP Architecture

### Q6. Explain the SAP BTP Global Account and Subaccount structure.

**A:**

```
SAP BTP Global Account
  (Your organization's master contract with SAP)
  ├── Entitlements: Which services you can use + quotas
  ├── Users: Global admins
  └── Directories (optional grouping)
       ├── Directory: "Development"
       │    ├── Subaccount: dev-eu10
       │    └── Subaccount: dev-us10
       ├── Directory: "Staging"
       │    └── Subaccount: staging-eu10
       └── Directory: "Production"
            └── Subaccount: prod-eu10
```

| Concept | Purpose |
|---------|---------|
| **Global Account** | Top-level; holds your SAP BTP contract and all entitlements |
| **Directory** | Optional grouping of subaccounts (e.g., by region, team) |
| **Subaccount** | Isolated unit; has its own services, spaces, users, and policies |
| **Entitlement** | Right to use a specific service (assigned at subaccount level) |
| **Quota** | Limit on how much of a service you can use |

---

### Q7. What are the SAP BTP runtimes? When do you use each?

**A:**

| Runtime | Description | Best For | Language |
|---------|-------------|---------|----------|
| **Cloud Foundry (CF)** | PaaS; push code and SAP handles OS, runtime | Web apps, APIs, microservices | Node.js, Python, Java, .NET |
| **Kyma** | Kubernetes-based; run Docker containers | Containerized apps, event-driven | Any language via Docker |
| **ABAP** | Classic SAP language runtime | Extend SAP-native ABAP systems | ABAP |
| **SAP Build** | Low-code/no-code | Business apps, automation, portals | No coding required |

**Cloud Foundry vs Kyma:**
- **Cloud Foundry:** Push code directly → buildpack handles containerization → simpler to use.
- **Kyma:** Push Docker images → full Kubernetes capabilities → more control and flexibility.

---

### Q8. What is the SAP BTP Cockpit?

**A:** The **SAP BTP Cockpit** is the web-based administration console for managing all BTP resources.

**What you can do:**
- View and manage subaccounts, spaces, and directories.
- Assign entitlements and quotas to subaccounts.
- Create and configure service instances.
- Manage users and roles.
- View deployed applications and their status.
- Access logs and monitoring.

**URL:** `https://cockpit.btp.cloud.sap/`

---

### Q9. What are service plans in SAP BTP?

**A:** Most SAP BTP services have multiple **service plans** offering different capabilities and pricing tiers.

**Example — SAP AI Core plans:**

| Plan | Description | Use Case |
|------|-------------|---------|
| **Free** | Limited; community support | Learning, prototyping |
| **Standard** | Full capabilities; standard support | Development and production |
| **Extended** | GPU training, more resources | Heavy ML training workloads |

**Service Instance vs Service Binding:**
```
Service Instance:  Create a service (like provisioning a database)
Service Binding:   Bind the service to your app (provides credentials)

cf create-service ai-core standard my-ai-core
cf bind-service my-app my-ai-core
# App now has credentials in VCAP_SERVICES environment variable
```

---

## 🔹 Section 3 — SAP Cloud Strategy

### Q10. What is RISE with SAP?

**A:** **RISE with SAP** is SAP's bundled transformation package — a single subscription that gives enterprises everything they need to move to the cloud and run their business.

**What's included:**

| Component | Description |
|-----------|-------------|
| **SAP S/4HANA Cloud** | The ERP in the cloud |
| **SAP BTP** | Platform for extensions, integration, AI |
| **SAP Business Network Starter Pack** | Supplier collaboration |
| **SAP Business Process Intelligence** | Process mining and optimization |
| **Tools & Methodology** | Migration tools, best practices |

**Why SAP created RISE:**
- Enterprises were overwhelmed by the complexity of moving to cloud.
- RISE simplifies: One contract, one vendor, end-to-end support.
- SAP becomes responsible for outcomes, not just software.

**GROW with SAP:** For smaller companies (new to SAP), using pre-configured SAP S/4HANA Cloud Public Edition.

---

### Q11. What is the "clean core" strategy?

**A:** **Clean core** is SAP's architectural principle: **keep the SAP core system standard and unmodified; all customizations and extensions go to SAP BTP**.

**Traditional approach (dirty core):**
```
SAP ECC
├── Core code: Modified ← ❌ Makes upgrades painful
├── Custom reports: Embedded
└── Integrations: Direct DB access to HANA
```

**Clean core approach:**
```
SAP S/4HANA (untouched)
    ↕ APIs / OData
SAP BTP (all customizations here)
├── Custom apps (CAP, Build Apps)
├── Extensions (side-by-side extensions)
├── Integrations (Integration Suite)
└── AI (AI Core, GenAI Hub)
```

**Benefits of clean core:**
- Upgrades to new SAP versions are easy (no custom code in core to migrate).
- SAP handles performance and security of the core.
- BTP extensions can be updated independently.
- Future-proof architecture.

---

### Q12. What is SAP's partner ecosystem?

**A:** SAP has a vast partner ecosystem:

| Partner Type | Role | Examples |
|-------------|------|---------|
| **SIs (System Integrators)** | Implement SAP projects | Accenture, Deloitte, IBM, Infosys |
| **ISVs (Independent Software Vendors)** | Build apps that extend SAP | Blackline, Vertex |
| **Technology Partners** | Integrate their tech with SAP | Microsoft, Google, Amazon |
| **Hosting Partners** | Host SAP on their infrastructure | HCL, T-Systems |

**Accenture** is one of SAP's largest system integrator partners — hence why you're in this training!

---

## 🔹 Section 4 — SAP Fiori & User Experience

### Q13. What is SAP Fiori? What are its design principles?

**A:** **SAP Fiori** is SAP's UX strategy and design system for modern, role-based, and responsive SAP applications.

**5 Design Principles:**

| Principle | Meaning |
|-----------|---------|
| **Role-based** | Each persona sees only what's relevant to them |
| **Responsive** | Works on desktop, tablet, and mobile |
| **Coherent** | Consistent design language across all SAP apps |
| **Simple** | 3-click principle — accomplish any task in 3 clicks or fewer |
| **Delightful** | Modern, intuitive, pleasant to use |

**Technology stack:**
- **SAPUI5** — JavaScript framework by SAP for enterprise-grade web UIs.
- **SAP Fiori Elements** — Generate Fiori apps from CAP annotations automatically.
- **SAP Build Apps** — Low-code Fiori app development.

---

### Q14. What is SAPUI5?

**A:** **SAPUI5** is SAP's open-source JavaScript UI framework for building enterprise web applications.

- Based on HTML5, CSS3, JavaScript (ES6+).
- Implements SAP Fiori design.
- 400+ UI controls (tables, charts, forms, inputs).
- MVC architecture.
- OData integration built-in.
- **OpenUI5** is the open-source version (SAPUI5 = OpenUI5 + additional enterprise controls).

---

### Q15. What is an SAP role? Why is role-based access important?

**A:** An **SAP role** is a collection of authorizations (permissions) that define what a user can see and do.

```
Role: "HR Manager"
├── Authorization: View all employee salaries
├── Authorization: Approve leave requests
├── Authorization: Run HR reports
└── Authorization: Access org chart

Role: "Employee"
├── Authorization: View own salary only
├── Authorization: Submit leave request
└── Authorization: View own org hierarchy only
```

**Why it matters for AI/Joule:**
- Joule inherits the user's SAP roles.
- An employee asking Joule "Show me all salaries" gets only their own — role-based filtering.
- AI must respect business authorization — not a loophole around SAP security.

---

## 🔹 Section 5 — Quick Fire Questions

### Q16. What is the difference between SAP Business One, SAP B1, and SAP S/4HANA?

**A:**
- **SAP Business One (B1)** — SAP's ERP for small businesses (< 50 users). Simpler, affordable.
- **SAP S/4HANA** — SAP's flagship ERP for large enterprises. Full capabilities, runs on HANA.
- **SAP Business ByDesign** — Mid-market cloud ERP. Between B1 and S/4HANA.

---

### Q17. What is an SAP transaction code (T-code)?

**A:** A **T-code** is a 2-8 character shortcut to navigate directly to a specific function in SAP GUI.

| T-code | What It Opens |
|--------|--------------|
| `MM01` | Create Material Master |
| `FB60` | Post Vendor Invoice |
| `SE38` | ABAP Editor |
| `ST05` | SQL Trace |
| `SM50` | Work Process Overview |

T-codes are for SAP GUI (legacy). In SAP Fiori, you navigate using apps and tiles instead.

---

### Q18. What is ABAP?

**A:** **ABAP (Advanced Business Application Programming)** is SAP's proprietary programming language for extending and customizing SAP systems.

- Created in the 1980s specifically for SAP.
- Strongly typed, compiled language that runs on the ABAP runtime.
- Used for: Custom reports, enhancements, BAPIs, IDocs, data migration.
- **ABAP on BTP:** Modern ABAP development uses RESTful ABAP Programming (RAP) model.

**ABAP vs Python (in the context of this training):**
- **ABAP** → For SAP-core customizations and standard SAP extensions.
- **Python** → For data engineering, ML, and custom BTP applications.

---

### Q19. What is a BTP service key?

**A:** A **service key** provides credentials to access a BTP service from OUTSIDE of BTP (e.g., from your local machine or a non-CF application).

```bash
# Create a service key for AI Core:
cf create-service-key my-ai-core my-ai-core-key

# View the credentials (URL, client_id, client_secret):
cf service-key my-ai-core my-ai-core-key
# Returns JSON with: url, clientid, clientsecret, tokenurl

# Use these credentials in your code to call AI Core API
```

---

### Q20. What is the difference between On-Premise and Cloud SAP deployments?

**A:**

| Aspect | On-Premise | Cloud (SAP BTP) |
|--------|-----------|----------------|
| **Infrastructure** | Customer manages servers | SAP manages infrastructure |
| **Upgrades** | Customer's responsibility | SAP handles automatically |
| **Customization** | Full control | "Clean core" — via BTP extensions |
| **Cost model** | CapEx (large upfront) | OpEx (subscription) |
| **Scalability** | Manual; hardware-limited | Elastic; scale in minutes |
| **Data location** | On customer premises | SAP's data centers (GDPR regions) |
| **AI/ML** | Requires additional tools | Built-in via BTP services |

---

> **💡 Viva Tip:** For SAP Overview questions, the evaluator wants to see you understand WHY SAP matters in enterprise context, not just definitions. Connect SAP concepts to your project: "Our hackathon built a RAG system; in a production SAP environment, this would be deployed on SAP BTP, use HANA Cloud Vector Engine, and integrate with Joule."

---

*End of Unit 16 — SAP Overview 🏢*
