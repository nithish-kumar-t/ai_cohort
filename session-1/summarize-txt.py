import json
import time

from google import genai
from pydantic import BaseModel, Field, ValidationError


class PlanDay(BaseModel):
    day: int = Field(ge=1)
    activities: list[str]


class Itinerary(BaseModel):
    destination: str
    trip_duration_days: int = Field(gt=0)
    budget_category: str
    top_attractions: list[str]
    daily_plan: list[PlanDay]


def main() -> None:
    start_time = time.perf_counter()
    from_city = "Chicago"
    to_city = "Paris"

    prompt = (
        f"Create a 3-day, 2-night travel itinerary from {from_city} to {to_city}. "
        "Return only a JSON object matching this schema:\n"
        f"{json.dumps(Itinerary.model_json_schema())}"
    )

    client = genai.Client()
    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    end_time = time.perf_counter()

    try:
        itinerary = Itinerary.model_validate_json(interaction.output_text)
    except ValidationError as exc:
        print(interaction.output_text)
        raise ValueError("The model returned an invalid itinerary") from exc

    print(itinerary.model_dump_json(indent=2))

    print(f"Execution time: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()
