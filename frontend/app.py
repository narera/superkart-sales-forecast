
import os

import pandas as pd
import requests
import streamlit as st

# Base URL of the Flask backend ('backend' is the container name on the Docker network)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:7860")

# Known SuperKart stores, used to pre-fill the store details
STORES = {
    "OUT001": {"Store_Size": "High", "Store_Location_City_Type": "Tier 2", "Store_Type": "Supermarket Type1", "Year": 1987},
    "OUT002": {"Store_Size": "Small", "Store_Location_City_Type": "Tier 3", "Store_Type": "Food Mart", "Year": 1998},
    "OUT003": {"Store_Size": "Medium", "Store_Location_City_Type": "Tier 1", "Store_Type": "Departmental Store", "Year": 1999},
    "OUT004": {"Store_Size": "Medium", "Store_Location_City_Type": "Tier 2", "Store_Type": "Supermarket Type2", "Year": 2009},
}
SIZES = ["Small", "Medium", "High"]
TIERS = ["Tier 1", "Tier 2", "Tier 3"]
TYPES = ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="centered")
st.title("🛒 SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a SuperKart store.")

single_tab, batch_tab = st.tabs(["Single prediction", "Batch prediction"])

# ------------------------------------------------------------------ single prediction
with single_tab:
    st.subheader("Product details")
    col1, col2 = st.columns(2)
    with col1:
        Product_Weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
        Product_MRP = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=1.0)
        Product_Allocated_Area = st.number_input(
            "Product Allocated Area (share of display area)", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f"
        )
    with col2:
        Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        Product_Id_char = st.selectbox(
            "Product Group (Product ID prefix)", ["FD", "DR", "NC"],
            format_func=lambda x: {"FD": "FD - Food", "DR": "DR - Drinks", "NC": "NC - Non-Consumable"}[x],
        )
        Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

    st.subheader("Store details")
    store_choice = st.selectbox("Store", list(STORES.keys()) + ["Other / new store"], index=3)
    preset = STORES.get(store_choice)
    col3, col4 = st.columns(2)
    with col3:
        Store_Size = st.selectbox("Store Size", SIZES, index=SIZES.index(preset["Store_Size"]) if preset else 1, disabled=bool(preset))
        Store_Location_City_Type = st.selectbox(
            "Store Location City Type", TIERS, index=TIERS.index(preset["Store_Location_City_Type"]) if preset else 1, disabled=bool(preset)
        )
    with col4:
        Store_Type = st.selectbox("Store Type", TYPES, index=TYPES.index(preset["Store_Type"]) if preset else 0, disabled=bool(preset))
        Store_Establishment_Year = st.number_input(
            "Store Establishment Year", min_value=1950, max_value=2025, value=preset["Year"] if preset else 2015, disabled=bool(preset)
        )
    Store_Age_Years = 2025 - int(Store_Establishment_Year)
    st.caption(f"Store age used by the model: {Store_Age_Years} years")

    # Create JSON payload with the features expected by the model
    product_data = {
        "Product_Weight": Product_Weight,
        "Product_Sugar_Content": Product_Sugar_Content,
        "Product_Allocated_Area": Product_Allocated_Area,
        "Product_MRP": Product_MRP,
        "Store_Size": Store_Size,
        "Store_Location_City_Type": Store_Location_City_Type,
        "Store_Type": Store_Type,
        "Product_Id_char": Product_Id_char,
        "Store_Age_Years": Store_Age_Years,
        "Product_Type_Category": Product_Type_Category,
    }

    if st.button("Predict sales", type="primary"):
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
            if response.status_code == 200:
                prediction = response.json()["Predicted_Product_Store_Sales_Total"]
                st.success(f"Predicted Product Store Sales Total: **{prediction:,.2f}**")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

# ------------------------------------------------------------------ batch prediction
with batch_tab:
    st.write(
        "Upload a CSV with the columns: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, Product_MRP, "
        "Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category."
    )
    uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.write(f"Preview ({len(batch_df)} rows):")
        st.dataframe(batch_df.head())

        if st.button("Predict batch", type="primary"):
            try:
                uploaded_file.seek(0)
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                    timeout=120,
                )
                if response.status_code == 200:
                    predictions = response.json()
                    result = batch_df.copy()
                    # Show the prediction as the first column so it is visible without scrolling
                    result.insert(0, "Predicted_Sales", list(predictions.values()))
                    st.success("Batch predictions completed.")
                    st.dataframe(result)
                    st.metric("Total predicted sales", f"{result['Predicted_Sales'].sum():,.2f}")
                    st.download_button(
                        "Download predictions as CSV", result.to_csv(index=False).encode("utf-8"), "superkart_predictions.csv", "text/csv"
                    )
                else:
                    st.error(f"API error ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
