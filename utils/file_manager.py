"""
File and directory management utilities
"""
import shutil
from pathlib import Path
from typing import List
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FileManager:
    """Manages file operations for the project"""
    
    @staticmethod
    def create_workspace(model_name: str, base_dir: Path) -> Path:
        """Create a unique workspace directory for a model"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace_name = f"{model_name}_{timestamp}"
        workspace_path = base_dir / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created workspace: {workspace_path}")
        return workspace_path
    
    @staticmethod
    def save_file(content: str, file_path: Path) -> bool:
        """Save content to a file"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_file(file_path: Path) -> str:
        """Read content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ""
    
    @staticmethod
    def find_files(directory: Path, pattern: str) -> List[Path]:
        """Find files matching a pattern in directory"""
        return list(directory.glob(pattern))
    
    @staticmethod
    def clean_workspace(workspace_path: Path, keep_outputs: bool = True):
        """Clean workspace, optionally keeping output files"""
        if not workspace_path.exists():
            return
        
        if keep_outputs:
            # Remove only temporary files
            patterns = ["*.o", "*.c", "*.h", "*.xml", "*.log"]
            for pattern in patterns:
                for file in workspace_path.glob(pattern):
                    file.unlink()
                    logger.debug(f"Removed temporary file: {file}")
        else:
            # Remove entire workspace
            shutil.rmtree(workspace_path)
            logger.info(f"Removed workspace: {workspace_path}")
    
    @staticmethod
    def get_model_name_from_mo(mo_file_path: Path) -> str:
        """Extract model name from .mo file"""
        try:
            content = FileManager.read_file(mo_file_path)
            # Simple extraction: look for "model ModelName"
            for line in content.split('\n'):
                if 'model ' in line and not line.strip().startswith('//'):
                    parts = line.split('model ')
                    if len(parts) > 1:
                        model_name = parts[1].split()[0].strip()
                        return model_name
        except Exception as e:
            logger.error(f"Failed to extract model name: {e}")
        return mo_file_path.stem