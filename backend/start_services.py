"""
Quick Start Script for SunoSaathi Backend Services
Run this to start all services at once for testing
"""
import subprocess
import sys
import time
import os

def start_service(name, script_path, port):
    """Start a service in a new process"""
    print(f"Starting {name} on port {port}...")
    env = os.environ.copy()
    env[f"{name.upper().replace(' ', '_')}_PORT"] = str(port)
    
    process = subprocess.Popen(
        [sys.executable, script_path],
        env=env,
        cwd=os.path.dirname(script_path)
    )
    return process

def main():
    print("=" * 60)
    print("SunoSaathi Backend Services - Quick Start")
    print("=" * 60)
    
    # Initialize database first
    print("\n[1/6] Initializing database...")
    db_init = subprocess.run(
        [sys.executable, "database/connection.py"],
        cwd=os.path.dirname(__file__)
    )
    
    if db_init.returncode != 0:
        print("❌ Database initialization failed!")
        return
    
    print("✓ Database initialized")
    time.sleep(1)
    
    # Start services
    services = []
    
    print("\n[2/6] Starting ISL Recognition Service (port 8001)...")
    services.append(start_service(
        "ISL Recognition",
        "services/isl_recognition/app.py",
        8001
    ))
    time.sleep(2)
    
    print("\n[3/6] Starting Translation Service (port 8002)...")
    services.append(start_service(
        "Translation",
        "services/translation/app.py",
        8002
    ))
    time.sleep(2)
    
    print("\n[4/6] Starting TTS Service (port 8003)...")
    services.append(start_service(
        "TTS",
        "services/tts/app.py",
        8003
    ))
    time.sleep(2)
    
    print("\n[5/6] Starting Safety Filter Service (port 8004)...")
    services.append(start_service(
        "Safety",
        "services/safety/app.py",
        8004
    ))
    time.sleep(2)
    
    print("\n[6/6] Starting API Gateway (port 8000)...")
    services.append(start_service(
        "API Gateway",
        "api_gateway/main.py",
        8000
    ))
    
    print("\n" + "=" * 60)
    print("✓ All services started!")
    print("=" * 60)
    print("\nServices running:")
    print("  - API Gateway:      http://localhost:8000")
    print("  - API Docs:         http://localhost:8000/docs")
    print("  - ISL Recognition:  http://localhost:8001")
    print("  - Translation:      http://localhost:8002")
    print("  - TTS:              http://localhost:8003")
    print("  - Safety Filter:    http://localhost:8004")
    print("\nPress Ctrl+C to stop all services...")
    
    try:
        # Keep running until Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping all services...")
        for service in services:
            service.terminate()
        print("✓ All services stopped")

if __name__ == "__main__":
    main()
