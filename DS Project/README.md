# Fraud Detection System

A full-stack real-time fraud detection application built with FastAPI, React, XGBoost, and SQLite.

![Architecture](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-React%2BTailwind-61DAFB)
![ML](https://img.shields.io/badge/ML-XGBoost-FF6F00)

## Features

- **Real-time Transaction Streaming**: Simulates live credit card transactions every 3 seconds
- **ML-Powered Detection**: XGBoost classifier trained on the Kaggle Credit Card Fraud dataset
- **Live Dashboard**: Real-time updating React frontend with polling
- **Dark FinTech UI**: Modern Tailwind CSS design with red/green fraud indicators
- **Interactive Charts**: Pie chart (fraud distribution) and Line chart (probability trends)
- **USD to INR Conversion**: All amounts displayed in Indian Rupees (₹)

## Project Structure

```
DS Project/
├── creditcard.csv              # Original Kaggle dataset (USD amounts)
├── train_model.py              # XGBoost model training script
├── fraud_model.pkl             # Saved model (generated after training)
├── scaler.pkl                  # Saved scaler (generated after training)
├── processed_transactions.csv  # Sample data for simulator
├── fraud_detection.db          # SQLite database (created at runtime)
├── main.py                     # FastAPI backend
├── requirements.txt            # Python dependencies
├── frontend/                   # React frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       └── components/
│           ├── StatCard.jsx
│           ├── LiveFeed.jsx
│           ├── FraudChart.jsx
│           └── ProbabilityChart.jsx
└── README.md                   # This file
```

## Quick Start

### 1. Backend Setup

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Train the model (first time only):**
```bash
python train_model.py
```

This will:
- Load `creditcard.csv`
- Convert USD amounts to INR (×83)
- Train an XGBoost classifier
- Save `fraud_model.pkl` and `scaler.pkl`
- Create `processed_transactions.csv` for simulation

**Start the FastAPI server:**
```bash
python main.py
```

The server will start on `http://localhost:8000`

Available endpoints:
- `GET /` - Health check
- `GET /transactions/recent` - Last 10 transactions
- `GET /stats` - Fraud statistics
- `GET /health` - System health

### 2. Frontend Setup

**Navigate to frontend directory:**
```bash
cd frontend
```

**Install dependencies:**
```bash
npm install
```

**Start the development server:**
```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

## How It Works

### Data Flow
1. **CSV Dataset** → `train_model.py` reads credit card transactions (USD)
2. **USD→INR Conversion** → All amounts multiplied by 83
3. **XGBoost Training** → Model learns fraud patterns
4. **Simulator Loop** → FastAPI background task picks random rows every 3 seconds
5. **Prediction** → Model predicts fraud probability
6. **SQLite Storage** → Results saved to database
7. **Frontend Polling** → React fetches updates every 3 seconds
8. **Dashboard Update** → Live feed, charts, and stats refresh automatically

### Database Schema
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    amount REAL,
    fraud_probability REAL,
    is_fraud_flag INTEGER,
    status TEXT
);
```

### API Response Format

**GET /transactions/recent**
```json
[
  {
    "id": 1,
    "timestamp": "2024-01-15T10:30:00",
    "amount": 12418.46,
    "fraud_probability": 0.02,
    "is_fraud_flag": 0,
    "status": "Legit"
  }
]
```

**GET /stats**
```json
{
  "total_analyzed": 150,
  "threats_blocked": 3,
  "fraud_percentage": 2.0
}
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn, SQLAlchemy |
| Database | SQLite |
| ML | XGBoost, Scikit-learn |
| Frontend | React 18, Vite |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Icons | Lucide React |

## Development Notes

- The simulator runs as a background task using `asyncio`
- Frontend uses `setInterval` with 3-second polling (not WebSockets)
- All monetary values are in INR (Indian Rupees)
- Fraud threshold is set at 50% probability
- Red rows in the live feed indicate detected fraud

## Troubleshooting

**Model not found error:**
Run `python train_model.py` first to generate the model files.

**CORS errors:**
The backend is configured to allow all origins (`allow_origins=["*"]`) for development.

**Database locked:**
SQLite may lock if multiple processes access it. Stop and restart the backend.

**Port conflicts:**
- Backend uses port 8000
- Frontend uses port 3000

## License

MIT License - Feel free to use and modify.

## Credits

- Dataset: [Kaggle Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- Conversion Rate: 1 USD = 83 INR (approximate)
