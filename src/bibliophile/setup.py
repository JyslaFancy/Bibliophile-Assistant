"""
Ollama setup and hardware detection utilities.
"""

import os
import sys
import subprocess
import platform
import psutil
import GPUtil
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()


def check_ollama() -> bool:
    """Check if Ollama is installed and available in PATH."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def setup_ollama() -> bool:
    """
    Install Ollama based on the operating system.
    Returns True if successful, False otherwise.
    """
    system = platform.system().lower()
    
    console.print("\n[bold blue]Installing Ollama...[/bold blue]")
    
    try:
        if system == "linux":
            # Try to install via curl
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.ai/install.sh", "-o", "install.sh"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                console.print("[red]Failed to download Ollama installer[/red]")
                return False
            
            result = subprocess.run(
                ["bash", "install.sh"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                console.print(f"[red]Failed to install Ollama: {result.stderr}[/red]")
                return False
            
            # Clean up
            os.remove("install.sh")
            console.print("[green]Ollama installed successfully![/green]")
            return True
            
        elif system == "darwin":  # macOS
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.ai/install.sh", "-o", "install.sh"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                console.print("[red]Failed to download Ollama installer[/red]")
                return False
            
            result = subprocess.run(
                ["bash", "install.sh"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                console.print(f"[red]Failed to install Ollama: {result.stderr}[/red]")
                return False
            
            os.remove("install.sh")
            console.print("[green]Ollama installed successfully![/green]")
            return True
            
        elif system == "windows":
            console.print("[yellow]Windows installation not yet automated.[/yellow]")
            console.print("Please download and install Ollama from https://ollama.ai")
            return False
        else:
            console.print(f"[yellow]Unsupported OS: {system}[/yellow]")
            console.print("Please install Ollama manually from https://ollama.ai")
            return False
            
    except Exception as e:
        console.print(f"[red]Error installing Ollama: {e}[/red]")
        return False


def detect_hardware() -> Dict[str, Any]:
    """
    Detect system hardware (RAM, GPU, etc.).
    Returns a dictionary with hardware information.
    """
    hardware = {
        "ram_gb": 0,
        "available_ram_gb": 0,
        "gpu": None,
        "gpu_memory_gb": None,
        "cpu_cores": 0,
        "os": platform.system(),
        "architecture": platform.machine(),
    }
    
    try:
        # RAM detection
        ram = psutil.virtual_memory()
        hardware["ram_gb"] = round(ram.total / (1024 ** 3), 2)
        hardware["available_ram_gb"] = round(ram.available / (1024 ** 3), 2)
        
        # CPU cores
        hardware["cpu_cores"] = psutil.cpu_count(logical=False) or 1
        
        # GPU detection
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                hardware["gpu"] = gpu.name
                hardware["gpu_memory_gb"] = round(gpu.memoryTotal / 1024, 2)
        except Exception:
            pass
        
    except Exception as e:
        console.print(f"[yellow]Warning: Could not detect some hardware: {e}[/yellow]")
    
    return hardware


def suggest_models(hardware: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest appropriate models based on hardware.
    Returns a dictionary with suggested chat and embedding models.
    """
    ram_gb = hardware.get("ram_gb", 0)
    gpu = hardware.get("gpu")
    gpu_memory_gb = hardware.get("gpu_memory_gb", 0)
    
    suggestions = {
        "chat": "llama3",
        "chat_reason": "Default",
        "embedding": "llama3",
        "embedding_reason": "Default",
    }
    
    # Chat model suggestions
    if gpu and gpu_memory_gb >= 24:
        suggestions["chat"] = "llama3.2:3b"
        suggestions["chat_reason"] = f"GPU with {gpu_memory_gb}GB detected"
    elif gpu and gpu_memory_gb >= 12:
        suggestions["chat"] = "llama3.2:3b"
        suggestions["chat_reason"] = f"GPU with {gpu_memory_gb}GB detected"
    elif ram_gb >= 32:
        suggestions["chat"] = "llama3.2:3b"
        suggestions["chat_reason"] = f"{ram_gb}GB RAM detected"
    elif ram_gb >= 16:
        suggestions["chat"] = "llama3.2"
        suggestions["chat_reason"] = f"{ram_gb}GB RAM - smaller model recommended"
    elif ram_gb >= 8:
        suggestions["chat"] = "llama3.1"
        suggestions["chat_reason"] = f"{ram_gb}GB RAM - lightweight model"
    else:
        suggestions["chat"] = "llama3"
        suggestions["chat_reason"] = "Low RAM - smallest model"
    
    # Embedding model suggestions (typically smaller)
    # Ollama supports various embedding models like llama3, mistral, etc.
    if ram_gb >= 16 or (gpu and gpu_memory_gb >= 8):
        suggestions["embedding"] = "llama3:latest"
        suggestions["embedding_reason"] = "Sufficient resources for larger embedding model"
    else:
        suggestions["embedding"] = "llama3"
        suggestions["embedding_reason"] = "Conservative choice for limited resources"
    
    return suggestions


def pull_model(model_name: str) -> bool:
    """
    Pull a model using Ollama.
    Returns True if successful, False otherwise.
    """
    if not check_ollama():
        console.print("[red]Ollama is not installed![/red]")
        return False
    
    console.print(f"\n[bold blue]Pulling model: {model_name}[/bold blue]")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )
        
        if result.returncode == 0:
            console.print(f"[green]Model {model_name} pulled successfully![/green]")
            return True
        else:
            console.print(f"[red]Failed to pull model: {result.stderr}[/red]")
            return False
            
    except subprocess.TimeoutExpired:
        console.print(f"[red]Timeout pulling model {model_name}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Error pulling model: {e}[/red]")
        return False


def list_local_models() -> list:
    """
    List all locally available Ollama models.
    Returns a list of model names.
    """
    if not check_ollama():
        return []
    
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            models = []
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if line.strip():
                    models.append(line.split()[0])
            return models
        return []
    except Exception:
        return []
