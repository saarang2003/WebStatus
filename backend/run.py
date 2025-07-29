import subprocess
import sys
import threading
import time

def run_fastapi():
    """Run FastAPI server"""
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

def run_status_checker():
    """Run status checker in background"""
    time.sleep(5)  # Wait for FastAPI to start
    subprocess.run([sys.executable, "status_checker.py"])

if __name__ == "__main__":
    # Start FastAPI server in main thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    # Start status checker in background thread
    checker_thread = threading.Thread(target=run_status_checker)
    checker_thread.daemon = True
    checker_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)