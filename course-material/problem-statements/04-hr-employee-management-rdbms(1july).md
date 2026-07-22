# Problem Statement 4 — HR Employee Management System Using RDBMS Concepts

| | |
|---|---|
| **Project Title** | HR Employee Records, Attendance and Payroll Management System |
| **Domain** | Human Resources |
| **Topic** | RDBMS design — keys, constraints, relationships, basic SQL |
| **Duration** | 4 Hours |

---

## 1. Project Objective

Design and implement a small relational database system for an HR department.

The HR department currently maintains employee, department, attendance, and payroll details manually in spreadsheets. This creates issues such as:

- Duplicate records
- Incorrect employee–department mapping
- Difficulty in tracking attendance
- Confusion in payroll status

Your task is to design an **RDBMS-based HR database** that stores data in multiple related tables and applies proper keys, constraints, and relationships.

## 2. Business Scenario

A company wants to digitize its HR data management process. The HR team wants to manage:

- Departments
- Job roles
- Employees
- Employee attendance
- Monthly payroll

The system should help HR answer questions such as:

- Which employees belong to each department?
- Which employees are active, on probation, or resigned?
- Which employees were absent on a particular date?
- Which employees have pending salary payments?
- Which employees are from a specific city?
- Who are the top-paid employees?
- Are duplicate employee or attendance records being prevented?

## 3. Concepts to Be Covered

| Category | Concepts |
|---|---|
| **RDBMS basics** | Tables, rows, columns, schema |
| **Keys** | Primary key, Foreign key, Unique key, Composite unique constraint |
| **Constraints** | `NOT NULL`, `CHECK`, `DEFAULT` |
| **DML** | `INSERT`, `SELECT`, `UPDATE`, `DELETE` |
| **Query clauses** | `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT` |
| **Verification** | Schema inspection, constraint testing |

## 4. Database Tables Required

1. `departments`
2. `job_roles`
3. `employees`
4. `attendance`
5. `payroll`

---

## 5. Table Details

### Table 1: `departments`

Stores company department details.

| Column Name | Description |
|---|---|
| `department_id` | Unique ID for each department |
| `department_name` | Name of the department |

**Rules**

- Each department must have a unique ID.
- Department name should not be blank.
- Duplicate department names should not be allowed.

**Sample Departments:** Human Resources, Information Technology, Finance, Sales, Operations

---

### Table 2: `job_roles`

Stores job role details.

| Column Name | Description |
|---|---|
| `role_id` | Unique ID for each job role |
| `role_title` | Name of the job role |
| `min_salary` | Minimum salary range for the role |
| `max_salary` | Maximum salary range for the role |

**Rules**

- Each role must have a unique ID.
- Role title should not be blank.
- Duplicate role titles should not be allowed.
- Minimum salary should not be negative.
- Maximum salary should be greater than or equal to minimum salary.

**Sample Job Roles:** HR Executive, Software Developer, Accountant, Sales Executive, Operations Associate

---

### Table 3: `employees`

Stores employee master data.

| Column Name | Description |
|---|---|
| `employee_id` | Unique ID for each employee |
| `employee_name` | Name of the employee |
| `email` | Employee email address |
| `city` | Employee city |
| `joining_date` | Date of joining |
| `department_id` | Department assigned to the employee |
| `role_id` | Job role assigned to the employee |
| `status` | Employment status |

**Rules**

- Each employee must have a unique ID.
- Employee name should not be blank.
- Employee email should not be blank.
- Duplicate employee emails should not be allowed.
- Each employee must belong to a valid department.
- Each employee must have a valid job role.
- Employee `status` must be one of: `Active`, `Probation`, `Resigned`.
- If no status is provided, the default status should be `Active`.

**Sample Employees**

| Employee Name | City | Status |
|---|---|---|
| Rahul Kumar | Patna | Active |
| Priya Singh | Kolkata | Active |
| Amit Raj | Delhi | Probation |
| Sneha Verma | Patna | Active |
| Aditya Sharma | Mumbai | Active |

---

### Table 4: `attendance`

Stores daily attendance records of employees.

| Column Name | Description |
|---|---|
| `attendance_id` | Unique attendance record ID |
| `employee_id` | Employee linked to attendance |
| `attendance_date` | Date of attendance |
| `attendance_status` | Attendance status |

**Rules**

- Each attendance record must have a unique ID.
- Attendance must be linked to a valid employee.
- Attendance date should not be blank.
- `attendance_status` must be one of: `Present`, `Absent`, `Leave`, `Half Day`.
- One employee should not have more than one attendance record for the same date (composite unique constraint on `employee_id` + `attendance_date`).

**Sample Attendance**

| Employee | Date | Attendance Status |
|---|---|---|
| Rahul Kumar | 2026-02-01 | Present |
| Priya Singh | 2026-02-01 | Present |
| Amit Raj | 2026-02-01 | Leave |
| Sneha Verma | 2026-02-01 | Half Day |
| Aditya Sharma | 2026-02-01 | Absent |

---

### Table 5: `payroll`

Stores monthly payroll records of employees.

| Column Name | Description |
|---|---|
| `payroll_id` | Unique payroll record ID |
| `employee_id` | Employee linked to payroll |
| `salary_month` | Salary month |
| `basic_salary` | Basic salary of employee |
| `bonus` | Bonus amount |
| `deductions` | Deduction amount |
| `payment_status` | Salary payment status |

**Rules**

- Each payroll record must have a unique ID.
- Payroll must be linked to a valid employee.
- Salary month should not be blank.
- Basic salary, bonus, and deductions should not be negative.
- One employee should have only one payroll record for one salary month (composite unique constraint).
- `payment_status` must be one of: `Paid`, `Pending`, `Hold`.

**Sample Payroll Records**

| Employee | Salary Month | Basic Salary | Bonus | Deductions | Payment Status |
|---|---|---|---|---|---|
| Rahul Kumar | 2026-02 | 35000 | 2000 | 1000 | Paid |
| Priya Singh | 2026-02 | 80000 | 5000 | 2000 | Paid |
| Amit Raj | 2026-02 | 45000 | 0 | 1000 | Pending |
| Sneha Verma | 2026-02 | 30000 | 3000 | 500 | Paid |
| Aditya Sharma | 2026-02 | 28000 | 0 | 0 | Hold |

---

## 6. Relationship Requirements

| Relationship | Cardinality | Example |
|---|---|---|
| Department → Employees | One-to-many | The IT department can have multiple software developers |
| Job Role → Employees | One-to-many | The Software Developer role can be assigned to many employees |
| Employee → Attendance | One-to-many | Rahul Kumar can have attendance records for multiple dates |
| Employee → Payroll | One-to-many | Rahul Kumar can have payroll records for February, March, and April |

---

## 7. Hands-on Tasks

### Task 1: Understand the Business Requirement

Read the HR business scenario carefully and identify main entities, relationships between entities, data rules, and constraints required.

### Task 2: Design the Database Schema

Design the schema for all five tables. For each table identify: columns, primary key, foreign key, unique constraints, check constraints, default values.

### Task 3: Create the Tables

Create all five tables. Design must include primary keys, foreign keys, unique constraints, not-null constraints, check constraints, default values, and composite unique constraints where required.

### Task 4: Insert Sample Data

Minimum records required:

| Table | Minimum Records |
|---|---|
| `departments` | 5 |
| `job_roles` | 5 |
| `employees` | 5 |
| `attendance` | 5 |
| `payroll` | 5 |

Insert in this order so foreign key relationships are not violated:

1. `departments`
2. `job_roles`
3. `employees`
4. `attendance`
5. `payroll`

### Task 5: Display All Table Data

Display all records from each of the five tables.

### Task 6: Perform Basic SQL Queries

1. Show all employees.
2. Show employee name, email, and city.
3. Show all employees from Patna.
4. Show all active employees.
5. Show all employees under probation.
6. Show all employees sorted by joining date.
7. Show the top 3 highest-paid employees.
8. Show all distinct employee cities.
9. Show payroll records where payment status is `Pending`.
10. Show attendance records where attendance status is `Absent`.

### Task 7: Perform Insert Operation

Add a new employee:

| Field | Value |
|---|---|
| `employee_name` | Rohan Das |
| `email` | rohan.hr@example.com |
| `city` | Pune |
| `joining_date` | 2026-02-15 |
| department | Human Resources |
| job role | HR Executive |
| `status` | Probation |

After inserting, display the newly added employee record.

### Task 8: Perform Update Operation

Update the city of Rohan Das from Pune to Bengaluru. Display the updated record.

### Task 9: Update Employee Status

Update Rohan Das from `Probation` to `Active`. Display the updated record.

### Task 10: Perform Delete Operation

Delete Rohan Das from the `employees` table. Before deleting, ensure the employee does not have related attendance or payroll records. After deleting, display all employees and confirm removal.

---

## 8. Constraint Testing Tasks

The purpose of this section is to check whether your database rules are working correctly. **Every test below must be rejected by the database.**

| # | Test | Expected Result |
|---|---|---|
| 1 | **Duplicate Email** — add an employee using an email that already exists | Record rejected |
| 2 | **Invalid Department** — add an employee with a department that does not exist | Record rejected |
| 3 | **Invalid Job Role** — add an employee with a job role that does not exist | Record rejected |
| 4 | **Invalid Employee Status** — add an employee with status `Joined` | Rejected; only `Active`, `Probation`, `Resigned` allowed |
| 5 | **Duplicate Attendance** — two attendance records for the same employee on the same date | Duplicate rejected |
| 6 | **Invalid Attendance Status** — attendance status `Late` | Rejected; only `Present`, `Absent`, `Leave`, `Half Day` allowed |
| 7 | **Duplicate Payroll** — two payroll records for same employee in the same salary month | Duplicate rejected |
| 8 | **Negative Salary** — payroll record with negative basic salary | Record rejected |
| 9 | **Invalid Payroll Status** — payroll status `Processing` | Rejected; only `Paid`, `Pending`, `Hold` allowed |

---

## 9. Schema Inspection Tasks

Inspect the schema of all five tables. For each table, verify:

- Column names
- Data types
- Primary key
- Not-null rules
- Foreign key relationships
- Unique constraints
- Check constraints

---

## 10. Expected Final Output

At the end of the exercise, submit:

1. HR database schema design
2. All five created tables
3. Inserted sample data
4. Output of all basic SQL queries
5. Insert operation output
6. Update operation output
7. Delete operation output
8. Constraint testing results
9. Schema inspection output
10. Short explanation of table relationships
