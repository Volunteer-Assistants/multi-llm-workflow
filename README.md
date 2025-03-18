# Multi-LLM Workflow

This repository demonstrates how to orchestrate **Claude** (3.7 Sonnet) and **ChatGPT** (GPT-4/o3-mini) to collaboratively generate and refine code. By leveraging the strengths of multiple language models in a sequential pipeline, you can create higher quality code than using a single model alone.

## How It Works

1. **User** inputs a coding prompt
2. **Claude** (Anthropic's 3.7 Sonnet) provides the initial code and explanation
3. **ChatGPT** (OpenAI's GPT-4 or o3-mini) reviews and refines Claude's code
4. The final code is displayed to the user and can be saved to a file

This workflow demonstrates how different AI models can be combined to produce better results by using each model for what it does best.

## Interface Options

This repository offers two ways to interact with the multi-LLM workflow:

### 1. Command-Line Interface

Run `multi_model_workflow.py` with a single prompt argument to get both models' responses and save the output to a file.

### 2. Web-Based Chat Interface

Run `chat_gui.py` to launch a Gradio web interface for a more interactive experience with:
- Real-time responses
- Chat history
- Side-by-side comparison of outputs
- Improved user experience

![Chat GUI Screenshot](https://raw.githubusercontent.com/Davisfox5/multi-llm-workflow/main/docs/chat_gui_screenshot.png)

## Features

- **Two Interface Options**: Command-line for scripting or Web UI for interactive use
- **Improved Error Handling**: Robust error handling for API failures, authentication issues, and rate limiting
- **Exponential Backoff**: Automatically retries API calls with exponential backoff
- **Interactive File Saving**: Option to save the generated code directly to a file
- **Progress Indicators**: Clear indication of the current stage in the workflow
- **Latest API Clients**: Uses the most recent OpenAI and Anthropic API clients

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Anthropic API key

### Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Davisfox5/multi-llm-workflow.git
   cd multi-llm-workflow
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your actual API keys:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

## Usage

### Command-Line Interface

Run the script with your coding prompt as an argument:

```bash
python multi_model_workflow.py "Create a Python function that converts a CSV file to JSON"
```

More examples:

```bash
# Generate a simple utility function
python multi_model_workflow.py "Write a function to check if a string is a palindrome"

# Create a more complex application
python multi_model_workflow.py "Create a Flask API that serves as a URL shortener"

# Request an algorithm implementation
python multi_model_workflow.py "Implement the merge sort algorithm in Python"
```

### Web Interface

Launch the web-based chat interface:

```bash
python chat_gui.py
```

Then open your browser to http://127.0.0.1:7860 and interact with the models through the chat interface.

## Advanced Configuration

You can modify the models used in the workflow by editing these environment variables in your `.env` file:

```
# Optional Configuration
CLAUDE_MODEL="claude-3-7-sonnet-20250219"
OPENAI_MODEL="gpt-4"  # or "o3-mini" for coding
```

Or directly edit the model variables in the Python files:

- In `multi_model_workflow.py`: 
  - `claude_model` in the `claude_generate()` function
  - `model_name` in the `chatgpt_refine()` function

- In `chat_gui.py`:
  - `CLAUDE_MODEL` near the top of the file
  - `CHATGPT_MODEL` near the top of the file

## Troubleshooting

- **Authentication Errors**: Make sure your API keys in the `.env` file are correct and have the necessary permissions
- **Rate Limits**: If you encounter rate limit errors, the script will automatically retry with exponential backoff
- **Model Not Found**: Ensure you're using valid model names that are available in your account
- **Gradio Installation**: If you have issues with Gradio, try `pip install gradio --upgrade`

## Contributing

Contributions to improve this workflow are welcome! Some ideas:

- Add support for more LLM providers
- Improve the web interface with additional features
- Add unit tests and CI/CD
- Create a configuration file for customizing the workflow

## License

MIT