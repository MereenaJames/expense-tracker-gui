# expense_gui_upgraded.py
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv, os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
from openpyxl import Workbook

FILE_NAME = "expenses.csv"
BUDGET_FILE = "budget.txt"

categories = ["Food", "Travel", "Shopping", "Other"]

def load_budget():
    global monthly_budget
    if os.path.exists(BUDGET_FILE):
        try:
            with open(BUDGET_FILE, "r") as f:
                monthly_budget = float(f.read().strip())
        except:
            monthly_budget = None
    else:
        monthly_budget = None


def save_budget():
    global monthly_budget
    with open(BUDGET_FILE, "w") as f:
        f.write(str(monthly_budget))

def initialize_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Description", "Amount", "Category"])

def save_expense():
    desc = desc_entry.get().strip()
    amt = amount_entry.get().strip()
    cat = category_entry.get().strip()
    if not desc or not amt or not cat:
        messagebox.showerror("Error", "All fields required")
        return
    try:
        amt_f = float(amt)
    except:
        messagebox.showerror("Error", "Amount must be a number")
        return
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(FILE_NAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, desc, amt_f, cat])
    desc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    load_expenses()
    update_budget_remaining()
    messagebox.showinfo("Saved", "Expense added")

def load_expenses():
    # Clear the tree
    for r in tree.get_children():
        tree.delete(r)

    if not os.path.exists(FILE_NAME):
        return

    # Read all expenses first
    expenses = []
    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            if row:
                expenses.append(row)

    # 🔥 Sort category-wise (Food together, Travel together, etc.)
    expenses.sort(key=lambda x: x[3])  # Assuming x[3] = category column

    # Insert sorted rows into tree
    for row in expenses:
        amount = float(row[2])

        if amount >= 5000:
            tree.insert("", tk.END, values=row, tags=("high_amount",))
        else:
            tree.insert("", tk.END, values=row)


def export_to_excel():
    if not os.path.exists(FILE_NAME):
        messagebox.showinfo("No data", "No expenses to export.")
        return
    wb = Workbook()
    ws = wb.active
    ws.append(["Date", "Description", "Amount", "Category"])
    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            # try convert amount to float for Excel number
            try:
                row2 = [row[0], row[1], float(row[2]), row[3]]
            except:
                row2 = row
            ws.append(row2)
    # Ask user where to save
    path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                        filetypes=[("Excel files","*.xlsx")],
                                        title="Save as")
    if path:
        wb.save(path)
        messagebox.showinfo("Exported", f"Exported to {path}")

def show_category_pie():
    if not os.path.exists(FILE_NAME):
        messagebox.showinfo("No data", "Add expenses first.")
        return
    cats = {}
    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            cat = row[3]
            amt = float(row[2])
            cats[cat] = cats.get(cat, 0) + amt
    if not cats:
        messagebox.showinfo("No data", "Add expenses first.")
        return
    plt.figure(figsize=(6,6))
    plt.pie(cats.values(), labels=cats.keys(), autopct="%1.1f%%")
    plt.title("Expenses by Category")
    plt.show()

def show_daily_trend():
    if not os.path.exists(FILE_NAME):
        messagebox.showinfo("No data", "Add expenses first.")
        return
    daily = defaultdict(float)
    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            date_str = row[0].split()[0]  # YYYY-MM-DD
            daily[date_str] += float(row[2])
    if not daily:
        messagebox.showinfo("No data", "Add expenses first.")
        return
    dates = sorted(daily.keys())
    amounts = [daily[d] for d in dates]
    plt.figure(figsize=(8,4))
    plt.plot(dates, amounts, marker="o")
    plt.xticks(rotation=45)
    plt.title("Daily Expense Trend")
    plt.tight_layout()
    plt.show()

def set_budget():
    global monthly_budget
    try:
        monthly_budget = float(budget_entry.get())
    except:
        messagebox.showerror("Error", "Enter numeric budget")
        return
    save_budget()
    update_budget_remaining()
    messagebox.showinfo("Budget set", f"Monthly budget set to ₹{monthly_budget}")

def update_budget_remaining():
    if monthly_budget is None:
        remaining_var.set("No budget set")
        return
    # compute total spent in current month
    total = 0.0
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                # row[0] format: YYYY-MM-DD HH:MM
                date_part = row[0].split()[0]
                if date_part.startswith(datetime.now().strftime("%Y-%m")):
                    total += float(row[2])
    rem = monthly_budget - total
    remaining_var.set(f"Remaining this month: ₹{rem:.2f}")

def delete_selected():
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Select", "Select a row to delete")
        return
    # remove first selected
    values = tree.item(sel[0])['values']
    date, desc, amt, cat = values
    # remove matching row from CSV (best-effort remove first matching row)
    rows = []
    removed = False
    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
    newrows = []
    for r in rows:
        if not removed and r[0]==date and r[1]==desc and str(r[2])==str(amt) and r[3]==cat:
            removed = True
            continue
        newrows.append(r)
    with open(FILE_NAME, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(newrows)
    load_expenses()
    update_budget_remaining()
def show_category_totals():
    if not os.path.exists(FILE_NAME):
        messagebox.showinfo("No data", "Add expenses first.")
        return
    
    totals = defaultdict(float)

    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            cat = row[3]
            amt = float(row[2])
            totals[cat] += amt

    if not totals:
        messagebox.showinfo("No data", "Add expenses first.")
        return

    # Build message
    msg = "Total Spent by Category:\n\n"
    for cat, amount in totals.items():
        msg += f"{cat}: ₹{amount:.2f}\n"

    messagebox.showinfo("Category Totals", msg)
def show_monthly_dashboard():
    if not os.path.exists(FILE_NAME):
        messagebox.showerror("Error", "No expenses found!")
        return

    # Read and group data
    month_category = defaultdict(lambda: defaultdict(float))
    month_daily = defaultdict(lambda: defaultdict(float))

    with open(FILE_NAME, "r") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 4:
                continue  # skip invalid rows
            date, desc, amount, category = row
            try:
                amount = float(amount)
                dt = datetime.strptime(date.split()[0], "%Y-%m-%d")
                month = dt.strftime("%B")
                day = dt.day
            except:
                continue  # skip invalid dates/amounts

            month_category[month][category] += amount
            month_daily[month][day] += amount

    if not month_category:
        messagebox.showinfo("Info", "No valid expenses found!")
        return

    # ---------------------------
    #   Dashboard Window
    # ---------------------------
    win = tk.Toplevel()
    win.title("Monthly Analytics Dashboard")
    win.geometry("500x300")

    tk.Label(win, text="Select Month:", font=("Arial", 11)).pack(pady=8)

    months = list(month_category.keys())
    month_var = tk.StringVar()
    month_dropdown = ttk.Combobox(win, textvariable=month_var, values=months, state="readonly")
    month_dropdown.pack()

    def show_dashboard():
        selected = month_var.get()
        if not selected:
            messagebox.showwarning("Warning", "Please select a month")
            return

        categories = month_category[selected]
        daily = month_daily[selected]

        if not categories:
            messagebox.showinfo("Info", "No data for selected month")
            return

        total_spent = sum(categories.values())
        highest_category = max(categories, key=categories.get)
        transactions_count = sum([1 for _ in open(FILE_NAME)]) - 1  # minus header

        # ---------------------------
        #   Dashboard Summary Info
        # ---------------------------
        summary = (
            f"Month: {selected}\n\n"
            f"Total Spent: ₹{total_spent:.2f}\n"
            f"Highest Spending Category: {highest_category}\n"
            f"Transactions: {transactions_count}\n"
        )
        messagebox.showinfo("Monthly Summary", summary)

        # ---------------------------
        #   PIE CHART
        # ---------------------------
        plt.figure(figsize=(5, 5))
        plt.pie(categories.values(), labels=categories.keys(), autopct="%1.1f%%")
        plt.title(f"Category Distribution - {selected}")
        plt.show()

        # ---------------------------
        #   LINE CHART (Daily Trend)
        # ---------------------------
        days = sorted(daily.keys())
        values = [daily[d] for d in days]

        plt.figure(figsize=(8, 4))
        plt.plot(days, values, marker="o")
        plt.title(f"Daily Spending Trend - {selected}")
        plt.xlabel("Day")
        plt.ylabel("Amount (₹)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    tk.Button(win, text="Show Dashboard", command=show_dashboard, width=20).pack(pady=20)

# GUI building
root = tk.Tk()
root.title("Expense Tracker - Upgraded")
root.geometry("800x600")

initialize_file()
load_budget()

# Input frame
frm = tk.Frame(root)
frm.pack(pady=10)

tk.Label(frm, text="Description").grid(row=0, column=0, padx=5)
desc_entry = tk.Entry(frm, width=30); desc_entry.grid(row=0, column=1, padx=5)
tk.Label(frm, text="Amount (₹)").grid(row=0, column=2, padx=5)
amount_entry = tk.Entry(frm, width=12); amount_entry.grid(row=0, column=3, padx=5)
tk.Label(frm, text="Category").grid(row=0, column=4, padx=5)

category_options = ["Food", "Travel", "Shopping", "Other"]
category_entry = ttk.Combobox(frm, values=category_options, width=15, state="readonly")
category_entry.grid(row=0, column=5, padx=5)
category_entry.set("Food")  # default selected

tk.Button(frm, text="Add Expense", command=save_expense, bg="#a3e4a3").grid(row=0, column=6, padx=8)

# Budget frame
budget_frame = tk.Frame(root)
budget_frame.pack(pady=5)
tk.Label(budget_frame, text="Monthly Budget (₹)").grid(row=0, column=0)
budget_entry = tk.Entry(budget_frame, width=12); budget_entry.grid(row=0, column=1, padx=5)
tk.Button(budget_frame, text="Set Budget", command=set_budget).grid(row=0, column=2, padx=5)
remaining_var = tk.StringVar()
remaining_var.set("No budget set")
tk.Label(budget_frame, textvariable=remaining_var, fg="blue").grid(row=0, column=3, padx=10)

# Buttons for charts/export
action_frame = tk.Frame(root)
action_frame.pack(pady=5)
tk.Button(action_frame, text="Category Pie Chart", command=show_category_pie, bg="#d0e6ff").grid(row=0, column=0, padx=6)
tk.Button(action_frame, text="Daily Trend Chart", command=show_daily_trend, bg="#d0e6ff").grid(row=0, column=1, padx=6)
tk.Button(action_frame, text="Export to Excel", command=export_to_excel, bg="#ffe0a3").grid(row=0, column=2, padx=6)
tk.Button(action_frame, text="Delete Selected Row", command=delete_selected, bg="#ffb3b3").grid(row=0, column=3, padx=6)
tk.Button(action_frame, text="Category Totals", command=show_category_totals, bg="#c9ffc9").grid(row=0, column=4, padx=6)
tk.Button(action_frame, text="Monthly Analytics Dashboard", command=show_monthly_dashboard, bg="#d0ffd0").grid(row=0, column=5, padx=6)

# Treeview for listing expenses
columns = ("Date","Description","Amount","Category")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
tree.tag_configure("high_amount", foreground="red")
tree.tag_configure("food_tag", foreground="green")
tree.tag_configure("travel_tag", foreground="blue")
tree.tag_configure("shopping_tag", foreground="purple")
tree.tag_configure("other_tag", foreground="brown")
for c in columns:
    tree.heading(c, text=c)
    tree.column(c, anchor=tk.W, width=180 if c=="Description" else 100)
tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

load_expenses()
update_budget_remaining()

root.mainloop()
