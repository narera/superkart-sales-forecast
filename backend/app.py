
# Import necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize Flask app with a name
superkart_api = Flask("SuperKart")
# Keep the batch predictions in the same order as the input rows
superkart_api.json.sort_keys = False

# Load the trained model pipeline (preprocessing + Random Forest)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in training order
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page
@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Forecasting API"


# Define an endpoint to predict sales for a single product
@superkart_api.post("/v1/predict")
def predict_sales():
    # Get JSON data from the request
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    # Make sure all required features are present
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Extract the relevant features in the expected order and convert into a DataFrame
    input_data = pd.DataFrame([{f: data[f] for f in FEATURES}])

    # Make a prediction using the trained model
    prediction = float(model.predict(input_data)[0])

    # Return the prediction as JSON
    return jsonify({"Predicted_Product_Store_Sales_Total": round(prediction, 2)})


# Define an endpoint to predict sales for a batch of products uploaded as a CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "Upload a CSV file using the form field 'file'"}), 400

    # Read the CSV file into a DataFrame
    input_data = pd.read_csv(file)

    # Make sure all required features are present
    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    # Make predictions for all rows
    predictions = model.predict(input_data[FEATURES]).round(2).tolist()

    # Use Product_Id as the key if the file has one, otherwise the row index
    keys = input_data["Product_Id"].astype(str) if "Product_Id" in input_data.columns else input_data.index.astype(str)

    # Return a dictionary of {row key: predicted sales}
    return jsonify(dict(zip(keys, predictions)))


# Run the app locally (inside Docker, Gunicorn is used instead)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
