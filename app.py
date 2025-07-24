import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(page_title="Employee Insights Chat", layout="wide")
st.title("💬 Ask About Employee Data")

@st.cache_data
def load_data():
    current_emp_snapchat = pd.read_csv("current_employee_snapshot.csv")
    department_employee = pd.read_csv("department_employee.csv")
    employee = pd.read_csv("employee.csv")
    department = pd.read_csv("department.csv")
    salary = pd.read_csv("salary.csv")
    title = pd.read_csv("title.csv")
    department_manager = pd.read_csv("department_manager.csv")
    return current_emp_snapchat, department_employee, employee, department, salary, title, department_manager

# Load data
current_emp_snapchat, department_employee, employee, department, salary, title, department_manager = load_data()

# Preprocessing
department_employee['to_date'] = department_employee['to_date'].replace('9999-01-01', "2002-12-12")
salary['from_date'] = pd.to_datetime(salary['from_date'])
salary['year'] = salary['from_date'].dt.year

# Salary growth calculation
salary_sorted = salary.sort_values(by=['employee_id', 'from_date'])
salary_sorted['salary_growth'] = salary_sorted.groupby('employee_id')['amount'].diff()
salary_sorted['growth_year'] = salary_sorted['from_date'].dt.year

# Top 10 highest paid employees in each department
latest_salary = salary.sort_values("to_date").drop_duplicates("employee_id", keep="last")
current_dept = department_employee[department_employee["to_date"] == "2002-12-12"]
merged = latest_salary.merge(current_dept, on="employee_id", how="inner")
merged = merged.merge(employee, left_on="employee_id", right_on="id", how="inner")
merged = merged[["employee_id", "first_name", "last_name", "department_id", "amount"]]
merged["rank"] = merged.groupby("department_id")["amount"].rank(ascending=False)
top_10 = merged[merged["rank"] <= 10].sort_values(["department_id", "rank"])

# --- Question input ---
question = st.text_input("❓ Type your question here:")
if question:
    q = question.lower()

    if "top salaries" in q or "highest paid" in q:
        st.write("📌 Top 10 highest-paid employees in each department:")
        st.dataframe(top_10)

    elif "average salary" in q or "year" in q:
        avg_salary_per_year = salary.groupby('year')['amount'].mean().reset_index()
        fig, ax = plt.subplots()
        ax.plot(avg_salary_per_year['year'], avg_salary_per_year['amount'], marker='o')
        ax.set_title('Average Salary Over Years')
        ax.set_xlabel('Year')
        ax.set_ylabel('Average Salary')
        ax.grid(True)
        st.pyplot(fig)

    elif "salary growth" in q or "salary change" in q:
        avg_growth = salary_sorted.groupby('growth_year')['salary_growth'].mean().reset_index()
        fig, ax = plt.subplots()
        ax.plot(avg_growth['growth_year'], avg_growth['salary_growth'], marker='o', color='green')
        ax.set_title('Average Annual Salary Growth')
        ax.set_xlabel('Year')
        ax.set_ylabel('Average Growth')
        ax.grid(True)
        st.pyplot(fig)

    elif "age group" in q or "most common age" in q:
        emp_snapshot = current_emp_snapchat.merge(employee[["id", "birth_date"]], left_on="employee_id", right_on="id", how="left")
        emp_snapshot["birth_date"] = pd.to_datetime(emp_snapshot["birth_date"])
        emp_snapshot["age"] = emp_snapshot["birth_date"].apply(lambda x: 2002 - x.year)
        emp_snapshot["age_group"] = pd.cut(emp_snapshot["age"], bins=[10, 20, 30, 40, 50, 60, 70], labels=["10s", "20s", "30s", "40s", "50s", "60s"], right=False)

        st.subheader("👤 Most Common Job Titles by Age")
        top_titles = emp_snapshot.groupby("age")["title"].agg(lambda x: x.value_counts().idxmax())
        top_titles = top_titles.reset_index().rename(columns={"title": "Most Common Title"})
        st.dataframe(top_titles)

        age_counts = emp_snapshot["age_group"].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.barplot(x=age_counts.index, y=age_counts.values, palette="viridis", ax=ax)
        ax.set_title("Number of Employees in Each Age Group", fontsize=14)
        ax.set_xlabel("Age Group", fontsize=12)
        ax.set_ylabel("Number of Employees", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

    elif "top department" in q or "highest average" in q:
        highest_avg_dept = current_emp_snapchat.groupby("dept_name")["salary_amount"].mean().sort_values(ascending=False).head(1)
        st.write("🏆 Department with the highest average salary:")
        st.dataframe(highest_avg_dept)

    elif "turnover" in q or "average tenure" in q or "department tenure" in q:
        st.subheader("🏢 Average Tenure by Department (Turnover Analysis)")

        # Clean and calculate tenure
        department_employee['to_date'] = department_employee['to_date'].replace('9999-01-01', "2002-12-12")
        department_employee['from_date'] = pd.to_datetime(department_employee['from_date'])
        department_employee['to_date'] = pd.to_datetime(department_employee['to_date'])
        department_employee['tenure_days'] = (department_employee['to_date'] - department_employee['from_date']).dt.days
        department_employee['tenure_years'] = department_employee['tenure_days'] / 365

        # Average tenure per department
        avg_tenure = department_employee.groupby('department_id')['tenure_years'].mean().reset_index()
        avg_tenure.columns = ['department_id', 'avg_tenure_years']
        high_turnover = avg_tenure.sort_values('avg_tenure_years')

        st.dataframe(high_turnover)

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=high_turnover, x='department_id', y='avg_tenure_years', palette='crest', ax=ax)
        ax.set_title('Average Employee Tenure by Department')
        ax.set_xlabel('Department ID')
        ax.set_ylabel('Average Tenure (Years)')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

    elif "tenure vs salary" in q or ("tenure" in q and "salary" in q):
        st.subheader("📊 Relationship Between Tenure and Salary")

        # Ensure tenure is calculated
        department_employee['to_date'] = department_employee['to_date'].replace('9999-01-01', "2002-12-12")
        department_employee['from_date'] = pd.to_datetime(department_employee['from_date'])
        department_employee['to_date'] = pd.to_datetime(department_employee['to_date'])
        department_employee['tenure_days'] = (department_employee['to_date'] - department_employee['from_date']).dt.days
        department_employee['tenure_years'] = department_employee['tenure_days'] / 365

        # Merge with salary data
        merged_tenure = merged.merge(department_employee[['employee_id', 'tenure_years']], on='employee_id', how='left')
        merged_tenure = merged_tenure.dropna(subset=['tenure_years', 'amount'])

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(merged_tenure['tenure_years'], merged_tenure['amount'], alpha=0.5, color='teal')
        ax.set_title("Tenure vs Salary")
        ax.set_xlabel("Tenure (Years)")
        ax.set_ylabel("Salary")
        ax.grid(True)
        st.pyplot(fig)

    elif "total salary" in q or "department spending" in q or "salary distribution" in q:

        st.subheader("🏢 Total Salary Paid by Each Department")

        dept_total_salary = merged.groupby('department_id')['amount'].sum().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        dept_total_salary.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Total Salary Paid by Department')
        ax.set_ylabel('Total Salary')
        ax.set_xlabel('Department ID')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

    elif "salary overall distribution" in q or "salary histogram" in q:
        st.subheader("📊 Overall Salary Distribution")

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(merged['amount'], bins=30, edgecolor='black', color='steelblue')
        ax.set_title("Overall Salary Distribution")
        ax.set_xlabel("Salary")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

    elif "average salary per title" in q or "title salary" in q:
        st.subheader("💼 Average Salary per Title")
        avg_salary_per_title = merged.groupby("title")["amount"].mean().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        avg_salary_per_title.plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title("Average Salary per Title")
        ax.set_ylabel("Average Salary")
        ax.set_xlabel("Title")
        ax.grid(axis='y')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif "gender salary" in q or "average salary per gender" in q:
        st.subheader("👫 Average Salary by Gender")

        gender_salary = employee.merge(salary, left_on="id", right_on="employee_id")
        avg_gender_salary = gender_salary.groupby("gender")["amount"].mean()

        fig, ax = plt.subplots(figsize=(6, 4))
        avg_gender_salary.plot(kind='bar', color=['lightblue', 'pink'], ax=ax)
        ax.set_title("Average Salary per Gender")
        ax.set_ylabel("Salary")
        plt.xticks(rotation=0)
        ax.grid(axis='y')
        st.pyplot(fig)

    # elif "employee distribution" in q or "title distribution" in q:
    #     st.subheader("📊 Employee Distribution by Title")

    #     fig, ax = plt.subplots(figsize=(10, 6))
    #     merged["title"].value_counts().plot(kind='bar', color='purple', ax=ax)
    #     ax.set_title("Distribution of Employees by Title")
    #     ax.set_ylabel("Number of Employees")
    #     plt.xticks(rotation=45)
    #     st.pyplot(fig)

    elif "employee distribution" in q or "title distribution" in q:
        st.subheader("📊 Employee Distribution by Title")
    
        # تأكد إن عمود title موجود
        if "title" not in merged.columns:
            merged = merged.merge(title[["employee_id", "title"]], on="employee_id", how="left")
    
        fig, ax = plt.subplots(figsize=(10, 6))
        merged["title"].value_counts().plot(kind='bar', color='purple', ax=ax)
        ax.set_title("Distribution of Employees by Title")
        ax.set_ylabel("Number of Employees")
        plt.xticks(rotation=45)
        st.pyplot(fig)


    elif "department switch" in q or "moved departments" in q or "switching departments" in q:
        st.subheader("🔄 Department Switching Analysis")

        dept_switches = department_employee.groupby("employee_id")["department_id"].nunique()
        num_switchers = (dept_switches > 1).sum()

        st.write(f"📌 Number of employees who moved between departments: **{num_switchers}** out of **{len(dept_switches)}** total employees.")









    else:
        st.warning("⚠️ Your question was not recognized. Try a different phrasing.")

# --- Input for employee ID to show salary trend ---
st.markdown("---")
employee_id_input = st.text_input("🔍 Enter employee ID to see salary progression:")

if employee_id_input:
    try:
        emp_id = int(employee_id_input)
        emp_salary = salary_sorted[salary_sorted["employee_id"] == emp_id]

        if not emp_salary.empty:
            st.write(f"📈 Salary progression for employee ID {emp_id}:")
            st.dataframe(emp_salary[["from_date", "amount", "salary_growth"]])

            fig, ax = plt.subplots()
            ax.plot(emp_salary["from_date"], emp_salary["amount"], marker='o', label='Salary')
            ax.set_title(f'Salary Over Time for Employee {emp_id}')
            ax.set_xlabel('Date')
            ax.set_ylabel('Salary')
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.warning("❌ No data found for this employee.")
    except ValueError:
        st.warning("⚠️ Please enter a valid numeric employee ID.")

# # --- Age group and most common job title analysis ---
# st.markdown("---")
# st.subheader("👤 Most Common Job Titles by Age")

# emp_snapshot = current_emp_snapchat.merge(employee[["id", "birth_date"]], left_on="employee_id", right_on="id", how="left")
# emp_snapshot["birth_date"] = pd.to_datetime(emp_snapshot["birth_date"])
# emp_snapshot["age"] = emp_snapshot["birth_date"].apply(lambda x: 2002 - x.year)
# emp_snapshot["age_group"] = pd.cut(emp_snapshot["age"], bins=[10, 20, 30, 40, 50, 60, 70], labels=["10s", "20s", "30s", "40s", "50s", "60s"], right=False)

# top_titles = emp_snapshot.groupby("age")["title"].agg(lambda x: x.value_counts().idxmax())
# top_titles = top_titles.reset_index().rename(columns={"title": "Most Common Title"})
# st.dataframe(top_titles)

# age_counts = emp_snapshot["age_group"].value_counts().sort_index()
# fig, ax = plt.subplots(figsize=(8, 5))
# sns.barplot(x=age_counts.index, y=age_counts.values, palette="viridis", ax=ax)
# ax.set_title("Number of Employees in Each Age Group", fontsize=14)
# ax.set_xlabel("Age Group", fontsize=12)
# ax.set_ylabel("Number of Employees", fontsize=12)
# ax.grid(axis='y', linestyle='--', alpha=0.5)
# st.pyplot(fig)
