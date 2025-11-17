# 🎯 SYSTEM READY - HOW TO RUN YOUR FIRST MODEL

## ⚡ The Absolute Fastest Path (5 Minutes)

### Step 1: Configure (1 minute)
```bash
# Copy the template
cp .env.example .env

# Edit it and add your Azure credentials
nano .env
```

Inside `.env`, make sure these have REAL values (not ${PLACEHOLDERS}):
```
AZURE_OPENAI_API_KEY=your-actual-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-0806
```

### Step 2: Verify OpenModelica (30 seconds)
```bash
omc --version
```

Should show version number. If not, install from [openmodelica.org](https://openmodelica.org/download/)

### Step 3: Run Your First Model (1 minute)
```bash
python main.py
```

When it asks what to do, type: **2**

### Step 4: Wait for Magic (1-2 minutes)
The system will:
1. ✅ Generate a pendulum model (AI)
2. ✅ Simulate it (OpenModelica)
3. ✅ Create visualizations (Matplotlib)
4. ✅ Save everything to `outputs/`

### Step 5: See Results (1 minute)
```bash
# View block diagram
open outputs/model_plots/block_diagram.png

# View simulation results
open outputs/result_plots/summary_report.png

# View generated model
cat outputs/models/SimplePendulum.mo
```

---

## 📝 What Just Happened?

You just completed the full 6-step pipeline:

```
1. 🤖 AI Generated Modelica Model
   User description → Azure OpenAI → Valid Modelica code
   
2. 📊 Parsed Model Structure
   Extract: variables, parameters, equations
   
3. 🔧 Generated Simulation Script
   Create: OpenModelica .mos script
   
4. ▶️ Ran Simulation
   Execute: OpenModelica compiler
   
5. 🎨 Created Model Visualization
   Block diagram, dependency graph
   
6. 📈 Created Result Visualization
   Time series, phase portrait, summary report
```

Total time: **~30 seconds** ⚡

---

## 🎮 What You Can Do Now

### Option A: Try Different Examples
```bash
python main.py
# Select: 3 (RC Circuit example)
```

### Option B: Create Your Own Model
```bash
python main.py
# Select: 1 (Custom model)
# Describe: "Spring-mass-damper with m=1kg, k=10N/m, c=0.5"
```

### Option C: Validate Everything Works
```bash
python test_runner.py
```

Shows 5 tests:
- ✅ AI model generation
- ✅ Model parsing
- ✅ Script generation
- ✅ OpenModelica available
- ✅ Full pipeline

### Option D: Read and Learn
→ See [GETTING_STARTED.md](GETTING_STARTED.md) for comprehensive guide

---

## 📂 What Gets Created

After running a model, you'll have:

```
outputs/
├── models/
│   └── SimplePendulum.mo                 ← Generated Modelica code
├── scripts/
│   └── SimplePendulum.mos                ← Simulation script
├── results/
│   └── SimplePendulum_results.mat        ← Simulation results
├── model_plots/
│   ├── block_diagram.png                 ← Model structure
│   └── dependency_graph.png              ← Dependencies
└── result_plots/
    ├── all_variables.png                 ← All time series
    ├── phase_portrait.png                ← Position vs velocity
    └── summary_report.png                ← Statistics
```

---

## 🔍 Example: What the Generated Model Looks Like

Input: "Simple pendulum with length 1m"

Output `SimplePendulum.mo`:
```modelica
model SimplePendulum
  parameter Real L = 1.0 "Length";
  parameter Real g = 9.81 "Gravity";
  
  Real x "Angle";
  Real v "Angular velocity";
  
equation
  der(x) = v;
  der(v) = -g/L*sin(x);
end SimplePendulum;
```

Then automatically:
- Simulates for 10 seconds
- Generates 500 data points
- Creates visualizations
- Saves everything

All in **one command**! 🚀

---

## 💡 Key Commands You'll Need

| What You Want | Command |
|---------------|---------|
| Run the system | `python main.py` |
| Run tests | `python test_runner.py` |
| Check OpenModelica | `omc --version` |
| View logs | `tail -f app.log` |
| Check config | `cat .env` |

---

## 🆘 If Something Doesn't Work

### "omc command not found"
```bash
# Install OpenModelica
# Windows: Download from openmodelica.org
# Mac: brew install openmodelica
# Linux: sudo apt-get install openmodelica
```

### "API key error"
```bash
# Check .env file
cat .env

# Make sure it has REAL values, not ${PLACEHOLDERS}
# If blank, fill in from Azure portal
```

### "Import error"
```bash
# Install dependencies
pip install -r requirements.txt
```

### "Simulation failed"
```bash
# Check the logs
cat app.log

# Try a simpler description
# Or check OpenModelica is working: omc --version
```

### "Still stuck?"
→ Read [README.md](README.md) **Troubleshooting** section

---

## 📚 Documentation

Here's what's available:

| Document | Use For |
|----------|---------|
| **[START_HERE.md](START_HERE.md)** | This file (navigation) |
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Complete setup guide |
| **[EXECUTION_WORKFLOW.md](EXECUTION_WORKFLOW.md)** | Understand the 6 steps |
| **[API_REFERENCE.md](API_REFERENCE.md)** | Code integration |
| **[README.md](README.md)** | Project overview & troubleshooting |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | How to test |
| **[ENV_SETUP.md](ENV_SETUP.md)** | Configuration |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Commands |

Pick what you need, or start with [GETTING_STARTED.md](GETTING_STARTED.md) 📖

---

## ✅ Pre-Flight Checklist

Before you start, verify:

- [ ] Python 3.8+ installed: `python --version`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] OpenModelica installed: `omc --version`
- [ ] Azure credentials available (from Azure portal)
- [ ] `.env` file created: `cp .env.example .env`
- [ ] `.env` has real values (not ${PLACEHOLDERS})

**All checked?** You're ready!

---

## 🚀 Your Command Right Now

```bash
python main.py
```

Select option **2** to run SimplePendulum example.

Then check `outputs/` for all results.

---

## 📊 What Happens In Each Step

### Step 1: AI Model Generation (3-10 seconds)
```
Your description
    ↓
Azure OpenAI GPT-4o
    ↓
Valid Modelica code (.mo file)
```

### Step 2: Model Parsing (0.1 seconds)
```
.mo file
    ↓
Extract structure (variables, equations, etc.)
    ↓
Model information dict
```

### Step 3: AI Script Generation (2-5 seconds)
```
Model info
    ↓
Azure OpenAI GPT-4o
    ↓
OpenModelica simulation script (.mos file)
```

### Step 4: Simulation Execution (2-30 seconds)
```
.mo file + .mos script
    ↓
OpenModelica compiler (omc)
    ↓
Simulation results (.mat file)
```

### Step 5: Model Visualization (1-2 seconds)
```
Model structure
    ↓
Matplotlib plotting
    ↓
block_diagram.png + dependency_graph.png
```

### Step 6: Results Visualization (2-5 seconds)
```
Simulation results
    ↓
Matplotlib & Seaborn plotting
    ↓
all_variables.png + phase_portrait.png + summary.png
```

---

## 🎯 Three Ways to Use This

### Method 1: Interactive (Easiest)
```bash
python main.py
# Choose option 1, 2, or 3
# System does everything automatically
```

### Method 2: Automated Tests
```bash
python test_runner.py
# Validates all components
# Shows pass/fail for each
```

### Method 3: In Your Code
```python
from agents.openmodelica_agent import OpenModelicaAgent

agent = OpenModelicaAgent()
model = agent.generate_modelica_model("Your description")
# ... use in your application
```

See [API_REFERENCE.md](API_REFERENCE.md) for all available functions

---

## 🎓 What You Get

### In `outputs/` Directory:

✅ **models/** - Generated Modelica code (.mo files)
✅ **scripts/** - Generated simulation scripts (.mos files)  
✅ **results/** - Simulation results (.mat files)
✅ **model_plots/** - Block diagrams and dependency graphs
✅ **result_plots/** - Time series, phase portraits, summary reports

### In `workspaces/` Directory:

✅ Timestamped copies of everything above
✅ Organized in numbered directories (e.g., 2024-01-15_14-30-45/)

---

## 🔐 Security Notes

✅ **API keys are NOT in the code**
✅ **All credentials are in `.env`**
✅ **`.env` is in `.gitignore` (won't be committed)**
✅ **Safe to share code without credentials**
✅ **Team members fill their own `.env` file**

Just follow the setup in [GETTING_STARTED.md](GETTING_STARTED.md)

---

## ⏱️ Time Expectations

| Step | Time |
|------|------|
| AI Model Generation | 3-10s |
| Model Parsing | 0.1s |
| AI Script Generation | 2-5s |
| Simulation | 2-30s |
| Model Visualization | 1-2s |
| Results Visualization | 2-5s |
| **TOTAL** | **10-60s** (usually 30s) |

The LLM API calls (steps 1 & 3) are typically the slowest.

---

## 🎉 You're All Set!

Everything is installed, configured, documented, and tested.

### Right now:

1. **Configure:** `cp .env.example .env` and add your Azure key
2. **Run:** `python main.py`
3. **Choose:** Option 2 (SimplePendulum example)
4. **See:** Results in `outputs/` directory

That's it! 🚀

---

## 📖 Next Steps

After your first successful run:

1. **Learn the system:** Read [EXECUTION_WORKFLOW.md](EXECUTION_WORKFLOW.md)
2. **Try custom models:** Run `python main.py` → Option 1
3. **Integrate in code:** Read [API_REFERENCE.md](API_REFERENCE.md)
4. **Deploy to team:** Follow [ENV_SETUP.md](ENV_SETUP.md)

---

## 🎯 TL;DR (30 Second Version)

```bash
# Setup (1 minute)
cp .env.example .env
nano .env  # Add your Azure API key

# Run (1 command)
python main.py

# Select: 2 (SimplePendulum example)

# Wait: ~30 seconds

# Check: outputs/ directory for all results
```

---

**That's all you need to know to get started!** 🚀

For more info, see [GETTING_STARTED.md](GETTING_STARTED.md) or [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
