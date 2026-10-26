from google import genai
from pydantic import BaseModel, ValidationError
import json
from google.genai import types
import electoral_data_tool


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

electoral_data_tool_function = {
    "name": "electoral_data_tool",
    "description": "Retrieves structured electoral data for the U.S. Senate midterms.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "category": {
                "type": "STRING",
                "description": "The category of data to retrieve.",
                "enum": ["national_summary", "battleground_list", "state_detail"],
            },
            "state_name": {
                "type": "STRING",
                "description": "The name of the state (required if category is 'state_detail').",
            },
        },
        "required": ["category"],
    },
}




tool = types.Tool(function_declarations=[calculator_function, electoral_data_tool_function])
config = types.GenerateContentConfig(tools=[tool], temperature=0.0)

query = "currently US is having midterm elections, i want you to help me predict who is going to win, " \
"and why are they going to win. how many seats in senate are currently competing, and what are the key " \
"battleground states? and for each state whats the percentage of voters participating out ot total us voters"

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
        print(response.content)

        if response.function_calls:
            print("Processing function calls...")
            print(response.function_calls)

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
                elif call.name == "electoral_data_tool":
                    print(f"Electoral Data Tool called with arguments: {call.arguments}")
                    args = json.loads(call.arguments)
                    result = electoral_data_tool.get_election_dataset(
                        category=args["category"],
                        state_name=args.get("state_name")
                    )
                    print(f"Electoral Data Tool result: {result}")
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=f"Electoral Data Tool result: {result}")]
                        )
                    )
                else:
                    print(f"Unknown function call: {call.name}")



if __name__ == "__main__":
    __main__()
