# How to Test the Agentic Workflow

This guide will help you run the complete agentic workflow to generate Modelica models and create MAT files.

## Quick Start (5 minutes)

### Step 1: Verify Prerequisites

```bash
# Check if OpenModelica is installed
omc --version

# Check Python
python --version

# Check dependencies
pip list | grep openai
```

If OpenModelica is not installed:
- Windows: Download from https://openmodelica.org/download/
- macOS: `brew install openmodelica`
- Linux: `sudo apt-get install openmodelica`

### Step 2: Set Up Credentials

Edit your `.env` file with actual Azure OpenAI credentials:

```bash
nano .env
```

Update these values:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-api-key
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=GPT-4o-0806
```

### Step 3: Run the Test

```bash
python test_agentic_workflow.py
```

Expected output:
```
[TEST 1] Full Agentic Workflow
  ✓ OpenModelicaAgent initialized
  ✓ OMCExecutor initialized
  ✓ OpenModelica is available
  ✓ Model generated successfully
  ✓ Model saved to: .../SimplePendulum.mo
  ✓ Simulation completed successfully!
  ✓ MAT file generated: .../SimplePendulum_res.mat
```

---

## Detailed Workflow Explanation

### Architecture

```
1. INPUT (Description)
   ↓
2. AGENT (OpenModelicaAgent)
   - Calls Azure OpenAI
   - Generates Modelica code
   ↓
3. MODEL FILE (.mo)
   - Saved to workspace
   ↓
4. SIMULATION SCRIPT (ScriptGenerator)
   - Creates .mos simulation script
   ↓
5. EXECUTION (OMCExecutor)
   - Runs OpenModelica compiler
   - Executes simulation
   ↓
6. OUTPUT (MAT File)
   - Results file
```

### What Happens in Each Step

**Step 1: Initialize Components**
- Creates OpenModelicaAgent (uses Azure OpenAI)
- Creates OMCExecutor (runs OpenModelica CLI)
- Verifies OpenModelica installation

**Step 2: Generate Model**
- Sends description to Azure OpenAI (GPT-4o)
- Receives Modelica model code
- Saves to `.mo` file

**Step 3: Validate Model**
- Checks model syntax
- Verifies it can be loaded

**Step 4: Generate Script**
- Creates simulation configuration
- Generates `.mos` script file
- Specifies time range, intervals, solver options

**Step 5: Run Simulation**
- Executes OpenModelica with .mos script
- Generates results in `.mat` file
- Returns success/failure status

---

## Different Test Scenarios

### Scenario 1: Full Agentic (Recommended)

Uses Azure OpenAI to generate everything:

```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor

agent = OpenModelicaAgent()
executor = OMCExecutor()

# Generate model
description = "Create a simple pendulum..."
mo_code = agent.generate_modelica_model(description)

# Generate script
mos_code = agent.generate_simulation_script("PendulumModel", "pendulum.mo")

# Execute
success, output, mat_file = executor.run_simulation_script(mos_file)
```

**Pros:** Fully automated, AI-powered
**Cons:** Requires Azure OpenAI API key and credits
**Time:** 30-60 seconds

### Scenario 2: Manual Model + Script + Execute

Define model manually, generate script with AI:

```python
from generators.model_generator import ModelGenerator
from generators.script_generator import ScriptGenerator
from executors.omc_executor import OMCExecutor

# Define model manually
gen = ModelGenerator()
gen.set_model_info("MyModel")
gen.add_parameter("m", "Real", "1.0")
gen.add_variable("x", "Real")
gen.add_equation("der(x) = 1")

mo_code = gen.generate_model_code()

# Generate script with agent
agent = OpenModelicaAgent()
mos_code = agent.generate_simulation_script("MyModel", "MyModel.mo")

# Execute
executor = OMCExecutor()
success, output, mat = executor.simulate_model_direct("MyModel", mo_file)
```

**Pros:** Mix of automation and control
**Cons:** Still needs API key for script generation
**Time:** 20-40 seconds

### Scenario 3: Pure Code (No AI)

Everything hardcoded, useful for testing without API:

```python
from generators.model_generator import ModelGenerator
from generators.script_generator import ScriptGenerator
from executors.omc_executor import OMCExecutor

# Define model programmatically
model_gen = ModelGenerator()
model_gen.set_model_info("SimplePendulum")
model_gen.add_parameter("L", "Real", "1.0", "m")
model_gen.add_variable("theta", "Real")
model_gen.add_equation("der(theta) = omega")

# Define simulation programmatically
script_gen = ScriptGenerator()
script_gen.set_model("SimplePendulum.mo", "SimplePendulum")
script_gen.set_simulation_time(0, 10)
script_gen.set_solver_options(500, 1e-6, "dassl")

# Execute
executor = OMCExecutor()
success, output, mat = executor.simulate_model_direct(
    "SimplePendulum",
    Path("SimplePendulum.mo")
)
```

**Pros:** No API needed, full control
**Cons:** More code to write
**Time:** 10-20 seconds

### Scenario 4: Direct Simulation

Simplest approach - just run a model:

```python
from executors.omc_executor import OMCExecutor
from pathlib import Path

executor = OMCExecutor()

# If you have a .mo file already:
success, output, mat_file = executor.simulate_model_direct(
    model_name="SimplePendulum",
    mo_file=Path("SimplePendulum.mo"),
    start_time=0.0,
    stop_time=10.0,
    num_intervals=500
)

if success and mat_file:
    print(f"Success! MAT file: {mat_file}")
else:
    print(f"Failed: {output}")
```

**Pros:** Simplest, no AI needed
**Cons:** Need existing .mo file
**Time:** 5-15 seconds

---

## Testing Without Azure OpenAI

If you don't have Azure OpenAI credentials, you can still test:

```bash
# Just run direct simulation test
python test_agentic_workflow.py
```

The script will:
1. Use fallback model if API fails
2. Use fallback script if API fails
3. Still execute the simulation
4. Generate a MAT file

**Output:** You'll see which tests pass/fail

---

## Troubleshooting

### Issue: "OpenModelica not found"

**Solution:**
```bash
# Windows: Download installer
# macOS:
brew install openmodelica

# Linux:
sudo apt-get install openmodelica

# Verify:
omc --version
```

### Issue: "Azure OpenAI client initialization failed"

**Causes:**
1. `.env` file not found
2. Environment variables not set correctly
3. Invalid credentials

**Solution:**
```bash
# Check .env exists
ls -la .env

# Check content
cat .env

# If missing, create it:
cp .env.example .env
# Edit with your real credentials
nano .env
```

### Issue: "Simulation failed"

**Common reasons:**
1. Invalid Modelica syntax in generated code
2. Missing variables in equation
3. Simulation timeout
4. File permissions

**Solution:**
```bash
# Check the .mo file syntax
omc -c "checkModel(SimplePendulum)"

# Check the error message in test output
# Look in workspace for .log files
cat workspaces/*/app.log

# Increase timeout if needed:
Config.SIMULATION_TIMEOUT = 600  # seconds
```

### Issue: "ModuleNotFoundError: openai"

**Solution:**
```bash
pip install openai>=1.0.0
pip install -r requirements.txt
```

---

## Files Generated

After running a test, you'll find:

```
workspaces/
├── SimplePendulum_Test_TIMESTAMP/
│   ├── SimplePendulum.mo          # Generated model
│   ├── simulate_SimplePendulum.mos # Simulation script
│   ├── SimplePendulum_res.mat      # Results (MAT file)
│   └── app.log                     # Execution log
```

### MAT File Contents

The `.mat` file contains:
- All model variables over time
- Simulation metadata
- Timestamps

**Open with:**
- MATLAB: `load('SimplePendulum_res.mat')`
- Python: `scipy.io.loadmat('SimplePendulum_res.mat')`
- OpenModelica: `OMEdit` (GUI)

---

## Next Steps

### 1. Test with Your Own Description

```python
# In test_agentic_workflow.py, modify the description:
description = """
Create YOUR model description here
"""

# Run:
python test_agentic_workflow.py
```

### 2. Visualize Results

```python
from parsers.mat_parser import MatParser
import matplotlib.pyplot as plt

# Load MAT file
parser = MatParser(Path("SimplePendulum_res.mat"))
data = parser.parse()

# Plot
plt.plot(data['time'], data['theta'])
plt.xlabel('Time (s)')
plt.ylabel('Angle (rad)')
plt.show()
```

### 3. Use in Your Application

```python
from agents.openmodelica_agent import OpenModelicaAgent

agent = OpenModelicaAgent()

# Generate a model
model = agent.generate_modelica_model(your_description)

# Process it
enhanced = agent.enhance_model(model, enhancement_request)

# Explain it
explanation = agent.explain_model(model)
```

---

## Performance Tips

### Speed Up Testing
- Use Scenario 3 or 4 (no API calls)
- Reduce simulation time (stopTime < 10)
- Reduce intervals (numberOfIntervals < 500)

### Improve Reliability
- Validate model before simulation
- Check OpenModelica version
- Monitor API quotas

### Debug Issues
- Enable debug logging:
  ```python
  import logging
  logging.basicConfig(level=logging.DEBUG)
  ```
- Check workspace log files
- Read OpenModelica output carefully

---

## Summary

| Task | Command | Time |
|------|---------|------|
| Quick test | `python test_agentic_workflow.py` | 1-2 min |
| Full workflow | See Scenario 1 | 30-60 sec |
| No API test | See Scenario 3 | 10-20 sec |
| Direct simulation | See Scenario 4 | 5-15 sec |

**Questions?** Check `ENV_SETUP.md`, `SECURITY_CHECKLIST.md`, or `QUICK_REFERENCE.md`
