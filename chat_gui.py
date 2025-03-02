import os
import time
import sys
from anthropic import Anthropic, AuthenticationError, APIError, RateLimitError
from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr

"""
chat_gui.py

This script provides a web-based chat interface for the multi-LLM workflow:
1) Claude (Anthropic) for initial response generation
2) ChatGPT (OpenAI) for refinement
3) Display both in a clean, user-friendly interface

Usage:
    python chat_gui.py
"""

# Load .env if present
load_dotenv()

# Grab keys from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Make sure keys exist
if not ANTHROPIC_API_KEY:
    print("ERROR: Missing ANTHROPIC_API_KEY environment variable.")
    print("Make sure to create a .env file with your API keys.")
    sys.exit(1)
if not OPENAI_API_KEY:
    print("ERROR: Missing OPENAI_API_KEY environment variable.")
    print("Make sure to create a .env file with your API keys.")
    sys.exit(1)

# Model names (customizable)
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
CHATGPT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")  # or "o1" for GPT-4o

# Initialize API clients
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def claude_generate(prompt):
    """
    Get a response from Claude using the newer Messages API
    with retry logic and error handling
    """
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Using the Messages API (preferred over the older Completion API)
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=800,
                temperature=0.7,
                system="You are an expert assistant with deep knowledge in coding, technical topics, and creative tasks.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the text content from the response
            return response.content[0].text
            
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"Claude API rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return "⚠️ Error: Claude API rate limit exceeded. Please try again later."
        except AuthenticationError:
            return "⚠️ Error: Claude API authentication failed. Please check your API key."
        except APIError as e:
            return f"⚠️ Error with Claude API: {str(e)}"
        except Exception as e:
            return f"⚠️ Unexpected error with Claude API: {str(e)}"

def chatgpt_refine(claude_text):
    """
    Send Claude's output to ChatGPT for refinement
    with retry logic and error handling
    """
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = openai_client.chat.completions.create(
                model=CHATGPT_MODEL,
                temperature=0.3,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a coding expert. Refine or correct the given text/code while maintaining the core ideas. Improve clarity, accuracy, and implementation details."
                    },
                    {
                        "role": "user", 
                        "content": f"Claude said:\n\n{claude_text}\n\nPlease refine/correct/improve."
                    }
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"OpenAI API error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return f"⚠️ Error with OpenAI API: {str(e)}"

def combine_llms(user_prompt, history=None):
    """
    1) Claude 3.7 Sonnet produces an initial response.
    2) GPT-4 refines that response.
    3) Return the combined text.
    """
    # Show status message
    progress_message = "⏳ Generating responses from Claude and ChatGPT... (this may take a moment)"
    yield progress_message
    
    # 1) Ask Claude (Anthropic)
    claude_text = claude_generate(user_prompt)
    if claude_text.startswith("⚠️ Error"):
        yield claude_text
        return
    
    # 2) Ask ChatGPT to refine Claude's output
    chatgpt_text = chatgpt_refine(claude_text)
    if chatgpt_text.startswith("⚠️ Error"):
        yield f"Claude's response:\n\n{claude_text}\n\n{chatgpt_text}"
        return

    # Combine them in final output
    combined_text = (
        f"**Claude ({CLAUDE_MODEL.split('-')[2].capitalize()}) Output**:\n\n{claude_text}\n\n"
        f"**ChatGPT Refinement**:\n\n{chatgpt_text}"
    )
    yield combined_text

def chat_interface(user_message, chat_history):
    """
    Gradio chat function. 
    user_message: new message from user
    chat_history: list of (user, ai) messages so far
    """
    # Update chat history with the user message immediately
    chat_history.append((user_message, ""))
    yield "", chat_history
    
    # Generate responses
    bot_message = ""
    for message in combine_llms(user_message, chat_history):
        # Update the last message
        bot_message = message
        chat_history[-1] = (user_message, bot_message)
        yield "", chat_history

# Build the Gradio UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Multi-LLM Workflow: Claude + ChatGPT")
    gr.Markdown("""
    This interface demonstrates a workflow that combines two large language models:
    - **Claude** generates the initial response
    - **ChatGPT** refines and improves that response
    
    Both responses are shown for comparison.
    """)
    
    chatbot = gr.Chatbot(
        label="Claude + ChatGPT Conversation",
        elem_id="chatbot",
        bubble_full_width=False,
        height=500,
        avatar_images=(None, "🤖")
    )
    
    with gr.Row():
        msg = gr.Textbox(
            label="Enter your prompt here",
            placeholder="Ask a question or describe a coding task...",
            lines=3,
            max_lines=10,
            show_label=False,
            container=False
        )
        submit_btn = gr.Button("Submit", variant="primary")
    
    with gr.Row():
        clear = gr.Button("Clear Chat")
        model_info = gr.Markdown(f"**Models:** Claude = `{CLAUDE_MODEL}` | ChatGPT = `{CHATGPT_MODEL}`")

    def clear_history():
        return []

    msg.submit(chat_interface, [msg, chatbot], [msg, chatbot])
    submit_btn.click(chat_interface, [msg, chatbot], [msg, chatbot])
    clear.click(fn=clear_history, inputs=[], outputs=[chatbot])

    gr.Markdown("""
    ## Tips for Effective Prompting
    - Be specific and detailed in your requests
    - For code generation, specify the language and any requirements
    - For creative tasks, provide context and examples
    """)

# Launch with a local URL
if __name__ == "__main__":
    print(f"Starting Multi-LLM Chat GUI with Claude ({CLAUDE_MODEL}) and ChatGPT ({CHATGPT_MODEL})")
    print("Access the web interface at http://127.0.0.1:7860")
    demo.queue().launch(server_name="127.0.0.1", server_port=7860, share=False)