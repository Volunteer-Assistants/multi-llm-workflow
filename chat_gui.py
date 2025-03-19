import os
import time
import sys
import re
from openai import OpenAI
from anthropic import Anthropic, AuthenticationError, APIError, RateLimitError
from dotenv import load_dotenv
import gradio as gr

# Import our multi-model workflow
from multi_model_workflow import ai_collaboration

"""
chat_gui.py

This script provides a web-based chat interface where Claude and ChatGPT
talk directly to each other in a conversational format. It now includes:
- File attachments (text files)
- Persistent conversation memory
- GitHub context enrichment via MCP

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
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o3-mini")

print(f"Using Claude model: {CLAUDE_MODEL}")
print(f"Using OpenAI model: {OPENAI_MODEL}")

# Initialize API clients using modern formats
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Persistent conversation memory for the session
conversation_memory = []
MAX_MEMORY_ENTRIES = 10  # Limit to prevent very long contexts

def update_memory(role, content):
    """Add a new entry to the conversation memory with metadata"""
    conversation_memory.append({
        "role": role,
        "content": content,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # If we exceed the max entries, remove the oldest one (but keep at least one entry)
    if len(conversation_memory) > MAX_MEMORY_ENTRIES:
        conversation_memory.pop(0)

def format_conversation_history():
    """Format the memory into a string for the models to process"""
    if not conversation_memory:
        return ""
    
    history = "--- Previous Conversation History ---\n\n"
    for entry in conversation_memory:
        history += f"[{entry['role']}] ({entry['timestamp']}): {entry['content']}\n\n"
    history += "--- End of History ---\n\n"
    
    return history

def process_file_content(file_obj):
    """
    Extract text content from an uploaded file
    Returns the content as string or None if the file couldn't be processed
    """
    if file_obj is None:
        return None
        
    try:
        # Check file size
        MAX_FILE_SIZE = 1024 * 1024  # 1MB limit
        
        # Check the file size in memory (for bytes) or on disk
        if isinstance(file_obj, bytes):
            file_size = len(file_obj)
        else:
            file_obj.seek(0, os.SEEK_END)
            file_size = file_obj.tell()
            file_obj.seek(0)
            
        if file_size > MAX_FILE_SIZE:
            return "ERROR: File exceeds the maximum size limit of 1MB."
            
        # Extract content - assume text file
        file_content = file_obj.decode("utf-8") if isinstance(file_obj, bytes) else file_obj.read().decode("utf-8")
        
        # Truncate if it's extremely long
        MAX_CONTENT_LENGTH = 20000  # ~20KB of text
        if len(file_content) > MAX_CONTENT_LENGTH:
            file_content = file_content[:MAX_CONTENT_LENGTH] + "\n...[content truncated due to length]..."
            
        return file_content
        
    except UnicodeDecodeError:
        return "ERROR: Could not process the file. Make sure it's a text file."
    except Exception as e:
        return f"ERROR: {str(e)}"

def chat_interface(user_message, file_upload, chat_history):
    """
    Gradio chat function that shows the conversation between the AIs
    Now processes file uploads and maintains conversation memory
    """
    # Process file if uploaded
    file_content = None
    if file_upload is not None:
        try:
            file_content = process_file_content(file_upload)
            if file_content and file_content.startswith("ERROR:"):
                chat_history.append((f"File upload: {file_upload.name}", file_content))
                return "", None, chat_history
        except Exception as e:
            error_msg = f"⚠️ Error processing file: {str(e)}"
            chat_history.append((f"File upload: {file_upload.name}", error_msg))
            return "", None, chat_history
    
    # Get conversation context
    conversation_context = format_conversation_history()
    
    # Update chat history with the user message immediately
    upload_note = f" [with file: {file_upload.name}]" if file_upload else ""
    chat_history.append((user_message + upload_note, ""))
    yield "", None, chat_history
    
    # Generate responses
    bot_message = ""
    for message in ai_collaboration(user_message, file_content, conversation_context):
        # Update the last message
        bot_message = message
        chat_history[-1] = (user_message + upload_note, bot_message)
        yield "", None, chat_history
    
    # Extract content for memory (stripping HTML)
    if bot_message:
        # Parse Claude's response from the combined output
        claude_match = re.search(r'<div class=\'claude-message\'><h3>.*?</h3>\s*\n\n(.*?)\s*</div>', bot_message, re.DOTALL)
        if claude_match:
            claude_text = claude_match.group(1).strip()
            update_memory("Claude", claude_text)
        
        # Parse ChatGPT's response from the combined output
        chatgpt_match = re.search(r'<div class=\'chatgpt-message\'><h3>.*?</h3>\s*\n\n(.*?)\s*</div>', bot_message, re.DOTALL)
        if chatgpt_match:
            chatgpt_text = chatgpt_match.group(1).strip()
            update_memory("ChatGPT", chatgpt_text)
        
        # Update user message in memory
        update_memory("User", user_message + (f" [with attached file]" if file_content else ""))

# Updated CSS to meet the requested refinements
custom_css = """
/* 1) Ensure Claude's text is black (or near-black) */
/* Force Claude's bubble text to true black */
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

/* File upload area styling */
.file-upload {
    margin-top: 10px;
    margin-bottom: 10px;
    padding: 10px;
    border: 2px dashed #ccc;
    border-radius: 8px;
    background-color: #f8f9fa;
}

/* Memory indicator */
.memory-indicator {
    font-size: 0.8em;
    color: #666;
    text-align: right;
    margin-bottom: 5px;
}

/* GitHub section styling */
.github-section {
    padding: 10px;
    background-color: #f4f6f8;
    border-left: 4px solid #0366d6;
    margin-bottom: 10px;
    border-radius: 0 6px 6px 0;
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
    
    **New Features:**
    - Upload text files for the models to analyze
    - Conversation memory allows models to reference previous exchanges
    - GitHub integration via MCP for repository context
    """)
    
    # Memory indicator
    memory_indicator = gr.Markdown("", elem_classes=["memory-indicator"])
    
    # Display chat with reduced height
    chatbot = gr.Chatbot(
        label="AI Collaboration",
        elem_id="chatbot",
        bubble_full_width=True,
        height=400,
        show_copy_button=True,
        avatar_images=(None, "🤖")
    )
    
    # File upload component
    file_upload = gr.File(
        label="Upload a text file (optional, max 1MB)",
        file_count="single",
        file_types=[".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv"]
    )
    
    # Row for the user's text entry
    with gr.Row():
        msg = gr.Textbox(
            label="Enter your task or question here",
            placeholder="For example: Write a Python function that checks if a number is prime or analyze repository openai/openai-python",
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
        global conversation_memory
        conversation_memory = []
        return [], None, "Memory cleared"

    def update_memory_indicator():
        if not conversation_memory:
            return "No conversation history"
        return f"Memory: {len(conversation_memory)} entries from current session"

    # Connect components
    msg.submit(chat_interface, [msg, file_upload, chatbot], [msg, file_upload, chatbot])
    submit_btn.click(chat_interface, [msg, file_upload, chatbot], [msg, file_upload, chatbot])
    clear.click(clear_history, inputs=[], outputs=[chatbot, file_upload, memory_indicator])
    
    # Update memory indicator periodically
    demo.load(update_memory_indicator, inputs=None, outputs=[memory_indicator], every=5)

    # Tips section
    with gr.Accordion("Tips for Effective Prompts", open=False):
        gr.Markdown("""
        - Be specific about what you want the AIs to accomplish
        - For coding tasks, specify the language, requirements, and expected behavior
        - For creative work, provide clear parameters and examples
        - For analysis, clearly define the scope and goals
        - Complex tasks often get better results than simple ones, as the AIs can truly collaborate
        - When uploading files, make sure they're text-based (code, data, documentation)
        - To use GitHub integration, mention a repository (e.g., "Tell me about repository owner/repo")
        """)
    
    # GitHub MCP info
    with gr.Accordion("GitHub Integration (MCP)", open=False):
        gr.Markdown("""
        ### GitHub Model Context Protocol Integration
        
        This interface supports GitHub context enrichment through the Model Context Protocol (MCP).
        
        #### How to use:
        
        1. **Repository information**: Mention a GitHub repository in your prompt
           - Example: "Tell me about the repository openai/openai-python"
        
        2. **Issue details**: Reference a specific issue
           - Example: "What's in issue #123 in tensorflow/tensorflow?"
        
        3. **Pull request analysis**: Ask about a specific PR
           - Example: "Analyze PR #456 in facebook/react"
        
        #### Setup:
        
        To use this feature, you need to have the MCP GitHub server running. In a separate terminal:
        
        ```bash
        npx -y @modelcontextprotocol/server-github
        ```
        
        Make sure your GitHub token is set in the .env file as GITHUB_PERSONAL_ACCESS_TOKEN.
        """)

# Launch with a local URL
if __name__ == "__main__":
    print(f"✨ Starting AI Collaboration between Claude ({claude_display}) and ChatGPT ({openai_display})")
    print("📊 Access the web interface at http://127.0.0.1:7860")
    demo.queue().launch(server_name="127.0.0.1", server_port=7860, share=True)