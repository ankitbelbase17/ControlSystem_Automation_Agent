"""
OpenModelica CLI executor for running simulations
"""
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class OMCExecutor:
    """Executes OpenModelica commands via CLI"""
    
    def __init__(self, omc_command: str = None):
        """
        Initialize OMC executor
        
        Args:
            omc_command: Path to omc executable (uses config default if None)
        """
        self.omc_command = omc_command or Config.OMC_COMMAND
        self.timeout = Config.SIMULATION_TIMEOUT
        logger.info(f"OMC Executor initialized with command: {self.omc_command}")
    
    def check_omc_available(self) -> bool:
        """Check if OpenModelica is available"""
        try:
            result = subprocess.run(
                [self.omc_command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"OpenModelica version: {result.stdout.strip()}")
                return True
            else:
                logger.error("OpenModelica not found or not working properly")
                return False
        except Exception as e:
            logger.error(f"Failed to check OpenModelica: {e}")
            return False
    
    def validate_model(self, mo_file: Path) -> Tuple[bool, str]:
        """
        Validate a Modelica model file
        
        Args:
            mo_file: Path to .mo file
            
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Validating model: {mo_file}")
        
        # Create a temporary script to check the model
        check_script = f"""
loadFile("{mo_file.absolute()}");
checkModel({mo_file.stem});
getErrorString();
"""
        
        try:
            result = subprocess.run(
                [self.omc_command],
                input=check_script,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=mo_file.parent
            )
            
            output = result.stdout + result.stderr
            
            if "Check of" in output and "completed successfully" in output:
                logger.info("Model validation successful")
                return True, output
            else:
                logger.warning(f"Model validation issues: {output}")
                return False, output
                
        except subprocess.TimeoutExpired:
            logger.error("Model validation timed out")
            return False, "Validation timed out"
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return False, str(e)
    
    def run_simulation_script(self, mos_file: Path) -> Tuple[bool, str, Optional[Path]]:
        """
        Run a simulation script
        
        Args:
            mos_file: Path to .mos file
            
        Returns:
            Tuple of (success, output_message, mat_file_path)
        """
        logger.info(f"Running simulation script: {mos_file}")
        
        try:
            # Run the simulation
            result = subprocess.run(
                [self.omc_command, str(mos_file.absolute())],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=mos_file.parent
            )
            
            output = result.stdout + result.stderr
            logger.debug(f"Simulation output: {output}")
            
            # Look for the generated .mat file
            mat_files = list(mos_file.parent.glob("*_res.mat"))
            
            if mat_files:
                mat_file = mat_files[0]
                logger.info(f"Simulation completed. Result file: {mat_file}")
                return True, output, mat_file
            else:
                logger.warning("Simulation completed but no .mat file found")
                logger.warning(f"Output: {output}")
                return False, output, None
                
        except subprocess.TimeoutExpired:
            logger.error(f"Simulation timed out after {self.timeout} seconds")
            return False, "Simulation timed out", None
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return False, str(e), None
    
    def simulate_model_direct(
        self, 
        model_name: str, 
        mo_file: Path,
        start_time: float = 0.0,
        stop_time: float = 10.0,
        num_intervals: int = 500
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Simulate a model directly without .mos script
        
        Args:
            model_name: Name of the model
            mo_file: Path to .mo file
            start_time: Simulation start time
            stop_time: Simulation stop time
            num_intervals: Number of intervals
            
        Returns:
            Tuple of (success, output_message, mat_file_path)
        """
        logger.info(f"Simulating model directly: {model_name}")
        
        # Create inline simulation commands
        sim_commands = f"""
loadFile("{mo_file.absolute()}");
simulate({model_name}, startTime={start_time}, stopTime={stop_time}, numberOfIntervals={num_intervals});
getErrorString();
"""
        
        try:
            result = subprocess.run(
                [self.omc_command],
                input=sim_commands,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=mo_file.parent
            )
            
            output = result.stdout + result.stderr
            
            # Look for result file
            mat_file = mo_file.parent / f"{model_name}_res.mat"
            
            if mat_file.exists():
                logger.info(f"Direct simulation successful: {mat_file}")
                return True, output, mat_file
            else:
                logger.error(f"Simulation failed. Output: {output}")
                return False, output, None
                
        except subprocess.TimeoutExpired:
            logger.error("Direct simulation timed out")
            return False, "Simulation timed out", None
        except Exception as e:
            logger.error(f"Direct simulation failed: {e}")
            return False, str(e), None