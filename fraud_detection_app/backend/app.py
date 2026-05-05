# backend/app.py
# This is the main FastAPI application file that serves our fraud detection model.

# Import FastAPI to create the web server
from fastapi import FastAPI, HTTPException
# Import CORS middleware to allow the frontend to connect to this API
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic BaseModel to define the structure of incoming data
from pydantic import BaseModel
# Import pandas for easy data handling
import pandas as pd
# Import numpy for numerical processing
import numpy as np
# Import joblib to load our saved model and tools
import joblib
# Import os to check for file existence
import os

# Initialize the FastAPI app
app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GLOBALS TO STORE OUR LOADED MODEL AND TOOLS
model = None
scaler = None
encoders = None
recent_predictions = []

class Transaction(BaseModel):
    amount: float
    merchant_id: int
    transaction_type: str
    location: str
    hour: int
    day_of_week: int
    month: int
    is_weekend: int

# Function to load models lazily
def load_models():
    global model, scaler, encoders
    if model is not None:
        return True
        
    print("--- LOADING MODELS ---")
    model_path = 'fraud_model.pkl'
    scaler_path = 'scaler.pkl'
    encoders_path = 'encoders.pkl'
    
    try:
        if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(encoders_path):
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            encoders = joblib.load(encoders_path)
            print("SUCCESS: Model, Scaler, and Encoders loaded correctly!")
            return True
        else:
            print("WARNING: Model files not found!")
            return False
    except Exception as e:
        print(f"CRITICAL ERROR during loading: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.get("/")
def read_root():
    return {"message": "Fraud Detection API is running"}

@app.get("/stats")
def get_stats():
    try:
        df = pd.read_csv('credit_card_fraud_dataset.csv')
        total_tx = len(df)
        total_fraud = int(df['IsFraud'].sum())
        total_normal = total_tx - total_fraud
        fraud_pct = (total_fraud / total_tx) * 100
        avg_amt = float(df['Amount'].mean())
        fraud_by_loc = df[df['IsFraud'] == 1]['Location'].value_counts().to_dict()
        fraud_by_type = df[df['IsFraud'] == 1]['TransactionType'].value_counts().to_dict()
        
        return {
            "total_transactions": total_tx,
            "total_fraud": total_fraud,
            "total_normal": total_normal,
            "fraud_percentage": round(fraud_pct, 2),
            "avg_amount": round(avg_amt, 2),
            "fraud_by_location": fraud_by_loc,
            "fraud_by_type": fraud_by_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
def predict_fraud(tx: Transaction):
    global recent_predictions
    
    if not load_models():
        raise HTTPException(status_code=500, detail="Model could not be loaded on server.")
    
    try:
        data = tx.dict()
        type_enc = encoders['TransactionType']
        loc_enc = encoders['Location']
        
        encoded_type = type_enc.transform([data['transaction_type']])[0]
        encoded_loc = loc_enc.transform([data['location']])[0]
        
        feature_list = [
            data['amount'],
            data['merchant_id'],
            encoded_type,
            encoded_loc,
            data['hour'],
            data['day_of_week'],
            data['month'],
            data['is_weekend']
        ]
        
        feature_names = ['Amount', 'MerchantID', 'TransactionType', 'Location', 'Hour', 'DayOfWeek', 'Month', 'IsWeekend']
        input_df = pd.DataFrame([feature_list], columns=feature_names)
        input_df['Amount'] = scaler.transform(input_df[['Amount']])
        
        prediction_val = int(model.predict(input_df)[0])
        probabilities = model.predict_proba(input_df)[0]
        
        result = "FRAUD" if prediction_val == 1 else "NORMAL"
        fraud_prob = float(probabilities[1])
        normal_prob = float(probabilities[0])
        confidence = fraud_prob * 100 if prediction_val == 1 else normal_prob * 100
        
        prediction_summary = {
            "amount": data['amount'],
            "type": data['transaction_type'],
            "location": data['location'],
            "result": result,
            "confidence": round(confidence, 2)
        }
        
        recent_predictions.insert(0, prediction_summary)
        recent_predictions = recent_predictions[:10]
        
        return {
            "prediction": result,
            "confidence": round(confidence, 2),
            "fraud_probability": round(fraud_prob, 4),
            "normal_probability": round(normal_prob, 4)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recent_predictions")
def get_recent():
    return recent_predictions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
