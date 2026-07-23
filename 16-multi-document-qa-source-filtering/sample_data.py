"""
STEP 2 -- THE SAMPLE DOCUMENTS

Normally these would be uploaded files. Keeping them as plain strings means
the project needs no data folder and no upload step to demonstrate.

The overlaps between areas are deliberate: HR has a home-office *allowance*
and Finance has a meal *allowance*; HR mentions the HR portal login and IT
owns password resets. Those near-collisions are what the filter is for.
"""

HR_LEAVE_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.

Casual Leave

In addition to annual leave, employees receive 7 days of casual leave per
calendar year for short personal absences. Casual leave is taken in blocks of no
more than 2 consecutive days and does not carry forward.

Applications for annual leave must be raised in the HR portal at least 5 working
days before the first day of leave.

Carry Forward

A maximum of 6 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. Absence of 3 or
more consecutive days requires a medical certificate.
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

All eligible employees may work from home for up to 2 days per week. A one-time
home-office allowance of 15,000 INR is paid after confirmation. Internet charges
are not reimbursed.
"""

IT_SUPPORT_FAQ = """
Resetting Your Password

Go to the self-service portal at portal.company.local and click Reset Password.
Enter your employee ID and the one-time code sent to your registered mobile
number. The new password must be at least 12 characters and cannot repeat any of
your last 5 passwords. Passwords expire every 90 days.

If the one-time code does not arrive within 5 minutes, raise a ticket with the
IT helpdesk on extension 4400.

Account Lockout

Five failed sign-in attempts lock the account for 30 minutes. The helpdesk can
unlock it sooner after verifying your identity over a video call.

Email Access

Mailboxes are 50 GB. Mail older than 24 months is archived automatically and
stays searchable from the archive folder.
"""

IT_NETWORK_FAQ = """
VPN Disconnects

If the VPN keeps disconnecting, first switch from the automatic protocol to TCP
in the client settings, as unstable Wi-Fi drops UDP sessions quickly. Then move
to the 5 GHz band on your router and disable any other VPN or proxy running on
the machine.

The VPN client disconnects on purpose after 12 hours, and after 30 minutes of
inactivity. Reconnecting is expected in both cases and is not a fault.

If disconnects continue, run the Network Report tool from the company portal and
attach its output to a helpdesk ticket.

Wi-Fi and Guest Access

The office network is CORP-SECURE, joined with your domain account. Guest access
expires after 24 hours.

Hardware Replacement

Laptops are replaced every 4 years, or sooner if a hardware fault is confirmed.
"""

FINANCE_TRAVEL_POLICY = """
Booking Business Travel

Domestic travel is booked through the travel desk at least 7 days in advance.
Employees at grade M3 and above travel by air; all other grades travel by train
in AC 2-tier. International travel needs written approval from the department
head.

Daily Allowance

The daily meal allowance on business trips is 1,800 INR for metro cities and
1,200 INR elsewhere. Receipts are not required for the meal allowance. Hotel
bills must be uploaded within 10 days of returning.

The hotel limit is 6,000 INR per night in metro cities and 4,000 INR elsewhere.

Local Transport

Personal-vehicle use is reimbursed at 12 INR per kilometre against a trip log.
"""

FINANCE_REIMBURSEMENT_RULES = """
Claim Deadlines

Every reimbursement claim is submitted in the finance portal within 30 days of
the expense date. Approved claims are paid with the next payroll run, generally
within 15 working days.

Travel Reimbursement Limit

The total travel reimbursement limit is 50,000 INR per employee per quarter.
Claims beyond that limit require the department head's approval.

Receipts

Any single expense above 500 INR needs a scanned receipt showing the vendor,
the date and the amount.

Internet and Phone

A monthly phone allowance of 1,000 INR is paid to employees in client-facing
roles. Home internet is not reimbursed for any grade.
"""

# (source, category, text)
SAMPLE_DOCUMENTS = [
    ("hr_leave_policy.txt", "HR", HR_LEAVE_POLICY),
    ("hr_employment_terms.txt", "HR", HR_EMPLOYMENT_TERMS),
    ("it_faq.txt", "IT", IT_SUPPORT_FAQ),
    ("it_network_faq.txt", "IT", IT_NETWORK_FAQ),
    ("finance_travel_policy.txt", "Finance", FINANCE_TRAVEL_POLICY),
    ("finance_reimbursement_rules.txt", "Finance", FINANCE_REIMBURSEMENT_RULES),
]
