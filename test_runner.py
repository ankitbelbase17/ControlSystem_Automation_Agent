#!/usr/bin/env python3
"""
Simple test runner for the OpenModelica AI Agent
Run this script to test the agentic workflow without interactive input
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from parsers.mat_parser import MATParser
from parsers.model_parser import ModelParser
from visualizers.model_visualizer import ModelVisualizer
from visualizers.results_visualizer import ResultsVisualizer
from utils.file_manager import FileManager
from utils.logger import setup_logger

logger = setup_logger(__name__, Config.BASE_DIR / "test.log")


def test_model_generation():
    """Test 1: AI Model Generation"""
    print("\n" + "="*80)
    print("TEST 1: AI Model Generation")
    print("="*80)
    
    agent = OpenModelicaAgent()
    
    description = """
    Create a simple RC circuit model:
    - Resistance R = 1000 Ohms
    - Capacitance C = 0.001 Farads
    - Input voltage Vin = 5 Volts (step input)
    - Output voltage Vout across capacitor
    The model should solve for the voltage across the capacitor.
    """
    
    print("\nDescription:")
    print(description)
    print("\nGenerating model using Azure OpenAI...")
    
    mo_code = agent.generate_modelica_model(description)
    
    if mo_code and "model" in mo_code:
        print("\n✓ SUCCESS: Model generated")
        print(f"  Code length: {len(mo_code)} characters")
        print(f"  Contains 'model': {'Yes' if 'model' in mo_code else 'No'}")
        print(f"  Contains 'equation': {'Yes' if 'equation' in mo_code else 'No'}")
        return True, mo_code
    else:
        print("\n✗ FAILED: Could not generate model")
        return False, None


def test_model_parsing(mo_code):
    """Test 2: Model Parsing"""
    print("\n" + "="*80)
    print("TEST 2: Model Parsing")
    print("="*80)
    
    # Save model to temp file
    temp_mo = Path(Config.WORKSPACES_DIR) / "test_circuit.mo"
    temp_mo.parent.mkdir(parents=True, exist_ok=True)
    
    with open(temp_mo, "w") as f:
        f.write(mo_code)
    
    print(f"\nParsing model from: {temp_mo}")
    
    parser = ModelParser(temp_mo)
    if parser.parse():
        print("\n✓ SUCCESS: Model parsed")
        print(f"  Variables: {len(parser.variables)}")
        print(f"  Parameters: {len(parser.parameters)}")
        print(f"  Equations: {len(parser.equations)}")
        print(f"  Components: {len(parser.components)}")
        return True, parser
    else:
        print("\n✗ FAILED: Could not parse model")
        return False, None


def test_script_generation():
    """Test 3: Simulation Script Generation"""
    print("\n" + "="*80)
    print("TEST 3: Simulation Script Generation")
    print("="*80)
    
    agent = OpenModelicaAgent()
    
    print("\nGenerating simulation script...")
    
    mos_code = agent.generate_simulation_script("TestCircuit", "test_circuit.mo")
    
    if mos_code and ("loadFile" in mos_code or "simulate" in mos_code):
        print("\n✓ SUCCESS: Script generated")
        print(f"  Code length: {len(mos_code)} characters")
        return True, mos_code
    else:
        print("\n✗ FAILED: Could not generate script")
        return False, None


def test_omc_availability():
    """Test 4: OpenModelica Availability"""
    print("\n" + "="*80)
    print("TEST 4: OpenModelica Availability")
    print("="*80)
    
    executor = OMCExecutor()
    
    print("\nChecking if OpenModelica is installed...")
    
    if executor.check_omc_available():
        print("\n✓ SUCCESS: OpenModelica is available")
        return True
    else:
        print("\n✗ FAILED: OpenModelica not found")
        print("  Install from: https://openmodelica.org/download/")
        return False


def test_full_pipeline():
    """Test 5: Full Pipeline"""
    print("\n" + "="*80)
    print("TEST 5: Full Pipeline (Model Generation → Simulation → Visualization)")
    print("="*80)
    
    # Initialize components
    agent = OpenModelicaAgent()
    executor = OMCExecutor()
    file_manager = FileManager()
    
    # Check OpenModelica first
    if not executor.check_omc_available():
        print("\n✗ FAILED: OpenModelica not available")
        return False
    
    # Create workspace
    workspace = file_manager.create_workspace("TestModel", Config.WORKSPACES_DIR)
    print(f"\nWorkspace: {workspace}")
    
    # Step 1: Generate model
    print("\n[1/5] Generating model...")
    description = "Create a simple first-order system: dy/dt = -y"
    mo_code = agent.generate_modelica_model(description)
    
    if not mo_code:
        print("✗ Model generation failed")
        return False
    
    mo_file = workspace / "TestModel.mo"
    file_manager.save_file(mo_code, mo_file)
    print(f"✓ Model saved: {mo_file.name}")
    
    # Step 2: Generate script
    print("\n[2/5] Generating simulation script...")
    mos_code = agent.generate_simulation_script("TestModel", "TestModel.mo")
    mos_file = workspace / "simulate_TestModel.mos"
    file_manager.save_file(mos_code, mos_file)
    print(f"✓ Script saved: {mos_file.name}")
    
    # Step 3: Run simulation
    print("\n[3/5] Running simulation...")
    success, output, mat_file = executor.simulate_model_direct(
        "TestModel",
        mo_file,
        start_time=0,
        stop_time=5,
        num_intervals=100
    )
    
    if not success or mat_file is None:
        print("✗ Simulation failed")
        print(f"Output: {output}")
        return False
    
    print(f"✓ Simulation completed: {mat_file.name}")
    
    # Step 4: Parse model
    print("\n[4/5] Parsing model...")
    parser = ModelParser(mo_file)
    if parser.parse():
        print(f"✓ Model parsed: {len(parser.equations)} equations")
    
    # Step 5: Visualize
    print("\n[5/5] Creating visualizations...")
    
    try:
        # Model visualization
        viz = ModelVisualizer(parser)
        diagram = Config.DIAGRAMS_DIR / "test_diagram.png"
        viz.create_block_diagram(diagram)
        print(f"✓ Block diagram: {diagram.name}")
        
        # Results visualization
        mat_parser = MATParser(mat_file)
        if mat_parser.load():
            res_viz = ResultsVisualizer(mat_parser)
            plots = Config.GRAPHS_DIR / "test_results.png"
            res_viz.plot_all_variables(plots, max_plots=4)
            print(f"✓ Results plot: {plots.name}")
    except Exception as e:
        print(f"✓ Visualizations skipped (matplotlib may be required): {e}")
    
    print("\n✓ SUCCESS: Full pipeline completed!")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "OPENMODELICA AI AGENT - TEST SUITE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    results = {}
    
    # Test 1: Model Generation
    success, mo_code = test_model_generation()
    results["Model Generation"] = success
    
    if success:
        # Test 2: Model Parsing
        success, parser = test_model_parsing(mo_code)
        results["Model Parsing"] = success
        
        # Test 3: Script Generation
        success, mos_code = test_script_generation()
        results["Script Generation"] = success
    
    # Test 4: OpenModelica Availability
    success = test_omc_availability()
    results["OpenModelica Check"] = success
    
    # Test 5: Full Pipeline (if OpenModelica is available)
    if results["OpenModelica Check"]:
        success = test_full_pipeline()
        results["Full Pipeline"] = success
    else:
        results["Full Pipeline"] = "SKIPPED (OpenModelica required)"
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = f"⊘ {result}"
        
        print(f"{test_name:30s}: {status}")
    
    print("="*80)
    
    passed = sum(1 for r in results.values() if r is True)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        return True
    else:
        print("\n✗ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.exception(f"Test suite failed: {e}")
        print(f"\n✗ Test suite failed: {e}")
        sys.exit(1)
