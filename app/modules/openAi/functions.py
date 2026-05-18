def create_answer_function(justify: bool = False, answer_json_type: str = "string", optional_answer: bool = False):
    schema = {
        "type": "object",
        "required": [] if optional_answer else ["answer"],
        "properties": {
            "answer": {
                "type": answer_json_type,
                "description": "Direct answer to the question. Only provide the requested value, do not elaborate with an explanation.",
            }
        },
    }

    if justify:
        schema["required"] = ["justification"] + schema["required"]
        schema["properties"] = {
            "justification": {
                "type": "string",
                "description": "Explain the reasoning and rational behind the answer. Do not directly reference the question.",
            },
            **schema["properties"],
        }

    return {
        "type": "function",
        "function": {
            "name": "answer",
            "description": "Generate an answer based on the given query",
            "parameters": schema,
        },
    }
