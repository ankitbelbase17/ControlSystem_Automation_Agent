"""
Base agent class for OpenModelica AI Agent
"""
from abc import ABC, abstractmethod
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for agents"""
    
    def __init__(self, name: str = "BaseAgent"):
        """
        Initialize base agent
        
        Args:
            name: Agent name
        """
        self.name = name
        self.history = []
        logger.info(f"Agent '{name}' initialized")
    
    @abstractmethod
    def process(self, input_data: str) -> str:
        """
        Process input and generate output
        
        Args:
            input_data: Input string
            
        Returns:
            Output string
        """
        pass
    
    def add_to_history(self, input_text: str, output_text: str):
        """
        Add interaction to history
        
        Args:
            input_text: Input text
            output_text: Output text
        """
        self.history.append({
            'input': input_text,
            'output': output_text
        })
        logger.debug(f"Added to history. Total entries: {len(self.history)}")
    
    def get_history(self):
        """Get interaction history"""
        return self.history.copy()
    
    def clear_history(self):
        """Clear interaction history"""
        self.history = []
        logger.debug("Cleared history")
