import openai  # OpenAI API client for GPT models
from openai import RateLimitError, APIConnectionError  # OpenAI error handling
import time  # For sleep during retries
from config import  load_config



# Load the config and instantiate the OpenAI client
def setup_openai():
    config = load_config()
    api_key = config.get("openai_api_key")
    if not api_key:
        raise ValueError("API key not found in config.yaml")

    openai.api_key = api_key  # Set the OpenAI API key
    return openai.api_key


# Define the decorator for error handling
def retry_on_error(max_retries=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)  # Call the original function
                except RateLimitError:
                    retries += 1
                    wait_time = 2 ** retries  # Exponential backoff
                    print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except APIConnectionError:
                    retries += 1
                    wait_time = 2 ** retries
                    print(f"Connection error. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

            raise Exception("Maximum retries reached. Failed to enhance text due to rate limits or connection issues.")
        return wrapper
    return decorator


# The original function that enhances Arabic text
@retry_on_error(max_retries=5)  # Apply the retry decorator to this function
def get_field_from_text(openai_client ='', MAIN_PROMPT='',field_promt='', text='',field =''):
    """Enhances and corrects Arabic text using GPT-4."""
    client = openai_client
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": (MAIN_PROMPT)},
            {"role": "user", "content": f" {field_promt} : {field} in this text : {text}"}
        ]
    )
    return response.choices[0].message.content

