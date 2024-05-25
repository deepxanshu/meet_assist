import json

# from ai import chat_completion_request, measure_time_total
from app.ai import translate
from tenacity import retry, wait_random_exponential, stop_after_attempt

from app.ai.ai import chat_completion_request, measure_time_total

def generate_context_entries(data):
    context_entries = []
    for entry in data:
        entry_context = ". ".join([f"{key} will be {value}" for key, value in entry.items()])
        context_entries.append(entry_context)
    return " ".join(context_entries)

system_prompt = """
Act as a virtual assistant for a fintech company, capable of providing concise, actionable advice based on meeting logs and engaging in casual conversation. For professional inquiries related to meeting logs, offer insights and recommendations. For casual or personal inquiries, respond in a friendly and direct manner without delving into professional advice. Also, keep the response to the point, don't add unnecessary details, keep the response short until it is asked to be detailed.
"""
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


    
@measure_time_total
@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def generate_advice_with_context(input_text: str, data: list) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    english_query = translate.translate_to_english(input_text)
    
    # If the input is casual or doesn't require data context, adjust the prompt accordingly
    if english_query.lower() in casual_phrases:
        casual_response = "It sounds like you're making a casual inquiry. How can I assist you further?"
        return casual_response

    if english_query.lower() in ["thanks", "thank you", "thank", "ty", "okay", "ok"]:
        return "You're welcome! Let me know if there's anything else I can help with."
    else:
        # For more substantive advice queries, include the meeting data context
        context_entries = generate_context_entries(data)
        context = f"Here is what I know from the meeting logs: {context_entries} Based on this, how should we proceed?"
    
        messages.append({"role": "user", "content": english_query + " " + context})


    functions = [
        {
            "name": "generate_advice",
            "description": "Generates advice based on the given context and query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "advice_text": {"type": "string", "description": "The generated advice text."}
                },
            },
            "required": ["advice_text"]
        }
    ]
    function_call = {"name": "generate_advice"}

    # Simulate a chat completion request as done in your translation function
    try:
        chat_response = chat_completion_request(messages, functions=functions, function_call=function_call)
        assistant_message = chat_response.json()["choices"][0]["message"]
    except KeyError:
        assistant_message = "I'm sorry, I couldn't process that request." 
    messages.append(assistant_message)
    if assistant_message.get("function_call"):
        arguments = json.loads(assistant_message.get("function_call").get('arguments'))
        advice_text: str = arguments.get("advice_text") or "Advice generation failed"
        return advice_text
    else:
        raise Exception("Advice generation failed")
