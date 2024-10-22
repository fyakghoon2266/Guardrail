from pydantic_settings import BaseSettings
from typing import Dict, List

class Settings(BaseSettings):

    default_message: str = '一加一等於多少'
    missing_token_message: str = "Missing Authorization header"
    error_token_message: str = "Unrecognized Authorization token"
    input_keyword_block_message: str = '非常抱歉輸入內容被阻擋(關鍵字被阻擋)'
    output_keyword_block_message: str = '非常抱歉輸出內容被阻擋(關鍵字被阻擋)'
    input_content_block_message: str = '非常抱歉輸入內容被阻擋(內容被阻擋)'
    output_content_block_message: str = '非常抱歉輸出內容被阻擋(內容被阻擋)'

    stream_input_keyword_block_message: str = "非常抱歉輸入內容被阻擋(關鍵字被阻擋)，因為觸犯到護欄的關鍵字規則了"
    stream_output_keyword_block_message: str = "非常抱歉輸出內容被阻擋(關鍵字被阻擋)，因為這觸犯到護欄的關鍵字規則了"
    stream_input_content_block_message: str = "非常抱歉輸入內容被阻擋(內容被阻擋)，因為觸犯到護欄的內容規則了"
    stream_output_content_block_message: str = "非常抱歉輸出內容被阻擋(內容被阻擋)，因為觸犯到護欄的內容規則了"

settings = Settings()