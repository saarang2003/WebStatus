import subprocess
import sys
import threading
import time
import signal
import os

# Global flag for graceful shutdown
shutdown_flag = False

def signal_handler(signum, frame):
    global shutdown_flag
    print(f"\nReceived signal {signum}. Initiating graceful shutdown...")
    shutdown_flag = True

def run_fastapi():
    """Run FastAPI server"""
    try:
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload" if os.getenv("DEBUG", "false").lower() == "true" else "--no-reload"
        ]
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error running FastAPI: {e}")

def run_status_checker():
    """Run status checker in background"""
    time.sleep(10)  # Wait for FastAPI to start
    try:
        subprocess.run([sys.executable, "status_checker.py"])
    except Exception as e:
        print(f"Error running status checker: {e}")

def monitor_processes():
    """Monitor and restart processes if they fail"""
    global shutdown_flag
    fastapi_process = None
    checker_process = None
    
    while not shutdown_flag:
        try:
            # Start FastAPI if not running
            if fastapi_process is None or fastapi_process.poll() is not None:
                print("Starting FastAPI server...")
                fastapi_process = subprocess.Popen([
                    sys.executable, "-m", "uvicorn",
                    "main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000"
                ])
            
            # Start status checker if not running
            if checker_process is None or checker_process.poll() is not None:
                print("Starting status checker...")
                time.sleep(5)  # Wait a bit for FastAPI
                checker_process = subprocess.Popen([
                    sys.executable, "status_checker.py"
                ])
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            shutdown_flag = True
        except Exception as e:
            print(f"Error in process monitor: {e}")
            time.sleep(5)
    
    # Cleanup
    print("Shutting down processes...")
    if fastapi_process and fastapi_process.poll() is None:
        fastapi_process.terminate()
        fastapi_process.wait()
    
    if checker_process and checker_process.poll() is None:
        checker_process.terminate()
        checker_process.wait()

def main():
    """Main entry point with different startup modes"""
    mode = os.getenv("STARTUP_MODE", "threading")  # Options: threading, monitoring, separate
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Website Status Monitor - Enhanced Edition")
    print("=" * 50)
    print(f"Startup mode: {mode}")
    
    if mode == "monitoring":
        # Process monitoring mode with auto-restart
        monitor_processes()
        
    elif mode == "separate":
        # Run only FastAPI (status checker should be run separately)
        print("Running FastAPI only. Start status_checker.py separately.")
        run_fastapi()
        
    else:
        # Default threading mode
        global shutdown_flag
        
        try:
            # Start FastAPI server in a thread
            fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
            fastapi_thread.start()
            
            # Start status checker in a thread
            checker_thread = threading.Thread(target=run_status_checker, daemon=True)
            checker_thread.start()
            
            print("Both services started successfully!")
            print("FastAPI server: http://localhost:8000")
            print("API documentation: http://localhost:8000/docs")
            print("\nPress Ctrl+C to stop all services")
            
            # Keep main thread alive
            while not shutdown_flag:
                time.sleep(1)
                
                # Check if threads are still alive
                if not fastapi_thread.is_alive():
                    print("FastAPI thread died, restarting...")
                    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
                    fastapi_thread.start()
                
                if not checker_thread.is_alive():
                    print("Status checker thread died, restarting...")
                    checker_thread = threading.Thread(target=run_status_checker, daemon=True)
                    checker_thread.start()
                    
        except KeyboardInterrupt:
            shutdown_flag = True
            print("\nShutting down gracefully...")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            print("All services stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()