"""
STEP 2 -- THE SAMPLE DOCUMENTS

Normally these would be uploaded files. Keeping them as plain strings means the
project needs no data folder and no upload step to demonstrate.

Two HR documents, enough to show the quality check both ways: "What is the
probation period?" is answered and supported, while "What is the company's stock
price today?" is nowhere in here and comes back not supported.
"""

HR_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.

Carry Forward

A maximum of 10 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. An absence of 3
or more consecutive days requires a medical certificate.
"""

HR_EMPLOYMENT_TERMS = """
Working Hours

Standard working hours are 9 hours per day including a 1-hour break, between
9:00 and 19:00. Core hours during which every employee must be available are
11:00 to 16:00.

Notice Period

An employee resigning from the company must serve a notice period of 60 days.
Employees still on probation serve 15 days.

Probation

New employees serve a probation period of 6 months. Probation may be extended
once, by up to 3 months.

Work From Home

All eligible employees may work from home for up to 2 days per week.
"""

# (source, text)
SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", HR_POLICY),
    ("hr_employment_terms.txt", HR_EMPLOYMENT_TERMS),
]
