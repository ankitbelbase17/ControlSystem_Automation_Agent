# How to Run & Test the Agentic Workflow

## Prerequisites

Before running the code, ensure you have:

1. **OpenModelica Installed**
   - Download: https://openmodelica.org/download/
   - Verify installation: Open terminal and run `omc --version`

2. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Add your Azure OpenAI credentials:
     ```bash
     cp .env.example .env
     nano .env  # Edit with your actual credentials
     ```

3. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Azure OpenAI Access**
   - Azure resource with OpenAI deployment
   - API Key and endpoint configured in `.env`

---

## Quick Start - Interactive Mode

### Simple 3-Step Setup

```bash
# 1. Navigate to project directory
cd path/to/ControlSystem_Automation_Agent

# 2. Edit .env with your credentials
nano .env

# 3. Run the application
python main.py
```

### What You'll See

```
================================================================================
OpenModelica AI Agent - Interactive Mode
================================================================================

Options:
1. Generate new model from description
2. Run example: Simple Pendulum
3. Run example: RC Circuit
4. Exit

Select option (1-4): 
```

---

## Step-by-Step Workflow

### Option 1: Run Built-In Examples (Easiest)

```
Select option (1-4): 2

[Output shows:]
================================================================================
[1/6] Generating Modelica model...
✓ Model saved: SimplePendulum.mo
[2/6] Parsing model structure...
✓ Found 3 variables, 2 equations
[3/6] Generating simulation script...
✓ Script saved: simulate_SimplePendulum.mos
[4/6] Running OpenModelica simulation...
✓ Simulation completed: SimplePendulum_res.mat
[5/6] Generating model visualizations...
✓ Block diagram: 20250116_120530_block_diagram.png
✓ Dependency graph: 20250116_120530_dependencies.png
[6/6] Generating results visualizations...
✓ All variables plot: 20250116_120530_all_variables.png
✓ Summary report: 20250116_120530_summary.png
================================================================================
✓ COMPLETE! All outputs generated successfully.
================================================================================

Workspace: workspaces/SimplePendulum_20250116_120530
Diagrams:  outputs/diagrams
Graphs:    outputs/graphs
```

### Option 2: Create Custom Model

```
Select option (1-4): 1

Describe the model you want to create:
> Create a mass-spring-damper system with mass=1kg, spring constant=10N/m, damping=0.5

Enter model name (e.g., MyModel): 
> MassSpringDamper

[Then proceeds with full pipeline as above]
```

---

## Complete Agentic Workflow Breakdown

### 1. **AI Model Generation** (Using Azure OpenAI)
```
Description Input
        ↓
Azure OpenAI API
    ↓     ↓
Generate code → Modelica Model (.mo file)
```

**What happens:**
- Agent sends model description to GPT-4o
- Receives syntactically correct Modelica code
- Saves to workspace

### 2. **Model Parsing**
```
.mo File
   ↓
ModelParser
   ↓
Extract: Variables, Parameters, Equations, Components
```

### 3. **Script Generation**
```
Model name + .mo file
        ↓
Azure OpenAI API
    ↓     ↓
Generate script → Simulation Script (.mos file)
```

### 4. **OpenModelica Execution**
```
.mos Script
    ↓
OpenModelica CLI (omc)
    ↓
Simulation Results (.mat file)
```

### 5. **Model Visualization**
```
Parsed Model
    ↓
ModelVisualizer
    ├─→ Block Diagram (PNG)
    └─→ Dependency Graph (PNG)
```

### 6. **Results Visualization**
```
.mat File
    ↓
MATParser + ResultsVisualizer
    ├─→ Time Series Plots (PNG)
    ├─→ Phase Portraits (PNG)
    └─→ Summary Report (PNG)
```

---

## Testing Different Models

### Test 1: Simple Pendulum
```
Select option: 2

Expected output:
- Model: Simple pendulum equations of motion
- Variables: theta (angle), omega (angular velocity)
- Simulation: Oscillating pendulum behavior
- Plot: Sinusoidal theta and omega curves
```

### Test 2: RC Circuit
```
Select option: 3

Expected output:
- Model: RC circuit charging/discharging
- Variables: Vc (capacitor voltage), Ic (current)
- Simulation: Exponential voltage rise
- Plot: Exponential curve reaching steady state
```

### Test 3: Custom Model
```
Select option: 1

Example descriptions to try:

a) Spring system:
   "Create a vertical spring-mass system with gravity"

b) Thermal system:
   "Create a heat transfer model between two bodies"

c) Electrical system:
   "Create an RLC circuit with AC voltage source"

d) Mechanical system:
   "Create a two-body collision system"
```

---

## Programmatic Usage (For Advanced Users)

### Generate Model Only

```python
from agents.openmodelica_agent import OpenModelicaAgent
from pathlib import Path

# Initialize agent
agent = OpenModelicaAgent()

# Generate model
description = """
Create a simple RC circuit:
- Resistance R = 1000 Ohms
- Capacitance C = 0.001 Farads
- Input voltage = 5V
"""

mo_code = agent.generate_modelica_model(description)
print(mo_code)

# Save it
with open("MyCircuit.mo", "w") as f:
    f.write(mo_code)
```

### Generate and Simulate

```python
from executors.omc_executor import OMCExecutor

executor = OMCExecutor()

# Simulate model
success, output, mat_file = executor.simulate_model_direct(
    "MyCircuit",
    Path("MyCircuit.mo"),
    start_time=0,
    stop_time=5,
    num_intervals=500
)

if success:
    print(f"Simulation successful: {mat_file}")
else:
    print(f"Simulation failed: {output}")
```

### Parse and Visualize

```python
from parsers.model_parser import ModelParser
from visualizers.model_visualizer import ModelVisualizer
from pathlib import Path

# Parse model
parser = ModelParser(Path("MyCircuit.mo"))
parser.parse()

# Visualize
visualizer = ModelVisualizer(parser)
visualizer.create_block_diagram(Path("diagram.png"))
visualizer.create_dependency_graph(Path("dependencies.png"))

print(f"Variables: {len(parser.variables)}")
print(f"Parameters: {len(parser.parameters)}")
print(f"Equations: {len(parser.equations)}")
```

---

## Output Files

After each run, you'll find:

```
outputs/
├── diagrams/
│   ├── {workspace}_block_diagram.png
│   └── {workspace}_dependencies.png
└── graphs/
    ├── {workspace}_all_variables.png
    └── {workspace}_summary.png

workspaces/
└── {ModelName}_{timestamp}/
    ├── {ModelName}.mo
    ├── simulate_{ModelName}.mos
    └── {ModelName}_res.mat
```

---

## Troubleshooting

### Problem: "OpenModelica is not available"

**Solution:**
1. Install OpenModelica from https://openmodelica.org/download/
2. Verify: `omc --version` in terminal
3. Add to PATH if needed

### Problem: "Azure OpenAI API call failed"

**Solution:**
1. Check `.env` file exists in project root
2. Verify API key is correct
3. Check endpoint URL is valid
4. Ensure API version is supported
5. Check network connectivity

### Problem: "Simulation failed"

**Solution:**
1. Check the generated .mo file syntax
2. Run `omc --version` to verify OpenModelica works
3. Check `app.log` for detailed error
4. Try a simpler model first

### Problem: "No visualization generated"

**Solution:**
1. Ensure matplotlib is installed: `pip install matplotlib seaborn`
2. Check permissions on outputs/ directory
3. Verify .mat file was created
4. Check `app.log` for errors

---

## Example Output Screenshots

### Generated Model (SimplePendulum.mo)
```modelica
model SimplePendulum
  "A simple pendulum model"
  
  parameter Real m = 1.0 "Mass in kg";
  parameter Real L = 1.0 "Length in meters";
  parameter Real g = 9.81 "Gravity in m/s²";
  
  Real theta "Angle in radians";
  Real omega "Angular velocity in rad/s";
  
equation
  der(theta) = omega;
  der(omega) = -(g/L) * sin(theta);
  
end SimplePendulum;
```

### Simulation Results
```
Variable Summary:
theta:                  min=    -0.5010  max=     0.5010  mean=    -0.0023
omega:                  min=    -3.1314  max=     3.1297  mean=    -0.0001
time:                   min=     0.0000  max=    10.0000  mean=     5.0000
```

---

## Performance Tips

1. **Start with examples** - Build confidence before custom models
2. **Simple first** - Start with 2-3 parameter systems
3. **Check logs** - Always check `app.log` when something fails
4. **Monitor output** - Watch the step-by-step progress messages
5. **Reuse workspaces** - Check `workspaces/` for previous runs

---

## Next Steps

1. Run the built-in examples (Options 2 & 3)
2. Create your own custom model (Option 1)
3. Explore the generated files in outputs/
4. Read the generated model code
5. Try programmatic API for advanced features

**Happy modeling!** 🚀

For detailed documentation, see:
- `ENV_SETUP.md` - Configuration guide
- `README.md` - Project overview
- `app.log` - Detailed execution logs
