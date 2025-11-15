"""
Script Generator for OpenModelica - Generates .mos simulation scripts
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from utils.logger import setup_logger
from config.config import Config

logger = setup_logger(__name__)


class ScriptGenerator:
    """Generates OpenModelica simulation scripts (.mos files)"""
    
    def __init__(self):
        """Initialize the script generator"""
        self.model_path = ""
        self.model_name = ""
        self.working_directory = ""
        self.output_directory = ""
        self.start_time = 0.0
        self.stop_time = 1.0
        self.number_of_intervals = 500
        self.tolerance = 1e-6
        self.method = "dassl"
        self.variables_to_save = []
        self.solver_options = {}
        self.pre_simulation_commands = []
        self.post_simulation_commands = []
        self.output_formats = ["mat"]  # mat, csv, etc.
        logger.info("ScriptGenerator initialized")
    
    def set_model(self, model_path: str, model_name: str) -> None:
        """
        Set the model to simulate
        
        Args:
            model_path: Path to the model file or library
            model_name: Full model name (e.g., PackageName.ModelName)
        """
        self.model_path = model_path
        self.model_name = model_name
        logger.debug(f"Model set to: {model_name}")
    
    def set_simulation_time(self, start_time: float, stop_time: float) -> None:
        """
        Set simulation time range
        
        Args:
            start_time: Start time of simulation
            stop_time: Stop time of simulation
        """
        self.start_time = start_time
        self.stop_time = stop_time
        logger.debug(f"Simulation time: {start_time} to {stop_time}")
    
    def set_solver_options(self,
                          number_of_intervals: int = 500,
                          tolerance: float = 1e-6,
                          method: str = "dassl") -> None:
        """
        Set solver options
        
        Args:
            number_of_intervals: Number of output intervals
            tolerance: Solver tolerance
            method: Solver method (dassl, euler, etc.)
        """
        self.number_of_intervals = number_of_intervals
        self.tolerance = tolerance
        self.method = method
        logger.debug(f"Solver options: method={method}, tol={tolerance}, intervals={number_of_intervals}")
    
    def set_directories(self, working_dir: str, output_dir: str) -> None:
        """
        Set working and output directories
        
        Args:
            working_dir: Working directory path
            output_dir: Output directory path
        """
        self.working_directory = working_dir
        self.output_directory = output_dir
        logger.debug(f"Directories set: work={working_dir}, out={output_dir}")
    
    def add_variable_to_save(self, variable_name: str) -> None:
        """
        Add a variable to save in simulation output
        
        Args:
            variable_name: Full variable path (e.g., model.variable)
        """
        if variable_name not in self.variables_to_save:
            self.variables_to_save.append(variable_name)
            logger.debug(f"Added variable to save: {variable_name}")
    
    def add_variables_to_save(self, variables: List[str]) -> None:
        """
        Add multiple variables to save in simulation output
        
        Args:
            variables: List of variable names
        """
        for var in variables:
            self.add_variable_to_save(var)
    
    def add_solver_option(self, option_name: str, option_value: Any) -> None:
        """
        Add a custom solver option
        
        Args:
            option_name: Option name (e.g., "jacobian")
            option_value: Option value
        """
        self.solver_options[option_name] = option_value
        logger.debug(f"Added solver option: {option_name}={option_value}")
    
    def add_pre_simulation_command(self, command: str) -> None:
        """
        Add a command to execute before simulation
        
        Args:
            command: OpenModelica command
        """
        if command:
            self.pre_simulation_commands.append(command)
            logger.debug(f"Added pre-simulation command: {command[:50]}...")
    
    def add_post_simulation_command(self, command: str) -> None:
        """
        Add a command to execute after simulation
        
        Args:
            command: OpenModelica command
        """
        if command:
            self.post_simulation_commands.append(command)
            logger.debug(f"Added post-simulation command: {command[:50]}...")
    
    def set_output_formats(self, formats: List[str]) -> None:
        """
        Set output file formats
        
        Args:
            formats: List of formats (e.g., ["mat", "csv"])
        """
        self.output_formats = formats
        logger.debug(f"Output formats set to: {formats}")
    
    def _generate_header(self) -> str:
        """Generate script header with documentation"""
        lines = [
            "// Generated OpenModelica Simulation Script",
            f"// Model: {self.model_name}",
            f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "// This script simulates the model and saves results",
            ""
        ]
        return "\n".join(lines)
    
    def _generate_workspace_setup(self) -> str:
        """Generate workspace setup commands"""
        lines = []
        
        if self.working_directory:
            lines.append(f"cd(\"{self.working_directory}\");")
        
        if self.output_directory:
            lines.append(f"// Output directory: {self.output_directory}")
        
        lines.append("")
        return "\n".join(lines)
    
    def _generate_model_loading(self) -> str:
        """Generate model loading commands"""
        lines = [
            f"// Load model from {self.model_path}",
            f'loadModel(Modelica);'
        ]
        
        if self.model_path and self.model_path != "Modelica":
            lines.append(f'loadFile("{self.model_path}");')
        
        lines.append(f'loadFile(modelName="{self.model_name}");')
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_simulation_setup(self) -> str:
        """Generate simulation setup commands"""
        lines = [
            "// Simulation setup",
            f'setCommandLineOptions("+d=nogen,nofoldFunctionCalls");'
        ]
        
        # Set simulation parameters
        lines.append("")
        lines.append("// Set simulation parameters")
        
        lines.append(f'startTime = {self.start_time};')
        lines.append(f'stopTime = {self.stop_time};')
        lines.append(f'numberOfIntervals = {self.number_of_intervals};')
        lines.append(f'tolerance = {self.tolerance};')
        lines.append(f'method = "{self.method}";')
        
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_pre_simulation_commands(self) -> str:
        """Generate pre-simulation commands"""
        if not self.pre_simulation_commands:
            return ""
        
        lines = ["// Pre-simulation commands"]
        lines.extend(self.pre_simulation_commands)
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_simulation_command(self) -> str:
        """Generate simulation command"""
        lines = [
            "// Simulate the model",
            "simulate(",
            f'  {self.model_name},',
            '  startTime=startTime,',
            '  stopTime=stopTime,',
            '  numberOfIntervals=numberOfIntervals,',
            '  tolerance=tolerance,',
            '  method=method,'
        ]
        
        # Add output format if specified
        if self.output_formats:
            output_format = self.output_formats[0]
            lines.append(f'  outputFormat="{output_format}",')
        
        # Add solver options
        if self.solver_options:
            options_str = ", ".join(f'"{k}={v}"' for k, v in self.solver_options.items())
            lines.append(f'  simflags="{options_str}",')
        
        # Add variables to plot
        if self.variables_to_save:
            vars_str = '", "'.join(self.variables_to_save)
            lines.append(f'  variableFilter="{vars_str}",')
        
        lines[-1] = lines[-1].rstrip(',')  # Remove trailing comma from last option
        lines.append(');')
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_output_handling(self) -> str:
        """Generate output handling commands"""
        lines = [
            "// Handle simulation results",
            "if simulationSuccessful then",
            "  print(\"Simulation completed successfully\\n\");",
        ]
        
        if self.output_directory:
            output_file = f"{self.output_directory}/{self.model_name.split('.')[-1]}"
            lines.append(f'  print("Results saved to: {output_file}\\n");')
        else:
            lines.append(f'  print("Results saved\\n");')
        
        lines.append("else")
        lines.append('  print("Simulation failed\\n");')
        lines.append("end if;")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_post_simulation_commands(self) -> str:
        """Generate post-simulation commands"""
        if not self.post_simulation_commands:
            return ""
        
        lines = ["// Post-simulation commands"]
        lines.extend(self.post_simulation_commands)
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_script(self) -> str:
        """
        Generate complete OpenModelica simulation script
        
        Returns:
            Generated script as string
        """
        if not self.model_name:
            logger.error("Model name not set")
            raise ValueError("Model name must be set before generating script")
        
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Workspace setup
        sections.append(self._generate_workspace_setup())
        
        # Model loading
        sections.append(self._generate_model_loading())
        
        # Simulation setup
        sections.append(self._generate_simulation_setup())
        
        # Pre-simulation commands
        pre_cmds = self._generate_pre_simulation_commands()
        if pre_cmds:
            sections.append(pre_cmds)
        
        # Simulation
        sections.append(self._generate_simulation_command())
        
        # Output handling
        sections.append(self._generate_output_handling())
        
        # Post-simulation commands
        post_cmds = self._generate_post_simulation_commands()
        if post_cmds:
            sections.append(post_cmds)
        
        script = "\n".join(sections)
        logger.info(f"Generated simulation script for: {self.model_name}")
        return script
    
    def save_script(self, output_path: Path) -> bool:
        """
        Save generated script to file
        
        Args:
            output_path: Path to save the .mos file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            script = self.generate_script()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script)
            
            logger.info(f"Saved script to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save script: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert script configuration to dictionary
        
        Returns:
            Dictionary representation of the script configuration
        """
        return {
            'model_path': self.model_path,
            'model_name': self.model_name,
            'working_directory': self.working_directory,
            'output_directory': self.output_directory,
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'number_of_intervals': self.number_of_intervals,
            'tolerance': self.tolerance,
            'method': self.method,
            'variables_to_save': self.variables_to_save,
            'solver_options': self.solver_options,
            'pre_simulation_commands': self.pre_simulation_commands,
            'post_simulation_commands': self.post_simulation_commands,
            'output_formats': self.output_formats
        }
    
    def from_dict(self, config: Dict[str, Any]) -> None:
        """
        Load script configuration from dictionary
        
        Args:
            config: Dictionary with script configuration
        """
        self.model_path = config.get('model_path', '')
        self.model_name = config.get('model_name', '')
        self.working_directory = config.get('working_directory', '')
        self.output_directory = config.get('output_directory', '')
        self.start_time = config.get('start_time', 0.0)
        self.stop_time = config.get('stop_time', 1.0)
        self.number_of_intervals = config.get('number_of_intervals', 500)
        self.tolerance = config.get('tolerance', 1e-6)
        self.method = config.get('method', 'dassl')
        self.variables_to_save = config.get('variables_to_save', [])
        self.solver_options = config.get('solver_options', {})
        self.pre_simulation_commands = config.get('pre_simulation_commands', [])
        self.post_simulation_commands = config.get('post_simulation_commands', [])
        self.output_formats = config.get('output_formats', ['mat'])
        logger.info(f"Loaded script configuration: {self.model_name}")
    
    def reset(self) -> None:
        """Reset the generator to initial state"""
        self.model_path = ""
        self.model_name = ""
        self.working_directory = ""
        self.output_directory = ""
        self.start_time = 0.0
        self.stop_time = 1.0
        self.number_of_intervals = 500
        self.tolerance = 1e-6
        self.method = "dassl"
        self.variables_to_save = []
        self.solver_options = {}
        self.pre_simulation_commands = []
        self.post_simulation_commands = []
        self.output_formats = ["mat"]
        logger.debug("ScriptGenerator reset")


class BatchScriptGenerator:
    """Generates batch simulation scripts for multiple models"""
    
    def __init__(self):
        """Initialize batch script generator"""
        self.scripts = []
        self.parallel = False
        self.max_jobs = 1
        logger.info("BatchScriptGenerator initialized")
    
    def add_script(self, script_gen: ScriptGenerator) -> None:
        """
        Add a script generator to the batch
        
        Args:
            script_gen: ScriptGenerator instance
        """
        self.scripts.append(script_gen)
        logger.debug(f"Added script to batch: {script_gen.model_name}")
    
    def set_parallel_execution(self, parallel: bool = True, max_jobs: int = 4) -> None:
        """
        Configure parallel execution
        
        Args:
            parallel: Whether to run scripts in parallel
            max_jobs: Maximum number of parallel jobs
        """
        self.parallel = parallel
        self.max_jobs = max_jobs
        logger.debug(f"Parallel execution: {parallel}, max_jobs={max_jobs}")
    
    def generate_batch_script(self) -> str:
        """
        Generate a batch script that runs all scripts
        
        Returns:
            Generated batch script as string
        """
        lines = [
            "// Batch Simulation Script",
            f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"// Number of simulations: {len(self.scripts)}",
            ""
        ]
        
        if self.parallel:
            lines.append("// Parallel execution mode")
            lines.append(f"// Max parallel jobs: {self.max_jobs}")
        else:
            lines.append("// Sequential execution mode")
        
        lines.append("")
        
        for i, script_gen in enumerate(self.scripts, 1):
            lines.append(f"// Simulation {i}: {script_gen.model_name}")
            script = script_gen.generate_script()
            # Indent script content
            script_lines = script.split('\n')
            indented_lines = ['  ' + line if line.strip() else '' for line in script_lines]
            lines.extend(indented_lines)
            lines.append("")
        
        return "\n".join(lines)
    
    def save_batch_script(self, output_path: Path) -> bool:
        """
        Save batch script to file
        
        Args:
            output_path: Path to save the script
            
        Returns:
            True if successful, False otherwise
        """
        try:
            script = self.generate_batch_script()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script)
            
            logger.info(f"Saved batch script to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save batch script: {e}")
            return False
