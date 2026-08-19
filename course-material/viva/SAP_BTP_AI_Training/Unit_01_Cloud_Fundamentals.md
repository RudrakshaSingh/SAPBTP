# ☁️ Unit 1 — Cloud Fundamentals

> **Module**: Module 1 — Cloud  
> **Duration**: Day 1 (8 hours)  
> **Date**: 29-Jun-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — What is Cloud Computing?

### Q1. What is cloud computing? Define it in simple terms.

**A:** **Cloud computing** is the delivery of computing services — servers, storage, databases, networking, software, analytics, and intelligence — **over the internet ("the cloud")** on a pay-as-you-go basis.

Instead of owning and maintaining physical servers and data centers, you **rent** computing resources from a cloud provider (like AWS, Azure, GCP, or SAP BTP) and access them on demand.

**Simple analogy:** Electricity — you don't build a power plant at home; you plug into the grid and pay for what you use. Cloud computing does the same for IT infrastructure.

---

### Q2. What are the key characteristics of cloud computing?

**A:** The **5 essential characteristics** (defined by NIST — National Institute of Standards and Technology):

| Characteristic | Meaning | Example |
|----------------|---------|---------|
| **On-demand self-service** | Get resources instantly without human intervention | Spin up a VM in 30 seconds via a portal |
| **Broad network access** | Accessible from any device over the internet | Access your app from laptop, phone, tablet |
| **Resource pooling** | Provider's resources are shared across multiple tenants | Multiple companies use the same physical servers |
| **Rapid elasticity** | Scale up/down automatically based on demand | Auto-scaling during a flash sale |
| **Measured service** | Pay only for what you use; usage is metered | Billed per GB of storage, per hour of compute |

---

### Q3. What are the benefits of cloud computing over traditional on-premises infrastructure?

**A:**

| Aspect | On-Premises | Cloud |
|--------|-------------|-------|
| **Capital cost** | High (buy servers, build data center) | Low (no upfront hardware cost) |
| **Operational cost** | Fixed (pay even when idle) | Variable (pay-per-use) |
| **Scalability** | Weeks/months to add capacity | Minutes to scale up/down |
| **Maintenance** | You manage everything | Provider handles hardware |
| **Availability** | Single location risk | Multi-region redundancy |
| **Speed to deploy** | Slow (procurement, setup) | Fast (click and deploy) |
| **Innovation** | Limited by your hardware | Access to AI, ML, IoT services instantly |

**Key business benefit:** Converts **CapEx (Capital Expenditure)** to **OpEx (Operational Expenditure)** — no large upfront investment needed.

---

### Q4. What are some disadvantages or risks of cloud computing?

**A:**
1. **Vendor lock-in** — Migrating between cloud providers is difficult; proprietary services don't transfer easily.
2. **Internet dependency** — No internet = no access to cloud services.
3. **Security concerns** — Data is stored on someone else's servers; compliance and data sovereignty issues.
4. **Latency** — Remote servers may have higher latency than local on-premises servers.
5. **Cost unpredictability** — Pay-per-use can lead to unexpected bills if usage spikes.
6. **Limited control** — You can't customize the underlying hardware or network in shared environments.
7. **Downtime risk** — Even major providers have outages (AWS, Azure have had multi-hour outages).

---

## 🔹 Section 2 — Cloud Service Models (IaaS, PaaS, SaaS)

### Q5. What are the three main cloud service models? Explain each.

**A:**

| Model | Full Form | What You Manage | What Provider Manages | Example |
|-------|-----------|-----------------|----------------------|---------|
| **IaaS** | Infrastructure as a Service | OS, middleware, apps, data | Servers, storage, networking, virtualization | AWS EC2, Azure VMs, Google Compute Engine |
| **PaaS** | Platform as a Service | Apps, data | OS, middleware, runtime, servers, storage | SAP BTP, Heroku, Google App Engine, Azure App Service |
| **SaaS** | Software as a Service | Nothing (just use it) | Everything | Gmail, Salesforce, SAP S/4HANA Cloud, Microsoft 365 |

**Analogy — Pizza:**
- **IaaS** = You get the kitchen, oven, and ingredients → you make the pizza yourself.
- **PaaS** = You get the kitchen with pre-made dough → you just add toppings and bake.
- **SaaS** = Pizza is delivered to your door → you just eat it.

---

### Q6. What is IaaS? When would you use it?

**A:** **IaaS (Infrastructure as a Service)** provides virtualized computing resources over the internet. You get raw infrastructure — virtual machines, storage, and networking — and you manage everything on top.

**When to use IaaS:**
- You need **full control** over the OS and software stack.
- Running **legacy applications** that can't be containerized.
- **Custom networking** requirements (VPNs, firewalls, load balancers).
- **Development and testing** environments that need to be quickly set up and torn down.

**Examples:** AWS EC2, Azure Virtual Machines, Google Compute Engine.

**You manage:** OS, patches, middleware, runtime, applications, data.
**Provider manages:** Physical servers, networking hardware, data center, virtualization layer.

---

### Q7. What is PaaS? Why is SAP BTP considered PaaS?

**A:** **PaaS (Platform as a Service)** provides a complete development and deployment platform. You focus only on writing code and managing data — the platform handles infrastructure, OS, middleware, and runtime.

**SAP BTP (Business Technology Platform) is PaaS because:**
- It provides a **ready-made platform** for building SAP extensions and custom apps.
- Developers don't manage servers, OS, or middleware.
- It includes built-in services: **HANA Cloud** (database), **AI Core** (ML), **Integration Suite**, etc.
- You deploy applications and SAP handles scaling, patching, and availability.
- It supports multiple runtimes: **Cloud Foundry**, **Kyma (Kubernetes)**, and **ABAP environment**.

**Other PaaS examples:** Heroku, Google App Engine, Azure App Service.

---

### Q8. What is SaaS? Give examples relevant to SAP.

**A:** **SaaS (Software as a Service)** delivers fully functional software over the internet. You just use the application — no installation, no maintenance.

**SAP SaaS examples:**

| Product | What It Does |
|---------|-------------|
| **SAP S/4HANA Cloud** | ERP — finance, logistics, manufacturing |
| **SAP SuccessFactors** | Human Capital Management (HCM) |
| **SAP Ariba** | Procurement and supply chain |
| **SAP Concur** | Travel and expense management |
| **SAP Analytics Cloud** | Business intelligence and planning |

**Key SaaS characteristics:**
- Accessed via a web browser.
- Subscription-based pricing (monthly/annual).
- Automatic updates — you always have the latest version.
- Multi-tenant — many customers share the same application instance.

---

### Q9. What is the shared responsibility model in cloud computing?

**A:** The **shared responsibility model** defines what the **cloud provider** manages vs. what the **customer** manages. Responsibilities shift depending on the service model:

```
                    IaaS        PaaS        SaaS
─────────────────────────────────────────────────
Data              Customer    Customer    Customer
Applications      Customer    Customer    Provider
Runtime           Customer    Provider    Provider
Middleware        Customer    Provider    Provider
OS                Customer    Provider    Provider
Virtualization    Provider    Provider    Provider
Servers           Provider    Provider    Provider
Storage           Provider    Provider    Provider
Networking        Provider    Provider    Provider
─────────────────────────────────────────────────
```

**Key takeaway:** In **SaaS**, you're only responsible for your data and user access. In **IaaS**, you manage almost everything except the physical hardware.

---

### Q10. What is the difference between XaaS, FaaS, and BaaS?

**A:**

| Model | Full Form | What It Is | Example |
|-------|-----------|-----------|---------|
| **XaaS** | Everything as a Service | Umbrella term for any cloud service | All of the below |
| **FaaS** | Function as a Service | Run individual functions without managing servers (serverless) | AWS Lambda, Azure Functions, Google Cloud Functions |
| **BaaS** | Backend as a Service | Pre-built backend features (auth, DB, push notifications) | Firebase, AWS Amplify |
| **DaaS** | Database as a Service | Managed database in the cloud | SAP HANA Cloud, Amazon RDS, Azure SQL |
| **AIaaS** | AI as a Service | Pre-built AI/ML capabilities | SAP AI Core, AWS SageMaker, Azure AI |

**FaaS (Serverless) is notable:** You write a function, upload it, and it runs only when triggered. You pay only for the execution time (milliseconds). No server management at all.

---

## 🔹 Section 3 — Cloud Deployment Models

### Q11. What are the four cloud deployment models?

**A:**

| Model | Description | Who Uses It | Example |
|-------|-------------|-------------|---------|
| **Public Cloud** | Resources owned and operated by a third-party provider, shared across many organizations | Startups, SMBs, anyone wanting low-cost scalability | AWS, Azure, GCP, SAP BTP |
| **Private Cloud** | Cloud infrastructure exclusively for one organization (on-premises or hosted) | Banks, government, healthcare (strict compliance) | VMware vSphere, OpenStack, SAP Private Cloud |
| **Hybrid Cloud** | Combination of public and private clouds with data/app portability | Enterprises transitioning to cloud | Azure Arc, AWS Outposts |
| **Community Cloud** | Shared infrastructure for organizations with common concerns (e.g., regulations) | Healthcare consortiums, government agencies | GovCloud (AWS), healthcare-specific clouds |

---

### Q12. What is a hybrid cloud? Why do enterprises prefer it?

**A:** A **hybrid cloud** combines **private cloud (or on-premises)** with **public cloud**, allowing data and applications to move between them.

**Why enterprises prefer it:**
1. **Keep sensitive data on-premises** — financial records, patient data stay in private cloud for compliance.
2. **Burst to public cloud** — handle traffic spikes using public cloud capacity (cloud bursting).
3. **Gradual migration** — move workloads to cloud incrementally, not all at once.
4. **Best of both worlds** — private cloud for control + public cloud for scalability.

**SAP hybrid cloud example:** An enterprise runs **SAP S/4HANA on-premises** but uses **SAP BTP (public cloud)** for extensions, AI services, and integrations. SAP Integration Suite connects the two.

---

### Q13. What is multi-cloud? How is it different from hybrid cloud?

**A:**

| Aspect | Hybrid Cloud | Multi-Cloud |
|--------|-------------|-------------|
| **Definition** | Mix of private + public cloud | Using multiple public cloud providers |
| **Goal** | Keep some workloads private | Avoid vendor lock-in, use best services |
| **Example** | On-premises SAP + SAP BTP | AWS for compute + GCP for AI + Azure for Office 365 |
| **Complexity** | Medium | High (managing multiple providers) |

**Why multi-cloud:**
- **Avoid vendor lock-in** — don't depend on a single provider.
- **Best-of-breed** — use AWS for compute, GCP for BigQuery/AI, Azure for enterprise integrations.
- **Resilience** — if one provider goes down, others can take over.
- **Compliance** — some data must stay in specific regions/providers.

---

## 🔹 Section 4 — Virtualization & Containers

### Q14. What is virtualization? Why is it foundational to cloud computing?

**A:** **Virtualization** is the technology that creates **virtual versions** of physical hardware — allowing multiple virtual machines (VMs) to run on a single physical server.

**How it works:**
```
Physical Server
  └── Hypervisor (VMware, Hyper-V, KVM)
       ├── VM 1 (Ubuntu + App A)
       ├── VM 2 (Windows + App B)
       └── VM 3 (CentOS + App C)
```

**Why it's foundational to cloud:**
- **Resource efficiency** — One physical server can host 10-50 VMs. No wasted capacity.
- **Isolation** — Each VM is independent; if one crashes, others are unaffected.
- **Rapid provisioning** — Spin up a new VM in seconds vs. weeks for physical hardware.
- **Multi-tenancy** — Cloud providers use virtualization to serve thousands of customers on shared hardware.

Without virtualization, cloud computing would not be economically viable.

---

### Q15. What is a hypervisor? What are Type 1 and Type 2 hypervisors?

**A:** A **hypervisor** is software that creates and manages virtual machines. It sits between the physical hardware and the VMs.

| Type | Also Called | Runs On | Performance | Example |
|------|-----------|---------|-------------|---------|
| **Type 1** | Bare-metal | Directly on hardware | High (no host OS overhead) | VMware ESXi, Microsoft Hyper-V, KVM, Xen |
| **Type 2** | Hosted | On top of a host OS | Lower (extra OS layer) | VirtualBox, VMware Workstation, Parallels |

**Cloud providers use Type 1 hypervisors** because they need maximum performance and direct hardware access. AWS uses a custom hypervisor called **Nitro**, GCP uses **KVM**.

---

### Q16. What are containers? How are they different from VMs?

**A:** **Containers** are lightweight, standalone packages that include an application and all its dependencies but **share the host OS kernel**.

| Aspect | Virtual Machine | Container |
|--------|----------------|-----------|
| **Size** | Gigabytes (includes full OS) | Megabytes (just app + dependencies) |
| **Boot time** | Minutes | Seconds |
| **Isolation** | Full (separate OS per VM) | Process-level (shares host kernel) |
| **Resource usage** | Heavy (each VM has its own OS) | Light (shared OS) |
| **Portability** | Moderate | High (runs anywhere with container runtime) |
| **Use case** | Running different OS on same hardware | Microservices, CI/CD, scalable apps |
| **Example** | VMware, VirtualBox | Docker, Podman |

**Analogy:**
- **VM** = A house (full infrastructure, separate utilities for each).
- **Container** = An apartment (shared building infrastructure, isolated living space).

---

### Q17. What is Docker? What is a Docker image vs. a Docker container?

**A:** **Docker** is the most popular platform for building, shipping, and running containers.

| Concept | What It Is | Analogy |
|---------|-----------|---------|
| **Docker Image** | A read-only template with app code, dependencies, and config | A recipe/blueprint |
| **Docker Container** | A running instance of an image | A dish made from the recipe |
| **Dockerfile** | A text file with instructions to build an image | The recipe steps |
| **Docker Hub** | A registry to share/download images | A cookbook library |

```dockerfile
# Example Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key commands:**
```bash
docker build -t myapp .          # Build image from Dockerfile
docker run -p 8000:8000 myapp    # Run container from image
docker ps                         # List running containers
docker stop <container_id>        # Stop a container
```

---

### Q18. What is Kubernetes? Why is it needed?

**A:** **Kubernetes (K8s)** is an open-source **container orchestration** platform. It manages the deployment, scaling, and operations of containerized applications.

**Why it's needed:** Docker runs containers, but in production you might have **hundreds or thousands** of containers. Kubernetes handles:

| Feature | What Kubernetes Does |
|---------|---------------------|
| **Auto-scaling** | Adds/removes containers based on load |
| **Self-healing** | Restarts crashed containers automatically |
| **Load balancing** | Distributes traffic across containers |
| **Rolling updates** | Updates apps without downtime |
| **Service discovery** | Containers find each other automatically |
| **Secret management** | Securely stores passwords, API keys |

**SAP context:** SAP BTP offers the **Kyma runtime**, which is a managed Kubernetes environment for deploying containerized SAP extensions.

---

## 🔹 Section 5 — Cloud Providers & SAP BTP

### Q19. Name the major cloud providers and their key services.

**A:**

| Provider | Compute | Database | AI/ML | Serverless | Market Share |
|----------|---------|----------|-------|------------|-------------|
| **AWS** (Amazon) | EC2 | RDS, DynamoDB | SageMaker | Lambda | ~31% |
| **Azure** (Microsoft) | Virtual Machines | Azure SQL, Cosmos DB | Azure AI | Azure Functions | ~25% |
| **GCP** (Google) | Compute Engine | Cloud SQL, BigQuery | Vertex AI | Cloud Functions | ~11% |
| **SAP BTP** | Cloud Foundry, Kyma | HANA Cloud | AI Core, GenAI Hub | — | SAP ecosystem |

**SAP BTP is unique** because it's not a general-purpose cloud — it's specifically designed for **extending and integrating SAP applications**.

---

### Q20. What is SAP BTP? What are its key pillars?

**A:** **SAP BTP (Business Technology Platform)** is SAP's PaaS offering that provides tools and services for building, integrating, and extending SAP applications.

**Four key pillars:**

| Pillar | What It Does | Key Services |
|--------|-------------|-------------|
| **Database & Data Management** | Store and manage data | SAP HANA Cloud, Data Intelligence |
| **Analytics** | Business intelligence and planning | SAP Analytics Cloud |
| **Application Development** | Build custom apps and extensions | SAP Build, Cloud Foundry, Kyma, CAPM |
| **Integration** | Connect SAP and non-SAP systems | Integration Suite, API Management |
| **AI** | AI and ML capabilities | SAP AI Core, AI Launchpad, GenAI Hub |

**Why BTP matters:** Most enterprises run SAP for core business processes. BTP lets them extend SAP without modifying the core system — following the **"clean core"** principle.

---

### Q21. What are Cloud Foundry and Kyma in SAP BTP?

**A:** These are two **runtime environments** in SAP BTP for deploying applications:

| Aspect | Cloud Foundry | Kyma |
|--------|--------------|------|
| **Type** | PaaS runtime | Kubernetes-based runtime |
| **Best for** | Traditional web apps, microservices | Container-based, event-driven apps |
| **Language support** | Java, Node.js, Python, Go | Any (via Docker containers) |
| **Deployment** | `cf push` | Kubernetes YAML manifests / Helm charts |
| **Scaling** | Managed by platform | Kubernetes auto-scaling |
| **Complexity** | Lower (simpler abstraction) | Higher (Kubernetes knowledge needed) |
| **Extensions** | Simple SAP extensions | Complex, event-driven extensions |

**When to use which:**
- **Cloud Foundry** — Simple REST API, business logic extension, quick prototypes.
- **Kyma** — Event-driven processing, complex microservices, need full container control.

---

### Q22. What are cloud regions and availability zones?

**A:**

| Concept | Definition | Example |
|---------|-----------|---------|
| **Region** | A geographic area with multiple data centers | US East (Virginia), EU (Frankfurt), AP (Singapore) |
| **Availability Zone (AZ)** | An isolated data center within a region | us-east-1a, us-east-1b, us-east-1c |

**Why they matter:**
- **Latency** — Deploy close to your users for faster response times.
- **Data sovereignty** — Some regulations require data to stay in specific countries (GDPR = EU).
- **High availability** — Deploy across multiple AZs so if one data center fails, others take over.

**SAP BTP regions:** Available in multiple regions (EU10-Frankfurt, US10-US East, AP10-Australia, etc.). When creating a BTP subaccount, you choose a region.

---

## 🔹 Section 6 — Cloud-Native Concepts

### Q23. What does "cloud-native" mean?

**A:** **Cloud-native** is an approach to building applications that fully exploit cloud computing advantages. Cloud-native apps are:

1. **Containerized** — Packaged in containers for portability.
2. **Microservices-based** — Broken into small, independent services.
3. **Dynamically orchestrated** — Managed by Kubernetes or similar.
4. **DevOps-driven** — Continuous integration/deployment (CI/CD).

**Cloud-native ≠ "runs in the cloud":**
- A legacy app running on a cloud VM is **cloud-hosted**, not cloud-native.
- A cloud-native app is **designed from the ground up** for the cloud.

**12-Factor App principles** guide cloud-native development (codebase, dependencies, config, backing services, build/release/run, processes, port binding, concurrency, disposability, dev/prod parity, logs, admin processes).

---

### Q24. What are microservices? How do they differ from monolithic architecture?

**A:**

| Aspect | Monolithic | Microservices |
|--------|-----------|---------------|
| **Structure** | Single large application | Multiple small, independent services |
| **Deployment** | Deploy everything together | Deploy each service independently |
| **Scaling** | Scale the entire app | Scale only the services that need it |
| **Technology** | One tech stack for everything | Each service can use different tech |
| **Failure impact** | One bug can crash everything | One service failure doesn't affect others |
| **Team structure** | One large team | Small teams own individual services |
| **Communication** | Function calls | APIs (REST, gRPC, message queues) |

**Example:** An e-commerce app:
- **Monolith:** One app handles users, orders, payments, inventory.
- **Microservices:** Separate services for users, orders, payments, inventory — each with its own database and API.

---

### Q25. What is serverless computing?

**A:** **Serverless** means you run code without provisioning or managing servers. The cloud provider automatically handles infrastructure, scaling, and availability.

**Key characteristics:**
- **No server management** — you just upload code.
- **Event-driven** — functions run in response to triggers (HTTP request, file upload, timer).
- **Auto-scaling** — scales from 0 to thousands of instances automatically.
- **Pay-per-execution** — billed for actual execution time (often in milliseconds).
- **Stateless** — each invocation is independent.

**Serverless ≠ "no servers"** — servers exist, but you don't manage them.

| Provider | Serverless Service |
|----------|-------------------|
| AWS | Lambda |
| Azure | Azure Functions |
| GCP | Cloud Functions |
| SAP | SAP BTP Serverless Runtime (deprecated) → Kyma Functions |

---

### Q26. What is a CDN (Content Delivery Network)?

**A:** A **CDN** is a globally distributed network of servers that caches and delivers content (images, CSS, JS, videos) from the server **closest to the user**.

**How it works:**
```
User in India → CDN node in Mumbai (cached copy) → Fast response
Instead of:
User in India → Origin server in US East → Slow response
```

**Benefits:**
- **Faster load times** — content served from nearby edge servers.
- **Reduced server load** — origin server handles fewer requests.
- **DDoS protection** — CDN absorbs traffic spikes.
- **Global availability** — content available worldwide.

**Examples:** Cloudflare, AWS CloudFront, Azure CDN, Akamai.

---

### Q27. What is auto-scaling? Explain horizontal vs. vertical scaling.

**A:**

| Scaling Type | What It Does | Analogy | Limitation |
|-------------|-------------|---------|------------|
| **Vertical Scaling (Scale Up)** | Add more power to existing server (more CPU, RAM) | Get a bigger desk | Hardware limits; single point of failure |
| **Horizontal Scaling (Scale Out)** | Add more servers/instances | Get more desks | Need load balancer; app must be stateless |

**Auto-scaling** = The system automatically adds or removes instances based on metrics (CPU usage, request count, queue length).

```
Low traffic:   [Server 1]
Peak traffic:  [Server 1] [Server 2] [Server 3] [Server 4]
After peak:    [Server 1] [Server 2]  ← scales back down
```

**Cloud-native apps prefer horizontal scaling** because it's more resilient (no single point of failure) and theoretically unlimited.

---

## 🔹 Section 7 — Cloud Security & Economics

### Q28. What are the main cloud security concerns and how are they addressed?

**A:**

| Concern | Risk | Solution |
|---------|------|----------|
| **Data breach** | Unauthorized access to data | Encryption at rest + in transit, IAM policies |
| **Identity theft** | Compromised credentials | Multi-factor authentication (MFA), SSO |
| **Insecure APIs** | API vulnerabilities exploited | API gateways, rate limiting, OAuth/JWT |
| **Data loss** | Accidental deletion, corruption | Automated backups, geo-replication |
| **Compliance** | Violating GDPR, HIPAA, etc. | Region-specific deployment, audit logs |
| **DDoS attacks** | Service overwhelmed by traffic | CDN, WAF (Web Application Firewall), auto-scaling |

**Encryption types:**
- **At rest** — Data stored on disk is encrypted (AES-256).
- **In transit** — Data moving over network is encrypted (TLS/SSL).
- **In use** — Confidential computing (data encrypted even while being processed).

---

### Q29. What is IAM (Identity and Access Management)?

**A:** **IAM** controls **who** (identity) can do **what** (access) on **which** resources.

**Core concepts:**

| Concept | Meaning | Example |
|---------|---------|---------|
| **User** | An individual identity | developer@company.com |
| **Group** | Collection of users | "Developers" group |
| **Role** | Set of permissions | "ReadOnly", "Admin", "DeployOnly" |
| **Policy** | Rules defining allowed/denied actions | "Allow read access to S3 bucket X" |
| **Principle of Least Privilege** | Give minimum permissions needed | Developer can deploy but not delete databases |

**SAP BTP context:** Uses **SAP Authorization and Trust Management (XSUAA)** for IAM. Roles and role collections control access to BTP services and applications.

---

### Q30. Explain cloud pricing models.

**A:**

| Model | How It Works | Best For | Example |
|-------|-------------|----------|---------|
| **Pay-as-you-go** | Pay for actual usage (per hour, per GB, per request) | Variable/unpredictable workloads | AWS EC2 on-demand, BTP service consumption |
| **Reserved Instances** | Commit to 1-3 years for discounted rate (up to 72% off) | Predictable, steady workloads | AWS Reserved Instances, Azure Reserved VMs |
| **Spot/Preemptible** | Use spare capacity at huge discount; can be interrupted | Batch processing, fault-tolerant workloads | AWS Spot Instances (up to 90% off) |
| **Free Tier** | Limited free usage for learning/prototyping | Students, startups, POCs | AWS Free Tier, SAP BTP Free Tier |
| **Subscription** | Fixed monthly/annual fee | SaaS applications | SAP SuccessFactors, Microsoft 365 |

**SAP BTP pricing:** Uses **Cloud Credits** — you purchase credits and consume services against them. Different services have different consumption rates.

---

### Q31. What is the difference between CapEx and OpEx in cloud?

**A:**

| Aspect | CapEx (Capital Expenditure) | OpEx (Operational Expenditure) |
|--------|-----------------------------|-------------------------------|
| **What** | Upfront investment in physical assets | Ongoing expenses for services |
| **Cloud model** | On-premises (buy servers) | Cloud (pay-per-use) |
| **Accounting** | Depreciated over years | Expensed monthly |
| **Flexibility** | Low (stuck with purchased hardware) | High (scale up/down anytime) |
| **Risk** | High (hardware may become obsolete) | Low (always using latest tech) |

**Cloud computing shifts CapEx to OpEx** — instead of buying a $100,000 server, you pay $500/month for equivalent cloud resources. This is especially beneficial for startups that can't afford large upfront investments.

---

## 🔹 Section 8 — Quick-Fire Conceptual Questions

### Q32. What is an SLA (Service Level Agreement)?

**A:** An **SLA** is a formal agreement between a cloud provider and customer that defines **guaranteed service levels** — usually uptime percentage.

| Uptime % | Downtime per Year | Downtime per Month |
|----------|--------------------|---------------------|
| 99% | 3.65 days | 7.3 hours |
| 99.9% ("three nines") | 8.76 hours | 43.8 minutes |
| 99.99% ("four nines") | 52.6 minutes | 4.38 minutes |
| 99.999% ("five nines") | 5.26 minutes | 26.3 seconds |

Most cloud services offer **99.9% to 99.99%** SLAs. If the provider fails to meet the SLA, customers get **service credits** (partial refunds).

---

### Q33. What is latency vs. bandwidth vs. throughput?

**A:**

| Term | Definition | Analogy |
|------|-----------|---------|
| **Latency** | Time for data to travel from source to destination | How long it takes a car to travel from A to B |
| **Bandwidth** | Maximum data transfer capacity of a connection | How many lanes the highway has |
| **Throughput** | Actual data transfer rate achieved | How many cars actually pass per hour |

**In cloud context:**
- **Low latency** is critical for real-time apps (gaming, video calls).
- **High bandwidth** matters for data-intensive workloads (big data, video streaming).
- **Throughput** may be lower than bandwidth due to congestion, packet loss, etc.

---

### Q34. What is a load balancer?

**A:** A **load balancer** distributes incoming network traffic across multiple servers to ensure no single server is overwhelmed.

**Types:**
- **Layer 4 (Transport)** — Routes based on IP and port (faster, simpler).
- **Layer 7 (Application)** — Routes based on URL, headers, cookies (smarter, more flexible).

```
Client requests → Load Balancer → Server 1 (30% traffic)
                                → Server 2 (30% traffic)
                                → Server 3 (40% traffic)
```

**Algorithms:**
- **Round Robin** — Distribute evenly in order.
- **Least Connections** — Send to server with fewest active connections.
- **Weighted** — Send more traffic to more powerful servers.
- **IP Hash** — Same client always goes to same server (session persistence).

---

### Q35. What is DNS? How does it relate to cloud?

**A:** **DNS (Domain Name System)** translates human-readable domain names (e.g., `www.sap.com`) into IP addresses (e.g., `194.39.131.34`) that computers use to route traffic.

**In cloud context:**
- Cloud providers offer managed DNS services (AWS Route 53, Azure DNS, Google Cloud DNS).
- DNS enables **geographic routing** — send users to the nearest cloud region.
- **DNS-based load balancing** — distribute traffic across multiple regions.
- **Custom domains** — map your domain to a cloud-deployed application.

```
User types "app.company.com"
  → DNS resolves to 52.23.186.5 (AWS EC2 instance in US-East)
  → Browser connects to that IP
```

---

### Q36. What is cloud migration? What are the 6 R's of migration?

**A:** **Cloud migration** is the process of moving applications, data, and workloads from on-premises to the cloud.

**The 6 R's (migration strategies):**

| Strategy | What It Means | When to Use |
|----------|--------------|-------------|
| **Rehost** (Lift & Shift) | Move as-is to cloud VMs | Quick migration, no code changes |
| **Replatform** (Lift & Reshape) | Minor optimizations while migrating | Use managed DB instead of self-managed |
| **Refactor** (Re-architect) | Redesign for cloud-native | Microservices, containers, serverless |
| **Repurchase** | Replace with SaaS product | Switch from on-prem CRM to Salesforce |
| **Retain** | Keep on-premises (for now) | Legacy systems not ready for cloud |
| **Retire** | Decommission the application | Unused or redundant applications |

**SAP context:** Many enterprises use **RISE with SAP** to migrate from on-premises SAP ECC to **SAP S/4HANA Cloud** — typically a replatform or refactor approach.

---

> **💡 Viva Tip:** Always connect cloud concepts back to **SAP BTP** — the evaluator wants to see you understand how cloud fundamentals apply to the SAP ecosystem specifically.

---

*End of Unit 1 — Cloud Fundamentals ☁️*
