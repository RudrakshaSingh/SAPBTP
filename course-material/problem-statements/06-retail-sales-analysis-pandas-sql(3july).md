# Problem Statement 6 — Retail Sales Analysis using Pandas and SQL

| | |
|---|---|
| **Title** | Customer Purchase and Sales Performance Analysis |
| **Source label** | Labelled "Problem Statement – 5a" in the original PDF |
| **Domain** | Retail / E-commerce |
| **Topic** | SQL joins & aggregation + Pandas merge & groupby |
| **Deliverable** | SQL scripts + Pandas notebook + business insights |

---

## Objective

You are working as a data analyst for a retail company. The company sells products across different cities through **online and offline** channels. Your task is to analyze sales, customer behavior, product performance, and revenue trends using **both SQL and Pandas**.

You need to create tables, load sample data, write SQL queries, and then perform the same analysis using Pandas.

## Business Scenario

A retail company wants to understand:

- Which products are selling the most
- Which city is generating the highest revenue
- Which customers are buying frequently
- Which sales channel is performing better
- Monthly revenue trend
- Products with low sales performance
- High-value customers

Three datasets are shared: **Customers**, **Products**, **Orders**.

---

## Datasets

### Table 1: `customers`

| Column Name | Description |
|---|---|
| `customer_id` | Unique customer ID |
| `customer_name` | Name of the customer |
| `city` | Customer city |
| `age` | Customer age |
| `gender` | Male / Female |

**Sample Data**

| customer_id | customer_name | city | age | gender |
|---|---|---|---|---|
| C001 | Rahul Sharma | Patna | 32 | Male |
| C002 | Priya Singh | Delhi | 28 | Female |
| C003 | Amit Kumar | Kolkata | 35 | Male |
| C004 | Sneha Verma | Pune | 30 | Female |
| C005 | Rohit Raj | Patna | 40 | Male |
| C006 | Neha Gupta | Delhi | 26 | Female |
| C007 | Ankit Sinha | Mumbai | 38 | Male |
| C008 | Riya Das | Kolkata | 24 | Female |

---

### Table 2: `products`

| Column Name | Description |
|---|---|
| `product_id` | Unique product ID |
| `product_name` | Product name |
| `category` | Product category |
| `price` | Product price |

**Sample Data**

| product_id | product_name | category | price |
|---|---|---|---|
| P001 | Laptop | Electronics | 55000 |
| P002 | Mobile Phone | Electronics | 25000 |
| P003 | Office Chair | Furniture | 7000 |
| P004 | Headphones | Electronics | 3000 |
| P005 | Study Table | Furniture | 12000 |
| P006 | Shoes | Fashion | 4000 |
| P007 | Backpack | Fashion | 2500 |

---

### Table 3: `orders`

| Column Name | Description |
|---|---|
| `order_id` | Unique order ID |
| `customer_id` | Customer who placed the order |
| `product_id` | Product purchased |
| `order_date` | Date of order |
| `quantity` | Number of units purchased |
| `sales_channel` | Online or Offline |

**Sample Data**

| order_id | customer_id | product_id | order_date | quantity | sales_channel |
|---|---|---|---|---|---|
| O001 | C001 | P002 | 2026-01-10 | 2 | Online |
| O002 | C002 | P001 | 2026-01-15 | 1 | Offline |
| O003 | C003 | P004 | 2026-02-05 | 3 | Online |
| O004 | C004 | P003 | 2026-02-12 | 2 | Offline |
| O005 | C005 | P006 | 2026-03-01 | 4 | Online |
| O006 | C001 | P004 | 2026-03-08 | 2 | Online |
| O007 | C006 | P005 | 2026-03-18 | 1 | Offline |
| O008 | C007 | P001 | 2026-04-02 | 1 | Online |
| O009 | C008 | P007 | 2026-04-10 | 5 | Online |
| O010 | C003 | P002 | 2026-04-22 | 1 | Offline |
| O011 | C005 | P003 | 2026-05-05 | 1 | Offline |
| O012 | C002 | P004 | 2026-05-15 | 4 | Online |

---

## Part A: SQL Hands-on Tasks

### Task 1: Create Tables

Create three tables — `customers`, `products`, `orders` — with proper columns and suitable data types.

### Task 2: Insert Data

Insert the given sample data into all three tables.

### Task 3: View All Orders with Customer and Product Details

Display: `order_id`, `customer_name`, `city`, `product_name`, `category`, `quantity`, `price`, `total_amount`, `sales_channel`, `order_date`.

**Formula:** `total_amount = quantity × price`

### Task 4: Find Total Revenue

Output column: `total_revenue`

### Task 5: Revenue by City

Output columns: `city`, `total_revenue`

### Task 6: Best-Selling Product

Find the product with the highest quantity sold.
Output columns: `product_name`, `total_quantity_sold`

### Task 7: Category-wise Revenue

Output columns: `category`, `total_revenue`

### Task 8: Online vs Offline Sales

Output columns: `sales_channel`, `total_revenue`

### Task 9: Monthly Revenue Trend

Find monthly revenue from January to May 2026.
Output columns: `month`, `total_revenue`

### Task 10: High-Value Customers

Find customers whose total purchase value is more than ₹50,000.
Output columns: `customer_name`, `city`, `total_purchase_value`

---

## Part B: Pandas Hands-on Tasks

Perform the same analysis using Pandas.

| Task | Description |
|---|---|
| **Task 1: Create DataFrames** | Create `customers_df`, `products_df`, `orders_df` |
| **Task 2: Merge DataFrames** | Merge all three into one final sales DataFrame containing customer, product, and order details |
| **Task 3: Create Total Amount Column** | Add `total_amount = quantity × price` |
| **Task 4: Calculate Total Revenue** | Find the total revenue |
| **Task 5: Revenue by City** | Group by city and calculate total revenue |
| **Task 6: Product-wise Quantity Sold** | Total quantity sold for each product |
| **Task 7: Category-wise Revenue** | Revenue generated by each category |
| **Task 8: Sales Channel Analysis** | Compare online and offline revenue |
| **Task 9: Monthly Revenue Trend** | Convert `order_date` to datetime, extract month, calculate monthly revenue |
| **Task 10: High-Value Customers** | Customers with total purchase value more than ₹50,000 |

---

## Final Deliverables

1. SQL table creation queries
2. SQL insert queries
3. SQL analysis queries
4. Pandas DataFrame creation steps
5. Pandas analysis output
6. Short business insights based on the analysis

## Expected Business Insights

After completing this hands-on, you should be able to answer:

- Which city gives the highest revenue?
- Which product sells the most?
- Which category performs best?
- Is online sales better than offline sales?
- Who are the high-value customers?
- Which month generated the highest revenue?

## Skills Practiced

- SQL table creation, joins, aggregation, grouping, filtering
- Pandas DataFrame creation, `merge`, `groupby`
- Date handling in Pandas
- Business data analysis using Python and SQL
