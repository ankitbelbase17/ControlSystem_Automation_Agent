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

### Interactive Mode

```bash
python main.py
```

This launches an interactive menu with options:
1. Generate custom model from description
2. Run example: Simple Pendulum
3. Run example: RC Circuit
4. Exit

### Programmatic Usage

```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor

# Initialize agent
agent = OpenModelicaAgent()

# Generate model
description = "Create a spring-mass-damper system with m=1kg, k=10N/m, c=0.5Ns/m"
mo_content = agent.generate_modelica_model(description)

# Execute simulation
executor = OMCExecutor()
success, output, mat_file = executor.simulate_model_direct(
    "SpringMassDamper", 
    Path("SpringMassDamper.mo")
)
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