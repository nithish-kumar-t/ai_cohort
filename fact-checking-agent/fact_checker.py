from google import genai
from pydantic import BaseModel, ValidationError
import json
from google.genai import types

client = genai.Client()

class PlanDay(BaseModel):
    day: int
    activities: list[str]

class WeatherInfo(BaseModel):
    city: str
    temperature_c: float
    condition: str
    humidity: int
    weather_summary: str

class Itinerary(BaseModel):
    destination: str
    trip_duration_days: int
    budget_category: str
    top_attractions: list[str]
    daily_plan: list[PlanDay]

prompt = """
Generate a travel itinerary as JSON only, with these fields:
destination, trip_duration_days, budget_category,
top_attractions, daily_plan.
Each daily_plan item should include day and activities.
"""

prompt1="""fetch and display the current weather of Chicago Use weather API and display the result as JSON only, with these fields:
format with fields: temperature_c, city, condition, weather_summary, and humidity.
"""

def get_weather(city: str) -> dict:
    """Fetch the current weather for a city."""
    return {
        "city": city,
        "temperature_c": 23.4,
        "condition": "Partly cloudy",
        "humidity": 58,
        "wind_kph": 12.8,
    }


def get_weather(city: str) -> dict:
    """Fetch the current weather for a city."""
    return {
        "city": city,
        "temperature_c": 23.4,
        "condition": "Partly cloudy",
        "humidity": 58,
        "wind_kph": 12.8,
    }


get_weather_function = {
    "name": "get_weather",
    "description": "Fetch the current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "The name of the city to fetch weather for."}
        },
        "required": ["city"]
    }
}

tools = types.Tools(
    functions=[get_weather_function]
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt1,
    config=types.GenerateContentConfig(
        tools=[tools],
        temperature=0.0
    )
)

try:
    data = json.loads(response.text)
    weather_info = WeatherInfo.model_validate(data)
    print(weather_info.model_dump_json(indent=2))
except json.JSONDecodeError:
    print("Model output was not valid JSON")
except ValidationError as e:
    print("Output did not match schema:", e)