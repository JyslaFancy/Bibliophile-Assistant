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
        result = _run_subprocess(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _run_subprocess(cmd, **kwargs):
    """Run subprocess with proper encoding for Windows."""
    import sys
    # On Windows, use utf-8 encoding to avoid charmap errors
    if platform.system() == "Windows":
        kwargs["encoding"] = "utf-8"
        kwargs["errors"] = "ignore"
    return subprocess.run(cmd, **kwargs)


def setup_ollama() -> bool:
    """
    Install Ollama based on the operating system.
    Returns True if successful, False otherwise.
    """
    import shutil
    system = platform.system().lower()
    
    console.print("\n[bold blue]Installing Ollama...[/bold blue]")
    
    try:
        if system == "linux":
            # Download the installer
            console.print("[blue]Downloading Ollama installer...[/blue]")
            result = _run_subprocess(
                ["curl", "-fsSL", "https://ollama.ai/install.sh", "-o", "install_ollama.sh"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                console.print("[red]Failed to download Ollama installer[/red]")
                console.print(f"Error: {result.stderr}")
                return False
            
            # Make executable
            os.chmod("install_ollama.sh", 0o755)
            
            # Run the installer
            console.print("[blue]Running Ollama installer...[/blue]")
            result = _run_subprocess(
                ["bash", "install_ollama.sh"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Clean up
            if os.path.exists("install_ollama.sh"):
                os.remove("install_ollama.sh")
            
            if result.returncode != 0:
                console.print(f"[red]Failed to install Ollama[/red]")
                if result.stderr:
                    console.print(f"Error: {result.stderr[:500]}")
                return False
            
            console.print("[green]Ollama installed successfully![/green]")
            
            # Verify installation
            if not check_ollama():
                console.print("[yellow]Ollama installed but not in PATH. You may need to restart your shell or add it manually.[/yellow]")
                console.print("Try: source ~/.bashrc or restart your terminal")
                return False
            
            return True
            
        elif system == "darwin":  # macOS
            console.print("[blue]Downloading Ollama installer...[/blue]")
            result = _run_subprocess(
                ["curl", "-fsSL", "https://ollama.ai/install.sh", "-o", "install_ollama.sh"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                console.print("[red]Failed to download Ollama installer[/red]")
                return False
            
            os.chmod("install_ollama.sh", 0o755)
            
            console.print("[blue]Running Ollama installer...[/blue]")
            result = _run_subprocess(
                ["bash", "install_ollama.sh"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if os.path.exists("install_ollama.sh"):
                os.remove("install_ollama.sh")
            
            if result.returncode != 0:
                console.print(f"[red]Failed to install Ollama[/red]")
                if result.stderr:
                    console.print(f"Error: {result.stderr[:500]}")
                return False
            
            console.print("[green]Ollama installed successfully![/green]")
            
            if not check_ollama():
                console.print("[yellow]Ollama installed but not in PATH.[/yellow]")
                return False
            
            return True
            
        elif system == "windows":
            console.print("[blue]Windows detected. Attempting to install via winget...[/blue]")
            
            # Try using winget
            try:
                result = _run_subprocess(
                    ["winget", "install", "-e", "--id", "Ollama.Ollama", "--silent"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes for winget install
                )
                
                if result.returncode == 0:
                    console.print("[green]Ollama installed successfully via winget![/green]")
                    
                    # Verify installation
                    if not check_ollama():
                        console.print("[yellow]Ollama installed but not in PATH yet.[/yellow]")
                        console.print("You may need to restart your terminal or computer.")
                        return False
                    
                    return True
                else:
                    console.print(f"[yellow]winget install failed (exit code: {result.returncode})[/yellow]")
                    # Try non-silent mode
                    console.print("[blue]Trying interactive winget install...[/blue]")
                    result = _run_subprocess(
                        ["winget", "install", "--id", "Ollama.Ollama"],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    if result.returncode == 0:
                        console.print("[green]Ollama installed![/green]")
                        if not check_ollama():
                            console.print("[yellow]Restart your terminal to update PATH[/yellow]")
                            return False
                        return True
                    else:
                        console.print(f"[yellow]winget not available or failed[/yellow]")
            except FileNotFoundError:
                console.print("[yellow]winget not found[/yellow]")
            except subprocess.TimeoutExpired:
                console.print("[red]winget install timed out[/red]")
            
            # Fallback: manual install instructions
            console.print("\n[bold]Manual Windows Installation:[/bold]")
            console.print("1. Open PowerShell as Administrator")
            console.print("2. Run: winget install -e --id Ollama.Ollama")
            console.print("3. Or download from: https://ollama.ai")
            console.print("\nThen restart this tool.")
            return False
        else:
            console.print(f"[yellow]Unsupported OS: {system}[/yellow]")
            console.print("Please install Ollama manually from https://ollama.ai")
            return False
            
    except subprocess.TimeoutExpired:
        console.print("[red]Ollama installation timed out[/red]")
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


def pull_model(model_name: str, progress_callback=None) -> bool:
    """
    Pull a model using Ollama.
    Returns True if successful, False otherwise.
    
    Args:
        model_name: Name of the model to pull
        progress_callback: Optional callback for progress updates
    """
    if not check_ollama():
        console.print("[red]Ollama is not installed![/red]")
        return False
    
    try:
        # Show that we're pulling
        if progress_callback:
            progress_callback(f"[blue]Pulling {model_name}...[/blue]")
        else:
            console.print(f"[blue]Pulling {model_name}...[/blue]")
        
        result = _run_subprocess(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes for larger models
        )
        
        if result.returncode == 0:
            if progress_callback:
                progress_callback(f"[green]{model_name} pulled successfully![/green]")
            else:
                console.print(f"[green]Model {model_name} pulled successfully![/green]")
            return True
        else:
            if progress_callback:
                progress_callback(f"[red]Failed to pull {model_name}[/red]")
            else:
                console.print(f"[red]Failed to pull model: {model_name}[/red]")
                if result.stderr:
                    console.print(f"Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        if progress_callback:
            progress_callback(f"[red]Timeout pulling {model_name}[/red]")
        else:
            console.print(f"[red]Timeout pulling model {model_name}[/red]")
        return False
    except Exception as e:
        if progress_callback:
            progress_callback(f"[red]Error: {str(e)[:50]}[/red]")
        else:
            console.print(f"[red]Error pulling model: {e}[/red]")
        return False


def start_ollama_server() -> bool:
    """
    Start the Ollama server if not already running.
    Returns True if server is running, False otherwise.
    """
    if not check_ollama():
        console.print("[red]Ollama is not installed[/red]")
        return False
    
    # Check if server is already running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            console.print("[green]Ollama server is already running[/green]")
            return True
    except:
        pass
    
    console.print("[blue]Starting Ollama server...[/blue]")
    
    try:
        # Start ollama serve in background
        # Note: This will continue running after the script exits
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        
        # Wait for server to start
        import time
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    console.print("[green]Ollama server started successfully[/green]")
                    return True
            except:
                pass
        
        console.print("[red]Ollama server failed to start[/red]")
        return False
        
    except Exception as e:
        console.print(f"[red]Error starting Ollama server: {e}[/red]")
        return False


def list_local_models() -> list:
    """
    List all locally available Ollama models.
    Returns a list of model names.
    """
    if not check_ollama():
        return []
    
    try:
        result = _run_subprocess(
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
