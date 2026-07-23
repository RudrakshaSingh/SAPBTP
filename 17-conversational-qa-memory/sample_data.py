"""
STEP 2 -- THE SAMPLE DOCUMENTS

Normally these would be uploaded files. Keeping them as plain strings means the
project needs no data folder and no upload step to demonstrate.

These two HR documents cover exactly the two conversations in the problem
statement: annual leave and carrying it over, sick leave, the maternity leave
policy and how long it is, and whether it also applies to adoption.
"""

HR_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.
Annual leave is applied for in the HR portal at least 5 working days in advance.

Carry Forward

A maximum of 10 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March, after which
they lapse.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. An absence of 3
or more consecutive days requires a medical certificate. Unused sick leave does
not carry forward.
"""

HR_PARENTAL_LEAVE = """
Maternity Leave

A female employee is entitled to 26 weeks of paid maternity leave for the first
two children. From the third child onwards the entitlement is 12 weeks. Leave
may begin up to 8 weeks before the expected due date.

Paternity Leave

A male employee is entitled to 15 days of paid paternity leave, to be taken
within 3 months of the birth.

Adoption Leave

An employee who legally adopts a child below the age of one year is entitled to
26 weeks of adoption leave, on the same terms as maternity leave. For a child
aged one year or above the entitlement is 12 weeks.
"""

# (source, text)
SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", HR_POLICY),
    ("hr_parental_leave.txt", HR_PARENTAL_LEAVE),
]
