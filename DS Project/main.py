"""
FastAPI Backend for Fraud Detection System
Real-time streaming simulation with SQLite database
"""


import asyncio
import pickle
import random
import pandas as pd
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup9
SQLALCHEMY_DATABASE_URL = "sqlite:///./fraud_detection.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float)
    fraud_probability = Column(Float)
    is_fraud_flag = Column(Integer)  # 0 or 1
    status = Column(String)  # "Legit" or "Fraud"

# Pydantic models
class TransactionResponse(BaseModel):
    id: int
    timestamp: datetime
    amount: float
    fraud_probability: float
    is_fraud_flag: int
    status: str
    
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_analyzed: int
    threats_blocked: int
    fraud_percentage: float

# Create tables
Base.metadata.create_all(bind=engine)

# Global variables for simulator
data_buffer = []
model = None
scaler = None
feature_cols = None
simulator_running = False

def engineer_features_for_prediction(row: dict) -> dict:
    """Apply the same feature engineering as in training"""
    row = row.copy()
    
    # Time-based features
    row['Hour'] = (row['Time'] / 3600) % 24
    row['Day_Night'] = 1 if (row['Hour'] >= 22 or row['Hour'] <= 6) else 0
    row['Hour_Sin'] = np.sin(2 * np.pi * row['Hour'] / 24)
    row['Hour_Cos'] = np.cos(2 * np.pi * row['Hour'] / 24)
    
    # Amount transformations
    row['Amount_Log'] = np.log1p(row['Amount'])
    row['Amount_High'] = 1 if row['Amount'] > 10000 else 0
    row['Amount_Very_High'] = 1 if row['Amount'] > 50000 else 0
    
    # V-feature interactions with Amount
    row['V1_Amount'] = row['V1'] * row['Amount_Log']
    row['V3_Amount'] = row['V3'] * row['Amount_Log']
    row['V14_Amount'] = row['V14'] * row['Amount_Log']
    
    # Statistical aggregations of V-features
    v_cols = [f'V{i}' for i in range(1, 29)]
    v_values = [row[v] for v in v_cols]
    row['V_Mean'] = np.mean(v_values)
    row['V_Std'] = np.std(v_values)
    row['V_Max'] = np.max(v_values)
    row['V_Min'] = np.min(v_values)
    
    # Flag extreme V-values
    outlier_count = sum(1 for v in v_values if v > 3 or v < -3)
    row['V_Outlier'] = 1 if outlier_count > 0 else 0
    
    return row

# Load model and data
def load_model():
    """Load trained XGBoost model, scaler, and feature columns"""
    global model, scaler, feature_cols, data_buffer
    
    try:
        with open('fraud_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open('feature_cols.pkl', 'rb') as f:
            feature_cols = pickle.load(f)
        
        # Load transaction data
        data_buffer = pd.read_csv('processed_transactions.csv')
        print(f"Model loaded. Features: {len(feature_cols)}. Data buffer: {len(data_buffer)} records")
        return True
    except FileNotFoundError as e:
        print(f"Error loading model: {e}")
        print("Please run 'python train_model.py' first")
        return False

def get_db():
    """Database session generator"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def predict_fraud(transaction_data: dict) -> tuple:
    """Predict fraud probability using XGBoost model with feature engineering"""
    global model, scaler, feature_cols
    
    # Apply feature engineering
    row_engineered = engineer_features_for_prediction(transaction_data)
    
    # Extract features in correct order
    features = [[row_engineered.get(col, 0) for col in feature_cols]]
    
    # Scale features
    features_scaled = scaler.transform(features)
    
    # Predict probability
    fraud_proba = model.predict_proba(features_scaled)[0][1]
    is_fraud = 1 if fraud_proba > 0.5 else 0
    
    return fraud_proba, is_fraud

async def transaction_simulator():
    """Background task: Simulate real-time transactions every 3 seconds"""
    global simulator_running, data_buffer
    
    simulator_running = True
    print("Transaction simulator started")
    
    while simulator_running:
        try:
            # Pick random transaction from buffer
            random_idx = random.randint(0, len(data_buffer) - 1)
            row = data_buffer.iloc[random_idx].to_dict()
            
            # Predict fraud
            fraud_proba, is_fraud = predict_fraud(row)
            
            # Save to database
            db = SessionLocal()
            transaction = Transaction(
                amount=row['Amount'],
                fraud_probability=fraud_proba,
                is_fraud_flag=is_fraud,
                status="Marked Suspicious" if is_fraud else "Verified Safe"
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            db.close()
            
            print(f"[{transaction.timestamp.strftime('%H:%M:%S')}] "
                  f"Amount: ₹{transaction.amount:.2f} | "
                  f"Suspicion Prob: {fraud_proba:.2%} | "
                  f"Status: {transaction.status}")
            
        except Exception as e:
            print(f"Simulator error: {e}")
        
        # Wait 3 seconds
        await asyncio.sleep(3)

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    if load_model():
        # Start simulator as background task
        asyncio.create_task(transaction_simulator())
    else:
        print("Warning: Model not loaded. Simulator not started.")
    
    yield
    
    # Shutdown
    global simulator_running
    simulator_running = False
    print("Shutting down simulator...")

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection with streaming simulation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Fraud Detection API", "status": "running"}

@app.get("/transactions/recent", response_model=List[TransactionResponse])
async def get_recent_transactions(limit: int = 10):
    """Get the last N transactions"""
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).order_by(
            Transaction.timestamp.desc()
        ).limit(limit).all()
        return transactions
    finally:
        db.close()

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get fraud detection statistics"""
    db = SessionLocal()
    try:
        total = db.query(Transaction).count()
        fraud_count = db.query(Transaction).filter(
            Transaction.is_fraud_flag == 1
        ).count()
        
        fraud_percentage = (fraud_count / total * 100) if total > 0 else 0
        
        return StatsResponse(
            total_analyzed=total,
            threats_blocked=fraud_count,
            fraud_percentage=round(fraud_percentage, 2)
        )
    finally:
        db.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "simulator_running": simulator_running
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
