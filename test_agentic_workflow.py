"""
Complete Agentic Workflow Test
Tests the end-to-end process: Description -> Modelica Model -> Simulation Script -> MAT File
"""

import sys
from pathlib import Path
from datetime import datetime

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from generators.model_generator import ModelGenerator
from generators.script_generator import ScriptGenerator
from utils.logger import setup_logger
from config.config import Config

logger = setup_logger(__name__)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_simple_pendulum():
    """Test the agentic workflow with a simple pendulum model"""
    
    print_section("AGENTIC WORKFLOW TEST - Simple Pendulum")
    
    # Ensure output directories exist
    Config.ensure_directories()
    
    # Create workspace
    workspace = Config.get_workspace_path("SimplePendulum_Test")
    print(f"\nWorkspace: {workspace}")
    
    # Step 1: Initialize components
    print_section("Step 1: Initialize Components")
    
    try:
        agent = OpenModelicaAgent()
        print("✓ OpenModelicaAgent initialized")
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")
        agent = None
    
    executor = OMCExecutor()
    print("✓ OMCExecutor initialized")
    
    # Check if OpenModelica is available
    print("\nChecking OpenModelica availability...")
    if executor.check_omc_available():
        print("✓ OpenModelica is available")
    else:
        print("⚠ OpenModelica not found - simulation may fail")
        print("  Install OpenModelica from: https://openmodelica.org/download/")
    
    # Step 2: Generate Modelica Model
    print_section("Step 2: Generate Modelica Model")
    
    description = """
    Create a simple pendulum model:
    - Mass m = 1 kg at the end of a rod
    - Rod length L = 1 meter
    - Pivot point at origin
    - Gravity g = 9.81 m/s²
    - Initial angle theta = 0.5 radians from vertical
    - Initial angular velocity = 0 rad/s
    - Add damping with coefficient c = 0.1
    
    Output the angle theta and angular velocity omega over time.
    """
    
    if agent:
        print("Calling Azure OpenAI to generate model...")
        try:
            mo_code = agent.generate_modelica_model(description)
            print("✓ Model generated successfully")
            print("\nGenerated Model Code:")
            print("-" * 70)
            print(mo_code[:500])
            if len(mo_code) > 500:
                print(f"... ({len(mo_code)} total characters)")
            print("-" * 70)
        except Exception as e:
            print(f"✗ Failed to generate model: {e}")
            mo_code = None
    else:
        print("⚠ Skipping AI generation (agent not available)")
        print("Using pre-built model instead...")
        mo_code = create_fallback_model()
    
    if not mo_code:
        print("✗ No model code available")
        return False
    
    # Save model to file
    mo_file = workspace / "SimplePendulum.mo"
    try:
        with open(mo_file, 'w', encoding='utf-8') as f:
            f.write(mo_code)
        print(f"\n✓ Model saved to: {mo_file}")
    except Exception as e:
        print(f"✗ Failed to save model: {e}")
        return False
    
    # Step 3: Validate Model
    print_section("Step 3: Validate Model")
    
    print(f"Validating model file: {mo_file}")
    try:
        valid, message = executor.validate_model(mo_file)
        if valid:
            print("✓ Model validation successful")
        else:
            print("⚠ Model validation had issues:")
            print(message[:300])
    except Exception as e:
        print(f"⚠ Validation check skipped: {e}")
    
    # Step 4: Generate Simulation Script
    print_section("Step 4: Generate Simulation Script")
    
    if agent:
        print("Calling Azure OpenAI to generate simulation script...")
        try:
            mos_code = agent.generate_simulation_script("SimplePendulum", "SimplePendulum.mo")
            print("✓ Simulation script generated")
        except Exception as e:
            print(f"✗ Failed to generate script: {e}")
            mos_code = None
    else:
        print("⚠ Using fallback simulation script...")
        mos_code = create_fallback_script()
    
    if mos_code:
        print("\nGenerated Simulation Script:")
        print("-" * 70)
        print(mos_code[:400])
        if len(mos_code) > 400:
            print(f"... ({len(mos_code)} total characters)")
        print("-" * 70)
        
        # Save script
        mos_file = workspace / "simulate_SimplePendulum.mos"
        try:
            with open(mos_file, 'w', encoding='utf-8') as f:
                f.write(mos_code)
            print(f"\n✓ Script saved to: {mos_file}")
        except Exception as e:
            print(f"✗ Failed to save script: {e}")
            return False
    else:
        print("✗ No simulation script available")
        return False
    
    # Step 5: Run Simulation
    print_section("Step 5: Run Simulation")
    
    print("Executing simulation...")
    try:
        success, output, mat_file = executor.run_simulation_script(mos_file)
        
        if success and mat_file:
            print(f"✓ Simulation completed successfully!")
            print(f"✓ MAT file generated: {mat_file}")
            print(f"\nFile size: {mat_file.stat().st_size} bytes")
            print(f"Simulation output:\n{output[:300]}...")
            return True
        else:
            print(f"✗ Simulation failed")
            print(f"Error: {output}")
            return False
            
    except Exception as e:
        print(f"✗ Simulation execution failed: {e}")
        return False

def create_fallback_model():
    """Create a fallback simple pendulum model if API fails"""
    return """
model SimplePendulum
  "Simple pendulum model with damping"
  
  parameter Real L = 1.0 "Pendulum length (m)";
  parameter Real m = 1.0 "Mass (kg)";
  parameter Real g = 9.81 "Gravity acceleration (m/s²)";
  parameter Real c = 0.1 "Damping coefficient";
  
  Real theta(start=0.5) "Angle from vertical (rad)";
  Real omega(start=0) "Angular velocity (rad/s)";
  
  equation
    // Angular momentum equation: I*alpha = -m*g*L*sin(theta) - c*omega
    // where I = m*L²
    m * L^2 * der(omega) = -m * g * L * sin(theta) - c * omega;
    der(theta) = omega;
    
end SimplePendulum;
"""

def create_fallback_script():
    """Create a fallback simulation script if API fails"""
    return """
loadFile("SimplePendulum.mo");
simulate(SimplePendulum, startTime=0, stopTime=10, numberOfIntervals=500);
getErrorString();
"""

def test_direct_simulation():
    """Test direct simulation without script file"""
    
    print_section("DIRECT SIMULATION TEST")
    
    Config.ensure_directories()
    workspace = Config.get_workspace_path("DirectSimTest")
    
    # Create model file
    model_code = create_fallback_model()
    mo_file = workspace / "SimplePendulum.mo"
    
    with open(mo_file, 'w') as f:
        f.write(model_code)
    
    print(f"Model file created: {mo_file}")
    
    # Run direct simulation
    executor = OMCExecutor()
    
    print("\nRunning direct simulation...")
    print("Parameters:")
    print("  - Start time: 0")
    print("  - Stop time: 10")
    print("  - Intervals: 500")
    
    try:
        success, output, mat_file = executor.simulate_model_direct(
            "SimplePendulum",
            mo_file,
            start_time=0.0,
            stop_time=10.0,
            num_intervals=500
        )
        
        if success and mat_file:
            print(f"\n✓ Direct simulation successful!")
            print(f"✓ MAT file: {mat_file}")
            print(f"✓ File size: {mat_file.stat().st_size} bytes")
            return True
        else:
            print(f"\n✗ Direct simulation failed")
            print(f"Output: {output[:300]}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def main():
    """Main test runner"""
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  AGENTIC WORKFLOW TEST SUITE - Modelica Model Generation  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {Config.to_dict()}")
    
    results = {}
    
    # Test 1: Full agentic workflow
    print("\n" + "▶" * 35)
    print("TEST 1: Full Agentic Workflow")
    print("▶" * 35)
    results['full_workflow'] = test_simple_pendulum()
    
    # Test 2: Direct simulation
    print("\n" + "▶" * 35)
    print("TEST 2: Direct Simulation (fallback)")
    print("▶" * 35)
    results['direct_simulation'] = test_direct_simulation()
    
    # Summary
    print_section("TEST SUMMARY")
    
    print("\nResults:")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if all(results.values()):
        print("\n✓ All tests passed! Agentic workflow is working.")
    else:
        print("\n⚠ Some tests failed. Check error messages above.")
        print("\nCommon issues:")
        print("  1. OpenModelica not installed - install from openmodelica.org")
        print("  2. Azure OpenAI credentials not set - check .env file")
        print("  3. API rate limits - wait a few seconds and retry")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
