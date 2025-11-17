#!/usr/bin/env python3
"""
GUI-based Modelica Simulator with Parameter Control
Provides real-time parameter adjustment with immediate re-simulation and visualization
"""

import sys
import re
from pathlib import Path
from datetime import datetime
import numpy as np
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading

sys.path.insert(0, str(Path(__file__).parent))

from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelicaSimulatorGUI:
    """GUI for Modelica model simulation with parameter control"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Modelica Model Simulator - Parameter Control")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.agent = OpenModelicaAgent()
        self.executor = OMCExecutor()
        Config.ensure_directories()
        
        # Workspace setup
        self.workspace = Config.get_workspace_path("GUI_Simulator")
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Current model state
        self.current_model_code = None
        self.current_model_name = None
        self.current_mat_file = None
        self.parameters = {}
        
        # Create UI
        self.create_widgets()
        
        # Check OpenModelica availability
        if not self.executor.check_omc_available():
            messagebox.showerror("Error", "OpenModelica not found!\nPlease install OpenModelica from openmodelica.org")
            sys.exit(1)
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Main notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # ============================================================
        # TAB 1: Model Generation
        # ============================================================
        frame_gen = ttk.Frame(notebook)
        notebook.add(frame_gen, text="Model Generation")
        
        # Description input
        ttk.Label(frame_gen, text="Model Description:").pack(anchor=W, padx=10, pady=(10, 0))
        self.text_description = Text(frame_gen, height=8, width=100)
        self.text_description.pack(padx=10, pady=5, fill=BOTH, expand=True)
        self.text_description.insert(END, """A simple force-mass-acceleration system:
- Mass m = 1.0 kg
- Applied force F = 10.0 N (constant)
- Initial velocity = 0 m/s
- Initial position = 0 m
- Simulate for 10 seconds""")
        
        # Generate button
        btn_frame = ttk.Frame(frame_gen)
        btn_frame.pack(padx=10, pady=10, fill=X)
        
        ttk.Button(btn_frame, text="Generate Model", command=self.generate_model).pack(side=LEFT, padx=5)
        self.status_label = ttk.Label(btn_frame, text="Ready", foreground="blue")
        self.status_label.pack(side=LEFT, padx=10)
        
        # ============================================================
        # TAB 2: Parameters & Simulation
        # ============================================================
        frame_params = ttk.Frame(notebook)
        notebook.add(frame_params, text="Parameters & Simulation")
        
        # Parameters frame
        params_canvas = Canvas(frame_params)
        scrollbar = ttk.Scrollbar(frame_params, orient="vertical", command=params_canvas.yview)
        self.params_frame = ttk.Frame(params_canvas)
        
        self.params_frame.bind(
            "<Configure>",
            lambda e: params_canvas.configure(scrollregion=params_canvas.bbox("all"))
        )
        
        params_canvas.create_window((0, 0), window=self.params_frame, anchor="nw")
        params_canvas.configure(yscrollcommand=scrollbar.set)
        
        params_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Simulation controls
        sim_frame = ttk.LabelFrame(frame_params, text="Simulation Settings", padding=10)
        sim_frame.pack(padx=10, pady=10, fill=X, side=BOTTOM)
        
        ttk.Label(sim_frame, text="Stop Time (s):").grid(row=0, column=0, sticky=W)
        self.stop_time_var = DoubleVar(value=10.0)
        ttk.Spinbox(sim_frame, from_=0.1, to=100, textvariable=self.stop_time_var, width=10).grid(row=0, column=1, sticky=W, padx=5)
        
        ttk.Label(sim_frame, text="Number of Intervals:").grid(row=0, column=2, sticky=W, padx=(20, 0))
        self.intervals_var = IntVar(value=500)
        ttk.Spinbox(sim_frame, from_=10, to=5000, textvariable=self.intervals_var, width=10).grid(row=0, column=3, sticky=W, padx=5)
        
        btn_sim_frame = ttk.Frame(frame_params)
        btn_sim_frame.pack(padx=10, pady=10, fill=X, side=BOTTOM)
        ttk.Button(btn_sim_frame, text="Run Simulation", command=self.run_simulation).pack(side=LEFT, padx=5)
        ttk.Button(btn_sim_frame, text="Visualize Results", command=self.visualize_results).pack(side=LEFT, padx=5)
        
        # ============================================================
        # TAB 3: Visualization (OMEdit Style)
        # ============================================================
        frame_viz = ttk.Frame(notebook)
        notebook.add(frame_viz, text="Visualization")
        
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        
        self.fig = Figure(figsize=(11, 7), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_viz)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Visualization options
        viz_frame = ttk.Frame(frame_viz)
        viz_frame.pack(padx=10, pady=5, fill=X)
        
        ttk.Label(viz_frame, text="Style:").pack(side=LEFT, padx=5)
        self.style_var = StringVar(value="OMEdit")
        ttk.Combobox(viz_frame, textvariable=self.style_var, values=["OMEdit", "Overlay", "Grid"], state="readonly", width=15).pack(side=LEFT, padx=5)
        
        ttk.Button(viz_frame, text="Refresh Plot", command=self.visualize_results).pack(side=LEFT, padx=5)
    
    def update_status(self, message, color="blue"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def generate_model(self):
        """Generate model from description in separate thread"""
        def generate():
            try:
                self.update_status("Generating model...", "blue")
                
                description = self.text_description.get("1.0", END)
                if not description.strip():
                    messagebox.showerror("Error", "Please enter a model description")
                    return
                
                # Generate model
                self.current_model_code = self.agent.generate_modelica_model(description)
                
                # Extract model name
                match = re.search(r'\bmodel\s+([A-Za-z_]\w*)\b', self.current_model_code)
                if match:
                    self.current_model_name = match.group(1)
                    if self.current_model_name.lower() in ['model', 'end', 'equation', 'parameter']:
                        self.current_model_name = "GeneratedModel"
                else:
                    self.current_model_name = "GeneratedModel"
                
                # Save model
                mo_file = self.workspace / f"{self.current_model_name}.mo"
                with open(mo_file, 'w', encoding='utf-8') as f:
                    f.write(self.current_model_code)
                
                # Extract parameters from model
                self.extract_parameters(self.current_model_code)
                self.populate_parameter_controls()
                
                self.update_status(f"Model generated: {self.current_model_name}", "green")
                messagebox.showinfo("Success", f"Model '{self.current_model_name}' generated successfully!\n\nExtracted {len(self.parameters)} parameters.")
                
            except Exception as e:
                self.update_status(f"Error: {str(e)}", "red")
                messagebox.showerror("Error", f"Failed to generate model:\n{str(e)}")
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def extract_parameters(self, mo_code):
        """Extract parameters from Modelica code"""
        self.parameters = {}
        
        # Find all parameter declarations
        pattern = r'parameter\s+Real\s+(\w+)\s*=\s*([\d.]+)'
        matches = re.findall(pattern, mo_code)
        
        for param_name, param_value in matches:
            try:
                self.parameters[param_name] = float(param_value)
            except ValueError:
                self.parameters[param_name] = 0.0
    
    def populate_parameter_controls(self):
        """Create slider controls for parameters"""
        # Clear previous controls
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        if not self.parameters:
            ttk.Label(self.params_frame, text="No parameters found in model").pack(padx=10, pady=10)
            return
        
        ttk.Label(self.params_frame, text="Model Parameters", font=("Arial", 12, "bold")).pack(anchor=W, padx=10, pady=(10, 5))
        
        self.param_vars = {}
        
        for param_name, param_value in self.parameters.items():
            # Determine reasonable range based on value
            min_val = max(0.1, param_value * 0.1)
            max_val = param_value * 10
            
            # Frame for each parameter
            param_frame = ttk.LabelFrame(self.params_frame, text=f"{param_name} = {param_value}", padding=10)
            param_frame.pack(padx=10, pady=5, fill=X)
            
            # Variable for this parameter
            self.param_vars[param_name] = DoubleVar(value=param_value)
            
            # Slider
            scale = Scale(param_frame, from_=min_val, to=max_val, orient=HORIZONTAL, 
                         variable=self.param_vars[param_name],
                         command=lambda val, name=param_name: self.update_param_label(name, val),
                         resolution=0.01, length=300)
            scale.pack(fill=X, expand=True)
            
            # Value display
            self.param_labels = {}
            self.param_labels[param_name] = ttk.Label(param_frame, text=f"Value: {param_value:.4f}", foreground="blue")
            self.param_labels[param_name].pack(anchor=E, padx=10, pady=5)
    
    def update_param_label(self, param_name, value):
        """Update parameter value display"""
        if hasattr(self, 'param_labels') and param_name in self.param_labels:
            self.param_labels[param_name].config(text=f"Value: {float(value):.4f}")
    
    def run_simulation(self):
        """Run simulation with current parameters"""
        def simulate():
            try:
                if not self.current_model_code or not self.current_model_name:
                    messagebox.showerror("Error", "Please generate a model first")
                    return
                
                self.update_status("Running simulation...", "blue")
                
                # Update model with current parameters
                updated_model = self.current_model_code
                
                for param_name, var in self.param_vars.items():
                    current_value = var.get()
                    # Replace parameter value in model
                    pattern = rf'(parameter\s+Real\s+{param_name}\s*=\s*)([\d.]+)'
                    updated_model = re.sub(pattern, rf'\g<1>{current_value}', updated_model)
                
                self.current_model_code = updated_model
                
                # Save updated model
                mo_file = self.workspace / f"{self.current_model_name}.mo"
                with open(mo_file, 'w', encoding='utf-8') as f:
                    f.write(updated_model)
                
                # Generate simulation script
                stop_time = self.stop_time_var.get()
                intervals = self.intervals_var.get()
                
                mos_code = self.agent.generate_simulation_script(self.current_model_name, mo_file)
                
                # Customize script with parameters
                mos_code = mos_code.replace("stopTime=10", f"stopTime={stop_time}")
                mos_code = mos_code.replace("numberOfIntervals=500", f"numberOfIntervals={intervals}")
                
                mos_file = self.workspace / f"simulate_{self.current_model_name}.mos"
                with open(mos_file, 'w', encoding='utf-8') as f:
                    f.write(mos_code)
                
                # Run simulation
                success, output, mat_file = self.executor.run_simulation_script(mos_file)
                
                if success and mat_file:
                    self.current_mat_file = mat_file
                    self.update_status(f"Simulation complete: {mat_file.name}", "green")
                    messagebox.showinfo("Success", "Simulation completed successfully!")
                else:
                    self.update_status("Simulation failed", "red")
                    messagebox.showerror("Error", f"Simulation failed:\n{output}")
                
            except Exception as e:
                self.update_status(f"Error: {str(e)}", "red")
                messagebox.showerror("Error", f"Simulation error:\n{str(e)}")
        
        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()
    
    def visualize_results(self):
        """Visualize MAT file with OMEdit-style plots"""
        def visualize():
            try:
                if not self.current_mat_file or not self.current_mat_file.exists():
                    messagebox.showerror("Error", "No simulation results available")
                    return
                
                self.update_status("Generating visualization...", "blue")
                
                from scipy.io import loadmat
                import matplotlib.pyplot as plt
                
                # Load MAT file
                data = loadmat(str(self.current_mat_file))
                
                # Extract data
                if 'data_1' not in data or 'data_2' not in data:
                    messagebox.showerror("Error", "Invalid MAT file format")
                    return
                
                time = data['data_1'].flatten()
                var_data = data['data_2']
                
                if len(var_data.shape) > 1:
                    n_vars = var_data.shape[1]
                else:
                    n_vars = 1
                
                # Clear previous plot
                self.fig.clear()
                
                style = self.style_var.get()
                
                if style == "OMEdit":
                    # OMEdit style: separate subplots, dark grid, white background
                    n_plots = min(n_vars, 5)
                    axes = self.fig.subplots(n_plots, 1)
                    if n_plots == 1:
                        axes = [axes]
                    
                    for i in range(n_plots):
                        if len(var_data.shape) > 1:
                            y = var_data[:, i]
                        else:
                            y = var_data.flatten()
                        
                        # Match time if possible
                        if len(time) == len(y):
                            x = time
                        else:
                            x = np.arange(len(y))
                        
                        # OMEdit style: dark lines, light background
                        axes[i].plot(x, y, color='#1f77b4', linewidth=1.5, label=f'Var_{i}')
                        axes[i].grid(True, alpha=0.3, linestyle='--', color='gray')
                        axes[i].set_facecolor('#f8f8f8')
                        axes[i].set_ylabel(f'Variable {i}', fontsize=10)
                        axes[i].legend(loc='upper right', fontsize=8)
                        axes[i].spines['top'].set_visible(False)
                        axes[i].spines['right'].set_visible(False)
                    
                    axes[-1].set_xlabel('Time (s)', fontsize=10)
                
                elif style == "Overlay":
                    # All variables on one plot
                    ax = self.fig.add_subplot(111)
                    colors = plt.cm.tab10(np.linspace(0, 1, min(n_vars, 5)))
                    
                    for i in range(min(n_vars, 5)):
                        if len(var_data.shape) > 1:
                            y = var_data[:, i]
                        else:
                            y = var_data.flatten()
                        
                        if len(time) == len(y):
                            x = time
                        else:
                            x = np.arange(len(y))
                        
                        ax.plot(x, y, linewidth=1.5, label=f'Var_{i}', color=colors[i])
                    
                    ax.grid(True, alpha=0.3)
                    ax.set_xlabel('Time (s)', fontsize=10)
                    ax.set_ylabel('Values', fontsize=10)
                    ax.legend()
                    ax.set_facecolor('#f8f8f8')
                
                elif style == "Grid":
                    # Grid of all variables
                    n_cols = 2
                    n_rows = (min(n_vars, 6) + n_cols - 1) // n_cols
                    axes = self.fig.subplots(n_rows, n_cols)
                    axes = axes.flatten()
                    
                    for i in range(min(n_vars, 6)):
                        if len(var_data.shape) > 1:
                            y = var_data[:, i]
                        else:
                            y = var_data.flatten()
                        
                        if len(time) == len(y):
                            x = time
                        else:
                            x = np.arange(len(y))
                        
                        axes[i].plot(x, y, color='#1f77b4', linewidth=1.5)
                        axes[i].grid(True, alpha=0.3)
                        axes[i].set_title(f'Variable {i}', fontsize=9)
                        axes[i].set_facecolor('#f8f8f8')
                    
                    # Hide unused subplots
                    for i in range(min(n_vars, 6), len(axes)):
                        axes[i].set_visible(False)
                
                self.fig.suptitle(f'Simulation Results: {self.current_model_name}', fontsize=12, fontweight='bold')
                self.fig.tight_layout()
                self.canvas.draw()
                
                self.update_status("Visualization complete", "green")
                
            except Exception as e:
                self.update_status(f"Visualization error: {str(e)}", "red")
                messagebox.showerror("Error", f"Visualization failed:\n{str(e)}")
        
        thread = threading.Thread(target=visualize, daemon=True)
        thread.start()


def main():
    root = Tk()
    gui = ModelicaSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
