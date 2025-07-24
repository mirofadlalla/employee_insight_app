# 💼 Employee Insights Chat App

This is an interactive Streamlit-based web application designed to help you explore and analyze employee data with natural language queries. The app allows users to ask questions about salaries, tenure, department performance, and more, and receive insightful visualizations and summaries in response.

---

## 🚀 Features

- 📊 Visual salary analysis over time and by department/title.
- 👤 Most common job titles by age and gender.
- 📈 Salary growth trends per employee.
- 🏢 Department-level metrics like total salary, turnover, and average tenure.
- 🔁 Analysis of employee department switches.

---

## 🧠 Example Questions You Can Ask

Try typing any of the following in the chat input:

- `"top salaries"`  
- `"average salary per year"`  
- `"salary growth"`  
- `"most common age group"`  
- `"department with highest average salary"`  
- `"turnover"` or `"average tenure by department"`  
- `"tenure vs salary"`  
- `"total salary by department"`  
- `"average salary per title"`  
- `"gender salary"`  
- `"employee distribution"`  
- `"moved departments"`

---

## 📦 Dataset Files Required

Make sure these CSV files are in the same directory as your app:

- `current_employee_snapshot.csv`
- `department_employee.csv`
- `employee.csv`
- `department.csv`
- `salary.csv`
- `title.csv`
- `department_manager.csv`

---

## 🛠 How to Run

1. **Install requirements:**

```bash
pip install streamlit pandas matplotlib seaborn
