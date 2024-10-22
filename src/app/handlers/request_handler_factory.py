from typing import Any
from .completions_handler import CompletionsRequestHandler
from .embeddings_handler import EmbeddingsRequestHandler
from .chat_completions_handler import ChatCompletionsRequestHandler

class RequestHandlerFactory:
    @staticmethod
    def get_handler(request_type: str, model_info: str, api_version: str) -> Any:
        if request_type == "completions":
            return CompletionsRequestHandler(model_info, api_version)
        elif request_type == "embeddings":
            return EmbeddingsRequestHandler(model_info, api_version)
        elif request_type == "chat_completions":
            return ChatCompletionsRequestHandler(model_info, api_version)
        else:
            raise ValueError("Invalid request type")