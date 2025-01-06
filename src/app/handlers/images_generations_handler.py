import os
import logging
import sys
from typing import Any, Dict
import httpx
import json

from fastapi import Request
from starlette.responses import JSONResponse, Response

from app.handlers.untils import process_input
from app.handlers.keyword_blocker import check_and_block_keywords, chat_block_response

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')
logging.getLogger("nemoguardrails").setLevel(logging.ERROR)


class RequestHandler:
    def __init__(self, model_info: str, api_version: str):
        self.model_info = model_info
        self.api_version = api_version

class ImagesRequestHandler(RequestHandler):
    async def handle_request(self, request: Request, rails: Any) -> Dict[str, Any]:

        rails_rule = rails

        url = str(request.url)
        method = request.method
        # 複製原始請求的 body 和 headers
        body = await request.body()

         # Step 2: 解碼字節流為字串
        body_str = body.decode('utf-8')

        # Step 3: 解析 JSON 字串為 Python 字典
        body_json = json.loads(body_str)

        logging.info(f"process input : {body_json.get('prompt')}")

        block_result_input = await check_and_block_keywords(body_json.get('prompt'), rails_rule, mode='images', rails_type='input')

        if block_result_input==400:
            logging.exception("An error occurred")
            return JSONResponse(content={"error": "很抱歉，您的資料中有觸犯到護欄關鍵字規則，因此被阻擋"}, status_code=504)
        
        elif block_result_input==401:

            logging.exception("An error occurred")
            return JSONResponse(content={"error": "很抱歉，您的資料中有觸犯到護欄內容規則，因此被阻擋"}, status_code=504)


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

        return azure_response