import os
import logging
import sys
from typing import Any, Dict
import httpx
import json


from fastapi import Request
from starlette.responses import Response

from app.handlers.keyword_blocker import check_and_block_keywords, chat_block_response, chat_stream_output_block_response, chat_stream_input_block_response
from app.handlers.untils import accumulate_streamed_content, process_response_content, get_last_user_content
from app.config.settings import settings

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger("nemoguardrails").setLevel(logging.ERROR)

class RequestHandler:
    def __init__(self, model_info: str, api_version: str):
        self.model_info = model_info
        self.api_version = api_version

class ChatCompletionsRequestHandler(RequestHandler):
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

        for message in body_json.get('messages', []):
            if message.get('role') == 'system':
                system_content = message.get('content')

                logging.info(f'system prompt : {system_content}')

        # 取得最後一個 message
        last_message = get_last_user_content(body_json)

        logging.info(f'User Massage : {last_message}')

        block_result_input = await check_and_block_keywords(last_message, rails_rule, mode='chat')

        if block_result_input==400:
            if body_json['stream'] == True:
                body = await chat_stream_input_block_response(last_message, request, reason=settings.stream_input_keyword_block_message)

            else:
                block_response = await chat_block_response(request, reason=settings.input_keyword_block_message)

                return block_response
        
        elif block_result_input==401:
            if body_json['stream'] == True:
                body = await chat_stream_input_block_response(last_message, request, reason=settings.stream_input_content_block_message)
            else:
                block_response = await chat_block_response(request, reason=settings.input_content_block_message)

                return block_response

        headers = {
            key: value for key, value in request.headers.items()
        }

        headers['host'] = os.getenv("AZURE_HOST")
        headers['api-key'] = os.getenv("AZURE_OPENAI_API_KEY")
        headers['content-length'] = str(len(body))
        
        # Replace url
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

        if process_response_content(azure_response.body.decode('utf-8'))==True:

            response_content_str = azure_response.body.decode('utf-8')

            if block_result_input == 400:
                block_response = await chat_stream_output_block_response(forwarded_response, reason=settings.stream_input_keyword_block_message)

                return block_response
            elif block_result_input == 401:
                block_response = await chat_stream_output_block_response(forwarded_response, reason=settings.stream_input_content_block_message)

                return block_response

            if body_json['stream'] == True:

                logging.info(f'chat output message : {accumulate_streamed_content(response_content_str)}')

                block_result_ouput = await check_and_block_keywords(str(accumulate_streamed_content(response_content_str)), rails_rule, mode='chat')

            else: 

                logging.info(f"chat output message : {json.loads(response_content_str)['choices'][0]['message']['content']}")

                block_result_ouput = await check_and_block_keywords(json.loads(response_content_str)['choices'][0]['message']['content'], rails_rule, mode='chat')

            if block_result_ouput==400:
                if body_json['stream'] == True:
                    block_response = await chat_stream_output_block_response(forwarded_response, reason=settings.stream_output_keyword_block_message)

                else:
                    block_response = await chat_block_response(request, reason=settings.output_keyword_block_message)

                return block_response
            
            elif block_result_ouput==401:
                if body_json['stream'] == True:
                    block_response = await chat_stream_output_block_response(forwarded_response, reason=settings.stream_output_content_block_message)
                else:
                    block_response = await chat_block_response(request, reason=settings.output_content_block_message)

                return block_response
                            
            else:

                return azure_response

        else:

            return azure_response
