import pandas as pd


file_path = "C:/Users/HP/Downloads/transactions.csv"

df = pd.read_csv(file_path)


print(df.columns.tolist())
df["Date"] = pd.to_datetime(df["Date"])
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")


df = df.dropna(subset=["Date", "Amount", "Category"])


df["Month"] = df["Date"].dt.to_period("M")



def get_monthly_spending():

    result = (
        df.groupby("Month")["Amount"]
        .sum()
        .reset_index()
    )

    result["Month"] = result["Month"].astype(str)

    return result



def get_category_spending():

    result = (
        df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    total_spending = df["Amount"].sum()

    result["Percentage"] = (
        result["Amount"] / total_spending * 100
    ).round(2)

    return result



def get_category_trend():

    result = pd.pivot_table(
        df,
        values="Amount",
        index="Category",
        columns="Month",
        aggfunc="sum",
        fill_value=0
    )

    return result


def get_category_changes():

    monthly = (
        df.groupby(["Category", "Month"])["Amount"]
        .sum()
        .reset_index()
    )

    months = sorted(monthly["Month"].unique())

    if len(months) < 2:
        return pd.DataFrame()

    previous_month = months[-2]
    current_month = months[-1]

    previous = monthly[
        monthly["Month"] == previous_month
    ].set_index("Category")["Amount"]

    current = monthly[
        monthly["Month"] == current_month
    ].set_index("Category")["Amount"]

    result = pd.DataFrame({
        "Previous": previous,
        "Current": current
    }).fillna(0)

    result["Change"] = (
        result["Current"] - result["Previous"]
    )

    result["Change_Percentage"] = 0.0

    for category in result.index:

        previous_value = result.loc[category, "Previous"]

        if previous_value != 0:
            result.loc[category, "Change_Percentage"] = (
                result.loc[category, "Change"]
                / previous_value
                * 100
            )

    return result.sort_values(
        "Change_Percentage",
        ascending=False
    )


def find_recurring_charges():

    merchant_counts = (
        df.groupby("Merchant")
        .agg(
            Transactions=("Amount", "count"),
            Average_Amount=("Amount", "mean")
        )
        .reset_index()
    )

    # Simple prototype rule:
    # Merchant appearing at least 2 times
    recurring = merchant_counts[
        merchant_counts["Transactions"] >= 2
    ].copy()

    recurring["Average_Amount"] = (
        recurring["Average_Amount"].round(2)
    )

    return recurring.sort_values(
        "Transactions",
        ascending=False
    )



def generate_financial_summary():

    total = df["Amount"].sum()

    monthly = get_monthly_spending()
    categories = get_category_spending()
    changes = get_category_changes()
    recurring = find_recurring_charges()

    summary = {
        "total_spending": round(total, 2),
        "monthly_spending": monthly.to_dict("records"),
        "category_spending": categories.to_dict("records"),
        "category_changes": changes.reset_index().to_dict("records"),
        "recurring_charges": recurring.to_dict("records")
    }

    return summary


summary = generate_financial_summary()

print("\nTOTAL SPENDING")
print(summary["total_spending"])

print("\nMONTHLY SPENDING")
for item in summary["monthly_spending"]:
    print(item)

print("\nCATEGORY SPENDING")
for item in summary["category_spending"]:
    print(item)

print("\nCATEGORY CHANGES")
for item in summary["category_changes"]:
    print(item)

print("\nRECURRING CHARGES")
for item in summary["recurring_charges"]:
    print(item)
