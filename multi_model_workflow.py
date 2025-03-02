import os
import sys
import time
from openai import OpenAI
from anthropic import Anthropic, AuthenticationError, APIError, RateLimitError
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key or not anthropic_api_key:
        print("ERROR: Missing API keys. Please set them in .env or environment variables.")
        print("Make sure to rename .env.example to .env and add your API keys.")
        sys.exit(1)

    # Check command-line args
    if len(sys.argv) < 2:
        print("Usage: python multi_model_workflow.py \"Your prompt here\"")
        print("Example: python multi_model_workflow.py \"Create a function to calculate Fibonacci numbers\"")
        sys.exit(0)

    user_prompt = sys.argv[1]
    print(f"\n🔍 Processing prompt: \"{user_prompt}\"")
    
    try:
        # 1) Send to Claude for initial code generation
        print("\n⏳ Generating initial code with Claude...")
        claude_response = claude_generate(anthropic_api_key, user_prompt)
        
        # 2) Send to ChatGPT for review & refinement
        print("⏳ Refining code with ChatGPT...")
        final_code = chatgpt_refine(openai_api_key, claude_response)
        
        # Output final combined code
        print("\n=== 📝 Claude's Initial Code ===")
        print(claude_response)
        print("\n=== ✨ ChatGPT's Refined Code ===")
        print(final_code)
        print("\n✅ Done. You can now review this output and optionally save it to a file.")
        
        # Offer to save the output
        save_option = input("\nWould you like to save the final code to a file? (y/n): ")
        if save_option.lower() == 'y':
            filename = input("Enter filename to save to: ")
            with open(filename, 'w') as f:
                f.write(final_code)
            print(f"Code saved to {filename}")
    
    except AuthenticationError:
        print("❌ ERROR: Authentication failed. Please check your API keys in the .env file.")
        sys.exit(1)
    except RateLimitError:
        print("❌ ERROR: Rate limit exceeded. Please try again later.")
        sys.exit(1)
    except APIError as e:
        print(f"❌ ERROR: API error occurred: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred: {str(e)}")
        sys.exit(1)


def claude_generate(anthropic_api_key, prompt):
    """
    Calls Claude 3.7 Sonnet for initial code generation.
    Uses the most updated API client patterns.
    """
    client = Anthropic(api_key=anthropic_api_key)
    
    # Use the current Claude 3.7 Sonnet model ID
    claude_model = "claude-3-7-sonnet-20250219"
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Using the Messages API (preferred over the older Completion API)
            response = client.messages.create(
                model=claude_model,
                max_tokens=1024,
                temperature=0.7,
                system="You are an expert programmer. Generate high-quality, well-documented code based on the user's request. Focus on best practices and clarity.",
                messages=[
                    {"role": "user", "content": f"Please generate code for: {prompt}. Include comments and explanations. Focus only on the code implementation."}
                ]
            )
            
            # Extract the text content from the response
            return response.content[0].text
            
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
        except Exception as e:
            print(f"Error with Claude API: {str(e)}")
            raise


def chatgpt_refine(openai_api_key, initial_code):
    """
    Sends the code from Claude to ChatGPT for review and refinement.
    Uses the current OpenAI client library.
    """
    client = OpenAI(api_key=openai_api_key)
    
    # Use GPT-4 as default, but you can change this to "o1" or another model
    model_name = "gpt-4"
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a coding expert with extensive experience in code review. Improve the provided code by addressing bugs, implementing best practices, and enhancing performance and readability. Provide the complete refined code without omitting any parts."
                    },
                    {
                        "role": "user", 
                        "content": f"Here is the code generated by Claude:\n\n{initial_code}\n\nPlease review and refine this code. Provide the complete improved version."
                    }
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                print(f"Error with OpenAI API. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error with OpenAI API: {str(e)}")
                raise


if __name__ == "__main__":
    main()