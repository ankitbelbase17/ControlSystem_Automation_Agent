"""
Configuration management for OpenModelica AI Agent
"""
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Central configuration class"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = "https://misumi-eastus-2480-openai-test.openai.azure.com/"
    AZURE_OPENAI_API_KEY = "f79ea912919d4b86a65a5c9d4f2baf4d"
    AZURE_OPENAI_API_VERSION = "2024-08-01-preview"
    AZURE_OPENAI_DEPLOYMENT = "GPT-4o-0806"
    
    # Project Paths
    BASE_DIR = Path(__file__).parent.parent
    WORKSPACES_DIR = BASE_DIR / "workspaces"
    OUTPUTS_DIR = BASE_DIR / "outputs"
    DIAGRAMS_DIR = OUTPUTS_DIR / "diagrams"
    GRAPHS_DIR = OUTPUTS_DIR / "graphs"
    
    # OpenModelica Configuration
    OMC_COMMAND = "omc"  # Assumes omc is in PATH
    SIMULATION_TIMEOUT = 300  # seconds
    
    # Agent Configuration
    MODEL_TEMPERATURE = 0.7
    MAX_TOKENS = 4000
    
    # Visualization Configuration
    FIGURE_DPI = 300
    FIGURE_SIZE = (12, 8)
    SEABORN_STYLE = "darkgrid"
    COLOR_PALETTE = "husl"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
        cls.GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_workspace_path(cls, model_name: str) -> Path:
        """Get workspace path for a specific model"""
        workspace = cls.WORKSPACES_DIR / model_name
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "deployment": cls.AZURE_OPENAI_DEPLOYMENT,
            "temperature": cls.MODEL_TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS
        }