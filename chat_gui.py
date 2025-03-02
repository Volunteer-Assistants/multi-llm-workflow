import os
import anthropic
import openai
from dotenv import load_dotenv
import gradio as gr

# Load .env if present
load_dotenv()

# Grab keys from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Make sure keys exist
if not ANTHROPIC_API_KEY:
    raise ValueError("Missing ANTHROPIC_API_KEY environment variable.")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable.")

# Configure each API client
openai.api_key = OPENAI_API_KEY
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Model names
# Claude 3.7 Sonnet => "claude-3-7-sonnet-20250219"
# GPT-4o => "o1"
CLAUDE_MODEL = "claude-3-7-sonnet-20250219"
CHATGPT_MODEL = "o1"

def combine_llms(user_prompt, history):
    """
    1) Claude 3.7 Sonnet produces an initial response.
    2) GPT-4o (o1) refines that response.
    3) Return the combined text.
    """

    # 1) Ask Claude (Anthropic)
    claude_prompt = f"{anthropic.HUMAN_PROMPT}{user_prompt}\n{anthropic.AI_PROMPT}"
    claude_response = anthropic_client.completions.create(
        model=CLAUDE_MODEL,
        prompt=claude_prompt,
        max_tokens_to_sample=800,
        temperature=0.7,
    )
    claude_text = claude_response.completion.strip()

    # 2) Ask ChatGPT (o1) to refine Claude's output
    chatgpt_messages = [
        {"role": "system", "content": "You are a coding expert. Refine or correct the given text/code."},
        {"role": "user", "content": f"Claude said:\n\n{claude_text}\n\nPlease refine/correct/improve."}
    ]
    chatgpt_response = openai.ChatCompletion.create(
        model=CHATGPT_MODEL,
        messages=chatgpt_messages,
        temperature=0.3
    )
    chatgpt_text = chatgpt_response["choices"][0]["message"]["content"].strip()

    # Combine them in final output
    combined_text = (
        f"**Claude (3.7 Sonnet) Output**:\n\n{claude_text}\n\n"
        f"**GPT-4o (o1) Refinement**:\n\n{chatgpt_text}"
    )
    return combined_text

def chat_interface(user_message, chat_history):
    """
    Gradio chat function. 
    user_message: new message from user
    chat_history: list of (user, ai) messages so far
    """
    # 1) For now, we ignore full chat history in the prompt. 
    #    We just send the new user_message to combine_llms.

    # 2) Get the combined output from Claude -> ChatGPT
    response = combine_llms(user_message, chat_history)

    # 3) Update chat_history
    #    The chat_history is a list of tuples (user_str, ai_str)
    chat_history.append((user_message, response))

    # Return the updated chat_history to display
    return "", chat_history

# Build the Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# Multi-LLM Workflow (Claude 3.7 Sonnet + GPT-4o)")
    chatbot = gr.Chatbot(
        label="Claude + ChatGPT Conversation",
        elem_id="chatbot",
        type='tuples'   # to silence "type='messages'" warning
    )
    msg = gr.Textbox(label="Enter your prompt here")
    clear = gr.Button("Clear Chat")

    def clear_history():
        return []

    msg.submit(chat_interface, [msg, chatbot], [msg, chatbot])
    clear.click(fn=clear_history, inputs=[], outputs=[chatbot])

# Launch with a local URL
if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
