# multi-llm-workflow

This repository demonstrates a Python script that orchestrates **Claude** (3.7 Sonnet) and **ChatGPT** (model o1) to collaboratively generate and refine code.

## How It Works

1. **User** inputs a coding prompt.
2. **Claude** (Anthropic) provides the initial code and explanation.
3. **ChatGPT** (OpenAI) reviews and refines it.
4. Final code is shown to the user, who can commit changes back to GitHub.

See [multi_model_workflow.py](multi_model_workflow.py) for usage instructions.
