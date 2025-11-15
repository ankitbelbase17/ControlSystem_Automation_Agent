"""
Parser for Modelica .mo files to extract structure
"""
import re
from pathlib import Path
from typing import Dict, List, Set
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ModelParser:
    """Parser for Modelica model files"""
    
    def __init__(self, mo_file: Path):
        """
        Initialize model parser
        
        Args:
            mo_file: Path to .mo file
        """
        self.mo_file = mo_file
        self.content = ""
        self.model_name = ""
        self.variables = []
        self.parameters = []
        self.equations = []
        self.components = []
        logger.info(f"Model Parser initialized for: {mo_file}")
    
    def parse(self) -> bool:
        """
        Parse the model file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.mo_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            self._extract_model_name()
            self._extract_variables()
            self._extract_parameters()
            self._extract_equations()
            self._extract_components()
            
            logger.info(f"Parsed model '{self.model_name}': "
                       f"{len(self.variables)} vars, "
                       f"{len(self.parameters)} params, "
                       f"{len(self.equations)} equations")
            return True
            
        except Exception as e:
            logger.error(f"Failed to parse model file: {e}")
            return False
    
    def _extract_model_name(self):
        """Extract model name from content"""
        match = re.search(r'model\s+(\w+)', self.content)
        if match:
            self.model_name = match.group(1)
    
    def _extract_variables(self):
        """Extract variable declarations"""
        # Pattern for Real, Integer, Boolean variables
        patterns = [
            r'(Real|Integer|Boolean)\s+(\w+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, self.content)
            for match in matches:
                var_type, var_name = match.groups()
                if not self._is_in_comment(match.start()):
                    self.variables.append({
                        'name': var_name,
                        'type': var_type,
                        'line': self.content[:match.start()].count('\n') + 1
                    })
    
    def _extract_parameters(self):
        """Extract parameter declarations"""
        pattern = r'parameter\s+(Real|Integer|Boolean)\s+(\w+)'
        matches = re.finditer(pattern, self.content)
        
        for match in matches:
            param_type, param_name = match.groups()
            if not self._is_in_comment(match.start()):
                self.parameters.append({
                    'name': param_name,
                    'type': param_type,
                    'line': self.content[:match.start()].count('\n') + 1
                })
    
    def _extract_equations(self):
        """Extract equations from equation section"""
        # Find equation section
        eq_section = re.search(r'equation(.*?)end\s+' + re.escape(self.model_name), 
                              self.content, re.DOTALL)
        
        if eq_section:
            eq_content = eq_section.group(1)
            # Split by semicolon
            equations = [eq.strip() for eq in eq_content.split(';') if eq.strip()]
            self.equations = [eq for eq in equations if not eq.startswith('//')]
    
    def _extract_components(self):
        """Extract component instances (e.g., connectors, blocks)"""
        # Pattern for component instances
        pattern = r'(\w+)\s+(\w+)\s*(?:\(.*?\))?;'
        matches = re.finditer(pattern, self.content)
        
        for match in matches:
            comp_type, comp_name = match.groups()
            # Exclude basic types and keywords
            if comp_type not in ['Real', 'Integer', 'Boolean', 'parameter', 'equation', 'model']:
                if not self._is_in_comment(match.start()):
                    self.components.append({
                        'type': comp_type,
                        'name': comp_name,
                        'line': self.content[:match.start()].count('\n') + 1
                    })
    
    def _is_in_comment(self, position: int) -> bool:
        """Check if position is inside a comment"""
        # Check single-line comment
        line_start = self.content.rfind('\n', 0, position)
        line_content = self.content[line_start:position]
        if '//' in line_content:
            return True
        
        # Check multi-line comment (simplified)
        before = self.content[:position]
        comment_starts = before.count('/*')
        comment_ends = before.count('*/')
        return comment_starts > comment_ends
    
    def get_structure(self) -> Dict:
        """
        Get model structure summary
        
        Returns:
            Dictionary with model structure information
        """
        return {
            'name': self.model_name,
            'file': str(self.mo_file),
            'variables': self.variables,
            'parameters': self.parameters,
            'equations': self.equations,
            'components': self.components,
            'stats': {
                'num_variables': len(self.variables),
                'num_parameters': len(self.parameters),
                'num_equations': len(self.equations),
                'num_components': len(self.components)
            }
        }
    
    def get_variable_names(self) -> List[str]:
        """Get list of all variable names"""
        return [var['name'] for var in self.variables]
    
    def get_parameter_names(self) -> List[str]:
        """Get list of all parameter names"""
        return [param['name'] for param in self.parameters]