import requests
import io
import time
import json
import logging
from typing import Dict, Any
from app.models.schemas import ComfyUIPrompt, HistoryResponse, ProgressResponse

logger = logging.getLogger(__name__)

def queue_prompt(server_address: str, client_id: str, prompt: Dict) -> Dict[str, Any]:
    """Sends a workflow JSON prompt to ComfyUI."""
    try:
        payload = {"prompt": prompt, "client_id": client_id}
        logger.info(f"Sending prompt to ComfyUI: {json.dumps(payload, indent=2)}")
        response = requests.post(
            f"http://{server_address}/prompt",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"ComfyUI response: {json.dumps(result, indent=2)}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Error queuing prompt: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in queue_prompt: {str(e)}")
        return {"error": str(e)}

def track_progress(server_address: str, prompt_id: str) -> Dict[str, Any]:
    """Tracks progress of an ongoing prompt until completion."""
    try:
        counter = 1
        while True:
            response = requests.get(f"http://{server_address}/history/{prompt_id}")
            response.raise_for_status()
            history_data = response.json()

            if prompt_id not in history_data:
                logger.info(f"Waiting... {counter} seconds (Prompt ID {prompt_id} not found yet)")
                counter += 1
                time.sleep(1)
                continue

            status = history_data[prompt_id].get("status", {}).get("completed", False)
            if status:
                logger.info(f"Image generation completed in {counter} seconds!")
                return history_data

            logger.info(f"Still processing... {counter} seconds elapsed")
            counter += 1
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error tracking progress: {str(e)}")
        return {"error": str(e)}

def get_image(server_address: str, filename: str) -> Dict[str, Any]:
    """Fetches the generated image from ComfyUI."""
    try:
        params = {"filename": filename, "subfolder": "", "type": "output"}
        response = requests.get(f"http://{server_address}/view", params=params)
        response.raise_for_status()
        return {
            "filename": filename,
            "image_data": io.BytesIO(response.content).getvalue()
        }
    except Exception as e:
        logger.error(f"Error fetching image: {str(e)}")
        return {"error": str(e)}