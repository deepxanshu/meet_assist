
from app.ai import translate
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt

from app.ai.advice import generate_context_entries
from app.ai.ai import chat_completion_request, measure_time_total

@measure_time_total
@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def generate_surf(input_text: str) -> str:
    messages = [{"role": "system", "content": "You are a Finance Expert. Provide concise and relevant financial insights."}]
    english_query = translate.translate_to_english(input_text)
    casual_phrases = [
    'yo',
    'what up',
    'sup',
    'theek ho',
    'how are you',
    'what’s up',
    'okay',
    'hi',
    'hello',
    'good morning',
    'good afternoon',
    'good evening',
    'bye',
    'see ya',
    'thanks',
    'thank you',
    'lol',
    'haha',
    'that’s funny',
    'i’m bored',
    'tell me a joke',
    'what’s your name',
    'who made you',
    'what can you do'
]

    # Determine if the query is casual or requires a finance context
    if english_query.lower() in casual_phrases:
        casual_response = "While I specialize in finance, I'm here to help with any questions or provide advice! How can I assist you further?"
        return casual_response
    else:
        # For more detailed finance queries, include the data context
        context = "Given your interest in finance and possibly Stashfin, let's explore the most current and relevant insights available."
        messages.append({"role": "user", "content": english_query + " " + context})

    functions = [
        {
            "name": "generate_surf",
            "description": "Generates finance-related insights based on the given context and query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "surf_text": {"type": "string", "description": "The generated finance-related insight text."}
                },
            },
            "required": ["surf_text"]
        }
    ]
    function_call = {"name": "generate_surf"}

    # Simulate a chat completion request as done in your translation function
    chat_response = chat_completion_request(messages, functions=functions, function_call=function_call)
    assistant_message = chat_response.json()["choices"][0]["message"]
    messages.append(assistant_message)
    if assistant_message.get("function_call"):
        arguments = json.loads(assistant_message.get("function_call").get('arguments'))
        surf_text: str = arguments.get("surf_text") or "Surf generation"
        return surf_text
    else:
        raise Exception("Surf generation Failed. Please try again")
