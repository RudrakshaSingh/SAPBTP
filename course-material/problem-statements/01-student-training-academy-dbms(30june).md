# Problem Statement 1 — Student Training Academy Database Management System

| | |
|---|---|
| **Project Title** | Student Training Academy Database Management System |
| **Domain** | EdTech / Training Academy |
| **Topic** | RDBMS Foundation, Schema Design, Keys and Basic SQL Using Python |
| **Stack** | SQLite + Python (`sqlite3`) + Pandas |
| **Deliverable** | `training_academy.db` + Python notebook/script + query outputs |
| **Source** | `course-material/Tasks.docx` |

---

## 1. Problem Overview

A training academy wants to manage its student enrollment process using a relational database.

Currently, the academy stores student, course, instructor, enrollment, and payment details manually in Excel sheets. This creates problems such as duplicate records, difficulty in tracking enrollments, incorrect payment status, and difficulty in generating reports.

Your task is to design and build a small RDBMS-based system using **SQLite and Python**.

The system should store structured data in multiple related tables and allow users to perform basic database operations such as creating tables, inserting data, reading records, updating records, deleting records, and validating relationships using keys and constraints.

## 2. Learning Objectives

By completing this hands-on assignment, learners will understand:

- What an RDBMS is
- How tables, rows, columns, and schema work
- How to design a relational database schema
- How to use primary keys and foreign keys
- How to apply constraints such as `NOT NULL`, `UNIQUE`, `CHECK`, and `DEFAULT`
- How to insert, read, update, and delete records
- How to filter and sort data using SQL
- How to use Python to connect with SQLite
- How to execute SQL queries from Python
- How to fetch SQL results into Pandas DataFrames

## 3. Business Scenario

The training academy offers multiple courses across different departments. The academy wants to track: **Departments, Students, Instructors, Courses, Student enrollments, Payments**.

### Business Rules

- Each department can have many instructors.
- Each department can offer many courses.
- Each instructor belongs to one department.
- Each instructor can teach many courses.
- Each student can enroll in many courses.
- Each course can have many students.
- **A student should not be enrolled in the same course twice.**
- Each enrollment can have one payment record.
- Payment status should be one of: `Paid`, `Pending`, `Refunded`.
- Enrollment status should be one of: `Active`, `Completed`, `Cancelled`.

---

## 4. Database Tables Required

### Table 1: `departments`

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `department_id` | INTEGER | PRIMARY KEY | Unique department ID |
| `department_name` | TEXT | NOT NULL, UNIQUE | Name of the department |

**Sample Data**

| department_id | department_name |
|---|---|
| 1 | Data Science |
| 2 | Software Engineering |
| 3 | Business Analytics |

---

### Table 2: `students`

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `student_id` | INTEGER | PRIMARY KEY | Unique student ID |
| `student_name` | TEXT | NOT NULL | Name of the student |
| `email` | TEXT | NOT NULL, UNIQUE | Student email |
| `city` | TEXT | Optional | City of student |
| `registration_date` | DATE | NOT NULL | Registration date |

**Sample Data**

| student_id | student_name | email | city | registration_date |
|---|---|---|---|---|
| 1 | Rahul Kumar | rahul.kumar@example.com | Patna | 2026-01-05 |
| 2 | Priya Singh | priya.singh@example.com | Kolkata | 2026-01-06 |
| 3 | Amit Raj | amit.raj@example.com | Delhi | 2026-01-07 |
| 4 | Sneha Verma | sneha.verma@example.com | Patna | 2026-01-10 |
| 5 | Aditya Sharma | aditya.sharma@example.com | Mumbai | 2026-01-12 |

---

### Table 3: `instructors`

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `instructor_id` | INTEGER | PRIMARY KEY | Unique instructor ID |
| `instructor_name` | TEXT | NOT NULL | Name of instructor |
| `email` | TEXT | NOT NULL, UNIQUE | Instructor email |
| `department_id` | INTEGER | FOREIGN KEY | Linked department ID |

**Relationship:** `department_id` references `departments(department_id)`.

**Sample Data**

| instructor_id | instructor_name | email | department_id |
|---|---|---|---|
| 1 | Dr. Meera Iyer | meera.iyer@example.com | 1 |
| 2 | Arjun Sen | arjun.sen@example.com | 2 |
| 3 | Kavita Rao | kavita.rao@example.com | 3 |

---

### Table 4: `courses`

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `course_id` | INTEGER | PRIMARY KEY | Unique course ID |
| `course_name` | TEXT | NOT NULL | Name of course |
| `department_id` | INTEGER | FOREIGN KEY | Linked department ID |
| `instructor_id` | INTEGER | FOREIGN KEY | Linked instructor ID |
| `fee` | REAL | NOT NULL, CHECK `fee >= 0` | Course fee |
| `level` | TEXT | CHECK | Beginner, Intermediate, Advanced |

**Relationships**

- `department_id` references `departments(department_id)`
- `instructor_id` references `instructors(instructor_id)`

**Sample Data**

| course_id | course_name | department_id | instructor_id | fee | level |
|---|---|---|---|---|---|
| 101 | Python for Beginners | 2 | 2 | 4999 | Beginner |
| 102 | SQL and RDBMS Masterclass | 1 | 1 | 6999 | Beginner |
| 103 | Machine Learning Basics | 1 | 1 | 11999 | Intermediate |
| 104 | Business Dashboarding | 3 | 3 | 8999 | Intermediate |
| 105 | Advanced Data Engineering | 1 | 1 | 15999 | Advanced |

---

### Table 5: `enrollments`

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `enrollment_id` | INTEGER | PRIMARY KEY | Unique enrollment ID |
| `student_id` | INTEGER | FOREIGN KEY | Linked student ID |
| `course_id` | INTEGER | FOREIGN KEY | Linked course ID |
| `enrollment_date` | DATE | NOT NULL | Date of enrollment |
| `status` | TEXT | DEFAULT `'Active'`, CHECK | Active, Completed, Cancelled |

**Relationships**

- `student_id` references `students(student_id)`
- `course_id` references `courses(course_id)`

**Special Rule** — a student should not be enrolled in the same course twice:

```sql
UNIQUE(student_id, course_id)
```

**Sample Data**

| enrollment_id | student_id | course_id | enrollment_date | status |
|---|---|---|---|---|
| 1001 | 1 | 101 | 2026-02-01 | Active |
| 1002 | 1 | 102 | 2026-02-03 | Completed |
| 1003 | 2 | 102 | 2026-02-04 | Active |
| 1004 | 3 | 103 | 2026-02-05 | Active |
| 1005 | 4 | 104 | 2026-02-07 | Cancelled |

---

### Table 6: `payments`

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `payment_id` | INTEGER | PRIMARY KEY | Unique payment ID |
| `enrollment_id` | INTEGER | FOREIGN KEY, UNIQUE | Linked enrollment ID |
| `amount` | REAL | NOT NULL, CHECK `amount >= 0` | Payment amount |
| `payment_date` | DATE | NOT NULL | Payment date |
| `payment_status` | TEXT | CHECK | Paid, Pending, Refunded |

**Relationship:** `enrollment_id` references `enrollments(enrollment_id)`.

**Sample Data**

| payment_id | enrollment_id | amount | payment_date | payment_status |
|---|---|---|---|---|
| 501 | 1001 | 4999 | 2026-02-01 | Paid |
| 502 | 1002 | 6999 | 2026-02-03 | Paid |
| 503 | 1003 | 6999 | 2026-02-04 | Pending |
| 504 | 1004 | 11999 | 2026-02-05 | Paid |
| 505 | 1005 | 0 | 2026-02-07 | Refunded |

---

## 5. Hands-on Tasks

### Task 1: Create SQLite Database Using Python

Create a database named `training_academy.db` using Python's `sqlite3` library. Enable foreign key support:

```python
conn.execute("PRAGMA foreign_keys = ON;")
```

### Task 2: Create Tables

Create all six tables: `departments`, `students`, `instructors`, `courses`, `enrollments`, `payments`.

Your table design must include: primary keys, foreign keys, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, and a composite unique constraint on `student_id` + `course_id`.

### Task 3: Insert Sample Data

Insert at least:

| Table | Minimum Records |
|---|---|
| `departments` | 3 |
| `students` | 5 |
| `instructors` | 3 |
| `courses` | 5 |
| `enrollments` | 5 |
| `payments` | 5 |

Follow the correct insertion order so foreign key constraints do not fail:

```
departments → students → instructors → courses → enrollments → payments
```

### Task 4: Display All Tables

Write Python code to display data from all tables using Pandas:

```python
pd.read_sql_query("SELECT * FROM students", conn)
```

Display: all students, all instructors, all courses, all enrollments, all payments.

### Task 5: Basic SQL Queries

1. Show all students.
2. Show only student name, email, and city.
3. Show all students from Patna.
4. Show all courses with fee greater than 7000.
5. Show all beginner-level courses.
6. Show all students sorted by student name.
7. Show the top 3 highest fee courses.
8. Show distinct student cities.
9. Show all pending payments.
10. Show all active enrollments.

### Task 6: INSERT Operation Using Python

Add a new student using a **parameterized query**:

| student_name | email | city | registration_date |
|---|---|---|---|
| Rohan Das | rohan.das@example.com | Pune | 2026-02-15 |

After insertion, display the student record.

### Task 7: UPDATE Operation Using Python

Update the city of Rohan Das from Pune to Bengaluru. After update, display the updated record.

### Task 8: DELETE Operation Using Python

Delete the student Rohan Das. After deletion, display all students and confirm the record has been removed.

### Task 9: Constraint Testing

Intentionally test the constraints. **All four inserts below must be rejected by the database.**

| # | Test | Attempt | Expected Result |
|---|---|---|---|
| 1 | **UNIQUE** | Insert a student with an email that already exists | Insert rejected |
| 2 | **FOREIGN KEY** | Insert an enrollment with a student ID that does not exist | Insert rejected |
| 3 | **CHECK** | Insert a course with a negative fee | Insert rejected |
| 4 | **CHECK on status** | Insert an enrollment status called `Started` | Rejected — only `Active`, `Completed`, `Cancelled` allowed |

### Task 10: Schema Inspection

Write Python code to inspect table structure:

```sql
PRAGMA table_info(table_name);
```

Inspect the schema of `students`, `courses`, `enrollments`, `payments`.

Also inspect foreign keys using:

```sql
PRAGMA foreign_key_list(table_name);
```

---

## 6. Expected SQL Queries

Learners should write and run these queries:

```sql
SELECT * FROM students;

SELECT student_name, email, city
FROM students;

SELECT *
FROM students
WHERE city = 'Patna';

SELECT *
FROM courses
WHERE fee > 7000;

SELECT *
FROM courses
WHERE level = 'Beginner';

SELECT *
FROM students
ORDER BY student_name ASC;

SELECT course_name, fee
FROM courses
ORDER BY fee DESC
LIMIT 3;

SELECT DISTINCT city
FROM students;

SELECT *
FROM payments
WHERE payment_status = 'Pending';

SELECT *
FROM enrollments
WHERE status = 'Active';
```

---

## 7. Expected Python Functions

Create reusable Python functions:

```python
def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_query(conn, sql, params=None):
    if params is None:
        params = []
    cursor = conn.execute(sql, params)
    conn.commit()
    return cursor


def read_query(conn, sql, params=None):
    if params is None:
        params = []
    return pd.read_sql_query(sql, conn, params=params)
```

---

## 8. Final Output Expected

At the end of the hands-on assignment, learners should submit:

1. SQLite database file: `training_academy.db`
2. Python notebook or Python script
3. SQL table creation script
4. Sample data insertion script
5. Output screenshots or displayed DataFrames
6. Answers to all SQL query tasks
7. Constraint testing output
8. Short explanation of schema and relationships

## 9. Evaluation Checklist

| Evaluation Area | Requirement |
|---|---|
| RDBMS understanding | Tables and relationships are correctly explained |
| Schema design | All six tables are created properly |
| Primary keys | Each table has a valid primary key |
| Foreign keys | Relationships are correctly implemented |
| Constraints | `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT` are used |
| Sample data | Correct sample data inserted |
| Basic SQL | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `DISTINCT` used |
| CRUD | `INSERT`, `UPDATE`, `DELETE` performed from Python |
| Constraint testing | Invalid records are blocked |
| Python integration | SQLite connection and Pandas display are working |
| Code quality | Code is clean, readable, and reusable |

## 10. Mini Viva / Concept Questions

1. What is an RDBMS?
2. What is the difference between a table and a schema?
3. What is a primary key?
4. What is a foreign key?
5. Why do we use constraints?
6. Why should email be marked as `UNIQUE`?
7. Why is `UNIQUE(student_id, course_id)` used in the `enrollments` table?
8. Why should foreign keys be enabled in SQLite?
9. What is the purpose of `WHERE`?
10. What is the difference between `UPDATE` and `DELETE`?
11. Why are parameterized queries safer?
12. Why should parent table records be inserted before child table records?

## 11. Bonus Task

Add a new table named `course_feedback`:

| Column Name | Data Type | Constraint |
|---|---|---|
| `feedback_id` | INTEGER | PRIMARY KEY |
| `enrollment_id` | INTEGER | FOREIGN KEY |
| `rating` | INTEGER | CHECK `rating BETWEEN 1 AND 5` |
| `comments` | TEXT | Optional |
| `feedback_date` | DATE | NOT NULL |

**Required Queries**

1. Insert 3 feedback records.
2. Show all feedback.
3. Show feedback with rating greater than or equal to 4.
4. Try inserting rating as 6 and check whether the database rejects it.

## 12. Final Learning Outcome

After completing this hands-on problem, learners will be able to design a relational database from a business requirement, create tables with proper keys and constraints, insert and manage data, execute basic SQL queries, test database rules, and connect Python with SQLite for practical database operations.
