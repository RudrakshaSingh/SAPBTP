# Problem Statement 2 — Revenue by Course Report

| | |
|---|---|
| **Domain** | EdTech / Online Learning |
| **Topic** | SQL — Joins, Aggregation, Conditional Sums |
| **Deliverable** | A single SQL query |

---

## Business Scenario

An online learning platform wants to analyze the revenue performance of each course. The platform stores data in three tables and management wants a **course-wise enrollment and payment report**.

## Tables Involved

### 1. `courses`

| Column |
|---|
| `course_id` |
| `course_name` |

### 2. `enrollments`

| Column |
|---|
| `enrollment_id` |
| `course_id` |
| `student_id` |
| `enrollment_date` |
| `status` |

### 3. `payments`

| Column |
|---|
| `payment_id` |
| `enrollment_id` |
| `amount` |
| `payment_status` |

## Requirement

Write an SQL query to display the following columns:

| Column | Meaning |
|---|---|
| `course_name` | Name of the course |
| `total_enrollments` | Total number of students enrolled in that course |
| `paid_revenue` | Total payment amount where payment status is `Paid` |
| `pending_amount` | Total payment amount where payment status is `Pending` |

## Business Rules

- The report must include **all courses**, even if a course has no enrollment or payment yet.
- This is why a **`LEFT JOIN`** must be used.

## Sorting Requirement

The final result must be sorted by:

```
paid_revenue DESC
```

The course with the highest paid revenue should appear first.

## Final Objective

Create a course-wise revenue report that helps the business understand:

- Which course has the highest revenue
- How many enrollments each course has
- How much revenue has already been paid
- How much payment is still pending

## Skills Practiced

- `LEFT JOIN` across three tables
- `GROUP BY` with aggregation
- Conditional aggregation (`SUM(CASE WHEN ...)`)
- `ORDER BY` on an aggregated column
