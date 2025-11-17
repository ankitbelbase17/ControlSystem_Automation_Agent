# GUI Simulator with Parameter Control

## Overview

The `gui_simulator.py` provides an interactive GUI for Modelica model simulation with real-time parameter adjustment and visualization. It features an OMEdit-style visualization system that matches OpenModelica's native visualization.

## Key Features

### 1. **Model Generation Tab**
- Enter natural language descriptions of your system
- AI generates valid Modelica code automatically
- Automatic parameter extraction from generated models

### 2. **Parameters & Simulation Tab**
- **Interactive Sliders**: Adjust parameters in real-time with slider controls
- **Range Calibration**: Automatic range calculation (0.1x to 10x of current value)
- **Simulation Settings**:
  - Stop Time (0.1 - 100 seconds)
  - Number of Intervals (10 - 5000)
- **Quick Actions**: "Run Simulation" and "Visualize Results" buttons

### 3. **Visualization Tab (OMEdit-Style)**
Three visualization styles to choose from:

#### **OMEdit Style** (Default - Recommended)
- Separate subplots for each variable
- Clean blue lines (#1f77b4) with light background (#f8f8f8)
- Subtle grid lines (dashed, 30% alpha)
- Light fill under curves for better readability
- Matches OpenModelica OMEdit native visualization

#### **Overlay Style**
- All variables on single plot
- Different colors for each variable
- Good for comparing variable relationships
- Legend included

#### **Grid Style**
- 2-column grid layout (up to 6 variables)
- Compact view for many variables
- Individual titles for each plot
- Maximum 6 plots shown

## Usage

### Basic Workflow

```bash
# Launch the GUI
python gui_simulator.py
```

#### Step 1: Generate Model
1. Enter a model description in the "Model Generation" tab
2. Click "Generate Model"
3. System automatically extracts parameters

#### Step 2: Adjust Parameters
1. Navigate to "Parameters & Simulation" tab
2. Use sliders to adjust parameters
3. Set simulation stop time and intervals
4. Click "Run Simulation"

#### Step 3: Visualize
1. Go to "Visualization" tab
2. Select visualization style (OMEdit, Overlay, or Grid)
3. Click "Refresh Plot"
4. Results display with OMEdit-style formatting

### Example Descriptions

**Simple Mass-Force System**:
```
A simple force-mass-acceleration system:
- Mass m = 1.0 kg
- Applied force F = 10.0 N (constant)
- Initial velocity = 0 m/s
- Initial position = 0 m
- Simulate for 10 seconds
```

**Spring-Mass-Damper**:
```
Spring-mass-damper system:
- Mass m = 2.0 kg
- Spring constant k = 100 N/m
- Damping coefficient c = 10 N*s/m
- Initial displacement = 0.1 m
- Initial velocity = 0 m/s
```

**RC Circuit**:
```
RC electrical circuit:
- Resistance R = 1000 Ohms
- Capacitance C = 0.001 Farads
- Input voltage = 5V step
- Initial capacitor voltage = 0V
```

## GUI Components

### Model Generation Tab
```
┌─────────────────────────────────────────┐
│ Model Description:                      │
│ ┌─────────────────────────────────────┐ │
│ │ [Text input area - 8 lines]        │ │
│ └─────────────────────────────────────┘ │
│ [Generate Model] [Status: Ready]        │
└─────────────────────────────────────────┘
```

### Parameters & Simulation Tab
```
┌─────────────────────────────────────────┐
│ Parameter Controls (scrollable):         │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ param_1 = 1.0                      │ │
│ │ ├────●──────────────────────┤ 0.05 │ │
│ │                                     │ │
│ │ param_2 = 10.0                      │ │
│ │ ├──────────────────●────────┤ 8.50 │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Simulation Settings:                    │
│ Stop Time: [10.0] (0.1 - 100)          │
│ Intervals: [500]  (10 - 5000)          │
│                                         │
│ [Run Simulation] [Visualize Results]    │
└─────────────────────────────────────────┘
```

### Visualization Tab
```
┌─────────────────────────────────────────┐
│ Style: [OMEdit▼] [Refresh Plot]        │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │                                    │ │
│  │  Matplotlib Figure Area           │ │
│  │  (Plots rendered here)            │ │
│  │                                    │ │
│  │  OMEdit-style subplots by default │ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## OMEdit-Style Visualization Details

### Visual Characteristics
- **Color Scheme**: Professional blue (#1f77b4) lines
- **Background**: Light gray (#f8f8f8) for readability
- **Grid**: Dashed gray lines with 30% transparency
- **Spines**: Top and right borders removed for cleaner look
- **Line Width**: 1.5pt for clarity
- **Fill**: 10% alpha fill under curves

### Comparison with Other Styles

| Feature | OMEdit | Overlay | Grid |
|---------|--------|---------|------|
| Variables per plot | 1 | Multiple | 1-6 |
| Best for | Individual analysis | Comparison | Overview |
| Layout | Vertical stack | Single | 2-column grid |
| Lines | Clean, separated | Colored | Minimal |

## Advanced Features

### Multi-Parameter Optimization
1. Adjust slider for parameter A
2. Run simulation
3. Adjust slider for parameter B
4. Run simulation again
5. Compare results visually

### Real-Time Feedback
- Status updates show current operation (Generating, Running, Visualizing)
- Color-coded messages:
  - **Blue**: Operation in progress
  - **Green**: Success
  - **Red**: Error

### Threading
All long operations (model generation, simulation, visualization) run in background threads to keep UI responsive.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| GUI doesn't open | Check if tkinter is installed: `pip install tkinter` |
| OpenModelica error | Verify OMC is in PATH: `omc --version` |
| Parameters not extracted | Description should explicitly mention parameter names and values |
| Visualization blank | Run simulation first, then visualize |
| Slow simulation | Reduce number of intervals or stop time |

## Output Files

All files are saved in: `workspaces/GUI_Simulator/`

```
workspaces/GUI_Simulator/
├── [ModelName].mo              # Generated Modelica model
├── simulate_[ModelName].mos    # Simulation script
└── [ModelName]_res.mat         # Results file (binary)
```

Visualization is displayed directly in the GUI but not automatically saved. To save plots:
- Right-click on plot → Save Image
- Or use matplotlib toolbar "Save" button

## Tips for Best Results

1. **Clear Descriptions**: Include parameter names and values explicitly
   - Good: "mass m = 2.0 kg, spring k = 100 N/m"
   - Bad: "A mass-spring system"

2. **Parameter Ranges**: System auto-calculates as 0.1x to 10x current value
   - For mass 1.0 kg → slider 0.1 to 10.0 kg
   - Adjust slider handles to change ranges if needed

3. **Visualization**: Switch between styles to see different perspectives
   - Use OMEdit for detail analysis
   - Use Overlay for cross-variable relationships
   - Use Grid for overview of many variables

4. **Time Resolution**: More intervals = smoother plots but slower simulation
   - Default 500: Good balance
   - 1000+: Very smooth, slower
   - 100: Fast, choppy

## Requirements

- Python 3.8+
- tkinter (usually bundled with Python)
- matplotlib
- scipy
- numpy
- All packages in `requirements.txt`

## Command Reference

```bash
# Launch GUI
python gui_simulator.py

# View help
python gui_simulator.py --help

# Alternative: Use non-GUI versions
python interactive_workflow.py      # Console-based
python custom_models.py             # Automated
python visualize_mat.py <file.mat>  # Visualization only
```

## GUI Simulator Advantages Over Console

| Feature | GUI | Console |
|---------|-----|---------|
| Real-time parameters | ✅ Sliders | Manual edits |
| Visual feedback | ✅ Live plots | File-based |
| Parameter ranges | ✅ Auto-calibrated | Fixed |
| Multiple viz styles | ✅ 3 options | 1 style |
| Ease of use | ✅ Intuitive | Scripting |
| Batch processing | ❌ Not ideal | ✅ Better |

## Future Enhancements

Potential features for future versions:
- Save/load parameter presets
- Export plots to PNG/PDF
- Sensitivity analysis (vary parameters, compare results)
- Parameter optimization (find optimal values)
- Custom plot templates
- Model validation checker
