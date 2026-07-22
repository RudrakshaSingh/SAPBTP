"""One resume, three job descriptions -- the test set from section 10, task 7.

The same candidate is screened against an SAP BTP AI role, a Data Engineer role
and an SAP ABAP role. The resume never changes, so any difference in the score is
produced entirely by the job description, which is the point of the exercise.
"""

SAMPLE_RESUME = """
Prem Pratik
Senior SAP Consultant | 6 years of experience

Skills: SAP BTP, SAP HANA Cloud, Python, LangChain, LangGraph, RAG, GraphRAG,
SAP AI Core, SAP Generative AI Hub, CAP applications, SAP Build Process Automation,
prompt engineering, REST APIs, OData, SQL.

Projects:
- SAP GenAI Hub project: built a support automation agent on SAP AI Core and the
  Generative AI Hub that classifies incoming SAP incidents and drafts responses.
- GraphRAG project: knowledge graph over SAP documentation, queried through a
  LangChain retrieval pipeline for a code evaluation assistant.
- CAP service on SAP BTP exposing OData endpoints backed by SAP HANA Cloud.

Certifications: SAP Certified Associate - Business AI.
"""

JOB_DESCRIPTIONS = [
    (
        "SAP BTP AI Consultant",
        """
        We are hiring an SAP BTP AI Consultant with experience in SAP BTP, SAP AI Core,
        Joule, SAP Generative AI Hub, CAP, Integration Suite, HANA Cloud, and enterprise
        AI solution architecture. The candidate should understand GenAI, prompt
        engineering, RAG, and agentic AI workflows. Nice to have: LangChain, LangGraph,
        vector databases, and SAP Build Process Automation. 6+ years of experience.
        """,
    ),
    (
        "Data Engineer",
        """
        We are looking for a Data Engineer with strong Apache Spark, Apache Airflow, SQL,
        Python, ETL pipeline design, data modelling, Docker and Kubernetes experience.
        You will own batch and streaming pipelines on a cloud data platform and manage
        warehouse performance. Nice to have: dbt and Kafka. 4+ years of experience.
        """,
    ),
    (
        "SAP ABAP Developer",
        """
        We need an SAP ABAP Developer with deep ABAP, ABAP Cloud, RAP, S/4HANA, Fiori and
        OData experience. Responsibilities include building RAP business objects, custom
        Fiori applications, and clean-core extensions on S/4HANA. Nice to have: SAP BTP
        and CAP. 5+ years of experience.
        """,
    ),
]
