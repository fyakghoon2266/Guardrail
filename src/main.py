from dotenv import load_dotenv

load_dotenv()

import logging
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router.chat import chat_router



logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger("nemoguardrails").setLevel(logging.ERROR)

app = FastAPI()

os.environ['FASTEMBED_CATCH_PATH']='./emb_model'

environment = os.getenv("ENVIRONMENT", "dev")  # Default to 'development' if not set

if environment == "dev":
    logger = logging.getLogger("uvicorn")
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# define correction token，use 'example_token' for example
correct_token = os.getenv("API_TOKEN", "example_token")

app.include_router(chat_router, prefix="/openai/deployments")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True, port=8000)