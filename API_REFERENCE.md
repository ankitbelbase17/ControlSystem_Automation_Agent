# API Reference Guide

This document provides detailed API documentation for programmatic use of the OpenModelica AI Agent system.

## Table of Contents

1. [OpenModelica Agent](#openmodelica-agent)
2. [Model Generator](#model-generator)
3. [Script Generator](#script-generator)
4. [OMC Executor](#omc-executor)
5. [Model Parser](#model-parser)
6. [MAT Parser](#mat-parser)
7. [Model Visualizer](#model-visualizer)
8. [Results Visualizer](#results-visualizer)
9. [Configuration](#configuration)

---

## OpenModelica Agent

**Module:** `agents.openmodelica_agent`

**Class:** `OpenModelicaAgent(BaseAgent)`

AI-powered agent for generating Modelica models and scripts using Azure OpenAI.

### Constructor

```python
from agents.openmodelica_agent import OpenModelicaAgent

agent = OpenModelicaAgent()
```

**Parameters:** None (uses config from `config.config.Config`)

**Attributes:**
- `history` (list): Conversation history
- `logger`: Logger instance

### Methods

#### `generate_modelica_model(description, model_name=None)`

Generate a Modelica model from natural language description.

**Parameters:**
- `description` (str): Natural language description of the model
- `model_name` (str, optional): Custom model name. If None, extracted from description.

**Returns:** `str` - Valid Modelica code

**Example:**
```python
agent = OpenModelicaAgent()
mo_code = agent.generate_modelica_model(
    "Create a simple pendulum with length 1m and mass 1kg"
)
print(mo_code)  # Valid Modelica model code
```

**Raises:**
- `ValueError`: If Azure OpenAI API is not configured
- `Exception`: If API call fails

#### `generate_simulation_script(model_name, mo_file_name, start_time=0, stop_time=10, num_intervals=500)`

Generate an OpenModelica simulation script.

**Parameters:**
- `model_name` (str): Name of the model to simulate
- `mo_file_name` (str): Path to the .mo file
- `start_time` (float): Simulation start time (default: 0)
- `stop_time` (float): Simulation end time (default: 10)
- `num_intervals` (int): Number of simulation intervals (default: 500)

**Returns:** `str` - Valid OpenModelica script (.mos)

**Example:**
```python
mos_code = agent.generate_simulation_script(
    model_name="SimplePendulum",
    mo_file_name="SimplePendulum.mo",
    start_time=0,
    stop_time=5,
    num_intervals=1000
)
```

#### `enhance_model(current_model, enhancement_description)`

Iteratively improve an existing model with additional features.

**Parameters:**
- `current_model` (str): Current Modelica model code
- `enhancement_description` (str): Description of desired enhancement

**Returns:** `str` - Enhanced Modelica code

**Example:**
```python
enhanced = agent.enhance_model(
    current_model=mo_code,
    enhancement_description="Add friction and air resistance effects"
)
```

#### `explain_model(model_code)`

Generate documentation explaining a Modelica model.

**Parameters:**
- `model_code` (str): Modelica model code to explain

**Returns:** `str` - Human-readable explanation

**Example:**
```python
explanation = agent.explain_model(mo_code)
print(explanation)  # Description of model behavior
```

#### `process(input_data)`

Generic processing interface (implements BaseAgent contract).

**Parameters:**
- `input_data` (dict): Input data with keys like 'description', 'type'

**Returns:** `dict` - Processing results

---

## Model Generator

**Module:** `generators.model_generator`

**Class:** `ModelGenerator`

Constructs Modelica models programmatically.

### Constructor

```python
from generators.model_generator import ModelGenerator

generator = ModelGenerator(model_name="MyModel")
```

**Parameters:**
- `model_name` (str): Name of the model

### Methods

#### `set_model_info(description="", imports="")`

Set model metadata and imports.

```python
generator.set_model_info(
    description="A mass-spring-damper system",
    imports="import Modelica.Blocks.Sources;"
)
```

#### `add_variable(name, var_type="Real", start_value=0.0, unit="", annotation="")`

Add a variable to the model.

```python
generator.add_variable("x", var_type="Real", start_value=0.0, unit="m")
generator.add_variable("v", var_type="Real", unit="m/s")
```

**Parameters:**
- `name` (str): Variable name
- `var_type` (str): Modelica type (Real, Integer, Boolean)
- `start_value` (float): Initial value
- `unit` (str): Physical unit
- `annotation` (str): Modelica annotation

#### `add_parameter(name, var_type="Real", value=0.0, unit="", annotation="")`

Add a parameter to the model.

```python
generator.add_parameter("m", value=1.0, unit="kg")
generator.add_parameter("k", value=10.0, unit="N/m")
```

#### `add_input(name, var_type="Real")`

Add an input variable.

```python
generator.add_input("F", var_type="Real")  # Input force
```

#### `add_output(name, source_var)`

Add an output variable.

```python
generator.add_output("position", "x")
generator.add_output("velocity", "v")
```

#### `add_equation(equation_text)`

Add an equation to the model.

```python
generator.add_equation("der(x) = v")
generator.add_equation("der(v) = (F - c*v - k*x) / m")
```

**Format:** Use `der()` for derivatives, standard math notation

#### `add_component(component_type, component_name, parameters=None)`

Add a component instance.

```python
generator.add_component(
    "Modelica.Blocks.Sources.Step",
    "step_input",
    parameters={"startTime": 0, "height": 1}
)
```

#### `add_connection(from_comp, from_port, to_comp, to_port)`

Connect two components.

```python
generator.add_connection("step_input", "y", "model", "F")
```

#### `generate_model_code()`

Generate the complete Modelica code.

**Returns:** `str` - Valid Modelica model code

```python
mo_code = generator.generate_model_code()
print(mo_code)
```

#### `save_model(output_path)`

Save model to file.

**Parameters:**
- `output_path` (str or Path): File path for .mo file

```python
generator.save_model("MyModel.mo")
```

#### `to_dict()`

Serialize model to dictionary.

```python
model_dict = generator.to_dict()
```

#### `from_dict(data, model_name="Model")`

Create generator from dictionary (class method).

```python
restored = ModelGenerator.from_dict(model_dict, "RestoredModel")
```

#### `reset()`

Clear all model definitions.

```python
generator.reset()
```

---

## Script Generator

**Module:** `generators.script_generator`

**Class:** `ScriptGenerator`

Creates OpenModelica simulation scripts.

### Constructor

```python
from generators.script_generator import ScriptGenerator

generator = ScriptGenerator()
```

### Methods

#### `set_model(model_path, model_name)`

Set the model to simulate.

```python
generator.set_model("SimplePendulum.mo", "SimplePendulum")
```

**Parameters:**
- `model_path` (str): Path to .mo file
- `model_name` (str): Model class name

#### `set_simulation_time(start_time=0.0, stop_time=10.0)`

Set simulation time range.

```python
generator.set_simulation_time(start_time=0, stop_time=10)
```

#### `set_solver_options(number_of_intervals=500, tolerance=1e-6, method="dassl")`

Configure solver parameters.

```python
generator.set_solver_options(
    number_of_intervals=1000,
    tolerance=1e-8,
    method="runge-kutta"
)
```

**Methods:** "dassl", "runge-kutta", "euler"

#### `add_variable_to_save(variable_name)`

Specify output variables.

```python
generator.add_variable_to_save("x")      # Position
generator.add_variable_to_save("v")      # Velocity
generator.add_variable_to_save("a")      # Acceleration
```

#### `set_output_format(format_type="mat")`

Set result file format.

```python
generator.set_output_format("mat")   # MATLAB format
generator.set_output_format("csv")   # CSV format
```

#### `generate_script()`

Generate the script code.

**Returns:** `str` - OpenModelica script code

```python
mos_code = generator.generate_script()
```

#### `save_script(output_path)`

Save script to file.

```python
generator.save_script("simulation.mos")
```

#### `to_dict()` / `from_dict()`

Serialization methods.

```python
config = generator.to_dict()
restored = ScriptGenerator.from_dict(config)
```

### BatchScriptGenerator

**Class:** `BatchScriptGenerator`

Generate multiple simulation scripts for batch execution.

```python
from generators.script_generator import BatchScriptGenerator

batch = BatchScriptGenerator()
batch.add_script(config_dict_1)
batch.add_script(config_dict_2)
batch.generate_batch_script("batch_simulation.mos")
```

---

## OMC Executor

**Module:** `executors.omc_executor`

**Class:** `OMCExecutor`

Execute OpenModelica commands via CLI.

### Constructor

```python
from executors.omc_executor import OMCExecutor

executor = OMCExecutor()
```

### Methods

#### `check_omc_available()`

Check if OpenModelica is installed and available.

**Returns:** `bool` - True if OMC is available

```python
if executor.check_omc_available():
    print("OpenModelica is ready")
else:
    print("OpenModelica not found - install from openmodelica.org")
```

#### `validate_model(mo_file)`

Check if model has valid Modelica syntax.

**Parameters:**
- `mo_file` (str or Path): Path to .mo file

**Returns:** `bool` - True if valid

```python
is_valid = executor.validate_model("MyModel.mo")
```

#### `run_simulation_script(mos_file, timeout=300)`

Execute a simulation script.

**Parameters:**
- `mos_file` (str or Path): Path to .mos script
- `timeout` (int): Execution timeout in seconds (default: 300)

**Returns:** `tuple` - (success: bool, output: str, mat_file: Path or None)

```python
success, output, mat_file = executor.run_simulation_script("simulation.mos")
if success:
    print(f"Results saved to: {mat_file}")
    print(f"Output:\n{output}")
```

#### `simulate_model_direct(model_name, mo_file, start_time=0, stop_time=10, num_intervals=500)`

Simulate a model without pre-generated script.

**Parameters:**
- `model_name` (str): Model class name
- `mo_file` (str or Path): Path to .mo file
- `start_time` (float): Start time
- `stop_time` (float): Stop time
- `num_intervals` (int): Number of intervals

**Returns:** `tuple` - (success: bool, output: str, mat_file: Path or None)

```python
success, output, mat_file = executor.simulate_model_direct(
    "SpringMass",
    "SpringMass.mo",
    start_time=0,
    stop_time=20,
    num_intervals=2000
)
```

---

## Model Parser

**Module:** `parsers.model_parser`

**Class:** `ModelParser`

Extract structure from Modelica files.

### Constructor

```python
from parsers.model_parser import ModelParser
from pathlib import Path

parser = ModelParser(Path("MyModel.mo"))
```

**Parameters:**
- `model_file` (Path): Path to .mo file

### Methods

#### `parse()`

Parse the model file.

**Returns:** `dict` - Parsed structure

```python
structure = parser.parse()
```

**Returns structure with keys:**
- `model_name` (str)
- `variables` (list of dicts with name, type, unit)
- `parameters` (list of dicts)
- `equations` (list of str)
- `components` (list of dicts)
- `connections` (list of tuples)

#### `get_structure()`

Get parsed structure (calls parse if needed).

```python
info = parser.get_structure()
print(f"Model: {info['model_name']}")
print(f"Variables: {[v['name'] for v in info['variables']]}")
```

#### Example: Extracting Model Information

```python
from parsers.model_parser import ModelParser
from pathlib import Path

# Create and parse model
parser = ModelParser(Path("SimplePendulum.mo"))
structure = parser.parse()

# Access information
model_name = structure['model_name']
variables = {v['name']: v['unit'] for v in structure['variables']}
equations = structure['equations']

print(f"Model: {model_name}")
print(f"Variables: {variables}")
print(f"Equations: {len(equations)}")
```

---

## MAT Parser

**Module:** `parsers.mat_parser`

**Class:** `MatParser`

Load and analyze OpenModelica simulation results.

### Constructor

```python
from parsers.mat_parser import MatParser

parser = MatParser("results.mat")
parser.load()
```

**Parameters:**
- `mat_file` (str or Path): Path to .mat results file

### Methods

#### `load()`

Load the MATLAB file.

```python
parser.load()
```

#### `get_time_series(variable_name)`

Get time-series data for a variable.

**Returns:** `pandas.Series` - Time-indexed data

```python
x_data = parser.get_time_series("x")
print(x_data)  # Pandas Series with time index
```

#### `get_variable_data(variable_name)`

Get raw variable data.

**Returns:** `numpy.ndarray`

```python
x_values = parser.get_variable_data("x")
```

#### `get_summary(variables=None)`

Get statistical summary.

**Parameters:**
- `variables` (list, optional): Specific variables to summarize

**Returns:** `dict` - Statistics

```python
stats = parser.get_summary(["x", "v", "a"])
# Returns: {'x': {'min': ..., 'max': ..., 'mean': ..., 'std': ...}, ...}
```

#### `to_dataframe(variables=None)`

Export to pandas DataFrame.

**Returns:** `pandas.DataFrame`

```python
df = parser.to_dataframe(["x", "v"])
print(df)
df.to_csv("results.csv")
```

#### `filter_plot_variables()`

Get variables suitable for plotting.

**Returns:** `list` - Variable names

```python
plot_vars = parser.filter_plot_variables()
```

### Example: Analyzing Results

```python
from parsers.mat_parser import MatParser

# Load results
parser = MatParser("SimplePendulum_results.mat")
parser.load()

# Get time series
time = parser.get_time_series("time")
position = parser.get_time_series("x")

# Statistics
stats = parser.get_summary(["x", "v"])
print(f"Position range: {stats['x']['min']:.3f} to {stats['x']['max']:.3f}")
print(f"Velocity std dev: {stats['v']['std']:.3f}")

# Export to CSV
df = parser.to_dataframe()
df.to_csv("results.csv")
```

---

## Model Visualizer

**Module:** `visualizers.model_visualizer`

**Class:** `ModelVisualizer`

Create visual diagrams of model structure.

### Constructor

```python
from visualizers.model_visualizer import ModelVisualizer
from parsers.model_parser import ModelParser

parser = ModelParser("MyModel.mo")
parser.parse()
visualizer = ModelVisualizer(parser)
```

**Parameters:**
- `model_parser` (ModelParser): Parsed model

### Methods

#### `create_block_diagram(output_path)`

Generate block diagram visualization.

**Parameters:**
- `output_path` (str or Path): Output file path (PNG)

```python
visualizer.create_block_diagram("diagram.png")
```

**Creates:** PNG image showing model structure

#### `create_dependency_graph(output_path)`

Generate variable dependency graph.

**Parameters:**
- `output_path` (str or Path): Output file path (PNG)

```python
visualizer.create_dependency_graph("dependencies.png")
```

**Creates:** PNG image with NetworkX graph

### Example

```python
from visualizers.model_visualizer import ModelVisualizer
from parsers.model_parser import ModelParser
from pathlib import Path

parser = ModelParser(Path("SpringMass.mo"))
parser.parse()

visualizer = ModelVisualizer(parser)
visualizer.create_block_diagram("block_diagram.png")
visualizer.create_dependency_graph("dependency_graph.png")
```

---

## Results Visualizer

**Module:** `visualizers.results_visualizer`

**Class:** `ResultsVisualizer`

Create publication-quality result visualizations.

### Constructor

```python
from visualizers.results_visualizer import ResultsVisualizer
from parsers.mat_parser import MatParser

parser = MatParser("results.mat")
parser.load()
visualizer = ResultsVisualizer(parser)
```

**Parameters:**
- `mat_parser` (MatParser): Loaded results

### Methods

#### `plot_all_variables(output_path, max_plots=12)`

Create grid of time-series plots.

**Parameters:**
- `output_path` (str or Path): Output PNG file
- `max_plots` (int): Maximum plots to show

```python
visualizer.plot_all_variables("all_variables.png", max_plots=9)
```

#### `plot_specific_variables(variables, output_path, title="")`

Plot selected variables on same axes.

**Parameters:**
- `variables` (list): Variable names to plot
- `output_path` (str or Path): Output PNG file
- `title` (str): Plot title

```python
visualizer.plot_specific_variables(
    ["x", "v"],
    "position_velocity.png",
    title="Pendulum Motion"
)
```

#### `plot_phase_portrait(var_x, var_y, output_path)`

Create phase space plot.

**Parameters:**
- `var_x` (str): X-axis variable
- `var_y` (str): Y-axis variable
- `output_path` (str or Path): Output PNG file

```python
visualizer.plot_phase_portrait("x", "v", "phase_portrait.png")
```

#### `plot_distribution(variables, output_path, bins=30)`

Create histogram with KDE.

**Parameters:**
- `variables` (list): Variables to plot
- `output_path` (str or Path): Output PNG file
- `bins` (int): Histogram bins

```python
visualizer.plot_distribution(["x", "v"], "distributions.png")
```

#### `create_summary_report(output_path)`

Create comprehensive 3x3 grid report.

**Parameters:**
- `output_path` (str or Path): Output PNG file

```python
visualizer.create_summary_report("summary.png")
```

**Shows:** Time series, phase portrait, distributions, statistics

### Example: Complete Visualization Workflow

```python
from visualizers.results_visualizer import ResultsVisualizer
from parsers.mat_parser import MatParser

# Load and visualize results
mat_parser = MatParser("simulation_results.mat")
mat_parser.load()

visualizer = ResultsVisualizer(mat_parser)
visualizer.plot_all_variables("all_plots.png")
visualizer.plot_phase_portrait("x", "v", "phase.png")
visualizer.create_summary_report("summary.png")
```

---

## Configuration

**Module:** `config.config`

**Class:** `Config`

Global configuration settings.

### Key Attributes

**Azure OpenAI:**
```python
Config.AZURE_OPENAI_API_KEY      # API key
Config.AZURE_OPENAI_ENDPOINT      # Endpoint URL
Config.AZURE_OPENAI_DEPLOYMENT    # Deployment name (e.g., "gpt-4o")
```

**Model Parameters:**
```python
Config.MODEL_TEMPERATURE = 0.7    # Creativity (0-1)
Config.MAX_TOKENS = 4000          # Max response length
```

**Simulation:**
```python
Config.OMC_TIMEOUT = 300          # Simulation timeout (seconds)
```

**Visualization:**
```python
Config.FIGURE_SIZE = (12, 8)      # Size in inches
Config.FIGURE_DPI = 300           # Resolution
```

**Paths:**
```python
Config.WORKSPACE_DIR              # Root workspace directory
Config.OUTPUT_DIR                 # Output directory
```

### Using Configuration

```python
from config.config import Config

# Read configuration
api_key = Config.AZURE_OPENAI_API_KEY
timeout = Config.OMC_TIMEOUT

# Modify for specific run (not recommended for production)
original_timeout = Config.OMC_TIMEOUT
Config.OMC_TIMEOUT = 600  # Temporary change
# ... run simulations ...
Config.OMC_TIMEOUT = original_timeout
```

---

## Complete Workflow Example

```python
from pathlib import Path
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from parsers.model_parser import ModelParser
from parsers.mat_parser import MatParser
from visualizers.model_visualizer import ModelVisualizer
from visualizers.results_visualizer import ResultsVisualizer

# Step 1: Generate Model
print("Step 1: Generating model...")
agent = OpenModelicaAgent()
mo_code = agent.generate_modelica_model(
    "Create a spring-mass-damper with m=1kg, k=10N/m, c=0.5"
)
mo_file = Path("SpringMassDamper.mo")
mo_file.write_text(mo_code)

# Step 2: Parse Model
print("Step 2: Parsing model...")
model_parser = ModelParser(mo_file)
model_parser.parse()

# Step 3: Generate Script
print("Step 3: Generating simulation script...")
mos_code = agent.generate_simulation_script("SpringMassDamper", str(mo_file))
mos_file = Path("springmass.mos")
mos_file.write_text(mos_code)

# Step 4: Run Simulation
print("Step 4: Running simulation...")
executor = OMCExecutor()
success, output, mat_file = executor.simulate_model_direct(
    "SpringMassDamper", mo_file, start_time=0, stop_time=20, num_intervals=2000
)

# Step 5: Visualize Model
print("Step 5: Creating model visualization...")
model_viz = ModelVisualizer(model_parser)
model_viz.create_block_diagram("block_diagram.png")
model_viz.create_dependency_graph("dependencies.png")

# Step 6: Visualize Results
print("Step 6: Creating result visualizations...")
if mat_file:
    mat_parser = MatParser(mat_file)
    mat_parser.load()
    
    results_viz = ResultsVisualizer(mat_parser)
    results_viz.plot_all_variables("all_variables.png")
    results_viz.plot_phase_portrait("x", "v", "phase_portrait.png")
    results_viz.create_summary_report("summary_report.png")

print("✅ Complete workflow finished!")
print(f"Model: {mo_file}")
print(f"Results: {mat_file}")
print(f"Visualizations: block_diagram.png, phase_portrait.png, summary_report.png")
```

---

## Error Handling

All components use exceptions for error reporting:

```python
from agents.openmodelica_agent import OpenModelicaAgent

agent = OpenModelicaAgent()
try:
    mo_code = agent.generate_modelica_model("test")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

Check `app.log` for detailed error messages and debugging information.

