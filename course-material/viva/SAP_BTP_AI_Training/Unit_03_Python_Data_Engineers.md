# 🐍 Unit 3 — Python for Data Engineers

> **Module**: Module 2 — Fundamentals  
> **Duration**: Day 5–8 (32 hours)  
> **Dates**: 03-Jul-2026, 06-Jul-2026, 07-Jul-2026, 08-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — Python Basics

### Q1. What is Python? Why is it the language of choice for AI/ML and data engineering?

**A:** **Python** is a high-level, interpreted, dynamically-typed, general-purpose programming language created by Guido van Rossum (1991).

**Why it dominates AI/ML/Data Engineering:**

| Reason | Explanation |
|--------|-------------|
| **Simple syntax** | Reads like English; fast to prototype |
| **Rich ecosystem** | NumPy, Pandas, Scikit-learn, TensorFlow, PyTorch, LangChain |
| **Community** | Largest open-source community; endless tutorials and packages |
| **Versatility** | Web apps (FastAPI/Django), scripting, data science, automation |
| **Integration** | APIs, databases, cloud services all have Python SDKs |
| **Jupyter Notebooks** | Interactive development for data exploration |

---

### Q2. What are Python's key features?

**A:**
1. **Interpreted** — No compilation step; runs line by line via Python interpreter.
2. **Dynamically typed** — Variables don't need type declarations (`x = 5` then `x = "hello"` is valid).
3. **Indentation-based** — Uses whitespace for blocks (no `{}` like Java/C++).
4. **Object-oriented** — Everything is an object; supports classes, inheritance, polymorphism.
5. **Garbage collected** — Automatic memory management (reference counting + cyclic garbage collector).
6. **Cross-platform** — Runs on Windows, macOS, Linux.
7. **Extensive standard library** — `os`, `json`, `math`, `datetime`, `re`, `http`, etc. — "batteries included."

---

### Q3. What are Python data types? List all major ones.

**A:**

| Category | Type | Example | Mutable? |
|----------|------|---------|----------|
| **Numeric** | `int` | `x = 42` | ❌ |
| | `float` | `y = 3.14` | ❌ |
| | `complex` | `z = 2 + 3j` | ❌ |
| **Boolean** | `bool` | `flag = True` | ❌ |
| **String** | `str` | `s = "hello"` | ❌ |
| **Sequence** | `list` | `[1, 2, 3]` | ✅ |
| | `tuple` | `(1, 2, 3)` | ❌ |
| | `range` | `range(10)` | ❌ |
| **Mapping** | `dict` | `{"a": 1, "b": 2}` | ✅ |
| **Set** | `set` | `{1, 2, 3}` | ✅ |
| | `frozenset` | `frozenset({1, 2})` | ❌ |
| **None** | `NoneType` | `x = None` | ❌ |
| **Binary** | `bytes` | `b"hello"` | ❌ |
| | `bytearray` | `bytearray(5)` | ✅ |

**Mutable** = Can be modified after creation. **Immutable** = Cannot be changed; a new object is created instead.

---

### Q4. Explain the difference between list, tuple, set, and dictionary.

**A:**

| Feature | List | Tuple | Set | Dictionary |
|---------|------|-------|-----|------------|
| **Syntax** | `[1, 2, 3]` | `(1, 2, 3)` | `{1, 2, 3}` | `{"a": 1}` |
| **Ordered** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes (3.7+) |
| **Mutable** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Duplicates** | ✅ Allows | ✅ Allows | ❌ No duplicates | Keys: ❌ No; Values: ✅ Yes |
| **Indexed** | ✅ Yes | ✅ Yes | ❌ No | By key |
| **Use case** | General collection | Immutable data, dict keys, function returns | Unique values, set operations | Key-value mapping |
| **Performance** | O(n) search | O(n) search | O(1) lookup | O(1) lookup by key |

```python
my_list = [1, 2, 3, 2]          # Ordered, mutable, allows duplicates
my_tuple = (1, 2, 3, 2)         # Ordered, immutable, allows duplicates
my_set = {1, 2, 3}              # Unordered, no duplicates
my_dict = {"name": "Rudra", "age": 22}  # Key-value pairs
```

---

### Q5. What is the difference between `==` and `is` in Python?

**A:**

| Operator | Checks | Example |
|----------|--------|---------|
| `==` | **Value equality** — do they have the same content? | `[1,2] == [1,2]` → `True` |
| `is` | **Identity** — are they the exact same object in memory? | `[1,2] is [1,2]` → `False` |

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

a == b   # True  (same content)
a is b   # False (different objects)
a is c   # True  (c points to same object as a)

# For small integers and interned strings, Python caches them:
x = 256
y = 256
x is y   # True  (Python caches integers -5 to 256)
```

---

### Q6. What are mutable vs immutable types? Why does it matter?

**A:**

| Immutable | Mutable |
|-----------|---------|
| `int`, `float`, `str`, `tuple`, `frozenset`, `bool` | `list`, `dict`, `set`, `bytearray` |
| Modifying creates a new object | Modifying changes the object in-place |
| Can be dict keys or set members | Cannot be dict keys |
| Thread-safe | Not thread-safe |

```python
# Immutable: string
s = "hello"
s[0] = "H"  # ❌ TypeError! Strings are immutable

# Mutable: list
lst = [1, 2, 3]
lst[0] = 10  # ✅ Works! Lists are mutable → [10, 2, 3]

# ⚠️ Gotcha with mutable default arguments:
def add_item(item, items=[]):  # BAD! Default list is shared
    items.append(item)
    return items

add_item(1)  # [1]
add_item(2)  # [1, 2] ← NOT [2]! Same list object is reused

# Fix:
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## 🔹 Section 2 — Control Flow & Functions

### Q7. Explain if/elif/else, for loops, and while loops.

**A:**

```python
# if/elif/else
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

# Ternary operator
grade = "Pass" if score >= 60 else "Fail"

# for loop (iterates over sequences)
for i in range(5):           # 0, 1, 2, 3, 4
    print(i)

for name in ["Rudra", "Priya", "Amit"]:
    print(name)

for key, value in my_dict.items():
    print(f"{key}: {value}")

# while loop (repeats while condition is true)
count = 0
while count < 5:
    print(count)
    count += 1

# break, continue, else
for n in range(10):
    if n == 3:
        continue    # Skip 3
    if n == 7:
        break       # Stop at 7
    print(n)        # Prints: 0, 1, 2, 4, 5, 6
else:
    print("Completed")  # Only runs if loop finished without break
```

---

### Q8. What are functions in Python? Explain `*args` and `**kwargs`.

**A:**

```python
# Basic function
def greet(name: str) -> str:
    """Returns a greeting string."""
    return f"Hello, {name}!"

# Default parameters
def connect(host="localhost", port=3306):
    print(f"Connecting to {host}:{port}")

# *args: Variable positional arguments (tuple)
def add(*args):
    return sum(args)
add(1, 2, 3, 4)  # 10

# **kwargs: Variable keyword arguments (dict)
def create_user(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")
create_user(name="Rudra", age=22, role="Engineer")

# Both together (order matters: regular → *args → **kwargs)
def func(a, b, *args, **kwargs):
    print(a, b, args, kwargs)
func(1, 2, 3, 4, x=5, y=6)
# Output: 1 2 (3, 4) {'x': 5, 'y': 6}
```

---

### Q9. What is a lambda function? When should you use it?

**A:** A **lambda** is an anonymous (unnamed) function defined in a single line.

```python
# Regular function
def square(x):
    return x ** 2

# Equivalent lambda
square = lambda x: x ** 2

# Common use cases:
# 1. Sorting with custom key
employees = [("Rudra", 85000), ("Priya", 72000), ("Amit", 90000)]
employees.sort(key=lambda emp: emp[1])  # Sort by salary

# 2. map, filter, reduce
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))      # [1, 4, 9, 16, 25]
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

from functools import reduce
total = reduce(lambda a, b: a + b, numbers)         # 15
```

**When to use:** For simple, one-time functions — especially as arguments to `sort()`, `map()`, `filter()`. For complex logic, use a regular `def` function.

---

### Q10. What are decorators in Python?

**A:** A **decorator** is a function that takes another function and extends its behavior without modifying it.

```python
# Basic decorator
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@logger
def add(a, b):
    return a + b

add(3, 5)
# Output:
# Calling add
# add returned 8

# Decorator with arguments
def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def say_hello():
    print("Hello!")

say_hello()  # Prints "Hello!" three times

# Real-world usage: FastAPI uses decorators for routing
# @app.get("/health")  ← This is a decorator!
```

---

### Q11. What is a generator? How is it different from a regular function?

**A:** A **generator** is a function that yields values one at a time using `yield` instead of `return`. It's memory-efficient for large datasets.

```python
# Regular function: creates entire list in memory
def get_squares(n):
    result = []
    for i in range(n):
        result.append(i ** 2)
    return result  # All 1 million items in memory at once

# Generator: yields one item at a time
def gen_squares(n):
    for i in range(n):
        yield i ** 2  # Pauses here, resumes on next iteration

# Usage
for sq in gen_squares(1000000):  # Only one value in memory at a time
    if sq > 100:
        break

# Generator expression (like list comprehension but with ())
squares = (x**2 for x in range(1000000))  # Generator object
```

**Generator vs List:**

| Aspect | List | Generator |
|--------|------|-----------|
| Memory | Entire list in memory | One item at a time |
| Speed (creation) | Slow (computes all) | Fast (lazy evaluation) |
| Reusable | Yes (iterate multiple times) | No (exhausted after one pass) |
| Use case | Small datasets | Large/infinite datasets, streaming |

---

## 🔹 Section 3 — Object-Oriented Programming (OOP)

### Q12. What is OOP? Explain the four pillars.

**A:** **OOP (Object-Oriented Programming)** organizes code around **objects** — instances of classes that bundle data (attributes) and behavior (methods).

**Four pillars:**

| Pillar | Meaning | Python Example |
|--------|---------|----------------|
| **Encapsulation** | Bundle data + methods; hide internals | Private attributes with `_` or `__` prefix |
| **Abstraction** | Show only what's necessary; hide complexity | Abstract classes (`abc` module) |
| **Inheritance** | A class derives from another class | `class Dog(Animal):` |
| **Polymorphism** | Same method name, different behavior | `animal.speak()` — Dog barks, Cat meows |

```python
from abc import ABC, abstractmethod

# Abstraction
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

# Inheritance + Encapsulation
class Rectangle(Shape):
    def __init__(self, width, height):
        self.__width = width    # Private attribute
        self.__height = height

    def area(self):             # Polymorphism
        return self.__width * self.__height

class Circle(Shape):
    def __init__(self, radius):
        self.__radius = radius

    def area(self):             # Same method name, different behavior
        return 3.14159 * self.__radius ** 2

# Polymorphism in action
shapes = [Rectangle(5, 3), Circle(7)]
for shape in shapes:
    print(shape.area())  # Calls the right area() method automatically
```

---

### Q13. What is `self` in Python classes?

**A:** `self` is a reference to the **current instance** of the class. It allows each object to maintain its own state.

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name       # Instance attribute
        self.salary = salary

    def raise_salary(self, amount):
        self.salary += amount  # self refers to the specific object

emp1 = Employee("Rudra", 85000)
emp2 = Employee("Priya", 72000)

emp1.raise_salary(5000)
print(emp1.salary)  # 90000
print(emp2.salary)  # 72000 (unchanged — different object)
```

**`self` is not a keyword** — it's a convention. You could call it `this` or anything, but `self` is the Python standard.

---

### Q14. What are `__init__`, `__str__`, and `__repr__` dunder methods?

**A:** **Dunder (double underscore) methods** are special methods that Python calls automatically.

```python
class Employee:
    def __init__(self, name, salary):
        """Constructor — called when creating an object."""
        self.name = name
        self.salary = salary

    def __str__(self):
        """Human-readable string — called by print() and str()."""
        return f"{self.name} (₹{self.salary:,})"

    def __repr__(self):
        """Developer-readable string — called by repr() and in REPL."""
        return f"Employee(name='{self.name}', salary={self.salary})"

    def __eq__(self, other):
        """Equality check — called by == operator."""
        return self.name == other.name and self.salary == other.salary

    def __len__(self):
        """Called by len()."""
        return len(self.name)

emp = Employee("Rudra", 85000)
print(emp)      # Rudra (₹85,000)      ← calls __str__
repr(emp)       # Employee(name='Rudra', salary=85000)  ← calls __repr__
```

---

## 🔹 Section 4 — File Handling & Data Processing

### Q15. How do you read and write files in Python?

**A:**

```python
# Reading a file
with open("data.txt", "r") as f:
    content = f.read()         # Read entire file as string
    # or
    lines = f.readlines()     # Read as list of lines
    # or
    for line in f:             # Memory-efficient line-by-line reading
        print(line.strip())

# Writing a file
with open("output.txt", "w") as f:      # "w" overwrites
    f.write("Hello\n")
    f.write("World\n")

with open("output.txt", "a") as f:      # "a" appends
    f.write("New line\n")

# Working with CSV
import csv
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["salary"])

# Working with JSON
import json
with open("data.json", "r") as f:
    data = json.load(f)       # Parse JSON file → Python dict

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)  # Python dict → JSON file
```

**`with` statement** ensures the file is properly closed even if an error occurs (context manager).

---

### Q16. What is exception handling in Python?

**A:**

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")           # Catches specific exception
except (TypeError, ValueError) as e:
    print(f"Type/Value error: {e}")  # Catch multiple types
except Exception as e:
    print(f"Unexpected error: {e}")  # Catch-all (use sparingly)
else:
    print("No error occurred")      # Runs only if no exception
finally:
    print("Always runs")            # Runs whether or not an exception occurred

# Raising exceptions
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age

# Custom exceptions
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"Cannot withdraw ₹{amount}. Balance: ₹{balance}")
```

---

## 🔹 Section 5 — Python for Data Engineering

### Q17. What is NumPy? Why is it important for data engineering?

**A:** **NumPy (Numerical Python)** is a library for high-performance numerical computing with multi-dimensional arrays.

```python
import numpy as np

# Create arrays
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4], [5, 6]])
zeros = np.zeros((3, 3))
ones = np.ones((2, 4))
arange = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]

# Vectorized operations (much faster than Python loops)
arr * 2          # [2, 4, 6, 8, 10]
arr + arr        # [2, 4, 6, 8, 10]
np.sqrt(arr)     # [1.0, 1.41, 1.73, 2.0, 2.24]

# Aggregations
arr.mean()       # 3.0
arr.std()        # 1.41
arr.sum()        # 15

# Slicing
matrix[0, :]     # First row: [1, 2]
matrix[:, 1]     # Second column: [2, 4, 6]

# Boolean indexing
arr[arr > 3]     # [4, 5]
```

**Why it matters:**
- **Speed** — NumPy arrays are stored in contiguous memory; operations are vectorized in C. Up to 100x faster than Python lists.
- **Foundation** — Pandas, Scikit-learn, TensorFlow all use NumPy arrays internally.
- **Memory efficient** — Fixed-type arrays use less memory than Python lists.

---

### Q18. What is Pandas? Explain DataFrame and Series.

**A:** **Pandas** is the primary data manipulation library in Python, built on NumPy.

```python
import pandas as pd

# Series: 1D labeled array
s = pd.Series([85000, 72000, 90000], index=["Rudra", "Priya", "Amit"])
s["Rudra"]  # 85000

# DataFrame: 2D labeled table (like a SQL table or Excel sheet)
df = pd.DataFrame({
    "name": ["Rudra", "Priya", "Amit"],
    "department": ["Engineering", "HR", "Engineering"],
    "salary": [85000, 72000, 90000]
})

# Reading data
df = pd.read_csv("employees.csv")
df = pd.read_json("data.json")
df = pd.read_excel("data.xlsx")
df = pd.read_sql("SELECT * FROM employees", connection)

# Inspection
df.head()           # First 5 rows
df.info()           # Data types, non-null counts
df.describe()       # Statistical summary
df.shape            # (rows, columns)
df.columns          # Column names
df.dtypes           # Data types
```

---

### Q19. How do you filter, select, and transform data in Pandas?

**A:**

```python
# Select columns
df["name"]                    # Single column → Series
df[["name", "salary"]]       # Multiple columns → DataFrame

# Filter rows
df[df["salary"] > 75000]                              # Boolean filter
df[(df["department"] == "Engineering") & (df["salary"] > 80000)]  # AND
df[df["department"].isin(["HR", "Finance"])]           # IN operator
df.query("salary > 75000 and department == 'Engineering'")  # Query string

# Sorting
df.sort_values("salary", ascending=False)
df.sort_values(["department", "salary"], ascending=[True, False])

# Adding/modifying columns
df["annual_bonus"] = df["salary"] * 0.10
df["level"] = df["salary"].apply(lambda x: "Senior" if x > 80000 else "Junior")

# Renaming columns
df.rename(columns={"name": "employee_name"}, inplace=True)

# Dropping columns/rows
df.drop(columns=["annual_bonus"])
df.drop(index=[0, 1])        # Drop rows by index
df.dropna()                   # Drop rows with any NULL
df.dropna(subset=["email"])   # Drop rows where email is NULL

# Filling NULLs
df["phone"].fillna("N/A", inplace=True)
df["salary"].fillna(df["salary"].mean(), inplace=True)
```

---

### Q20. Explain groupby, merge, and pivot_table in Pandas.

**A:**

```python
# GroupBy (like SQL GROUP BY)
df.groupby("department")["salary"].mean()
df.groupby("department").agg({
    "salary": ["mean", "max", "min", "count"],
    "name": "count"
})

# Merge (like SQL JOIN)
employees = pd.DataFrame({"emp_id": [1,2,3], "name": ["A","B","C"], "dept_id": [10,20,10]})
departments = pd.DataFrame({"dept_id": [10,20,30], "dept_name": ["Eng","HR","Fin"]})

# Inner join
pd.merge(employees, departments, on="dept_id", how="inner")

# Left join
pd.merge(employees, departments, on="dept_id", how="left")

# Concatenation (stack DataFrames)
pd.concat([df1, df2], axis=0)   # Vertical stack (rows)
pd.concat([df1, df2], axis=1)   # Horizontal stack (columns)

# Pivot Table (like Excel pivot tables)
sales = pd.DataFrame({
    "region": ["North","South","North","South"],
    "product": ["A","A","B","B"],
    "revenue": [100, 150, 200, 120]
})
pivot = sales.pivot_table(values="revenue", index="region", columns="product", aggfunc="sum")
#          A    B
# North  100  200
# South  150  120
```

---

### Q21. How do you handle missing data in Pandas?

**A:**

```python
# Detect missing values
df.isnull()              # DataFrame of True/False
df.isnull().sum()        # Count NULLs per column
df.isnull().sum().sum()  # Total NULLs in entire DataFrame

# Drop missing values
df.dropna()                             # Drop rows with ANY null
df.dropna(how="all")                    # Drop only if ALL values are null
df.dropna(subset=["email", "phone"])    # Drop if specific columns are null
df.dropna(thresh=3)                     # Keep rows with at least 3 non-null values

# Fill missing values
df["salary"].fillna(0)                  # Fill with constant
df["salary"].fillna(df["salary"].mean())  # Fill with mean
df["salary"].fillna(method="ffill")     # Forward fill (use previous row's value)
df["salary"].fillna(method="bfill")     # Backward fill

# Interpolation
df["salary"].interpolate(method="linear")  # Linear interpolation

# Replace specific values
df.replace({"N/A": None, "": None})
```

---

## 🔹 Section 6 — APIs & HTTP with Python

### Q22. How do you make HTTP requests in Python?

**A:**

```python
import requests

# GET request
response = requests.get("https://api.example.com/users")
print(response.status_code)    # 200
print(response.json())         # Parse JSON response

# GET with query parameters
response = requests.get(
    "https://api.example.com/users",
    params={"page": 1, "limit": 10}
)

# POST request with JSON body
response = requests.post(
    "https://api.example.com/users",
    json={"name": "Rudra", "email": "rudra@test.com"},
    headers={"Authorization": "Bearer TOKEN123"}
)

# Error handling
response = requests.get("https://api.example.com/users")
response.raise_for_status()  # Raises exception for 4xx/5xx responses

# Timeout
response = requests.get("https://api.example.com/users", timeout=5)  # 5 second timeout
```

---

### Q23. What is FastAPI? How do you create a simple API?

**A:**

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.get("/")
def root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def get_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

@app.post("/items/")
def create_item(item: Item):
    return {"message": f"Created {item.name}", "item": item}

# Run with: uvicorn app:app --reload
```

**FastAPI advantages:**
- Auto-generates Swagger docs at `/docs`.
- Pydantic validation for request/response.
- Type hints for auto-completion and docs.
- Async support for high-performance APIs.

---

## 🔹 Section 7 — Advanced Python Concepts

### Q24. What are list comprehensions, dict comprehensions, and set comprehensions?

**A:**

```python
# List comprehension
squares = [x**2 for x in range(10)]                    # [0, 1, 4, 9, ...]
evens = [x for x in range(20) if x % 2 == 0]          # [0, 2, 4, 6, ...]
upper = [name.upper() for name in names if len(name) > 3]

# Dict comprehension
word_lengths = {word: len(word) for word in ["hello", "world"]}  # {"hello": 5, "world": 5}
squared_dict = {x: x**2 for x in range(5)}                       # {0:0, 1:1, 2:4, 3:9, 4:16}

# Set comprehension
unique_lengths = {len(word) for word in ["hi", "hello", "hey"]}  # {2, 5, 3}

# Nested list comprehension
matrix = [[1,2,3], [4,5,6], [7,8,9]]
flat = [num for row in matrix for num in row]  # [1,2,3,4,5,6,7,8,9]
```

---

### Q25. What are modules and packages in Python?

**A:**

| Concept | What It Is | Example |
|---------|-----------|---------|
| **Module** | A single `.py` file containing functions/classes | `import math` → `math.py` |
| **Package** | A directory of modules with an `__init__.py` file | `import langchain.chat_models` |
| **Library** | A collection of packages (installed via pip) | `pip install pandas` |

```python
# Importing
import math                       # Import entire module
from math import sqrt, pi         # Import specific items
from math import sqrt as square_root  # Import with alias
import pandas as pd               # Module alias (convention)

# Creating your own module
# utils.py
def cosine_similarity(a, b):
    ...

# app.py
from utils import cosine_similarity
```

**`__init__.py`** makes a directory a package:
```
mypackage/
    __init__.py
    module_a.py
    module_b.py
```

---

### Q26. What is `pip` and virtual environments?

**A:**

```bash
# pip: Python's package manager
pip install pandas              # Install a package
pip install pandas==2.0.3       # Install specific version
pip install -r requirements.txt # Install from requirements file
pip freeze > requirements.txt   # Export installed packages
pip list                        # List installed packages
pip uninstall pandas            # Remove a package

# Virtual environment: Isolated Python environment
python -m venv myenv            # Create
myenv\Scripts\activate          # Activate (Windows)
source myenv/bin/activate       # Activate (Mac/Linux)
deactivate                      # Deactivate

# Why virtual environments?
# Project A needs pandas==1.5
# Project B needs pandas==2.0
# Without venv → conflict! With venv → each has its own pandas version
```

---

### Q27. Explain `map()`, `filter()`, and `reduce()`.

**A:**

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map(): Apply function to every element
squared = list(map(lambda x: x**2, numbers))       # [1, 4, 9, 16, 25]

# filter(): Keep elements that satisfy condition
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

# reduce(): Accumulate elements into single value
total = reduce(lambda a, b: a + b, numbers)           # 15 (1+2+3+4+5)
product = reduce(lambda a, b: a * b, numbers)          # 120 (1*2*3*4*5)
```

**Modern Python preference:**
```python
# List comprehensions are often preferred over map/filter:
squared = [x**2 for x in numbers]          # Clearer than map
evens = [x for x in numbers if x % 2 == 0]  # Clearer than filter
total = sum(numbers)                        # Clearer than reduce
```

---

### Q28. What are iterators and iterables?

**A:**

| Concept | Definition | Example |
|---------|-----------|---------|
| **Iterable** | Any object you can loop over | `list`, `str`, `dict`, `set`, `range`, file objects |
| **Iterator** | An object that produces values one at a time via `__next__()` | Result of `iter([1,2,3])`, generator objects |

```python
# Every iterable can produce an iterator
my_list = [1, 2, 3]
my_iter = iter(my_list)     # Get iterator from iterable

next(my_iter)  # 1
next(my_iter)  # 2
next(my_iter)  # 3
next(my_iter)  # StopIteration exception

# Custom iterator
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for n in Countdown(5):
    print(n)  # 5, 4, 3, 2, 1
```

---

### Q29. What is the difference between `deepcopy` and `copy`?

**A:**

```python
import copy

original = [[1, 2], [3, 4]]

# Shallow copy: New list, but inner lists are still references
shallow = copy.copy(original)
shallow[0][0] = 99
print(original)  # [[99, 2], [3, 4]] ← CHANGED! Inner list is shared

# Deep copy: Completely independent copy at all levels
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 99
print(original)  # [[1, 2], [3, 4]] ← UNCHANGED! Fully independent

# Assignment is NOT copying at all
a = [1, 2, 3]
b = a           # b points to same object
b[0] = 99
print(a)        # [99, 2, 3] ← Both changed!
```

---

### Q30. What are type hints and why are they important?

**A:**

```python
# Without type hints
def process(data, threshold):
    ...  # What type is data? threshold? What does it return?

# With type hints
def process(data: list[dict], threshold: float) -> pd.DataFrame:
    ...  # Clear: takes list of dicts, returns DataFrame

# Variable annotations
name: str = "Rudra"
scores: list[int] = [85, 90, 78]
config: dict[str, str] = {"model": "gemini"}

# Optional (can be None)
from typing import Optional
def find_user(user_id: int) -> Optional[dict]:
    ...  # May return dict or None

# Union types (Python 3.10+)
def process(data: str | list[str]) -> None:
    ...
```

**Why they matter:**
- **Pydantic** uses them for automatic validation (FastAPI requests).
- **IDEs** provide autocompletion, error detection.
- **Documentation** — self-documenting code.
- **Static analysis** — tools like `mypy` catch type errors before runtime.

---

## 🔹 Section 8 — Python & Databases

### Q31. How do you connect Python to MySQL?

**A:**

```python
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="company_db"
)

cursor = conn.cursor(dictionary=True)  # Returns rows as dicts

# Execute queries
cursor.execute("SELECT * FROM employees WHERE department = %s", ("Engineering",))
rows = cursor.fetchall()
for row in rows:
    print(row["name"], row["salary"])

# Insert data
cursor.execute(
    "INSERT INTO employees (name, department, salary) VALUES (%s, %s, %s)",
    ("Rudra", "Engineering", 85000)
)
conn.commit()  # Must commit DML changes!

# Close connection
cursor.close()
conn.close()

# Using pandas with MySQL
import pandas as pd
df = pd.read_sql("SELECT * FROM employees", conn)
```

**⚠️ Always use parameterized queries** (`%s` placeholders) — never use f-strings to prevent SQL injection.

---

### Q32. What is an ORM? What is SQLAlchemy?

**A:** An **ORM (Object-Relational Mapping)** maps Python objects to database tables, so you interact with the database using Python classes instead of raw SQL.

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# Define a model (maps to a table)
class Employee(Base):
    __tablename__ = "employees"
    emp_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    salary = Column(Float)

# Connect
engine = create_engine("mysql+pymysql://root:pass@localhost/company_db")
Session = sessionmaker(bind=engine)
session = Session()

# Query (no raw SQL!)
employees = session.query(Employee).filter(Employee.salary > 75000).all()
for emp in employees:
    print(emp.name, emp.salary)

# Insert
new_emp = Employee(name="Rudra", salary=85000)
session.add(new_emp)
session.commit()
```

**ORM vs Raw SQL:**

| Aspect | Raw SQL | ORM |
|--------|---------|-----|
| Learning curve | SQL knowledge needed | Python OOP knowledge |
| Portability | MySQL-specific syntax | Works across databases |
| Performance | Fastest (hand-optimized) | Slightly slower (abstraction overhead) |
| Readability | SQL strings in Python code | Pythonic, object-oriented |

---

## 🔹 Section 9 — Data Engineering Concepts in Python

### Q33. What is data serialization? Explain JSON, CSV, and Pickle.

**A:** **Serialization** = converting a Python object into a format that can be stored or transmitted. **Deserialization** = the reverse.

| Format | Human Readable | Cross-Language | Python Library | Use Case |
|--------|---------------|----------------|----------------|----------|
| **JSON** | ✅ Yes | ✅ Yes | `json` | APIs, config files, web data |
| **CSV** | ✅ Yes | ✅ Yes | `csv`, `pandas` | Tabular data, spreadsheets |
| **Pickle** | ❌ No (binary) | ❌ Python only | `pickle` | Saving Python objects (models, dataframes) |
| **Parquet** | ❌ No (binary) | ✅ Yes | `pyarrow`, `pandas` | Big data, columnar storage |
| **YAML** | ✅ Yes | ✅ Yes | `pyyaml` | Config files, Kubernetes manifests |

```python
import json, pickle

# JSON
data = {"name": "Rudra", "scores": [85, 90]}
json_str = json.dumps(data)          # Python → JSON string
parsed = json.loads(json_str)        # JSON string → Python

# Pickle
import pickle
with open("model.pkl", "wb") as f:
    pickle.dump(ml_model, f)         # Save Python object

with open("model.pkl", "rb") as f:
    loaded_model = pickle.load(f)    # Load Python object
```

---

### Q34. What is logging in Python? Why is it better than print()?

**A:**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log"
)

logger = logging.getLogger(__name__)

# Log levels (in order of severity)
logger.debug("Detailed debugging info")      # Lowest
logger.info("General information")
logger.warning("Something unexpected")
logger.error("Something went wrong")
logger.critical("System is crashing!")       # Highest
```

**Logging vs Print:**

| Aspect | print() | logging |
|--------|---------|---------|
| Severity levels | No | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| Output control | Only stdout | File, stdout, network, email |
| Performance | No control | Can disable by level |
| Production use | ❌ No | ✅ Yes |
| Timestamps | Manual | Automatic |

---

### Q35. What is environment variable management in Python?

**A:**

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read environment variables
api_key = os.getenv("GOOGLE_API_KEY")              # Returns None if not set
db_host = os.getenv("DB_HOST", "localhost")         # Returns default if not set
port = int(os.environ.get("PORT", "8000"))          # os.environ raises KeyError if not set

# Set environment variable (for current process only)
os.environ["NEW_VAR"] = "value"
```

**.env file:**
```
GOOGLE_API_KEY=AIza...
DB_HOST=localhost
DB_PORT=3306
DEBUG=true
```

**Why .env files:**
- Keep secrets out of source code.
- Different configs for dev/staging/production.
- `.env` is in `.gitignore` — never committed.
- `.env.example` provides template for teammates.

---

## 🔹 Section 10 — Quick Fire Questions

### Q36. What is the GIL (Global Interpreter Lock)?

**A:** The **GIL** is a mutex in CPython that allows only **one thread to execute Python bytecode at a time**, even on multi-core CPUs.

**Impact:**
- CPU-bound tasks (heavy computation) don't benefit from multithreading.
- I/O-bound tasks (network calls, file I/O) DO benefit because the GIL is released during I/O.

**Workarounds:**
- Use `multiprocessing` (separate processes, each with its own GIL).
- Use `asyncio` for I/O-bound tasks.
- Use C extensions (NumPy operations release the GIL).

---

### Q37. What is the difference between `append()`, `extend()`, and `+=` for lists?

**A:**

```python
lst = [1, 2, 3]

lst.append([4, 5])   # [1, 2, 3, [4, 5]]  ← Adds as single element
lst = [1, 2, 3]

lst.extend([4, 5])   # [1, 2, 3, 4, 5]    ← Adds each element
lst = [1, 2, 3]

lst += [4, 5]        # [1, 2, 3, 4, 5]    ← Same as extend
```

---

### Q38. What is `__name__ == "__main__"`?

**A:**

```python
# In a Python file:
if __name__ == "__main__":
    main()
```

- When a file is **run directly**: `__name__` is set to `"__main__"` → code runs.
- When a file is **imported as a module**: `__name__` is set to the module name → code doesn't run.

This allows a file to be both a standalone script AND an importable module.

---

### Q39. What is `enumerate()` and `zip()`?

**A:**

```python
# enumerate: Get index + value while looping
names = ["Rudra", "Priya", "Amit"]
for i, name in enumerate(names):
    print(f"{i}: {name}")
# 0: Rudra, 1: Priya, 2: Amit

# zip: Combine multiple iterables element-wise
names = ["Rudra", "Priya"]
salaries = [85000, 72000]
for name, salary in zip(names, salaries):
    print(f"{name}: {salary}")
# Rudra: 85000, Priya: 72000

# zip for dict creation
name_salary = dict(zip(names, salaries))  # {"Rudra": 85000, "Priya": 72000}
```

---

### Q40. What is the walrus operator (`:=`)?

**A:** The **walrus operator** (Python 3.8+) assigns a value and returns it in the same expression.

```python
# Without walrus
data = input("Enter: ")
if len(data) > 10:
    print(f"Too long: {len(data)}")

# With walrus (avoid calling len() twice)
if (n := len(input("Enter: "))) > 10:
    print(f"Too long: {n}")

# In list comprehensions
results = [y for x in data if (y := process(x)) is not None]
```

---

> **💡 Viva Tip:** Python questions in data engineering vivas focus on **Pandas operations**, **file handling**, **API integration**, and **database connectivity**. Be ready to write code for data transformation tasks on the spot.

---

*End of Unit 3 — Python for Data Engineers 🐍*
