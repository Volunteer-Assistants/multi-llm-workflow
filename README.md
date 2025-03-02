# Multi-LLM Workflow

This repository demonstrates a Python script that orchestrates **Claude** (3.7 Sonnet) and **ChatGPT** (GPT-4/o1) to collaboratively generate and refine code. By leveraging the strengths of multiple language models in a sequential pipeline, you can create higher quality code than using a single model alone.

## How It Works

1. **User** inputs a coding prompt via command line
2. **Claude** (Anthropic's 3.7 Sonnet) provides the initial code and explanation
3. **ChatGPT** (OpenAI's GPT-4) reviews and refines Claude's code
4. The final code is displayed to the user and can be saved to a file

This workflow demonstrates how different AI models can be combined to produce better results by using each model for what it does best.

## Features

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