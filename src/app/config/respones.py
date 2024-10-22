def generate_block_message(block_id, block_reason):
    return {
        "block_id": block_id,
        "block_reason": block_reason
    }

def completions_format_response(response, block_id=0, block_reason=""):
    return {
        "body": {
            "id": response.id,
            "created": response.created,
            "choices":[
                {
                    "text": response.choices[0].text,
                    "index": response.choices[0].index,
                    "finish_reason": response.choices[0].finish_reason,
                    "logprobs": response.choices[0].logprobs
                }
            ],
            "usage": 
                {
                    'completion_tokens':response.usage.completion_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                },
            # "block_message": generate_block_message(block_id, block_reason)
        }
    }


def chat_format_response(response, block_id=0, block_reason=""):
    return {
        "body": {
            "id": response.id,
            "created": response.created,
            "choices":[
                {
                    "index": response.choices[0].index,
                    "finish_reason": response.choices[0].finish_reason,
                    "logprobs": response.choices[0].logprobs,
                    "message":
                        {
                            "role": response.choices[0].message.role,
                            "content": response.choices[0].message.content
                        }
                }
            ],
            "usage": 
                {
                    'completion_tokens':response.usage.completion_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                },
            # "block_message": generate_block_message(block_id, block_reason)
        }
    }


def embeddings_format_response(response, block_id=0, block_reason=""):
    return {
        "body": {
            "data":
                {
                    "index": response.data[0].index,
                    "embedding": response.data[0].embedding,
                },
            "usage": 
                {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens
                },
            "block_message": generate_block_message(block_id, block_reason)
        }
    }

def chatollama_format_response(response, block_id=0, block_reason=""):
    return {
            "lc": 1,
            "type": "constructor",
            "id": [
                "langchain_core",
                "messages",
                "AIMessage"
            ],
            "kwargs": {
                "content": "sadfdsafadsfasddassdf",
                "additional_kwargs": {}
            }
            }