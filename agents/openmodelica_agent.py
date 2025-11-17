"""
OpenModelica AI Agent - Uses Azure OpenAI to generate Modelica models
"""
import os
from typing import Optional
from openai import AzureOpenAI
from agents.base_agent import BaseAgent
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class OpenModelicaAgent(BaseAgent):
    """Agent that uses Azure OpenAI to generate Modelica code"""
    
    def __init__(self):
        """Initialize OpenModelica Agent"""
        super().__init__("OpenModelicaAgent")
        print("[DEBUG] Initializing OpenModelicaAgent...")
        
        # Initialize Azure OpenAI client
        try:
            print(f"[DEBUG] Azure endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
            print(f"[DEBUG] Azure deployment: {Config.AZURE_OPENAI_DEPLOYMENT}")
            print(f"[DEBUG] API version: {Config.AZURE_OPENAI_API_VERSION}")
            
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
            print("[OK] Azure OpenAI client initialized successfully")
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            print(f"[FAIL] Failed to initialize Azure OpenAI: {e}")
            logger.error(f"Failed to initialize Azure OpenAI: {e}")
            self.client = None
    
    def _call_azure_openai(self, prompt: str, max_tokens: int = None) -> Optional[str]:
        """
        Call Azure OpenAI API
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens for response
            
        Returns:
            Response text or None if failed
        """
        if not self.client:
            print("[FAIL] Azure OpenAI client not initialized")
            logger.error("Azure OpenAI client not initialized")
            return None
        
        try:
            max_tokens = max_tokens or Config.MAX_TOKENS
            print(f"[DEBUG] Calling Azure OpenAI API...")
            print(f"[DEBUG] Model: {Config.AZURE_OPENAI_DEPLOYMENT}")
            print(f"[DEBUG] Max tokens: {max_tokens}")
            print(f"[DEBUG] Prompt length: {len(prompt)} chars")
            
            response = self.client.chat.completions.create(
                model=Config.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Modelica model designer. Generate syntactically correct Modelica code that simulates physical systems."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=Config.MODEL_TEMPERATURE,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            
            result = response.choices[0].message.content
            print(f"[OK] Received response from Azure OpenAI ({len(result)} chars)")
            logger.info("Successfully received response from Azure OpenAI")
            return result
            
        except Exception as e:
            print(f"[FAIL] Azure OpenAI API call failed: {e}")
            logger.error(f"Azure OpenAI API call failed: {e}")
            return None
    
    def generate_modelica_model(self, description: str) -> str:
        """
        Generate a Modelica model from a natural language description
        
        Args:
            description: Natural language description of the model
            
        Returns:
            Generated Modelica code as string
        """
        logger.info("Generating Modelica model from description...")
        
        prompt = f"""Create a SIMPLE Modelica model based on this description:

{description}

STRICT REQUIREMENTS - MUST FOLLOW:
1. Create ONLY a continuous differential equation model
2. NO algorithm sections, NO when/then/else statements, NO discrete events
3. NO external library imports whatsoever
4. Use ONLY: parameter Real, Real, equation, der(), basic math (+, -, *, /, ^, sqrt, sin, cos, etc.)
5. Number of equations MUST EQUAL number of unknown variables (not counting parameters)
6. Only use continuous equations with der() for time derivatives

EXAMPLE FORMAT (follow exactly):
model Example
  parameter Real param1 = 1.0 "First parameter";
  parameter Real param2 = 2.0 "Second parameter";
  Real state1(start=0.0) "State variable 1";
  Real state2(start=0.0) "State variable 2";
equation
  der(state1) = state2;
  der(state2) = -param1*state1 - param2*state2;
end Example;

GUIDELINES:
- If input is mentioned (like step voltage), make it a constant parameter
- All differential equations should use der() only
- Variables with der() are state variables (integrate-able)
- Non-differential equations must describe relationships between variables
- Keep equations simple and physically meaningful
- Always balance variables with equations

Output ONLY the Modelica code, nothing else.
No markdown, no backticks, no explanations - just the code starting with 'model' and ending with 'end ModelName;'
"""
        
        response = self._call_azure_openai(prompt, max_tokens=1500)
        
        if response:
            print(f"[DEBUG] Cleaning up response ({len(response)} chars before cleanup)...")
            # Clean up response (remove markdown code blocks if present)
            response = response.strip()
            print(f"[DEBUG] After strip: {len(response)} chars")
            
            if response.startswith("```"):
                print("[DEBUG] Removing markdown code blocks...")
                response = response.split("```")[1]
                if response.startswith("modelica"):
                    print("[DEBUG] Removing 'modelica' language tag...")
                    response = response[9:].strip()
                response = response.strip()
            
            # Remove any leftover code block markers and language tags
            cleanup_iterations = 0
            while response.startswith("model\n") and response.count("model") > 1:
                cleanup_iterations += 1
                print(f"[DEBUG] Cleanup iteration {cleanup_iterations}: removing duplicate 'model' keyword...")
                first_line = response.split('\n')[0]
                if first_line.strip() == "model":
                    response = '\n'.join(response.split('\n')[1:])
                else:
                    break
            
            print(f"[OK] Model generation successful ({len(response)} chars final)")
            self.add_to_history(f"Generate model: {description[:100]}...", response[:200])
            logger.info("Model generation successful")
            return response
        else:
            logger.error("Failed to generate model")
            return "model FailedModel\nend FailedModel;"
    
    def generate_simulation_script(self, model_name: str, mo_file_name: str) -> str:
        """
        Generate a simulation script for a Modelica model
        
        Args:
            model_name: Name of the model
            mo_file_name: Name/path of the .mo file
            
        Returns:
            Generated simulation script (.mos) as string
        """
        logger.info(f"Generating simulation script for {model_name}...")
        
        # Convert Windows backslashes to forward slashes for OpenModelica compatibility
        mo_file_path = str(mo_file_name).replace("\\", "/")
        
        # Create a simple, direct script without relying on AI to format paths correctly
        # This avoids issues with backslashes in Windows paths being treated as escape sequences
        script = f'loadFile("{mo_file_path}");\n'
        script += f'simulate({model_name}, startTime=0, stopTime=10, numberOfIntervals=500);\n'
        script += 'getErrorString();\n'
        
        logger.info("Script generation successful")
        self.add_to_history(f"Generate script: {model_name}", script[:200])
        return script
    
    def enhance_model(self, current_model: str, enhancement: str) -> str:
        """
        Enhance an existing Modelica model with additional features
        
        Args:
            current_model: Current Modelica model code
            enhancement: Description of enhancement
            
        Returns:
            Enhanced Modelica model code
        """
        logger.info("Enhancing model...")
        
        prompt = f"""
Enhance this Modelica model with the following requirement:

Requirement: {enhancement}

Current Model:
```
{current_model}
```

Provide the enhanced Modelica code that:
1. Maintains all existing functionality
2. Adds the new feature as requested
3. Keeps proper syntax and structure
4. Includes comments for new additions

Output ONLY the enhanced Modelica code, no additional text.
"""
        
        response = self._call_azure_openai(prompt, max_tokens=3000)
        
        if response:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("modelica"):
                    response = response[9:]
                response = response.strip()
            
            self.add_to_history(f"Enhance model: {enhancement[:50]}...", response[:200])
            logger.info("Model enhancement successful")
            return response
        else:
            logger.error("Failed to enhance model")
            return current_model
    
    def explain_model(self, model_code: str) -> str:
        """
        Generate an explanation of what a Modelica model does
        
        Args:
            model_code: Modelica model code
            
        Returns:
            Explanation of the model
        """
        logger.info("Generating model explanation...")
        
        prompt = f"""
Provide a clear, technical explanation of this Modelica model:

```
{model_code}
```

Include:
1. What physical system it simulates
2. The main variables and parameters
3. The equations and their physical meaning
4. Assumptions and limitations
5. Typical use cases

Be concise but comprehensive.
"""
        
        response = self._call_azure_openai(prompt, max_tokens=1500)
        
        if response:
            self.add_to_history(f"Explain model", response[:200])
            logger.info("Model explanation generated")
            return response
        else:
            logger.error("Failed to generate explanation")
            return "Failed to generate explanation"
    
    def process(self, input_data: str) -> str:
        """
        Process input using the agent
        
        Args:
            input_data: Input string
            
        Returns:
            Response string
        """
        logger.info(f"Processing: {input_data[:100]}...")
        
        # Simple processing - can be extended for more complex logic
        if "generate" in input_data.lower():
            return self.generate_modelica_model(input_data)
        else:
            return self._call_azure_openai(input_data) or "Failed to process input"
