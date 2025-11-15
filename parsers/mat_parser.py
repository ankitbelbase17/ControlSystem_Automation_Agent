"""
Parser for OpenModelica .mat result files
"""
import scipy.io as sio
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MATParser:
    """Parser for OpenModelica .mat result files"""
    
    def __init__(self, mat_file: Path):
        """
        Initialize MAT file parser
        
        Args:
            mat_file: Path to .mat file
        """
        self.mat_file = mat_file
        self.data = None
        self.variables = []
        self.time = None
        logger.info(f"MAT Parser initialized for: {mat_file}")
    
    def load(self) -> bool:
        """
        Load the .mat file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.data = sio.loadmat(str(self.mat_file))
            logger.info(f"Loaded MAT file with keys: {list(self.data.keys())}")
            
            # Extract variable names (excluding metadata)
            self.variables = [
                key for key in self.data.keys() 
                if not key.startswith('__') and key != 'time'
            ]
            
            # Try to get time vector
            if 'time' in self.data:
                self.time = self.data['time'].flatten()
            elif 'Time' in self.data:
                self.time = self.data['Time'].flatten()
            else:
                # Look for time-like variable
                for key in self.variables:
                    if 'time' in key.lower():
                        self.time = self.data[key].flatten()
                        break
            
            logger.info(f"Found {len(self.variables)} variables")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load MAT file: {e}")
            return False
    
    def get_variable_names(self) -> List[str]:
        """Get list of all variable names"""
        return self.variables.copy()
    
    def get_variable_data(self, var_name: str) -> Optional[np.ndarray]:
        """
        Get data for a specific variable
        
        Args:
            var_name: Variable name
            
        Returns:
            Numpy array of variable data, or None if not found
        """
        if self.data is None:
            logger.warning("Data not loaded. Call load() first.")
            return None
        
        if var_name in self.data:
            data = self.data[var_name]
            # Handle different array shapes
            if data.ndim > 1:
                data = data.flatten()
            return data
        else:
            logger.warning(f"Variable '{var_name}' not found")
            return None
    
    def get_time_series(self, var_name: str) -> Optional[pd.Series]:
        """
        Get time series for a variable
        
        Args:
            var_name: Variable name
            
        Returns:
            Pandas Series with time index, or None if not available
        """
        var_data = self.get_variable_data(var_name)
        
        if var_data is None:
            return None
        
        if self.time is not None:
            # Ensure same length
            min_len = min(len(self.time), len(var_data))
            return pd.Series(var_data[:min_len], index=self.time[:min_len], name=var_name)
        else:
            # No time vector, use index
            return pd.Series(var_data, name=var_name)
    
    def to_dataframe(self, variables: List[str] = None) -> pd.DataFrame:
        """
        Convert data to pandas DataFrame
        
        Args:
            variables: List of variables to include (all if None)
            
        Returns:
            DataFrame with variables as columns
        """
        if self.data is None:
            logger.warning("Data not loaded. Call load() first.")
            return pd.DataFrame()
        
        if variables is None:
            variables = self.variables
        
        df_dict = {}
        
        # Add time if available
        if self.time is not None:
            df_dict['time'] = self.time
        
        # Add variables
        for var_name in variables:
            var_data = self.get_variable_data(var_name)
            if var_data is not None:
                # Ensure same length as time
                if self.time is not None:
                    min_len = min(len(self.time), len(var_data))
                    df_dict[var_name] = var_data[:min_len]
                else:
                    df_dict[var_name] = var_data
        
        df = pd.DataFrame(df_dict)
        logger.info(f"Created DataFrame with shape {df.shape}")
        return df
    
    def get_summary(self) -> Dict:
        """
        Get summary statistics for all variables
        
        Returns:
            Dictionary with variable summaries
        """
        summary = {}
        
        for var_name in self.variables:
            var_data = self.get_variable_data(var_name)
            if var_data is not None:
                summary[var_name] = {
                    'min': float(np.min(var_data)),
                    'max': float(np.max(var_data)),
                    'mean': float(np.mean(var_data)),
                    'std': float(np.std(var_data)),
                    'shape': var_data.shape
                }
        
        return summary
    
    def filter_plot_variables(self) -> List[str]:
        """
        Filter variables suitable for plotting
        
        Returns:
            List of plottable variable names
        """
        plottable = []
        
        for var_name in self.variables:
            # Skip derivative variables (der(...))
            if 'der(' in var_name.lower():
                continue
            
            # Skip metadata-like variables
            if any(skip in var_name.lower() for skip in ['name', 'description', 'unit']):
                continue
            
            var_data = self.get_variable_data(var_name)
            if var_data is not None and len(var_data) > 1:
                # Check if variable has variance (not constant)
                if np.std(var_data) > 1e-10:
                    plottable.append(var_name)
        
        logger.info(f"Found {len(plottable)} plottable variables")
        return plottable