import json
import os
import types
from certifi import contents
from google import genai

from rich.console import Console


client = genai.Client()

CHECKPOINT_FILE = "checkpoint.json"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

task = "Design a URL shortening service like bit.ly. "
"The service should allow users to input a long URL and receive a shortened version. "
"The shortened URL should redirect to the original long URL when accessed. "
"Additionally, the service should track the number of times each shortened URL is accessed."


SYSTEM_PROMPT = """
    You are an expert software engineer. Your task is to design a URL shortening service like bit.ly.

"""

STEPS = [
    {
        "step_id": 1,
        "name": "Requirements & Scope Definition",
        "description": "Define functional requirements (URL creation, redirection, custom aliases, expiration) and non-functional requirements (high availability, low latency, 100:1 read/write ratio). Estimate storage and throughput requirements.",
    },
    {
        "step_id": 2,
        "name": "Encoding Strategy & ID Generation",
        "description": "Determine the short key generation strategy (e.g., Base62 encoding of an auto-incrementing integer or MD5 hash truncation with collision handling). Calculate key length requirements for target capacity.",
    },
    {
        "step_id": 3,
        "name": "Database & Data Model Design",
        "description": "Design the database schema for mappings (long URL, short code, user ID, creation timestamp, expiration) and analytics. Select appropriate storage solutions (SQL vs. NoSQL) and caching strategies (Redis/Memcached).",
    },
    {
        "step_id": 4,
        "name": "API Design & Specification",
        "description": "Specify RESTful API endpoints for creating short links (`POST /api/v1/shorten`), expanding/redirecting URLs (`GET /{short_code}`), and fetching analytics (`GET /api/v1/analytics/{short_code}`). Include request/response formats and status codes.",
    },
    {
        "step_id": 5,
        "name": "Core Service Logic Implementation",
        "description": "Write the core application logic handling short URL creation, cache checks, database persistence, HTTP 301/302 redirect generation, and custom alias validation.",
    },
    {
        "step_id": 6,
        "name": "Rate Limiting & Security Policies",
        "description": "Design and implement protection mechanisms against abuse, including API rate limiting (sliding window/token bucket via Redis), input validation, and malicious URL detection hooks.",
    },
    {
        "step_id": 7,
        "name": "Testing & Validation",
        "description": "Create unit and integration test suites covering key generation, HTTP redirects, collision handling, expired links, and API validation error cases.",
    }
]

MODEL="gemini-3.1-flash-lite"
console = Console()

def run_agent(reset = False):
    if (reset):
        delete_checkpoint_info()
    # loaded checkpoint info
    checkpoint_info = load_checkpoint_info()
    console.print(f"[blue]Loaded checkpoint info: {checkpoint_info}[/blue]")

    current_step = checkpoint_info.get("current_step", 0)
    completed_steps = checkpoint_info.get("completed_steps", [])

    for i in range(0, len(STEPS)):
        if i < current_step:
            console.print(f"[green]Step {STEPS[i]['step_id']} already completed. Skipping...[/green]")
            completed_steps.append(completed_steps[i])
            continue
        step = STEPS[i]
        console.print(f"[blue]Executing Step {step['step_id']}: {step['name']}[/blue]")
        console.print(f"[yellow]{step['description']}[/yellow]")

        prompt = SYSTEM_PROMPT + f"Task: {task}\nStep Description: {step['description']}"
        response = call_model(prompt)

        checkpoint_step_info = {
            "step_id": step['step_id'],
            "name": step['name'],
            "prompt": prompt,
            "response": response
        }

        completed_steps.append(checkpoint_step_info)
        current_step += 1
        update_checkpoint_info(current_step, completed_steps)
        console.print(f"[green]Step {step['step_id']} completed.[/green]\n")


def load_checkpoint_info():
    DEFAULT_CHECKPOINT = {
        "current_step": 0,
        "completed_steps": []
    }

    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # File exists but is empty (0 bytes) or invalid JSON.
            # Overwrite it with default state and return the default.
            update_checkpoint_info(DEFAULT_CHECKPOINT["current_step"], DEFAULT_CHECKPOINT["completed_steps"])
            return DEFAULT_CHECKPOINT
    else:
        return DEFAULT_CHECKPOINT

def update_checkpoint_info(current_step, completed_steps):
    checkpoint_info = {
        "current_step": current_step,
        "completed_steps": completed_steps
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint_info, f, indent=4)

def delete_checkpoint_info():
    DEFAULT_CHECKPOINT = {
        "current_step": 0,
        "completed_steps": []
    }
    # Always write valid JSON instead of truncating to 0 bytes
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(DEFAULT_CHECKPOINT, f, indent=4)


def call_model(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text.strip()



run_agent(reset = False)