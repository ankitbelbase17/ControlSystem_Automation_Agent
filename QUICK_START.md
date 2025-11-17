# Quick Start Guide - ✅ TESTED & WORKING

## 🎯 Generate Your First MAT File (30 seconds)

```bash
cd C:\Users\acer\OneDrive\Desktop\ConSys\ControlSystem_Automation_Agent
python test_agentic_workflow.py
```

✅ **Result:** 2 MAT files generated successfully in `workspaces/` folder

**What just happened:**
- Model 1: AI generated a pendulum model → simulated → result saved
- Model 2: Direct simulation fallback → also working

---

## 📖 One-Minute Tutorial

**Option A: Run Complete Workflow (Easiest)**
```bash
python test_agentic_workflow.py
```
- Generates a pendulum model from description
- Creates simulation script
- Runs in OpenModelica
- Outputs MAT file (33 KB)

**Option B: Generate Custom Model**
```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from config.config import Config
from pathlib import Path

Config.ensure_directories()
ws = Config.get_workspace_path("MyModel")

# Create
agent = OpenModelicaAgent()
model = agent.generate_modelica_model("RC circuit with R=1kΩ, C=1µF")

# Save
mo_file = ws / "Circuit.mo"
mo_file.parent.mkdir(parents=True, exist_ok=True)
mo_file.write_text(model)

# Simulate
executor = OMCExecutor()
script = agent.generate_simulation_script("Circuit", "Circuit.mo")
mos_file = ws / "run.mos"
mos_file.write_text(script)

success, out, mat = executor.run_simulation_script(mos_file)
print(f"✅ MAT file: {mat}")
```

**Option C: Analyze Results**
```python
from scipy.io import loadmat
import matplotlib.pyplot as plt

data = loadmat("SimplePendulum_res.mat")
plt.plot(data['time'], data['theta'])
plt.show()
```

## Key Commands at a Glance

| Task | Command |
|------|---------|
| **Generate MAT file** | `python test_agentic_workflow.py` |
| **Check OpenModelica** | `omc --version` |
| **View results** | `workspaces/*/  *_res.mat` |
| **Read MAT** | `from scipy.io import loadmat` |
| **Setup .env** | `cp .env.example .env` (then edit) |
| **Test config** | `python -c "from config.config import Config; print(Config.to_dict())"` |

## Expected Output Locations


After running a model, find outputs here:

```
📁 outputs/
  📁 models/              ← Generated .mo files
  📁 scripts/             ← Generated .mos simulation scripts
  📁 results/             ← Simulation result .mat files
  📁 model_plots/         ← Block diagrams and graphs
  📁 result_plots/        ← Time series and summary plots

📁 workspaces/
  📁 [timestamp]/         ← Complete timestamped run
    📁 model/
    📁 script/
    📁 results/
    📁 plots/
```

## Most Common Workflows

### Workflow 1: Test Everything (5 minutes)
```bash
# Check if system is set up correctly
python test_runner.py

# Then try a built-in example
python main.py    # Select option 2
```

### Workflow 2: Generate Your First Model (10 minutes)
```bash
python main.py    # Select option 1
# Type your model description
# Wait for 6-step pipeline to complete
# Check outputs/ directory for results
```

### Workflow 3: Programmatic Integration (5-30 minutes)
```python
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor

agent = OpenModelicaAgent()
mo_code = agent.generate_modelica_model("your description here")
# Use mo_code in your application...
```

## Pre-Flight Checklist

Before your first run:

- [ ] `.env` file exists and has real credentials (not placeholders)
- [ ] `omc --version` works in terminal
- [ ] `python main.py` runs without import errors
- [ ] `python test_runner.py` completes (some tests can fail if OpenModelica not installed)

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| `omc not found` | Install OpenModelica from openmodelica.org |
| `API key error` | Check `.env` file - it shouldn't have `${VAR}` placeholders |
| `Import error` | Run `pip install -r requirements.txt` |
| `No plots` | Check that simulation succeeded in app.log |
| `API timeout` | Your OpenAI API might be overloaded; try again in 30s |

## Next Steps

1. **Run a test:** `python test_runner.py`
2. **Try an example:** `python main.py` → Select option 2
3. **Create custom model:** `python main.py` → Select option 1
4. **Review full docs:** See `TESTING_GUIDE.md` and `README.md`
5. **Integrate in code:** Copy patterns from `agents/openmodelica_agent.py`

## Getting Help

- **Logs:** Check `app.log` for detailed error messages
- **Tests:** Run `python test_runner.py` to identify failing components
- **Documentation:** Read `TESTING_GUIDE.md` for 6-step workflow details
- **Code:** Review example usage in `main.py` lines 50-150

---

**Pro Tip:** Start with option 2 (SimplePendulum example) to understand the full workflow before attempting custom models.
