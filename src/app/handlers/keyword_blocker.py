import os
import json
import logging
from typing import Any, Dict


from fastapi import Request
from starlette.responses import JSONResponse, Response
import httpx

from app.config.settings import settings
from app.handlers.untils import block_chat_stream



async def check_and_block_keywords(data: Any, rails: Any, mode: Any) -> Dict[str, Any]:

    response = await rails.generate_async(prompt=data, options={"mode": mode, "rails": ["input"]})

    print('response : ', response)

    if response.response == '999':

        return 400

    elif response.response == '997':

        return 401

    else:
        return None

async def chat_block_response(request: Request, reason: str) -> Any:
    logging.info(f'Forwarding request to: OpenAI')
    
    try:
        # 取得 method
        url = str(request.url)
        method = request.method
        # 複製原始請求的 body 和 headers
        body = await request.body()
        #print(body)
        headers = {
            key: value for key, value in request.headers.items()
        }

        # Step 2: 解碼字節流為字串
        body_str = body.decode('utf-8')

        # Step 3: 解析 JSON 字串為 Python 字典
        body_json = json.loads(body_str)

        # Step 4: 確定 messages 列表不為空，並修改最後一個 'content' 欄位
        if 'messages' in body_json and body_json['messages']:
            # 取得最後一個 message
            last_message = body_json['messages'][-1]

            # 確定最後一個 message 中有 'content' 欄位
            if 'content' in last_message:
                last_message['content'] = settings.default_message 


        # Step 5: 將修改後的字典轉回 JSON 並編碼為字節格式
        modified_request_body = json.dumps(body_json).encode('utf-8')

        headers['host'] = os.getenv("AZURE_HOST")
        headers['api-key'] = os.getenv("AZURE_OPENAI_API_KEY")
        headers['content-length'] = str(len(modified_request_body))
        

        # Replace url.
        url = url.replace(f'{os.getenv("BASE_URL")}', f'{os.getenv("AZURE_ENDPOINT")}')

        # 使用 httpx 發送請求
        async with httpx.AsyncClient(timeout=None) as client:
            forwarded_response = await client.request(method, url, content=modified_request_body, headers=headers)

        block_response = Response(
            content=forwarded_response.content,
            status_code=forwarded_response.status_code,
            headers=dict(forwarded_response.headers),  # Copy existing headers
            media_type=forwarded_response.headers.get("Content-Type")
        )

        # Step 1: Decode and modify the response body
        response_content_str = forwarded_response.content.decode('utf-8')
        response_json = json.loads(response_content_str)

        # Step 2: Modify the JSON content
        response_json['choices'][0]['message']['content'] = reason

        # Step 3: Re-encode the modified content
        modified_response_content = json.dumps(response_json).encode('utf-8')

        # Step 4: Create new Response and update Content-Length
        block_response = Response(
            content=modified_response_content,
            status_code=forwarded_response.status_code,
            headers=dict(forwarded_response.headers),  # Copy existing headers
            media_type=forwarded_response.headers.get("Content-Type")
        )

        # Step 5: Update Content-Length header to match the new content length
        block_response.headers["Content-Length"] = str(len(modified_response_content))

        return block_response

    except httpx.RequestError:
        logging.exception('Request error')
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)

    except:
        logging.exception("An error occurred")
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)



async def completions_block_response(request: Request, reason: str) -> Any:
    logging.info(f'Forwarding request to: OpenAI')
    try:
        # 取得 method
        url = str(request.url)
        method = request.method
        # 複製原始請求的 body 和 headers
        body = await request.body()
        #print(body)
        headers = {
            key: value for key, value in request.headers.items()
        }

        # Step 2: 解碼字節流為字串
        body_str = body.decode('utf-8')

        # Step 3: 解析 JSON 字串為 Python 字典
        body_json = json.loads(body_str)

        last_message = body_json['prompt']

        body_json['prompt'][0] = settings.default_message
        
        last_message = ' '.join(last_message)

        modified_request_body = json.dumps(body_json).encode('utf-8')

        headers['host'] = os.getenv("AZURE_HOST")
        headers['api-key'] = os.getenv("AZURE_OPENAI_API_KEY")
        headers['content-length'] = str(len(modified_request_body))
        headers['authorization'] = 'Bearer ' + os.getenv("AZURE_OPENAI_API_KEY")

        # Replace url.
        url = url.replace(f'{os.getenv("BASE_URL")}', f'{os.getenv("AZURE_ENDPOINT")}')

        # 使用 httpx 發送請求
        async with httpx.AsyncClient(timeout=None) as client:
            forwarded_response = await client.request(method, url, content=modified_request_body, headers=headers)

        # Step 1: Decode and modify the response body
        response_content_str = forwarded_response.content.decode('utf-8')
        response_json = json.loads(response_content_str)

        # Step 2: Modify the JSON content

        response_json["choices"][0]["text"] = reason

        # Step 3: Re-encode the modified content
        modified_response_content = json.dumps(response_json).encode('utf-8')

        # Step 4: Create new Response and update Content-Length
        block_response = Response(
            content=modified_response_content,
            status_code=forwarded_response.status_code,
            headers=dict(forwarded_response.headers),  # Copy existing headers
            media_type=forwarded_response.headers.get("Content-Type")
        )

        # Step 5: Update Content-Length header to match the new content length
        block_response.headers["Content-Length"] = str(len(modified_response_content))

        return block_response

    except httpx.RequestError:
        logging.exception('Request error')
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)

    except:
        logging.exception("An error occurred")
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)



async def chat_stream_output_block_response(request: Request, reason: str) -> Any:
    logging.info(f'Forwarding request to: OpenAI')
    try:
        
        content = block_chat_stream(request, reason)
        
        block_response = Response(
            content=content,
            status_code=request.status_code,
            headers=dict(request.headers),  # Copy existing headers
            media_type=request.headers.get("Content-Type")
        )

        return block_response

    except httpx.RequestError:
        logging.exception('Request error')
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)

    except:
        logging.exception("An error occurred")
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)


async def chat_stream_input_block_response(latest_message: str, request: Request, reason: str) -> Any:
    logging.info(f'Forwarding request to: OpenAI')
    try:
        # 取得 method
        url = str(request.url)
        method = request.method
        # 複製原始請求的 body 和 headers
        body = await request.body()
        headers = {
            key: value for key, value in request.headers.items()
        }

        # Step 2: 解碼字節流為字串
        body_str = body.decode('utf-8')

        # Step 3: 解析 JSON 字串為 Python 字典
        body_json = json.loads(body_str)

        # Step 4: 確定 messages 列表不為空，並修改最後一個 'content' 欄位
        if 'messages' in body_json and body_json['messages']:
            # 取得最後一個 message

            for message in reversed(body_json.get('messages', [])):
                if message.get('content') == latest_message:
                    message['content'] = settings.default_message
                    # 如果只需要修改第一個匹配項，找到後即可跳出迴圈
                    break

        modified_request_body = json.dumps(body_json).encode('utf-8')

        return modified_request_body

    except httpx.RequestError:
        logging.exception('Request error')
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)

    except:
        logging.exception("An error occurred")
        return JSONResponse(content={"error": "Failed to forward request to OpenAI."}, status_code=502)