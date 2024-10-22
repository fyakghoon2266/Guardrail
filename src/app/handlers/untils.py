import json
import copy

import tiktoken

def get_last_user_message(conversation_str, system_identifiers=["AI:"]):
    try:
        # 將字串分割為多行
        conversation_lines = conversation_str.strip().split("\n")
        
        last_user_message = None
        
        # 遍歷對話列表，尋找最後一個用戶的訊息
        for line in conversation_lines:
            # 檢查該行是否為系統訊息
            if not any(line.strip().lower().startswith(identifier.lower()) for identifier in system_identifiers):
                last_user_message = line.strip()  # 更新最後的用戶訊息
        
        return last_user_message
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # 若發生錯誤，返回 None


def replace_content(streaming_data, replace_str: str):
    # 用來累積所有 content 的變數
    all_content = ""

    # 解析每個流的數據塊
    for chunk in streaming_data.split("\n"):
        # 確認數據塊是否以 "data:" 開頭，並去除 "data: "
        if chunk.startswith("data:"):
            chunk_data = chunk[len("data:"):].strip()

            # 忽略空的或 "data: [DONE]" 的數據塊
            if chunk_data and chunk_data != "[DONE]":
                # 將 JSON 字串解析為 Python 字典
                chunk_json = json.loads(chunk_data)

                # 檢查 JSON 是否有 delta 欄位以及其內的 content
                choices = chunk_json.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    all_content += content

    # 構造新的數據塊來逐字回傳替換內容
    new_streaming_data = []
    index = 0  # 用來逐字替換的指標

    for chunk in streaming_data.split("\n"):
        if chunk.startswith("data:"):
            chunk_data = chunk[len("data:"):].strip()
            if chunk_data and chunk_data != "[DONE]":
                chunk_json = json.loads(chunk_data)
                choices = chunk_json.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    if "content" in delta and index < len(replace_str):
                        # 用新的替換內容逐字取代原來的 content
                        delta["content"] = replace_str[index]
                        chunk_json["choices"][0]["delta"] = delta
                        index += 1

                # 將修改後的 JSON 轉回為字串，並加上 "data: " 前綴
                new_streaming_data.append(f"data: {json.dumps(chunk_json).encode('utf-8')}")

    # 最後加上 [DONE] 來表示結束
    new_streaming_data.append("data: [DONE]")

    # 將所有新生成的數據塊合併為一個字串，並返回
    return "\n".join(new_streaming_data)

def accumulate_streamed_content(streaming_data):
    # 用來累積所有 content 的變數
    complete_content = ""

    # 解析每個流的數據塊
    for chunk in streaming_data.split("\n"):
        # 確認數據塊是否以 "data:" 開頭，並去除 "data: "
        if chunk.startswith("data:"):
            chunk_data = chunk[len("data:"):].strip()

            # 忽略空的或 "data: [DONE]" 的數據塊
            if chunk_data and chunk_data != "[DONE]":
                # 將 JSON 字串解析為 Python 字典
                chunk_json = json.loads(chunk_data)

                # 檢查 JSON 是否有 delta 欄位以及其內的 content
                choices = chunk_json.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    complete_content += content  # 累積 content

    # 返回累積後的完整內容
    return complete_content


def replace_content_preserve_format(forwarded_response, replace_str):
    # 將 forwarded_response 的內容解碼為 utf-8 字串
    content_str = forwarded_response.body.decode('utf-8')

    # 用來處理修改過的內容
    new_streaming_data = []

    # 將數據流按行分割並處理
    for chunk in content_str.split("\n"):
        if chunk.startswith("data:"):
            # 獲取 "data:" 之後的 JSON 資料
            chunk_data = chunk[len("data:"):].strip()

            # 忽略空數據或已結束的數據
            if chunk_data and chunk_data != "[DONE]":
                # 將 JSON 字串解析為 Python 字典
                chunk_json = json.loads(chunk_data)

                # 檢查是否有 "choices" 和 "delta" 欄位
                choices = chunk_json.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    if "content" in delta:
                        # 將 delta["content"] 替換為新的內容
                        delta["content"] = replace_str[:len(delta["content"])]
                        replace_str = replace_str[len(delta["content"]):]  # 剩下的部分

                # 將修改後的 JSON 轉換為字串，並加上 "data: " 前綴
                new_streaming_data.append(f"data: {json.dumps(chunk_json)}")
            else:
                # 保持 [DONE] 部分或其他空行不變
                new_streaming_data.append(chunk)

    # 將所有新生成的數據塊合併為一個字串，並返回
    return "\n".join(new_streaming_data)

# 解析回應內容並檢查 'finish_reason'
def process_response_content(response_content: str) -> bool:
    # 嘗試直接解析為 JSON 物件
    if try_parse_json(response_content):
        data = json.loads(response_content)
        if handle_data(data):
            return True
    else:
        # 如果不是 JSON 物件，嘗試按照多行 'data: ' 格式處理
        lines = response_content.strip().split('\n')
        for line in lines:
            # 檢查行是否以 'data: ' 開頭
            if line.startswith('data: '):
                json_data = line[len('data: '):].strip()
                # 檢查是否為 [DONE]
                if json_data == '[DONE]':
                    print("Stream completed.")
                    continue
                try:
                    data = json.loads(json_data)
                    if handle_data(data):
                        return True
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    continue
            else:
                continue
    return False

# 嘗試解析為 JSON，返回布林值
def try_parse_json(content: str) -> bool:
    try:
        json.loads(content)
        return True
    except json.JSONDecodeError:
        return False

# 處理解析後的資料，檢查 'finish_reason'
def handle_data(data: dict) -> bool:
    choices = data.get('choices', [])
    for choice in choices:
        finish_reason = choice.get('finish_reason')
        if finish_reason == 'stop':
            print("Received 'stop' finish_reason, stopping further processing.")
            return True  # 返回 True，表示已經遇到 'stop'
        else:
            # 處理其他內容
            # 根據不同的資料結構，可能需要從 'message' 或 'delta' 中取得內容
            content = ''
            if 'delta' in choice:
                content = choice.get('delta', {}).get('content', '')
            elif 'message' in choice:
                content = choice.get('message', {}).get('content', '')

    return False  # 沒有遇到 'stop'，返回 False



def block_chat_stream(forwarded_response, block_context):
    """
    這邊定義了當訊息被阻擋，且 `stream=True` 時
    如何將內容置換成預設的阻擋文字。
    """

    print('forwarded_response : ', forwarded_response)
    lines = forwarded_response.text.splitlines()
    basic_info = lines[0:1] + lines[2:3]
    template = json.loads(lines[4].replace('data: ', ''))
    end_info = lines[-4:-3] + lines[-2:-1]
    message = block_context

    block_contents = list()
    # get block message
    for s in message:
        tmp = copy.deepcopy(template)
        tmp['choices'][0]['delta']['content'] = s
        tmp_content = 'data: ' + json.dumps(tmp)
        block_contents.append(tmp_content)

    block_info = basic_info + block_contents + end_info
    output = "\n\n".join(block_info).encode('utf-8')

    return output

def get_last_user_content(data):
    for message in reversed(data.get('messages', [])):
        if message.get('role') == 'user' and message.get('content') is not None:
            return message.get('content')
    return None  # 如果没有找到符合条件的消息，返回None


def process_input(packet):
    model_name = packet.get('model')
    encoding_format = packet.get('encoding_format')  # Optional: can be used if needed
    input_data = packet.get('input')

    # 步驟 1: 判斷 input_data 是不是需要解碼
    if isinstance(input_data, list) and all(isinstance(i, int) for i in input_data[0]):  
        # 假設這裡的 input_data 是 token IDs，需要進行解碼
        encoding_name = tiktoken.encoding_name_for_model(model_name)
        tokenizer = tiktoken.get_encoding(encoding_name)
        
        # 解碼封包
        decoded_data = [tokenizer.decode(tokens) for tokens in input_data]
        result_string = " ".join(decoded_data)
        return result_string
    
    elif isinstance(input_data, list) and all(isinstance(i, str) for i in input_data):
        # 如果 input 是文字的列表，不需要解碼，直接返回原始的文字
        return " ".join(input_data)
    
    elif isinstance(input_data, str):
        # 如果 input 是單純的字串，直接返回原始字串
        return input_data

    else:
        raise ValueError("Unrecognized input format!")