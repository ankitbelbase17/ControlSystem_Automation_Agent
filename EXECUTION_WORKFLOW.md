# Execution Workflow Guide

## Complete 6-Step Pipeline

This document shows exactly what happens when you run the OpenModelica AI Agent.

### Step 1: Model Generation (AI-Powered)

**What happens:**
- You provide a description: *"Simple pendulum with length 1m"*
- System calls Azure OpenAI GPT-4o
- AI generates valid Modelica code

**Example flow:**
```
Input:  "Simple pendulum with length L=1m, mass m=1kg"
                            ↓
                    [Azure OpenAI API]
                    [GPT-4o Processing]
                            ↓
Output: model SimplePendulum
          parameter Real L = 1.0 "Length";
          parameter Real m = 1.0 "Mass";
          Real x, v, a;
        equation
          der(x) = v;
          der(v) = -9.81*sin(x)/L;
        end SimplePendulum;
```

**Generated file:** `outputs/models/SimplePendulum.mo`

### Step 2: Model Parsing & Verification

**What happens:**
- System reads the generated `.mo` file
- Extracts structure: variables, parameters, equations, components
- Verifies model has required elements

**Extracted information:**
```
Model Name:  SimplePendulum
Variables:   [x, v, a]
Parameters:  [L=1.0, m=1.0]
Equations:   [der(x) = v, der(v) = -9.81*sin(x)/L]
Components:  []
```

**Used for:** Creating block diagrams and dependency graphs

### Step 3: Simulation Script Generation (AI-Powered)

**What happens:**
- System creates OpenModelica simulation script (`.mos`)
- Configures simulation time, solver options, output variables
- Uses AI to ensure script is properly formatted

**Generated `.mos` script:**
```modelica
// SimplePendulum simulation script
buildModel(SimplePendulum);
simulate(SimplePendulum, startTime=0, stopTime=10, numberOfIntervals=500);
plot({x, v, a});
savePlot("SimplePendulum_results.mat");
```

**Generated file:** `outputs/scripts/SimplePendulum.mos`

### Step 4: OpenModelica Simulation Execution

**What happens:**
- System launches OpenModelica compiler (`omc`)
- Runs the `.mos` simulation script
- Compiler executes the model simulation
- Produces results in `.mat` (MATLAB) format

**Command executed:**
```bash
omc SimplePendulum.mos
```

**Output:** `.mat` file containing time-series data for all variables

**Generated file:** `outputs/results/SimplePendulum_results.mat`

### Step 5: Model Visualization

**What happens:**
- System extracts model structure
- Creates visual representation of model components
- Generates dependency graph showing connections

**Two visualizations:**

1. **Block Diagram**
   ```
   ┌─────────────────┐
   │ SimplePendulum  │
   ├─────────────────┤
   │ Variables: x,v  │
   │ Params: L,m     │
   └─────────────────┘
   ```

2. **Dependency Graph**
   ```
   [x] ──→ [der(x)]
    ↑        ↓
    └────v───┘
   ```

**Generated files:**
- `outputs/model_plots/block_diagram.png`
- `outputs/model_plots/dependency_graph.png`

### Step 6: Results Visualization

**What happens:**
- System loads `.mat` simulation results
- Parses time-series data for each variable
- Creates publication-quality plots

**Generated visualizations:**

1. **All Variables Time Series**
   - Grid of plots showing all variables over time
   - X-axis: Time (seconds)
   - Y-axis: Variable values

2. **Phase Portrait**
   - Position (x) vs Velocity (v)
   - Shows oscillatory behavior
   - Marked start and end points

3. **Summary Report**
   - Multi-panel visualization
   - Statistics: min, max, mean, std
   - Distribution histograms

**Generated files:**
- `outputs/result_plots/all_variables.png`
- `outputs/result_plots/phase_portrait.png`
- `outputs/result_plots/summary_report.png`

---

## Running Each Step Manually

### Option A: Interactive Mode (Fully Automated)

```bash
python main.py
```

Choose option and system runs all 6 steps automatically.

**Output:**
```
Step 1/6: Generating Modelica model... ✓
Step 2/6: Parsing model structure... ✓
Step 3/6: Generating simulation script... ✓
Step 4/6: Running simulation... ✓
Step 5/6: Visualizing model... ✓
Step 6/6: Visualizing results... ✓
Workflow completed successfully!
```

### Option B: Programmatic Control (Step-by-Step)

```python
from pathlib import Path
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from parsers.model_parser import ModelParser
from parsers.mat_parser import MatParser
from visualizers.model_visualizer import ModelVisualizer
from visualizers.results_visualizer import ResultsVisualizer

# Step 1: Generate Model
agent = OpenModelicaAgent()
description = "Simple pendulum with length 1m, mass 1kg"
mo_code = agent.generate_modelica_model(description)
print("✓ Model generated")

# Save model
mo_file = Path("SimplePendulum.mo")
mo_file.write_text(mo_code)

# Step 2: Parse Model
parser = ModelParser(mo_file)
structure = parser.parse()
print(f"✓ Model parsed: {structure['model_name']}")

# Step 3: Generate Script
mos_code = agent.generate_simulation_script("SimplePendulum", str(mo_file))
mos_file = Path("SimplePendulum.mos")
mos_file.write_text(mos_code)
print("✓ Script generated")

# Step 4: Run Simulation
executor = OMCExecutor()
success, output, mat_file = executor.simulate_model_direct(
    "SimplePendulum",
    mo_file,
    start_time=0,
    stop_time=10,
    num_intervals=500
)
print(f"✓ Simulation complete: {mat_file}")

# Step 5: Visualize Model
if success:
    model_viz = ModelVisualizer(parser)
    model_viz.create_block_diagram("block_diagram.png")
    model_viz.create_dependency_graph("dependency.png")
    print("✓ Model visualization complete")

# Step 6: Visualize Results
if mat_file:
    mat_parser = MatParser(mat_file)
    mat_parser.load()
    
    results_viz = ResultsVisualizer(mat_parser)
    results_viz.plot_all_variables("all_variables.png")
    results_viz.create_summary_report("summary.png")
    print("✓ Results visualization complete")

print("\n✅ Full 6-step workflow completed!")
```

---

## Real-World Example: Spring-Mass-Damper

### Step 1: User Description
```
"Create a spring-mass-damper system with mass m=1kg, spring constant k=10N/m, 
damping coefficient c=0.5Ns/m. Apply a step input force of 1N at t=0."
```

### Step 2: AI-Generated Model
```modelica
model SpringMassDamper
  parameter Real m = 1.0 "Mass (kg)";
  parameter Real k = 10.0 "Spring constant (N/m)";
  parameter Real c = 0.5 "Damping coefficient (Ns/m)";
  
  Real x "Position (m)";
  Real v "Velocity (m/s)";
  Real F "Applied force (N)";
  
equation
  F = if time > 0 then 1.0 else 0.0;
  der(x) = v;
  der(v) = (F - c*v - k*x) / m;
end SpringMassDamper;
```

### Step 3: Simulation Parameters
```
Start time: 0 seconds
Stop time: 10 seconds
Intervals: 500 steps
Output variables: [x, v, F]
Solver: DASSL
Tolerance: 1e-6
```

### Step 4: Expected Behavior
```
t=0-1s: System accelerates (F applied)
t=1-5s: Oscillates around equilibrium
t=5-10s: Settles to steady state
Final position: x ≈ 0.1 m (F/k = 1/10)
```

### Step 5-6: Outputs
```
✓ block_diagram.png     - Shows mass-spring-damper structure
✓ dependency_graph.png  - Shows x → v → a connections
✓ all_variables.png     - Time series for x, v, F
✓ phase_portrait.png    - Position vs velocity spiral
✓ summary_report.png    - Statistics and distributions
```

---

## Timing: How Long Does Each Step Take?

| Step | Task | Time | Notes |
|------|------|------|-------|
| 1 | AI Model Generation | 3-10s | Calls Azure OpenAI API |
| 2 | Model Parsing | 0.1s | Fast regex parsing |
| 3 | Script Generation | 2-5s | Calls Azure OpenAI API |
| 4 | Simulation | 2-30s | Depends on time span & intervals |
| 5 | Model Visualization | 1-2s | Matplotlib rendering |
| 6 | Results Visualization | 2-5s | Multiple plots with Seaborn |
| **Total** | **Full Pipeline** | **10-60s** | Typical run: 30s |

**Slowest component:** Step 1 and 3 (LLM API calls)

**Tips to speed up:**
- Use simpler model descriptions (fewer components)
- Reduce `numberOfIntervals` in simulation (Step 4)
- Lower Config.MAX_TOKENS (fewer tokens = faster)

---

## Debugging the Pipeline

### Testing Each Step Independently

```python
# Test Step 1: AI Model Generation
from agents.openmodelica_agent import OpenModelicaAgent
agent = OpenModelicaAgent()
result = agent.generate_modelica_model("Test model with x = sin(time)")
print(f"Generated {len(result)} characters of Modelica code")
assert "model" in result
assert "equation" in result

# Test Step 2: Model Parsing
from parsers.model_parser import ModelParser
from pathlib import Path
Path("test.mo").write_text(result)
parser = ModelParser(Path("test.mo"))
structure = parser.parse()
print(f"Found model: {structure['model_name']}")

# Test Step 3: Script Generation
mos = agent.generate_simulation_script("TestModel", "test.mo")
print(f"Generated {len(mos)} characters of .mos script")
assert "simulate" in mos

# Test Step 4: Execution
from executors.omc_executor import OMCExecutor
executor = OMCExecutor()
available = executor.check_omc_available()
print(f"OpenModelica available: {available}")

# Test Step 5: Visualize Model
if available:
    viz = ModelVisualizer(parser)
    viz.create_block_diagram("test_diagram.png")
    
# Test Step 6: Visualize Results (requires successful simulation)
```

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input                               │
│            (Model Description Text)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Step 1: AI Agent                           │
│        (Azure OpenAI GPT-4o Model Generation)               │
│    Input: Natural language description                      │
│    Output: Valid Modelica code (.mo)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Step 2: Model Parser                                │
│    (Extract Structure & Components)                         │
│    Input: .mo file                                          │
│    Output: Parsed model structure                           │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
   Step 5: Model Viz         Step 3: AI Agent (Script Gen)
   (Diagram & Graphs)        (Generate .mos script)
         │                               │
         │                               ▼
         │                    Step 4: OMC Executor
         │                    (Simulate in OpenModelica)
         │                    Output: .mat results
         │                               │
         │                               ▼
         │                    Step 6: Results Viz
         │                    (Create result plots)
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
                  Output Directory
          (All plots, models, results)
```

---

## Key Files Generated During Workflow

```
After complete run, you'll find:

outputs/
├── models/
│   └── SimplePendulum.mo               ← Step 1 output
├── scripts/
│   └── SimplePendulum.mos              ← Step 3 output
├── results/
│   └── SimplePendulum_results.mat      ← Step 4 output
├── model_plots/
│   ├── block_diagram.png               ← Step 5 output
│   └── dependency_graph.png            ← Step 5 output
└── result_plots/
    ├── all_variables.png               ← Step 6 output
    ├── phase_portrait.png              ← Step 6 output
    └── summary_report.png              ← Step 6 output

Plus workspace directory with timestamped copies of everything
```

---

## Success Criteria

How to know if each step worked:

| Step | Success Indicator | How to Verify |
|------|-------------------|---------------|
| 1 | Model code generated | Check `outputs/models/*.mo` exists |
| 2 | Structure extracted | See "Variables: [...] Parameters: [...]" in log |
| 3 | Script generated | Check `outputs/scripts/*.mos` exists |
| 4 | Simulation ran | Check `outputs/results/*.mat` exists |
| 5 | Diagrams created | Check `outputs/model_plots/` for PNG files |
| 6 | Results plotted | Check `outputs/result_plots/` for PNG files |

All success = "Workflow completed successfully! ✅"

