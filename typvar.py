import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Streamlit app title
st.title("Dynamic CPA Analysis with Typical Variation Zone")

# Sidebar input
st.sidebar.header("Input Parameters")
start_date = st.sidebar.date_input("Select Start Date", value=datetime.now() - timedelta(weeks=4))
end_date = st.sidebar.date_input("Select End Date", value=datetime.now())

# Validate date range
if start_date >= end_date:
    st.sidebar.error("End Date must be later than Start Date.")

# User input for CPA values
actual_cpa = st.sidebar.text_area("Enter Actual CPA values (comma-separated):", "200, 230, 180, 210, 190")
target_cpa = st.sidebar.number_input("Enter Target CPA:", value=220)

# Add a button to start the app
if st.sidebar.button("Analyze Data"):
    try:
        # Process user input for Actual CPA values
        actual_cpa_values = [float(value.strip()) for value in actual_cpa.split(",") if value.strip()]
        
        # Adjust the end date to ensure it includes the last Sunday
        adjusted_end_date = (
            end_date + timedelta(days=(6 - end_date.weekday())) if end_date.weekday() != 6 else end_date
        )

        # Generate weekly dates
        dates = pd.date_range(start=start_date, end=adjusted_end_date, freq="W")

        # Validate the number of CPA values matches the number of weeks
        if len(actual_cpa_values) != len(dates):
            st.sidebar.warning(
                f"Please provide exactly {len(dates)} values to match the number of weeks in the date range."
            )
        else:
            # Create a DataFrame
            df = pd.DataFrame({"Date": dates, "Actual CPA": actual_cpa_values})
            df["Target CPA"] = target_cpa

            # Calculate dynamic rolling bounds
            rolling_window = 2  # Rolling window size in weeks
            df["Rolling Mean"] = df["Actual CPA"].rolling(window=rolling_window, min_periods=1).mean()
            df["Rolling Std"] = df["Actual CPA"].rolling(window=rolling_window, min_periods=1).std()

            # Dynamic bounds based on rolling mean and std
            df["Upper Bound"] = df["Rolling Mean"] + df["Rolling Std"].fillna(0)
            df["Lower Bound"] = df["Rolling Mean"] - df["Rolling Std"].fillna(0)

            # Ensure Actual CPA is contained within the bounds
            df["Upper Bound"] = np.maximum(df["Upper Bound"], df["Actual CPA"])
            df["Lower Bound"] = np.minimum(df["Lower Bound"], df["Actual CPA"])

            # Plot the data
            fig, ax = plt.subplots(figsize=(10, 6))

            # Dynamically shaped typical variation zone
            ax.fill_between(
                df["Date"], df["Upper Bound"], df["Lower Bound"], color="lightblue", alpha=0.5, label="Typical Variation"
            )
            # Target CPA line
            ax.plot(df["Date"], df["Target CPA"], color="blue", linestyle="--", label="Target CPA")
            # Actual CPA line
            ax.plot(df["Date"], df["Actual CPA"], color="darkblue", marker="o", label="Actual CPA")

            # Chart formatting
            ax.set_title("Comparison of Actual CPA, Target CPA, and Dynamically Shaped Typical Variation")
            ax.set_xlabel("Date")
            ax.set_ylabel("CPA Value")
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Display the plot
            st.pyplot(fig)

    except ValueError as e:
        st.sidebar.error("Ensure Actual CPA values are numbers, separated by commas.")
        st.sidebar.write(f"Error details: {e}")
