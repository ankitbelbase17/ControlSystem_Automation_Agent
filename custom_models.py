import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from config.config import Config


def extract_model_name(modelica_code: str) -> str:
    """Extract the model name from Modelica code"""
    print("[DEBUG] Extracting model name from generated code...")
    match = re.search(r'\bmodel\s+([A-Za-z_]\w*)\b', modelica_code)
    if match:
        name = match.group(1)
        print(f"[DEBUG] Found potential model name: '{name}'")
        if name.lower() not in ['model', 'end', 'equation', 'parameter']:
            print(f"[✓] Extracted model name: {name}")
            return name
        else:
            print(f"[DEBUG] Name '{name}' is a reserved keyword, skipping...")
    print(f"[✗] Could not extract model name, using default: 'Model'")
    return "Model"


# Initialize components
print("[INFO] ========================================")
print("[INFO] INITIALIZING COMPONENTS")
print("[INFO] ========================================")
print("[DEBUG] Creating OpenModelicaAgent...")
agent = OpenModelicaAgent()
print("[DEBUG] Creating OMCExecutor...")
executor = OMCExecutor()

# Ensure output directories exist
print("[DEBUG] Ensuring output directories exist...")
Config.ensure_directories()
print("[✓] Output directories ready")

# Create workspace
print("[DEBUG] Creating workspace for simulation...")
workspace = Config.get_workspace_path("ForceMassAccel_Test")
print(f"[✓] Workspace: {workspace}\n")

print("=" * 70)
print("FORCE-MASS-ACCELERATION SYSTEM SIMULATION")
print("=" * 70)

# ============================================================
# Define the Model Description
# ============================================================
description = """
Create a force-mass-acceleration model:
- Mass m = 2 kg
- Applied force F = 10 N (constant)
- Initial position x = 0 m
- Initial velocity v = 0 m/s
- Friction/damping coefficient c = 0.5 N*s/m
- Output position and velocity over time
- Simulate for 10 seconds
Using Newton's second law: F - c*v = m*a, where a = dv/dt and v = dx/dt
"""

print(f"\nModel Description:\n{description}\n")

# ============================================================
# Step 1: Generate Model from Description
# ============================================================
print("[INFO] ========================================")
print("[INFO] STEP 1: GENERATING MODELICA MODEL")
print("[INFO] ========================================")
print("[DEBUG] Description length: {} chars".format(len(description)))
print("[DEBUG] Calling agent.generate_modelica_model()...")
try:
    mo_code = agent.generate_modelica_model(description)
    print("[DEBUG] Model code length: {} chars".format(len(mo_code)))
    print("[✓] Model generated successfully\n")
except Exception as e:
    print("[✗] Failed to generate model: {}".format(e))
    print("[DEBUG] Exception details: {}".format(repr(e)))
    exit(1)

# Extract the actual model name from the generated code
print("[DEBUG] Generated model code preview:")
print(mo_code[:300])
print("...")
actual_model_name = extract_model_name(mo_code)
print(f"[✓] Model name: {actual_model_name}\n")

# ============================================================
# Step 2: Save Model to File
# ============================================================
print("[INFO] ========================================")
print("[INFO] STEP 2: SAVING MODEL TO FILE")
print("[INFO] ========================================")
model_file_name = "ForceMass"
mo_file = workspace / f"{model_file_name}.mo"

print("[DEBUG] Model filename: {}".format(model_file_name))
print("[DEBUG] Full path: {}".format(mo_file))
print("[DEBUG] Parent directory exists: {}".format(mo_file.parent.exists()))
print("[DEBUG] Writing {} bytes to file...".format(len(mo_code)))

try:
    with open(mo_file, 'w', encoding='utf-8') as f:
        f.write(mo_code)
    
    # Verify file was written
    if mo_file.exists():
        file_size = mo_file.stat().st_size
        print("[✓] Model file created successfully")
        print("[DEBUG] File size: {} bytes".format(file_size))
    else:
        print("[✗] File was written but verification failed")
except Exception as e:
    print("[✗] Failed to save model: {}".format(e))
    print("[DEBUG] Exception details: {}".format(repr(e)))
    exit(1)

print("[✓] Model saved: {}\n".format(mo_file))

# ============================================================
# Step 3: Generate Simulation Script
# ============================================================
print("[INFO] ========================================")
print("[INFO] STEP 3: GENERATING SIMULATION SCRIPT")
print("[INFO] ========================================")
print("[DEBUG] Model name: {}".format(actual_model_name))
print("[DEBUG] Model file path: {}".format(mo_file))
print("[DEBUG] Calling agent.generate_simulation_script()...")

try:
    mos_code = agent.generate_simulation_script(actual_model_name, mo_file)
    print("[DEBUG] Script code length: {} chars".format(len(mos_code)))
    print("[✓] Script generated successfully\n")
except Exception as e:
    print("[✗] Failed to generate script: {}".format(e))
    print("[DEBUG] Exception details: {}".format(repr(e)))
    exit(1)

print("[DEBUG] Generated script preview:")
print(mos_code)
print()

# ============================================================
# Step 4: Save Simulation Script
# ============================================================
print("[INFO] ========================================")
print("[INFO] STEP 4: SAVING SIMULATION SCRIPT")
print("[INFO] ========================================")
mos_file = workspace / f"simulate_{model_file_name}.mos"

print("[DEBUG] Script filename: {}".format(mos_file.name))
print("[DEBUG] Full path: {}".format(mos_file))
print("[DEBUG] Writing {} bytes to file...".format(len(mos_code)))

try:
    with open(mos_file, 'w', encoding='utf-8') as f:
        f.write(mos_code)
    
    # Verify file was written
    if mos_file.exists():
        file_size = mos_file.stat().st_size
        print("[✓] Script file created successfully")
        print("[DEBUG] File size: {} bytes".format(file_size))
    else:
        print("[✗] File was written but verification failed")
except Exception as e:
    print("[✗] Failed to save script: {}".format(e))
    print("[DEBUG] Exception details: {}".format(repr(e)))
    exit(1)

print("[✓] Script saved: {}\n".format(mos_file))

# ============================================================
# Step 5: Run Simulation
# ============================================================
print("[INFO] ========================================")
print("[INFO] STEP 5: RUNNING SIMULATION")
print("[INFO] ========================================")
print("[DEBUG] Calling executor.run_simulation_script()...")
print("[DEBUG] Script file: {}".format(mos_file))
print("[DEBUG] Working directory: {}".format(mos_file.parent))

try:
    success, output, mat_file = executor.run_simulation_script(mos_file)
    
    print("[DEBUG] Execution returned:")
    print("[DEBUG]   Success: {}".format(success))
    print("[DEBUG]   Output length: {} chars".format(len(output) if output else 0))
    print("[DEBUG]   MAT file: {}".format(mat_file))
    
    if success and mat_file:
        print("[✓] Simulation completed successfully!\n")
        file_size = mat_file.stat().st_size
        print("[DEBUG] MAT file verified:")
        print("[DEBUG]   Path: {}".format(mat_file))
        print("[DEBUG]   Size: {} bytes".format(file_size))
        print("[✓] MAT file generated: {}".format(mat_file))
        print("[✓] File size: {} bytes\n".format(file_size))
    else:
        print("[✗] Simulation failed")
        print("[DEBUG] Success flag: {}".format(success))
        print("[DEBUG] Output: {}".format(output[:500] if output else "No output"))
        exit(1)
except Exception as e:
    print("[✗] Exception during simulation: {}".format(e))
    print("[DEBUG] Exception details: {}".format(repr(e)))
    import traceback
    traceback.print_exc()
    exit(1)

# ============================================================
# Step 6: Display Final Results
# ============================================================
print("[INFO] ========================================")
print("[INFO] STEP 6: FINAL RESULTS")
print("[INFO] ========================================")

print("\n[RESULTS SUMMARY]")
print("=" * 70)
print("SIMULATION RESULTS")
print("=" * 70)
print(f"\nModel Details:")
print(f"  [DEBUG] Actual model name: {actual_model_name}")
print(f"  [DEBUG] Model file name: {model_file_name}.mo")
print(f"  [DEBUG] Full path: {mo_file}")
print(f"  [DEBUG] File exists: {mo_file.exists()}")
if mo_file.exists():
    print(f"  [DEBUG] File size: {mo_file.stat().st_size} bytes")

print(f"\nSimulation Details:")
print(f"  [DEBUG] Script file name: simulate_{model_file_name}.mos")
print(f"  [DEBUG] Full path: {mos_file}")
print(f"  [DEBUG] File exists: {mos_file.exists()}")
if mos_file.exists():
    print(f"  [DEBUG] File size: {mos_file.stat().st_size} bytes")

print(f"\nResults File:")
print(f"  [DEBUG] MAT file name: {mat_file.name if mat_file else 'Not generated'}")
print(f"  [DEBUG] Full path: {mat_file}")
print(f"  [DEBUG] File exists: {mat_file.exists() if mat_file else False}")
if mat_file and mat_file.exists():
    print(f"  [DEBUG] File size: {mat_file.stat().st_size} bytes")

print(f"\nWorkspace:")
print(f"  [DEBUG] Location: {workspace}")
print(f"  [DEBUG] Exists: {workspace.exists()}")
if workspace.exists():
    import os
    files = os.listdir(workspace)
    print(f"  [DEBUG] Files in workspace: {files}")

print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print("[✓] SUCCESS! Your MAT file is ready for analysis!")