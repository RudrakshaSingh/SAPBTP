# 🗄️ Unit 2 — RDBMS Concepts & SQL (MySQL)

> **Module**: Module 2 — Fundamentals  
> **Duration**: Day 2–4 (24 hours)  
> **Dates**: 30-Jun-2026, 01-Jul-2026, 02-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — Database Fundamentals

### Q1. What is a database? Why do we need databases?

**A:** A **database** is an organized collection of structured data stored electronically. It allows efficient storage, retrieval, modification, and deletion of data.

**Why we need databases:**
- **Persistent storage** — Data survives application restarts (unlike variables in memory).
- **Structured access** — Query data using SQL instead of manually searching files.
- **Concurrent access** — Multiple users can read/write data simultaneously.
- **Data integrity** — Constraints ensure data is valid and consistent.
- **Security** — Role-based access control limits who can see/modify data.
- **Scalability** — Handle millions of records efficiently.

**Without a database:** You'd store data in flat files (CSV, JSON) — no indexing, no queries, no concurrency control. Doesn't scale.

---

### Q2. What is a DBMS vs. RDBMS?

**A:**

| Aspect | DBMS (Database Management System) | RDBMS (Relational DBMS) |
|--------|-----------------------------------|-------------------------|
| **Data model** | Data stored in files (hierarchical, network) | Data stored in **tables** with rows and columns |
| **Relationships** | No standard way to relate data | **Foreign keys** define relationships between tables |
| **Query language** | Varies | **SQL** (Structured Query Language) |
| **ACID compliance** | Not guaranteed | Yes (Atomicity, Consistency, Isolation, Durability) |
| **Normalization** | Not required | Normalization reduces redundancy |
| **Examples** | XML databases, flat file systems | **MySQL**, PostgreSQL, Oracle, SAP HANA, SQL Server |

**Key point:** All RDBMS are DBMS, but not all DBMS are RDBMS. The "R" (Relational) is what makes it special — data is organized in **relations (tables)** connected by **keys**.

---

### Q3. What is a relational database? Explain with an example.

**A:** A **relational database** organizes data into **tables (relations)** where each table has **rows (records/tuples)** and **columns (fields/attributes)**. Tables are connected through **keys**.

**Example — Employee Management System:**

**`departments` table:**
| dept_id | dept_name |
|---------|-----------|
| 1 | Engineering |
| 2 | HR |
| 3 | Finance |

**`employees` table:**
| emp_id | name | dept_id | salary |
|--------|------|---------|--------|
| 101 | Rudraksha | 1 | 85000 |
| 102 | Priya | 2 | 72000 |
| 103 | Amit | 1 | 90000 |

Here, `dept_id` in the `employees` table is a **foreign key** referencing `departments.dept_id`. This creates a **relationship** — we know which department each employee belongs to.

---

### Q4. What is a primary key? What is a foreign key?

**A:**

| Key Type | Definition | Rules | Example |
|----------|-----------|-------|---------|
| **Primary Key** | Uniquely identifies each row in a table | Must be unique, cannot be NULL, one per table | `emp_id` in employees table |
| **Foreign Key** | A column that references the primary key of another table | Creates a relationship between tables; can be NULL | `dept_id` in employees table → references `departments.dept_id` |
| **Composite Key** | A primary key made of two or more columns | Together they are unique | `(student_id, course_id)` in an enrollment table |
| **Candidate Key** | Any column(s) that could serve as primary key | Table may have multiple candidates; one is chosen as PK | `emp_id` and `email` could both be candidate keys |
| **Unique Key** | Ensures all values in a column are unique | Similar to PK but allows one NULL value | `email` column |

```sql
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,           -- Primary Key
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,        -- Unique Key
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)  -- Foreign Key
);
```

---

### Q5. What is normalization? Explain 1NF, 2NF, and 3NF.

**A:** **Normalization** is the process of organizing a database to **reduce data redundancy** and **improve data integrity** by splitting tables and defining relationships.

**1NF (First Normal Form):**
- Each column contains **atomic (indivisible) values**.
- No repeating groups or arrays.

```
❌ BAD: | name | phones          |
        | John | 9876, 1234      |  ← multiple values in one cell

✅ 1NF: | name | phone |
        | John | 9876  |
        | John | 1234  |
```

**2NF (Second Normal Form):**
- Must be in 1NF.
- No **partial dependency** — every non-key column depends on the **entire** primary key (relevant for composite keys).

```
❌ BAD (composite PK: student_id + course_id):
| student_id | course_id | student_name | grade |
student_name depends only on student_id, not on course_id → partial dependency

✅ 2NF: Split into two tables:
Students: | student_id | student_name |
Grades:   | student_id | course_id | grade |
```

**3NF (Third Normal Form):**
- Must be in 2NF.
- No **transitive dependency** — non-key columns should not depend on other non-key columns.

```
❌ BAD:
| emp_id | dept_id | dept_name |
dept_name depends on dept_id, not emp_id → transitive dependency

✅ 3NF: Split into:
Employees:   | emp_id | dept_id |
Departments: | dept_id | dept_name |
```

---

### Q6. What is denormalization? When would you use it?

**A:** **Denormalization** is the intentional introduction of redundancy into a database (the opposite of normalization) to **improve read performance**.

**When to use:**
- **Read-heavy workloads** — If you're doing many JOINs on every read, denormalization avoids expensive joins.
- **Reporting/analytics** — Data warehouses often denormalize for faster queries.
- **Caching** — Store computed values instead of recalculating every time.

**Trade-off:**

| Aspect | Normalized | Denormalized |
|--------|-----------|-------------|
| Redundancy | Low | High |
| Write performance | Fast (update one place) | Slow (update multiple places) |
| Read performance | Slow (many JOINs) | Fast (fewer JOINs) |
| Data integrity | High | Risk of inconsistency |

**Example:** Instead of JOINing `orders` + `customers` every time, store `customer_name` directly in the `orders` table.

---

### Q7. What is ACID in databases?

**A:** **ACID** properties ensure database transactions are reliable:

| Property | Meaning | Example |
|----------|---------|---------|
| **Atomicity** | A transaction is all-or-nothing; if any part fails, the entire transaction is rolled back | Bank transfer: debit AND credit must both succeed or both fail |
| **Consistency** | Transaction moves the database from one valid state to another | Balance can't go negative if there's a constraint |
| **Isolation** | Concurrent transactions don't interfere with each other | Two people transferring from the same account don't see each other's partial changes |
| **Durability** | Once a transaction is committed, it's permanently saved even if the system crashes | Data written to disk/WAL before confirming commit |

```sql
START TRANSACTION;
UPDATE accounts SET balance = balance - 500 WHERE id = 1;  -- Debit
UPDATE accounts SET balance = balance + 500 WHERE id = 2;  -- Credit
COMMIT;  -- Both succeed → Atomic
-- If any fails → ROLLBACK; → Neither takes effect
```

---

## 🔹 Section 2 — SQL Fundamentals

### Q8. What is SQL? What are the different categories of SQL commands?

**A:** **SQL (Structured Query Language)** is the standard language for interacting with relational databases.

| Category | Full Form | Purpose | Commands |
|----------|-----------|---------|----------|
| **DDL** | Data Definition Language | Define/modify database structure | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` |
| **DML** | Data Manipulation Language | Insert/update/delete data | `INSERT`, `UPDATE`, `DELETE` |
| **DQL** | Data Query Language | Query/retrieve data | `SELECT` |
| **DCL** | Data Control Language | Control access permissions | `GRANT`, `REVOKE` |
| **TCL** | Transaction Control Language | Manage transactions | `COMMIT`, `ROLLBACK`, `SAVEPOINT` |

---

### Q9. Write SQL to create a table, insert data, and query it.

**A:**

```sql
-- DDL: Create table
CREATE TABLE employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department VARCHAR(50),
    salary DECIMAL(10, 2) DEFAULT 0.00,
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- DML: Insert data
INSERT INTO employees (name, email, department, salary, hire_date)
VALUES
    ('Rudraksha', 'rudra@company.com', 'Engineering', 85000, '2025-01-15'),
    ('Priya', 'priya@company.com', 'HR', 72000, '2025-03-01'),
    ('Amit', 'amit@company.com', 'Engineering', 90000, '2024-11-20');

-- DQL: Query data
SELECT name, salary FROM employees WHERE department = 'Engineering';
```

**Output:**
| name | salary |
|------|--------|
| Rudraksha | 85000.00 |
| Amit | 90000.00 |

---

### Q10. Explain SELECT, WHERE, ORDER BY, LIMIT, and DISTINCT.

**A:**

```sql
-- SELECT: Choose which columns to retrieve
SELECT name, salary FROM employees;

-- WHERE: Filter rows based on conditions
SELECT * FROM employees WHERE salary > 75000;

-- AND, OR, NOT: Combine conditions
SELECT * FROM employees WHERE department = 'Engineering' AND salary > 80000;

-- ORDER BY: Sort results (ASC default, DESC for descending)
SELECT * FROM employees ORDER BY salary DESC;

-- LIMIT: Restrict number of rows returned
SELECT * FROM employees ORDER BY salary DESC LIMIT 5;

-- DISTINCT: Remove duplicate values
SELECT DISTINCT department FROM employees;

-- Combining all:
SELECT DISTINCT department, name, salary
FROM employees
WHERE salary > 50000
ORDER BY salary DESC
LIMIT 10;
```

**Execution order** (how SQL processes a query):
```
FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

---

### Q11. What are SQL operators? List the main types.

**A:**

| Type | Operators | Example |
|------|----------|---------|
| **Comparison** | `=`, `!=` / `<>`, `>`, `<`, `>=`, `<=` | `WHERE salary > 70000` |
| **Logical** | `AND`, `OR`, `NOT` | `WHERE dept = 'HR' AND salary > 50000` |
| **Range** | `BETWEEN` | `WHERE salary BETWEEN 60000 AND 90000` |
| **Pattern** | `LIKE` | `WHERE name LIKE 'R%'` (starts with R) |
| **List** | `IN` | `WHERE dept IN ('HR', 'Finance')` |
| **NULL check** | `IS NULL`, `IS NOT NULL` | `WHERE email IS NOT NULL` |
| **Arithmetic** | `+`, `-`, `*`, `/`, `%` | `SELECT salary * 1.1 AS raised_salary` |

**LIKE wildcards:**
- `%` — matches any number of characters: `'R%'` matches "Rudraksha", "Raj"
- `_` — matches exactly one character: `'_mit'` matches "Amit"

---

### Q12. Explain UPDATE and DELETE with examples.

**A:**

```sql
-- UPDATE: Modify existing data
UPDATE employees
SET salary = 95000, department = 'Senior Engineering'
WHERE emp_id = 103;

-- ⚠️ ALWAYS use WHERE with UPDATE! Without it, ALL rows are updated:
UPDATE employees SET salary = 0;  -- DANGER: Sets everyone's salary to 0!

-- DELETE: Remove rows
DELETE FROM employees WHERE emp_id = 102;

-- ⚠️ ALWAYS use WHERE with DELETE! Without it, ALL rows are deleted:
DELETE FROM employees;  -- DANGER: Deletes all employees!

-- TRUNCATE vs DELETE:
TRUNCATE TABLE employees;  -- Removes ALL rows (faster, can't rollback, resets AUTO_INCREMENT)
DELETE FROM employees;      -- Removes ALL rows (slower, can rollback, keeps AUTO_INCREMENT)
```

---

## 🔹 Section 3 — SQL Joins

### Q13. What are SQL JOINs? Explain each type with diagrams.

**A:** **JOINs** combine rows from two or more tables based on a related column.

**Sample tables:**

`employees`:
| emp_id | name | dept_id |
|--------|------|---------|
| 1 | Rudraksha | 10 |
| 2 | Priya | 20 |
| 3 | Amit | NULL |

`departments`:
| dept_id | dept_name |
|---------|-----------|
| 10 | Engineering |
| 20 | HR |
| 30 | Finance |

---

**INNER JOIN** — Only matching rows from both tables:
```sql
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;
```
| name | dept_name |
|------|-----------|
| Rudraksha | Engineering |
| Priya | HR |

*(Amit excluded — no matching dept_id; Finance excluded — no matching employee)*

---

**LEFT JOIN (LEFT OUTER JOIN)** — All rows from left table + matching from right:
```sql
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;
```
| name | dept_name |
|------|-----------|
| Rudraksha | Engineering |
| Priya | HR |
| Amit | NULL |

*(Amit included with NULL for dept_name)*

---

**RIGHT JOIN (RIGHT OUTER JOIN)** — All rows from right table + matching from left:
```sql
SELECT e.name, d.dept_name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.dept_id;
```
| name | dept_name |
|------|-----------|
| Rudraksha | Engineering |
| Priya | HR |
| NULL | Finance |

*(Finance included with NULL for name)*

---

**FULL OUTER JOIN** — All rows from both tables (MySQL doesn't support directly; use UNION):
```sql
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id
UNION
SELECT e.name, d.dept_name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.dept_id;
```
| name | dept_name |
|------|-----------|
| Rudraksha | Engineering |
| Priya | HR |
| Amit | NULL |
| NULL | Finance |

---

**CROSS JOIN** — Cartesian product (every row × every row):
```sql
SELECT e.name, d.dept_name FROM employees e CROSS JOIN departments d;
```
Produces 3 × 3 = 9 rows (every combination).

---

**SELF JOIN** — A table joined with itself:
```sql
-- Find employees and their managers (manager_id references emp_id)
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.emp_id;
```

---

### Q14. What is the difference between INNER JOIN and LEFT JOIN?

**A:**

| Aspect | INNER JOIN | LEFT JOIN |
|--------|-----------|-----------|
| Returns | Only rows with matches in BOTH tables | ALL rows from left + matches from right |
| Unmatched rows | Excluded | Included with NULLs for right table columns |
| Use case | "Show me employees who HAVE a department" | "Show me ALL employees, even those without a department" |
| Performance | Generally faster (fewer rows) | Slightly slower (more rows) |

**Rule of thumb:** Use INNER JOIN when you only want matching data. Use LEFT JOIN when you want to keep all records from one table regardless of matches.

---

### Q15. What is a NATURAL JOIN? What is USING clause?

**A:**

```sql
-- NATURAL JOIN: Automatically joins on columns with the SAME NAME in both tables
SELECT * FROM employees NATURAL JOIN departments;
-- Equivalent to: JOIN ON employees.dept_id = departments.dept_id

-- USING clause: Explicitly specify the common column
SELECT * FROM employees JOIN departments USING (dept_id);
-- Cleaner than: ON employees.dept_id = departments.dept_id
```

**⚠️ NATURAL JOIN risk:** If tables share multiple column names, it joins on ALL of them — which may not be what you want. Use `USING` or explicit `ON` for clarity.

---

## 🔹 Section 4 — Aggregate Functions & GROUP BY

### Q16. What are aggregate functions in SQL?

**A:** **Aggregate functions** perform calculations on a set of rows and return a single value.

| Function | Purpose | Example | Result |
|----------|---------|---------|--------|
| `COUNT()` | Count rows | `SELECT COUNT(*) FROM employees` | 100 |
| `SUM()` | Total of values | `SELECT SUM(salary) FROM employees` | 8500000 |
| `AVG()` | Average value | `SELECT AVG(salary) FROM employees` | 85000 |
| `MAX()` | Maximum value | `SELECT MAX(salary) FROM employees` | 150000 |
| `MIN()` | Minimum value | `SELECT MIN(salary) FROM employees` | 45000 |

```sql
-- Multiple aggregates in one query
SELECT
    COUNT(*) AS total_employees,
    AVG(salary) AS avg_salary,
    MAX(salary) AS highest_salary,
    MIN(salary) AS lowest_salary,
    SUM(salary) AS total_payroll
FROM employees;
```

**Note:** `COUNT(*)` counts all rows including NULLs. `COUNT(column)` counts only non-NULL values.

---

### Q17. Explain GROUP BY and HAVING with examples.

**A:**

```sql
-- GROUP BY: Group rows that share a value, then apply aggregate functions
SELECT department, COUNT(*) AS emp_count, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;
```
| department | emp_count | avg_salary |
|-----------|-----------|------------|
| Engineering | 45 | 92000 |
| HR | 20 | 68000 |
| Finance | 15 | 78000 |

```sql
-- HAVING: Filter GROUPS (like WHERE, but for aggregated results)
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 75000;
```
| department | avg_salary |
|-----------|------------|
| Engineering | 92000 |
| Finance | 78000 |

**WHERE vs HAVING:**

| Aspect | WHERE | HAVING |
|--------|-------|--------|
| Filters | Individual rows | Grouped results |
| Used with | Any query | Only with GROUP BY |
| Aggregate functions | ❌ Cannot use | ✅ Can use |
| Execution order | Before grouping | After grouping |

```sql
-- Combined: WHERE filters rows first, then GROUP BY groups, then HAVING filters groups
SELECT department, AVG(salary)
FROM employees
WHERE is_active = TRUE          -- Filter: only active employees
GROUP BY department             -- Group by department
HAVING AVG(salary) > 70000;    -- Filter: only departments with avg > 70K
```

---

## 🔹 Section 5 — Subqueries & Advanced SQL

### Q18. What is a subquery? Explain with examples.

**A:** A **subquery** (nested query) is a query inside another query. The inner query runs first, and its result is used by the outer query.

```sql
-- Subquery in WHERE: Find employees earning more than the average
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- Subquery in FROM: Use subquery result as a temporary table
SELECT dept_avg.department, dept_avg.avg_sal
FROM (
    SELECT department, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department
) AS dept_avg
WHERE dept_avg.avg_sal > 75000;

-- Subquery with IN: Find employees in departments located in Mumbai
SELECT name FROM employees
WHERE dept_id IN (SELECT dept_id FROM departments WHERE location = 'Mumbai');

-- Correlated subquery: References outer query (runs once per outer row)
SELECT e.name, e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department = e.department
);
```

**Subquery vs JOIN:**

| Aspect | Subquery | JOIN |
|--------|---------|------|
| Readability | Often clearer for simple cases | Better for complex multi-table queries |
| Performance | Can be slower (especially correlated) | Generally optimized better by DB engine |
| Use case | Filter, calculate, check existence | Combine data from multiple tables |

---

### Q19. What are window functions? Explain ROW_NUMBER, RANK, DENSE_RANK.

**A:** **Window functions** perform calculations across a set of rows **related to the current row**, without collapsing them into groups (unlike GROUP BY).

```sql
-- ROW_NUMBER: Assigns unique sequential numbers
SELECT name, department, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num
FROM employees;
```
| name | department | salary | row_num |
|------|-----------|--------|---------|
| Amit | Engineering | 90000 | 1 |
| Rudraksha | Engineering | 85000 | 2 |
| Priya | HR | 72000 | 3 |

```sql
-- RANK vs DENSE_RANK (with ties):
SELECT name, salary,
       RANK() OVER (ORDER BY salary DESC) AS rank_val,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank_val
FROM employees;
```
| name | salary | rank_val | dense_rank_val |
|------|--------|----------|---------------|
| Amit | 90000 | 1 | 1 |
| Raj | 90000 | 1 | 1 |
| Rudraksha | 85000 | 3 | 2 |

**RANK** skips numbers after ties (1, 1, **3**). **DENSE_RANK** doesn't skip (1, 1, **2**).

```sql
-- PARTITION BY: Window function within groups
SELECT name, department, salary,
       ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;
```
This ranks employees **within each department** separately.

---

### Q20. What are Common Table Expressions (CTEs)?

**A:** A **CTE** (using `WITH` clause) creates a named temporary result set that exists only for the duration of a single query. It improves readability over nested subqueries.

```sql
-- CTE: Find departments with above-average salaries, then list their employees
WITH dept_avg AS (
    SELECT department, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department
),
company_avg AS (
    SELECT AVG(salary) AS overall_avg FROM employees
)
SELECT d.department, d.avg_salary, e.name, e.salary
FROM dept_avg d
JOIN employees e ON e.department = d.department
WHERE d.avg_salary > (SELECT overall_avg FROM company_avg);

-- Recursive CTE: Generate a sequence or traverse hierarchies
WITH RECURSIVE numbers AS (
    SELECT 1 AS n          -- Base case
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 10  -- Recursive case
)
SELECT n FROM numbers;
-- Returns: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
```

**CTE vs Subquery:**
- CTE is **named** and **reusable** within the same query.
- CTE is **more readable** for complex queries.
- CTE supports **recursion** — subqueries don't.

---

### Q21. Explain UNION, UNION ALL, INTERSECT, and EXCEPT.

**A:** **Set operations** combine results from multiple SELECT queries.

```sql
-- UNION: Combine results, removing duplicates
SELECT name FROM employees_mumbai
UNION
SELECT name FROM employees_delhi;

-- UNION ALL: Combine results, keeping duplicates (faster)
SELECT name FROM employees_mumbai
UNION ALL
SELECT name FROM employees_delhi;

-- INTERSECT: Only rows that appear in BOTH queries
SELECT name FROM employees_mumbai
INTERSECT
SELECT name FROM employees_delhi;
-- Returns employees who work in BOTH Mumbai and Delhi

-- EXCEPT (MINUS in Oracle): Rows in first query but NOT in second
SELECT name FROM employees_mumbai
EXCEPT
SELECT name FROM employees_delhi;
-- Returns employees in Mumbai who are NOT in Delhi
```

**Rules:**
- All queries must have the **same number of columns**.
- Corresponding columns must have **compatible data types**.
- `UNION` is slower than `UNION ALL` because it removes duplicates.

---

## 🔹 Section 6 — Indexes, Views, and Stored Procedures

### Q22. What is an index? Why are indexes important?

**A:** An **index** is a data structure (typically B-tree) that speeds up data retrieval by providing a shortcut to rows, similar to a book index.

```sql
-- Create an index
CREATE INDEX idx_department ON employees(department);

-- Create a unique index
CREATE UNIQUE INDEX idx_email ON employees(email);

-- Create a composite index
CREATE INDEX idx_dept_salary ON employees(department, salary);

-- Drop an index
DROP INDEX idx_department ON employees;
```

**How indexes speed up queries:**
```
Without index: Full table scan → check every row → O(N)
With index:    B-tree lookup → find matching rows → O(log N)
```

**When to use:**
- Columns used frequently in `WHERE`, `JOIN`, `ORDER BY`.
- Foreign key columns.
- Columns with high cardinality (many unique values).

**When NOT to use:**
- Small tables (full scan is fine).
- Columns that are rarely queried.
- Columns with low cardinality (e.g., boolean `is_active`).
- Tables with heavy INSERT/UPDATE (indexes slow down writes).

**Trade-off:** Indexes **speed up reads** but **slow down writes** (because the index must be updated on every insert/update/delete).

---

### Q23. What is a view? What is a materialized view?

**A:**

```sql
-- Create a VIEW: A virtual table based on a SELECT query
CREATE VIEW active_employees AS
SELECT emp_id, name, department, salary
FROM employees
WHERE is_active = TRUE;

-- Use the view like a table
SELECT * FROM active_employees WHERE department = 'Engineering';

-- Drop a view
DROP VIEW active_employees;
```

**View vs Materialized View:**

| Aspect | View | Materialized View |
|--------|------|-------------------|
| Storage | No data stored; query runs every time | Stores the result set on disk |
| Performance | Same as underlying query | Faster (pre-computed) |
| Freshness | Always up-to-date | May be stale; needs refresh |
| Write support | Can be updatable (simple views) | Read-only |
| Use case | Security (hide columns), simplify queries | Reporting, dashboards, complex aggregations |

**Note:** MySQL doesn't natively support materialized views. PostgreSQL, Oracle, and SAP HANA do.

---

### Q24. What is a stored procedure? What is a function?

**A:**

```sql
-- STORED PROCEDURE: A saved block of SQL that can be executed with parameters
DELIMITER //
CREATE PROCEDURE get_dept_employees(IN dept_name VARCHAR(50))
BEGIN
    SELECT name, salary
    FROM employees
    WHERE department = dept_name
    ORDER BY salary DESC;
END //
DELIMITER ;

-- Call the procedure
CALL get_dept_employees('Engineering');

-- FUNCTION: Returns a single value
DELIMITER //
CREATE FUNCTION get_tax(salary DECIMAL(10,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    RETURN salary * 0.30;
END //
DELIMITER ;

-- Use the function
SELECT name, salary, get_tax(salary) AS tax FROM employees;
```

**Procedure vs Function:**

| Aspect | Stored Procedure | Function |
|--------|-----------------|----------|
| Return value | Can return 0, 1, or multiple values (via OUT params) | Must return exactly one value |
| Usage | Called with `CALL` | Used in `SELECT`, `WHERE`, etc. |
| DML operations | Can INSERT, UPDATE, DELETE | Typically read-only |
| Transaction control | Can use COMMIT, ROLLBACK | Cannot |

---

### Q25. What are triggers in SQL?

**A:** A **trigger** is a stored procedure that **automatically executes** when a specific event occurs on a table (INSERT, UPDATE, DELETE).

```sql
-- Create a trigger: Log salary changes
CREATE TRIGGER salary_audit
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
    IF OLD.salary != NEW.salary THEN
        INSERT INTO salary_log (emp_id, old_salary, new_salary, changed_at)
        VALUES (OLD.emp_id, OLD.salary, NEW.salary, NOW());
    END IF;
END;
```

**Trigger types:**
- `BEFORE INSERT` — Run before a new row is inserted.
- `AFTER INSERT` — Run after a new row is inserted.
- `BEFORE UPDATE` — Run before a row is updated.
- `AFTER UPDATE` — Run after a row is updated.
- `BEFORE DELETE` — Run before a row is deleted.
- `AFTER DELETE` — Run after a row is deleted.

**`OLD` and `NEW` keywords:**
- `OLD.column` — The value before the change (available in UPDATE, DELETE triggers).
- `NEW.column` — The value after the change (available in INSERT, UPDATE triggers).

---

## 🔹 Section 7 — Transactions & Concurrency

### Q26. What is a database transaction?

**A:** A **transaction** is a sequence of one or more SQL operations treated as a **single logical unit of work**. Either ALL operations succeed (COMMIT) or ALL are undone (ROLLBACK).

```sql
START TRANSACTION;

-- Step 1: Deduct from sender
UPDATE accounts SET balance = balance - 1000 WHERE account_id = 'A001';

-- Step 2: Add to receiver
UPDATE accounts SET balance = balance + 1000 WHERE account_id = 'A002';

-- If both succeed:
COMMIT;

-- If anything fails:
-- ROLLBACK;  (undoes both operations)
```

**SAVEPOINT** — Create a point within a transaction to partially rollback:
```sql
START TRANSACTION;
INSERT INTO orders VALUES (...);
SAVEPOINT sp1;
INSERT INTO order_items VALUES (...);
-- Oops, wrong item:
ROLLBACK TO sp1;  -- Only undoes the order_items insert
INSERT INTO order_items VALUES (...);  -- Correct item
COMMIT;
```

---

### Q27. What are isolation levels? Explain read phenomena.

**A:** **Isolation levels** define how transactions interact with each other.

**Read phenomena (problems):**

| Phenomenon | Description |
|-----------|-------------|
| **Dirty Read** | Transaction A reads data modified by Transaction B BEFORE B commits. If B rolls back, A has read invalid data. |
| **Non-Repeatable Read** | Transaction A reads a row, Transaction B updates it and commits, Transaction A reads it again and gets a different value. |
| **Phantom Read** | Transaction A reads a set of rows matching a condition, Transaction B inserts a new row matching the condition, Transaction A re-reads and sees the new "phantom" row. |

**Isolation levels (MySQL/InnoDB):**

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Performance |
|-------|-----------|--------------------|--------------| ------------|
| **READ UNCOMMITTED** | ✅ Possible | ✅ Possible | ✅ Possible | Fastest |
| **READ COMMITTED** | ❌ Prevented | ✅ Possible | ✅ Possible | Fast |
| **REPEATABLE READ** (MySQL default) | ❌ Prevented | ❌ Prevented | ✅ Possible* | Moderate |
| **SERIALIZABLE** | ❌ Prevented | ❌ Prevented | ❌ Prevented | Slowest |

*MySQL's InnoDB actually prevents phantom reads at REPEATABLE READ level using gap locks.

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

---

## 🔹 Section 8 — MySQL Specifics & Data Types

### Q28. What are the main MySQL data types?

**A:**

**Numeric:**
| Type | Size | Range | Use Case |
|------|------|-------|----------|
| `TINYINT` | 1 byte | -128 to 127 | Boolean-like flags |
| `INT` | 4 bytes | -2B to 2B | IDs, counts |
| `BIGINT` | 8 bytes | Very large | Large IDs (Twitter snowflake) |
| `DECIMAL(p,s)` | Variable | Exact precision | Money, financial data |
| `FLOAT` / `DOUBLE` | 4/8 bytes | Approximate | Scientific data |

**String:**
| Type | Max Size | Use Case |
|------|----------|----------|
| `CHAR(n)` | 255 chars (fixed length) | Fixed-format codes (country code: 'IN') |
| `VARCHAR(n)` | 65,535 chars (variable) | Names, emails, descriptions |
| `TEXT` | 65,535 chars | Long text, articles |
| `LONGTEXT` | 4 GB | Very large text |
| `ENUM` | Predefined values | Status ('active', 'inactive') |

**Date/Time:**
| Type | Format | Example |
|------|--------|---------|
| `DATE` | YYYY-MM-DD | '2026-07-01' |
| `TIME` | HH:MM:SS | '14:30:00' |
| `DATETIME` | YYYY-MM-DD HH:MM:SS | '2026-07-01 14:30:00' |
| `TIMESTAMP` | Auto-updates, timezone-aware | Created_at, updated_at |

---

### Q29. What is the difference between CHAR and VARCHAR?

**A:**

| Aspect | CHAR(10) | VARCHAR(10) |
|--------|----------|-------------|
| Storage | Always 10 bytes (padded with spaces) | Actual length + 1-2 bytes |
| 'Hello' stored as | 'Hello     ' (5 chars + 5 spaces) | 'Hello' (5 chars + 1 byte for length) |
| Performance | Faster (fixed-length reads) | Slightly slower (variable length) |
| Use case | Fixed-length data (ISO codes, PINs) | Variable-length data (names, emails) |
| Max length | 255 | 65,535 |

**Rule:** Use `CHAR` for fixed-length data (state codes, currency codes). Use `VARCHAR` for everything else.

---

### Q30. What are constraints in MySQL?

**A:** **Constraints** enforce rules on data in a table to maintain data integrity.

```sql
CREATE TABLE employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,    -- PRIMARY KEY: unique + not null
    name VARCHAR(100) NOT NULL,               -- NOT NULL: cannot be empty
    email VARCHAR(100) UNIQUE,                -- UNIQUE: no duplicate emails
    salary DECIMAL(10,2) CHECK (salary > 0),  -- CHECK: salary must be positive
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)  -- FOREIGN KEY
        ON DELETE SET NULL     -- If department deleted, set dept_id to NULL
        ON UPDATE CASCADE      -- If dept_id changes, update here too
);
```

**Foreign Key actions (ON DELETE / ON UPDATE):**

| Action | Behavior |
|--------|---------|
| `CASCADE` | Delete/update child rows automatically |
| `SET NULL` | Set foreign key to NULL |
| `SET DEFAULT` | Set to default value |
| `RESTRICT` | Prevent the delete/update (default) |
| `NO ACTION` | Same as RESTRICT |

---

## 🔹 Section 9 — SQL in Data Engineering Context

### Q31. What is the difference between SQL and NoSQL?

**A:**

| Aspect | SQL (Relational) | NoSQL (Non-Relational) |
|--------|-----------------|----------------------|
| **Data model** | Tables with rows/columns | Document, Key-Value, Column-family, Graph |
| **Schema** | Fixed schema (defined upfront) | Flexible/schema-less |
| **Query language** | SQL (standardized) | Varies (MongoDB query, CQL, etc.) |
| **Scaling** | Vertical (scale up) | Horizontal (scale out) |
| **ACID** | Yes | Often eventual consistency (BASE) |
| **Best for** | Structured, relational data | Unstructured, high-volume, flexible data |
| **Examples** | MySQL, PostgreSQL, SAP HANA | MongoDB, Cassandra, Redis, DynamoDB |

**When to use SQL:** Banking, ERP (SAP), HR systems — structured data with strict integrity.
**When to use NoSQL:** Social media feeds, IoT data, real-time analytics — high volume, flexible schema.

---

### Q32. What is SAP HANA? How does it compare to MySQL?

**A:** **SAP HANA** is an **in-memory, column-oriented** relational database management system developed by SAP.

| Aspect | MySQL | SAP HANA |
|--------|-------|----------|
| **Storage** | Disk-based (with memory cache) | In-memory (primary storage in RAM) |
| **Orientation** | Row-oriented | Column-oriented |
| **Speed** | Fast for OLTP | Ultra-fast for both OLTP and OLAP |
| **Analytics** | Needs separate data warehouse | Built-in analytics engine |
| **Cost** | Free (open source) | Enterprise license (expensive) |
| **Cloud** | MySQL on any cloud | SAP HANA Cloud (managed service on BTP) |
| **AI/ML** | Limited | Built-in PAL (Predictive Analysis Library) |
| **Use case** | General purpose | SAP applications, enterprise analytics |

**Column-oriented advantage:** For analytics queries that aggregate large datasets (e.g., "sum of all salaries by department"), column storage reads only the needed columns — much faster than reading entire rows.

---

### Q33. What is ETL? How does SQL fit into data engineering?

**A:** **ETL = Extract, Transform, Load** — the process of moving data from source systems into a data warehouse.

| Phase | What Happens | SQL Role |
|-------|-------------|----------|
| **Extract** | Pull data from sources (databases, APIs, files) | `SELECT` queries, database connections |
| **Transform** | Clean, filter, aggregate, join, reshape data | `JOIN`, `GROUP BY`, `CASE WHEN`, functions |
| **Load** | Insert processed data into target system | `INSERT INTO`, `MERGE`, bulk loading |

```sql
-- Example: ETL to create a summary table
INSERT INTO monthly_sales_summary (month, region, total_sales, avg_order_value)
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    region,
    SUM(amount) AS total_sales,
    AVG(amount) AS avg_order_value
FROM orders
WHERE order_date >= '2026-01-01'
GROUP BY DATE_FORMAT(order_date, '%Y-%m'), region;
```

**SQL is the backbone of data engineering** — used in every phase of ETL and in data pipeline tools like Apache Spark SQL, dbt, Airflow.

---

### Q34. What are string functions in MySQL?

**A:**

```sql
-- CONCAT: Join strings
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM employees;

-- SUBSTRING: Extract part of a string
SELECT SUBSTRING(email, 1, 5) FROM employees;  -- First 5 chars

-- UPPER / LOWER: Case conversion
SELECT UPPER(name), LOWER(email) FROM employees;

-- LENGTH: Number of characters
SELECT name, LENGTH(name) AS name_length FROM employees;

-- TRIM: Remove whitespace
SELECT TRIM('  hello  ');  -- 'hello'
SELECT LTRIM('  hello'), RTRIM('hello  ');

-- REPLACE: Substitute text
SELECT REPLACE(phone, '-', '') FROM employees;  -- Remove dashes

-- LEFT / RIGHT: Extract from start/end
SELECT LEFT(name, 3), RIGHT(email, 10) FROM employees;

-- LOCATE / INSTR: Find position of substring
SELECT LOCATE('@', email) FROM employees;  -- Position of @
```

---

### Q35. What are date functions in MySQL?

**A:**

```sql
-- Current date/time
SELECT NOW();          -- '2026-07-01 14:30:00'
SELECT CURDATE();      -- '2026-07-01'
SELECT CURTIME();      -- '14:30:00'

-- Extract parts
SELECT YEAR(hire_date), MONTH(hire_date), DAY(hire_date) FROM employees;

-- Date arithmetic
SELECT DATE_ADD(hire_date, INTERVAL 90 DAY) AS probation_end FROM employees;
SELECT DATEDIFF(CURDATE(), hire_date) AS days_employed FROM employees;

-- Format dates
SELECT DATE_FORMAT(hire_date, '%d-%b-%Y') FROM employees;  -- '15-Jan-2025'

-- Timestamps
SELECT UNIX_TIMESTAMP();                    -- Epoch time
SELECT FROM_UNIXTIME(1719792000);           -- Convert epoch to datetime
```

---

### Q36. What is CASE WHEN in SQL?

**A:** **CASE WHEN** is SQL's if-else logic. It allows conditional expressions in SELECT, WHERE, ORDER BY, etc.

```sql
-- Simple CASE: Categorize salaries
SELECT name, salary,
    CASE
        WHEN salary >= 100000 THEN 'Senior'
        WHEN salary >= 70000 THEN 'Mid-Level'
        WHEN salary >= 40000 THEN 'Junior'
        ELSE 'Intern'
    END AS level
FROM employees;

-- CASE in aggregation
SELECT department,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) AS active_count,
    COUNT(CASE WHEN is_active = FALSE THEN 1 END) AS inactive_count
FROM employees
GROUP BY department;

-- CASE in ORDER BY
SELECT name, department FROM employees
ORDER BY
    CASE department
        WHEN 'Engineering' THEN 1
        WHEN 'Finance' THEN 2
        ELSE 3
    END;
```

---

### Q37. Explain COALESCE and IFNULL.

**A:**

```sql
-- IFNULL: Replace NULL with a default value (MySQL-specific)
SELECT name, IFNULL(phone, 'N/A') AS phone FROM employees;

-- COALESCE: Returns the first non-NULL value from a list (ANSI SQL standard)
SELECT name, COALESCE(mobile, landline, office_phone, 'No phone') AS contact
FROM employees;
-- Checks mobile first, then landline, then office_phone; if all NULL, returns 'No phone'

-- NULLIF: Returns NULL if two values are equal
SELECT NULLIF(bonus, 0) AS bonus FROM employees;
-- Returns NULL instead of 0 (useful to avoid division by zero)
```

---

### Q38. How do you optimize slow SQL queries?

**A:**

| Technique | What It Does | Example |
|-----------|-------------|---------|
| **Use indexes** | Speed up WHERE and JOIN lookups | `CREATE INDEX idx_dept ON employees(department)` |
| **EXPLAIN** | Analyze query execution plan | `EXPLAIN SELECT * FROM employees WHERE dept = 'HR'` |
| **Avoid SELECT *** | Fetch only needed columns | `SELECT name, salary` instead of `SELECT *` |
| **Limit results** | Don't fetch more than needed | `LIMIT 100` |
| **Avoid functions on indexed columns** | Prevents index usage | ❌ `WHERE YEAR(hire_date) = 2025` → ✅ `WHERE hire_date BETWEEN '2025-01-01' AND '2025-12-31'` |
| **Use JOINs instead of subqueries** | Often more optimized by the engine | Replace `WHERE IN (SELECT ...)` with `JOIN` |
| **Batch operations** | Insert/update in bulk | `INSERT INTO ... VALUES (...), (...), (...)` |
| **Proper data types** | Smaller types = faster reads | Use `INT` not `BIGINT` for small IDs |

**EXPLAIN output example:**
```sql
EXPLAIN SELECT * FROM employees WHERE department = 'Engineering';
-- Shows: type=ref, key=idx_department, rows=45 → Using index!
-- If type=ALL → Full table scan → Need an index!
```

---

## 🔹 Section 10 — Quick Fire Questions

### Q39. What is the difference between DELETE, TRUNCATE, and DROP?

**A:**

| Command | What It Does | Rollback? | Speed | Triggers? | Auto-increment |
|---------|-------------|-----------|-------|-----------|----------------|
| `DELETE` | Removes specific rows (with WHERE) | ✅ Yes | Slow | ✅ Fires | Keeps counter |
| `TRUNCATE` | Removes ALL rows | ❌ No | Fast | ❌ Doesn't fire | Resets counter |
| `DROP` | Removes the entire table (structure + data) | ❌ No | Fastest | N/A | N/A |

---

### Q40. What is the difference between WHERE and HAVING?

**A:**
- `WHERE` filters **individual rows** BEFORE grouping.
- `HAVING` filters **groups** AFTER `GROUP BY`.

```sql
SELECT department, AVG(salary) AS avg_sal
FROM employees
WHERE is_active = TRUE       -- Filter rows first
GROUP BY department
HAVING AVG(salary) > 70000;  -- Filter groups after
```

---

### Q41. What is a schema in MySQL?

**A:** In MySQL, a **schema** is essentially the same as a **database**. It's a logical container that holds tables, views, procedures, and other database objects.

```sql
CREATE SCHEMA company_db;     -- Same as CREATE DATABASE
USE company_db;               -- Switch to this schema
SHOW TABLES;                  -- List tables in current schema
```

In other RDBMS (PostgreSQL, Oracle, SAP HANA), a schema is a namespace **within** a database — one database can have multiple schemas.

---

### Q42. What is ALTER TABLE? Give examples.

**A:**

```sql
-- Add a column
ALTER TABLE employees ADD COLUMN phone VARCHAR(15);

-- Modify a column's data type
ALTER TABLE employees MODIFY COLUMN salary DECIMAL(12, 2);

-- Rename a column
ALTER TABLE employees CHANGE COLUMN phone mobile VARCHAR(15);

-- Drop a column
ALTER TABLE employees DROP COLUMN mobile;

-- Add a constraint
ALTER TABLE employees ADD CONSTRAINT chk_salary CHECK (salary > 0);

-- Rename the table
ALTER TABLE employees RENAME TO staff;
```

---

### Q43. What is AUTO_INCREMENT?

**A:** `AUTO_INCREMENT` automatically generates a unique integer for each new row. Used for primary keys.

```sql
CREATE TABLE employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,  -- Starts at 1, increments by 1
    name VARCHAR(100)
);

INSERT INTO employees (name) VALUES ('Rudraksha');  -- emp_id = 1
INSERT INTO employees (name) VALUES ('Priya');      -- emp_id = 2

-- Check current value
SELECT AUTO_INCREMENT FROM information_schema.TABLES
WHERE TABLE_NAME = 'employees';

-- Reset AUTO_INCREMENT
ALTER TABLE employees AUTO_INCREMENT = 100;
```

---

### Q44. How do you handle NULL values in SQL?

**A:**

```sql
-- Check for NULL (don't use = NULL!)
SELECT * FROM employees WHERE phone IS NULL;
SELECT * FROM employees WHERE phone IS NOT NULL;

-- ❌ WRONG: WHERE phone = NULL    (always returns empty!)
-- ✅ RIGHT: WHERE phone IS NULL

-- COALESCE: Replace NULL with a default
SELECT name, COALESCE(phone, 'No phone') FROM employees;

-- NULL in calculations: Any arithmetic with NULL = NULL
SELECT 100 + NULL;  -- NULL (not 100!)

-- COUNT and NULL:
SELECT COUNT(*);        -- Counts ALL rows (including NULLs)
SELECT COUNT(phone);    -- Counts only non-NULL phone values
```

---

### Q45. Write a query to find the second highest salary.

**A:**

```sql
-- Method 1: LIMIT with OFFSET
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;

-- Method 2: Subquery
SELECT MAX(salary) AS second_highest
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Method 3: DENSE_RANK (get Nth highest)
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM employees
) ranked
WHERE rnk = 2;
```

---

> **💡 Viva Tip:** For SQL questions, always be ready to **write queries on the spot**. Practice writing JOINs, GROUP BY with HAVING, subqueries, and window functions without looking at references. Evaluators often ask you to solve a problem by writing SQL live.

---

*End of Unit 2 — RDBMS Concepts & SQL (MySQL) 🗄️*
