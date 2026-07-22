"""Three HR policy documents, loaded at startup so ``/ask`` works immediately."""

HR_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.
Employees serving their probation period earn leave from day one but may only
apply for it after confirmation.

Applications for annual leave must be raised in the HR portal at least 5 working
days before the first day of leave. Any period of more than 5 consecutive
working days needs approval from both the reporting manager and the department
head.

Carry Forward

A maximum of 6 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March, after which
they lapse without compensation. Unused leave beyond the 6-day limit is not
encashable.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. Sick leave does
not carry forward. Absence of 3 or more consecutive days requires a medical
certificate from a registered practitioner, submitted within 7 days of returning
to work.

Public Holidays

The company observes 10 public holidays each year. The list is published every
December for the following year. Public holidays that fall on a weekend are not
compensated with an additional day off.
"""

REMOTE_WORK_POLICY = """
Work From Home

All eligible employees may work from home for up to 2 days per week. The
remaining 3 days are worked from the assigned office location. Teams choose
their own anchor day, on which every member is expected in the office.

Eligibility begins after the probation period ends. Employees in roles that
require physical presence, such as lab and facilities roles, are not eligible.

Requesting Remote Days

Remote days are booked in the HR portal by the end of the previous week. A
manager may recall an employee to the office for a client visit, an audit or a
team event with at least 48 hours of notice.

Fully Remote Arrangements

A fully remote arrangement is possible for a maximum of 90 days per year, for
example when an employee relocates temporarily. It requires written approval
from the department head and the HR business partner before travel.

Equipment and Expenses

The company provides a laptop and a headset to every remote worker. A one-time
home-office allowance of 15,000 INR is available after confirmation. Internet
charges are not reimbursed.
"""

EMPLOYMENT_TERMS = """
Notice Period

An employee resigning from the company must serve a notice period of 60 days.
Employees still on probation serve 15 days. The notice period begins on the date
the resignation is acknowledged by the reporting manager in the HR portal, not
on the date the email is sent.

Notice may be shortened only with written approval from the department head.
Unserved days are recovered from the final settlement at the employee's basic
salary rate.

Final Settlement

The full and final settlement is paid within 45 days of the last working day. It
covers unpaid salary, encashable leave and any reimbursements already approved.
Company assets, including the laptop and access cards, must be returned on or
before the last working day.

Working Hours

Standard working hours are 9 hours per day including a 1-hour break, between
9:00 and 19:00. Core hours during which every employee must be available are
11:00 to 16:00.

Probation

New employees serve a probation period of 6 months. Confirmation follows a
review by the reporting manager. Probation may be extended once, by up to 3
months, with written reasons shared with the employee.
"""

SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", HR_POLICY),
    ("remote_work_policy.txt", REMOTE_WORK_POLICY),
    ("employment_terms.txt", EMPLOYMENT_TERMS),
]
