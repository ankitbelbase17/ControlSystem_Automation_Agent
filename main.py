"""
Main entry point for OpenModelica AI Agent
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from agents.openmodelica_agent import OpenModelicaAgent
from executors.omc_executor import OMCExecutor
from parsers.mat_parser import MATParser
from parsers.model_parser import ModelParser
from visualizers.model_visualizer import ModelVisualizer
from visualizers.results_visualizer import ResultsVisualizer
from utils.file_manager import FileManager
from utils.logger import setup_logger

# Setup main logger
logger = setup_logger(__name__, Config.BASE_DIR / "app.log")

class OpenModelicaAgentApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize the application"""
        logger.info("="*80)
        logger.info("OpenModelica AI Agent Starting...")
        logger.info("="*80)
        
        # Ensure directories exist
        Config.ensure_directories()
        
        # Initialize components
        self.agent = OpenModelicaAgent()
        self.executor = OMCExecutor()
        self.file_manager = FileManager()
        
        # Check OpenModelica availability
        if not self.executor.check_omc_available():
            logger.error("OpenModelica is not available. Please install it first.")
            logger.error("Download from: https://openmodelica.org/download/")
            sys.exit(1)
        
        logger.info("Application initialized successfully")
    
    def run_interactive(self):
        """Run in interactive mode"""
        print("\n" + "="*80)
        print("OpenModelica AI Agent - Interactive Mode")
        print("="*80)
        print("\nOptions:")
        print("1. Generate new model from description")
        print("2. Run example: Simple Pendulum")
        print("3. Run example: RC Circuit")
        print("4. Exit")
        print("\n")
        
        while True:
            choice = input("Select option (1-4): ").strip()
            
            if choice == '1':
                self.generate_custom_model()
            elif choice == '2':
                self.run_example_pendulum()
            elif choice == '3':
                self.run_example_rc_circuit()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def generate_custom_model(self):
        """Generate a custom model from user description"""
        print("\n" + "-"*80)
        print("Custom Model Generation")
        print("-"*80)
        
        description = input("\nDescribe the model you want to create:\n> ")
        
        if not description.strip():
            print("Description cannot be empty.")
            return
        
        # Generate model name
        model_name = input("\nEnter model name (e.g., MyModel): ").strip()
        if not model_name:
            model_name = "CustomModel"
        
        self.generate_and_simulate(model_name, description)
    
    def run_example_pendulum(self):
        """Run simple pendulum example"""
        description = """
        Create a simple pendulum model with the following characteristics:
        - Mass m = 1 kg
        - Length L = 1 meter
        - Gravitational acceleration g = 9.81 m/s²
        - Initial angle theta0 = 0.5 radians
        - Initial angular velocity omega0 = 0
        
        The model should include:
        - Angular position theta
        - Angular velocity omega
        - Equations of motion for a simple pendulum
        """
        
        self.generate_and_simulate("SimplePendulum", description)
    
    def run_example_rc_circuit(self):
        """Run RC circuit example"""
        description = """
        Create an RC circuit model with:
        - Resistance R = 1000 Ohms
        - Capacitance C = 0.001 Farads
        - Input voltage Vin = 5 Volts (step input)
        - Output voltage Vout across capacitor
        
        The model should solve for the voltage across the capacitor over time.
        """
        
        self.generate_and_simulate("RCCircuit", description)
    
    def generate_and_simulate(self, model_name: str, description: str):
        """
        Complete pipeline: generate, simulate, and visualize
        
        Args:
            model_name: Name for the model
            description: Model description
        """
        try:
            # Create workspace
            workspace = self.file_manager.create_workspace(
                model_name, 
                Config.WORKSPACES_DIR
            )
            logger.info(f"Working in: {workspace}")
            
            # Step 1: Generate Modelica model
            print("\n[1/6] Generating Modelica model...")
            mo_content = self.agent.generate_modelica_model(description)
            mo_file = workspace / f"{model_name}.mo"
            self.file_manager.save_file(mo_content, mo_file)
            print(f"✓ Model saved: {mo_file.name}")
            
            # Step 2: Parse model structure
            print("\n[2/6] Parsing model structure...")
            model_parser = ModelParser(mo_file)
            if model_parser.parse():
                print(f"✓ Found {len(model_parser.variables)} variables, "
                      f"{len(model_parser.equations)} equations")
            
            # Step 3: Generate simulation script
            print("\n[3/6] Generating simulation script...")
            mos_content = self.agent.generate_simulation_script(
                model_name, 
                mo_file.name
            )
            mos_file = workspace / f"simulate_{model_name}.mos"
            self.file_manager.save_file(mos_content, mos_file)
            print(f"✓ Script saved: {mos_file.name}")
            
            # Step 4: Run simulation
            print("\n[4/6] Running OpenModelica simulation...")
            success, output, mat_file = self.executor.run_simulation_script(mos_file)
            
            if not success or mat_file is None:
                print("✗ Simulation failed!")
                print(f"Output: {output}")
                
                # Try direct simulation as fallback
                print("\nTrying direct simulation...")
                success, output, mat_file = self.executor.simulate_model_direct(
                    model_name, mo_file
                )
            
            if not success or mat_file is None:
                print("✗ Simulation failed! Check the logs.")
                return
            
            print(f"✓ Simulation completed: {mat_file.name}")
            
            # Step 5: Visualize model structure
            print("\n[5/6] Generating model visualizations...")
            model_viz = ModelVisualizer(model_parser)
            
            diagram_path = Config.DIAGRAMS_DIR / f"{workspace.name}_block_diagram.png"
            model_viz.create_block_diagram(diagram_path)
            print(f"✓ Block diagram: {diagram_path.name}")
            
            dep_graph_path = Config.DIAGRAMS_DIR / f"{workspace.name}_dependencies.png"
            model_viz.create_dependency_graph(dep_graph_path)
            print(f"✓ Dependency graph: {dep_graph_path.name}")
            
            # Step 6: Visualize results
            print("\n[6/6] Generating results visualizations...")
            mat_parser = MATParser(mat_file)
            if mat_parser.load():
                results_viz = ResultsVisualizer(mat_parser)
                
                # All variables plot
                all_vars_path = Config.GRAPHS_DIR / f"{workspace.name}_all_variables.png"
                results_viz.plot_all_variables(all_vars_path)
                print(f"✓ All variables plot: {all_vars_path.name}")
                
                # Summary report
                summary_path = Config.GRAPHS_DIR / f"{workspace.name}_summary.png"
                results_viz.create_summary_report(summary_path)
                print(f"✓ Summary report: {summary_path.name}")
                
                # Print variable summary
                print("\n" + "="*80)
                print("Variable Summary:")
                print("="*80)
                summary = mat_parser.get_summary()
                for var_name, stats in list(summary.items())[:10]:
                    print(f"{var_name:25s}: "
                          f"min={stats['min']:10.4f}  "
                          f"max={stats['max']:10.4f}  "
                          f"mean={stats['mean']:10.4f}")
            
            print("\n" + "="*80)
            print("✓ COMPLETE! All outputs generated successfully.")
            print("="*80)
            print(f"\nWorkspace: {workspace}")
            print(f"Diagrams:  {Config.DIAGRAMS_DIR}")
            print(f"Graphs:    {Config.GRAPHS_DIR}")
            print("\n")
            
        except Exception as e:
            logger.exception(f"Error in pipeline: {e}")
            print(f"\n✗ Error: {e}")
            print("Check app.log for details.")

def main():
    """Main entry point"""
    try:
        app = OpenModelicaAgentApp()
        app.run_interactive()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        print(f"\nFatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()