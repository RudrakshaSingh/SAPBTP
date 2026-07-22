"""Generate the sample ``sap_incidents.xlsx`` dataset.

The first eight incidents (Excel rows 2-9) are exactly the rows given in the
problem statement, so INC-1006 lands on Excel row 7 as the expected output
requires. The remaining incidents extend the dataset so that comparison and
analytical questions have something to work with.

A few rows are intentionally messy -- a completely empty row, padded whitespace,
a missing root cause, a resolution time stored as text -- so that the cleaning
step in Task 2 has real work to do.

Run:
    python create_dataset.py
"""

from __future__ import annotations

import pandas as pd

COLUMNS = [
    "incident_id",
    "incident_date",
    "sap_module",
    "category",
    "priority",
    "issue_summary",
    "issue_description",
    "root_cause",
    "resolution",
    "owner_team",
    "resolution_time_hours",
    "status",
]

# --------------------------------------------------------------------------- #
# Rows 2-9: the eight incidents from the problem statement, verbatim.
# --------------------------------------------------------------------------- #
SAMPLE_ROWS = [
    {
        "incident_id": "INC-1001",
        "incident_date": "2024-01-12",
        "sap_module": "SAP MM",
        "category": "Invoice Management",
        "priority": "P2",
        "issue_summary": "Supplier invoice blocked because of price variance",
        "issue_description": (
            "The supplier invoice posted through MIRO was blocked for payment. "
            "The invoice value did not match the purchase-order value and the "
            "system raised a price-variance block, so the payment run skipped it."
        ),
        "root_cause": "Incorrect purchase-order condition record",
        "resolution": "Corrected condition record and reprocessed invoice",
        "owner_team": "Procure-to-Pay Support",
        "resolution_time_hours": 3.5,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1002",
        "incident_date": "2024-01-19",
        "sap_module": "SAP HANA",
        "category": "Database Availability",
        "priority": "P1",
        "issue_summary": "HANA database became unavailable",
        "issue_description": (
            "The production HANA database stopped accepting connections during "
            "the month-end close. The index server terminated and users could "
            "not log on to any connected application."
        ),
        "root_cause": "Severe memory exhaustion",
        "resolution": (
            "Released memory, restarted service and adjusted allocation limits"
        ),
        "owner_team": "Database Platform Team",
        "resolution_time_hours": 5.0,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1003",
        "incident_date": "2024-02-02",
        "sap_module": "SAP SD",
        "category": "Pricing",
        "priority": "P3",
        "issue_summary": "Incorrect discount in sales order",
        "issue_description": (
            "Sales orders created for a customer group applied a larger discount "
            "than the agreed contract value, which understated the net order value."
        ),
        "root_cause": "Incorrect pricing procedure sequence",
        "resolution": "Corrected condition sequence and repriced order",
        "owner_team": "Order-to-Cash Support",
        "resolution_time_hours": 1.2,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1004",
        "incident_date": "2024-02-14",
        "sap_module": "SAP BTP",
        "category": "Connectivity",
        "priority": "P1",
        "issue_summary": "Application could not connect to backend system",
        "issue_description": (
            "A Cloud Foundry application on SAP BTP failed every call to the "
            "on-premise backend with an authentication error. The destination "
            "test connection also failed from the cockpit."
        ),
        "root_cause": "Expired destination credentials",
        "resolution": "Renewed credentials and corrected destination properties",
        "owner_team": "BTP Platform Team",
        "resolution_time_hours": 7.5,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1005",
        "incident_date": "2024-02-21",
        "sap_module": "SAP SuccessFactors",
        "category": "Integration",
        "priority": "P2",
        "issue_summary": "Employee replication was delayed",
        "issue_description": (
            "Employee master data replication from SuccessFactors to the ERP "
            "system stopped for two days. New joiners were missing in payroll."
        ),
        "root_cause": "Mapping error in integration flow",
        "resolution": "Corrected mapping and reran integration job",
        "owner_team": "HR Integration Team",
        "resolution_time_hours": 4.0,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1006",
        "incident_date": "2024-03-05",
        "sap_module": "SAP HANA",
        "category": "Performance",
        "priority": "P1",
        "issue_summary": "Critical transactions became slow",
        "issue_description": (
            "Users experienced severe performance degradation. Business-critical "
            "transactions that normally finish in seconds took several minutes, "
            "and the delta merge queue kept growing."
        ),
        "root_cause": "Long-running savepoint and storage pressure",
        "resolution": "Corrected storage pressure and optimized workload",
        "owner_team": "Database Platform Team",
        "resolution_time_hours": 9.0,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1007",
        "incident_date": "2024-03-11",
        "sap_module": "SAP MM",
        "category": "Purchase Order",
        "priority": "P3",
        "issue_summary": "Purchase order release was not triggered",
        "issue_description": (
            "Purchase orders above the approval threshold were saved without "
            "entering the release workflow, so buyers could order without approval."
        ),
        "root_cause": "Incorrect release strategy configuration",
        "resolution": "Corrected release strategy and regenerated classification",
        "owner_team": "Procure-to-Pay Support",
        "resolution_time_hours": 2.5,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1008",
        "incident_date": "2024-03-18",
        "sap_module": "SAP BTP",
        "category": "Authorization",
        "priority": "P2",
        "issue_summary": "User could not access deployed application",
        "issue_description": (
            "A business user opened the application URL and received a 403 "
            "Forbidden page. Other users in the same department had no problem."
        ),
        "root_cause": "Missing role collection assignment",
        "resolution": "Assigned required role collection",
        "owner_team": "BTP Platform Team",
        "resolution_time_hours": 1.8,
        "status": "Closed",
    },
]

# --------------------------------------------------------------------------- #
# Rows 10+: extra incidents, including deliberately messy ones.
# --------------------------------------------------------------------------- #
EXTRA_ROWS = [
    # A completely empty row -- Task 2 must drop it.
    {c: None for c in COLUMNS},
    {
        "incident_id": "INC-1009",
        "incident_date": "2024-03-26",
        "sap_module": "  sap hana  ",  # inconsistent case + padding
        "category": "Backup",
        "priority": "p2",  # lower case priority
        "issue_summary": "Nightly backup job failed",
        "issue_description": (
            "The scheduled full backup of the HANA production tenant failed with "
            "a write error and no usable backup existed for that day."
        ),
        "root_cause": "Backup target file system was full",
        "resolution": "Freed space on the backup volume and reran the full backup",
        "owner_team": "Database Platform Team",
        "resolution_time_hours": "2.75",  # numeric stored as text
        "status": "Closed",
    },
    {
        "incident_id": "INC-1010",
        "incident_date": "01-04-2024",  # different date format
        "sap_module": "SAP BTP",
        "category": "Connectivity",
        "priority": "P2",
        "issue_summary": "Cloud Connector tunnel dropped intermittently",
        "issue_description": (
            "The Cloud Connector lost its tunnel to the BTP subaccount several "
            "times a day. Applications calling the on-premise system failed "
            "during each outage window."
        ),
        "root_cause": "Firewall idle-timeout closed the tunnel connection",
        "resolution": (
            "Adjusted the firewall idle timeout and enabled keep-alive on the "
            "Cloud Connector"
        ),
        "owner_team": "BTP Platform Team",
        "resolution_time_hours": 6.0,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1011",
        "incident_date": "2024-04-08",
        "sap_module": "SAP SD",
        "category": "Billing",
        "priority": "P2",
        "issue_summary": "Billing documents stuck in the accounting interface",
        "issue_description": (
            "Billing documents were created but not released to accounting, so "
            "revenue was missing from the general ledger."
        ),
        "root_cause": "Missing account determination for a new material group",
        "resolution": "Maintained account determination and released the documents",
        "owner_team": "Order-to-Cash Support",
        "resolution_time_hours": 3.0,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1012",
        "incident_date": "2024-04-15",
        "sap_module": "SAP MM",
        "category": "Inventory",
        "priority": "P1",
        "issue_summary": "Goods receipt postings failed during shift start",
        "issue_description": (
            "Warehouse staff could not post any goods receipt. Every posting "
            "terminated with a number-range error and the receiving dock stopped."
        ),
        "root_cause": "Material document number range was exhausted",
        "resolution": "Extended the number range interval and reposted the documents",
        "owner_team": "Procure-to-Pay Support",
        "resolution_time_hours": 4.5,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1013",
        "incident_date": "2024-04-22",
        "sap_module": "SAP SuccessFactors",
        "category": "Authorization",
        "priority": "P3",
        "issue_summary": "Managers could not see their team in the org chart",
        "issue_description": (
            "Several managers reported an empty org chart although their direct "
            "reports were maintained correctly in employee central."
        ),
        "root_cause": None,  # missing text field -- Task 2 fills a default
        "resolution": "Rebuilt the role-based permission group and refreshed the cache",
        "owner_team": "HR Integration Team",
        "resolution_time_hours": 2.0,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1014",
        "incident_date": "2024-05-03",
        "sap_module": "SAP HANA",
        "category": "Performance",
        "priority": "P2",
        "issue_summary": "Reporting queries slowed down after data load",
        "issue_description": (
            "Analytical queries on the sales tables became progressively slower "
            "after the nightly load finished."
        ),
        "root_cause": "Delta storage was not merged after the bulk load",
        "resolution": "Triggered a delta merge and tuned the auto-merge settings",
        "owner_team": "Database Platform Team",
        "resolution_time_hours": 3.25,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1015",
        "incident_date": "2024-05-10",
        "sap_module": "SAP BTP",
        "category": "Integration",
        "priority": "P1",
        "issue_summary": "Integration Suite iFlow stopped processing messages",
        "issue_description": (
            "Messages piled up in the queue and none reached the receiver "
            "system. The iFlow showed a permanent error status."
        ),
        "root_cause": "Expired client certificate on the receiver channel",
        "resolution": "Deployed a renewed certificate and restarted the iFlow",
        "owner_team": "BTP Platform Team",
        "resolution_time_hours": 8.0,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1016",
        "incident_date": "2024-05-17",
        "sap_module": "SAP SD",
        "category": "Delivery",
        "priority": "P2",
        "issue_summary": "Deliveries could not be picked in the warehouse",
        "issue_description": (
            "Outbound deliveries were created but picking could not start, so "
            "trucks waited at the dock."
        ),
        "root_cause": "Shipping point was not assigned to the new plant",
        "resolution": "Assigned the shipping point and reprocessed the deliveries",
        "owner_team": "Order-to-Cash Support",
        "resolution_time_hours": 2.2,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1017",
        "incident_date": "2024-05-24",
        "sap_module": "SAP HANA",
        "category": "Database Availability",
        "priority": "P3",
        "issue_summary": "Secondary system fell behind in system replication",
        "issue_description": (
            "The replication delay on the secondary site grew beyond the agreed "
            "recovery point objective, putting failover readiness at risk."
        ),
        "root_cause": "Network bandwidth saturation between data centres",
        "resolution": "Rescheduled bulk traffic and re-established replication",
        "owner_team": "Database Platform Team",
        "resolution_time_hours": 5.5,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1018",
        "incident_date": "2024-06-01",
        "sap_module": "SAP MM",
        "category": "Invoice Management",
        "priority": "P2",
        "issue_summary": "Duplicate supplier invoices were posted",
        "issue_description": (
            "The same supplier invoice was posted twice in the same week, which "
            "created a risk of double payment."
        ),
        "root_cause": "Duplicate invoice check was not active for the company code",
        "resolution": "Activated the duplicate check and reversed the extra document",
        "owner_team": "Procure-to-Pay Support",
        "resolution_time_hours": 3.8,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1019",
        "incident_date": "2024-06-09",
        "sap_module": "SAP SuccessFactors",
        "category": "Integration",
        "priority": "P1",
        "issue_summary": "Payroll interface failed before the pay run",
        "issue_description": (
            "The compensation data transfer to payroll aborted, and the pay run "
            "could not start on the planned date."
        ),
        "root_cause": "Unmapped pay component introduced by a configuration change",
        "resolution": "Added the missing mapping and reran the interface",
        "owner_team": "HR Integration Team",
        "resolution_time_hours": 6.5,
        "status": "Closed",
    },
    {
        "incident_id": "INC-1020",
        "incident_date": "2024-06-14",
        "sap_module": "SAP BTP",
        "category": "Authorization",
        "priority": "P3",
        "issue_summary": "Service key rotation broke a scheduled job",
        "issue_description": (
            "A background job calling a BTP service started failing with an "
            "unauthorized error after a routine key rotation."
        ),
        "root_cause": "Job still referenced the old service key",
        "resolution": "Updated the job configuration with the new service key",
        "owner_team": "BTP Platform Team",
        "resolution_time_hours": 1.5,
        "status": "Open",
    },
]


def build_dataframe() -> pd.DataFrame:
    """Return the raw (deliberately imperfect) incident dataframe."""
    return pd.DataFrame(SAMPLE_ROWS + EXTRA_ROWS, columns=COLUMNS)


def main() -> None:
    df = build_dataframe()
    df.to_excel("sap_incidents.xlsx", sheet_name="incidents", index=False)
    print(f"Wrote sap_incidents.xlsx with {len(df)} rows (sheet: incidents).")
    print("INC-1006 is on Excel row", df.index[df["incident_id"] == "INC-1006"][0] + 2)


if __name__ == "__main__":
    main()
