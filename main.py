import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def create_synthetic_expenses(file_path="data/expenses.csv", rows=200):
    os.makedirs("data", exist_ok=True)
    categories = ["Food", "Rent", "Transport", "Shopping", "Utilities", "Health", "Entertainment", "Education"]
    payment_methods = ["Cash", "Credit Card", "Debit Card", "UPI/Wallet"]
    start_date = datetime(2025, 1, 1)
    data = []
    for _ in range(rows):
        date = start_date + timedelta(days=np.random.randint(0, 180))
        category = np.random.choice(categories)
        amount = round(np.random.uniform(5, 200), 2)
        payment = np.random.choice(payment_methods)
        note = f"{category} expense"
        data.append([date.strftime("%Y-%m-%d"), category, amount, payment, note])

    df = pd.DataFrame(data, columns=["date", "category", "amount", "payment_method", "note"])
    df.to_csv(file_path, index=False)
    print(f"✅ Synthetic dataset created at {file_path}")

def load_and_clean_data(file_path="data/expenses.csv"):
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(inplace=True)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

def plot_category_expense(df):
    category_data = df.groupby("category")["amount"].sum()
    category_data.plot(kind="bar", color="skyblue")
    plt.title("Category-wise Spending")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.savefig("outputs/category_spending.png")
    plt.close()

def plot_monthly_trend(df):
    monthly_data = df.groupby("month")["amount"].sum()
    monthly_data.plot(kind="line", marker="o", color="green")
    plt.title("Monthly Spending Trend")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.savefig("outputs/monthly_trend.png")
    plt.close()

def plot_payment_method(df):
    payment_data = df.groupby("payment_method")["amount"].sum()
    payment_data.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Payment Method Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("outputs/payment_method.png")
    plt.close()

def plot_daily_trend(df):
    daily = df.groupby("date")["amount"].sum()
    daily.plot(color="purple")
    plt.title("Daily Spending Trend")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.savefig("outputs/daily_trend.png")
    plt.close()

def generate_report(df):
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/summary_report.csv"
    summary = {
        "Total Spending": [df["amount"].sum()],
        "Highest Category": [df.groupby("category")["amount"].sum().idxmax()],
        "Average Daily Spending": [df.groupby("date")["amount"].sum().mean()]
    }
    pd.DataFrame(summary).to_csv(report_path, index=False)
    print(f"✅ Report generated at {report_path}")

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)

    create_synthetic_expenses()
    df = load_and_clean_data()

    plot_category_expense(df)
    plot_monthly_trend(df)
    plot_payment_method(df)
    plot_daily_trend(df)

    generate_report(df)

    print("✅ Project executed successfully.")