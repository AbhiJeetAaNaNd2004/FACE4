#!/usr/bin/env python3
"""
Fix Memory and Port Issues Script
This script helps resolve common issues with the Face Tracking System:
1. PyTorch shared memory problems
2. Port binding conflicts
3. Memory optimization
"""

import os
import sys
import subprocess
import psutil
import socket
import time
import gc
from pathlib import Path

def check_and_kill_port(port):
    """Check if port is in use and kill the process using it"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                try:
                    process = psutil.Process(conn.pid)
                    print(f"Killing process {conn.pid} ({process.name()}) using port {port}")
                    process.terminate()
                    time.sleep(2)
                    if process.is_running():
                        process.kill()
                    return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return False
    except Exception as e:
        print(f"Error checking port {port}: {e}")
        return False

def optimize_system_memory():
    """Optimize system memory settings"""
    print("🧹 Optimizing system memory...")
    
    # Force garbage collection
    gc.collect()
    
    # Set environment variables for memory optimization
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Limit to first GPU only
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    
    # Disable PyTorch JIT compilation to save memory
    os.environ['PYTORCH_JIT'] = '0'
    
    print("Memory optimization settings applied")

def configure_pytorch_memory():
    """Configure PyTorch memory settings"""
    print("Configuring PyTorch memory settings...")
    
    try:
        import torch
        
        # Set multiprocessing start method to spawn
        if hasattr(torch.multiprocessing, 'set_start_method'):
            try:
                torch.multiprocessing.set_start_method('spawn', force=True)
            except RuntimeError:
                pass  # Already set
        
        # Set sharing strategy to file_system to avoid shared memory issues
        torch.multiprocessing.set_sharing_strategy('file_system')
        
        # Set conservative thread count
        torch.set_num_threads(1)
        
        # Clear CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            # Set memory fraction
            torch.cuda.set_per_process_memory_fraction(0.6)
            print(f"CUDA available: {torch.cuda.device_count()} devices")
        
        print("PyTorch memory configuration complete")
        
    except ImportError:
        print("WARNING: PyTorch not available, skipping PyTorch configuration")
    except Exception as e:
        print(f"WARNING: Error configuring PyTorch: {e}")

def check_virtual_memory():
    """Check and display virtual memory information"""
    print("Checking system memory...")
    
    try:
        # Get virtual memory info
        vm = psutil.virtual_memory()
        print(f"Total RAM: {vm.total / (1024**3):.2f} GB")
        print(f"Available RAM: {vm.available / (1024**3):.2f} GB")
        print(f"Used RAM: {vm.used / (1024**3):.2f} GB ({vm.percent}%)")
        
        # Get swap memory info
        swap = psutil.swap_memory()
        print(f"Swap total: {swap.total / (1024**3):.2f} GB")
        print(f"Swap used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)")
        
        # Check if we have enough memory
        if vm.available < 2 * (1024**3):  # Less than 2GB available
            print("WARNING: Low memory available. Consider closing other applications.")
        
        if swap.percent > 50:
            print("WARNING: High swap usage detected. This may cause performance issues.")
            
    except Exception as e:
        print(f"Error checking memory: {e}")

def cleanup_temp_files():
    """Clean up temporary files that might be consuming space"""
    print("🧹 Cleaning up temporary files...")
    
    try:
        # Clean up Python cache files
        for root, dirs, files in os.walk('.'):
            # Remove __pycache__ directories
            if '__pycache__' in dirs:
                import shutil
                pycache_path = os.path.join(root, '__pycache__')
                shutil.rmtree(pycache_path, ignore_errors=True)
                print(f"Removed: {pycache_path}")
            
            # Remove .pyc files
            for file in files:
                if file.endswith('.pyc'):
                    pyc_path = os.path.join(root, file)
                    try:
                        os.remove(pyc_path)
                        print(f"Removed: {pyc_path}")
                    except:
                        pass
        
        print("Temporary file cleanup complete")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    print("Face Tracking System Memory and Port Fixer")
    print("=" * 50)
    
    # Check system memory
    check_virtual_memory()
    print()
    
    # Clean up temp files
    cleanup_temp_files()
    print()
    
    # Optimize memory
    optimize_system_memory()
    print()
    
    # Configure PyTorch
    configure_pytorch_memory()
    print()
    
    # Check and clean up common ports
    common_ports = [8000, 8001, 8080, 3000, 5000]
    print("Checking for port conflicts...")
    for port in common_ports:
        if check_and_kill_port(port):
            print(f"Cleaned up port {port}")
        else:
            print(f"Port {port} is free")
    
    print()
    print("System optimization complete!")
    print("Tips:")
    print("   - Start the server with fewer workers (--workers 1)")
    print("   - Disable FTS auto-start if memory is limited")
    print("   - Monitor memory usage during operation")
    
if __name__ == "__main__":
    main()