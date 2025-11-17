#!/usr/bin/env python3
"""
Interactive Agentic Workflow - Run simulations from console input
User interacts directly without needing to create a file
"""

import sys
import re
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def extract_model_name(modelica_code: str) -> str:
    """Extract the model name from Modelica code"""
    print("[DEBUG] Extracting model name from generated code...")
    match = re.search(r'\bmodel\s+([A-Za-z_]\w*)\b', modelica_code)
    if match:
        name = match.group(1)
        print(f"[DEBUG] Found model name: {name}")
        if name.lower() not in ['model', 'end', 'equation', 'parameter']:
            return name
    print("[DEBUG] No valid model name found, using default 'Model'")
    return "Model"


def interactive_workflow():
    """Main interactive workflow"""
    
    print("\n" + "=" * 80)
    print(" " * 15 + "INTERACTIVE AGENTIC WORKFLOW - Modelica Simulation")
    print("=" * 80 + "\n")
    
    # Initialize components
    print("[INIT] Initializing OpenModelicaAgent...")
    agent = OpenModelicaAgent()
    print("[INIT] ✓ Agent initialized\n")
    
    print("[INIT] Initializing OMCExecutor...")
    executor = OMCExecutor()
    print("[INIT] ✓ Executor initialized\n")
    
    print("[INIT] Ensuring output directories exist...")
    Config.ensure_directories()
    print("[INIT] ✓ Directories ready\n")
    
    # Check OpenModelica availability
    print("[CHECK] Checking OpenModelica availability...")
    is_available = executor.check_omc_available()
    if not is_available:
        print("[ERROR] OpenModelica not found! Please install it.")
        print("[ERROR] Download from: https://openmodelica.org/download/")
        return
    print("[CHECK] ✓ OpenModelica is available\n")
    
    # Get workspace name from user
    print("[INPUT] Enter workspace name (default: 'InteractiveTest'):")
    workspace_name = input("  > ").strip() or "InteractiveTest"
    print(f"[DEBUG] Workspace name: {workspace_name}\n")
    
    workspace = Config.get_workspace_path(workspace_name)
    print(f"[INFO] Workspace location: {workspace}\n")
    
    # Get model description from user
    print("[INPUT] Describe the system you want to simulate:")
    print("  Example: 'A simple pendulum with mass 1 kg, length 1 m, gravity 9.81'")
    print("  (Enter multi-line description. Type 'END' on a new line when done)\n")
    
    description_lines = []
    while True:
        line = input("  > ").strip()
        if line.upper() == "END":
            break
        if line:
            description_lines.append(line)
    
    description = " ".join(description_lines)
    
    if not description:
        print("[ERROR] No description provided. Exiting.")
        return
    
    print(f"\n[DEBUG] Received description ({len(description)} chars):")
    print(f"  {description[:100]}...\n")
    
    # ============================================================
    # STEP 1: Generate Model
    # ============================================================
    print("[STEP 1] Generating Modelica model from description...")
    print("[DEBUG] Calling Azure OpenAI to generate model...")
    
    try:
        mo_code = agent.generate_modelica_model(description)
        print(f"[DEBUG] Generated {len(mo_code)} characters of Modelica code")
        print("[STEP 1] ✓ Model generated successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to generate model: {e}")
        return
    
    # Extract model name
    actual_model_name = extract_model_name(mo_code)
    print(f"[DEBUG] Model name: {actual_model_name}\n")
    
    # Show generated code
    print("[DEBUG] Generated Modelica Code Preview:")
    print("-" * 80)
    code_lines = mo_code.split('\n')[:20]  # First 20 lines
    for i, line in enumerate(code_lines, 1):
        print(f"  {i:2d}: {line}")
    total_lines = len(mo_code.split('\n'))
    if total_lines > 20:
        remaining = total_lines - 20
        print(f"  ... ({remaining} more lines)")
    print("-" * 80 + "\n")
    
    # ============================================================
    # STEP 2: Save Model
    # ============================================================
    print("[STEP 2] Saving Modelica model to file...")
    model_file_name = actual_model_name.replace(" ", "_")
    mo_file = workspace / f"{model_file_name}.mo"
    
    print(f"[DEBUG] File path: {mo_file}")
    print(f"[DEBUG] File size will be: {len(mo_code)} bytes")
    
    try:
        workspace.mkdir(parents=True, exist_ok=True)
        with open(mo_file, 'w', encoding='utf-8') as f:
            bytes_written = f.write(mo_code)
        print(f"[DEBUG] Wrote {bytes_written} bytes to file")
        print(f"[STEP 2] ✓ Model saved: {mo_file}\n")
    except Exception as e:
        print(f"[ERROR] Failed to save model: {e}")
        return
    
    # ============================================================
    # STEP 3: Validate Model
    # ============================================================
    print("[STEP 3] Validating model syntax...")
    print(f"[DEBUG] Validating: {mo_file}")
    
    try:
        is_valid, validation_msg = executor.validate_model(mo_file)
        print(f"[DEBUG] Validation result: {is_valid}")
        if validation_msg:
            print(f"[DEBUG] Validation message: {validation_msg[:200]}")
        print(f"[STEP 3] ✓ Model validation complete\n")
    except Exception as e:
        print(f"[WARNING] Validation check failed: {e}\n")
    
    # ============================================================
    # STEP 4: Generate Simulation Script
    # ============================================================
    print("[STEP 4] Generating simulation script...")
    print(f"[DEBUG] Model name for simulation: {actual_model_name}")
    print(f"[DEBUG] Model file: {mo_file}")
    
    try:
        mos_code = agent.generate_simulation_script(actual_model_name, mo_file)
        print(f"[DEBUG] Generated {len(mos_code)} characters of script")
        print("[STEP 4] ✓ Simulation script generated\n")
    except Exception as e:
        print(f"[ERROR] Failed to generate script: {e}")
        return
    
    # Show script
    print("[DEBUG] Generated Simulation Script:")
    print("-" * 80)
    print(mos_code)
    print("-" * 80 + "\n")
    
    # ============================================================
    # STEP 5: Save Simulation Script
    # ============================================================
    print("[STEP 5] Saving simulation script...")
    mos_file = workspace / f"simulate_{model_file_name}.mos"
    
    print(f"[DEBUG] Script file path: {mos_file}")
    
    try:
        with open(mos_file, 'w', encoding='utf-8') as f:
            bytes_written = f.write(mos_code)
        print(f"[DEBUG] Wrote {bytes_written} bytes to script file")
        print(f"[STEP 5] ✓ Script saved: {mos_file}\n")
    except Exception as e:
        print(f"[ERROR] Failed to save script: {e}")
        return
    
    # ============================================================
    # STEP 6: Run Simulation
    # ============================================================
    print("[STEP 6] Running OpenModelica simulation...")
    print(f"[DEBUG] Script file: {mos_file}")
    print(f"[DEBUG] Simulation timeout: {Config.SIMULATION_TIMEOUT} seconds")
    
    try:
        success, output, mat_file = executor.run_simulation_script(mos_file)
        
        print(f"[DEBUG] Simulation success: {success}")
        print(f"[DEBUG] Output length: {len(str(output))} chars")
        
        if success and mat_file:
            file_size = mat_file.stat().st_size
            print(f"[DEBUG] MAT file created: {mat_file}")
            print(f"[DEBUG] MAT file size: {file_size} bytes")
            print("[STEP 6] ✓ Simulation completed successfully!\n")
        else:
            print(f"[WARNING] Simulation completed but with issues:")
            print(f"[DEBUG] {str(output)[:500]}\n")
            return
    except Exception as e:
        print(f"[ERROR] Simulation execution failed: {e}")
        return
    
    # ============================================================
    # STEP 7: Display Results
    # ============================================================
    print("=" * 80)
    print(" " * 30 + "SIMULATION RESULTS")
    print("=" * 80)
    print(f"\n[RESULT] Model:")
    print(f"  Name: {actual_model_name}")
    print(f"  File: {mo_file}")
    print(f"  Size: {mo_file.stat().st_size} bytes")
    
    print(f"\n[RESULT] Simulation:")
    print(f"  Script: {mos_file}")
    print(f"  Duration: 10 seconds (0-10)")
    print(f"  Intervals: 500")
    print(f"  Solver: dassl")
    
    print(f"\n[RESULT] Output:")
    print(f"  MAT File: {mat_file}")
    print(f"  File Size: {file_size} bytes")
    print(f"  Location: {workspace}")
    
    print(f"\n[RESULT] Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)
    print(" " * 20 + "✓ SUCCESS! MAT file generated and ready for analysis")
    print("=" * 80 + "\n")
    
    # ============================================================
    # STEP 8: Optional - Visualize Results
    # ============================================================
    print("[PROMPT] Would you like to visualize the results? (y/n)")
    visualize = input("  > ").strip().lower()
    
    if visualize == 'y':
        print("\n[STEP 8] Visualizing results...")
        try:
            from scipy.io import loadmat
            import matplotlib.pyplot as plt
            
            print("[DEBUG] Loading MAT file...")
            data = loadmat(str(mat_file))
            
            print("[DEBUG] MAT file keys:")
            for key in data.keys():
                if not key.startswith('__'):
                    print(f"  - {key}")
            
            # OpenModelica uses data_1 (time) and data_2 (variables)
            if 'data_1' in data and 'data_2' in data:
                print("[DEBUG] Using OpenModelica MAT format (data_1, data_2)")
                time = data['data_1'].flatten()
                var_data = data['data_2']
                
                print(f"[DEBUG] Time points: {len(time)}")
                print(f"[DEBUG] Variables shape: {var_data.shape}")
                
                # Create subplots for each variable
                if len(var_data.shape) > 1:
                    n_vars = var_data.shape[1]  # Variables are in columns
                else:
                    n_vars = 1
                
                if n_vars > 1:
                    fig, axes = plt.subplots(min(n_vars, 5), 1, figsize=(12, 3*min(n_vars, 5)))
                else:
                    fig, axes = plt.subplots(1, 1, figsize=(12, 4))
                    axes = [axes]
                
                print(f"[DEBUG] Creating {n_vars} subplots (limited to 5 for visibility)...")
                
                # Plot each variable (limit to first 5 for clarity)
                for i in range(min(n_vars, 5)):
                    if len(var_data.shape) > 1:
                        y = var_data[:, i]  # Get column i
                    else:
                        y = var_data.flatten()
                    
                    # Use time if lengths match, otherwise use indices
                    if len(time) == len(y):
                        x_axis = time
                        x_label = 'Time (s)'
                    else:
                        x_axis = np.arange(len(y))
                        x_label = 'Index'
                        print(f"[DEBUG] Note: Time array length ({len(time)}) != Data length ({len(y)}), using indices")
                    
                    axes[i].plot(x_axis, y, 'b-', linewidth=2)
                    axes[i].fill_between(x_axis, y, alpha=0.2)
                    axes[i].set_ylabel(f'Variable {i}', fontsize=11)
                    axes[i].grid(True, alpha=0.3)
                
                axes[-1].set_xlabel(x_label, fontsize=11)
                plt.suptitle(f'Simulation Results: {actual_model_name}', fontsize=14, fontweight='bold')
                plt.tight_layout()
                
                plot_file = workspace / f"{model_file_name}_plot.png"
                plt.savefig(plot_file, dpi=150, bbox_inches='tight')
                print(f"[DEBUG] OK Plot saved: {plot_file}")
                print(f"[DEBUG] Plot size: {plot_file.stat().st_size} bytes")
                print("[STEP 8] OK Visualization complete\n")
                
                plt.show()
            else:
                print("[WARNING] MAT file format not recognized. Expected data_1 and data_2.")
                print("[INFO] You can visualize manually using: python visualize_mat.py")
                
        except Exception as e:
            print(f"[WARNING] Could not visualize: {e}")
            print("[INFO] You can visualize manually using: python visualize_mat.py")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}\n")
    
    print("[INFO] Workflow complete!")
    print(f"[INFO] All files saved in: {workspace}\n")


if __name__ == "__main__":
    try:
        interactive_workflow()
    except KeyboardInterrupt:
        print("\n\n[INFO] Workflow interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
