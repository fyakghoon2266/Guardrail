import sys
import logging

from fastapi import APIRouter, Query, Body, Request
from nemoguardrails import LLMRails, RailsConfig
from starlette.responses import JSONResponse


from app.handlers.request_handler_factory import RequestHandlerFactory
from app.handlers.verify_token import verify_token

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')
logging.getLogger("nemoguardrails").setLevel(logging.ERROR)

chat_router = APIRouter()

# Initialize NemoGuardrails
config = RailsConfig.from_path("./app/config")
rails = LLMRails(config)

@chat_router.post("/{deployment_id}/completions")
async def handle_completions(request: Request, deployment_id: str, api_version: str = Query(..., alias="api-version")):
    
    verification_result = verify_token(request.headers.get("api-key"))

    if verification_result==400:
        logging.exception("An error occurred")
        return JSONResponse(content={"error": "很抱歉，您沒有輸入api-key，因此出現此錯誤訊息"}, status_code=504)
    
    elif verification_result==401:
        logging.exception("An error occurred")
        return JSONResponse(content={"error": "很抱歉，您的api-key有誤，因此出現此錯誤訊息"}, status_code=504)
        

    
    handler = RequestHandlerFactory.get_handler("completions", deployment_id, api_version)
    result = await handler.handle_request(request, rails)
    
    return result

@chat_router.post("/{deployment_id}/embeddings")
async def handle_embeddings( request: Request, deployment_id: str, api_version: str = Query(..., alias="api-version")):
    
    verification_result = verify_token(request.headers.get("api-key"))

    if verification_result==400:

        logging.exception("An error occurred")
        return JSONResponse(content={"error": "很抱歉，您沒有輸入api-key，因此出現此錯誤訊息"}, status_code=504)

    elif verification_result==401:

        logging.exception("An error occurred")
        return JSONResponse(content={"error": "很抱歉，您的api-key有誤，因此出現此錯誤訊息"}, status_code=504)

    handler = RequestHandlerFactory.get_handler("embeddings", deployment_id, api_version)
    result = await handler.handle_request(request, rails)
    
    return result

@chat_router.post("/{deployment_id}/chat/completions")
async def handle_chat_completions(request: Request, deployment_id: str, api_version: str = Query(..., alias="api-version")):

    verification_result = verify_token(request.headers.get("api-key"))

    if verification_result==400:

        logging.exception("An error occurred")
        return JSONResponse(content={"error": "很抱歉，您沒有輸入api-key，因此出現此錯誤訊息"}, status_code=504)
        
    elif verification_result==401:

        logging.exception("An error occurred")
        return JSONResponse(content={"error": "很抱歉，您的api-key有誤，因此出現此錯誤訊息"}, status_code=504)
    

    handler = RequestHandlerFactory.get_handler("chat_completions", deployment_id, api_version)
    result = await handler.handle_request(request, rails)

    return result