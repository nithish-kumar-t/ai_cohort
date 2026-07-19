import subprocess
import sys
from rich.console import Console
from sympy import content
from google import genai

console = Console()
client = genai.Client()

def observe():
    console.print("Running num-test.py...\n")
    content = ""

    with open("num-test.py", "r") as file:
        content = file.read()

    result = subprocess.run(
        [sys.executable, "num-test.py"],
        capture_output=True,
        text=True,
        check=False
    )
    output = result.stdout
    error_output = result.stderr

    console.print("Contents of num-test.py:")
    console.print(content)
    console.print("Output is:")
    console.print(output if output else error_output)

    if (error_output):
        return (content, error_output)
    else:
        return (content, None)


def think(code, error):
    prompt = (
        "You are an expert Python developer fixing a script. "
        "I will provide the code and the error it produced. "
        "You must return ONLY the fully corrected python code. "
        "Do NOT include any conversational text. Do NOT use markdown formatting or backticks (```). "
        "Just output the raw code.\n\n"
        f"Code:\n{code}\n\n"
        f"Error:\n{error}"
    )
    contents = [
        {"role": "user", "parts": [{"text": prompt}]}
    ]
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=contents
    )
    console.print("[green]Model's response:[/green]")
    corrected_code = response.text.strip()
    
    if corrected_code.startswith("```python"):
        corrected_code = corrected_code[9:] # Remove '```python'
    elif corrected_code.startswith("```"):
        corrected_code = corrected_code[3:] # Remove '```'
        
    if corrected_code.endswith("```"):
        corrected_code = corrected_code[:-3] # Remove ending '```'
    
    console.print(corrected_code)
        
    return corrected_code.strip()


def act(new_content):
    with open("num-test.py", "w", encoding="utf-8") as file:
        file.write(new_content)
    console.print("[green]Updated num-test.py with new content.[/green]")


def orchestrate():
    num_iterations = 3
    for i in range(num_iterations):
        console.print(f"[yellow]Iteration {i + 1}/{num_iterations}[/yellow]")
        code, err = observe()
        if err:
            corrected_code = think(code, err)
            act(corrected_code) 
        else:
            console.print("[green]No errors detected. Exiting.[/green]")
            break


if __name__ == "__main__":
    orchestrate()