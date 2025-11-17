#!/usr/bin/env python3
"""
Improved MAT file visualization that uses JSON info for proper variable names
"""

from scipy.io import loadmat
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

def get_variable_names_from_json(mat_file_path):
    """Extract variable names from the JSON info file"""
    mat_path = Path(mat_file_path)
    model_name = mat_path.stem.replace('_res', '')
    json_file = mat_path.parent / f"{model_name}_info.json"
    
    if not json_file.exists():
        return None
    
    try:
        with open(json_file, 'r') as f:
            info = json.load(f)
        
        variables = info.get('variables', {})
        # Get only state variables and derivatives (skip parameters)
        var_names = []
        for var_name, var_info in variables.items():
            kind = var_info.get('kind', '')
            if kind in ['state', 'derivative']:
                var_names.append(var_name)
        
        return var_names
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return None

def visualize_mat_with_names(mat_file_path):
    """Visualize MAT file with proper variable names from JSON"""
    
    mat_path = Path(mat_file_path)
    print(f"Visualizing: {mat_path.name}")
    
    # Load MAT file
    data = loadmat(str(mat_file_path))
    
    # Extract time and variables
    if 'data_1' not in data or 'data_2' not in data:
        print("ERROR: Invalid MAT file format")
        return
    
    time = data['data_1'].flatten()
    var_data = data['data_2']
    
    print(f"Time points: {len(time)}")
    print(f"Variable data shape: {var_data.shape}")
    
    # Get variable names from JSON
    var_names = get_variable_names_from_json(mat_file_path)
    
    if var_data.shape[1] != len(time):
        # Data is transposed: (n_vars, n_timepoints)
        n_vars = var_data.shape[0]
        n_points = var_data.shape[1]
        
        print(f"\nData structure: {n_vars} variables x {n_points} time points")
        print(f"Time array has {len(time)} points")
        
        # Create plots
        fig, axes = plt.subplots(min(n_vars, 5), 1, figsize=(12, 3*min(n_vars, 5)))
        if n_vars == 1:
            axes = [axes]
        
        # Use indices as x-axis since time dimension doesn't match
        for i in range(min(n_vars, 5)):
            y = var_data[i, :]
            x = np.arange(len(y))
            
            # Get proper variable name
            if var_names and i < len(var_names):
                var_label = var_names[i]
            else:
                var_label = f"Variable {i}"
            
            axes[i].plot(x, y, 'b-', linewidth=2, label=var_label)
            axes[i].fill_between(x, y, alpha=0.2)
            axes[i].set_ylabel(var_label, fontsize=11, fontweight='bold')
            axes[i].grid(True, alpha=0.3)
            axes[i].legend(loc='upper right')
            axes[i].set_facecolor('#f8f8f8')
        
        axes[-1].set_xlabel('Sample Index', fontsize=11)
        
    else:
        # Data is (n_timepoints, n_vars)
        n_vars = var_data.shape[1]
        
        print(f"\nData structure: {len(time)} time points x {n_vars} variables")
        
        # Create plots
        fig, axes = plt.subplots(min(n_vars, 5), 1, figsize=(12, 3*min(n_vars, 5)))
        if n_vars == 1:
            axes = [axes]
        
        for i in range(min(n_vars, 5)):
            y = var_data[:, i]
            
            # Get proper variable name
            if var_names and i < len(var_names):
                var_label = var_names[i]
            else:
                var_label = f"Variable {i}"
            
            axes[i].plot(time, y, 'b-', linewidth=2, label=var_label)
            axes[i].fill_between(time, y, alpha=0.2)
            axes[i].set_ylabel(var_label, fontsize=11, fontweight='bold')
            axes[i].grid(True, alpha=0.3)
            axes[i].legend(loc='upper right')
            axes[i].set_facecolor('#f8f8f8')
        
        axes[-1].set_xlabel('Time (s)', fontsize=11)
    
    model_name = mat_path.stem.replace('_res', '')
    plt.suptitle(f'Simulation Results: {model_name}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save and show
    output_file = mat_path.parent / f"{model_name}_corrected_visualization.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved: {output_file}")
    print(f"✓ File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    plt.show()

if __name__ == "__main__":
    # Test with recent MAT file
    workspace = Path("workspaces/GUI_Simulator")
    mat_files = sorted(workspace.glob("*_res.mat"))
    
    if mat_files:
        visualize_mat_with_names(mat_files[-1])
    else:
        print("No MAT files found")
