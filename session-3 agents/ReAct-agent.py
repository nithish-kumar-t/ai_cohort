from google import genai
from pydantic import BaseModel, ValidationError
import json
from google.genai import types


client = genai.Client()


SYSTEM_PROMPT = """You are a ReAct agent. You should follow the ReAct framework, 
reasoning step by step and taking actions based on observations.
"""

MAX_ITR = 100

def search():
    pass

def calculator(a, b, operation):
    return eval(f"{a} {operation} {b}")



calculator_function = {
    "name": "calculator",
    "description": "Performs a basic arithmetic operation between two numbers.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "a": {"type": "NUMBER", "description": "The first number."},
            "b": {"type": "NUMBER", "description": "The second number."},
            "operation": {
                "type": "STRING",
                "description": "The arithmetic operator to use.",
                "enum": ["+", "-", "*", "/"],
            },
        },
        "required": ["a", "b", "operation"],
    },
}




tool = types.Tool(function_declarations=[calculator_function])
config = types.GenerateContentConfig(tools=[tool], temperature=0.0)

query = "currently US is having midterm elections, i want you to help me predict who is going to win, and why are they going to win" \
    "how many seats in senate are currently competing, and what are the key battleground states? and for each state whats the percentage of voters participating out ot total us voters"

contents = [
    types.Content(role="user", parts=[types.Part.from_text(text=query)])
]


def __main__():
    #Start the ReAct agent loop here

    for itr in range(MAX_ITR):
        print(f"Iteration {itr} :", contents[-1].parts[0].text if contents else "No content")
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=contents,  
            config=config
        )
        print(response.candidates)

        if response.function_calls:
            for call in response.function_calls:
                print(call)
                if call.name == "calculator":
                    print(f"Calculator called with arguments: {call.arguments}")
                    args = json.loads(call.arguments)
                    result = calculator(args["a"], args["b"], args["operation"])
                    print(f"Calculator result: {result}")
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=f"Calculator result: {result}")]
                        )
                    )



if __name__ == "__main__":
    __main__()
