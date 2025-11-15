
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx
from pathlib import Path
from typing import Dict, List
from parsers.model_parser import ModelParser
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ModelVisualizer:
    """Visualizer for Modelica model structure"""
    
    def __init__(self, model_parser: ModelParser):
        """
        Initialize model visualizer
        
        Args:
            model_parser: Parsed model parser instance
        """
        self.parser = model_parser
        logger.info("Model visualizer initialized")
    
    def create_block_diagram(self, output_path: Path):
        """
        Create block diagram visualization of model structure
        
        Args:
            output_path: Path to save the figure
        """
        logger.info("Creating block diagram...")
        
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Title
        ax.text(5, 9.5, f'Model: {self.parser.model_name}', 
               ha='center', va='top', fontsize=18, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7))
        
        # Parameters box
        if self.parser.parameters:
            param_y = 8
            param_box = FancyBboxPatch((0.5, param_y-0.8), 2.5, 0.8,
                                      boxstyle="round,pad=0.1",
                                      edgecolor='darkgreen', facecolor='lightgreen',
                                      alpha=0.6, linewidth=2)
            ax.add_patch(param_box)
            ax.text(1.75, param_y-0.4, 'Parameters', ha='center', va='center',
                   fontsize=11, fontweight='bold')
            
            # List parameters
            param_text = '\n'.join([f"• {p['name']}" for p in self.parser.parameters[:5]])
            if len(self.parser.parameters) > 5:
                param_text += f"\n... and {len(self.parser.parameters)-5} more"
            ax.text(1.75, param_y-1.5, param_text, ha='center', va='top',
                   fontsize=8, fontfamily='monospace')
        
        # Variables box
        if self.parser.variables:
            var_y = 6
            var_box = FancyBboxPatch((0.5, var_y-0.8), 2.5, 0.8,
                                    boxstyle="round,pad=0.1",
                                    edgecolor='darkblue', facecolor='lightblue',
                                    alpha=0.6, linewidth=2)
            ax.add_patch(var_box)
            ax.text(1.75, var_y-0.4, 'Variables', ha='center', va='center',
                   fontsize=11, fontweight='bold')
            
            # List variables
            var_text = '\n'.join([f"• {v['name']}" for v in self.parser.variables[:5]])
            if len(self.parser.variables) > 5:
                var_text += f"\n... and {len(self.parser.variables)-5} more"
            ax.text(1.75, var_y-1.5, var_text, ha='center', va='top',
                   fontsize=8, fontfamily='monospace')
        
        # Equations box
        if self.parser.equations:
            eq_y = 5
            eq_box = FancyBboxPatch((4, eq_y-1.5), 5.5, 3,
                                   boxstyle="round,pad=0.15",
                                   edgecolor='darkred', facecolor='lightyellow',
                                   alpha=0.6, linewidth=2)
            ax.add_patch(eq_box)
            ax.text(6.75, eq_y+1.2, 'Equations', ha='center', va='center',
                   fontsize=12, fontweight='bold')
            
            # List equations
            eq_text = '\n'.join([f"• {eq[:60]}..." if len(eq) > 60 else f"• {eq}" 
                                for eq in self.parser.equations[:8]])
            if len(self.parser.equations) > 8:
                eq_text += f"\n... and {len(self.parser.equations)-8} more"
            ax.text(6.75, eq_y+0.5, eq_text, ha='center', va='top',
                   fontsize=7, fontfamily='monospace')
        
        # Components box
        if self.parser.components:
            comp_y = 2
            comp_box = FancyBboxPatch((0.5, comp_y-0.8), 2.5, 0.8,
                                     boxstyle="round,pad=0.1",
                                     edgecolor='purple', facecolor='lavender',
                                     alpha=0.6, linewidth=2)
            ax.add_patch(comp_box)
            ax.text(1.75, comp_y-0.4, 'Components', ha='center', va='center',
                   fontsize=11, fontweight='bold')
            
            # List components
            comp_text = '\n'.join([f"• {c['name']}: {c['type']}" 
                                  for c in self.parser.components[:5]])
            if len(self.parser.components) > 5:
                comp_text += f"\n... and {len(self.parser.components)-5} more"
            ax.text(1.75, comp_y-1.5, comp_text, ha='center', va='top',
                   fontsize=8, fontfamily='monospace')
        
        # Draw arrows showing relationships
        if self.parser.parameters and self.parser.equations:
            arrow1 = FancyArrowPatch((3, 7.6), (4, 6), 
                                    arrowstyle='->', mutation_scale=20,
                                    color='gray', linewidth=2, alpha=0.6)
            ax.add_patch(arrow1)
        
        if self.parser.variables and self.parser.equations:
            arrow2 = FancyArrowPatch((3, 5.6), (4, 5), 
                                    arrowstyle='->', mutation_scale=20,
                                    color='gray', linewidth=2, alpha=0.6)
            ax.add_patch(arrow2)
        
        # Statistics box
        stats_text = f"Statistics:\n"
        stats_text += f"Parameters: {len(self.parser.parameters)}\n"
        stats_text += f"Variables: {len(self.parser.variables)}\n"
        stats_text += f"Equations: {len(self.parser.equations)}\n"
        stats_text += f"Components: {len(self.parser.components)}"
        
        ax.text(7.5, 1, stats_text, ha='center', va='center',
               fontsize=10, fontfamily='monospace',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=Config.FIGURE_DPI)
        plt.close()
        
        logger.info(f"Saved block diagram: {output_path}")
    
    def create_dependency_graph(self, output_path: Path):
        """
        Create dependency graph of model variables
        
        Args:
            output_path: Path to save the figure
        """
        logger.info("Creating dependency graph...")
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes for variables and parameters
        for var in self.parser.variables:
            G.add_node(var['name'], node_type='variable')
        
        for param in self.parser.parameters:
            G.add_node(param['name'], node_type='parameter')
        
        # Analyze equations to find dependencies
        for equation in self.parser.equations:
            # Find all identifiers in equation
            identifiers = set()
            for var in self.parser.variables:
                if var['name'] in equation:
                    identifiers.add(var['name'])
            for param in self.parser.parameters:
                if param['name'] in equation:
                    identifiers.add(param['name'])
            
            # Create edges between identifiers
            id_list = list(identifiers)
            for i in range(len(id_list)):
                for j in range(i+1, len(id_list)):
                    G.add_edge(id_list[i], id_list[j])
        
        if len(G.nodes()) == 0:
            logger.warning("No nodes to visualize in dependency graph")
            return
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Separate nodes by type
        var_nodes = [n for n, attr in G.nodes(data=True) 
                    if attr.get('node_type') == 'variable']
        param_nodes = [n for n, attr in G.nodes(data=True) 
                      if attr.get('node_type') == 'parameter']
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, nodelist=var_nodes,
                              node_color='lightblue', node_size=1500,
                              alpha=0.8, ax=ax, label='Variables')
        nx.draw_networkx_nodes(G, pos, nodelist=param_nodes,
                              node_color='lightgreen', node_size=1500,
                              alpha=0.8, ax=ax, label='Parameters')
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray',
                              alpha=0.5, arrows=True, ax=ax,
                              arrowsize=15, arrowstyle='->')
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, 
                               font_weight='bold', ax=ax)
        
        ax.set_title(f'Dependency Graph: {self.parser.model_name}',
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', fontsize=10)
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=Config.FIGURE_DPI)
        plt.close()
        
        logger.info(f"Saved dependency graph: {output_path}")