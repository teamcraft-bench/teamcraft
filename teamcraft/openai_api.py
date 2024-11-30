import base64
import requests

# OpenAI API Key
api_key = "sk-proj-?"


def encode_image(image_path):
  """
  Encodes an image file to a base64 string.

  Args:
  image_path (str): The file path of the image to be encoded.

  Returns:
  str: The base64 encoded string of the image.
  """
  
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def openai_chat(string, image_paths, max_tokens = 3000, model = "gpt-4o", openai_api_key = api_key):
    """
    Sends a text string and a list of image file paths to the OpenAI chat model and returns the response.

    Args:
    string (str): The text input for the chat model.
    image_paths (list): A list of file paths to the images to be sent.
    openai_api_key (str, optional): The API key for accessing the OpenAI API. Defaults to the global api_key.

    Returns:
    dict: The JSON response from the OpenAI API, or None if an error occurs.
    """
    
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {openai_api_key}"
    }
    
    content = []
    for image_path in image_paths:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
            }
        })
    
    payload = {
      "model": model,
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": string
            },
            *content
          ]
        }
      ],
      "max_tokens": max_tokens
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None