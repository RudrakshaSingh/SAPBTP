# Problem Statement 3 — Student Payment Summary View

| | |
|---|---|
| **Domain** | EdTech / Online Learning |
| **Topic** | SQL — Views, Joins, Conditional Aggregation, CASE Categorization |
| **Deliverable** | A SQL view named `vw_student_payment_summary` |

---

## Business Scenario

An online learning platform wants to monitor **student-wise enrollment and payment performance**. Currently, student details, course enrollment details, and payment details are stored in separate tables.

The finance team does not want to write complex joins every time. They want a **reusable SQL VIEW** that shows each student's total enrollments, total amount paid, pending amount, and payment category.

The platform wants to identify:

- Which students have enrolled in multiple courses
- How much amount each student has paid
- How much payment is still pending
- Which students are high-value customers
- Which students have pending dues

This view will help the finance and academic teams track student-wise revenue.

## Object to Create

```
vw_student_payment_summary
```

## Tables Involved

1. `students`
2. `enrollments`
3. `courses`
4. `payments`

## Required Output Columns

| Column Name | Description |
|---|---|
| `student_id` | Unique ID of the student |
| `student_name` | Name of the student |
| `city` | City of the student |
| `total_enrollments` | Total number of courses enrolled by the student |
| `total_paid_amount` | Total amount paid by the student |
| `total_pending_amount` | Total pending payment amount |
| `student_category` | Category based on total paid amount |

## Business Rules

### Join Rule

Use **`LEFT JOIN`**, because every student should appear in the report even if the student has not enrolled or paid yet.

### Payment Calculation Rule

| Condition | Action |
|---|---|
| `payment_status = 'Paid'` | Add the amount to `total_paid_amount` |
| `payment_status = 'Pending'` | Add the amount to `total_pending_amount` |

### Student Category Rule

| Condition | Category |
|---|---|
| Paid amount >= 20000 | Premium Student |
| Paid amount >= 10000 | Regular Student |
| Paid amount < 10000 | Basic Student |

> Note: the conditions are evaluated in order, so a `CASE` expression must check `>= 20000` before `>= 10000`.

## Skills Practiced

- `CREATE VIEW`
- Multi-table `LEFT JOIN`
- Conditional aggregation with `SUM(CASE WHEN ...)`
- `CASE` based bucketing / categorization
- `COUNT(DISTINCT ...)` for enrollment counts
