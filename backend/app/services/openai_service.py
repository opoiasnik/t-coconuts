import requests
from app.config import Config

def call_openai(text, instructions):
    """
    Sends a request to the OpenAI API with the provided text and instructions.

    Args:
        text (str): Extracted text from the document.
        instructions (str): Instructions for the AI model to process the text.

    Returns:
        str: The response from the OpenAI API.
    """
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # The data payload for the OpenAI API request
    data = {
        "model": "gpt-3.5-turbo",  # Specify the model to use
        "messages": [
            {"role": "system", "content": "You are a document assistant."},
            {"role": "user", "content": f"{instructions}\n\n{text}"}
        ]
    }

    try:
        # Send the POST request to the OpenAI API
        response = requests.post(Config.OPENAI_URL, json=data, headers=headers)

        # Raise an exception if the status code is not 200
        response.raise_for_status()

        # Extract and return the AI's response
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        # Handle errors (e.g., network issues or invalid API key)
        raise Exception(f"Error communicating with OpenAI API: {str(e)}")
