# Fact-Checking Agent

This is a starter implementation for a fact-checking agent that queries multiple LLM opinions and uses majority voting to decide whether a claim is supported, refuted, or unverified.

## Design

1. Collect opinions from three LLMs.
2. Normalize each response into one of:
   - `SUPPORTS`
   - `REFUTES`
   - `UNVERIFIED`
3. Apply majority voting:
   - If 2 or more models agree, return that verdict.
   - If all three disagree, return `UNVERIFIED`.
4. Return the final decision plus each model's reasoning.

## Why this helps

Using multiple models helps reduce bias and overconfidence from a single source. It is still not a guarantee of truth, but it improves robustness by comparing independent outputs.

## File structure

- `fact_checker.py` — core logic for querying LLMs and majority voting.
- `requirements.txt` — minimal dependencies.

## Usage

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Set your API key(s):

```bash
export OPENAI_API_KEY="your-openai-key"
```

3. Run the script with a claim:

```bash
python3 fact_checker.py "The Eiffel Tower is in Berlin."
```

## Notes

- The current implementation uses OpenAI by default.
- You can add additional providers by extending the `LLMProvider` abstraction.
- If the models do not reach a consensus, the system returns `UNVERIFIED`.
- For a production system, add retrieval from trusted sources and source citation.
