import os
import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Expense Tracker", layout="wide")

def apply_accessible_theme(base_font_px: int = 22, high_contrast: bool = True):
    if high_contrast:
        bg = "#0B0F14"
        card = "#111827"
        text = "#F9FAFB"
        muted = "#D1D5DB"
        accent = "#22C55E"
        accent2 = "#60A5FA"
        border = "#374151"
        code_bg = "#0F172A"
    else:
        bg = "white"
        card = "white"
        text = "#111827"
        muted = "#374151"
        accent = "#16A34A"
        accent2 = "#2563EB"
        border = "#E5E7EB"
        code_bg = "#F3F4F6"

    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-size: {base_font_px}px !important;
        }}

        .stApp {{
            background: {bg};
            color: {text};
        }}

        h1 {{
            font-size: {base_font_px + 18}px !important;
            line-height: 1.15 !important;
            color: {text} !important;
        }}
        h2 {{
            font-size: {base_font_px + 10}px !important;
            color: {text} !important;
        }}
        h3 {{
            font-size: {base_font_px + 6}px !important;
            color: {text} !important;
        }}

        p, li, label, div {{
            color: {text};
        }}

        section[data-testid="stSidebar"] {{
            background: {card} !important;
            border-right: 2px solid {border} !important;
        }}
        section[data-testid="stSidebar"] * {{
            font-size: {base_font_px}px !important;
            color: {text} !important;
        }}

        div[data-baseweb="input"] input,
        div[data-baseweb="select"] div,
        div[data-baseweb="textarea"] textarea {{
            background-color: {bg} !important;
            color: {text} !important;
            border: 2px solid {border} !important;
            border-radius: 10px !important;
        }}

        div.stButton > button {{
            font-size: {base_font_px}px !important;
            padding: 0.65rem 1rem !important;
            border-radius: 12px !important;
            border: 2px solid {border} !important;
            background: {accent2} !important;
            color: white !important;
            font-weight: 800 !important;
        }}

        [data-testid="stMetricValue"] {{
            font-size: {base_font_px + 14}px !important;
            color: {accent} !important;
            font-weight: 900 !important;
        }}
        [data-testid="stMetricLabel"] {{
            font-size: {base_font_px}px !important;
            color: {muted} !important;
            font-weight: 800 !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 2px solid {border} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }}

        hr {{
            border: none !important;
            border-top: 2px solid {border} !important;
        }}

        a {{
            color: {accent2} !important;
            font-weight: 800 !important;
        }}

        code, pre {{
            background: {code_bg} !important;
            color: {text} !important;
            border: 2px solid {border} !important;
            border-radius: 12px !important;
            font-size: {max(base_font_px - 2, 14)}px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
h1, h2, h3 { color: #00d4ff; }
div[data-testid="stMetricValue"] { color: #00ff99; }
div[data-testid="stMetricLabel"] { color: #cccccc; }
section[data-testid="stSidebar"] { background-color: #1c1f26; }
</style>
""", unsafe_allow_html=True)

st.title("💰 Personal Expense Tracker Dashboard")

DATA_PATH = "data/expenses.csv"

if not os.path.exists(DATA_PATH):
    st.error("❌ expenses.csv not found. Please run main.py first.")
else:
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(inplace=True)
    df["month"] = df["date"].dt.to_period("M").astype(str)

    st.sidebar.header("Filters")
    selected_category = st.sidebar.multiselect("Select Category", df["category"].unique(), default=df["category"].unique())
    selected_payment = st.sidebar.multiselect("Select Payment Method", df["payment_method"].unique(), default=df["payment_method"].unique())

    filtered_df = df[
        (df["category"].isin(selected_category)) &
        (df["payment_method"].isin(selected_payment))
    ]

    # Download filtered CSV
    st.sidebar.download_button(
        label="⬇️ Download Filtered Data (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_expenses.csv",
        mime="text/csv"
    )

    # Summary tables
    summary_category = filtered_df.groupby("category")["amount"].sum().reset_index()
    summary_month = filtered_df.groupby("month")["amount"].sum().reset_index()
    summary_payment = filtered_df.groupby("payment_method")["amount"].sum().reset_index()

    # Excel with charts
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        summary_category.to_excel(writer, sheet_name="Category", index=False)
        summary_month.to_excel(writer, sheet_name="Month", index=False)
        summary_payment.to_excel(writer, sheet_name="Payment", index=False)

        workbook = writer.book

        cat_sheet = writer.sheets["Category"]
        chart1 = workbook.add_chart({"type": "column"})
        chart1.add_series({
            "name": "Category Spend",
            "categories": ["Category", 1, 0, len(summary_category), 0],
            "values": ["Category", 1, 1, len(summary_category), 1],
        })
        chart1.set_title({"name": "Category-wise Spending"})
        cat_sheet.insert_chart("D2", chart1)

        month_sheet = writer.sheets["Month"]
        chart2 = workbook.add_chart({"type": "line"})
        chart2.add_series({
            "name": "Monthly Spend",
            "categories": ["Month", 1, 0, len(summary_month), 0],
            "values": ["Month", 1, 1, len(summary_month), 1],
        })
        chart2.set_title({"name": "Monthly Spending Trend"})
        month_sheet.insert_chart("D2", chart2)

        pay_sheet = writer.sheets["Payment"]
        chart3 = workbook.add_chart({"type": "pie"})
        chart3.add_series({
            "name": "Payment Method Share",
            "categories": ["Payment", 1, 0, len(summary_payment), 0],
            "values": ["Payment", 1, 1, len(summary_payment), 1],
        })
        chart3.set_title({"name": "Payment Method Distribution"})
        pay_sheet.insert_chart("D2", chart3)

    st.sidebar.download_button(
        label="⬇️ Download Summary (Excel + Charts)",
        data=buffer.getvalue(),
        file_name="summary_report_with_charts.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Metrics
    st.subheader("📊 Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spend", f"{filtered_df['amount'].sum():.2f}")
    col2.metric("Average Daily Spend", f"{filtered_df.groupby('date')['amount'].sum().mean():.2f}")
    col3.metric("Highest Category", filtered_df.groupby("category")["amount"].sum().idxmax())

    # Charts
    st.subheader("📌 Category-wise Spending")
    cat_data = filtered_df.groupby("category")["amount"].sum()
    fig1, ax1 = plt.subplots(figsize=(6,3))
    cat_data.plot(kind="bar", ax=ax1, color="#00d4ff")
    ax1.set_ylabel("Amount")
    st.pyplot(fig1, use_container_width=False)

    st.subheader("📈 Monthly Spending Trend")
    month_data = filtered_df.groupby("month")["amount"].sum()
    fig2, ax2 = plt.subplots(figsize=(6,3))
    month_data.plot(kind="line", marker="o", ax=ax2, color="#00ff99")
    ax2.set_ylabel("Amount")
    st.pyplot(fig2, use_container_width=False)

    st.subheader("💳 Payment Method Distribution")
    pay_data = filtered_df.groupby("payment_method")["amount"].sum()
    fig3, ax3 = plt.subplots(figsize=(6,3))
    pay_data.plot(kind="pie", autopct="%1.1f%%", ax=ax3)
    ax3.set_ylabel("")
    st.pyplot(fig3, use_container_width=False)

    st.subheader("📆 Daily Spending Trend")
    daily_data = filtered_df.groupby("date")["amount"].sum()
    fig4, ax4 = plt.subplots(figsize=(6,3))
    daily_data.plot(ax=ax4, color="#ff6f61")
    ax4.set_ylabel("Amount")
    st.pyplot(fig4, use_container_width=False)