# Multi-LLM Workflow

This repository demonstrates how to orchestrate **Claude** (3.7 Sonnet) and **ChatGPT** (GPT-4/o3-mini) to collaboratively generate and refine code. By leveraging the strengths of multiple language models in a sequential pipeline, you can create higher quality code than using a single model alone.

## How It Works

1. **User** inputs a coding prompt or uploads a text file
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
- File uploading capabilities
- Persistent conversation memory
- GitHub repository context via MCP
- Improved user experience

![Chat GUI Screenshot](https://raw.githubusercontent.com/Davisfox5/multi-llm-workflow/main/docs/chat_gui_screenshot.png)

## Features

- **Two Interface Options**: Command-line for scripting or Web UI for interactive use
- **File Attachments**: Upload text files (code, data, documentation) for the models to analyze
- **Persistent Conversation Memory**: Models can reference previous exchanges within the session
- **GitHub Integration via MCP**: Enhance prompts with GitHub repository context automatically
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
- GitHub Personal Access Token (for GitHub integration)
- Node.js (for running the MCP GitHub server)

### Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Volunteer-Assistants/multi-llm-workflow.git
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
   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
   ```

4. **Set up the MCP GitHub server** (optional, for GitHub integration):
   
   Ensure you have Node.js installed, then run:
   ```bash
   npx -y @modelcontextprotocol/server-github
   ```
   
   This will start the Model Context Protocol server for GitHub integration.

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

# With GitHub context
python multi_model_workflow.py "Explain the repository structure of openai/openai-python"
```

### Web Interface

Launch the web-based chat interface:

```bash
python chat_gui.py
```

Then open your browser to http://127.0.0.1:7860 and interact with the models through the chat interface.

#### Working with File Attachments

1. Click the upload button to attach a text file (supported formats: .txt, .md, .py, .js, .html, .css, .json, .csv)
2. Enter your prompt that references the file (e.g., "Analyze this code and suggest improvements")
3. Submit your request - both models will have access to the file content

#### Using GitHub Integration

To leverage the GitHub integration via MCP:

1. Make sure the MCP GitHub server is running (`npx -y @modelcontextprotocol/server-github`)
2. In your prompt, reference a GitHub repository, issue, or pull request:
   - Repository: "Tell me about the repository openai/openai-python"
   - Issue: "What's in issue #123 in tensorflow/tensorflow?"
   - PR: "Analyze PR #456 in facebook/react"

#### Conversation Memory

The system maintains a memory of your conversation within the session, allowing the models to reference previous exchanges. The memory indicator shows how many entries are stored.

- Use the "Clear Chat" button to reset both the chat history and memory

## Advanced Configuration

You can modify the models used in the workflow by editing these environment variables in your `.env` file:

```
# Optional Configuration
CLAUDE_MODEL="claude-3-7-sonnet-20250219"
OPENAI_MODEL="o3-mini"  # or "gpt-4" for creative tasks
```

Or directly edit the model variables in the Python files:

- In `multi_model_workflow.py`: 
  - `CLAUDE_MODEL` near the top of the file
  - `OPENAI_MODEL` near the top of the file

- In `chat_gui.py`:
  - `CLAUDE_MODEL` near the top of the file
  - `OPENAI_MODEL` near the top of the file

## Memory Configuration

You can adjust the memory settings in `.env`:

```
# Maximum memory entries
MAX_MEMORY_ENTRIES=10
```

## File Upload Limits

The system has the following limits for file uploads:

- Maximum file size: 1MB
- Supported file types: .txt, .md, .py, .js, .html, .css, .json, .csv
- Content limit: 20,000 characters (longer content will be truncated)

## MCP GitHub Integration

The GitHub integration uses the Model Context Protocol (MCP) to enrich prompts with GitHub context.

### Claude Desktop Integration (Optional)

To integrate with Claude Desktop, create or update the configuration file at:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Example configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

Restart Claude Desktop after saving this configuration.

## Troubleshooting

- **Authentication Errors**: Make sure your API keys in the `.env` file are correct and have the necessary permissions
- **Rate Limits**: If you encounter rate limit errors, the script will automatically retry with exponential backoff
- **Model Not Found**: Ensure you're using valid model names that are available in your account
- **Gradio Installation**: If you have issues with Gradio, try `pip install gradio --upgrade`
- **File Upload Errors**: Make sure your file is in a supported format and under the size limit
- **MCP Server Connection**: Ensure the MCP GitHub server is running when trying to use GitHub integration
- **GitHub Token Issues**: Verify your GitHub token has the necessary permissions (public_repo at minimum)

## Contributing

Contributions to improve this workflow are welcome! Some ideas:

- Add support for more LLM providers
- Improve the web interface with additional features
- Add unit tests and CI/CD
- Create a configuration file for customizing the workflow
- Add support for more file types and larger files
- Implement file summarization for very large files
- Expand MCP integration to other services

## License

MIT