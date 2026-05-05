# backend/model_trainer.py
# This script trains a Random Forest model to detect fraudulent transactions.

# Import pandas for data manipulation and reading CSV files
import pandas as pd
# Import numpy for numerical operations and array handling
import numpy as np
# Import train_test_split to divide data into training and testing sets
from sklearn.model_selection import train_test_split
# Import LabelEncoder to convert categorical text labels into numbers
from sklearn.preprocessing import LabelEncoder
# Import StandardScaler to normalize numerical features for better model performance
from sklearn.preprocessing import StandardScaler
# Import RandomForestClassifier as our main machine learning algorithm
from sklearn.ensemble import RandomForestClassifier
# Import evaluation metrics to check how well our model is performing
from sklearn.metrics import classification_report, roc_auc_score
# Import SMOTE to handle class imbalance (1% fraud vs 99% normal)
from imblearn.over_sampling import SMOTE
# Import joblib to save our trained model, scaler, and encoders to disk
import joblib
# Import os to handle file paths
import os

# Define a function to train the model
def train_model():
    # Print a starting message
    print("--- Starting Model Training ---")
    
    # Load the dataset from the local CSV file
    # We use pandas read_csv to load the data into a DataFrame
    dataset_path = 'credit_card_fraud_dataset.csv'
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found!")
        return
    
    df = pd.read_csv(dataset_path)
    print(f"Dataset loaded: {len(df)} rows found.")
    
    # FEATURE ENGINEERING
    # Convert 'TransactionDate' to datetime objects to extract time-related features
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    
    # Extract 'Hour' from the timestamp (0 to 23)
    df['Hour'] = df['TransactionDate'].dt.hour
    # Extract 'DayOfWeek' (0 is Monday, 6 is Sunday)
    df['DayOfWeek'] = df['TransactionDate'].dt.dayofweek
    # Extract 'Month' (1 to 12)
    df['Month'] = df['TransactionDate'].dt.month
    # Identify if the transaction happened on a weekend (Saturday=5, Sunday=6)
    df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
    
    # DROP UNNECESSARY COLUMNS
    # 'TransactionID' is unique and doesn't help with fraud patterns
    # 'TransactionDate' is now redundant as we extracted features from it
    df = df.drop(['TransactionID', 'TransactionDate'], axis=1)
    
    # LABEL ENCODING
    # We need to convert text columns (TransactionType, Location) into numbers
    type_encoder = LabelEncoder()
    df['TransactionType'] = type_encoder.fit_transform(df['TransactionType'])
    
    loc_encoder = LabelEncoder()
    df['Location'] = loc_encoder.fit_transform(df['Location'])
    
    # Store encoders in a dictionary for easy saving/loading
    encoders = {
        'TransactionType': type_encoder,
        'Location': loc_encoder
    }
    
    # PREPARE DATA FOR SPLITTING
    # X contains our independent features (everything except IsFraud)
    X = df.drop('IsFraud', axis=1)
    # y contains the target label we want to predict (IsFraud)
    y = df['IsFraud']
    
    # TRAIN-TEST SPLIT
    # We use 80% for training and 20% for testing to see how the model generalizes
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    # FEATURE SCALING
    # We scale the 'Amount' column to ensure it doesn't dominate other features
    scaler = StandardScaler()
    X_train['Amount'] = scaler.fit_transform(X_train[['Amount']])
    X_test['Amount'] = scaler.transform(X_test[['Amount']])
    
    # HANDLE CLASS IMBALANCE (SMOTE)
    # Since only 1% are fraud, SMOTE creates synthetic fraud cases for better training
    print("Applying SMOTE to balance the training data...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    # TRAIN RANDOM FOREST MODEL
    # We initialize a Random Forest with 100 decision trees
    print("Training Random Forest model (this may take a minute)...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_resampled, y_train_resampled)
    
    # EVALUATE THE MODEL
    # We make predictions on the test set to check accuracy
    y_pred = rf_model.predict(X_test)
    # Get probabilities for ROC-AUC score calculation
    y_prob = rf_model.predict_proba(X_test)[:, 1]
    
    # Print metrics
    print("\n--- Model Evaluation ---")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}")
    
    # SAVE EVERYTHING
    # Save the trained model to a file
    joblib.dump(rf_model, 'fraud_model.pkl')
    # Save the scaler to normalize new data in the same way
    joblib.dump(scaler, 'scaler.pkl')
    # Save the encoders to handle text input in the same way
    joblib.dump(encoders, 'encoders.pkl')
    
    # Final success message
    print("\nSUCCESS: All files saved!")
    print("- fraud_model.pkl")
    print("- scaler.pkl")
    print("- encoders.pkl")

# If this script is run directly, execute the training function
if __name__ == "__main__":
    train_model()
