
from google import genai
from rich.console import Console
import subprocess
import os

console = Console()

class PatchAgent:
    def __init__(self):
        self. model="gemini-3.1-flash-lite"
        self.client = genai.Client()

    def analyze_file (self, file_path):
        console.print(f"[blue]Analyzing file: {file_path}[/blue]")
        with open(file_path, "r") as file:
            code = file.read()

        result = subprocess.run(
            ["python3", file_path],
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stdout
        error_output = result.stderr

        if error_output:
            console.print(f"[red]Error detected in {file_path}:[/red]")
            console.print(error_output)
        else:
            console.print(f"[green]No errors detected in {file_path}.[/green]")
            console.print(f"[green]Output:[/green]\n{output}")
        
        return code, output, error_output

    def prompt(self, code, error):
        prompt =  f"""You are an expert Python developer fixing a script. 
            I will provide the code and the error it produced. 
            You must return ONLY the diff of the fully corrected python code.
            Do NOT include any conversational text. Do NOT use markdown formatting or backticks (```).

            You must use standard git diff headers. Here is an example of the exact format required:

            --- a/num-test.py
            +++ b/num-test.py
            @@ -1,5 +1,6 @@
            def observe():
                console.print("Running num-test.py...\\n")
            -    content = ""
            +    # Here is the fix
            +    content = "New content"

            Code:
            {code}

            Error:
            {error} """

        return prompt
    
    def generate_patch(self, code, error):
        prompt = self.prompt(code, error)
        contents = [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents
        )
        console.print("[green]Model's response:[/green]")
        patch = response.text.strip()
        
        if patch.startswith("```diff"):
            patch = patch[8:] # Remove '```diff'
        elif patch.startswith("```"):
            patch = patch[3:] # Remove '```'
            
        if patch.endswith("```"):
            patch = patch[:-3] # Remove ending '```'
        
        console.print(patch)
            
        return patch.strip()
    
    def apply_patch(self, code, patch, file_path):
        target_dir = os.path.dirname(os.path.abspath(file_path))

        result = subprocess.run(
            ["git", "apply", "-"], 
            input=patch,
            text=True,
            capture_output=True,
            check=False,
            cwd = target_dir
        )

        if result.stderr:
            console.print("[red]Error applying patch:[/red]")
            console.print(result.stderr)
            return code, result.stderr
        else:
            console.print("[green]Patch applied successfully.[/green]")
            return code, None
        

if __name__ == "__main__":
    agent = PatchAgent()
    num_of_iterations = 3  # Set the number of iterations you want to run

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "num-test.py")

    console.print(f"[blue]Starting analysis for {file_path}[/blue]")

    for itr in range(num_of_iterations):
        console.print(f"[blue]Iteration {itr + 1} of {num_of_iterations}[/blue]")
        code, output, error_output = agent.analyze_file(file_path)

        if error_output:
            patch = agent.generate_patch(code, error_output)
            updated_code, apply_error = agent.apply_patch(code, patch, file_path)
            if apply_error:
                console.print("[red]Failed to apply the patch.[/red]")
                break
            else:
                console.print("[green]Patch applied successfully. Updated code:[/green]")
                console.print(updated_code)
        else:
            console.print("[green]No errors detected. No patch needed.[/green]")