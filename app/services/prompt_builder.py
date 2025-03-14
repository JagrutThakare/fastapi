import asyncio
import websockets
import uuid
import json
import logging
from gradio_client import Client
from huggingface_hub import login
import time
from app.services.prompt_templates import (
    post_type_prompts, post_type_properties, post_type_fields,
    FIELD_PROMPT_MAP, creative_guidelines, extension
)
from app.api.routes import connect_to_comfy, queue_prompt as queue_prompt_route

logger = logging.getLogger(__name__)

# ... (imports and other code remain the same)

async def generate_prompt(request_data):
    prompt_parts = []

    post_type = request_data.get("post_type", "").strip().lower()

    if post_type and post_type in post_type_prompts:
        prompt_parts.append(post_type_prompts[post_type])

    if post_type and post_type in post_type_properties:
        properties = post_type_properties[post_type]
        formatted_properties = " ".join(f"{key}: {value}" for key, value in properties.items() if value)
        if formatted_properties:
            prompt_parts.append(formatted_properties)

    if post_type in post_type_fields:
        for field in post_type_fields[post_type]:
            field_value = request_data.get(field)
            if field_value:
                prompt_parts.append(FIELD_PROMPT_MAP[field](field_value))

    general_fields = ["message", "brand_name", "font", "colors"]
    for field in general_fields:
        field_value = request_data.get(field)
        if field_value:
            prompt_parts.append(FIELD_PROMPT_MAP[field](field_value))

    if post_type in creative_guidelines:
        prompt_parts.append(creative_guidelines[post_type])

    if extension:
        prompt_parts.append(extension)

    final_prompt = "".join(filter(None, prompt_parts))

    login("HF_TOKEN")
    max_retries = 3
    retry_delay = 5
    for attempt in range(max_retries):
        print("Retry no ", attempt)
        try:
            client = Client("atharva-dev/prompt_generator")
            result = client.predict(prompt=final_prompt, api_name="/generate")
            positive = result[0]
            negative = result[1]
            break
        except Exception as e:
            if attempt == max_retries - 1:
                positive = "Dynamic social media post, bold colors, modern typography, engaging composition"
                negative = "Blurry text, low contrast, cluttered design, outdated style"
                print(f"Failed to connect to Hugging Face Space after {max_retries} attempts: {str(e)}. Using mocked response.")
            else:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

    print("Got the prompt")
    final_prompt = "Positive:\n" + positive + "\n\nNegative:\n" + negative
    print("final Prompt", final_prompt)

    workflow_path = "app\\services\\tutorial.json"
    try:
        print("Opening Json")
        with open(workflow_path, 'r') as file:
            data = json.load(file)

        data["prompt"]["6"]["inputs"]["text"] = positive
        data["prompt"]["7"]["inputs"]["text"] = negative

        print("writing to json")
        with open(workflow_path, 'w') as file:
            json.dump(data, file, indent=4)

        # Return the prompt and workflow data separately
        return {
            "generated_prompt": final_prompt,
            "workflow_data": data["prompt"]  # Only the "prompt" part of the workflow
        }
    except Exception as e:
        print(f"Error updating ComfyUI workflow: {str(e)}")
        raise