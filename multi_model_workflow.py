import os
import sys
import openai
import anthropic
from dotenv import load_dotenv

"""
multi_model_workflow.py

This script demonstrates a 2-step coding workflow:
1) Claude (Anthropic) for initial code generation
2) ChatGPT (OpenAI) for review/refinement

Usage:
    python multi_model_workflow.py "Your prompt here"
"""

def main():
    # Load environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY)
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not openai.api_key or not anthropic_api_key:
        print("ERROR: Missing API keys. Please set them in .env or environment variables.")
        sys.exit(1)

    # Check command-line args
    if len(sys.argv) < 2:
        print("Usage: python multi_model_workflow.py \"Your prompt here\"")
        sys.exit(0)

    user_prompt = sys.argv[1]

    # 1) Send to Claude for initial code generation
    claude_response = claude_generate(anthropic_api_key, user_prompt)

    # 2) Send to ChatGPT for review & refinement
    final_code = chatgpt_refine(openai.api_key, claude_response)

    # Output final combined code
    print("\n=== Claude's Initial Code ===")
    print(claude_response)
    print("\n=== ChatGPT's Refined Code ===")
    print(final_code)
    print("\nDone. You can now review this output and optionally commit it to the repository.")


def claude_generate(anthropic_api_key, prompt):
    """
    Calls Claude 3.7 Sonnet (or Claude Code) for initial code generation.
    Adjust the model ID as needed, e.g. 'claude-2', 'claude-instant-1'.
    """
    client = anthropic.Client(anthropic_api_key)
    claude_model = "claude-2"  # or the correct ID for "3.7 Sonnet"
    claude_prompt = f"{anthropic.HUMAN_PROMPT}Please generate Python or Java code for:\n\n{prompt}\n{anthropic.AI_PROMPT}"
    resp = client.completion(
        prompt=claude_prompt,
        model=claude_model,
        max_tokens_to_sample=1024,
        temperature=0.7,
    )
    return resp["completion"]


def chatgpt_refine(openai_api_key, initial_code):
    """
    Sends the code from Claude to ChatGPT (model 'o1') for review/refinement.
    If 'o1' is not recognized, you might specify model='gpt-4' or 'gpt-3.5-turbo'.
    """
    model_name = "gpt-4"  # or 'o1' if that is recognized by your deployment

    messages = [
        {
            "role": "system",
            "content": "You are a coding expert. Improve and correct the provided code."
        },
        {
            "role": "user",
            "content": f"Here is the code from Claude:\n\n{initial_code}\n\nPlease refine it."
        }
    ]
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=messages,
        temperature=0.3
    )
    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    main()
