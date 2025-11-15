"""
Results visualizer for simulation data using Seaborn
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List, Optional
from parsers.mat_parser import MATParser
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ResultsVisualizer:
    """Visualizer for OpenModelica simulation results"""
    
    def __init__(self, mat_parser: MATParser):
        """
        Initialize results visualizer
        
        Args:
            mat_parser: Loaded MAT parser instance
        """
        self.parser = mat_parser
        self.setup_style()
        logger.info("Results visualizer initialized")
    
    def setup_style(self):
        """Set up Seaborn style"""
        sns.set_style(Config.SEABORN_STYLE)
        sns.set_palette(Config.COLOR_PALETTE)
        plt.rcParams['figure.dpi'] = Config.FIGURE_DPI
        plt.rcParams['savefig.dpi'] = Config.FIGURE_DPI
        plt.rcParams['figure.figsize'] = Config.FIGURE_SIZE
    
    def plot_all_variables(self, output_path: Path, max_plots: int = 12):
        """
        Plot all plottable variables in a grid
        
        Args:
            output_path: Path to save the figure
            max_plots: Maximum number of subplots
        """
        logger.info("Plotting all variables...")
        
        variables = self.parser.filter_plot_variables()[:max_plots]
        
        if not variables:
            logger.warning("No plottable variables found")
            return
        
        # Calculate grid dimensions
        n_plots = len(variables)
        n_cols = min(3, n_plots)
        n_rows = (n_plots + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6*n_cols, 4*n_rows))
        
        if n_plots == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        for idx, var_name in enumerate(variables):
            ax = axes[idx]
            series = self.parser.get_time_series(var_name)
            
            if series is not None:
                sns.lineplot(x=series.index, y=series.values, ax=ax, linewidth=2)
                ax.set_title(f'{var_name}', fontsize=12, fontweight='bold')
                ax.set_xlabel('Time (s)', fontsize=10)
                ax.set_ylabel('Value', fontsize=10)
                ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for idx in range(n_plots, len(axes)):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved all variables plot: {output_path}")
    
    def plot_specific_variables(
        self, 
        variables: List[str], 
        output_path: Path,
        title: str = "Simulation Results"
    ):
        """
        Plot specific variables on the same axes
        
        Args:
            variables: List of variable names to plot
            output_path: Path to save the figure
            title: Plot title
        """
        logger.info(f"Plotting variables: {variables}")
        
        fig, ax = plt.subplots(figsize=Config.FIGURE_SIZE)
        
        for var_name in variables:
            series = self.parser.get_time_series(var_name)
            if series is not None:
                sns.lineplot(x=series.index, y=series.values, 
                           label=var_name, ax=ax, linewidth=2)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved specific variables plot: {output_path}")
    
    def plot_phase_portrait(
        self, 
        var_x: str, 
        var_y: str, 
        output_path: Path
    ):
        """
        Create phase portrait for two variables
        
        Args:
            var_x: X-axis variable
            var_y: Y-axis variable
            output_path: Path to save the figure
        """
        logger.info(f"Creating phase portrait: {var_x} vs {var_y}")
        
        data_x = self.parser.get_variable_data(var_x)
        data_y = self.parser.get_variable_data(var_y)
        
        if data_x is None or data_y is None:
            logger.warning("Variables not found for phase portrait")
            return
        
        fig, ax = plt.subplots(figsize=Config.FIGURE_SIZE)
        
        # Plot trajectory
        sns.lineplot(x=data_x, y=data_y, ax=ax, linewidth=2, alpha=0.7)
        
        # Mark start and end points
        ax.plot(data_x[0], data_y[0], 'go', markersize=10, label='Start')
        ax.plot(data_x[-1], data_y[-1], 'ro', markersize=10, label='End')
        
        ax.set_title(f'Phase Portrait: {var_x} vs {var_y}', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel(var_x, fontsize=12)
        ax.set_ylabel(var_y, fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved phase portrait: {output_path}")
    
    def plot_distribution(
        self, 
        variables: List[str], 
        output_path: Path
    ):
        """
        Plot distribution of variable values
        
        Args:
            variables: List of variable names
            output_path: Path to save the figure
        """
        logger.info(f"Plotting distributions for: {variables}")
        
        n_vars = len(variables)
        fig, axes = plt.subplots(1, n_vars, figsize=(6*n_vars, 5))
        
        if n_vars == 1:
            axes = [axes]
        
        for idx, var_name in enumerate(variables):
            data = self.parser.get_variable_data(var_name)
            
            if data is not None:
                sns.histplot(data, kde=True, ax=axes[idx], bins=30)
                axes[idx].set_title(f'{var_name} Distribution', 
                                  fontsize=12, fontweight='bold')
                axes[idx].set_xlabel('Value', fontsize=10)
                axes[idx].set_ylabel('Frequency', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved distribution plot: {output_path}")
    
    def create_summary_report(self, output_path: Path):
        """
        Create comprehensive visual summary report
        
        Args:
            output_path: Path to save the figure
        """
        logger.info("Creating summary report...")
        
        variables = self.parser.filter_plot_variables()[:6]
        
        if not variables:
            logger.warning("No variables to plot in summary")
            return
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Time series plots (top 2 rows)
        for idx, var_name in enumerate(variables[:6]):
            row = idx // 3
            col = idx % 3
            ax = fig.add_subplot(gs[row, col])
            
            series = self.parser.get_time_series(var_name)
            if series is not None:
                sns.lineplot(x=series.index, y=series.values, ax=ax, linewidth=2)
                ax.set_title(var_name, fontsize=11, fontweight='bold')
                ax.set_xlabel('Time (s)', fontsize=9)
                ax.set_ylabel('Value', fontsize=9)
                ax.grid(True, alpha=0.3)
        
        # Summary statistics (bottom row)
        ax_stats = fig.add_subplot(gs[2, :])
        summary = self.parser.get_summary()
        
        if summary:
            stats_text = "Variable Statistics:\n\n"
            for var_name in variables[:6]:
                if var_name in summary:
                    stats = summary[var_name]
                    stats_text += f"{var_name:20s}: "
                    stats_text += f"Min={stats['min']:8.3f}  "
                    stats_text += f"Max={stats['max']:8.3f}  "
                    stats_text += f"Mean={stats['mean']:8.3f}  "
                    stats_text += f"Std={stats['std']:8.3f}\n"
            
            ax_stats.text(0.05, 0.5, stats_text, 
                         transform=ax_stats.transAxes,
                         fontsize=10, verticalalignment='center',
                         fontfamily='monospace',
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
            ax_stats.axis('off')
        
        fig.suptitle('Simulation Results Summary', 
                    fontsize=18, fontweight='bold', y=0.995)
        
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved summary report: {output_path}")