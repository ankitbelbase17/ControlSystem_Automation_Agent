"""
Configuration management for OpenModelica AI Agent
"""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

class Config:
    """Central configuration class"""
    
    # Azure OpenAI Configuration (from .env)
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY', '')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-08-01-preview')
    AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'GPT-4o-0806')
    
    # Project Paths
    BASE_DIR = Path(__file__).parent.parent
    WORKSPACES_DIR = BASE_DIR / "workspaces"
    OUTPUTS_DIR = BASE_DIR / "outputs"
    DIAGRAMS_DIR = OUTPUTS_DIR / "diagrams"
    GRAPHS_DIR = OUTPUTS_DIR / "graphs"
    
    # OpenModelica Configuration (from .env)
    OMC_COMMAND = os.getenv('OMC_COMMAND', 'omc')
    SIMULATION_TIMEOUT = int(os.getenv('SIMULATION_TIMEOUT', 300))
    
    # Agent Configuration (from .env)
    MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', 0.7))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 4000))
    
    # Visualization Configuration (from .env)
    FIGURE_DPI = int(os.getenv('FIGURE_DPI', 300))
    FIGURE_SIZE = (
        int(os.getenv('FIGURE_SIZE_WIDTH', 12)),
        int(os.getenv('FIGURE_SIZE_HEIGHT', 8))
    )
    SEABORN_STYLE = os.getenv('SEABORN_STYLE', 'darkgrid')
    COLOR_PALETTE = os.getenv('COLOR_PALETTE', 'husl')
    
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