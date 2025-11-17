"""
Simple test script to generate a MAT file from a basic Modelica model
"""
import sys
from pathlib import Path
from config.config import Config
from generators.model_generator import ModelGenerator
from generators.script_generator import ScriptGenerator
from executors.omc_executor import OMCExecutor
from utils.file_manager import FileManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

def generate_simple_mat_file():
    """
    Generate a simple MAT file by creating a basic Modelica model and simulating it
    """
    print("\n" + "="*70)
    print("GENERATING SIMPLE MODELICA MODEL AND MAT FILE")
    print("="*70 + "\n")
    
    # Ensure directories exist
    Config.ensure_directories()
    workspace = Config.get_workspace_path("SimplePendulum")
    
    # Step 1: Generate a simple Modelica model
    print("Step 1: Generating Modelica Model...")
    print("-" * 70)
    
    model_gen = ModelGenerator()
    model_gen.set_model_info(
        "SimplePendulum",
        "A simple pendulum model with gravity"
    )
    
    # Add parameters
    model_gen.add_parameter("m", "Real", "1.0", "kg")
    model_gen.add_parameter("L", "Real", "1.0", "m")
    model_gen.add_parameter("g", "Real", "9.81", "m/s2")
    
    # Add variables
    model_gen.add_variable("theta", "Real", "0.5")  # angle in radians
    model_gen.add_variable("omega", "Real", "0.0")  # angular velocity
    model_gen.add_variable("alpha", "Real")         # angular acceleration
    
    # Add equations
    model_gen.add_equation("der(theta) = omega")
    model_gen.add_equation("der(omega) = alpha")
    model_gen.add_equation("alpha = -(g/L) * sin(theta)")
    
    # Generate and save model
    mo_file = workspace / "SimplePendulum.mo"
    model_gen.save_model(mo_file)
    print(f"✓ Model saved to: {mo_file}")
    
    # Step 2: Generate simulation script
    print("\nStep 2: Generating Simulation Script...")
    print("-" * 70)
    
    script_gen = ScriptGenerator()
    script_gen.set_model(str(mo_file), "SimplePendulum")
    script_gen.set_simulation_time(0, 10)
    script_gen.set_solver_options(
        number_of_intervals=1000,
        tolerance=1e-6,
        method="dassl"
    )
    script_gen.add_variable_to_save("SimplePendulum.theta")
    script_gen.add_variable_to_save("SimplePendulum.omega")
    script_gen.add_variable_to_save("SimplePendulum.alpha")
    script_gen.set_directories(str(workspace), str(workspace))
    
    mos_file = workspace / "simulate_SimplePendulum.mos"
    script_gen.save_script(mos_file)
    print(f"✓ Script saved to: {mos_file}")
    
    # Step 3: Check if OpenModelica is available
    print("\nStep 3: Checking OpenModelica Installation...")
    print("-" * 70)
    
    executor = OMCExecutor()
    omc_available = executor.check_omc_available()
    
    if not omc_available:
        print("⚠ WARNING: OpenModelica (omc) is not available on this system")
        print("To install OpenModelica:")
        print("  Windows: Download from https://openmodelica.org/download/")
        print("  Ubuntu/Debian: sudo apt-get install openmodelica")
        print("  macOS: brew install openmodelica")
        print("\nGenerated files are ready to use once OpenModelica is installed.")
        return False
    
    print("✓ OpenModelica is available")
    
    # Step 4: Run simulation
    print("\nStep 4: Running Simulation...")
    print("-" * 70)
    
    try:
        success, output, mat_file = executor.run_simulation_script(mos_file)
        
        if success:
            print(f"✓ Simulation completed successfully")
            print(f"✓ MAT file generated: {mat_file}")
            
            # Check if MAT file exists
            if mat_file and Path(mat_file).exists():
                file_size = Path(mat_file).stat().st_size
                print(f"✓ MAT file size: {file_size} bytes")
                print("\n" + "="*70)
                print("SUCCESS! MAT FILE GENERATED")
                print("="*70)
                print(f"\nLocation: {mat_file}")
                print(f"Model: SimplePendulum")
                print(f"Simulation time: 0 to 10 seconds")
                print(f"Variables: theta, omega, alpha")
                print("\nYou can now:")
                print("  1. Visualize the results using the visualizers")
                print("  2. Parse the MAT file using mat_parser.py")
                print("  3. Generate plots from the simulation data")
                return True
            else:
                print("✗ MAT file was not created")
                return False
        else:
            print(f"✗ Simulation failed")
            print(f"Output: {output}")
            return False
            
    except Exception as e:
        print(f"✗ Error during simulation: {e}")
        logger.error(f"Simulation error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = generate_simple_mat_file()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
