from google import genai
from pydantic import BaseModel, ValidationError
import json
from google.genai import types
from rich.console import Console

# Initialize the Rich console
console = Console()

client = genai.Client()

class WeatherInfo(BaseModel):
    city: str
    temperature_c: float
    condition: str
    humidity: int
    weather_summary: str

def get_weather(city: str) -> dict:
    """Fetch the current weather for a city."""
    return {
        "city": city,
        "temperature_c": 23.4,
        "condition": "Partly cloudy",
        "humidity": 58,
        "wind_kph": 12.8,
    }

prompt1 = """
fetch and display the current weather of Chicago. 
Use the weather API and display the result as JSON only, with these fields:
temperature_c, city, condition, weather_summary, and humidity.
"""

# Define the schema dictionary
get_weather_function = {
    "name": "get_weather",
    "description": "Fetch the current weather for a city.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "city": {"type": "STRING", "description": "The name of the city to fetch weather for."}
        },
        "required": ["city"]
    }
}

tool = types.Tool(function_declarations=[get_weather_function])
config = types.GenerateContentConfig(tools=[tool], temperature=0.0)

# Build the initial conversation history manually
contents = [
    types.Content(role="user", parts=[types.Part.from_text(text=prompt1)])
]

# Call generate_content (Turn 1)
console.print("[yellow]Sending initial request...[/yellow]")
response1 = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=contents,  
    config=config
)

# Check if the model asked to call a function
if response1.function_calls:
    # Append the model's function call request to the conversation history
    model_content = response1.candidates[0].content
    contents.append(model_content)
    
    result_parts = []
    for fc in response1.function_calls:
        console.print(f"[cyan]Executing tool:[/cyan] [bold]{fc.name}[/bold] with args: {fc.args}")
        
        # Run your Python function
        fc_resp_data = get_weather(**dict(fc.args))
        
        # Package the response
        function_response_part = types.Part.from_function_response(
            name=fc.name,
            response=fc_resp_data
        )
        result_parts.append(function_response_part)

    # Append the function output to history
    contents.append(
        types.Content(role="user", parts=result_parts)
    )

    # Call generate_content AGAIN with the full history (Turn 2)
    console.print("[yellow]Sending tool results back to model...[/yellow]")
    final_response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=contents,
        config=config
    )
    raw_text = final_response.text

else:
    raw_text = response1.text

# Parse and print your final output
try:
    if raw_text is None:
        raise ValueError("Model returned an empty text response.")
        
    clean_json = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(clean_json)
    weather_info = WeatherInfo.model_validate(data)
    
    console.print("\n[green][bold]--- Final JSON Output ---[/bold][/green]")
    console.print(weather_info.model_dump_json(indent=2))
    
except (json.JSONDecodeError, ValueError) as e:
    console.print(f"[red]Model output was not valid JSON. Raw text was:[/red]\n{raw_text}")
except ValidationError as e:
    console.print(f"[red]Output did not match schema:[/red]\n{e}")