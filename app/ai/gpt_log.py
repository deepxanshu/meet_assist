from app.ai import translate
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import Dict
from app.ai.ai import chat_completion_request, measure_time_total

@measure_time_total
@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
async def interpret_user_input(input_text: str) -> Dict[str, str]:
    messages = [{"role": "system", "content": "You are an intelligent assistant. Interpret and organize meeting details provided in the user's input."}]
    english_query = translate.translate_to_english(input_text)

    # Include the data context for detailed meeting queries
    context = "The user is looking for an organized interpretation of their meeting notes. Please categorize the details appropriately."
    messages.append({"role": "user", "content": english_query + " " + context})

    functions = [
        {
            "name": "interpret_meeting_notes",
            "description": "Interprets and organizes meeting notes into categorized details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "meeting_notes": {"type": "string", "description": "The interpreted and organized meeting notes."}
                },
            },
            "required": ["meeting_notes"]
        }
    ]
    function_call = {"name": "interpret_meeting_notes"}

    # Simulate a chat completion request as done in your translation function
    chat_response = chat_completion_request(messages, functions=functions, function_call=function_call)
    assistant_message = chat_response.json()["choices"][0]["message"]
    
    if "function_call" in assistant_message:
        arguments = json.loads(assistant_message.get("function_call").get('arguments'))
        meeting_notes: Dict[str, str] = arguments.get("meeting_notes") or {"error": "Interpretation failed"}
        return meeting_notes
    else:
        raise Exception("Meeting notes interpretation failed")