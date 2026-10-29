from pathlib import Path
import io

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Energy Consumption Analyzer",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Energy Consumption Analyzer")
st.caption(
    "Analyze appliance-level electricity use, estimate costs, and export your results."
)

REQUIRED_COLUMNS = {"appliance", "power_watts", "hours_per_day"}
OPTIONAL_COLUMNS = {"quantity"}
SAMPLE_PATH = Path(__file__).parent / "data" / "appliances.csv"


def load_sample_data() -> pd.DataFrame:
    """Load the example appliance dataset bundled with this project."""
    return pd.read_csv(SAMPLE_PATH)


def validate_data(data: pd.DataFrame) -> tuple[pd.DataFrame | None, list[str]]:
    """Check the uploaded table and return a cleaned copy or validation errors."""
    errors = []
    data = data.copy()
    data.columns = [str(column).strip().lower() for column in data.columns]

    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        errors.append(
            "Missing required column(s): "
            + ", ".join(sorted(missing))
            + ". Required columns are appliance, power_watts, and hours_per_day."
        )
        return None, errors

    if "quantity" not in data.columns:
        data["quantity"] = 1

    data["appliance"] = data["appliance"].astype("string").str.strip()
    if data["appliance"].isna().any() or (data["appliance"] == "").any():
        errors.append("Every row needs an appliance name.")

    for column in ["power_watts", "hours_per_day", "quantity"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        if data[column].isna().any():
            errors.append(f"Column '{column}' must contain numbers.")
        elif (data[column] < 0).any():
            errors.append(f"Column '{column}' cannot contain negative values.")

    if not errors and (data["hours_per_day"] > 24).any():
        errors.append("hours_per_day cannot be greater than 24.")

    if not errors and (data["quantity"] < 1).any():
        errors.append("quantity must be at least 1.")

    if errors:
        return None, errors

    return data, errors


def calculate_energy(data: pd.DataFrame, rate: float) -> pd.DataFrame:
    """Calculate daily and 30-day energy use and estimated cost."""
    result = data.copy()
    result["total_power_watts"] = result["power_watts"] * result["quantity"]
    result["daily_energy_kwh"] = (
        result["total_power_watts"] * result["hours_per_day"] / 1000
    )
    result["daily_cost_rs"] = result["daily_energy_kwh"] * rate
    result["monthly_energy_kwh"] = result["daily_energy_kwh"] * 30
    result["monthly_cost_rs"] = result["daily_cost_rs"] * 30
    return result


with st.sidebar:
    st.header("Settings")
    electricity_rate = st.number_input(
        "Electricity rate (₹ per kWh)",
        min_value=0.0,
        value=8.0,
        step=0.5,
        help="Use your approximate rate. Actual bills may include fixed charges, taxes, and slab rates.",
    )
    st.caption("Monthly estimates assume 30 days of similar usage.")

    st.header("Data source")
    uploaded_file = st.file_uploader("Upload an appliance CSV", type=["csv"])
    use_sample = st.checkbox("Use the included sample data", value=True)

if uploaded_file is not None:
    try:
        raw_data = pd.read_csv(uploaded_file)
        source_label = f"Uploaded file: {uploaded_file.name}"
    except Exception as exc:
        st.error(f"Couldn't read that CSV file: {exc}")
        st.stop()
elif use_sample:
    raw_data = load_sample_data()
    source_label = "Included sample dataset"
else:
    st.info("Upload a CSV file or select 'Use the included sample data' in the sidebar.")
    st.stop()

clean_data, validation_errors = validate_data(raw_data)
if validation_errors:
    st.error("Please fix the following issue(s) in your CSV:")
    for error in validation_errors:
        st.write(f"- {error}")
    st.stop()

results = calculate_energy(clean_data, electricity_rate)

st.write(f"**Data source:** {source_label}")
st.write("Edit the table below to try different appliance ratings or usage hours.")
edited_data = st.data_editor(
    clean_data[["appliance", "power_watts", "hours_per_day", "quantity"]],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "appliance": st.column_config.TextColumn("Appliance", required=True),
        "power_watts": st.column_config.NumberColumn(
            "Power (W)", min_value=0.0, step=1.0, required=True
        ),
        "hours_per_day": st.column_config.NumberColumn(
            "Hours/day", min_value=0.0, max_value=24.0, step=0.5, required=True
        ),
        "quantity": st.column_config.NumberColumn(
            "Quantity", min_value=1, step=1, required=True
        ),
    },
)

edited_data, edited_errors = validate_data(edited_data)
if edited_errors:
    st.warning("The edited table needs attention:")
    for error in edited_errors:
        st.write(f"- {error}")
    st.stop()

results = calculate_energy(edited_data, electricity_rate)
total_daily_energy = results["daily_energy_kwh"].sum()
total_daily_cost = results["daily_cost_rs"].sum()
total_monthly_energy = results["monthly_energy_kwh"].sum()
total_monthly_cost = results["monthly_cost_rs"].sum()

st.subheader("Consumption summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Daily energy", f"{total_daily_energy:,.2f} kWh")
col2.metric("Daily cost", f"₹{total_daily_cost:,.2f}")
col3.metric("30-day energy", f"{total_monthly_energy:,.2f} kWh")
col4.metric("30-day cost", f"₹{total_monthly_cost:,.2f}")

st.subheader("Appliance-level results")
display_columns = [
    "appliance",
    "power_watts",
    "quantity",
    "hours_per_day",
    "daily_energy_kwh",
    "daily_cost_rs",
    "monthly_energy_kwh",
    "monthly_cost_rs",
]
display_names = {
    "appliance": "Appliance",
    "power_watts": "Power (W/unit)",
    "quantity": "Quantity",
    "hours_per_day": "Hours/day",
    "daily_energy_kwh": "Daily energy (kWh)",
    "daily_cost_rs": "Daily cost (₹)",
    "monthly_energy_kwh": "30-day energy (kWh)",
    "monthly_cost_rs": "30-day cost (₹)",
}
st.dataframe(
    results[display_columns].rename(columns=display_names).round(2),
    use_container_width=True,
    hide_index=True,
)

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.subheader("Daily energy by appliance")
    chart_data = results.set_index("appliance")["daily_energy_kwh"].sort_values()
    fig, ax = plt.subplots(figsize=(7, 4))
    chart_data.plot(kind="barh", ax=ax)
    ax.set_xlabel("Energy (kWh/day)")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with chart_col2:
    st.subheader("Share of daily energy")
    positive_data = results.loc[results["daily_energy_kwh"] > 0, ["appliance", "daily_energy_kwh"]]
    if positive_data.empty:
        st.info("No energy use to chart yet. Increase an appliance's power or usage.")
    else:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.pie(
            positive_data["daily_energy_kwh"],
            labels=positive_data["appliance"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.axis("equal")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

st.subheader("Export your analysis")
csv_bytes = results.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download results as CSV",
    data=csv_bytes,
    file_name="energy_analysis_results.csv",
    mime="text/csv",
)

with st.expander("How are the calculations made?"):
    st.markdown(
        """
        - **Total appliance power (W)** = power rating × quantity
        - **Daily energy (kWh)** = total power (W) × hours per day ÷ 1,000
        - **Daily cost (₹)** = daily energy (kWh) × electricity rate (₹/kWh)
        - **30-day estimates** = daily value × 30

        These are estimates. Real-world consumption can vary with load, duty cycle,
        operating conditions, and actual usage. Electricity bills may include
        additional charges and tariff slabs.
        """
    )

st.caption("Built with Python, Streamlit, pandas, and Matplotlib.")
