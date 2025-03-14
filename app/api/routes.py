import websockets
import uuid
import json
import logging
from fastapi import APIRouter, HTTPException, Query, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from app.services.comfyui import queue_prompt, track_progress, get_image
from app.models.schemas import ComfyUIPrompt, HistoryResponse, ProgressResponse, ImageResponse
import websocket 
import io
import os
import asyncio
import requests
server = "optimal-shot-operations-do.trycloudflare.com"
logger = logging.getLogger(__name__)
router = APIRouter()

async def connect_to_comfy(server_address: str):
    client_id = str(uuid.uuid4())
    uri = f"wss://{server_address}/ws?clientId={client_id}"
    try:
        logger.info(f"Attempting to connect to {uri}")
        async with await asyncio.wait_for(websockets.connect(uri), timeout=5) as websocket:
            await websocket.send(json.dumps({"type": "connect", "client_id": client_id}))
            response = await websocket.recv()
            logger.info(f"Connected to ComfyUI with client_id: {client_id}, response: ${response}")
            return client_id, server_address, websocket
    except (websockets.ConnectionClosed, OSError, asyncio.TimeoutError) as e:
        logger.error(f"Failed to connect to {uri}: ${str(e)}")
        raise HTTPException(status_code=500, detail=f"WebSocket connection failed: ${str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error connecting to {uri}: ${str(e)}")
        raise HTTPException(status_code=500, detail=f"WebSocket connection failed: ${str(e)}")

@router.post("/queue_prompt")
async def queue_prompt_route(prompt_data: dict):
    server_address = server
    client_id = str(uuid.uuid4())
    prompt = prompt_data.get("workflow_data", {})

    if not prompt or not server_address:
        raise HTTPException(status_code=400, detail="Missing required parameters")

    try:
        payload = {"prompt": prompt, "client_id": client_id}
        logger.info(f"Sending to ComfyUI /prompt: ${json.dumps(payload)}")
        response = requests.post(
            f"http://{server_address}/prompt",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"ComfyUI response: ${result}")
        prompt_id = result.get("prompt_id")
        if not prompt_id:
            raise HTTPException(status_code=500, detail="Failed to get prompt_id from ComfyUI")
        return JSONResponse(content={"message": "Prompt queued successfully", "prompt_id": prompt_id}, status_code=200)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error queuing prompt: ${str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"ComfyUI response body: ${e.response.text}")
        raise HTTPException(status_code=500, detail=f"Error queuing prompt: ${str(e)}")
    
@router.post("/generate_prompt")
async def create_prompt(request_data: dict):
    if not request_data.get("post_type") or request_data["post_type"] not in post_type_prompts:
        raise HTTPException(status_code=400, detail="Invalid post_type.")
    
    result = await generate_prompt(request_data)
    logger.info(f"Generated prompt: ${result['generated_prompt']}")
    return result

@router.get("/get_history")
async def get_history(server_address: str = Query(server)):
    try:
        response = requests.get(f"http://{server_address}/history")
        response.raise_for_status()
        return HistoryResponse(all_prompts=response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching history: ${str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/track_progress/{prompt_id}")
async def track_progress_route(prompt_id: str, server_address: str = Query(server)):
    try:
        progress = track_progress(server_address, prompt_id)
        if "error" in progress:
            raise HTTPException(status_code=500, detail=progress["error"])
        return ProgressResponse(status="completed", message=f"Prompt {prompt_id} completed")
    except Exception as e:
        logger.error(f"Error tracking progress: ${str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_image")
async def get_image_route(filename: str = Query(...), server_address: str = Query(server)):
    try:
        image_data = get_image(server_address, filename)
        if "error" in image_data:
            raise HTTPException(status_code=500, detail=image_data["error"])
        return StreamingResponse(
            io.BytesIO(image_data["image_data"]),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=${image_data['filename']}"}
        )
    except Exception as e:
        logger.error(f"Error fetching image: ${str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_image")
async def generate_image(request_data: dict):
    """Handles full process: Queue Prompt → Track Progress → Get Image."""
    try:
        # Extract workflow_data from the request
        workflow_data = request_data.get("workflow_data")
        if not workflow_data:
            tutorial_path = "app/services/tutorial.json"
            if os.path.exists(tutorial_path):
                with open(tutorial_path, "r") as file:
                    data = json.load(file)
                    workflow_data = data["prompt"]
            else:
                raise HTTPException(status_code=400, detail="No workflow_data in request and tutorial.json not found")

        # Use default server_address and generate a new client_id
        server_address = server
        client_id = str(uuid.uuid4())

        # Pass the workflow_data directly to queue_prompt
        queue_response = queue_prompt(server_address, client_id, workflow_data)
        prompt_id = queue_response.get("prompt_id")
        if not prompt_id:
            raise HTTPException(status_code=500, detail="Failed to get prompt_id")

        logger.info(f"Tracking progress for Prompt ID: ${prompt_id}")
        track_status = track_progress(server_address, prompt_id)
        if "error" in track_status:
            raise HTTPException(status_code=500, detail=track_status["error"])

        filename = track_status[prompt_id]["outputs"]["9"]["images"][0]["filename"]
        image_data = get_image(server_address, filename)
        if "error" in image_data:
            raise HTTPException(status_code=500, detail=image_data["error"])
        logger.info(f"Returning image with filename: ${image_data['filename']}")
        return StreamingResponse(
            io.BytesIO(image_data["image_data"]),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=${image_data['filename']}"}
        )
    except Exception as e:
        logger.error(f"Error in generate_image: ${str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload_image")
async def upload_image_endpoint(
    image: UploadFile = File(...),
    server_address: str = Form(server),
    filename: str = Form(...),
    folder_type: str = Form("input"),
    image_type: str = Form("image"),
    overwrite: str = Form("false")
):
    """Uploads an image to the ComfyUI server."""
    try:
        if not allowed_file(image.filename):
            raise HTTPException(status_code=400, detail="Invalid file type. Only PNG, JPG, JPEG, GIF, BMP, TIFF, and WEBP are allowed.")

        files = {"image": (filename, image.file, f"image/{filename.rsplit('.', 1)[1].lower()}" if '.' in filename else "image/png")}
        data = {
            "type": folder_type,
            "overwrite": overwrite.lower() == "true"
        }

        logger.info(f"Uploading image to {server_address} with filename: ${filename}")
        response = requests.post(
            f"http://{server_address}/upload/{image_type}",
            files=files,
            data=data,
            timeout=10
        )
        response.raise_for_status()
        return JSONResponse(content=response.json(), status_code=200)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error uploading image: ${str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"ComfyUI response body: ${e.response.text}")
        raise HTTPException(status_code=500, detail=f"Error uploading image: ${str(e)}")

# Prompt Generator endpoints
from fastapi import APIRouter, HTTPException, Query
from app.services.prompt_builder import generate_prompt
from app.services.prompt_templates import post_type_prompts, post_type_fields
from app.utils.news_fetcher import fetch_google_news, fetch_trends_by_topic as fetch_topic_news
from app.models.schemas import RequestData, NewsResponse, CaptionRequest, Article
import logging

GENERAL_FIELDS = ["message", "brand_name", "font", "colors"]

@router.get("/")
async def read_root():
    return {"message": "Visit /static/index.html for the frontend"}

@router.get("/post-types")
async def get_post_types():
    return {"post_types": list(post_type_prompts.keys())}

@router.get("/generate_prompt_form")
async def get_prompt_form(post_type: str):
    if post_type not in post_type_prompts:
        raise HTTPException(status_code=400, detail="Invalid post_type.")
    
    relevant_fields = post_type_fields.get(post_type, []) + GENERAL_FIELDS
    return {
        "post_type": post_type,
        "required_fields": post_type_fields.get(post_type, []),
        "optional_fields": GENERAL_FIELDS,
        "example": {field: f"example_{field}" for field in relevant_fields}
    }

@router.get("/trends", response_model=NewsResponse)
def fetch_trends(
    category: str = Query("WORLD", regex="^(WORLD|NATION|BUSINESS|TECHNOLOGY|ENTERTAINMENT|SPORTS|SCIENCE|HEALTH)$"),
    lang: str = Query("en", regex="^(en|hi|es|fr|uk|ja)$"),
    country: str = Query("WORLD", regex="^(WORLD|US|IN|GB|MX|UA|JP)$"),
    limit: int = Query(10, ge=1, le=50)
):
    return fetch_google_news(category, lang, country, limit)

@router.get("/fetch_trends/{topic_name}", response_model=NewsResponse)
def get_trends_by_topic(
    topic_name: str,
    lang: str = Query("en", regex="^(en|hi|es|fr|uk|ja)$"),
    country: str = Query("WORLD", regex="^(WORLD|US|IN|GB|MX|UA|JP)$"),
    limit: int = Query(10, ge=1, le=50)
):
    try:
        return fetch_topic_news(topic_name, lang, country, limit)
    except Exception as e:
        logger.error(f"API error for topic '{topic_name}': ${str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_caption_and_hashtags")
async def generate_caption_and_hashtags(request: CaptionRequest):
    prompt = f"""
    You are an expert social media strategist and AI image analyst. Your task is to generate a creative and engaging caption along with relevant hashtags for an AI-generated image.

    **Image Details:**
    - **Positive Prompt:** {request.positive_prompt}
    - **Negative Prompt:** {request.negative_prompt}

    **Instructions:**
    1. Understand the theme, subject, and mood from the positive prompt.
    2. Ensure elements in the negative prompt are avoided.
    3. Generate a concise and captivating caption (within 15 words).
    4. Provide 10-15 hashtags that are relevant, balancing popular and niche keywords.

    **Output Format (strictly follow this structure):**
    Caption: "Your creative caption here."
    Hashtags: #hashtag1 #hashtag2 #hashtag3 ... #hashtag15
    """
    return {"generated_prompt": prompt}

# Just for Postman ( Having no use in this any space )
@router.post("/connect_to_comfy")
async def connect_to_comfy_endpoint(request_data: dict):
    """Establishes a WebSocket connection to the ComfyUI server and returns connection details."""
    server_address = request_data.get("server_address", "describing-bones-alan-mv.trycloudflare.com")
    try:
        # Call the existing connect_to_comfy function
        client_id, server_address, websocket = await connect_to_comfy(server_address)
        # Since we can't return the websocket object, we'll close it and return the connection details
        await websocket.close()
        logger.info(f"WebSocket connection closed for client_id: {client_id}")
        return JSONResponse(
            content={
                "message": "Successfully connected to ComfyUI",
                "client_id": client_id,
                "server_address": server_address
            },
            status_code=200
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions (e.g., 500 errors from connect_to_comfy)
        raise e
    except Exception as e:
        logger.error(f"Error in connect_to_comfy_endpoint: ${str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to ComfyUI: ${str(e)}")
    
@router.post("/inpaint")
async def inpaint(
    prompt_file: UploadFile = File(...),
    image: UploadFile = File(...),
    mask: UploadFile = File(...)
):
    client_id = str(uuid.uuid4())
    ws = websocket.WebSocket()

    try:
        # Parse inpaint.json
        prompt_data = await prompt_file.read()
        prompt = json.loads(prompt_data)

        # Upload image
        await image.seek(0)
        image_files = {"image": (image.filename, image.file, "image/png")}
        data = {"type": "input", "overwrite": "false"}
        img_response = requests.post(f"http://{server}/upload/image", files=image_files, data=data)

        if img_response.status_code != 200:
            print(f"Image upload failed: {img_response.text}")
            raise HTTPException(status_code=img_response.status_code, detail="Failed to upload image")

        image_name = img_response.json().get("name")
        print(f"Uploaded image: {image_name}")

        # Upload mask
        await mask.seek(0)
        mask_files = {"image": (mask.filename, mask.file, "image/png")}
        mask_data = {
            "type": "input",
            "overwrite": "false",
        }
        mask_response = requests.post(f"http://{server}/upload/image", files=mask_files, data=mask_data)

        if mask_response.status_code != 200:
            print(f"Mask upload failed: {mask_response.text}")
            raise HTTPException(status_code=mask_response.status_code, detail=mask_response.text)

        mask_name = mask_response.json().get("name")
        print(f"Uploaded mask: {mask_name}")

        
        # Update JSON with uploaded file names
        prompt["58"]["inputs"]["image"] = image_name
        prompt["62"]["inputs"]["image"] = mask_name
        print("JSON Updated")
        
        # Connect to WebSocket
        ws.connect(f"ws://{server}/ws?clientId={client_id}")

        # Send prompt
        data = {"prompt": prompt, "client_id": client_id}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"http://{server}/prompt", json=data, headers=headers)

        print(response.json())
        if response.status_code != 200:
            print(f"Prompt submission failed: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        ws.close()
    
    
    
    