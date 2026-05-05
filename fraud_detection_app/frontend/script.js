// frontend/script.js
// This file handles the interaction between the user interface and the backend API.

// Configuration: Endpoint for our FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

// Global variables for Chart.js instances to allow updating them later
let locationChart = null;
let ratioChart = null;

// EVENT: This runs as soon as the HTML page is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("Dashboard loaded. Connecting to API...");
    
    // 1. Initial health check and stats load
    checkApiConnection();
    loadDashboardData();
    updateRecentPredictions();
    
    // 2. Setup Hour Slider label update
    const hourInput = document.getElementById('hour');
    const hourValLabel = document.getElementById('hour-val');
    hourInput.addEventListener('input', (e) => {
        hourValLabel.textContent = e.target.value;
    });

    // 3. Setup prediction form submission
    const form = document.getElementById('prediction-form');
    form.addEventListener('submit', handlePredictionSubmit);

    // 4. Set interval to refresh history every 10 seconds
    setInterval(updateRecentPredictions, 10000);
});

// Function to check if the backend server is online
async function checkApiConnection() {
    const apiDot = document.getElementById('api-dot');
    const apiText = document.getElementById('api-text');
    
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            // If server responds, show green dot
            apiDot.className = 'dot dot-online';
            apiText.textContent = 'API Connected';
        } else {
             throw new Error();
        }
    } catch (error) {
        // If server is down, show red dot
        apiDot.className = 'dot dot-offline';
        apiText.textContent = 'API Offline';
    }
}

// Function to fetch stats and render charts
async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const stats = await response.json();

        // Fill out numerical cards
        document.getElementById('stat-total').textContent = stats.total_transactions.toLocaleString();
        document.getElementById('stat-fraud').textContent = stats.total_fraud.toLocaleString();
        document.getElementById('stat-normal').textContent = stats.total_normal.toLocaleString();
        document.getElementById('stat-percent').textContent = stats.fraud_percentage + '%';

        // Render the Charts
        renderLocationChart(stats.fraud_by_location);
        renderRatioChart(stats.total_normal, stats.total_fraud);

    } catch (error) {
        console.error("Error loading stats:", error);
    }
}

// Function to render the Bar Chart (Fraud by Location)
function renderLocationChart(locationData) {
    const ctx = document.getElementById('locationChart').getContext('2d');
    
    // Extract labels (city names) and data (counts)
    const labels = Object.keys(locationData);
    const data = Object.values(locationData);

    if (locationChart) locationChart.destroy(); // Clear old chart if exists

    locationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Fraud Cases',
                data: data,
                backgroundColor: '#E24B4A', // Fraud Red
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

// Function to render the Pie Chart (Ratio)
function renderRatioChart(normal, fraud) {
    const ctx = document.getElementById('ratioChart').getContext('2d');
    
    if (ratioChart) ratioChart.destroy();

    ratioChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Normal', 'Fraud'],
            datasets: [{
                data: [normal, fraud],
                backgroundColor: ['#378ADD', '#E24B4A'], // Blue vs Red
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

// Function to handle the form submission for a new prediction
async function handlePredictionSubmit(event) {
    event.preventDefault(); // Prevent page refresh

    // UI elements for loading state
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('btn-spinner');
    
    // Show spinner and disable button
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    spinner.style.display = 'block';

    // 1. Collect form data
    const payload = {
        amount: parseFloat(document.getElementById('amount').value),
        merchant_id: parseInt(document.getElementById('merchant_id').value),
        transaction_type: document.getElementById('transaction_type').value,
        location: document.getElementById('location').value,
        hour: parseInt(document.getElementById('hour').value),
        day_of_week: parseInt(document.getElementById('day_of_week').value),
        month: parseInt(document.getElementById('month').value),
        is_weekend: document.getElementById('is_weekend').checked ? 1 : 0
    };

    try {
        // 2. Send POST request to API
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        // 3. Display result area with animation
        const resultArea = document.getElementById('results-area');
        const resultBox = document.getElementById('result-box');
        const resultText = document.getElementById('result-text');
        
        resultArea.style.display = 'block';
        
        if (result.prediction === 'FRAUD') {
            resultBox.className = 'result-box result-fraud';
            resultText.textContent = '🚩 FRAUD DETECTED';
        } else {
            resultBox.className = 'result-box result-normal';
            resultText.textContent = '✅ TRANSACTION NORMAL';
        }

        // 4. Update confidence bar and values
        document.getElementById('confidence-val').textContent = result.confidence + '%';
        document.getElementById('confidence-bar').style.width = result.confidence + '%';
        document.getElementById('prob-fraud').textContent = result.fraud_probability;
        document.getElementById('prob-normal').textContent = result.normal_probability;

        // 5. Update the history table globally immediately
        updateRecentPredictions();

    } catch (error) {
        alert("Prediction failed. Make sure the API is running at localhost:8000");
    } finally {
        // Restore button state
        submitBtn.disabled = false;
        btnText.style.display = 'block';
        spinner.style.display = 'none';
    }
}

// Function to fetch and update the table with last 10 predictions
async function updateRecentPredictions() {
    try {
        const response = await fetch(`${API_BASE_URL}/recent_predictions`);
        const predictions = await response.json();
        
        const tableBody = document.getElementById('history-body');
        tableBody.innerHTML = ''; // Clear current rows

        predictions.forEach(p => {
            const row = document.createElement('tr');
            // Apply highlight class based on result
            row.className = p.result === 'FRAUD' ? 'tr-fraud' : 'tr-normal';
            
            row.innerHTML = `
                <td>$${p.amount.toFixed(2)}</td>
                <td>${p.type}</td>
                <td>${p.location}</td>
                <td><strong>${p.result}</strong></td>
                <td>${p.confidence}%</td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching history:", error);
    }
}
