import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

FILE_NAME = "expenses.csv"
BUDGET_FILE = "budget.txt"
categories = ["Food", "Travel", "Shopping", "Other"]

# Initialize CSV file
if not os.path.exists(FILE_NAME):
    df_init = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
    df_init.to_csv(FILE_NAME, index=False)

# Load budget
def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            try:
                return float(f.read().strip())
            except:
                return 0.0
    return 0.0

def save_budget(budget):
    with open(BUDGET_FILE, "w") as f:
        f.write(str(budget))

st.title("💰 Expense Tracker & Analytics Dashboard")

# --- SIDEBAR: ADD EXPENSE & BUDGET ---
st.sidebar.header("Add New Expense")
desc = st.sidebar.text_input("Description")
amt = st.sidebar.text_input("Amount (₹)")
cat = st.sidebar.selectbox("Category", categories)

if st.sidebar.button("Add Expense"):
    if not desc or not amt:
        st.sidebar.error("Please fill in all fields.")
    else:
        try:
            amt_f = float(amt)
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_data = pd.DataFrame([[date, desc, amt_f, cat]], columns=["Date", "Description", "Amount", "Category"])
            new_data.to_csv(FILE_NAME, mode='a', header=not os.path.exists(FILE_NAME), index=False)
            st.sidebar.success("Expense added successfully!")
        except ValueError:
            st.sidebar.error("Amount must be a valid number.")

st.sidebar.divider()
st.sidebar.header("Monthly Budget")
current_budget = load_budget()
new_budget = st.sidebar.number_input("Set Budget (₹)", value=float(current_budget))
if st.sidebar.button("Save Budget"):
    save_budget(new_budget)
    st.sidebar.success("Budget updated!")

# --- MAIN DASHBOARD ---
df = pd.read_csv(FILE_NAME)

if not df.empty:
    # Budget tracking logic
    total_spent = df["Amount"].sum()
    remaining = new_budget - total_spent

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"₹{total_spent:.2f}")
    col2.metric("Monthly Budget", f"₹{new_budget:.2f}")
    col3.metric("Remaining", f"₹{remaining:.2f}", delta=f"₹{remaining:.2f}" if new_budget > 0 else None)

    st.subheader("Expense Records")
    st.dataframe(df, use_container_width=True)

    # Charts Section
    st.subheader("Analytics")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("### Spending by Category")
        cat_totals = df.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots()
        ax.pie(cat_totals, labels=cat_totals.index, autopct='%1.1f%%', startangle=90)
        st.pyplot(fig)

    with c2:
        st.write("### Daily Spending Trend")
        df["Date_Only"] = pd.to_datetime(df["Date"]).dt.date
        daily_totals = df.groupby("Date_Only")["Amount"].sum()
        fig2, ax2 = plt.subplots()
        ax2.plot(daily_totals.index.astype(str), daily_totals.values, marker="o", linestyle="-")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    # Delete row utility
    st.subheader("Manage Records")
    row_to_delete = st.selectbox("Select row index to delete", options=df.index)
    if st.button("Delete Selected Row"):
        df = df.drop(row_to_delete)
        df.drop(columns=["Date_Only"], errors="ignore", inplace=True)
        df.to_csv(FILE_NAME, index=False)
        st.success("Row deleted! Refresh page to update.")
else:
    st.info("No expenses recorded yet. Use the sidebar to add your first expense.")