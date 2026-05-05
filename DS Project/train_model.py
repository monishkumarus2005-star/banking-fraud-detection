"""
Train XGBoost Model for Fraud Detection
Uses the Kaggle Credit Card Fraud dataset with USD to INR conversion
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
import pickle
import os

# USD to INR conversion rate
USD_TO_INR = 83.0

def load_and_prepare_data(csv_path='creditcard.csv'):
    """Load dataset and convert USD to INR"""
    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    
    # Convert Amount from USD to INR
    df['Amount'] = df['Amount'] * USD_TO_INR
    
    print(f"Dataset shape: {df.shape}")
    print(f"Fraud cases: {df['Class'].sum()} ({df['Class'].mean()*100:.2f}%)")
    print(f"Amount range (INR): {df['Amount'].min():.2f} - {df['Amount'].max():.2f}")
    
    return df

def engineer_features(df):
    """
    Create engineered features for better fraud detection.
    Adds time-based features, amount transformations, and interactions.
    """
    print("\nEngineering features...")
    df = df.copy()
    
    # Time-based features (Time is in seconds since first transaction)
    df['Hour'] = (df['Time'] / 3600) % 24  # Hour of day (0-23)
    df['Day_Night'] = ((df['Hour'] >= 22) | (df['Hour'] <= 6)).astype(int)  # Night transactions
    df['Hour_Sin'] = np.sin(2 * np.pi * df['Hour'] / 24)  # Cyclical encoding
    df['Hour_Cos'] = np.cos(2 * np.pi * df['Hour'] / 24)
    
    # Amount transformations
    df['Amount_Log'] = np.log1p(df['Amount'])  # Log-transform amount
    df['Amount_High'] = (df['Amount'] > 10000).astype(int)  # Flag high-value transactions (>10K INR)
    df['Amount_Very_High'] = (df['Amount'] > 50000).astype(int)  # Flag very high (>50K INR)
    
    # V-feature interactions with Amount
    df['V1_Amount'] = df['V1'] * df['Amount_Log']
    df['V3_Amount'] = df['V3'] * df['Amount_Log']
    df['V14_Amount'] = df['V14'] * df['Amount_Log']
    
    # Statistical aggregations of V-features
    v_cols = [f'V{i}' for i in range(1, 29)]
    df['V_Mean'] = df[v_cols].mean(axis=1)
    df['V_Std'] = df[v_cols].std(axis=1)
    df['V_Max'] = df[v_cols].max(axis=1)
    df['V_Min'] = df[v_cols].min(axis=1)
    
    # Flag extreme V-values (potential outliers)
    df['V_Outlier'] = ((df[v_cols] > 3).sum(axis=1) + (df[v_cols] < -3).sum(axis=1) > 0).astype(int)
    
    print(f"Features added: Hour, Day_Night, Hour_Sin/Cos, Amount_Log/High/Very_High, V interactions, V stats")
    return df

def create_synthetic_features(df, n_samples=10000):
    """Generate additional synthetic samples for better training"""
    print("\nGenerating balanced dataset...")
    
    fraud_samples = df[df['Class'] == 1]
    legit_samples = df[df['Class'] == 0]
    
    # Oversample fraud cases
    fraud_upsampled = fraud_samples.sample(n=min(n_samples, len(fraud_samples) * 10), 
                                           replace=True, random_state=42)
    
    # Combine with legitimate samples
    balanced_df = pd.concat([legit_samples.sample(n=min(len(legit_samples), n_samples * 5), 
                                                   random_state=42), 
                               fraud_upsampled], axis=0).sample(frac=1, random_state=42)
    
    return balanced_df

def train_model():
    """Train XGBoost model and save artifacts"""
    
    # Load data
    df = load_and_prepare_data()
    
    # Apply feature engineering
    df = engineer_features(df)
    
    # Create synthetic balanced dataset
    df_balanced = create_synthetic_features(df)
    
    # Define feature columns (original + engineered)
    feature_cols = (
        ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount'] +
        ['Hour', 'Day_Night', 'Hour_Sin', 'Hour_Cos'] +
        ['Amount_Log', 'Amount_High', 'Amount_Very_High'] +
        ['V1_Amount', 'V3_Amount', 'V14_Amount'] +
        ['V_Mean', 'V_Std', 'V_Max', 'V_Min', 'V_Outlier']
    )
    
    print(f"\nTotal features: {len(feature_cols)}")
    X = df_balanced[feature_cols]
    y = df_balanced['Class']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train XGBoost
    print("\nTraining XGBoost model...")
    model = xgb.XGBClassifier(
        n_estimators=200,  # Increased for better performance
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    print("\n=== Model Performance ===")
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\nTop 10 Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Save model and scaler
    print("\nSaving model artifacts...")
    with open('fraud_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save feature columns for main.py
    with open('feature_cols.pkl', 'wb') as f:
        pickle.dump(feature_cols, f)
    
    print("Model saved as 'fraud_model.pkl'")
    print("Scaler saved as 'scaler.pkl'")
    print("Feature columns saved as 'feature_cols.pkl'")
    
    # Save processed data for simulator
    df_sample = df.sample(n=min(10000, len(df)), random_state=42)
    df_sample.to_csv('processed_transactions.csv', index=False)
    print("Sample data saved as 'processed_transactions.csv'")
    
    return model, scaler

if __name__ == "__main__":
    train_model()
