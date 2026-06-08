"""
Configuration management for Bibliophile Assistant.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()


class ConfigManager:
    """Manages configuration for Bibliophile Assistant."""
    
    DEFAULT_CONFIG = {
        "ollama": {
            "chat_model": "llama3",
            "embedding_model": "nomic-embed-text",
            "base_url": "http://localhost:11434"
        },
        "chroma": {
            "path": ".bibliophile/chroma",
            "persist_directory": None
        },
        "document_processing": {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "supported_extensions": [".pdf", ".docx", ".doc", ".md", ".txt", ".xlsx", ".xls", ".pptx", ".ppt"]
        },
        "collections": [],
        "version": "0.1.9"
    }
    
    def __init__(self, config_path: str):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = os.path.expanduser(config_path)
        self._config = {}
        self._loaded = False
        
        # Ensure directory exists
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
    
    def load(self) -> None:
        """Load configuration from file."""
        if self._loaded:
            return
        
        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
            self._loaded = True
        except FileNotFoundError:
            self._config = {}
            self._loaded = True
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
            self._config = {}
            self._loaded = True
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        Supports dot notation for nested keys.
        
        Args:
            key: The key to look up (e.g., "ollama.chat_model")
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        self.load()
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set configuration values.
        Merges the provided dictionary with existing config.
        
        Args:
            config: Dictionary of configuration values to set
        """
        self.load()
        
        def deep_merge(base: Dict, override: Dict) -> Dict:
            """Deep merge two dictionaries."""
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        self._config = deep_merge(self._config, config)
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration."""
        self.load()
        return self._config.copy()
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self._loaded = True
        self.save()
        console.print("[green]Configuration reset to defaults[/green]")
    
    def ensure_defaults(self) -> None:
        """Ensure all default configuration values are present."""
        self.load()
        
        def deep_update(base: Dict, update: Dict) -> Dict:
            """Update base dict with values from update dict, only for missing keys."""
            for key, value in update.items():
                if key not in base:
                    base[key] = value
                elif isinstance(base[key], dict) and isinstance(value, dict):
                    deep_update(base[key], value)
            return base
        
        self._config = deep_update(self._config, self.DEFAULT_CONFIG.copy())
        self.save()
