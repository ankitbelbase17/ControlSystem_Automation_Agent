"""
Model Generator for OpenModelica - Generates .mo files from specifications
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from utils.logger import setup_logger
from config.config import Config

logger = setup_logger(__name__)


class ModelGenerator:
    """Generates Modelica model files (.mo) from specifications"""
    
    def __init__(self):
        """Initialize the model generator"""
        self.model_name = ""
        self.description = ""
        self.variables = []
        self.parameters = []
        self.inputs = []
        self.outputs = []
        self.equations = []
        self.connections = []
        self.components = []
        self.imports = []
        logger.info("ModelGenerator initialized")
    
    def set_model_info(self, name: str, description: str = ""):
        """
        Set basic model information
        
        Args:
            name: Model name
            description: Model description
        """
        self.model_name = name
        self.description = description
        logger.debug(f"Model info set: {name}")
    
    def add_variable(self, 
                    name: str, 
                    var_type: str = "Real",
                    start_value: Optional[str] = None,
                    unit: Optional[str] = None,
                    annotation: Optional[str] = None) -> None:
        """
        Add a variable to the model
        
        Args:
            name: Variable name
            var_type: Variable type (Real, Integer, Boolean)
            start_value: Initial value
            unit: Unit of measurement
            annotation: Additional annotations
        """
        var = {
            'name': name,
            'type': var_type,
            'start_value': start_value,
            'unit': unit,
            'annotation': annotation
        }
        self.variables.append(var)
        logger.debug(f"Added variable: {name} ({var_type})")
    
    def add_parameter(self,
                     name: str,
                     var_type: str = "Real",
                     value: Optional[str] = None,
                     unit: Optional[str] = None,
                     annotation: Optional[str] = None) -> None:
        """
        Add a parameter to the model
        
        Args:
            name: Parameter name
            var_type: Parameter type (Real, Integer, Boolean)
            value: Parameter value
            unit: Unit of measurement
            annotation: Additional annotations
        """
        param = {
            'name': name,
            'type': var_type,
            'value': value,
            'unit': unit,
            'annotation': annotation
        }
        self.parameters.append(param)
        logger.debug(f"Added parameter: {name} ({var_type})")
    
    def add_input(self,
                 name: str,
                 var_type: str = "Real",
                 unit: Optional[str] = None) -> None:
        """
        Add an input connector to the model
        
        Args:
            name: Input name
            var_type: Variable type
            unit: Unit of measurement
        """
        input_var = {
            'name': name,
            'type': var_type,
            'unit': unit
        }
        self.inputs.append(input_var)
        logger.debug(f"Added input: {name}")
    
    def add_output(self,
                  name: str,
                  var_type: str = "Real",
                  unit: Optional[str] = None) -> None:
        """
        Add an output connector to the model
        
        Args:
            name: Output name
            var_type: Variable type
            unit: Unit of measurement
        """
        output_var = {
            'name': name,
            'type': var_type,
            'unit': unit
        }
        self.outputs.append(output_var)
        logger.debug(f"Added output: {name}")
    
    def add_equation(self, equation: str) -> None:
        """
        Add an equation to the model
        
        Args:
            equation: Equation string (without semicolon)
        """
        if equation:
            self.equations.append(equation.strip())
            logger.debug(f"Added equation: {equation[:50]}...")
    
    def add_component(self,
                     comp_type: str,
                     comp_name: str,
                     parameters: Optional[Dict[str, str]] = None) -> None:
        """
        Add a component instance to the model
        
        Args:
            comp_type: Component type/class
            comp_name: Component instance name
            parameters: Dictionary of component parameters
        """
        component = {
            'type': comp_type,
            'name': comp_name,
            'parameters': parameters or {}
        }
        self.components.append(component)
        logger.debug(f"Added component: {comp_type} {comp_name}")
    
    def add_connection(self, 
                      from_component: str,
                      from_port: str,
                      to_component: str,
                      to_port: str) -> None:
        """
        Add a connection between components
        
        Args:
            from_component: Source component name
            from_port: Source port name
            to_component: Destination component name
            to_port: Destination port name
        """
        connection = {
            'from': f"{from_component}.{from_port}",
            'to': f"{to_component}.{to_port}"
        }
        self.connections.append(connection)
        logger.debug(f"Added connection: {connection['from']} -> {connection['to']}")
    
    def add_import(self, library: str) -> None:
        """
        Add an import statement
        
        Args:
            library: Library to import (e.g., Modelica.Blocks.Interfaces)
        """
        if library not in self.imports:
            self.imports.append(library)
            logger.debug(f"Added import: {library}")
    
    def _generate_header(self) -> str:
        """Generate model header with documentation"""
        lines = [
            "(*",
            f"  Generated Modelica Model: {self.model_name}",
            f"  Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "*)"
        ]
        return "\n".join(lines)
    
    def _generate_imports(self) -> str:
        """Generate import statements"""
        if not self.imports:
            return ""
        
        lines = [imp for imp in self.imports]
        return "\n".join(lines) + "\n"
    
    def _generate_variable_declarations(self) -> str:
        """Generate variable declaration section"""
        if not self.variables:
            return ""
        
        lines = []
        for var in self.variables:
            line = f"  {var['type']} {var['name']}"
            
            if var['unit']:
                line += f"(unit=\"{var['unit']}\""
                if var['start_value']:
                    line += f", start={var['start_value']}"
                line += ")"
            elif var['start_value']:
                line += f"(start={var['start_value']})"
            
            if var['annotation']:
                line += f" {var['annotation']}"
            
            line += ";"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _generate_parameter_declarations(self) -> str:
        """Generate parameter declaration section"""
        if not self.parameters:
            return ""
        
        lines = []
        for param in self.parameters:
            line = f"  parameter {param['type']} {param['name']}"
            
            if param['unit']:
                line += f"(unit=\"{param['unit']}\""
                if param['value']:
                    line += f", start={param['value']}"
                line += ")"
            elif param['value']:
                line += f"={param['value']}"
            
            if param['annotation']:
                line += f" {param['annotation']}"
            
            line += ";"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _generate_input_declarations(self) -> str:
        """Generate input connector declarations"""
        if not self.inputs:
            return ""
        
        lines = []
        for inp in self.inputs:
            unit_str = f"(unit=\"{inp['unit']}\") " if inp['unit'] else ""
            line = f"  Modelica.Blocks.Interfaces.RealInput {inp['name']} {unit_str};"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _generate_output_declarations(self) -> str:
        """Generate output connector declarations"""
        if not self.outputs:
            return ""
        
        lines = []
        for outp in self.outputs:
            unit_str = f"(unit=\"{outp['unit']}\") " if outp['unit'] else ""
            line = f"  Modelica.Blocks.Interfaces.RealOutput {outp['name']} {unit_str};"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _generate_component_declarations(self) -> str:
        """Generate component instance declarations"""
        if not self.components:
            return ""
        
        lines = []
        for comp in self.components:
            if comp['parameters']:
                params = ", ".join(f"{k}={v}" for k, v in comp['parameters'].items())
                line = f"  {comp['type']} {comp['name']}({params});"
            else:
                line = f"  {comp['type']} {comp['name']};"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _generate_connections(self) -> str:
        """Generate connection statements"""
        if not self.connections:
            return ""
        
        lines = []
        for conn in self.connections:
            line = f"  connect({conn['from']}, {conn['to']});"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _generate_equations(self) -> str:
        """Generate equation section"""
        if not self.equations:
            return ""
        
        lines = []
        for eq in self.equations:
            lines.append(f"  {eq};")
        
        return "\n".join(lines)
    
    def generate_model_code(self) -> str:
        """
        Generate complete Modelica model code
        
        Returns:
            Generated Modelica model as string
        """
        if not self.model_name:
            logger.error("Model name not set")
            raise ValueError("Model name must be set before generating code")
        
        sections = []
        
        # Header
        sections.append(self._generate_header())
        sections.append("")
        
        # Imports
        imports = self._generate_imports()
        if imports:
            sections.append(imports)
        
        # Model declaration
        sections.append(f"model {self.model_name}")
        
        if self.description:
            sections.append(f"  \"{self.description}\"")
        
        # Declarations
        declarations = []
        
        imports_decl = self._generate_imports()
        if imports_decl:
            declarations.append(imports_decl)
        
        inputs_decl = self._generate_input_declarations()
        if inputs_decl:
            declarations.append(inputs_decl)
        
        outputs_decl = self._generate_output_declarations()
        if outputs_decl:
            declarations.append(outputs_decl)
        
        params_decl = self._generate_parameter_declarations()
        if params_decl:
            declarations.append(params_decl)
        
        vars_decl = self._generate_variable_declarations()
        if vars_decl:
            declarations.append(vars_decl)
        
        comps_decl = self._generate_component_declarations()
        if comps_decl:
            declarations.append(comps_decl)
        
        if declarations:
            sections.append("\n".join(declarations))
        
        sections.append("equation")
        
        # Equations and connections
        equations_section = []
        
        conns = self._generate_connections()
        if conns:
            equations_section.append(conns)
        
        eqs = self._generate_equations()
        if eqs:
            equations_section.append(eqs)
        
        if equations_section:
            sections.append("\n".join(equations_section))
        
        sections.append(f"end {self.model_name};")
        
        model_code = "\n".join(sections)
        logger.info(f"Generated model code for: {self.model_name}")
        return model_code
    
    def save_model(self, output_path: Path) -> bool:
        """
        Save generated model to file
        
        Args:
            output_path: Path to save the .mo file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model_code = self.generate_model_code()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(model_code)
            
            logger.info(f"Saved model to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model specification to dictionary
        
        Returns:
            Dictionary representation of the model
        """
        return {
            'name': self.model_name,
            'description': self.description,
            'parameters': self.parameters,
            'variables': self.variables,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'equations': self.equations,
            'components': self.components,
            'connections': self.connections,
            'imports': self.imports
        }
    
    def from_dict(self, model_spec: Dict[str, Any]) -> None:
        """
        Load model specification from dictionary
        
        Args:
            model_spec: Dictionary with model specification
        """
        self.model_name = model_spec.get('name', '')
        self.description = model_spec.get('description', '')
        self.parameters = model_spec.get('parameters', [])
        self.variables = model_spec.get('variables', [])
        self.inputs = model_spec.get('inputs', [])
        self.outputs = model_spec.get('outputs', [])
        self.equations = model_spec.get('equations', [])
        self.components = model_spec.get('components', [])
        self.connections = model_spec.get('connections', [])
        self.imports = model_spec.get('imports', [])
        logger.info(f"Loaded model specification: {self.model_name}")
    
    def reset(self) -> None:
        """Reset the generator to initial state"""
        self.model_name = ""
        self.description = ""
        self.variables = []
        self.parameters = []
        self.inputs = []
        self.outputs = []
        self.equations = []
        self.connections = []
        self.components = []
        self.imports = []
        logger.debug("ModelGenerator reset")
