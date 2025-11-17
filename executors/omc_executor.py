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
        print("[DEBUG] Initializing OMCExecutor...")
        self.omc_command = omc_command or Config.OMC_COMMAND
        self.timeout = Config.SIMULATION_TIMEOUT
        print(f"[DEBUG] OMC command: {self.omc_command}")
        print(f"[DEBUG] Simulation timeout: {self.timeout} seconds")
        print("[✓] OMCExecutor initialized")
        logger.info(f"OMC Executor initialized with command: {self.omc_command}")
    
    def check_omc_available(self) -> bool:
        """Check if OpenModelica is available"""
        try:
            print(f"[DEBUG] Checking OpenModelica availability using command: {self.omc_command}")
            result = subprocess.run(
                [self.omc_command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.strip()
                print(f"[✓] OpenModelica is available: {version_info}")
                logger.info(f"OpenModelica version: {version_info}")
                return True
            else:
                print(f"[✗] OpenModelica check failed with return code: {result.returncode}")
                logger.error("OpenModelica not found or not working properly")
                return False
        except Exception as e:
            print(f"[✗] Error checking OMC availability: {e}")
            logger.error(f"Error checking OMC availability: {e}")
            return False
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
            # Extract model name from the script to find result file
            model_name = None
            try:
                with open(mos_file, 'r') as f:
                    script_content = f.read()
                # Look for simulate(ModelName, ...) 
                for line in script_content.split('\n'):
                    if 'simulate(' in line:
                        # Extract model name
                        start = line.find('simulate(') + 9
                        end = line.find(',', start)
                        if end > start:
                            model_name = line[start:end].strip()
                            break
            except:
                pass
            
            # Run the simulation using the script file
            result = subprocess.run(
                [self.omc_command, mos_file.name],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(mos_file.parent.absolute())
            )
            
            output = result.stdout + result.stderr
            logger.debug(f"Simulation output: {output}")
            
            # Look for the generated .mat file
            if model_name:
                mat_file = mos_file.parent / f"{model_name}_res.mat"
                if mat_file.exists():
                    logger.info(f"Simulation completed. Result file: {mat_file}")
                    return True, output, mat_file
            
            # If not found with model name, search for any _res.mat file
            mat_files = list(mos_file.parent.glob("*_res.mat"))
            if mat_files:
                mat_file = mat_files[0]
                logger.info(f"Simulation completed. Result file: {mat_file}")
                return True, output, mat_file
            
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
        
        work_dir = mo_file.parent.absolute()
        mo_filename = mo_file.name
        
        # Create a proper simulation script
        script_content = f"""loadFile("{mo_filename}");
simulate({model_name}, startTime={start_time}, stopTime={stop_time}, numberOfIntervals={num_intervals});
getErrorString();
"""
        
        try:
            # Write temporary script
            temp_script = work_dir / "_temp_sim.mos"
            with open(temp_script, 'w') as f:
                f.write(script_content)
            
            # Run simulation
            result = subprocess.run(
                [self.omc_command, "_temp_sim.mos"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(work_dir)
            )
            
            output = result.stdout + result.stderr
            
            # Look for result file
            mat_file = work_dir / f"{model_name}_res.mat"
            
            if mat_file.exists():
                logger.info(f"Direct simulation successful: {mat_file}")
                # Clean up temp script
                try:
                    temp_script.unlink()
                except:
                    pass
                return True, output, mat_file
            else:
                logger.error(f"Simulation failed. No result file found.")
                logger.error(f"Output: {output}")
                # Clean up temp script
                try:
                    temp_script.unlink()
                except:
                    pass
                return False, output, None
                
        except subprocess.TimeoutExpired:
            logger.error("Direct simulation timed out")
            return False, "Simulation timed out", None
        except Exception as e:
            logger.error(f"Direct simulation failed: {e}")
            return False, str(e), None