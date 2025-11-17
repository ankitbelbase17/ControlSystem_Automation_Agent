# OpenModelica AI Agent - Agentic Workflow

An intelligent agent that generates Modelica models from natural language descriptions, simulates them with OpenModelica, and visualizes results using Azure OpenAI (GPT-4o).

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Verify OpenModelica
omc --version
```

### 2. Interactive Workflow

```bash
# Run interactive console mode
python interactive_workflow.py

# Or run test to verify everything works
python test_agentic_workflow.py
```

### 3. Visualize Results

```bash
# Visualize any MAT file
python visualize_mat.py "workspaces/InteractiveTest/SimpleMassForce_res.mat"
```

## Features

- 🤖 **AI-Powered Model Generation**: Describe system → AI generates Modelica code
- 📊 **Automatic Visualization**: Multi-plot analysis (time-series, phase portraits, statistics)
- 🔄 **Complete Pipeline**: Description → Model → Simulation → MAT file → Plots
- 📁 **Organized Workspaces**: Each run creates timestamped directory
- 🐛 **Extensive Debugging**: [STEP], [DEBUG], [INFO] tagged output for tracking

## How It Works

```
User Description
    ↓
Azure OpenAI (GPT-4o)
    ↓
Modelica Model (.mo)
    ↓
Simulation Script (.mos)
    ↓
OpenModelica Execution
    ↓
Results File (.mat)
    ↓
Multi-Plot Visualization
```

## Usage Examples

### Interactive Console (Recommended)

```bash
python interactive_workflow.py

# When prompted:
# 1. Enter workspace name: MySimulation
# 2. Describe system (multi-line, type END):
#    - A spring-mass-damper system
#    - Mass m = 1 kg
#    - Spring constant k = 100 N/m
#    - Damping coefficient c = 0.5 N*s/m
#    - Simulate for 10 seconds
#    END
# 3. Watch progress with [STEP 1-6] messages
# 4. Visualize results when prompted
```

### Programmatic Usage

```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from pathlib import Path

# Create agent and executor
agent = OpenModelicaAgent()
executor = OMCExecutor()

# Generate model
description = "Simple pendulum with m=1kg, L=1m, g=9.81"
mo_code = agent.generate_modelica_model(description)

# Save and simulate
mo_file = Path("pendulum.mo")
mo_file.write_text(mo_code)

mo_name = mo_code.split('\n')[0].split()[-1]  # Extract model name
mos_code = agent.generate_simulation_script(mo_name, mo_file)

mos_file = Path("simulate.mos")
mos_file.write_text(mos_code)

# Run
success, output, mat_file = executor.run_simulation_script(mos_file)
if success:
    print(f"Results: {mat_file}")
```

## Project Structure

```
├── interactive_workflow.py     # Main interactive entry point
├── visualize_mat.py            # Standalone MAT file visualizer
├── test_agentic_workflow.py    # Test suite
├── agents/                     # AI agents
├── executors/                  # OpenModelica execution
├── parsers/                    # File parsers
├── visualizers/                # Visualization
├── config/                     # Configuration
├── utils/                      # Logging, utilities
└── workspaces/                 # Generated output (auto-created)
```

## Output Files

After running simulations:

```
workspaces/
└── <workspace_name>/
    ├── <ModelName>.mo                    # Generated Modelica model
    ├── simulate_<ModelName>.mos          # Simulation script
    ├── <ModelName>_res.mat               # Results (binary)
    ├── app.log                           # Execution log
    └── visualizations/
        ├── 01_all_variables.png          # Time-series grid
        ├── 02_overlay_plot.png           # Multiple variables
        ├── 03_statistics.png             # Stats summary
        └── 04_phase_portrait.png         # Phase space
```

## Debugging Tips

### View Logs

```bash
# Real-time logs
tail -f workspaces/<workspace>/app.log

# Full logs
cat workspaces/<workspace>/app.log
```

### Run Tests

```bash
# Test full pipeline
python test_agentic_workflow.py

# Test individual components
python -c "from agents.openmodelica_agent import OpenModelicaAgent; print('✓ Agent OK')"
python -c "from executors.omc_executor import OMCExecutor; print('✓ Executor OK')"
```

### Check Configuration

```bash
# Verify credentials
python -c "from config.config import Config; print(f'API Key: {bool(Config.AZURE_OPENAI_API_KEY)}')"

# Verify OpenModelica
omc --version
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key not found | Check `.env` file has `AZURE_OPENAI_API_KEY` set |
| OpenModelica not found | Install: `openmodelica.org/download/` |
| Model generation fails | Simplify description, use standard differential equations |
| Visualization fails | Ensure SciPy installed: `pip install scipy seaborn` |
| Simulation timeout | Increase `Config.SIMULATION_TIMEOUT` in config.py |

## Configuration

Edit `.env` file with:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-api-key
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT=GPT-4o-0806
OMC_COMMAND=omc
SIMULATION_TIMEOUT=300
```

## API Reference

### OpenModelicaAgent
- `generate_modelica_model(description)` → Modelica code
- `generate_simulation_script(model_name, mo_file)` → Simulation script
- `enhance_model(model, enhancement)` → Enhanced model
- `explain_model(code)` → Model explanation

### OMCExecutor
- `check_omc_available()` → Boolean
- `validate_model(mo_file)` → (valid, message)
- `run_simulation_script(mos_file)` → (success, output, mat_file)
- `simulate_model_direct(name, mo_file, times, intervals)` → (success, output, mat_file)

## Performance Tips

- **Faster models**: Reduce `MAX_TOKENS` to 2000, lower `MODEL_TEMPERATURE` to 0.5
- **Faster simulation**: Reduce `numberOfIntervals`, use shorter time spans
- **Faster visualization**: Reduce `FIGURE_DPI` to 150, limit plotted variables

## Next Steps

1. Run `python interactive_workflow.py` for first-time usage
2. Try different system descriptions (pendulum, RC circuit, mass-spring-damper)
3. View generated plots in `workspaces/<name>/visualizations/`
4. Export results: use `scipy.io.loadmat()` to read MAT files
5. Integrate with your own code using programmatic API

## License

MIT License