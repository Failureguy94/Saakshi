import os
import subprocess
import time
import sys
import webbrowser

def main():
    if not os.path.exists("out/dvr_image.img"):
        print("Generating synthetic DVR image...")
        os.makedirs("out", exist_ok=True)
        subprocess.run([sys.executable, "scripts/make_synthetic_dvr.py"], check=True)
        
    print("Starting FastAPI server...")
    # Add project root to PYTHONPATH so it finds saakshi
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(".")
    
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "demo_server.main:app", "--host", "0.0.0.0", "--port", "8000"],
        env=env
    )
    
    print("Starting Vite frontend server...")
    frontend_dir = os.path.join(os.path.abspath("."), "saakshi", "frontend")
    vite_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir
    )
    
    time.sleep(2)
    print("Opening browser...")
    webbrowser.open("http://localhost:5173")
    
    try:
        api_proc.wait()
    except KeyboardInterrupt:
        api_proc.terminate()
        vite_proc.terminate()
        
if __name__ == "__main__":
    main()
