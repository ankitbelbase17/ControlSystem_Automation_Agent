# Interactive Agentic Workflow - Complete Guide

## Overview

The system now supports **two main ways** to interact with the agentic workflow:

1. **Interactive Console Workflow** - User inputs directly in terminal (✅ NEW)
2. **Pre-built Script Files** - User creates Python file with custom models

## Method 1: Interactive Console Workflow (RECOMMENDED)

### What It Does
- No file creation needed
- All input happens in the console
- Real-time progress tracking with `[DEBUG]`, `[INFO]`, `[STEP]` messages
- Comprehensive logging at every stage
- Optional visualization at the end

### Step-by-Step

#### Step 1: Run the Interactive Script

```powershell
cd C:\Users\acer\OneDrive\Desktop\ConSys\ControlSystem_Automation_Agent
python interactive_workflow.py
```

#### Step 2: Enter Workspace Name

```
[INPUT] Enter workspace name (default: 'InteractiveTest'):
  > MySimulation
```

**Output:**
```
[DEBUG] Workspace name: MySimulation
[INFO] Workspace location: ...workspaces/MySimulation
```

#### Step 3: Describe Your System

```
[INPUT] Describe the system you want to simulate:
  Example: 'A simple pendulum with mass 1 kg, length 1 m, gravity 9.81'
  (Enter multi-line description. Type 'END' on a new line when done)

  > A mass-spring system with:
  > Mass = 1 kg
  > Spring constant = 100 N/m
  > Damping = 0.5 N*s/m
  > Initial displacement = 0.1 m
  > END
```

**Output:**
```
[DEBUG] Received description (87 chars):
  A mass-spring system with...
```

#### Step 4: Watch the Progress

The system automatically:

```
[STEP 1] Generating Modelica model from description...
  [DEBUG] Calling Azure OpenAI to generate model...
  [DEBUG] Generated 285 characters of Modelica code
  [STEP 1] ✓ Model generated successfully

[STEP 2] Saving Modelica model to file...
  [DEBUG] File path: ...MySimulation/SpringMassSystem.mo
  [STEP 2] ✓ Model saved

[STEP 3] Validating model syntax...
  [STEP 3] ✓ Model validation complete

[STEP 4] Generating simulation script...
  [DEBUG] Generated 222 characters of script
  [STEP 4] ✓ Simulation script generated

[STEP 5] Running OpenModelica simulation...
  [DEBUG] Simulation timeout: 300 seconds
  [DEBUG] Simulation success: True
  [DEBUG] MAT file size: 20766 bytes
  [STEP 5] ✓ Simulation completed successfully!
```

#### Step 5: View Results

```
================================================================================
                              SIMULATION RESULTS
================================================================================

[RESULT] Model:
  Name: SpringMassSystem
  File: ...workspaces/MySimulation/SpringMassSystem.mo
  Size: 338 bytes

[RESULT] Simulation:
  Script: ...workspaces/MySimulation/simulate_SpringMassSystem.mos
  Duration: 10 seconds (0-10)
  Intervals: 500

[RESULT] Output:
  MAT File: ...workspaces/MySimulation/SpringMassSystem_res.mat
  File Size: 20766 bytes
```

#### Step 6: Optional - Visualize Results

```
[PROMPT] Would you like to visualize the results? (y/n)
  > y

[STEP 8] Visualizing results...
  [DEBUG] Loading MAT file...
  [DEBUG] Creating plots...
  [STEP 8] ✓ Visualization complete
```

**Generated Plots:**
- `01_all_variables.png` - Grid of all variables
- `02_overlay_plot.png` - Multiple variables on same axes
- `03_statistics.png` - Statistics summary table
- `04_phase_portrait.png` - Phase space visualization

---

## Method 2: Standalone Visualization

If you already have a MAT file from a previous simulation, you can visualize it:

```powershell
python visualize_mat.py "workspaces/MySimulation/SpringMassSystem_res.mat"
```

**Output:**
```
[INFO] Loading MAT file: workspaces/MySimulation/SpringMassSystem_res.mat
[DEBUG] Loaded 6 items from MAT file
[DEBUG] Extracting variables...
[INFO] Total variables to plot: 2

[PLOT 1] Creating grid of all variables...
[PLOT 2] Creating overlay plot...
[PLOT 3] Creating statistics summary...
[PLOT 4] Creating phase portrait...

[INFO] All visualizations saved to: workspaces/MySimulation/visualizations
```

---

## Debug Output Explained

### Debug Levels

| Tag | Meaning | Example |
|-----|---------|---------|
| `[INIT]` | Initialization phase | Component setup |
| `[CHECK]` | Verification phase | OpenModelica check |
| `[INPUT]` | Waiting for user input | Prompt message |
| `[DEBUG]` | Detailed info | File sizes, memory |
| `[INFO]` | General information | Workspace path |
| `[STEP N]` | Major step completion | Step 1 complete |
| `[RESULT]` | Final results | Output files |
| `[WARNING]` | Non-critical issue | Missing validation |
| `[ERROR]` | Critical failure | Aborted operation |

### Reading the Debug Output

**Example trace:**

```
[INIT] Initializing OpenModelicaAgent...
  └─ [DEBUG] Azure endpoint: https://...
  └─ [DEBUG] API version: 2024-08-01-preview
  └─ [✓] Azure OpenAI client initialized
[INIT] ✓ Agent initialized
```

**Interpretation:**
- ✅ Agent started successfully
- ✅ Azure credentials loaded
- ✅ Ready for model generation

---

## File Structure After Execution

```
workspaces/
└── MySimulation/
    ├── SpringMassSystem.mo
    │   └── Generated Modelica model (338 bytes)
    ├── simulate_SpringMassSystem.mos
    │   └── Simulation script (222 bytes)
    ├── SpringMassSystem_res.mat
    │   └── RESULTS FILE - Contains all simulation data
    ├── app.log
    │   └── Detailed execution log
    └── visualizations/
        ├── 01_all_variables.png
        ├── 02_overlay_plot.png
        ├── 03_statistics.png
        └── 04_phase_portrait.png
```

---

## Common Use Cases

### Use Case 1: Simple Pendulum

```
Enter workspace name:
  > Pendulum_Sim

Describe the system:
  > Simple pendulum
  > Length L = 1 m
  > Mass m = 1 kg
  > Gravity g = 9.81 m/s²
  > Initial angle = 0.5 radians
  > Damping coefficient = 0.1
  > Simulate for 10 seconds
  > END
```

**Result:** 
- `SimplePendulum_res.mat` with angle and angular velocity

---

### Use Case 2: RC Circuit

```
Enter workspace name:
  > RC_Circuit

Describe the system:
  > RC circuit model
  > Resistance R = 1000 Ohms
  > Capacitance C = 0.001 Farads
  > Input voltage = 5V step at t=0
  > Output capacitor voltage
  > Simulate for 5 seconds
  > END
```

**Result:**
- `RCCircuit_res.mat` with voltage over time

---

### Use Case 3: Mass-Spring-Damper

```
Enter workspace name:
  > MSD_System

Describe the system:
  > Mass spring damper system
  > Mass m = 2 kg
  > Spring stiffness k = 100 N/m
  > Damping coefficient c = 0.5 N*s/m
  > Applied force F = 10 N constant
  > Initial position x = 0.1 m
  > Simulate for 10 seconds
  > END
```

**Result:**
- `MassSpringDamper_res.mat` with position, velocity, acceleration

---

## Troubleshooting

### Issue: "Azure OpenAI initialization failed"

**Check:**
1. `.env` file exists
2. API key is correct
3. Endpoint URL is correct

**Fix:**
```powershell
# View .env file
Get-Content .env

# Update with correct credentials
notepad .env
```

---

### Issue: "OpenModelica not found"

**Check:**
```powershell
omc --version
```

**Fix:**
- Download from: https://openmodelica.org/download/
- Or: `choco install openmodelica` (if using Chocolatey)

---

### Issue: "Simulation completed but no MAT file found"

**Check simulation debug output for error:**
- Look for `[DEBUG] Simulation success: False`
- Check model syntax errors
- Verify all variables are properly defined

**Solution:**
- Simplify the description
- Use standard differential equations only
- Avoid discrete events (`when`/`then` statements)

---

## Progress Tracking Summary

**What Gets Logged:**

```
WORKFLOW INITIALIZATION
  ✓ Agent setup
  ✓ Executor setup
  ✓ OpenModelica check

USER INPUT
  ✓ Workspace name
  ✓ System description

CODE GENERATION
  ✓ API call made
  ✓ Response received
  ✓ Model generated (N chars)
  ✓ Model name extracted
  ✓ Model file saved (N bytes)

VALIDATION
  ✓ Model syntax check
  ✓ Validation result

SIMULATION
  ✓ Script generated
  ✓ Script saved
  ✓ Simulation executed
  ✓ MAT file location
  ✓ MAT file size

RESULTS
  ✓ All output paths
  ✓ Completion timestamp

OPTIONAL VISUALIZATION
  ✓ Variables extracted
  ✓ Plots generated
  ✓ Visualization paths
```

---

## Next Steps After Getting Results

### 1. View Plots

```powershell
# Open visualization directory
explorer "workspaces\MySimulation\visualizations"
```

### 2. Analyze Data in Python

```python
from scipy.io import loadmat
import matplotlib.pyplot as plt

# Load data
data = loadmat("workspaces/MySimulation/SpringMassSystem_res.mat")

# Access variables
time = data['time'].flatten()
position = data['position'].flatten()
velocity = data['velocity'].flatten()

# Custom plot
plt.figure(figsize=(12, 6))
plt.plot(time, position, label='Position')
plt.plot(time, velocity, label='Velocity')
plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.show()
```

### 3. Export Results

```python
# Create CSV file
import pandas as pd

data = loadmat("workspaces/MySimulation/SpringMassSystem_res.mat")
df = pd.DataFrame({
    'time': data['time'].flatten(),
    'position': data['position'].flatten(),
    'velocity': data['velocity'].flatten()
})

df.to_csv("results.csv", index=False)
```

---

## Command Reference

| Task | Command |
|------|---------|
| Run interactive | `python interactive_workflow.py` |
| Visualize MAT | `python visualize_mat.py <path_to_mat>` |
| List results | `Get-ChildItem "workspaces" -Recurse -Filter "*.mat"` |
| View logs | `Get-Content "workspaces/MySimulation/app.log"` |
| Clean output | `Remove-Item "workspaces" -Recurse` |

---

## Summary

✅ **Interactive Console Workflow enables:**
- Real-time progress tracking
- No file creation needed
- Comprehensive debugging output
- Automatic visualization
- Complete audit trail in logs

✅ **Visualizer provides:**
- Multi-variable plots
- Statistics summaries
- Phase portraits
- Automatic file generation

✅ **Extensive Logging shows:**
- Every step of execution
- File sizes and paths
- API calls and responses
- Simulation parameters
- Final results location
