#!/usr/bin/env python3
"""
Common Server Runner for Hospital Project
Runs both Mobile (port 8000) and Web (port 3000) servers simultaneously

Usage:
    python3 run_servers.py          # Run both servers
    python3 run_servers.py --mobile  # Run only mobile server
    python3 run_servers.py --web     # Run only web server
    python3 run_servers.py --check   # Just check configuration
"""

import os
import sys
import time
import signal
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv
from threading import Thread

# Optional import for health checks
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def check_env_file():
    """Check if .env file exists and is configured"""
    env_path = Path(__file__).parent / ".env"
    
    print_info("Checking environment configuration...")
    
    if not env_path.exists():
        print_error(f".env file not found at: {env_path}")
        print_warning("Please create .env file in the Hospital folder with SUPABASE_URL and SUPABASE_KEY")
        return False
    
    print_success(f".env file found: {env_path}")
    
    # Load and check variables
    load_dotenv(env_path, override=True)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url:
        print_error("SUPABASE_URL not found in .env file")
        return False
    if not supabase_key:
        print_error("SUPABASE_KEY not found in .env file")
        return False
    
    print_success(f"SUPABASE_URL: {supabase_url[:30]}...")
    print_success(f"SUPABASE_KEY: {'*' * 20} (hidden)")
    return True

def check_supabase_connection():
    """Test Supabase connection"""
    print_info("Testing Supabase connection...")
    
    try:
        from supabase import create_client
        load_dotenv(Path(__file__).parent / ".env", override=True)
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print_error("Supabase credentials not found")
            return False
        
        supabase = create_client(url, key)
        
        # Test connection by querying a table
        try:
            result = supabase.table("hospitals").select("id").limit(1).execute()
            print_success("Supabase connection successful")
            return True
        except Exception as e:
            print_warning(f"Supabase connection test failed: {str(e)}")
            print_info("This might be okay if tables don't exist yet")
            return True  # Connection works, just table might not exist
    except ImportError:
        print_error("supabase package not installed. Run: pip3 install supabase")
        return False
    except Exception as e:
        print_error(f"Supabase connection error: {str(e)}")
        return False

def check_port(port):
    """Check if port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False

def wait_for_server(url, name, timeout=30):
    """Wait for server to be ready"""
    print_info(f"Waiting for {name} server to start...")
    
    if not HAS_REQUESTS:
        print_warning("requests library not installed, skipping health check")
        print_info(f"Install with: pip3 install requests")
        time.sleep(3)  # Just wait a bit
        return True
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print_success(f"{name} server is ready!")
                return True
        except:
            pass
        time.sleep(1)
    
    print_warning(f"{name} server did not respond within {timeout} seconds")
    return False

def run_mobile_server():
    """Run mobile server on port 8000"""
    backend_dir = Path(__file__).parent / "backend"
    server_file = backend_dir / "server_mobile.py"
    
    if not server_file.exists():
        print_error(f"Mobile server file not found: {server_file}")
        return None
    
    print_info(f"Starting Mobile Server (Port 8000)...")
    print_info(f"Directory: {backend_dir}")
    
    # Change to backend directory and run server
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    process = subprocess.Popen(
        [sys.executable, "server_mobile.py"],
        cwd=str(backend_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return process

def run_web_server():
    """Run web server on port 3000"""
    backend_dir = Path(__file__).parent / "backend"
    server_file = backend_dir / "server_web.py"
    
    if not server_file.exists():
        print_error(f"Web server file not found: {server_file}")
        return None
    
    print_info(f"Starting Web Server (Port 3000)...")
    print_info(f"Directory: {backend_dir}")
    
    # Change to backend directory and run server
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    process = subprocess.Popen(
        [sys.executable, "server_web.py"],
        cwd=str(backend_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return process

def print_output(process, name, color):
    """Print output from server process"""
    for line in iter(process.stdout.readline, ''):
        if line:
            print(f"{color}[{name}]{Colors.RESET} {line.rstrip()}")

def main():
    parser = argparse.ArgumentParser(description='Run Hospital Project Servers')
    parser.add_argument('--mobile', action='store_true', help='Run only mobile server')
    parser.add_argument('--web', action='store_true', help='Run only web server')
    parser.add_argument('--check', action='store_true', help='Just check configuration')
    args = parser.parse_args()
    
    print_header("Hospital Project - Server Runner")
    
    # Check configuration
    if not check_env_file():
        sys.exit(1)
    
    if not check_supabase_connection():
        print_warning("Continuing anyway, but Supabase may not work properly")
    
    if args.check:
        print_success("Configuration check completed!")
        return
    
    # Determine which servers to run
    run_mobile = args.mobile or (not args.web and not args.mobile)
    run_web = args.web or (not args.mobile and not args.web)
    
    # Check ports
    if run_mobile and not check_port(8000):
        print_error("Port 8000 is already in use. Stop the process using it first.")
        print_info("Find process: lsof -ti:8000")
        print_info("Kill process: kill $(lsof -ti:8000)")
        sys.exit(1)
    
    if run_web and not check_port(3000):
        print_error("Port 3000 is already in use. Stop the process using it first.")
        print_info("Find process: lsof -ti:3000")
        print_info("Kill process: kill $(lsof -ti:3000)")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start servers
        if run_mobile:
            mobile_process = run_mobile_server()
            if mobile_process:
                processes.append(("Mobile", mobile_process, Colors.CYAN))
                # Start thread to print output
                Thread(target=print_output, args=(mobile_process, "Mobile", Colors.CYAN), daemon=True).start()
        
        if run_web:
            web_process = run_web_server()
            if web_process:
                processes.append(("Web", web_process, Colors.MAGENTA))
                # Start thread to print output
                Thread(target=print_output, args=(web_process, "Web", Colors.MAGENTA), daemon=True).start()
        
        if not processes:
            print_error("No servers started!")
            sys.exit(1)
        
        # Wait a bit for servers to start
        time.sleep(3)
        
        # Check server status
        print_header("Server Status")
        if run_mobile:
            if wait_for_server("http://127.0.0.1:8000", "Mobile"):
                print_success("Mobile Server: http://127.0.0.1:8000")
                print_info("  - API Docs: http://127.0.0.1:8000/docs")
                print_info("  - Health: http://127.0.0.1:8000/health")
        
        if run_web:
            if wait_for_server("http://127.0.0.1:3000", "Web"):
                print_success("Web Server: http://127.0.0.1:3000")
                print_info("  - Web UI: http://127.0.0.1:3000")
                print_info("  - API Docs: http://127.0.0.1:3000/docs")
                print_info("  - Health: http://127.0.0.1:3000/health")
        
        print_header("Servers Running")
        print_info("Press CTRL+C to stop all servers\n")
        
        # Wait for processes
        for name, process, _ in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print_header("Stopping Servers")
        print_info("Received interrupt signal, shutting down...")
        
        for name, process, _ in processes:
            print_info(f"Stopping {name} server...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print_success(f"{name} server stopped")
            except subprocess.TimeoutExpired:
                print_warning(f"{name} server didn't stop gracefully, forcing...")
                process.kill()
                process.wait()
                print_success(f"{name} server killed")
        
        print_success("All servers stopped!")

if __name__ == "__main__":
    # Make script executable
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)

