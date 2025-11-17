# OpenModelica AI Agent

An intelligent agent that generates, simulates, and visualizes OpenModelica models using Azure OpenAI (GPT-4o).

## Features

- 🤖 **AI-Powered Model Generation**: Generate Modelica models from natural language descriptions
- 📊 **Comprehensive Visualization**: Automatic generation of:
  - Model block diagrams
  - Dependency graphs
  - Time-series plots
  - Phase portraits
  - Summary reports
- 🔄 **Complete Automation**: End-to-end pipeline from description to visualization
- 📁 **Organized Workspaces**: Each model gets its own workspace directory
- 🎨 **Seaborn Visualizations**: Publication-quality plots using Seaborn

## Architecture

```
┌─────────────────┐
│  User Input     │
│  (Description)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Azure OpenAI   │
│  GPT-4o Agent   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  .mo File       │
│  Generation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  .mos Script    │
│  Generation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OpenModelica   │
│  CLI Execution  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  .mat Results   │
│  File           │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Dual Visualization Pipeline    │
├─────────────────┬───────────────┤
│  Model          │  Results      │
│  Structure      │  Analysis     │
│  - Diagrams     │  - Plots      │
│  - Dependencies │  - Statistics │
└─────────────────┴───────────────┘
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **OpenModelica**: Download from [openmodelica.org](https://openmodelica.org/download/)
3. **Azure OpenAI Access**: API credentials

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd openmodelica_agent

# Install Python dependencies
pip install -r requirements.txt

# Verify OpenModelica installation
omc --version
```

## Configuration

### Environment Setup

The project uses environment variables for secure credential management. Follow these steps:

1. **Copy the template file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your Azure OpenAI credentials:**
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-actual-api-key-here
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   AZURE_OPENAI_DEPLOYMENT=GPT-4o-0806
   ```

3. **Never commit `.env`** - it's protected by `.gitignore`

For detailed setup instructions, see [ENV_SETUP.md](ENV_SETUP.md).

### How It Works

Configuration is loaded dynamically from environment variables:
- `config/config.py` reads from `.env` using `python-dotenv`
- All sensitive values are stored locally, never in source code
- Team members use `.env.example` as a template

## Usage

### Quick Start - Interactive Mode

The easiest way to get started:

```bash
# 1. Set up environment
cp .env.example .env
nano .env  # Add your Azure OpenAI credentials

# 2. Run the application
python main.py

# 3. Choose an option:
# - Option 1: Generate custom model from description
# - Option 2: Run built-in Simple Pendulum example
# - Option 3: Run built-in RC Circuit example
# - Option 4: Exit
```

### Run Built-In Examples

Option 2 - Simple Pendulum Model:
```
Creates a simple pendulum with mass, length, gravity
Simulates oscillatory motion
Generates block diagram, dependency graph, and results plots
```

Option 3 - RC Circuit Model:
```
Creates an RC circuit with resistance and capacitance
Simulates charging behavior with step input
Generates model structure and voltage response plots
```

### Create Custom Models

Option 1 - Custom Model:
```
1. Describe your model in natural language
2. Optionally name the model
3. System automatically:
   - Generates Modelica code via AI
   - Parses model structure
   - Creates simulation script
   - Runs OpenModelica simulation
   - Visualizes model and results
```

Example descriptions:
```
- "Spring-mass-damper system with m=1kg, k=10N/m, c=0.5"
- "Thermal system with two bodies and heat transfer"
- "Electrical circuit with inductor and capacitor"
```

### Test the System

Run the automated test suite:

```bash
python test_runner.py
```

This runs 5 tests:
1. AI Model Generation (Azure OpenAI)
2. Model Parsing (Extract structure)
3. Script Generation (Create simulation)
4. OpenModelica Check (Verify installation)
5. Full Pipeline (End-to-end workflow)

### Programmatic Usage

Use the system in your own Python code:

```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from parsers.mat_parser import MatParser
from visualizers.results_visualizer import ResultsVisualizer
from pathlib import Path

# Step 1: Generate model via AI
agent = OpenModelicaAgent()
description = "Spring-mass-damper system with m=1kg, k=10N/m, c=0.5Ns/m"
mo_content = agent.generate_modelica_model(description)

# Step 2: Generate simulation script
mos_content = agent.generate_simulation_script("SpringMassDamper", "SpringMassDamper.mo")

# Step 3: Run simulation
executor = OMCExecutor()
success, output, mat_file = executor.simulate_model_direct(
    "SpringMassDamper",
    Path("SpringMassDamper.mo"),
    start_time=0,
    stop_time=10,
    num_intervals=500
)

# Step 4: Analyze results
if success and mat_file:
    parser = MatParser(mat_file)
    parser.load()
    
    # Get time series data
    time = parser.get_time_series("time")
    position = parser.get_time_series("x")
    
    # Create visualizations
    visualizer = ResultsVisualizer(parser)
    visualizer.plot_specific_variables(["x", "v"], "output.png")
```

### Output Structure

After running models, check these directories:

```
outputs/
├── models/                 # Generated .mo files
│   └── SimplePendulum.mo
├── scripts/                # Generated .mos scripts
│   └── SimplePendulum.mos
├── results/                # Simulation results (.mat files)
│   └── SimplePendulum_results.mat
├── model_plots/            # Model visualizations
│   ├── block_diagram.png
│   └── dependency_graph.png
└── result_plots/           # Simulation result plots
    ├── all_variables.png
    └── summary_report.png

workspaces/
└── [timestamp]/           # Timestamped run directory
    ├── model/
    ├── script/
    ├── results/
    └── plots/
```

## Project Structure

```
openmodelica_agent/
├── config/              # Configuration management
├── agents/              # AI agent implementations
├── executors/           # OpenModelica CLI execution
├── parsers/             # File parsers (.mo, .mat)
├── visualizers/         # Visualization engines
├── utils/               # Utilities (logging, file management)
├── workspaces/          # Working directories (auto-generated)
├── outputs/             # Visualization outputs
│   ├── diagrams/        # Model structure diagrams
│   └── graphs/          # Results plots
├── main.py              # Main entry point
└── requirements.txt     # Python dependencies
```

## Output Files

For each model simulation, the following files are generated:

### Workspace (per model)
- `{ModelName}.mo` - Modelica model file
- `simulate_{ModelName}.mos` - Simulation script
- `{ModelName}_res.mat` - Results file

### Diagrams
- `{workspace}_block_diagram.png` - Model structure visualization
- `{workspace}_dependencies.png` - Variable dependency graph

### Graphs
- `{workspace}_all_variables.png` - Time-series of all variables
- `{workspace}_summary.png` - Comprehensive summary report

## Examples

### Simple Pendulum

```python
description = """
Create a simple pendulum model:
- Mass m = 1 kg
- Length L = 1 meter
- Gravity g = 9.81 m/s²
- Initial angle = 0.5 radians
"""
```

### RC Circuit

```python
description = """
Create an RC circuit:
- Resistance R = 1000 Ohms
- Capacitance C = 0.001 Farads
- Input voltage = 5V step
"""
```

## Visualization Features

### Model Structure Visualization
- **Block Diagrams**: Shows parameters, variables, equations, and components
- **Dependency Graphs**: Network visualization of variable relationships

### Results Visualization
- **Time Series Plots**: Individual and combined variable plots
- **Phase Portraits**: State-space trajectories
- **Distribution Plots**: Statistical distributions
- **Summary Reports**: Comprehensive statistical analysis

## API Reference

### OpenModelicaAgent

```python
agent = OpenModelicaAgent()

# Generate model
mo_code = agent.generate_modelica_model(description: str) -> str

# Generate simulation script
mos_code = agent.generate_simulation_script(model_name: str, mo_file: str) -> str

# Enhance existing model
enhanced = agent.enhance_model(current_model: str, enhancement: str) -> str

# Explain model
explanation = agent.explain_model(model_code: str) -> str
```

### OMCExecutor

```python
executor = OMCExecutor()

# Check OpenModelica availability
is_available = executor.check_omc_available() -> bool

# Validate model
valid, msg = executor.validate_model(mo_file: Path) -> Tuple[bool, str]

# Run simulation
success, output, mat_file = executor.run_simulation_script(mos_file: Path)

# Direct simulation
success, output, mat_file = executor.simulate_model_direct(
    model_name: str,
    mo_file: Path,
    start_time: float = 0.0,
    stop_time: float = 10.0
)
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Azure OpenAI API Key Not Found
**Symptoms:** `OpenAI API key not found` error

**Solutions:**
```bash
# 1. Verify .env file exists
ls -la .env

# 2. Check .env contains actual API credentials (not placeholders)
cat .env | grep AZURE_OPENAI

# 3. Reload environment variables
# In Python: from dotenv import load_dotenv; load_dotenv(override=True)

# 4. Test API connectivity
python -c "from config.config import Config; print(f'Endpoint: {Config.AZURE_OPENAI_ENDPOINT}')"
```

#### Issue: OpenModelica Compiler Not Found
**Symptoms:** `omc command not found` or `OpenModelica not available`

**Solutions:**
```bash
# Verify installation
omc --version

# On Windows: Add OMC to PATH
# Default path: C:\OpenModelica\bin

# On Linux/Mac
sudo apt-get install openmodelica  # Debian/Ubuntu
brew install openmodelica          # macOS

# Verify OMC is in system PATH
which omc
```

#### Issue: Model Generation Produces Invalid Modelica Code
**Symptoms:** Simulation fails with syntax errors

**Troubleshooting steps:**
1. Check generated .mo file: `outputs/models/[ModelName].mo`
2. Review error message in `app.log`
3. Try refining the model description (be more specific)
4. Check that your description includes:
   - Variable names and units
   - Parameter values
   - Physical connections between components
   - Initial conditions

#### Issue: Simulation Timeout
**Symptoms:** `Simulation exceeded timeout` message

**Solutions:**
```bash
# Increase timeout in config.py
Config.OMC_TIMEOUT = 600  # Increase from default 300 seconds

# Reduce simulation time span
# Use smaller start/stop times in model description
```

#### Issue: Visualization Fails (No Plots Generated)
**Symptoms:** Empty plot files or dimension mismatch errors

**Solutions:**
```bash
# Check matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# Force a working backend in code
import matplotlib
matplotlib.use('Agg')  # Before other matplotlib imports

# Verify .mat file exists and contains data
python -c "from scipy.io import loadmat; data = loadmat('outputs/results/[model]_results.mat'); print(list(data.keys()))"
```

#### Issue: Memory Error During Large Simulation
**Symptoms:** `MemoryError` or out of memory

**Solutions:**
- Reduce `numberOfIntervals` in simulation script
- Reduce simulation time span
- Use fewer variables in result storage
- Close other applications to free memory

#### Issue: MATLAB .mat File Cannot Be Parsed
**Symptoms:** `KeyError` or `Unable to parse results file`

**Solutions:**
```bash
# Verify .mat file was created
ls -la outputs/results/

# Check if simulation actually ran
cat workspace/[timestamp]/script/[model].mos

# Try manual simulation to see detailed errors
omc model.mos
```

### Getting Help

1. **Check Logs**
   ```bash
   tail -f app.log  # View live logs
   cat app.log      # View entire log file
   ```

2. **Run Tests to Identify Issues**
   ```bash
   python test_runner.py
   # See which specific components are failing
   ```

3. **Debug with Programmatic Access**
   ```python
   from agents.openmodelica_agent import OpenModelicaAgent
   from config.config import Config
   
   # Check configuration
   print(f"API Key set: {bool(Config.AZURE_OPENAI_API_KEY)}")
   print(f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
   
   # Test model generation
   agent = OpenModelicaAgent()
   result = agent.generate_modelica_model("Simple test model with x equation der(x) = 1")
   print(f"Model generated: {len(result)} characters")
   ```

4. **Verify Each Component**
   ```bash
   # Test imports
   python -c "from agents.openmodelica_agent import OpenModelicaAgent; print('✓ Agents OK')"
   python -c "from executors.omc_executor import OMCExecutor; print('✓ Executors OK')"
   python -c "from visualizers.model_visualizer import ModelVisualizer; print('✓ Visualizers OK')"
   
   # Test OpenModelica
   omc --version
   
   # Test Python packages
   python -c "import openai; import scipy; import matplotlib; print('✓ All packages OK')"
   ```

### Performance Tips

1. **Faster Model Generation**
   - Use simpler descriptions (fewer components)
   - Reduce Config.MAX_TOKENS to 2000-3000
   - Lower Config.MODEL_TEMPERATURE to 0.5 for consistency

2. **Faster Simulations**
   - Reduce numberOfIntervals (default 500)
   - Use shorter simulation time spans
   - Use faster solvers (DASSL instead of Runge-Kutta)

3. **Faster Visualization**
   - Reduce Config.FIGURE_DPI to 150
   - Use smaller Config.FIGURE_SIZE
   - Limit plotted variables with `max_plots` parameter

### OpenModelica Not Found
```bash
# On Ubuntu/Debian
sudo apt-get install openmodelica

# On macOS
brew install openmodelica

# On Windows
# Download installer from openmodelica.org
```

### Simulation Fails
1. Check model syntax in the generated .mo file
2. Review simulation output in workspace directory
3. Check app.log for detailed error messages

### No Plots Generated
1. Ensure matplotlib backend is properly configured
2. Check that .mat file contains valid data
3. Verify variables exist in the model

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Check the logs: `app.log`
- Review OpenModelica documentation
- Open an issue on GitHub

## Acknowledgments

- OpenModelica Foundation
- Azure OpenAI / Microsoft
- Seaborn and Matplotlib communities