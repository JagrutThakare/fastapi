# Important Instruction for Manish
## Remember to put in HF_TOKEN everytime as i can't push the repo with token.

# FastAPI Backend

This backend handles:
- News fetching
- Prompt generation
- API endpoints for the application
- Inpainting

## Setup for Python 3.12 users
```bash
pip install -r requirements.txt
```

## Setup for Python <3.12 users (Remove pygooglenews from requirements.txt)
```bash
pip install -r requirements.txt
pip install pygooglenews==0.1.2 --no-deps
```

## Running the application

```bash
uvicorn app.main:app --reload
```








