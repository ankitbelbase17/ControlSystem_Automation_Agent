# Getting Started - Complete Guide

Welcome to the OpenModelica AI Agent system! This guide will help you get up and running quickly.

## What This System Does

The OpenModelica AI Agent automatically:
1. **Generates** Modelica models from natural language descriptions
2. **Simulates** those models using OpenModelica
3. **Visualizes** model structure and simulation results

All through an intelligent AI agent powered by Azure OpenAI (GPT-4o).

## Choose Your Path

### 🚀 Fast Path (5 minutes)
**Goal:** See it working immediately

1. **Prerequisites:**
   - Python 3.8+ installed
   - OpenModelica installed
   - Azure OpenAI API credentials

2. **Setup:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your Azure credentials
   nano .env
   ```

3. **Run:**
   ```bash
   python main.py
   # Select option: 2 (SimplePendulum example)
   # Watch it complete all 6 steps automatically
   ```

4. **View Results:**
   ```
   outputs/
   ├── models/SimplePendulum.mo
   ├── results/SimplePendulum_results.mat
   └── model_plots/block_diagram.png
   ```

### 📚 Learning Path (30 minutes)
**Goal:** Understand the system architecture

1. **Read:** `EXECUTION_WORKFLOW.md`
   - Understand the 6-step pipeline
   - See what each step produces
   - Learn timing expectations

2. **Run:** `python test_runner.py`
   - Validates each component
   - Identifies any setup issues
   - Shows which tests pass/fail

3. **Experiment:**
   - Try built-in examples (Option 2, 3)
   - Create a custom model (Option 1)
   - Review generated files

4. **Read:** `API_REFERENCE.md`
   - Understand available functions
   - Learn how to use each component
   - Copy examples for your code

### 🔬 Developer Path (1-2 hours)
**Goal:** Integrate into your own application

1. **Study:**
   - `API_REFERENCE.md` - Complete API documentation
   - `main.py` - Example implementation
   - `agents/openmodelica_agent.py` - AI integration

2. **Implement:**
   - Use `OpenModelicaAgent` for model generation
   - Use `OMCExecutor` for simulations
   - Use visualizers for plots

3. **Example Code:**
   ```python
   from agents.openmodelica_agent import OpenModelicaAgent
   from executors.omc_executor import OMCExecutor
   
   # Generate
   agent = OpenModelicaAgent()
   mo_code = agent.generate_modelica_model("Your model description")
   
   # Simulate
   executor = OMCExecutor()
   success, output, mat_file = executor.simulate_model_direct(...)
   
   # Use results in your application
   ```

## Key Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| **README.md** | Project overview | 5 min |
| **QUICK_START.md** | This file - step-by-step guides | 5 min |
| **QUICK_REFERENCE.md** | Commands at a glance | 2 min |
| **EXECUTION_WORKFLOW.md** | 6-step pipeline details | 15 min |
| **TESTING_GUIDE.md** | How to test the system | 10 min |
| **API_REFERENCE.md** | Complete API documentation | 20 min |
| **ENV_SETUP.md** | Environment configuration | 10 min |
| **SECURITY_CHECKLIST.md** | Security best practices | 5 min |

## Installation Checklist

- [ ] **Python 3.8+** installed
  ```bash
  python --version
  ```

- [ ] **pip dependencies** installed
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **OpenModelica** installed
  ```bash
  omc --version
  ```

- [ ] **Azure OpenAI** credentials obtained
  - Go to https://portal.azure.com/
  - Create Azure OpenAI resource
  - Deploy GPT-4o model
  - Copy: Endpoint URL, API Key, Deployment Name

- [ ] **.env file** created and configured
  ```bash
  cp .env.example .env
  nano .env  # Add your actual credentials
  ```

- [ ] **Credentials verified**
  ```bash
  python -c "from config.config import Config; print('✓ Config loaded')"
  ```

## Your First Run

### Option 1: Use Built-in Example (Recommended)

```bash
python main.py
```

When prompted, select **Option 2: SimplePendulum**

This will:
- Generate a simple pendulum model
- Simulate for 10 seconds
- Create 6 output files (model, script, results, visualizations)
- Complete in ~30 seconds

**Verify Success:**
- Check `outputs/models/SimplePendulum.mo` exists
- Check `outputs/results/SimplePendulum_results.mat` exists
- Check `outputs/model_plots/block_diagram.png` exists

### Option 2: Run Test Suite

```bash
python test_runner.py
```

This validates:
1. ✓ AI model generation (Azure OpenAI integration)
2. ✓ Model parsing (structure extraction)
3. ✓ Script generation (simulation script creation)
4. ✓ OpenModelica available (installation check)
5. ✓ Full pipeline (end-to-end test)

**Expected result:** `4/5` or `5/5` tests pass
(Test 4 may fail if OpenModelica not installed)

### Option 3: Create Custom Model

```bash
python main.py
```

Select **Option 1: Custom model**

Describe your system in natural language:
```
"Create a mass-spring-damper system with:
- Mass = 1 kg
- Spring constant = 10 N/m
- Damping = 0.5 N·s/m
- Applied force = 1 N step input at t=0"
```

System will:
- Generate complete Modelica code
- Automatically run simulation
- Create all visualizations
- Save to `outputs/` directory

## Troubleshooting First Run

### Problem: "omc not found"
**Solution:** Install OpenModelica
```bash
# Windows: Download from openmodelica.org
# macOS: brew install openmodelica
# Linux: sudo apt-get install openmodelica
```

### Problem: "API key not found"
**Solution:** Check .env file
```bash
# Verify .env exists and has real values (not ${PLACEHOLDER})
cat .env | grep AZURE_OPENAI_API_KEY
# Should show: AZURE_OPENAI_API_KEY=<actual-key>
```

### Problem: "Import error"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Problem: "Simulation failed"
**Solution:** Check logs
```bash
# View error messages
tail -f app.log

# Try a simpler model description
# Check if OpenModelica is working: omc --version
```

## Understanding Output Structure

After a successful run, you'll find:

```
outputs/
├── models/
│   └── SimplePendulum.mo              # Generated Modelica code
├── scripts/
│   └── SimplePendulum.mos             # OpenModelica simulation script
├── results/
│   └── SimplePendulum_results.mat     # Simulation results (MATLAB format)
├── model_plots/
│   ├── block_diagram.png              # Visual model structure
│   └── dependency_graph.png           # Variable dependencies
└── result_plots/
    ├── all_variables.png              # Time series of all variables
    ├── phase_portrait.png             # Position vs velocity
    └── summary_report.png             # Statistics and distributions

workspaces/
└── 2024-01-15_14-30-45/               # Timestamped run directory
    ├── model/
    ├── script/
    ├── results/
    └── plots/
```

## Next Steps After First Run

### 1. Explore Generated Files
```bash
# View generated Modelica code
cat outputs/models/SimplePendulum.mo

# View simulation script
cat outputs/scripts/SimplePendulum.mos

# Open visualizations
open outputs/model_plots/block_diagram.png
open outputs/result_plots/summary_report.png
```

### 2. Try Different Models
```bash
python main.py
# Option 1: Create your own custom model

# Good starting models to try:
# - "Simple RC circuit with R=1k, C=1µF"
# - "Thermal system with two bodies"
# - "Electrical RLC circuit"
```

### 3. Use in Your Code
See `API_REFERENCE.md` for programmatic examples:
```python
from agents.openmodelica_agent import OpenModelicaAgent

agent = OpenModelicaAgent()
model = agent.generate_modelica_model("Your description")
# ... use model in your application
```

### 4. Advanced Features
- Enhance existing models: `agent.enhance_model(current_code, enhancement)`
- Explain model behavior: `agent.explain_model(model_code)`
- Batch simulations: Use `BatchScriptGenerator`
- Custom visualizations: Use `ResultsVisualizer` methods

## Common Patterns

### Pattern 1: Generate → Simulate → Extract Data

```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from parsers.mat_parser import MatParser

# Generate model
agent = OpenModelicaAgent()
model = agent.generate_modelica_model("description")

# Simulate
executor = OMCExecutor()
success, output, mat_file = executor.simulate_model_direct(...)

# Extract data
parser = MatParser(mat_file)
parser.load()
df = parser.to_dataframe(["x", "v"])  # Export to pandas
```

### Pattern 2: Iterative Model Refinement

```python
agent = OpenModelicaAgent()

# Generate initial model
model = agent.generate_modelica_model("base model")

# Improve it
model = agent.enhance_model(model, "add friction")
model = agent.enhance_model(model, "add thermal effects")

# Save final version
Path("final_model.mo").write_text(model)
```

### Pattern 3: Batch Simulations

```python
from generators.script_generator import BatchScriptGenerator

# Generate multiple simulation configs
batch = BatchScriptGenerator()
for param_set in parameter_variations:
    config = create_config(param_set)
    batch.add_script(config)

batch.generate_batch_script("batch.mos")
```

## Performance Tips

| Optimization | Impact | Trade-off |
|-------------|--------|-----------|
| Use simpler descriptions | Faster generation | Less detailed models |
| Reduce `numberOfIntervals` | Faster simulation | Lower resolution results |
| Lower `MAX_TOKENS` | Faster API calls | Shorter responses |
| Use smaller `FIGURE_DPI` | Faster plotting | Lower quality plots |

## Getting Help

1. **Check Documentation:**
   - README.md - Overview
   - TESTING_GUIDE.md - Step-by-step workflow
   - API_REFERENCE.md - Function documentation

2. **Run Diagnostics:**
   ```bash
   python test_runner.py           # Test all components
   python -c "import openai; print('✓')"  # Test imports
   omc --version                   # Test OpenModelica
   ```

3. **Review Logs:**
   ```bash
   tail -f app.log                 # Live log view
   cat app.log | grep ERROR        # Find errors
   ```

4. **Try Simple Models First:**
   - Start with Option 2 (built-in example)
   - Then Option 3 (RC circuit example)
   - Then create custom models

## Summary

You now have:
- ✅ Installed the system
- ✅ Verified prerequisites
- ✅ Configured Azure credentials
- ✅ Run your first model

**Next:** Start with `python main.py` and select Option 2!

---

**Questions?**
- Check `README.md` for overview
- Check `TESTING_GUIDE.md` for detailed workflow
- Check `API_REFERENCE.md` for programmatic use
- Review `app.log` for error details
