# Complete Guide: Generate a MAT File with the Agentic Workflow

## Overview

The agentic workflow works like this:

```
Your Description
      ↓
  (Agent uses Azure OpenAI)
      ↓
   Modelica Code
      ↓
  (Save to .mo file)
      ↓
  Simulation Script
      ↓
  (OpenModelica executes)
      ↓
   MAT File (Results)
```

---

## Quick Start (3 Steps)

### Step 1: Verify Setup

```bash
# Check OpenModelica
omc --version

# Check Python
python -c "from config.config import Config; print('Config OK')"
```

If OpenModelica is missing:
- Download from: https://openmodelica.org/download/
- Or: `brew install openmodelica` (macOS)
- Or: `sudo apt-get install openmodelica` (Linux)

### Step 2: Update `.env` File

Edit `C:\Users\acer\OneDrive\Desktop\ConSys\ControlSystem_Automation_Agent\.env`:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-api-key-here
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=GPT-4o-0806
```

Replace with your actual Azure OpenAI credentials.

### Step 3: Run the Test

```bash
cd C:\Users\acer\OneDrive\Desktop\ConSys\ControlSystem_Automation_Agent
python test_agentic_workflow.py
```

**That's it!** The script will generate a MAT file automatically.

---

## What the Test Script Does

The `test_agentic_workflow.py` script:

1. **Initializes components**
   - Creates OpenModelicaAgent (AI for code generation)
   - Creates OMCExecutor (runs OpenModelica)
   - Checks if OpenModelica is installed

2. **Generates a Model**
   - Sends description to Azure OpenAI
   - Receives Modelica code
   - Saves to `SimplePendulum.mo`

3. **Generates a Script**
   - Creates OpenModelica simulation script
   - Configures time range (0-10 seconds)
   - Sets 500 output intervals
   - Saves to `simulate_SimplePendulum.mos`

4. **Runs Simulation**
   - Executes OpenModelica with the script
   - Generates `SimplePendulum_res.mat`
   - Returns success/failure

5. **Tests Direct Simulation**
   - Alternative method without script file
   - Also generates a MAT file

---

## Output Files

After running the test, you'll find:

```
workspaces/
└── SimplePendulum_Test_YYYYMMDD_HHMMSS/
    ├── SimplePendulum.mo
    │   └── The Modelica model code
    ├── simulate_SimplePendulum.mos
    │   └── The OpenModelica script
    ├── SimplePendulum_res.mat
    │   └── THE RESULTS FILE (MAT format)
    └── app.log
        └── Execution log
```

---

## Running Just a Direct Simulation

If you already have a `.mo` file and want to skip the AI generation:

```python
from executors.omc_executor import OMCExecutor
from pathlib import Path

executor = OMCExecutor()

# Run simulation directly
success, output, mat_file = executor.simulate_model_direct(
    model_name="SimplePendulum",
    mo_file=Path("SimplePendulum.mo"),
    start_time=0.0,
    stop_time=10.0,
    num_intervals=500
)

if success:
    print(f"MAT file created: {mat_file}")
else:
    print(f"Error: {output}")
```

---

## Creating Your Own Model Description

Edit the test script or create a new one:

```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from pathlib import Path

# Initialize
agent = OpenModelicaAgent()
executor = OMCExecutor()

# Your custom description
description = """
Create an RC circuit model:
- Resistance R = 1000 Ohms
- Capacitance C = 0.001 Farads  
- Input voltage = 5V step at t=0
- Output the voltage across capacitor
- Simulate for 5 seconds
"""

# Generate model
mo_code = agent.generate_modelica_model(description)
print(f"Generated {len(mo_code)} chars of Modelica code")

# Save to file
mo_file = Path("RC_Circuit.mo")
with open(mo_file, 'w') as f:
    f.write(mo_code)

# Generate script
mos_code = agent.generate_simulation_script("RC_Circuit", "RC_Circuit.mo")

# Save script
mos_file = Path("simulate_RC_Circuit.mos")
with open(mos_file, 'w') as f:
    f.write(mos_code)

# Run simulation
success, output, mat_file = executor.run_simulation_script(mos_file)

if success and mat_file:
    print(f"Success! MAT file: {mat_file}")
else:
    print(f"Failed: {output}")
```

---

## Testing Without Azure OpenAI

If you don't have API credentials, the test script will:

1. Use a fallback pendulum model (pre-built)
2. Use a fallback simulation script
3. Still run the actual simulation
4. Still generate a MAT file

Just run:
```bash
python test_agentic_workflow.py
```

You'll see which tests use API (may fail) and which use fallback (will succeed).

---

## Troubleshooting

### Problem: "OpenModelica not found"

**Solution:**
```bash
# Install OpenModelica
# Windows: Download from openmodelica.org
# macOS:
brew install openmodelica

# Linux:
sudo apt-get install openmodelica

# Verify:
omc --version
```

### Problem: "Azure OpenAI initialization failed"

**Causes:**
1. `.env` file doesn't exist
2. Credentials are wrong
3. API key is invalid

**Solution:**
```bash
# 1. Make sure .env exists
ls .env

# 2. Check it has correct format
cat .env

# 3. If missing, copy from example
cp .env.example .env

# 4. Edit with your credentials
# Open with your editor and add your actual keys
```

### Problem: "Simulation failed / No MAT file generated"

**Possible causes:**
1. Modelica syntax error in generated code
2. OpenModelica compilation failed
3. Simulation timeout

**Solution:**
```python
# Add more debugging:
import logging
logging.basicConfig(level=logging.DEBUG)

# Check the model syntax:
from executors.omc_executor import OMCExecutor
executor = OMCExecutor()
valid, msg = executor.validate_model(Path("SimplePendulum.mo"))
print(msg)

# Increase timeout:
from config.config import Config
Config.SIMULATION_TIMEOUT = 600  # 10 minutes
```

### Problem: "Test script errors"

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+

# Run with full error output
python -u test_agentic_workflow.py
```

---

## Understanding the Workflow

### Phase 1: Code Generation
```python
agent = OpenModelicaAgent()
mo_code = agent.generate_modelica_model(description)
# Calls Azure OpenAI GPT-4o
# Returns Modelica model code
```

### Phase 2: Model Storage
```python
# Save model to disk
with open("model.mo", "w") as f:
    f.write(mo_code)
```

### Phase 3: Simulation Setup
```python
mos_code = agent.generate_simulation_script("ModelName", "model.mo")
# Calls Azure OpenAI to generate simulation config
# Returns .mos script
```

### Phase 4: Execution
```python
executor = OMCExecutor()
success, output, mat_file = executor.run_simulation_script(mos_file)
# Runs OpenModelica compiler and simulator
# Generates MAT file with results
```

### Phase 5: Results
```
✓ mat_file = Path to SimplePendulum_res.mat
  Contains: time, all variables, solver info
```

---

## What Gets Generated

### 1. Modelica Model File (.mo)
Contains the physical system definition:
- Variables and parameters
- Equations
- Initial conditions

Example:
```modelica
model SimplePendulum
  parameter Real L = 1.0;
  Real theta(start=0.5);
  Real omega(start=0);
equation
  m*L^2*der(omega) = -m*g*L*sin(theta) - c*omega;
  der(theta) = omega;
end SimplePendulum;
```

### 2. Simulation Script (.mos)
Contains OpenModelica commands:
- Load model
- Configure simulation
- Run simulator
- Save results

Example:
```
loadFile("SimplePendulum.mo");
simulate(SimplePendulum, startTime=0, stopTime=10, numberOfIntervals=500);
```

### 3. Results File (.mat)
Binary file containing:
- Time vector
- All variables over time
- Metadata

Can be read with:
```python
from scipy.io import loadmat
data = loadmat("SimplePendulum_res.mat")
# data['time'], data['theta'], data['omega'], etc.
```

---

## Next: Visualize Results

Once you have a MAT file:

```python
from scipy.io import loadmat
import matplotlib.pyplot as plt

# Load data
data = loadmat("SimplePendulum_res.mat")

# Plot
plt.figure(figsize=(12, 8))

# Angle vs time
plt.subplot(2, 1, 1)
plt.plot(data['time'], data['theta'])
plt.xlabel('Time (s)')
plt.ylabel('Angle (rad)')
plt.title('Pendulum Angle')
plt.grid(True)

# Angular velocity vs time
plt.subplot(2, 1, 2)
plt.plot(data['time'], data['omega'])
plt.xlabel('Time (s)')
plt.ylabel('Angular Velocity (rad/s)')
plt.title('Pendulum Angular Velocity')
plt.grid(True)

plt.tight_layout()
plt.show()
```

---

## Summary

| What | Command/Code |
|------|-------------|
| **Run full test** | `python test_agentic_workflow.py` |
| **Generate model** | `agent.generate_modelica_model(description)` |
| **Run simulation** | `executor.run_simulation_script(mos_file)` |
| **Direct simulation** | `executor.simulate_model_direct(name, mo_file)` |
| **Read MAT file** | `from scipy.io import loadmat` |
| **Visualize** | `import matplotlib.pyplot as plt` |

---

## Additional Resources

- **Detailed guide:** `HOW_TO_TEST.md`
- **Setup guide:** `ENV_SETUP.md`
- **Quick reference:** `QUICK_REFERENCE.md`
- **API docs:** See docstrings in `.py` files
- **Examples:** In `test_agentic_workflow.py`

**Ready to generate your first MAT file? Run:**
```bash
python test_agentic_workflow.py
```
