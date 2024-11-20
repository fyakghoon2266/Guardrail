import os
import logging
import sys
from typing import Any, Dict
import httpx
import json

from fastapi import Request
from starlette.responses import Response

from app.handlers.keyword_blocker import check_and_block_keywords, completions_block_response
from app.config.settings import settings

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')
logging.getLogger("nemoguardrails").setLevel(logging.ERROR)

class RequestHandler:
    def __init__(self, model_info: str, api_version: str):
        self.model_info = model_info
        self.api_version = api_version
        
class CompletionsRequestHandler(RequestHandler):
    async def handle_request(self, request: Request, rails: Any) -> Dict[str, Any]:

        url = str(request.url)
        method = request.method
        # 複製原始請求的 body 和 headers
        body = await request.body()

         # Step 2: 解碼字節流為字串
        body_str = body.decode('utf-8')

        # Step 3: 解析 JSON 字串為 Python 字典
        body_json = json.loads(body_str)

        last_message = body_json['prompt']
        
        last_message = ' '.join(last_message)

        logging.info('completion input message : {last_message}')
        
        block_result = await check_and_block_keywords(last_message, rails, mode='completion', rails_type='input')

        if block_result==400:
            block_response = await completions_block_response(request, reason=settings.input_keyword_block_message)

            return block_response
        
        elif block_result==401:
            block_response = await completions_block_response(request, reason=settings.input_content_block_message)

            return block_response

        #print(body)
        headers = {
            key: value for key, value in request.headers.items()
        }

        headers['host'] = os.getenv("AZURE_HOST")
        headers['api-key'] = os.getenv("AZURE_OPENAI_API_KEY")
        
       # Replace url.
        url = url.replace(f'{os.getenv("BASE_URL")}', f'{os.getenv("AZURE_ENDPOINT")}')

        # 使用 httpx 發送請求
        async with httpx.AsyncClient(timeout=None) as client:
            forwarded_response = await client.request(method, url, content=body, headers=headers)

        azure_response = Response(
            content=forwarded_response.content,
            status_code=forwarded_response.status_code,
            headers=dict(forwarded_response.headers),
            media_type=forwarded_response.headers.get("Content-Type")
        )

        response_content_str = azure_response.body.decode('utf-8')

        # Step 2: 解析字串為 JSON 格式
        response_json = json.loads(response_content_str)

        logging.info(f"completions output : {response_json['choices'][0]['text']}")

        block_result = await check_and_block_keywords(response_json["choices"][0]["text"], rails, mode='completion', rails_type='output')
        
        if block_result==400:
            block_response = await completions_block_response(request, reason=settings.output_keyword_block_message)

            return block_response
        
        elif block_result==401:
            block_response = await completions_block_response(request, reason=settings.output_content_block_message)

            return block_response


        return azure_response