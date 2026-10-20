# SuperKart Sales Forecasting

Predicts `Product_Store_Sales_Total` for a product in a SuperKart store using a tuned Random Forest pipeline.

## Structure
```
backend/   Flask API (app.py, requirements.txt, Dockerfile, superkart_model.joblib)
frontend/  Streamlit UI (app.py, requirements.txt, Dockerfile)
run_app.sh Builds and starts both containers on a shared Docker network
```

## Run in a GitHub Codespace
```bash
bash run_app.sh
```
Then open the **Ports** tab: port **8501** is the Streamlit app, port **7860** is the API
(set 7860 to *Public* to call it from outside the Codespace).

## API
- `GET /` health check
- `POST /v1/predict` JSON body with the 10 model features
- `POST /v1/predictbatch` multipart form with a CSV file in the field `file`
