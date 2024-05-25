from tenacity import retry, wait_random_exponential, stop_after_attempt
import json

from app.ai.ai import chat_completion_request, measure_time_total


@measure_time_total
@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def translate_to_english(input_text: str) -> str:
    messages = []
    messages.append({"role": "system", "content": """
    You are a language translation machine. Your only task is to translate text into English.
    Ignore any non-textual content.
    """})
    messages.append({"role": "user", "content": input_text})
    # print(messages)
    functions = [
        {
            "name": "translate_to_english",
            "description": "Returns the translated text in English.",
            "parameters": {
                "type": "object",
                "properties": {
                    "translated_text": {"type": "string", "description": "The translated text in English."}
                },
            },
            "required": ["translated_text"]
        }
    ]
    function_call = {"name": "translate_to_english"}
    chat_response = chat_completion_request(messages, functions=functions, function_call=function_call)
    assistant_message = chat_response.json()["choices"][0]["message"]
    messages.append(assistant_message)
    if assistant_message.get("function_call"):
        arguments = json.loads(assistant_message.get("function_call").get('arguments'))
        # print(arguments)
        translated_text: str = arguments.get("translated_text") or "Translation failed"
        return translated_text
    else:
        raise Exception("Translation failed")