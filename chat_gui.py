import os
import time
import sys
from openai import OpenAI  # Modern OpenAI client
from anthropic import Anthropic, AuthenticationError, APIError, RateLimitError
from dotenv import load_dotenv
import gradio as gr

"""
chat_gui.py

This script provides a web-based chat interface where Claude and ChatGPT
talk directly to each other in a conversational format.

Usage:
    python chat_gui.py
"""

# Load .env if present
load_dotenv()

# Grab keys and configuration from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check for API keys
if not ANTHROPIC_API_KEY:
    print("ERROR: Missing ANTHROPIC_API_KEY environment variable.")
    print("Make sure to create a .env file with your API keys.")
    sys.exit(1)
if not OPENAI_API_KEY:
    print("ERROR: Missing OPENAI_API_KEY environment variable.")
    print("Make sure to create a .env file with your API keys.")
    sys.exit(1)

# Get model names from environment variables with defaults
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

print(f"Using Claude model: {CLAUDE_MODEL}")
print(f"Using OpenAI model: {OPENAI_MODEL}")

# Initialize API clients using modern formats
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)  # Modern OpenAI client

def claude_generate(prompt, task_description):
    """
    Get a response from Claude using the Messages API with a conversational tone
    where Claude addresses ChatGPT directly
    """
    max_retries = 3
    retry_delay = 2
    
    claude_system_prompt = f"""
    You are Claude, an AI assistant by Anthropic. You'll be collaborating with ChatGPT (by OpenAI) 
    to help solve the user's request.
    
    Address ChatGPT directly in your response, like you're having a conversation with a colleague.
    First, analyze the user's request: {task_description}
    
    Then generate a response that:
    1. Briefly introduces yourself to ChatGPT
    2. Outlines your approach to solving the user's request
    3. Provides your implementation, code, or answer
    4. IMPORTANT: Ends by specifically asking ChatGPT to review, improve, or enhance your response
    5. Signs off with your name "- Claude"
    
    Keep your tone professional, clear, and collaborative.
    """
    
    for attempt in range(max_retries):
        try:
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1500,
                temperature=0.7,
                system=claude_system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
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

def chatgpt_refine(claude_response, task_description):
    """
    Send Claude's output to ChatGPT for refinement,
    with ChatGPT responding directly to Claude
    """
    max_retries = 3
    retry_delay = 2
    
    chatgpt_system_prompt = f"""
    You are ChatGPT, an AI assistant by OpenAI. You're collaborating with Claude (by Anthropic)
    on solving the user's request: {task_description}
    
    Claude has provided their implementation and asked you to review it.
    
    Your response should:
    1. Begin with a brief greeting to Claude, addressing them by name
    2. Provide constructive feedback on Claude's implementation
    3. Offer specific improvements, enhancements, or corrections
    4. Include a complete, improved implementation when applicable (especially for code)
    5. End with a friendly sign-off like "- ChatGPT"
    
    Keep your tone positive, helpful, and collaborative, like you're working with a respected colleague.
    """
    
    for attempt in range(max_retries):
        try:
            # Using modern OpenAI client format
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=0.5,
                messages=[
                    {
                        "role": "system", 
                        "content": chatgpt_system_prompt
                    },
                    {
                        "role": "user", 
                        "content": claude_response
                    }
                ]
            )
            
            # New response format for modern client
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"OpenAI API error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return f"⚠️ Error with OpenAI API: {str(e)}"

def ai_collaboration(user_prompt, chat_history=None):
    """
    Facilitates a conversation between Claude and ChatGPT to solve the user's prompt
    """
    # Show status message
    progress_message = "⏳ Starting AI collaboration between Claude and ChatGPT..."
    yield progress_message
    
    # Get Claude's initial response
    print(f"Claude ({CLAUDE_MODEL}) is generating a response...")
    claude_text = claude_generate(user_prompt, user_prompt)
    if claude_text.startswith("⚠️ Error"):
        yield claude_text
        return
    
    # First yield Claude's response to show progress
    yield f"<div class='claude-message'><h3>🟣 Claude ({CLAUDE_MODEL.split('-')[2].capitalize() if '-' in CLAUDE_MODEL else CLAUDE_MODEL})</h3>\n\n{claude_text}</div>"
    
    # Get ChatGPT's refinement
    print(f"ChatGPT ({OPENAI_MODEL}) is reviewing and refining...")
    chatgpt_text = chatgpt_refine(claude_text, user_prompt)
    if chatgpt_text.startswith("⚠️ Error"):
        yield f"<div class='claude-message'><h3>🟣 Claude ({CLAUDE_MODEL.split('-')[2].capitalize() if '-' in CLAUDE_MODEL else CLAUDE_MODEL})</h3>\n\n{claude_text}</div>\n\n{chatgpt_text}"
        return

    # Get model display names
    claude_display = CLAUDE_MODEL.split('-')[2].capitalize() if '-' in CLAUDE_MODEL else CLAUDE_MODEL
    openai_display = OPENAI_MODEL.replace("-", " ").title()

    # Combine responses with clear visual separation
    combined_text = f"""
<div class='claude-message'><h3>🟣 Claude ({claude_display})</h3>

{claude_text}
</div>

<div class='chatgpt-message'><h3>🟢 ChatGPT ({openai_display})</h3>

{chatgpt_text}
</div>
"""
    yield combined_text

def chat_interface(user_message, chat_history):
    """
    Gradio chat function that shows the conversation between the AIs
    """
    # Update chat history with the user message immediately
    chat_history.append((user_message, ""))
    yield "", chat_history
    
    # Generate responses
    bot_message = ""
    for message in ai_collaboration(user_message, chat_history):
        # Update the last message
        bot_message = message
        chat_history[-1] = (user_message, bot_message)
        yield "", chat_history

# Updated CSS to meet the requested refinements
custom_css = """
/* 1) Ensure Claude’s text is black (or near-black) */
/* Force Claude’s bubble text to true black */
.claude-message {
    float: left;
    clear: both;
    display: inline-block;
    max-width: 70%;
    margin: 10px 0;
    padding: 10px 15px;
    border-radius: 16px;
    background-color: #e5e5ea; /* iMessage-like gray bubble */
}

.claude-message,
.claude-message * {
    color: #000000 !important; /* Force black text on any descendants */
}

/* Keep code sections dark if desired */
.claude-message code,
.claude-message pre {
    background-color: #2f3136 !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.5em 0.75em !important;
    border-radius: 6px !important;
    font-family: Menlo, Consolas, "DejaVu Sans Mono", monospace !important;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* ChatGPT bubble remains blue with white text */
.chatgpt-message {
    float: right;
    clear: both;
    display: inline-block;
    max-width: 70%;
    margin: 10px 0;
    padding: 10px 15px;
    border-radius: 16px;
    background-color: #007aff; /* iMessage-like blue bubble */
    color: #ffffff !important;
}

/* General container text color */
.gradio-container {
    color: #111827 !important;
}

/* 2) Code blocks + inline code styled closer to ChatGPT's dark look */
code, pre {
    background-color: #2f3136 !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.5em 0.75em !important;
    border-radius: 6px !important;
    font-family: Menlo, Consolas, "DejaVu Sans Mono", monospace !important;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* 3) Placeholder text (example) is light gray + italic, actual typed text is white, non-italic */
textarea, input {
    font-style: normal !important;
    color: #ffffff !important; /* typed text is white */
    background-color: #111827 !important; /* keep existing background or dark if desired */
}
textarea::placeholder, input::placeholder {
    color: #ccc !important; /* light gray placeholders */
    font-style: italic;
}

/* 4) The Clear Chat button is given a lighter gray background to offset from text */
#clear_btn {
    background-color: #f0f0f0 !important;
    color: #111827 !important;
}

/* 5) Make "Tips for Effective Prompts" white text */
.gr-accordion-label {
    color: #ffffff !important;
}

/* Additional elements remain with good contrast */
.chat-message {
    color: #111827 !important;
}
.user-message {
    color: #111827 !important;
    background-color: #e5e7eb !important;
}
.assistant-message {
    color: #111827 !important;
}
.claude-message h3, .chatgpt-message h3 {
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 0.95em;
    font-weight: 600;
    border-bottom: none;
    color: inherit;
}
/* 6) Reduce chat height to avoid scrolling for UI controls */
#chatbot {
    height: 400px !important;
}

/* Ensure button text is visible */
button {
    color: #111827 !important;
}
"""

# Get model display names for UI
claude_display = CLAUDE_MODEL.split('-')[2].capitalize() if '-' in CLAUDE_MODEL else CLAUDE_MODEL
openai_display = OPENAI_MODEL.replace("-", " ").title()

# Build the Gradio UI
with gr.Blocks(css=custom_css, theme=gr.themes.Default()) as demo:
    gr.Markdown(f"# AI Collaboration: Claude ({claude_display}) & ChatGPT ({openai_display})")
    gr.Markdown("""
    This interface demonstrates Claude and ChatGPT collaborating directly with each other:
    
    1. You provide a task or question
    2. Claude analyzes it and creates an initial response
    3. ChatGPT reviews Claude's work and provides improvements
    
    Watch as the two AI systems work together to create a better result than either could alone!
    """)
    
    # Display chat with reduced height
    chatbot = gr.Chatbot(
        label="AI Collaboration",
        elem_id="chatbot",
        bubble_full_width=True,
        height=400,
        show_copy_button=True,
        avatar_images=(None, "🤖")
    )
    
    # Row for the user's text entry
    with gr.Row():
        msg = gr.Textbox(
            label="Enter your task or question here",
            placeholder="For example: Write a Python function that checks if a number is prime",
            lines=3,
            max_lines=10,
            show_label=False,
            container=False
        )
    
    # Row with "Submit" and "Clear Chat" side-by-side
    with gr.Row():
        submit_btn = gr.Button("Submit", variant="primary")
        clear = gr.Button("Clear Chat", elem_id="clear_btn")
    
    # Model info
    model_info = gr.Markdown(f"**Models:** Claude = `{CLAUDE_MODEL}` | ChatGPT = `{OPENAI_MODEL}`")

    def clear_history():
        return []

    # Connect components
    msg.submit(chat_interface, [msg, chatbot], [msg, chatbot])
    submit_btn.click(chat_interface, [msg, chatbot], [msg, chatbot])
    clear.click(fn=clear_history, inputs=[], outputs=[chatbot])

    # Tips section (remove "Tips for Better AI Collaboration" line)
    with gr.Accordion("Tips for Effective Prompts", open=False):
        gr.Markdown("""
        - Be specific about what you want the AIs to accomplish
        - For coding tasks, specify the language, requirements, and expected behavior
        - For creative work, provide clear parameters and examples
        - For analysis, clearly define the scope and goals
        - Complex tasks often get better results than simple ones, as the AIs can truly collaborate
        """)

# Launch with a local URL
if __name__ == "__main__":
    print(f"✨ Starting AI Collaboration between Claude ({claude_display}) and ChatGPT ({openai_display})")
    print("📊 Access the web interface at http://127.0.0.1:7860")
    demo.queue().launch(server_name="127.0.0.1", server_port=7860, share=True)
