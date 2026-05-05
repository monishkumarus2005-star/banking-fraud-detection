import os
import subprocess
import sys

# Get the absolute path to the backend directory
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, "fraud_detection_app", "backend")

# Change working directory to backend
print(f"Moving to: {backend_dir}")
os.chdir(backend_dir)

# Command to run uvicorn
cmd = [sys.executable, "-m", "uvicorn", "app:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]

print("Starting Fraud Detection Server...")
print("URL: http://127.0.0.1:8000")
print("Press Ctrl+C to stop.")

try:
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("\nServer stopped.")
except Exception as e:
    print(f"Error starting server: {e}")
