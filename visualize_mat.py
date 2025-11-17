#!/usr/bin/env python3
"""
Visualization tool for MAT simulation results
Standalone script to visualize any MAT file from the system
"""

import sys
from pathlib import Path
from scipy.io import loadmat
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def load_and_visualize_mat(mat_file_path):
    """Load MAT file and visualize all variables"""
    
    print("\n" + "=" * 80)
    print(" " * 20 + "MAT FILE VISUALIZER - Simulation Results Analysis")
    print("=" * 80 + "\n")
    
    mat_path = Path(mat_file_path)
    
    if not mat_path.exists():
        print(f"[ERROR] File not found: {mat_path}")
        return
    
    print(f"[INFO] Loading MAT file: {mat_path}")
    print(f"[INFO] File size: {mat_path.stat().st_size} bytes\n")
    
    try:
        print("[DEBUG] Reading MAT file...")
        data = loadmat(str(mat_path))
        print(f"[DEBUG] Loaded {len(data)} items from MAT file\n")
    except Exception as e:
        print(f"[ERROR] Failed to load MAT file: {e}")
        return
    
    # Extract time and variables
    print("[DEBUG] Extracting variables...")
    time_data = None
    variables = {}
    
    # Try to extract actual simulation data from OpenModelica MAT format
    # OpenModelica MAT files have 'data_1' (time) and 'data_2' (values) 
    if 'data_1' in data:
        time_data = data['data_1'].flatten()
        print(f"[DEBUG] Found time vector in 'data_1' ({len(time_data)} points)")
    
    if 'data_2' in data:
        # data_2 contains all the variable values stacked
        # Get variable names from 'name'
        if 'name' in data:
            var_names_raw = data['name']
            var_names = []
            if var_names_raw.dtype.kind == 'O':  # Object array (strings)
                for name_array in var_names_raw:
                    try:
                        name_str = ''.join(chr(c) for c in name_array if 32 <= c < 127)
                        if name_str:
                            var_names.append(name_str.strip())
                    except:
                        pass
            
            print(f"[DEBUG] Found {len(var_names)} variable names: {var_names}")
            
            data_2 = data['data_2']
            if time_data is not None and len(data_2.shape) == 2:
                # Each column is a variable
                n_vars = data_2.shape[1]
                for i in range(min(n_vars, len(var_names))):
                    var_data = data_2[:, i].flatten()
                    var_names[i] = var_names[i] if i < len(var_names) else f"Variable_{i}"
                    variables[var_names[i]] = var_data
                    print(f"  - {var_names[i]:30s}: {len(var_data)} points, "
                          f"range [{var_data.min():.6f}, {var_data.max():.6f}]")
            elif time_data is not None:
                # Single variable
                var_data = data_2.flatten()
                var_name = var_names[0] if var_names else "Variable"
                variables[var_name] = var_data
                print(f"  - {var_name:30s}: {len(var_data)} points, "
                      f"range [{var_data.min():.6f}, {var_data.max():.6f}]")
    
    # Fallback: extract any remaining numeric arrays
    if not variables:
        print("[DEBUG] No standard MAT format found, extracting all numeric arrays...")
        for key in sorted(data.keys()):
            if not key.startswith('_'):
                try:
                    var_data = data[key].flatten()
                    if len(var_data) > 10 and var_data.dtype in [float, int]:  # Only numeric with enough points
                        variables[key] = var_data
                        print(f"  - {key:30s}: {len(var_data)} points")
                except:
                    pass
    
    if not variables:
        print("[ERROR] No plottable variables found")
        return
    
    print(f"\n[INFO] Total variables to plot: {len(variables)}\n")
    
    # Setup plotting style
    print("[DEBUG] Configuring Seaborn style...")
    sns.set_style(Config.SEABORN_STYLE)
    sns.set_palette(Config.COLOR_PALETTE)
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 150
    
    # Create output directory
    output_dir = mat_path.parent / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Output directory: {output_dir}\n")
    
    # ============================================================
    # Plot 1: All Variables Grid
    # ============================================================
    print("[PLOT 1] Creating grid of all variables...")
    
    var_list = list(variables.keys())[:12]  # Limit to 12 for visibility
    n_plots = len(var_list)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
    axes = axes.flatten()
    
    for idx, var_name in enumerate(var_list):
        ax = axes[idx]
        var_data = variables[var_name]
        
        print(f"[DEBUG] Plotting {idx+1}/{n_plots}: {var_name} ({len(var_data)} points)")
        
        # If time_data doesn't match length, use indices instead
        if time_data is not None and len(time_data) == len(var_data):
            x_axis = time_data
            x_label = 'Time (s)'
        else:
            x_axis = range(len(var_data))
            x_label = 'Index'
        
        ax.plot(x_axis, var_data, 'b-', linewidth=2)
        ax.fill_between(x_axis, var_data, alpha=0.3)
        ax.set_title(var_name, fontsize=12, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel('Value', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for idx in range(n_plots, len(axes)):
        axes[idx].set_visible(False)
    
    fig.suptitle('Simulation Results - All Variables', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    plot_file_1 = output_dir / "01_all_variables.png"
    plt.savefig(plot_file_1, bbox_inches='tight', dpi=150)
    print(f"[DEBUG] ✓ Saved: {plot_file_1}")
    plt.close()
    
    # ============================================================
    # Plot 2: First Few Variables on Same Axes
    # ============================================================
    if len(var_list) > 1:
        print(f"\n[PLOT 2] Creating overlay plot of first {min(4, len(var_list))} variables...")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for var_name in var_list[:4]:
            var_data = variables[var_name]
            
            # If time_data doesn't match, use indices
            if time_data is not None and len(time_data) == len(var_data):
                x_axis = time_data
            else:
                x_axis = range(len(var_data))
            
            ax.plot(x_axis, var_data, linewidth=2, label=var_name, 
                   marker='o', markersize=1, alpha=0.8)
        
        ax.set_title('Simulation Results - Overlay', fontsize=14, fontweight='bold')
        x_label = 'Time (s)' if (time_data is not None and len(time_data) == len(variables[var_list[0]])) else 'Index'
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        
        plot_file_2 = output_dir / "02_overlay_plot.png"
        plt.savefig(plot_file_2, bbox_inches='tight', dpi=150)
        print(f"[DEBUG] ✓ Saved: {plot_file_2}")
        plt.close()
    
    # ============================================================
    # Plot 3: Statistics Summary
    # ============================================================
    print(f"\n[PLOT 3] Creating statistics summary...")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create stats table
    stats_text = "VARIABLE STATISTICS SUMMARY\n"
    stats_text += "=" * 90 + "\n\n"
    stats_text += f"{'Variable':<25} {'Min':>15} {'Max':>15} {'Mean':>15} {'Std':>15}\n"
    stats_text += "-" * 90 + "\n"
    
    for var_name in var_list:
        var_data = variables[var_name]
        stats_text += (f"{var_name:<25} "
                      f"{var_data.min():>15.6f} "
                      f"{var_data.max():>15.6f} "
                      f"{var_data.mean():>15.6f} "
                      f"{var_data.std():>15.6f}\n")
    
    stats_text += "-" * 90
    
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.2))
    ax.axis('off')
    
    fig.suptitle('Simulation Results - Statistics', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    plot_file_3 = output_dir / "03_statistics.png"
    plt.savefig(plot_file_3, bbox_inches='tight', dpi=150)
    print(f"[DEBUG] ✓ Saved: {plot_file_3}")
    plt.close()
    
    # ============================================================
    # Plot 4: Phase Portrait (if 2+ variables)
    # ============================================================
    if len(var_list) >= 2:
        print(f"\n[PLOT 4] Creating phase portrait...")
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        var1_name = var_list[0]
        var2_name = var_list[1]
        var1_data = variables[var1_name]
        var2_data = variables[var2_name]
        
        # Make sure they have the same length
        min_len = min(len(var1_data), len(var2_data))
        var1_data = var1_data[:min_len]
        var2_data = var2_data[:min_len]
        
        # Plot trajectory
        ax.plot(var1_data, var2_data, 'b-', linewidth=2, alpha=0.7)
        
        # Mark start and end points
        ax.plot(var1_data[0], var2_data[0], 'go', markersize=12, 
               label='Start', zorder=5)
        ax.plot(var1_data[-1], var2_data[-1], 'r^', markersize=12, 
               label='End', zorder=5)
        
        # Add direction arrows
        if len(var1_data) > 10:
            step = len(var1_data) // 5
            for i in range(step, len(var1_data), step):
                ax.arrow(var1_data[i-step], var2_data[i-step],
                        var1_data[i] - var1_data[i-step],
                        var2_data[i] - var2_data[i-step],
                        head_width=0.02*(var1_data.max()-var1_data.min()),
                        head_length=0.02*(var2_data.max()-var2_data.min()),
                        fc='red', ec='red', alpha=0.5)
        
        ax.set_title(f'Phase Portrait: {var1_name} vs {var2_name}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel(var1_name, fontsize=12)
        ax.set_ylabel(var2_name, fontsize=12)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        
        plot_file_4 = output_dir / "04_phase_portrait.png"
        plt.savefig(plot_file_4, bbox_inches='tight', dpi=150)
        print(f"[DEBUG] ✓ Saved: {plot_file_4}")
        plt.close()
    
    # ============================================================
    # Final Summary
    # ============================================================
    print("\n" + "=" * 80)
    print(" " * 25 + "VISUALIZATION COMPLETE")
    print("=" * 80)
    print(f"\n[SUMMARY] Generated plots:")
    print(f"  1. All variables grid: {plot_file_1}")
    if len(var_list) > 1:
        print(f"  2. Overlay plot: {plot_file_2}")
    print(f"  3. Statistics: {plot_file_3}")
    if len(var_list) >= 2:
        print(f"  4. Phase portrait: {plot_file_4}")
    
    print(f"\n[INFO] All visualizations saved to: {output_dir}")
    print(f"[INFO] Total plots generated: {len(list(output_dir.glob('*.png')))}")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python visualize_mat.py <path_to_mat_file>")
        print("\nExample:")
        print("  python visualize_mat.py workspaces/InteractiveTest/SimpleMassForce_res.mat")
        print("\nOr use interactively:")
        print("  python visualize_mat.py\n")
        
        # Interactive mode
        mat_file = input("Enter path to MAT file: ").strip()
        if mat_file:
            load_and_visualize_mat(mat_file)
    else:
        mat_file = sys.argv[1]
        load_and_visualize_mat(mat_file)
