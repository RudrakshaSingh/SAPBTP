"""Six documents across three knowledge areas, loaded at startup so ``/ask`` works.

Each entry is ``(source, category, text)``. Two documents per category is
deliberate: it keeps ``sources_used`` interesting, because naming the category
is not the same as naming the file the answer came from.

The overlap between areas is deliberate too. HR grants a home-office
*allowance*, finance pays a meal *allowance*; HR mentions the HR portal login,
IT owns password resets. Those near-collisions are what the category filter is
for.
"""

HR_LEAVE_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.
Employees serving their probation period earn leave from day one but may only
apply for it after confirmation.

Casual Leave

In addition to annual leave, employees receive 7 days of casual leave per
calendar year for short personal absences. Casual leave is taken in blocks of no
more than 2 consecutive days and does not carry forward.

Applications for annual leave must be raised in the HR portal at least 5 working
days before the first day of leave. Any period of more than 5 consecutive
working days needs approval from both the reporting manager and the department
head.

Carry Forward

A maximum of 6 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March, after which
they lapse without compensation.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. Sick leave does
not carry forward. Absence of 3 or more consecutive days requires a medical
certificate from a registered practitioner, submitted within 7 days of returning
to work.
"""

HR_EMPLOYMENT_TERMS = """
Working Hours

Standard working hours are 9 hours per day including a 1-hour break, between
9:00 and 19:00. Core hours during which every employee must be available are
11:00 to 16:00.

Notice Period

An employee resigning from the company must serve a notice period of 60 days.
Employees still on probation serve 15 days. The notice period begins on the date
the resignation is acknowledged by the reporting manager in the HR portal, not
on the date the email is sent.

Probation

New employees serve a probation period of 6 months. Confirmation follows a
review by the reporting manager. Probation may be extended once, by up to 3
months, with written reasons shared with the employee.

Work From Home

All eligible employees may work from home for up to 2 days per week, booked in
the HR portal by the end of the previous week. A one-time home-office allowance
of 15,000 INR is paid after confirmation. Internet charges are not reimbursed.
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
stays searchable from the archive folder. Requests for a shared mailbox are
raised by the reporting manager, not by the user.
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
attach its output to a helpdesk ticket. Tickets that include the report are
resolved within 1 working day; tickets without it take up to 3.

Wi-Fi and Guest Access

The office network is CORP-SECURE, joined with your domain account. Guest access
is requested by the host at reception and expires after 24 hours.

Hardware Replacement

Laptops are replaced every 4 years, or sooner if a hardware fault is confirmed
by the helpdesk. A loaner laptop is available while a repair is in progress.
"""

FINANCE_TRAVEL_POLICY = """
Booking Business Travel

Domestic travel is booked through the travel desk at least 7 days in advance.
Employees at grade M3 and above travel by air; all other grades travel by train
in AC 2-tier. International travel needs written approval from the department
head before tickets are issued.

Daily Allowance

The daily meal allowance on business trips is 1,800 INR for metro cities and
1,200 INR elsewhere. Receipts are not required for the meal allowance. Hotel
bills must be uploaded within 10 days of returning.

The hotel limit is 6,000 INR per night in metro cities and 4,000 INR elsewhere.
Anything above the limit is paid by the employee unless approved in advance.

Local Transport

Airport transfers and client visits are reimbursed at actuals. Personal-vehicle
use is reimbursed at 12 INR per kilometre against a trip log.
"""

FINANCE_REIMBURSEMENT_RULES = """
Claim Deadlines

Every reimbursement claim is submitted in the finance portal within 30 days of
the expense date. Claims older than 30 days need a written exception from the
finance controller. Approved claims are paid with the next payroll run,
generally within 15 working days.

Travel Reimbursement Limit

The total travel reimbursement limit is 50,000 INR per employee per quarter.
Claims beyond that limit require the department head's approval before
submission.

Receipts

Any single expense above 500 INR needs a scanned receipt showing the vendor,
the date and the amount. Handwritten receipts are accepted only for local
transport.

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
